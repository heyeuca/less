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
