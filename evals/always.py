#!/usr/bin/env python3
"""Always-on cases (Python 3 stdlib only, no model calls).

always-on/AGENTS.md is a separate rule set from the editing skill: it shapes
new output instead of cutting existing text. These cases check that it removes
filler without leaving out what the reader needs.

  python3 evals/always.py prompts OUT
      Writes OUT/<id>.always.md (the rules as an AGENTS.md, then the request)
      and OUT/<id>.plain.md (the request alone). Run each in a fresh session
      and save the reply as OUT/<id>.always.out.md or OUT/<id>.plain.out.md.

  python3 evals/always.py sheet OUT
      Writes OUT/always.md: per case and arm, the reply and one checkbox per
      must_include and must_not_include item for a grader.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = (ROOT / "always-on/AGENTS.md").read_bytes().decode("utf-8")
CASES = json.loads((ROOT / "evals/always.json").read_bytes().decode("utf-8"))["cases"]
ARMS = ("always", "plain")


def save(path, text):
    path.write_bytes(text.encode("utf-8"))


def prompt(case, arm):
    request = case["prompt"] + "\n"
    if arm == "plain":
        return request
    return '<file path="AGENTS.md">\n' + RULES + "</file>\n\n" + request


def prompts(out):
    if out.is_dir() and any(out.iterdir()):
        raise SystemExit(f"{out} is not empty; use a new output directory")
    out.mkdir(parents=True, exist_ok=True)
    for case in CASES:
        for arm in ARMS:
            save(out / f"{case['id']}.{arm}.md", prompt(case, arm))
    print(f"Wrote {len(ARMS) * len(CASES)} prompts to {out}")


def sheet(out):
    lines = ["# Always-on grading", ""]
    for case in CASES:
        for arm in ARMS:
            path = out / f"{case['id']}.{arm}.out.md"
            reply = path.read_bytes().decode("utf-8") if path.exists() else "(missing)"
            lines += [f"## {case['id']} {arm}", "", case["prompt"], "", "```", reply.rstrip("\n"), "```", ""]
            lines += [f"- [ ] includes: {item}" for item in case["must_include"]]
            lines += [f"- [ ] free of: {item}" for item in case["must_not_include"]]
            lines.append("")
    save(out / "always.md", "\n".join(lines))
    print(f"Wrote {out / 'always.md'}")


if __name__ == "__main__":
    commands = {"prompts": prompts, "sheet": sheet}
    if len(sys.argv) != 3 or sys.argv[1] not in commands:
        sys.exit(__doc__)
    commands[sys.argv[1]](Path(sys.argv[2]))
