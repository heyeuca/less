#!/usr/bin/env python3
"""less eval runner (Python 3 stdlib only, no model calls).

  python3 evals/run.py prompts OUT
      Writes OUT/<id>.with.md (SKILL.md included) and OUT/<id>.without.md.
      Paste each into a fresh session of any model; save the reply as
      OUT/<id>.with.out.md or OUT/<id>.without.out.md.

  python3 evals/run.py sheet OUT
      Writes OUT/sheet.md: one row per case with the must-keep checklist,
      both outputs, and empty pass/fail columns for a human or model grader.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = json.loads((ROOT / "evals/evals.json").read_text())["evals"]
SKILL = (ROOT / "skills/less/SKILL.md").read_text()


def task(case, with_skill):
    parts = []
    if with_skill:
        parts.append("Use this skill:\n\n<skill>\n" + SKILL + "</skill>\n")
    if case.get("prompt"):
        parts.append("The user's original request:\n\n" + case["prompt"] + "\n")
    command = "/less" if with_skill else "Make this less verbose."
    parts.append(command + "\n\n" + case["before"] + "\n")
    return "\n".join(parts)


def prompts(out):
    out.mkdir(parents=True, exist_ok=True)
    for case in CASES:
        (out / f"{case['id']}.with.md").write_text(task(case, True))
        (out / f"{case['id']}.without.md").write_text(task(case, False))
    print(f"Wrote {2 * len(CASES)} prompts to {out}")


def cell(text):
    return text.strip().replace("|", "\\|").replace("\n", "<br>") if text else ""


def read(path):
    return path.read_text() if path.exists() else "(missing)"


def sheet(out):
    rows = [
        "| id | category | must keep | bad after | with skill | without skill | with pass? | without pass? |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for case in CASES:
        keep = "<br>".join("[ ] " + cell(k) for k in case["must_keep"]) or "reference: " + cell(case["after"])
        rows.append("| " + " | ".join([
            case["id"],
            cell(case["category"]),
            keep,
            cell(case.get("bad_after", "")),
            cell(read(out / f"{case['id']}.with.out.md")),
            cell(read(out / f"{case['id']}.without.out.md")),
            "",
            "",
        ]) + " |")
    (out / "sheet.md").write_text("\n".join(rows) + "\n")
    print(f"Wrote {out / 'sheet.md'}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("prompts", "sheet"):
        sys.exit(__doc__)
    {"prompts": prompts, "sheet": sheet}[sys.argv[1]](Path(sys.argv[2]))
