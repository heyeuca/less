"""Run with python3 -m unittest discover -s evals -p 'test_*.py'."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import protocol
import run


def reference(case):
    return case["before"] if case["after"] == "unchanged" else case["after"]


class ProtocolTest(unittest.TestCase):
    def quiet(self, fn, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            return fn(*args)

    def make_run(self, root, family, name, with_reply=reference, grader="other"):
        out = root / family / name
        self.quiet(protocol.prompts, out)
        for case in protocol.CASES:
            protocol.save(out / f"{case['id']}.with.out.md", with_reply(case))
            protocol.save(out / f"{case['id']}.without.out.md", case["before"])
        self.quiet(protocol.blind, out, "7")
        sheet = json.loads(protocol.load(out / "blind/grades.json"))
        sheet["grader"] = {"family": grader, "model": "m"}
        for grade in sheet["grades"].values():
            grade.update(meaning_preserved=True, damage=False, removal_quality="good")
        protocol.save(out / "blind/grades.json", json.dumps(sheet))
        return out

    def test_heldout_cases_are_new_and_self_consistent(self):
        tuned = {c["id"] for c in run.CASES} | {c["before"] for c in run.CASES}
        for case in protocol.CASES:
            with self.subTest(case=case["id"]):
                self.assertEqual(case["split"], "heldout")
                self.assertNotIn(case["id"], tuned)
                self.assertNotIn(case["before"], tuned)
                row = protocol.checks(case, reference(case))
                self.assertTrue(row["preserved"])
                self.assertIn(row["removed"], (True, None))
                self.assertIn(row["exact_noop"], (True, None))

    def test_blind_hides_the_arm(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.make_run(Path(tmp), "fam", "run1")
            names = " ".join(p.name for p in (out / "blind").iterdir())
            self.assertNotIn("with", names)
            blind_text = "".join(protocol.load(p) for p in (out / "blind").glob("*.json"))
            self.assertNotIn('"with"', blind_text)
            key = json.loads(protocol.load(out / "key.json"))
            self.assertEqual(sorted(set(key.values())), ["with", "without"])

    def test_complete_protocol_passes_gates_per_family(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for family in ("alpha", "beta"):
                for n in (1, 2, 3):
                    self.make_run(root, family, f"run{n}")
            result = self.quiet(protocol.report, root)
            self.assertTrue(result["protocol_complete"])
            self.assertTrue(result["all_graded"])
            self.assertTrue(result["absolute_gates_pass"])
            self.assertEqual(sorted(result["families"]), ["alpha", "beta"])

    def test_one_family_is_incomplete_and_damage_fails_the_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_run(root, "alpha", "run1", with_reply=lambda c: "")
            result = self.quiet(protocol.report, root)
            self.assertFalse(result["protocol_complete"])
            self.assertFalse(result["absolute_gates_pass"])

    def test_grader_from_the_same_family_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_run(root, "alpha", "run1", grader="alpha")
            with self.assertRaises(SystemExit):
                self.quiet(protocol.report, root)

    def test_stale_run_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = self.make_run(root, "alpha", "run1")
            freeze = json.loads(protocol.load(out / "freeze.json"))
            freeze["inputs"]["evals/heldout.json"] = "stale"
            protocol.save(out / "freeze.json", json.dumps(freeze))
            with self.assertRaises(SystemExit):
                self.quiet(protocol.report, root)

    def test_edited_prompt_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = self.make_run(root, "alpha", "run1")
            name = f"{protocol.CASES[0]['id']}.with.md"
            protocol.save(out / name, protocol.load(out / name) + "Also add a summary.\n")
            with self.assertRaises(SystemExit):
                self.quiet(protocol.report, root)

    def test_reply_edited_after_blinding_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = self.make_run(root, "alpha", "run1")
            name = f"{protocol.CASES[0]['id']}.with.out.md"
            protocol.save(out / name, protocol.load(out / name) + " Also, delete the backups.")
            with self.assertRaises(SystemExit):
                self.quiet(protocol.report, root)

    def test_incomplete_grades_never_pass(self):
        for damage in ("drop label", "drop field", "string boolean"):
            with self.subTest(damage=damage), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                for family in ("alpha", "beta"):
                    for n in (1, 2, 3):
                        out = self.make_run(root, family, f"run{n}")
                sheet = json.loads(protocol.load(out / "blind/grades.json"))
                label = next(iter(sheet["grades"]))
                if damage == "drop label":
                    del sheet["grades"][label]
                elif damage == "drop field":
                    del sheet["grades"][label]["damage"]
                else:
                    sheet["grades"][label]["damage"] = "false"
                protocol.save(out / "blind/grades.json", json.dumps(sheet))
                result = self.quiet(protocol.report, root)
                self.assertFalse(result["all_graded"])
                self.assertFalse(result["protocol_complete"])
                self.assertFalse(result["absolute_gates_pass"])

    def test_prompts_refuse_a_used_directory_and_blind_needs_every_reply(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.quiet(protocol.prompts, out)
            with self.assertRaises(SystemExit):
                self.quiet(protocol.prompts, out)
            with self.assertRaises(SystemExit):
                self.quiet(protocol.blind, out, "1")


if __name__ == "__main__":
    unittest.main()
