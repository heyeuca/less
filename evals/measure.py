#!/usr/bin/env python3
"""Run the held-out protocol locally with installed agent CLIs (no API keys).

  python3 evals/measure.py ROOT [--runs 3] [--families claude,codex] [--jobs 4] [--seed less]
                                 [--generate-only]

For every family and run it fills ROOT/<family>/run<k>/:
  1. protocol.py prompts (skipped when freeze.json already exists),
  2. each missing reply from that family's CLI, one fresh process per prompt
     in an empty temp directory, recording the CLI version, model, session
     setup, and every failed attempt in freeze.json,
  3. protocol.py blind (skipped when key.json exists),
  4. grades from the other family's CLI, one call per case, which sees only
     the blind case and the outputs labeled A and B,
then runs protocol.py report ROOT. Rerunning resumes: finished replies and
grades are kept. Commands come from evals/measure.json (LESS_MEASURE_CONFIG
overrides the path).
"""
import argparse
import json
import os
import re
import subprocess
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import protocol

CONFIG = json.loads(protocol.load(Path(os.environ.get(
    "LESS_MEASURE_CONFIG", protocol.ROOT / "evals/measure.json"))))
LOCK = threading.Lock()

GRADER_PROMPT = """You are grading two edits of the same input for an evaluation. The editor was asked to remove
unnecessary material while preserving meaning, behavior, and requested constraints.

Request: {request}

Input:
<input>
{input}
</input>

Material that must survive: {must_keep}

Output A:
<output_a>
{a}
</output_a>

Output B:
<output_b>
{b}
</output_b>

For each output decide:
- meaning_preserved: true if it keeps every fact, number, condition, qualifier, warning, and requested
  constraint of the input; false otherwise.
- damage: true if it lost, changed, or weakened good material (including the material that must survive),
  or added claims; false otherwise.
- removal_quality: "good" if it removed the unnecessary material, "partial" if some remains, "none" if it
  removed nothing that should go, "n/a" if the input had nothing to remove and the output left it unchanged.

Reply with JSON only, no prose and no code fence:
{{"A": {{"meaning_preserved": true, "damage": false, "removal_quality": "good"}}, "B": {{...}}}}
"""


def call(family, prompt):
    """Run one prompt through a family's CLI. Returns (reply, model) or raises RuntimeError."""
    spec = CONFIG["families"][family]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "last.txt"
        work = Path(tmp) / "work"
        work.mkdir()
        argv = [arg.replace("{out}", str(out)) for arg in spec["generate"]]
        done = subprocess.run(argv, input=prompt.encode("utf-8"), cwd=work, capture_output=True,
                              timeout=CONFIG.get("timeout_seconds", 600))
        stdout = done.stdout.decode("utf-8", "replace")
        stderr = done.stderr.decode("utf-8", "replace")
        if done.returncode != 0:
            raise RuntimeError(f"exit {done.returncode}: {(stderr or stdout).strip()[-400:]}")
        model = None
        if spec.get("model_from"):
            found = re.search(spec["model_from"], stdout + "\n" + stderr, re.M)
            model = found.group(1).strip() if found else None
        if spec.get("json"):
            data = json.loads(stdout)
            if data.get("is_error"):
                raise RuntimeError(str(data.get("result"))[-400:])
            model = model or ",".join(sorted(data.get("modelUsage") or {})) or None
            text = data.get("result", "")
        elif "{out}" in " ".join(spec["generate"]):
            text = out.read_bytes().decode("utf-8") if out.exists() else ""
        else:
            text = stdout
        if not text.strip():
            raise RuntimeError("empty reply")
        return text, model


def version(family):
    try:
        done = subprocess.run(CONFIG["families"][family]["version"], capture_output=True, timeout=60)
        return done.stdout.decode("utf-8", "replace").strip() or None
    except (OSError, subprocess.TimeoutExpired):
        return None


def update_freeze(out, **fields):
    with LOCK:
        path = out / "freeze.json"
        freeze = json.loads(protocol.load(path))
        attempts = fields.pop("attempt", None)
        freeze.update({k: v for k, v in fields.items() if v is not None})
        if attempts:
            freeze["attempts"] = (freeze.get("attempts") or []) + [attempts]
        protocol.save(path, json.dumps(freeze, indent=2, ensure_ascii=False) + "\n")


def generate(out, family, name, retries=1):
    target = out / name.replace(".md", ".out.md")
    if target.exists():
        return True
    prompt = protocol.load(out / name)
    for attempt in range(retries + 1):
        try:
            text, model = call(family, prompt)
            protocol.save(target, text)
            update_freeze(out, model=model)
            return True
        except (RuntimeError, ValueError, subprocess.TimeoutExpired, OSError) as error:
            update_freeze(out, attempt={"prompt": name, "try": attempt + 1, "error": str(error)[-400:]})
    return False


def parse_grade(text):
    found = re.search(r"\{.*\}", text, re.S)
    data = json.loads(found.group(0)) if found else {}
    grades = {label: data.get(label) or {} for label in "AB"}
    if not all(protocol.valid(g) for g in grades.values()):
        raise ValueError(f"unusable grade: {text.strip()[:200]}")
    return grades


def grade(out, family, case_id, retries=1):
    grader = CONFIG["grader_for"][family]
    path = out / "blind/grades.json"
    with LOCK:
        sheet = json.loads(protocol.load(path))
    if all(protocol.valid(sheet["grades"][f"{case_id}.{label}"]) for label in "AB"):
        return True
    case = json.loads(protocol.load(out / "blind/cases.json"))[case_id]
    prompt = GRADER_PROMPT.format(
        request=case["request"] or "(none)", input=case["input"], must_keep="; ".join(case["must_keep"]),
        a=protocol.load(out / f"blind/{case_id}.A.out.md"), b=protocol.load(out / f"blind/{case_id}.B.out.md"))
    for attempt in range(retries + 1):
        try:
            text, model = call(grader, prompt)
            grades = parse_grade(text)
        except (RuntimeError, ValueError, subprocess.TimeoutExpired, OSError) as error:
            update_freeze(out, attempt={"grade": case_id, "grader": grader, "try": attempt + 1,
                                        "error": str(error)[-400:]})
            continue
        with LOCK:
            sheet = json.loads(protocol.load(path))
            sheet["grader"] = {"family": grader, "model": model or sheet["grader"].get("model")}
            for label in "AB":
                sheet["grades"][f"{case_id}.{label}"] = {f: grades[label][f] for f in protocol.GRADE_FIELDS}
            protocol.save(path, json.dumps(sheet, indent=2) + "\n")
        return True
    return False


def measure(root, families, runs, jobs, seed, generate_only=False):
    dirs = [(family, root / family / f"run{k}") for family in families for k in range(1, runs + 1)]
    for family, out in dirs:
        if not (out / "freeze.json").exists():
            protocol.prompts(out)
        update_freeze(out, family=family, cli=version(family), sampling="CLI default",
                      session=CONFIG["families"][family]["session"],
                      runner={name: protocol.digest((protocol.ROOT / name).read_bytes())
                              for name in ("evals/measure.py", "evals/measure.json")})
    with ThreadPoolExecutor(jobs) as pool:
        work = [pool.submit(generate, out, family, f"{c['id']}.{arm}.md")
                for family, out in dirs for c in protocol.CASES for arm in protocol.ARMS]
        generated = all(f.result() for f in work)
    if not generated:
        raise SystemExit("some replies failed twice; see attempts in freeze.json and rerun to resume")
    if generate_only:
        print(f"Generated replies in {root}; rerun without --generate-only to blind, grade, and report")
        return None
    for family, out in dirs:
        if not (out / "key.json").exists():
            protocol.blind(out, f"{seed}:{family}:{out.name}")
    with ThreadPoolExecutor(jobs) as pool:
        work = [pool.submit(grade, out, family, c["id"]) for family, out in dirs for c in protocol.CASES]
        graded = all(f.result() for f in work)
    if not graded:
        raise SystemExit("some grades failed twice; see attempts in freeze.json and rerun to resume")
    return protocol.report(root)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", type=Path)
    parser.add_argument("--runs", type=int, default=protocol.PROTOCOL["min_runs_per_family"])
    parser.add_argument("--families", default=",".join(CONFIG["families"]))
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--seed", default="less")
    parser.add_argument("--generate-only", action="store_true",
                        help="stop after the replies, before blinding and grading")
    args = parser.parse_args()
    measure(args.root, args.families.split(","), args.runs, args.jobs, args.seed, args.generate_only)
