import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import course


class CourseProgressTest(unittest.TestCase):
    def test_progress_starts_at_first_level(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(course, "PROGRESS_FILE", Path(tmp) / "progress.json"):
                self.assertEqual(course.load_progress(), 1)
                self.assertEqual(course.current_level().project, "python-react-agent")

    def test_progress_is_clamped_to_existing_levels(self):
        with tempfile.TemporaryDirectory() as tmp:
            progress = Path(tmp) / "progress.json"
            progress.write_text('{"current_level": 999}', encoding="utf-8")
            with patch.object(course, "PROGRESS_FILE", progress):
                self.assertEqual(course.load_progress(), len(course.LEVELS))

    def test_command_for_current_level(self):
        level = course.LEVELS[0]
        self.assertEqual(
            course.command_for(level, "offline_demo")[-2:],
            ["-m", "python_react_agent.offline_demo"],
        )

    def test_single_target_does_not_unlock_next_level(self):
        with tempfile.TemporaryDirectory() as tmp:
            progress = Path(tmp) / "progress.json"
            with (
                patch.object(course, "PROGRESS_FILE", progress),
                patch.object(course, "run_target", return_value=True),
            ):
                self.assertEqual(course.run_current("self_check"), 0)
                self.assertFalse(progress.exists())

    def test_all_targets_unlock_next_level(self):
        with tempfile.TemporaryDirectory() as tmp:
            progress = Path(tmp) / "progress.json"
            with (
                patch.object(course, "PROGRESS_FILE", progress),
                patch.object(course, "run_target", return_value=True),
            ):
                self.assertEqual(course.run_current("all"), 0)
                self.assertEqual(course.load_progress(), 2)


if __name__ == "__main__":
    unittest.main()
