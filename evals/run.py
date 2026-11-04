#!/usr/bin/env python3
"""less eval runner (Python 3 stdlib only, no model calls).

  python3 evals/run.py prompts OUT
      Writes OUT/<id>.with.md (SKILL.md included) and OUT/<id>.without.md.
      Paste each into a fresh session of any model; save the reply as
      OUT/<id>.with.out.md or OUT/<id>.without.out.md.
      Also writes OUT/<id>.organic.json: the conversation a user would have, as
      role/content messages with no skill text or evaluation framing. The
      agent's own earlier answer is an assistant turn. Replay it in a session
      where the skill is installed, not pasted, and save the final reply as
      OUT/<id>.organic.out.md.

  python3 evals/run.py triggers OUT
      Writes OUT/triggers.md from triggers.json: each request, whether the skill
      should load, and an empty column for what happened in a fresh session.

  python3 evals/run.py preservation OUT
      Checks annotated spans and exact no-ops in both arms (and the organic arm
      when any of its replies exist); writes preservation.json.
      Does not replace semantic grading.

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
DESIGN = (ROOT / "skills/less/references/design.md").read_text()
TRIGGERS = json.loads((ROOT / "evals/triggers.json").read_text())
# What a user types when the case names no request of its own.
ORGANIC_REQUEST = "Tighten this up."
ORGANIC_FOLLOWUP = "Tighten your last answer."


def task(case, with_skill):
    parts = []
    if with_skill:
        skill = SKILL + ("\n<reference path=\"references/design.md\">\n" + DESIGN + "</reference>\n"
                         if case.get("format") in ("html", "jsx") else "")
        parts.append("Use this skill:\n\n<skill>\n" + skill + "</skill>\n")
    if case.get("prompt"):
        parts.append("The user's original request:\n\n" + case["prompt"] + "\n")
    if case.get("context"):
        parts.append("Context the user provided:\n\n" + case["context"] + "\n")
    command = "Remove unnecessary material while preserving meaning, behavior, and requested constraints."
    label = "Your earlier answer:\n\n" if case.get("author") == "assistant" else ""
    parts.append(command + "\n\n" + label + case["before"] + "\n")
    return "\n".join(parts)


def organic(case):
    """The conversation a user would have: no skill text and no evaluation framing.

    The agent's own earlier answer stays an assistant turn, and context sits
    beside the request instead of replacing it.
    """
    if case.get("author") == "assistant":
        question = "\n\n".join(filter(None, [case.get("context"), case["prompt"]]))
        return [{"role": "user", "content": question},
                {"role": "assistant", "content": case["before"]},
                {"role": "user", "content": ORGANIC_FOLLOWUP}]
    request = case.get("prompt") or ORGANIC_REQUEST
    content = "\n\n".join(filter(None, [request, case.get("context"), case["before"]]))
    return [{"role": "user", "content": content + "\n"}]


def prompts(out):
    out.mkdir(parents=True, exist_ok=True)
    for case in CASES:
        (out / f"{case['id']}.with.md").write_text(task(case, True))
        (out / f"{case['id']}.without.md").write_text(task(case, False))
        (out / f"{case['id']}.organic.json").write_text(
            json.dumps(organic(case), indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {3 * len(CASES)} prompts to {out}")


def triggers(out):
    out.mkdir(parents=True, exist_ok=True)
    rows = ["| # | request | should load less | loaded? |", "|---|---|---|---|"]
    for expected, key in (("yes", "should_trigger"), ("no", "should_not_trigger")):
        for request in TRIGGERS[key]:
            rows.append(f"| {len(rows) - 1} | {cell(request)} | {expected} | |")
    (out / "triggers.md").write_text("\n".join(rows) + "\n")
    print(f"Wrote {out / 'triggers.md'}")


def cell(text):
    return text.strip().replace("|", "\\|").replace("\n", "<br>") if text else ""


def read(path):
    return path.read_text() if path.exists() else "(missing)"


def preservation(out):
    """Exact regression backstops, not a semantic quality score."""
    reports = {}
    arms = ["with", "without"]
    if any(out.glob("*.organic.out.md")):
        arms.append("organic")
    for suffix in arms:
        rows = []
        for case in CASES:
            if not any(k in case for k in ("protected_spans", "must_remove_spans", "exact_noop")):
                continue
            path = out / f"{case['id']}.{suffix}.out.md"
            # Preserve line endings and final newlines for exact no-op checks.
            output = path.read_bytes().decode("utf-8") if path.exists() else None
            rows.append({
                "id": case["id"],
                "missing": output is None,
                "preserved": (output is not None and all(
                    span in output for span in case["protected_spans"]))
                    if case.get("protected_spans") else None,
                "removed": (output is not None and all(
                    span not in output for span in case["must_remove_spans"]))
                    if case.get("must_remove_spans") else None,
                "exact_noop": output == case["before"] if case.get("exact_noop") else None,
            })
        summary = {}
        for metric in ("preserved", "removed", "exact_noop"):
            applicable = [row[metric] for row in rows if row[metric] is not None]
            summary[metric] = {"passed": sum(applicable), "total": len(applicable)}
        reports[suffix] = {"summary": summary, "cases": rows}
    (out / "preservation.json").write_text(json.dumps(reports, indent=2) + "\n")
    print(f"Wrote {out / 'preservation.json'}")


def sheet(out):
    rows = [
        "| id | category | must keep | bad after | with skill | without skill | with pass? | without pass? |",
        "|---|---|---|---|---|---|---|---|",
    ]
    gates = {}
    for suffix in ("with", "without"):
        path = out / f"design-{suffix}.json"
        if path.exists():
            gates[suffix] = json.loads(path.read_text())
    for case in CASES:
        keep = "<br>".join("[ ] " + cell(k) for k in case["must_keep"]) or "reference: " + cell(case["after"])
        rows.append("| " + " | ".join([
            case["id"],
            cell(case["category"]),
            keep,
            cell(case.get("bad_after", "")),
            cell(read(out / f"{case['id']}.with.out.md")),
            cell(read(out / f"{case['id']}.without.out.md")),
            gates.get("with", {}).get(case["id"], ""),
            gates.get("without", {}).get(case["id"], ""),
        ]) + " |")
    (out / "sheet.md").write_text("\n".join(rows) + "\n")
    print(f"Wrote {out / 'sheet.md'}")
    quality = [
        "| id | arm | removal quality | meaning / behavior preserved | damage to good material | evidence |",
        "|---|---|---|---|---|---|",
    ]
    for case in CASES:
        for suffix in ("with", "without"):
            quality.append(f"| {case['id']} | {suffix} | | | | |")
    (out / "quality.md").write_text("\n".join(quality) + "\n")
    print(f"Wrote {out / 'quality.md'}")


if __name__ == "__main__":
    commands = {"prompts": prompts, "triggers": triggers, "sheet": sheet, "preservation": preservation}
    if len(sys.argv) != 3 or sys.argv[1] not in commands:
        sys.exit(__doc__)
    commands[sys.argv[1]](Path(sys.argv[2]))
