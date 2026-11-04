"""Run with python3 -m unittest discover -s evals -p 'test_*.py'."""
import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path

import repos


class RepoCaseTest(unittest.TestCase):
    def graded(self, case, side):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / case["id"]
            shutil.copytree(repos.ROOT / case["id"] / "before", folder)
            if side == "after":
                shutil.copytree(repos.ROOT / case["id"] / "after", folder, dirs_exist_ok=True)
            return repos.grade_one(case, folder)

    def test_cases_exist(self):
        self.assertGreaterEqual(len(repos.CASES), 3)

    def test_untouched_repo_keeps_everything_and_removes_nothing(self):
        for case in repos.CASES:
            with self.subTest(case=case["id"]):
                row = self.graded(case, "before")
                self.assertTrue(row["kept"])
                self.assertFalse(row["removed"])
                self.assertTrue(row["tests_pass"])

    def test_reference_removes_only_the_unused_code(self):
        for case in repos.CASES:
            with self.subTest(case=case["id"]):
                row = self.graded(case, "after")
                self.assertEqual((row["kept"], row["removed"], row["tests_pass"]), (True, True, True))

    def test_over_cut_breaks_the_tests_or_the_keep(self):
        # Deleting the kept item as well must not grade as a pass.
        for case in repos.CASES:
            with self.subTest(case=case["id"]), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp) / case["id"]
                shutil.copytree(repos.ROOT / case["id"] / "before", folder)
                for check in case["must_keep"]:
                    path = folder / check["file"]
                    path.write_text("", encoding="utf-8")
                row = repos.grade_one(case, folder)
                self.assertFalse(row["kept"] and row["tests_pass"])

    def test_weakened_tests_are_restored_before_grading(self):
        case = next(c for c in repos.CASES if c["id"] == "R01")
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "R01"
            shutil.copytree(repos.ROOT / "R01" / "before", folder)
            # Keep the word compact but drop the behavior and the assertion on it.
            (folder / "report.py").write_text(
                "def render(rows, *, compact=False):\n"
                "    return \"\\n\".join(f\"{n:<12}{t:>8}\" for n, t in rows)\n", encoding="utf-8")
            (folder / "test_report.py").write_text(
                "import unittest\n\n\nclass T(unittest.TestCase):\n"
                "    def test_ok(self):\n        pass\n", encoding="utf-8")
            self.assertFalse(repos.grade_one(case, folder)["tests_pass"])

    def test_dropped_export_import_fails_the_keep(self):
        case = next(c for c in repos.CASES if c["id"] == "R03")
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "R03"
            shutil.copytree(repos.ROOT / "R03" / "before", folder)
            init = folder / "dates" / "__init__.py"
            init.write_text(init.read_text(encoding="utf-8").replace(", parse_range", ""), encoding="utf-8")
            self.assertFalse(repos.grade_one(case, folder)["kept"])

    def test_timeout_is_a_failure_not_a_crash(self):
        case = dict(repos.CASES[0], test=["-c", "import time; time.sleep(5)"])
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / case["id"]
            shutil.copytree(repos.ROOT / case["id"] / "before", folder)
            original = repos.subprocess.run
            repos.subprocess.run = lambda *a, **k: original(*a, **{**k, "timeout": 0.5})
            try:
                self.assertFalse(repos.grade_one(case, folder)["tests_pass"])
            finally:
                repos.subprocess.run = original

    def test_prepare_then_grade_reports_every_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                repos.prepare(out)
                repos.grade(out)
            report = (out / "repos.json").read_bytes().decode("utf-8")
            for case in repos.CASES:
                self.assertIn(case["id"], report)
                self.assertTrue((out / f"{case['id']}.task.md").exists())
            with self.assertRaises(SystemExit):
                repos.prepare(out)


if __name__ == "__main__":
    unittest.main()
