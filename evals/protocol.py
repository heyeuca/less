#!/usr/bin/env python3
"""Held-out remeasurement protocol (Python 3 stdlib only, no model calls).

Layout: ROOT/<family>/<run>/, one directory per model family and run.

  python3 evals/protocol.py prompts DIR
      DIR must be empty. Writes <id>.with.md and <id>.without.md for every
      held-out case, and freeze.json: hashes of the skill, runner, protocol,
      and cases, a hash per prompt, and empty family, model, sampling, and
      session fields to fill in. Save replies as <id>.with.out.md and
      <id>.without.out.md.

  python3 evals/protocol.py blind DIR SEED
      Needs every reply. Copies them to DIR/blind/<id>.A.out.md and
      <id>.B.out.md in a seeded random order, with each case's request and
      input in DIR/blind/cases.json, and a grades.json to fill in. The arm
      mapping goes to DIR/key.json. Give the grader only DIR/blind/.

  python3 evals/protocol.py report ROOT
      Reads every ROOT/<family>/<run>/. Refuses a run whose inputs changed
      since its prompts. Checks protected spans, removals, and exact no-ops
      per arm, unblinds completed grades, applies the absolute gates in
      protocol.json to the with-skill arm, and writes ROOT/report.json per
      family, run, and case. Families are never pooled.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

import run

ROOT = run.ROOT
PROTOCOL = json.loads((ROOT / "evals/protocol.json").read_bytes().decode("utf-8"))
CASES = json.loads((ROOT / "evals/heldout.json").read_bytes().decode("utf-8"))["evals"]
FROZEN = ["skills/less/SKILL.md", "skills/less/references/design.md", "evals/run.py",
          "evals/protocol.py", "evals/protocol.json", "evals/heldout.json"]
ARMS = ("with", "without")
GRADE_FIELDS = ("meaning_preserved", "damage", "removal_quality")


def load(path):
    return path.read_bytes().decode("utf-8")


def save(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inputs():
    return {name: digest((ROOT / name).read_bytes()) for name in FROZEN}


def prompts(out):
    if out.is_dir() and any(out.iterdir()):
        raise SystemExit(f"{out} is not empty; use a new run directory")
    written = {f"{c['id']}.{arm}.md": run.task(c, arm == "with") for c in CASES for arm in ARMS}
    for name, text in written.items():
        save(out / name, text)
    freeze = {"inputs": inputs(), "prompts": {n: digest(t.encode("utf-8")) for n, t in written.items()},
              "family": None, "model": None, "sampling": None, "session": None}
    save(out / "freeze.json", json.dumps(freeze, indent=2) + "\n")
    print(f"Wrote {len(written)} prompts and freeze.json to {out}")


def reply(out, case, arm):
    path = out / f"{case['id']}.{arm}.out.md"
    return load(path) if path.exists() else None


def blind(out, seed):
    missing = [f"{c['id']}.{arm}" for c in CASES for arm in ARMS if reply(out, c, arm) is None]
    if missing:
        raise SystemExit("missing replies: " + ", ".join(missing))
    key, grades, cases = {}, {}, {}
    for case in CASES:
        arms = list(ARMS)
        random.Random(f"{seed}:{case['id']}").shuffle(arms)
        for label, arm in zip("AB", arms):
            save(out / "blind" / f"{case['id']}.{label}.out.md", reply(out, case, arm))
            key[f"{case['id']}.{label}"] = arm
            grades[f"{case['id']}.{label}"] = {field: None for field in GRADE_FIELDS}
        cases[case["id"]] = {"request": case.get("prompt"), "input": case["before"], "must_keep": case["must_keep"]}
    save(out / "blind" / "cases.json", json.dumps(cases, indent=2, ensure_ascii=False) + "\n")
    save(out / "blind" / "grades.json", json.dumps({
        "grader": {"family": None, "model": None},
        "scale": {"meaning_preserved": "true/false", "damage": "true if good material was lost or changed",
                  "removal_quality": "good / partial / none / n/a for clean inputs"},
        "grades": grades}, indent=2) + "\n")
    save(out / "key.json", json.dumps(key, indent=2) + "\n")
    print(f"Wrote {out / 'blind'}; keep {out / 'key.json'} from the grader")


def valid(grade):
    """A finished grade: true/false for the yes-no fields (not "false" strings), a label for quality."""
    return (all(isinstance(grade.get(f), bool) for f in ("meaning_preserved", "damage"))
            and grade.get("removal_quality") in ("good", "partial", "none", "n/a"))


def checks(case, output):
    return {
        "missing": output is None,
        "preserved": output is not None and all(s in output for s in case["protected_spans"]),
        "removed": (output is not None and not any(s in output for s in case["must_remove_spans"]))
        if case["must_remove_spans"] else None,
        "exact_noop": output == case["before"] if case["exact_noop"] else None,
    }


def score(rows, metric):
    values = [row[metric] for row in rows if row.get(metric) is not None]
    return {"passed": sum(bool(v) for v in values), "total": len(values)}


def run_report(out, family):
    freeze = json.loads(load(out / "freeze.json"))
    changed = [n for n, d in inputs().items() if freeze["inputs"].get(n) != d]
    if changed:
        raise SystemExit(f"{out}: {', '.join(changed)} changed since its prompts; report at that commit")
    edited = [n for n, d in freeze["prompts"].items()
              if not (out / n).exists() or digest((out / n).read_bytes()) != d]
    if edited:
        raise SystemExit(f"{out}: prompt files differ from freeze.json: {', '.join(edited)}")
    graded = {}
    if (out / "blind/grades.json").exists() and (out / "key.json").exists():
        sheet = json.loads(load(out / "blind/grades.json"))
        key = json.loads(load(out / "key.json"))
        # Count grades only when every blind label has every field filled in.
        if set(sheet["grades"]) == set(key) and all(valid(g) for g in sheet["grades"].values()):
            # A grade judges the blind copy; refuse it if that copy no longer matches the reply.
            stale = [label for label, arm in key.items()
                     if not (out / "blind" / f"{label}.out.md").exists()
                     or load(out / "blind" / f"{label}.out.md") != reply(out, {"id": label.split(".")[0]}, arm)]
            if stale:
                raise SystemExit(f"{out}: replies changed after blinding: {', '.join(stale)}")
            graded = {(label.split(".")[0], key[label]): g for label, g in sheet["grades"].items()}
            grader = sheet["grader"].get("family")
            if not grader or grader == family:
                raise SystemExit(f"{out}: the grader must name a family other than {family}")
    arms = {}
    for arm in ARMS:
        rows = []
        for case in CASES:
            row = {"id": case["id"], **checks(case, reply(out, case, arm))}
            row.update(graded.get((case["id"], arm), {}))
            rows.append(row)
        arms[arm] = {"summary": {m: score(rows, m) for m in ("preserved", "removed", "exact_noop", "meaning_preserved")}
                     | {"damage": {"cases": sum(bool(r.get("damage")) for r in rows), "graded": bool(graded)}},
                     "cases": rows}
    s = arms["with"]["summary"]
    arms["gates"] = {
        "preserved": s["preserved"]["passed"] == s["preserved"]["total"],
        "exact_noop": s["exact_noop"]["passed"] == s["exact_noop"]["total"],
        "damage": None if not graded else s["damage"]["cases"] == 0,
    }
    return arms


def report(root):
    families = {}
    for family_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        runs = {r.name: run_report(r, family_dir.name)
                for r in sorted(family_dir.iterdir()) if (r / "freeze.json").exists()}
        if runs:
            families[family_dir.name] = runs
    # Ungraded runs don't count: completion and the damage gate both need every run blind-graded.
    graded = bool(families) and all(r["gates"]["damage"] is not None for runs in families.values() for r in runs.values())
    complete = graded and (len(families) >= PROTOCOL["min_families"]
                           and all(len(runs) >= PROTOCOL["min_runs_per_family"] for runs in families.values()))
    gates = bool(families) and all(v is True for runs in families.values() for r in runs.values() for v in r["gates"].values())
    result = {"protocol_complete": complete, "all_graded": graded, "absolute_gates_pass": gates,
              "families": families}
    save(root / "report.json", json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    for family, runs in families.items():
        for name, r in runs.items():
            w = r["with"]["summary"]
            print(f"{family}/{name}: with preserved {w['preserved']['passed']}/{w['preserved']['total']}, "
                  f"noop {w['exact_noop']['passed']}/{w['exact_noop']['total']}, gates {r['gates']}")
    print(f"protocol complete: {complete}; all graded: {graded}; absolute gates pass: {gates}")
    return result


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["blind"] and len(args) == 3:
        blind(Path(args[1]), args[2])
    elif len(args) == 2 and args[0] in ("prompts", "report"):
        {"prompts": prompts, "report": report}[args[0]](Path(args[1]))
    else:
        sys.exit(__doc__)
