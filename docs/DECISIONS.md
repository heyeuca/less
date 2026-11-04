# Decisions

## 2026-11-04: The editing skill runs on request; always-on is a separate rule set

**Context.** `SKILL.md` applied less "only on request or a clear cue". The
README also suggested an `AGENTS.md` line telling agents to apply the skill to
everything they write. An agent given both couldn't tell which wins. The two
modes also fail in different ways: editing risks over-cutting existing text,
while always-on writing risks leaving out explanation the reader needed. Only
editing was evaluated (#41).

**Decision.** The skill stays on request. The README's line is replaced by
[`always-on/AGENTS.md`](../always-on/AGENTS.md), a short rule set for new
output. It names what to include as well as what to leave out, and says to use
the skill for cutting existing text. It has its own cases
([`evals/always.json`](../evals/always.json), run with `evals/always.py`) and a
120-word budget.

**Revisit when** always-on runs are measured. Drop or rewrite the rule set if
it misses any `must_include` item that the plain arm includes. Also drop it if
it removes no more filler than the plain arm in at least two model families.
