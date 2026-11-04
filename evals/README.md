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
