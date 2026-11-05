# Follow-up protocol-v2 candidate measurement

This is a completed candidate experiment, not a release-quality claim. Ten
newly authored V cases, two local CLI families, three runs per family, with
blind cross-family grading. Each family generated 60 replies (30 per arm).
There are ten distinct inputs, not thirty independent cases. The generating
and grading model identity, CLI version, session, prompt/output hashes, and
failed attempts are in the per-run freeze records.

| Metric | Claude with / without | Codex with / without |
|---|---|---|
| Protected spans (30) | 27 / 20 | 25 / 15 |
| Required removals (15) | 15 / 8 | 15 / 15 |
| Raw exact no-ops (15) | 6 / 0 | 7 / 0 |
| Presentation no-ops (15) | 12 / 0 | 7 / 0 |
| Meaning preserved, grader (30) | 27 / 18 | 28 / 18 |
| Damaged outputs, grader (30) | 3 / 27 | 8 / 15 |

`protocol_complete: true`, `all_graded: true`, `absolute_gates_pass: false`.
The shipping reporter additionally verifies grader receipts against the parsed
grades; this final hardening postdates the archived measurement snapshot.

No output was dropped from the denominator and no failure was reclassified to
make the gates pass. V06's clean local variable was inlined by both families
in all runs. Codex also changed V02 in two runs and echoed the evaluation
instruction in V08 in all three runs. Grader assessments are model judgments.

The candidate narrowed the heading and reduced-motion rules. Their tune
pairs pass 6/6 each, and fresh V07/V08 retain all protected headings and links,
while V09/V10 retain required copy and motion controls. However V08 is not a
no-op, and the overall predeclared acceptance gate fails. Therefore the
candidate rules are **not adopted**. Shipping SKILL.md and design.md remain
unchanged. The experiment resolves the decision requested in #54 by retaining
the conservative rules, rather than silently weakening its acceptance gate.
The other #53 failure shapes are encoded as P17–P22 tune regressions; they
have not been used to rewrite the skill in response to these held-out results.

## Evidence and replay

`followups-v2/` contains all prompts, raw replies, blind copies, arm keys,
raw successful grader responses, per-call receipts, and report.json. It also
contains `snapshot/` with the exact frozen candidate inputs and execution
code. To regenerate the report without changing the shipping skill:

```sh
python3 evals/results/followups-v2/snapshot/evals/protocol.py report evals/results/followups-v2
```

The report command at the repository root intentionally refuses this candidate
run because its skill hashes differ from the shipping rules. Historical
v0.3.4 artifacts are unmodified; replay those at their original commit.

V09 and V10 are markup probes through the core skill prompt (no `format`
routing), so they are not a full installed-skill/design-reference measurement.
D21/D22 exercise the full design reference separately. Organic invocation,
always-on output, and broad UI quality remain outside this experiment.

An earlier development run on surface variants of retired H cases was stopped
and superseded before publication. Its temporary files are not treated as
held-out evidence. The V corpus was authored before its candidate outputs were
viewed and has now been consumed; retire it before the next optimization claim.

## Session isolation

Claude runs here loaded the account's MCP servers, settings files, and
auto memory: `--tools ""` removed the built-in tools only. One reply
(followups-v2 claude run1 V01 without) mentions an available browser.
`measure.json` now adds `--strict-mcp-config`, `--setting-sources ""`, and
`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`; account-level organization
instructions still apply. See `followups-lessons.md`.

## Engineering verification

Python unit tests, including whitespace-sensitive normalization and execution
provenance regressions, pass. The full UI reference and checker suites pass.
A fixture false rejection of semantically correct D21/D22 outputs was corrected
by targeting the section rather than demanding an unused `.hero` class.
