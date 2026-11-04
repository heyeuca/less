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
        return json.loads(run.load(out / 'preservation.json'))

    def test_references_and_missing_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            for case in run.CASES:
                if 'protected_spans' in case:
                    run.save(out / f"{case['id']}.with.out.md", case['after'])
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
            run.save(out / 'P01.with.out.md', cases['P01']['before'])
            run.save(out / 'P02.with.out.md', cases['P02']['before'] + '\n')
            run.save(out / 'P03.with.out.md', '50%의 요청이 실패합니다.')
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
            run.save(out / 'P09.with.out.md',
                'Some inputs should be validated. Secrets must never appear in logs.')
            rows = {row['id']: row for row in self.report(out)['with']['cases']}
            self.assertFalse(rows['P09']['preserved'])
            self.assertTrue(rows['P09']['removed'])

    def test_removal_span_survives_whitespace_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            run.save(out / 'P09.with.out.md',
                'For completeness:\nAll inputs must be validated. Secrets must never appear in logs.')
            rows = {row['id']: row for row in self.report(out)['with']['cases']}
            self.assertTrue(rows['P09']['preserved'])
            self.assertFalse(rows['P09']['removed'])

    def test_annotations_never_enter_generation_prompts(self):
        cases = {case['id']: case for case in run.CASES}
        # P14 is user-authored; E01 is the agent's own answer, a separate organic path.
        for case_id in ('P14', 'E01'):
            case = dict(cases[case_id], protected_spans=['SECRET_GOLD_MARKER'])
            with self.subTest(case=case_id):
                for prompt in (run.task(case, True), run.task(case, False), json.dumps(run.organic(case))):
                    self.assertNotIn('SECRET_GOLD_MARKER', prompt)
                self.assertTrue(run.task(case, True).endswith(run.task(case, False)))

    def test_organic_prompts_carry_no_evaluation_framing(self):
        framing = re.compile(r'\b(evals?|tests?|judge|rubric|score|benchmark|candidate|skill)\b', re.I)
        for case in run.CASES:
            with self.subTest(case=case['id']):
                for message in run.organic(case):
                    text = message['content'].replace(case['before'], '')
                    self.assertNotRegex(text, framing)

    def test_organic_conversations_keep_authorship(self):
        for case in run.CASES:
            messages = run.organic(case)
            roles = [m['role'] for m in messages]
            with self.subTest(case=case['id']):
                if case.get('author') == 'assistant':
                    # The agent's own answer is its turn, after the question it answered.
                    self.assertEqual(roles, ['user', 'assistant', 'user'])
                    self.assertEqual(messages[1]['content'], case['before'])
                    self.assertIn(case['prompt'], messages[0]['content'])
                else:
                    self.assertEqual(roles, ['user'])
                    self.assertTrue(messages[0]['content'].endswith(case['before'] + '\n'))

    def test_context_never_replaces_the_request(self):
        cases = [case for case in run.CASES if case.get('context')]
        self.assertTrue(cases)
        for case in cases:
            with self.subTest(case=case['id']):
                self.assertTrue(case.get('prompt'))
                self.assertNotEqual(case['prompt'], case['context'])
                self.assertIn(case['prompt'], run.organic(case)[0]['content'])
                self.assertIn(case['context'], run.task(case, False))

    def test_runner_io_is_utf8_on_any_locale(self):
        source = run.load(Path(run.__file__))
        for call in ('read_text(', 'write_text(', 'open('):
            self.assertNotIn(call, source)

    def test_run_record_hashes_inputs_and_every_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                run.prompts(out)
            record = json.loads(run.load(out / 'run.json'))
            self.assertEqual(sorted(record['inputs']), sorted(run.FROZEN))
            prompts = sorted(p.name for p in out.iterdir() if p.name != 'run.json')
            self.assertEqual(sorted(record['prompts']), prompts)
            for name, digest in record['prompts'].items():
                self.assertEqual(run.sha256((out / name).read_bytes()), digest)
            for field in run.RUN_FIELDS:
                self.assertIsNone(record[field])
            # A filled-in record is never overwritten.
            with self.assertRaises(SystemExit):
                run.prompts(out)
        # Nor are replies from a run that predates run.json.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            run.save(out / 'P01.with.out.md', 'old reply')
            with self.assertRaises(SystemExit):
                run.prompts(out)

    def test_grading_refuses_changed_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            recorded = run.inputs()
            run.save(out / 'run.json', json.dumps({'inputs': recorded}))
            self.report(out)
            recorded['evals/evals.json'] = 'stale'
            run.save(out / 'run.json', json.dumps({'inputs': recorded}))
            for command in (run.preservation, run.sheet):
                with self.subTest(command=command.__name__), self.assertRaises(SystemExit):
                    command(out)

    def test_results_without_run_json_are_marked_unverified(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.assertFalse(self.report(out)['verified'])
            with contextlib.redirect_stdout(io.StringIO()):
                run.sheet(out)
            self.assertTrue(run.load(out / 'sheet.md').startswith('UNVERIFIED'))
            run.save(out / 'run.json', json.dumps({'inputs': run.inputs()}))
            self.assertTrue(self.report(out)['verified'])

    def test_sheet_cells_drop_carriage_returns(self):
        self.assertEqual(run.cell('a\r\nb'), 'a<br>b')

    def test_organic_arm_is_reported_only_when_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.assertNotIn('organic', self.report(out))
            run.save(out / 'P01.organic.out.md', run.CASES[0]['before'])
            self.assertIn('organic', self.report(out))


if __name__ == '__main__':
    unittest.main()
