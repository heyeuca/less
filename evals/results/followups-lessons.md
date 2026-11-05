# #53 lesson cases: P17–P22 (2026-11-05)

P17–P22 encode the three gpt-6.1-sol misses from the v0.3.4 held-out run as
`tune` pairs. Each was run with the shipping skill through both local CLIs,
three times per case, using the isolated `measure.json` session below. Raw
prompts, replies, model identities, and `summary.json` are in
[`followups-lessons/`](followups-lessons/).

## Session isolation

The first attempt used the earlier `claude -p` flags. Its Claude replies showed
that the session still had the account's MCP servers and connectors loaded:
`--tools ""` removes built-in tools only. One P18 reply listed the user's
connectors instead of editing the text. That attempt is discarded and not
published. `measure.json` now adds `--strict-mcp-config`, `--setting-sources ""`
and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. A probe in that session reported no
tools, MCP servers, or memory. Account-level organization instructions still
reach the model and cannot be turned off without an API key.

## Case fixes before the published run

- P17/P18 now mark the text as the assistant's earlier answer (`author:
  assistant`), as H01 did. Without it, both models read "Run `python
  --version`" as a request and tried to run it.
- P20 tested removing 念のため申し添えますが. Both models kept 念のため, which M9
  allows ("keep them when they carry social intent"). H04's actual failure was
  lowering いただけますでしょうか while trimming, so P20 now asks to drop a
  repeated request and checks that the remaining one keeps its register.

## Baseline (shipping rules)

Pass = protected spans kept; no-op cases unchanged apart from a transport
final newline or one wrapping code fence; P17/P22 lose their filler; P20 keeps
exactly one いただけますでしょうか.

| Case | Shape | claude | codex |
|---|---|---|---|
| P17 | trim an answer, keep its success example | 1/3 | 0/3 |
| P18 | same answer, already clean | 3/3 | 0/3 |
| P19 | clean keigo email | 3/3 | 3/3 |
| P20 | drop a repeated keigo request | 3/3 | 3/3 |
| P21 | clean code with a local variable | 0/3 | 0/3 |
| P22 | same code plus a restating comment | 1/3 | 2/3 |

- **P17/P18:** codex drops "A successful response looks like Python 3.12.8."
  in every run, reproducing H01. Claude keeps the sentence; its two P17 misses
  only add backticks around `Python 3.12.8`. This fails on one family, so per
  #53 no rule text changes.
- **P19/P20:** the register held in all 12 replies. H04 was one run in three
  on one family and did not reproduce here.
- **P21/P22:** both families inline `raw = env.get(...)` into the return,
  reproducing H06. Nothing in S1–S4 or M10 tells the model to leave kept code
  as written. This fails on both families, so a rule change is warranted.
- codex P22 run 3 first failed because the codex workspace ran out of
  credits (`codex-3-P22.error.json`). It was rerun with the same skill and
  cases once credits returned, and passed.

## Candidate rule (adopted)

One added sentence after S4:

> Keep the code you don't remove as written: don't inline its variables,
> rename, or reformat.

[`candidate-claude/`](followups-lessons/candidate-claude/) and
[`candidate-codex/`](followups-lessons/candidate-codex/) ran it on P21/P22 and
on the helper-removal cases E16, E17, and N18, to check that the new sentence
doesn't block S1–S4. One Claude N18 call timed out twice at 600 seconds and
passed on the third try. The codex run came later, after credits returned,
with the same skill, cases, and probe script (`candidate_probe.py.txt`, now
taking the family as its second argument).

| Case | Check | Baseline claude | Candidate claude | Baseline codex | Candidate codex |
|---|---|---|---|---|---|
| P21 | `raw` kept | 0/3 | 3/3 | 0/3 | 3/3 |
| P22 | `raw` kept, comment removed | 1/3 | 3/3 | 2/3 | 3/3 |
| E16 | helper and comments removed | — | 3/3 | — | 3/3 |
| E17 | option and impossible check removed | — | 3/3 | — | 3/3 |
| N18 | strategy class removed | — | 3/3 | — | 3/3 |

Codex's E16, E17, and N18 replies match each case's reference `after`. The
sentence passes on both families, so it is now in `SKILL.md` after S4, exactly
as measured (971/1000 words). These are `tune` cases, so this is regression
evidence, not a held-out gain. The next held-out measurement should include
fresh clean-code cases.
