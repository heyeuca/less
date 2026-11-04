"""Run with python3 -m unittest discover -s evals -p 'test_*.py'."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import always

# Pasted into every session's AGENTS.md, so it must stay short.
BUDGET = 120


class AlwaysOnTest(unittest.TestCase):
    def test_rules_stay_within_budget(self):
        self.assertLessEqual(len(always.RULES.split()), BUDGET)

    def test_rules_protect_needed_explanation(self):
        for phrase in ("steps", "warnings", "anything the user asked for", "When\nunsure, include it"):
            self.assertIn(phrase, always.RULES)

    def test_every_case_can_fail_on_missing_content(self):
        ids = [case["id"] for case in always.CASES]
        self.assertEqual(len(ids), len(set(ids)))
        for case in always.CASES:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["must_include"])
                self.assertTrue(case["must_not_include"])

    def test_arms_differ_only_by_the_rules(self):
        for case in always.CASES:
            plain = always.prompt(case, "plain")
            with_rules = always.prompt(case, "always")
            self.assertTrue(with_rules.endswith(plain))
            self.assertIn(always.RULES, with_rules)
            self.assertNotIn("less skill", plain)

    def test_prompts_and_sheet(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                always.prompts(out)
                always.sheet(out)
            sheet = (out / "always.md").read_bytes().decode("utf-8")
            for case in always.CASES:
                self.assertIn(f"## {case['id']} always", sheet)
                self.assertIn(f"## {case['id']} plain", sheet)
            with self.assertRaises(SystemExit):
                always.prompts(out)


if __name__ == "__main__":
    unittest.main()
