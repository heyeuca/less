"""Run with python3 -m unittest discover -s evals -p 'test_*.py'."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

import measure
import protocol

# A stand-in CLI: grades when it sees two outputs, otherwise returns the input unchanged.
FAKE = r'''
import json, re, sys
prompt = sys.stdin.read()
if "Output A:" in prompt:
    grade = {"meaning_preserved": True, "damage": False, "removal_quality": "n/a"}
    reply = json.dumps({"A": grade, "B": grade})
else:
    reply = prompt.split("requested constraints.\n\n", 1)[1]
    reply = reply.split("Your earlier answer:\n\n", 1)[-1][:-1]
mode = sys.argv[1]
if mode == "fail":
    sys.exit(3)
if mode == "file":
    open(sys.argv[2], "w", encoding="utf-8").write(reply)
    print("model: fake-file-1")
else:
    sys.stdout.write(reply)
'''


class MeasureTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        fake = self.dir / "fake.py"
        fake.write_text(FAKE, encoding="utf-8")
        self.saved = measure.CONFIG
        measure.CONFIG = {
            "families": {
                "one": {"generate": [sys.executable, str(fake), "stdout"], "version": [sys.executable, "--version"],
                        "session": "fake", "model": "fake-stdout-1"},
                "two": {"generate": [sys.executable, str(fake), "file", "{out}"], "version": [sys.executable, "--version"],
                        "model_from": "^model: (.+)$", "session": "fake", "model": "fake-stdout-1"},
            },
            "grader_for": {"one": "two", "two": "one"},
            "timeout_seconds": 60,
        }

    def tearDown(self):
        measure.CONFIG = self.saved
        self.tmp.cleanup()

    def run_measure(self, runs=3):
        with contextlib.redirect_stdout(io.StringIO()):
            return measure.measure(self.dir / "root", ["one", "two"], runs, 4, "t")

    def test_full_protocol_runs_and_records_setup(self):
        result = self.run_measure()
        self.assertTrue(result["protocol_complete"])
        self.assertTrue(result["absolute_gates_pass"])
        # A completed unchanged run resumes without replacing recorded provenance.
        first = protocol.load(self.dir / "root/two/run1/freeze.json")
        self.assertTrue(self.run_measure()["protocol_complete"])
        self.assertEqual(first, protocol.load(self.dir / "root/two/run1/freeze.json"))
        freeze = json.loads(protocol.load(self.dir / "root/two/run1/freeze.json"))
        self.assertEqual(freeze["family"], "two")
        self.assertEqual(freeze["model"], "fake-file-1")
        self.assertEqual(freeze["session"], "fake")
        sheet = json.loads(protocol.load(self.dir / "root/two/run1/blind/grades.json"))
        self.assertEqual(sheet["grader"]["family"], "one")
        first_label = next(iter(sheet["grades"]))
        sheet["grades"][first_label]["damage"] = True
        protocol.save(self.dir / "root/two/run1/blind/grades.json", json.dumps(sheet))
        with self.assertRaises(RuntimeError):
            protocol.run_report(self.dir / "root/two/run1", "two")

    def test_failures_are_recorded_and_a_rerun_resumes(self):
        good = measure.CONFIG["families"]["one"]["generate"]
        measure.CONFIG["families"]["one"]["generate"] = good[:2] + ["fail"]
        with self.assertRaises(SystemExit):
            self.run_measure(runs=1)
        freeze = json.loads(protocol.load(self.dir / "root/one/run1/freeze.json"))
        self.assertTrue(freeze["attempts"])
        self.assertTrue(any(self.dir.glob("root/two/run1/*.out.md")))
        measure.CONFIG["families"]["one"]["generate"] = good
        with self.assertRaises(RuntimeError):
            self.run_measure(runs=1)

    def test_grades_must_be_usable(self):
        with self.assertRaises(ValueError):
            measure.parse_grade('{"A": {"meaning_preserved": "true"}, "B": {}}')
        grades = measure.parse_grade('Sure: {"A": {"meaning_preserved": true, "damage": false, '
                                     '"removal_quality": "good"}, "B": {"meaning_preserved": false, '
                                     '"damage": true, "removal_quality": "none"}}')
        self.assertTrue(grades["B"]["damage"])

    def test_shipped_config_grades_across_families(self):
        for family, grader in self.saved["grader_for"].items():
            self.assertIn(family, self.saved["families"])
            self.assertNotEqual(family, grader)


if __name__ == "__main__":
    unittest.main()
