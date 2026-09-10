import json
import tempfile
import unittest
from pathlib import Path

from evals.run_eval import case_output_dir, manifest_matches_case


class EvaluationTests(unittest.TestCase):
    def test_cases_have_distinct_output_directories(self) -> None:
        root = Path("output/cases")
        self.assertNotEqual(case_output_dir(root, 0), case_output_dir(root, 1))

    def test_manifest_must_match_case_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "run_manifest.json"
            path.write_text(
                json.dumps({"brand_name": "A", "product_name": "P"}),
                encoding="utf-8",
            )
            self.assertTrue(
                manifest_matches_case(path.parent, {"brand_name": "A", "product_name": "P"})
            )
            self.assertFalse(
                manifest_matches_case(path.parent, {"brand_name": "B", "product_name": "P"})
            )


if __name__ == "__main__":
    unittest.main()
