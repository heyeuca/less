#!/usr/bin/env python3
"""Repository-shaped code cases (Python 3 stdlib only, no model calls).

Each case in evals/repos/<id>/ is a small project: a module, a caller or
export, and tests. The agent needs file access, so these run as organic
sessions with the skill installed, not as pasted prompts.

  python3 evals/repos.py prepare OUT
      Copies each case's before/ to OUT/<id>/ and writes OUT/<id>.task.md
      with the request. Open a fresh agent session in OUT/<id>/, send the
      request, and let the agent edit the files in place.

  python3 evals/repos.py grade OUT
      Checks each OUT/<id>/: the used helper or option is kept, the unused
      one is gone, and the tests still pass. Writes OUT/repos.json. Whether
      the agent ran the tests is read from its transcript, not the files, so
      ran_tests is left null for the grader to fill in.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "repos"
CASES = [json.loads((d / "case.json").read_bytes().decode("utf-8"))
         for d in sorted(ROOT.iterdir()) if (d / "case.json").exists()]


def prepare(out):
    out.mkdir(parents=True, exist_ok=True)
    for case in CASES:
        target = out / case["id"]
        if target.exists():
            raise SystemExit(f"{target} exists; use a new output directory")
        shutil.copytree(ROOT / case["id"] / "before", target)
        (out / f"{case['id']}.task.md").write_bytes((case["prompt"] + "\n").encode("utf-8"))
    print(f"Prepared {len(CASES)} repositories in {out}")


def found(folder, check):
    path = folder / check["file"]
    return path.exists() and re.search(check["pattern"], path.read_bytes().decode("utf-8")) is not None


def grade_one(case, folder):
    if not folder.is_dir():
        return {"missing": True, "kept": False, "removed": False, "tests_pass": False, "ran_tests": None}
    tests = subprocess.run([sys.executable, *case["test"]], cwd=folder, capture_output=True, timeout=120)
    return {
        "missing": False,
        "kept": all(found(folder, c) for c in case["must_keep"]),
        "removed": not any(found(folder, c) for c in case["must_remove"]),
        "tests_pass": tests.returncode == 0,
        "ran_tests": None,
    }


def grade(out):
    report = {case["id"]: grade_one(case, out / case["id"]) for case in CASES}
    (out / "repos.json").write_bytes((json.dumps(report, indent=2) + "\n").encode("utf-8"))
    print(f"Wrote {out / 'repos.json'}")


if __name__ == "__main__":
    commands = {"prepare": prepare, "grade": grade}
    if len(sys.argv) != 3 or sys.argv[1] not in commands:
        sys.exit(__doc__)
    commands[sys.argv[1]](Path(sys.argv[2]))
