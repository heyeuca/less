"""Run with python3 -m unittest discover -s evals -p 'test_*.py'."""
import re
import unittest

import run

SKILL_IDS = set(re.findall(r"^- ([WSM]\d+)\.", run.SKILL, re.M))
DESIGN_IDS = set(re.findall(r"^\| (C\d+) \|", run.DESIGN, re.M)) | set(
    re.findall(r"^- \*\*(K\d+) ", run.DESIGN, re.M))

# Rules no case exercises yet. Closing a gap means adding a case and removing
# its ID here; a new rule without a case fails until it gets one.
KNOWN_GAPS = set()


def noop(case):
    # "unchanged", "unchanged." and "unchanged (reason)" all describe a no-op;
    # "unchanged, or <cut>" allows a removal, so it is not one.
    return case["after"] == case["before"] or re.fullmatch(
        r"unchanged\.?( \(.*\))?", case["after"]) is not None


class CoverageTest(unittest.TestCase):
    def test_rule_ids_are_parsed(self):
        self.assertEqual(len([i for i in SKILL_IDS if i[0] == "W"]), 7)
        self.assertEqual(len([i for i in SKILL_IDS if i[0] == "S"]), 4)
        self.assertEqual(len([i for i in DESIGN_IDS if i[0] == "C"]), 15)

    def test_cases_cite_known_rules(self):
        for case in run.CASES:
            with self.subTest(case=case["id"]):
                self.assertIn("rules", case)
                self.assertLessEqual(set(case["rules"]), SKILL_IDS | DESIGN_IDS)

    def test_uncovered_rules_match_known_gaps(self):
        cited = {rule for case in run.CASES for rule in case["rules"]}
        self.assertEqual((SKILL_IDS | DESIGN_IDS) - cited, KNOWN_GAPS)

    def test_removal_rules_have_removal_and_protection_cases(self):
        # A deletion rule needs a case where it removes something and a case
        # where a legitimate use must survive (a known bad output or a no-op).
        for rule in sorted(i for i in SKILL_IDS if i[0] in "WS"):
            cases = [c for c in run.CASES if rule in c["rules"]]
            with self.subTest(rule=rule):
                self.assertTrue(any(not noop(c) for c in cases), "no removal case")
                self.assertTrue(any(noop(c) or "bad_after" in c for c in cases), "no protection case")


if __name__ == '__main__':
    unittest.main()
