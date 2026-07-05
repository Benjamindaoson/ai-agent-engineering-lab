import subprocess
import unittest
from unittest.mock import patch

from scripts.python_quality_gate import ProjectCheck, discover_projects, run


class PythonQualityGateTests(unittest.TestCase):
    def test_discovers_all_python_projects(self):
        projects = discover_projects()

        self.assertEqual(len(projects), 19)
        self.assertEqual(projects[0].project, "python-a2a-demo")
        self.assertTrue(all(project.package.startswith("python_") for project in projects))

    def test_run_returns_false_on_timeout(self):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["python"], 1)):
            self.assertFalse(run(ProjectCheck("python-react-agent", "python_react_agent"), "self_check", ["python"]))


if __name__ == "__main__":
    unittest.main()
