"""모델 호출 없이 코드 뼈대의 경계와 설정을 확인한다."""
import os
import unittest
from unittest.mock import patch
from rfp_rag.pipeline import STAGES, ask, status
from rfp_rag.settings import ROOT, load


class ScaffoldTests(unittest.TestCase):
    def test_unimplemented_pipeline_does_not_fabricate_answer(self):
        with self.assertRaises(NotImplementedError):
            ask("합성 질문", load())
        with self.assertRaises(ValueError):
            ask("  ", load())

    def test_every_stage_is_explicitly_unimplemented(self):
        self.assertEqual(set(status()), set(STAGES))
        self.assertEqual(set(status().values()), {"미구현"})
        for stage in STAGES:
            self.assertTrue((ROOT / "rfp_rag" / stage / ".gitkeep").is_file())

    def test_data_path_is_portable(self):
        with patch.dict(os.environ, {"RFP_DATA_DIR": ""}):
            self.assertEqual(load()["paths"]["data_dir"], ROOT / "data")
        with patch.dict(os.environ, {"RFP_DATA_DIR": "synthetic-data"}):
            self.assertEqual(load()["paths"]["data_dir"], ROOT / "synthetic-data")
