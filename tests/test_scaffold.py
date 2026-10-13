"""모델 호출 없이 코드 뼈대의 경계와 설정을 확인한다."""
import os
import unittest
from unittest.mock import patch
from rfp_rag.pipeline import STAGES, ask, status
from rfp_rag.settings import ROOT, load


class ScaffoldTests(unittest.TestCase):
    def test_default_matches_verified_haiku_and_openai_stays_separate(self):
        baseline = load()
        haiku = load('configs/haiku.toml')
        openai = load('configs/openai.toml')
        self.assertEqual(baseline, haiku)
        self.assertEqual(baseline['models']['provider'], 'anthropic')
        self.assertEqual(openai['models'], {
            'provider': 'openai', 'embedding': 'text-embedding-3-small',
            'generation': 'gpt-5-mini',
        })
        self.assertNotEqual(baseline['paths']['index_path'], openai['paths']['index_path'])

    def test_pipeline_rejects_empty_question_and_missing_index(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as folder:
            config = load()
            config['paths']['index_path'] = Path(folder) / 'missing.json'
            with self.assertRaises(FileNotFoundError):
                ask("합성 질문", config)
        with self.assertRaises(ValueError):
            ask("  ", load())

    def test_optional_stages_remain_unimplemented(self):
        self.assertEqual(set(status()), set(STAGES))
        for name in ('reranking', 'routing', 'memory', 'verification', 'evaluation'):
            self.assertEqual(status()[name], '미구현')
        self.assertEqual(status()['generation'], '기초 구현')
        for stage in STAGES:
            self.assertTrue((ROOT / "rfp_rag" / stage / ".gitkeep").is_file())

    def test_data_path_is_portable(self):
        with patch.dict(os.environ, {"RFP_DATA_DIR": ""}):
            self.assertEqual(load()["paths"]["data_dir"], ROOT / "data/raw")
        with patch.dict(os.environ, {"RFP_DATA_DIR": "synthetic-data"}):
            self.assertEqual(load()["paths"]["data_dir"], ROOT / "synthetic-data")
