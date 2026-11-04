"""Run with python3 -m unittest discover -s evals -p 'test_*.py'."""
import unittest

import run

# The skill is loaded into every invocation, so its size is a cost the user
# pays each time. Raising a budget is a deliberate decision, not a side effect
# of adding a rule: merge or cut an existing rule first.
BUDGETS = {
    "skills/less/SKILL.md": 1000,
    "skills/less/references/design.md": 750,
}


class BudgetTest(unittest.TestCase):
    def test_skill_files_stay_within_word_budget(self):
        for path, limit in BUDGETS.items():
            words = len(run.load(run.ROOT / path).split())
            with self.subTest(path=path):
                self.assertLessEqual(words, limit, f"{path} has {words} words; budget is {limit}")


if __name__ == '__main__':
    unittest.main()
