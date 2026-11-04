"""Run with python3 -m unittest discover -s evals -p 'test_*.py'."""
import contextlib
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

import run


class PreservationTest(unittest.TestCase):
    def report(self, out):
        with contextlib.redirect_stdout(io.StringIO()):
            run.preservation(out)
        return json.loads((out / 'preservation.json').read_text())

    def test_references_and_missing_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            for case in run.CASES:
                if 'protected_spans' in case:
                    (out / f"{case['id']}.with.out.md").write_text(case['after'])
            report = self.report(out)
            for counts in report['with']['summary'].values():
                self.assertEqual(counts['passed'], counts['total'])
            for counts in report['without']['summary'].values():
                self.assertEqual(counts['passed'], 0)
                self.assertGreater(counts['total'], 0)

    def test_noop_whitespace_damage_and_no_removal_are_separate(self):
        cases = {case['id']: case for case in run.CASES}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / 'P01.with.out.md').write_text(cases['P01']['before'])
            (out / 'P02.with.out.md').write_text(cases['P02']['before'] + '\n')
            (out / 'P03.with.out.md').write_text('50%의 요청이 실패합니다.')
            rows = {row['id']: row for row in self.report(out)['with']['cases']}
            self.assertTrue(rows['P01']['preserved'])
            self.assertFalse(rows['P01']['removed'])
            self.assertTrue(rows['P02']['preserved'])
            self.assertFalse(rows['P02']['exact_noop'])
            self.assertFalse(rows['P03']['preserved'])
            self.assertTrue(rows['P03']['removed'])

    def test_validation_obligation_cannot_be_weakened(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / 'P09.with.out.md').write_text(
                'Some inputs should be validated. Secrets must never appear in logs.')
            rows = {row['id']: row for row in self.report(out)['with']['cases']}
            self.assertFalse(rows['P09']['preserved'])
            self.assertTrue(rows['P09']['removed'])

    def test_removal_span_survives_whitespace_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / 'P09.with.out.md').write_text(
                'For completeness:\nAll inputs must be validated. Secrets must never appear in logs.')
            rows = {row['id']: row for row in self.report(out)['with']['cases']}
            self.assertTrue(rows['P09']['preserved'])
            self.assertFalse(rows['P09']['removed'])

    def test_annotations_never_enter_generation_prompts(self):
        case = dict(run.CASES[-1], protected_spans=['SECRET_GOLD_MARKER'])
        for prompt in (run.task(case, True), run.task(case, False), run.organic(case)):
            self.assertNotIn('SECRET_GOLD_MARKER', prompt)
        self.assertTrue(run.task(case, True).endswith(run.task(case, False)))

    def test_organic_prompts_carry_no_evaluation_framing(self):
        framing = re.compile(r'\b(evals?|tests?|judge|rubric|score|benchmark|candidate|skill)\b', re.I)
        for case in run.CASES:
            prompt = run.organic(case)
            with self.subTest(case=case['id']):
                self.assertTrue(prompt.endswith(case['before'] + '\n'))
                self.assertNotRegex(prompt[:-len(case['before']) - 1], framing)

    def test_organic_arm_is_reported_only_when_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.assertNotIn('organic', self.report(out))
            (out / 'P01.organic.out.md').write_text(run.CASES[0]['before'])
            self.assertIn('organic', self.report(out))


if __name__ == '__main__':
    unittest.main()
