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

P01–P14 are seven paired prose regressions: empty emphasis versus uncertainty,
scope and approximation, repeated endings versus actionable endings, causal
qualifications, obligation, and over-compression in English and Korean
(arrows, fragments, and dropped articles in place of complete sentences). Each
pair has a reduction case and a clean protection case. Good adjacent sentences are exact protected spans. Add a
removal example and a legitimate-use protection example together when adding a
new deletion rule; use the same approach for code and UI regressions.

P15–P16 and D21–D22 test two absolute keep rules from the other side (#34).
P15 has a heading that only repeats the title, and D21 has a reduced-motion
rule left with nothing to turn off. Their pairs, P16 and D22, keep headings a
contents list links to and an opt-out that still covers a spinner. A narrower
candidate wording was measured but not adopted, because the fresh measurement
failed its absolute gates. See `results/followups-v2.md` and the archived
candidate snapshot. P16 and D22 remain protection cases.

P23–P25 cover W6's emoji and separator lines in writing (UI emoji is C6). P23
is a commit message the agent decorated with emoji and a `───` line. P24 is
the user's own Slack message, whose emoji stay as their voice (M7, M8). P25 is
an agent's CI table whose ✅/❌ marks are the results. The W6 wording was added
with these cases and has not been measured yet.

D23–D26 cover C13 and K13, taken from the "dead CSS" and "keep some
hierarchy" points in [impeccable's distill](https://github.com/pbakaus/impeccable/blob/main/skill/reference/distill.md).
D23 removes selectors nothing uses and keeps a `:focus-visible` rule that only
looks unmatched. D24 keeps state rules that a script reaches by adding a class.
D25 removes stacked nav shadows and keeps the `aria-current` fill. D26 keeps
the red fill on a destructive primary button.

D27–D31 cover the design edits that go beyond removal (see
[DECISIONS](../docs/DECISIONS.md)). D27 flattens cards and keeps the plans
apart (K14). D28 gives body copy one color, size, and family and keeps the
error red (C14). D29 keeps three state colors that only look like variation.
D30 removes a sidebar and collapses its empty column (C15). D31 keeps a filter
sidebar that has a job, and any restructure must keep the filter before the
results (K15). Progressive disclosure and new components are still out of
scope. None of C13–C15 or K13–K15 has been measured yet.

`prompts` also writes `OUT/run.json`. It holds SHA-256 hashes of the skill,
runner, cases, and checker, and one for every generated prompt. It also has
empty fields for the model and version, the sampling settings, the session
setup (a fresh session per case? file, repo, or tool access?), the grader and
its instructions, and every failed or retried attempt. Fill these in, and
publish `run.json` with the results directory. A result without one can't be
checked. `prompts` refuses a directory that isn't empty.
`preservation`, `sheet`, and `check.mjs` refuse to grade it once the skill,
runner, cases, checker, its fixture, or its dependency lockfile differs from
what was recorded, so new criteria are never applied to old outputs. A
directory without `run.json` is still graded, but its results are marked
unverified (`"verified": false`, an `UNVERIFIED` line, `_unverified` in the
design results). `check.mjs` won't grade a recorded run with `LESS_CASES`.

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

## Rule coverage

Rules in `SKILL.md` (W, S, M) and `references/design.md` (C, K) carry stable
IDs, and every case lists the rules it exercises in `rules`. `test_coverage.py`
fails when a case cites an unknown ID, when a rule has no case and is not
listed in `KNOWN_GAPS`, when a listed gap now has a case, or when a writing or
code removal rule (W, S) lacks either a case where it removes something or a
protection case (a no-op or a known `bad_after`). Closing a gap means adding a
case and deleting its ID from `KNOWN_GAPS`.

## Organic and trigger runs

`prompts` also writes `OUT/<id>.organic.json`: the conversation a user would
have, as role/content messages, with no skill text and no evaluation framing.
Cases with `author: "assistant"` hold the agent's own earlier answer, so it
stays an assistant turn after the question in `prompt`, followed by a request
to tighten it. Other content is the user's, sent with their request. `context`
(such as a calendar invite) sits beside the request and never replaces it.
Replay these in a session where the skill is installed rather than pasted, and
save the final reply as `OUT/<id>.organic.out.md`. Replay each message with its
own role. Chat UIs usually cannot add a prior assistant turn, so replay
`author: "assistant"` cases through a client that takes the full message list
(an API or agent SDK with the skill installed). If no such client is available,
leave those cases unrun. Never merge the answer into a user message: that
reintroduces the authorship error these cases guard against. Once any organic reply
exists, `preservation` also reports an `organic` arm with the same span and
no-op checks. That checks the
output, not whether the skill loaded: record loading separately with
`python3 evals/run.py triggers OUT`, which writes `triggers.md` from
`triggers.json` for each request run in a fresh session.

## Repository cases

`SKILL.md` asks the agent to inspect callers, exports, and tests before
removing code, and to run existing checks afterward. Single snippets can't test
that, so `evals/repos/` holds small projects. Each has a module, a caller or
export, and tests. `case.json` gives the request, the code that must stay
(used by a caller or test, or exported), the code that must go, and the test
command. `after/` holds a reference solution.

```sh
python3 evals/repos.py prepare OUT   # OUT/<id>/ and OUT/<id>.task.md
python3 evals/repos.py grade OUT     # kept, removed, tests_pass in repos.json
```

Run each case in a fresh agent session opened in `OUT/<id>/` with the skill
installed, and send the request in `OUT/<id>.task.md`. Whether the agent ran
the tests comes from its transcript; fill in `ran_tests` by hand.

## Always-on cases

[`always-on/AGENTS.md`](../always-on/AGENTS.md) is a separate rule set that
shapes new output; it isn't the editing skill. Its cases in `always.json` are
requests for new text, code, or UI. Each lists what the reply must include and
what it must not include. A missing `must_include` item fails the case,
whatever filler it avoided.

```sh
python3 evals/always.py prompts OUT   # OUT/<id>.always.md and OUT/<id>.plain.md
python3 evals/always.py sheet OUT     # OUT/always.md checklist per case and arm
```

## Held-out remeasurement

`heldout.json` holds cases written after the skill was frozen and never used to
tune it. `protocol.json` fixes the requirements before any run: at least two
model families, three runs per family, absolute gates on the with-skill arm,
and blind grading by a model from a different family. `protocol.py` enforces
them:

```sh
python3 evals/protocol.py prompts ROOT/<family>/<run>   # prompts + freeze.json
python3 evals/protocol.py blind ROOT/<family>/<run> SEED  # blind/ for the grader, key.json kept back
python3 evals/protocol.py report ROOT                     # report.json per family, run, case
```

Give the grader only `blind/`: the request, the input, and outputs labeled A and
B. It fills in `blind/grades.json` and names its own family. `report` refuses a
run whose inputs changed after its prompts were written. It also refuses a
grader from the generating family. It never pools families. Absolute gates (no
lost protected span, every clean input returned unchanged, no graded damage)
fail on any single output, and a paired win over the baseline doesn't override
them. Don't change the skill based on held-out results. Encode the lesson as a
new `tune` case and write fresh held-out cases for the next measurement.

## Running it locally

`measure.py` runs the held-out protocol with locally installed, logged-in
agent CLIs, so no API keys are needed. The commands are in `measure.json`
(by default `claude -p` and `codex exec`). Each prompt runs in a fresh process
in an empty directory, with tools, skills, and user config off. Each family's
outputs are graded by the other family's CLI. The grader sees only the blind
copy.

```sh
python3 evals/measure.py evals/results/<version>-heldout --runs 3
```

It records the CLI version, model, session setup, and every failed attempt in
each `freeze.json`. Rerunning resumes from finished replies and grades.
`--generate-only` stops before blinding, for example while one CLI needs to
log in.

## Changing the skill

1. Encode a failure as a case before adding prose. Tag it with the rule it
   tests and add its pair. Add or change a rule only when no case and check
   can carry the lesson, and merge or replace an existing rule to stay inside
   the word budget.
2. Change one rule at a time. Measure it with the frozen prompts and grader,
   on several runs, against the previous version. Keep the change only when
   it helps past run-to-run noise and no case regresses; otherwise revert it.
3. Log every attempt outside the tree (for example `decision.tsv`: id,
   hypothesis, change, before, after, delta, verdict, note), including
   reverted ones.

The encode-first, one-change-per-measurement, and organic-prompt practices
follow [pstack](https://github.com/cursor/plugins/tree/c742dd61706fbacc1b95f1a20b7b988cf096ce6c/pstack)
(its encode-lessons-in-structure principle and its eval and hillclimb
playbooks). Its style rewrites are not adopted.

## Protocol v2 notes

Protocol v2 retains `exact_noop` as the raw byte metric and adds
`presentation_noop` for the clean-input gate. Only one terminal LF and one
optional outer code fence are ignored; spaces, extra blank lines, indentation,
and Markdown hard breaks remain significant. This does not normalize semantic
edits. New V cases replace the retired H corpus, archived in `heldout-v1.json`.
Historical reports must be replayed at their recorded commit; they are not
regraded under v2.

The measurement freezes the effective configuration (including an override),
the grader prompt, and the implementation before work starts. Each call records
model identity, CLI version, session description, and prompt/reply hashes.
Unknown or changed model identities are rejected, and resume validates both
configuration and cached replies. A changed execution requires a new directory;
existing evidence is never silently re-labelled. The Claude command also
skips MCP servers, settings files, and auto memory (`--strict-mcp-config`,
`--setting-sources ""`, and the `env` entry); earlier Claude runs did not. Successful grader responses
are retained as `grade-ID.json`. Run-level model names are summaries, not the
source of per-output provenance.
