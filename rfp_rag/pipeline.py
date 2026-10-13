"""문서 읽기부터 단순 검색과 답변 생성까지 연결한 기초 기준선."""
from rfp_rag.contracts import Answer
from rfp_rag.chunking.fixed import split
from rfp_rag.embeddings.openai import Embedder
from rfp_rag.embeddings.tfidf import TfidfEmbedder
from rfp_rag.generation.anthropic import AnthropicGenerator
from rfp_rag.generation.openai import OpenAIGenerator
from rfp_rag.indexing.json_index import VectorIndex
from rfp_rag.ingestion.files import load_documents
from rfp_rag.preprocessing.text import clean
from rfp_rag.providers.credentials import load_key
from rfp_rag.providers.anthropic_api import AnthropicClient
from rfp_rag.providers.openai_api import OpenAIClient
from rfp_rag.retrieval.dense import DenseRetriever

STAGES = {
    "ingestion": "HWP·PDF·CSV 불러오기",
    "preprocessing": "글 정리와 메타데이터 정규화",
    "chunking": "청크 생성",
    "embeddings": "임베딩·TF-IDF 벡터 생성",
    "indexing": "색인 저장과 불러오기",
    "retrieval": "근거 검색",
    "reranking": "검색 결과 재순위",
    "routing": "질문 분류",
    "generation": "근거를 이용한 답변 생성",
    "memory": "대화 맥락 관리",
    "verification": "답변과 근거 검증",
    "evaluation": "품질과 속도 평가",
}


def status() -> dict[str, str]:
    implemented = {'ingestion', 'preprocessing', 'chunking', 'embeddings', 'indexing', 'retrieval', 'generation'}
    return {name: '기초 구현' if name in implemented else '미구현' for name in STAGES}


def create_client(config: dict):
    if config['models']['provider'] == 'anthropic':
        return AnthropicClient(load_key('ANTHROPIC_API_KEY'))
    return OpenAIClient(load_key('OPENAI_API_KEY'))


def build(config: dict, *, client=None) -> VectorIndex:
    documents = [clean(document) for document in load_documents(config['paths']['data_dir'])]
    chunks = split(documents, **config['chunking'])
    if not chunks:
        raise ValueError('생성된 청크가 없습니다.')
    texts = [chunk.text for chunk in chunks]
    state = {}
    if config['models']['embedding'] == 'local-tfidf':
        embedder = TfidfEmbedder()
        embedder.fit(texts)
        state = embedder.state
    else:
        client = client if client is not None else create_client(config)
        embedder = Embedder(client, config['models']['embedding'])
    index = VectorIndex(chunks, embedder.embed(texts), embedder.model, state)
    index.save(config['paths']['index_path'])
    return index


def ask(question: str, config: dict, *, client=None) -> Answer:
    if not question.strip():
        raise ValueError("질문을 입력하세요.")
    index = VectorIndex.load(config['paths']['index_path'], model=config['models']['embedding'])
    if config['models']['embedding'] == 'local-tfidf':
        embedder = TfidfEmbedder(index.embedding_state)
    else:
        client = client if client is not None else create_client(config)
        embedder = Embedder(client, config['models']['embedding'])
    evidence = DenseRetriever(index, embedder).search(question, k=config['retrieval']['top_k'])
    if not evidence:
        return Answer('문서에서 답을 찾지 못했습니다.', False)
    client = client if client is not None else create_client(config)
    generator_type = AnthropicGenerator if config['models']['provider'] == 'anthropic' else OpenAIGenerator
    generator = generator_type(client, config['models']['generation'], config['generation']['max_output_tokens'])
    return generator.generate(question, evidence)
