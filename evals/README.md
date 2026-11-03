# Evaluating removal without damaging good material

Generate paired prompts with `python3 evals/run.py prompts OUT`. Store replies
as `OUT/ID.with.out.md` and `OUT/ID.without.out.md`, then run:

```sh
python3 evals/run.py preservation OUT
python3 evals/run.py sheet OUT
python3 -m unittest discover -s evals -p 'test_*.py'
```

The unit tests also hold `SKILL.md` and `references/design.md` to word budgets
(`test_budget.py`), because the skill is loaded on every invocation. A new rule
should merge with or replace an existing one; raise a budget only as a
deliberate decision. CI runs these tests and the design checker
(`node check.mjs self`, `npm test`) on every pull request.

`preservation.json` reports exact checks for annotated cases in each arm:

- `removed`: all specified unnecessary spans disappeared.
- `preserved`: all specified good spans remain verbatim.
- `exact_noop`: a clean input was returned byte-for-byte unchanged.

Missing replies fail every applicable check; non-applicable metrics are null.
No-op equality includes whitespace and final newlines. Save the raw reply without
adding a newline or stripping formatting. Do not strip output fences to make a
prose no-op pass. Checks cover only annotated cases, not the whole corpus.

These checks do not prove semantic preservation or successful repair: replacing
filler with different filler can pass removal, and appending a contradiction can
pass span preservation. Independently grade meaning/behavior preservation,
actual removal quality, and unintended damage to good material in the generated `quality.md` worksheet (use N/A for removal on clean cases).
Report these separately from reduction counts and exact no-op rates; do not
collapse them into one quality score. Inspect per-case failures in both arms.

P01–P10 are five paired prose regressions: empty emphasis versus uncertainty,
scope and approximation, repeated endings versus actionable endings, causal
qualifications, and obligation. Each pair has a reduction case and a clean
protection case. Good adjacent sentences are exact protected spans. Add a
removal example and a legitimate-use protection example together when adding a
new deletion rule; use the same approach for code and UI regressions.

The new cases are explicitly `tune`: their answers informed the instructions.
Existing cases are also development/regression evidence, not held-out evidence.
Before claiming quality gains, freeze the skill and grader, collect unseen
cases, and compare both arms using blind candidate labels and an independent
judge. Retain raw outputs and case-level judgments. Do not tune on that report.

The contextual-editing, paired-protection, and separate-metrics ideas were
informed by [UNSLOP's core contract](https://github.com/theclaymethod/unslop/blob/17ed39c9d0b522f44190ff0c6233867eadee192a/references/core-contract.md)
and [evaluation protocol](https://github.com/theclaymethod/unslop/blob/17ed39c9d0b522f44190ff0c6233867eadee192a/evals/CORE-BENCHMARK.md).
The cases and implementation here are written for less; no scanner, voice
preset, or rewrite pipeline is imported.
