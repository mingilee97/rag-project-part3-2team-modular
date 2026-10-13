"""합성 자료와 대역 API로 전체 흐름과 오류 경계를 점검한다."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from rfp_rag.chunking.fixed import split
from rfp_rag.contracts import Document, SearchHit
from rfp_rag.generation.openai import OpenAIGenerator
from rfp_rag.generation.anthropic import AnthropicGenerator
from rfp_rag.indexing.json_index import VectorIndex
from rfp_rag.pipeline import ask, build
from rfp_rag.providers.openai_api import OpenAIClient, ProviderError
from rfp_rag.retrieval.dense import DenseRetriever
from rfp_rag.settings import load


class FakeClient:
    def __init__(self):
        self.calls = []

    def post(self, endpoint, payload):
        self.calls.append((endpoint, payload))
        if endpoint == 'embeddings':
            return {'data': [{'index': i, 'embedding': [1., 0.] if '회의실' in text else [0., 1.]}
                             for i, text in enumerate(payload['input'])]}
        context = json.loads(payload['input'])['evidence']
        answer = {'text': '회의실 예약입니다.', 'found': True, 'evidence_ids': [context[0]['chunk_id']]}
        return {'status': 'completed', 'output': [{'type': 'message', 'content': [
            {'type': 'output_text', 'text': json.dumps(answer, ensure_ascii=False)}]}]}


class BaselineTests(unittest.TestCase):
    def test_local_tfidf_build_reload_and_haiku_generate(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'a.txt').write_text('회의실 예약 사업입니다.', encoding='utf-8')
            (root / 'b.txt').write_text('도서 검색 사업입니다.', encoding='utf-8')
            config = load()
            config['paths'] = {'data_dir': root, 'index_path': root / 'index.json'}
            with patch('rfp_rag.pipeline.create_client', side_effect=AssertionError('로컬 색인은 API를 사용하면 안 됩니다')):
                build(config)
                self.assertFalse(ask('zzzzunknown', config).found)
            client = FakeClient()
            packet = {'stop_reason': 'end_turn', 'content': [{'type': 'text', 'text': json.dumps(
                {'text': '예약 사업입니다.', 'found': True, 'evidence_ids': ['a.txt:c0']})}]}
            with patch.object(client, 'post', return_value=packet) as request:
                answer = ask('회의실', config, client=client)
            self.assertEqual(answer.evidence_ids, ('a.txt:c0',))
            self.assertEqual(request.call_args.args[0], 'messages')
            self.assertEqual(request.call_args.args[1]['model'], 'claude-haiku-4-5-20251001')

    def test_haiku_rejects_truncated_generation(self):
        client = FakeClient()
        evidence = [SearchHit(split([Document('a', '합성')], size=20, overlap=0)[0], 1.)]
        with patch.object(client, 'post', return_value={'stop_reason': 'max_tokens'}):
            with self.assertRaises(ProviderError):
                AnthropicGenerator(client, 'claude-haiku-4-5-20251001', 2048).generate('질문', evidence)

    def test_build_reload_retrieve_generate(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'a.txt').write_text('회의실 예약 사업입니다.', encoding='utf-8')
            (root / 'b.txt').write_text('도서 검색 사업입니다.', encoding='utf-8')
            config = load('configs/openai.toml')
            config['paths'] = {'data_dir': root, 'index_path': root / 'index.json'}
            config['retrieval']['top_k'] = 1
            client = FakeClient()
            index = build(config, client=client)
            self.assertEqual(len(index.chunks), 2)
            answer = ask('회의실 사업은?', config, client=client)
            self.assertTrue(answer.found)
            self.assertEqual(answer.evidence_ids, ('a.txt:c0',))
            self.assertEqual([endpoint for endpoint, _ in client.calls], ['embeddings', 'embeddings', 'responses'])
            self.assertEqual(client.calls[-1][1]['model'], 'gpt-5-mini')

    def test_chunk_overlap_and_short_tail(self):
        chunks = split([Document('a', '0123456789')], size=6, overlap=2)
        self.assertEqual([chunk.text for chunk in chunks], ['012345', '456789'])
        with self.assertRaises(ValueError):
            split([Document('a', 'test')], size=4, overlap=4)

    def test_cosine_top_k_and_dimension_validation(self):
        chunks = split([Document('a', '회의실'), Document('b', '도서')], size=20, overlap=0)
        index = VectorIndex(chunks, [[10., 0.], [0., 2.]], 'synthetic')
        retriever = DenseRetriever(index, type('E', (), {'embed': lambda _, texts: [[1., 0.]]})())
        self.assertEqual(retriever.search('질문', k=1)[0].chunk.doc_id, 'a')
        with self.assertRaises(ValueError):
            VectorIndex(chunks, [[1.], [1., 2.]], 'synthetic')

    def test_index_rejects_wrong_model(self):
        with tempfile.TemporaryDirectory() as folder:
            index = VectorIndex(split([Document('a', '합성')], size=20, overlap=0), [[1., 0.]], 'first')
            path = Path(folder) / 'index.json'
            index.save(path)
            with self.assertRaises(ValueError):
                VectorIndex.load(path, model='second')

    def test_generation_rejects_unknown_evidence_and_incomplete_response(self):
        evidence = [SearchHit(split([Document('a', '합성')], size=20, overlap=0)[0], 1.)]
        client = FakeClient()
        generator = OpenAIGenerator(client, 'gpt-5-mini', 2048)
        with patch.object(client, 'post', return_value={'status': 'incomplete'}):
            with self.assertRaises(ProviderError):
                generator.generate('질문', evidence)
        packet = {'status': 'completed', 'output': [{'type': 'message', 'content': [
            {'type': 'output_text', 'text': json.dumps({'text': '답변', 'found': True, 'evidence_ids': ['unknown']})}]}]}
        with patch.object(client, 'post', return_value=packet):
            with self.assertRaises(ProviderError):
                generator.generate('질문', evidence)
        self.assertFalse(generator.generate('질문', []).found)

    def test_provider_hides_key_and_error_body(self):
        client = OpenAIClient('synthetic-secret')
        error = HTTPError('https://api.openai.com/v1/responses', 401, 'synthetic-secret', {}, None)
        with patch('rfp_rag.providers.openai_api.urlopen', side_effect=error):
            with self.assertRaises(ProviderError) as caught:
                client.post('responses', {'model': 'gpt-5-mini'})
        self.assertIn('401', str(caught.exception))
        self.assertNotIn('synthetic-secret', str(caught.exception))

    def test_credential_environment_does_not_change_other_keys(self):
        from rfp_rag.providers.credentials import load_key
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'synthetic-openai', 'ANTHROPIC_API_KEY': 'synthetic-other'}):
            self.assertEqual(load_key(), 'synthetic-openai')


if __name__ == '__main__':
    unittest.main()
