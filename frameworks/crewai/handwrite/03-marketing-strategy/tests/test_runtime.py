import json
import tempfile
import unittest
from pathlib import Path

from marketing_posts.runtime import (
    KNOWN_OUTPUT_FILES,
    load_inputs,
    prepare_output_dir,
    validate_outputs,
    write_manifest,
)


class RuntimeTests(unittest.TestCase):
    def test_load_inputs_merges_case_overrides_and_sets_current_year(self) -> None:
        inputs = load_inputs(overrides={"brand_name": "测试品牌"})

        self.assertEqual(inputs["brand_name"], "测试品牌")
        self.assertTrue(inputs["product_name"])
        self.assertIsInstance(inputs["current_year"], int)

    def test_load_inputs_rejects_empty_required_field(self) -> None:
        with self.assertRaisesRegex(ValueError, "brand_name"):
            load_inputs(overrides={"brand_name": "  "})

    def test_prepare_output_dir_removes_only_known_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / KNOWN_OUTPUT_FILES[0]).write_text("stale", encoding="utf-8")
            keep = root / "keep.txt"
            keep.write_text("keep", encoding="utf-8")

            prepare_output_dir(root)

            self.assertFalse((root / KNOWN_OUTPUT_FILES[0]).exists())
            self.assertTrue(keep.exists())

    def test_write_manifest_is_reproducible_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = write_manifest(Path(temp), {"brand_name": "测试品牌", "current_year": 2026})

            self.assertEqual(path.name, "run_manifest.json")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["brand_name"], "测试品牌")

    def test_validate_outputs_requires_source_url(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in KNOWN_OUTPUT_FILES[:6]:
                (root / name).write_text("content", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "source URL"):
                validate_outputs(root)


if __name__ == "__main__":
    unittest.main()
