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

## 2026-11-05: Design edits may consolidate and restructure, not only remove

**Context.** `references/design.md` was removal-only: no new aesthetic, fonts,
or palette. Removal alone can leave a reduced page that reads worse than it
should. Flattened cards run together once their borders go, one role keeps
three near-identical colors and two sizes, and a sidebar emptied of
testimonials keeps its column. [impeccable's distill](https://github.com/pbakaus/impeccable/blob/main/skill/reference/distill.md)
was reviewed for ideas; its redesign steps were weighed against this skill's
zero-damage gates.

**Decision.** For UI code only, design edits may do three things besides
removing. They may keep items apart with spacing the code already uses (K14).
Values that serve one role may become one value the code already uses for it
(C14, R8); brand, state, emphasis, and heading levels are separate roles. A
layout left without a job may be collapsed (C15, R7), keeping reading and focus
order (K15). New colors, fonts, spacing values, components, and sections stay
out, as do progressive disclosure and restructuring a layout that still has a
job. Writing and code stay removal-only. The `design.md` budget rises from 750
to 900 words to hold these rules. Cases D27–D31 encode them, with D29 and D31
as protection cases.

**Revisit when** the design cases run on at least two model families. Drop or
narrow C14 or C15 if D29 or D31 fails in either family. Do the same if
graded damage on D cases rises above the removal-only arm.

## 2026-11-05: Layout repair by default, restructuring only on request

**Context.** C15 first covered only a layout left without a job, such as an
emptied column. Removals break layout in other ways too. Text keeps the half
width it shared with a removed illustration, and padding that cleared a
removed icon stays. Restructuring a whole page after every removal was
considered and rejected. It makes every region an edit target, so protection
cases can't hold, and no check can tell whether a whole re-layout is better.

**Decision.** R7 is now "Repair". Without a request, fix only what removals
broke (C15): an emptied column or track, a multi-column grid or row left with
one item, and padding, margin, or a width limit kept for a removed element.
Restructure further only when the user asks, within the sections they name.
Breakpoints that served only removed elements still stay (K9, as with D21).
Cases D32–D35 encode this; D34 and D35 are protection cases.

**Revisit when** design cases are measured. Narrow C15 to the emptied-track
case if D34 or D35 fails in either family.

## 2026-11-05: C15 covers a height kept for removed content

**Context.** In a demo run on a generated bakery page, the skill removed a
hero's illustration, tagline, and button but kept the `min-height` the hero
had been sized to. One heading was left centered in a 620px band. C15 named
padding, margin, and width limits, not heights, so the edit followed the
rule and still left the layout broken.

**Decision.** C15 now names a width or height limit kept for a removed
element. D36 encodes the failure with a reserve that gave an illustration its
size. D37 is its protection case: a banner keeps its min-height when only a
badge goes. The checker gains `must_hug`, which measures the gap between a
section and the visible text and media inside it, so a reserve moved onto a
wrapper still fails. Not measured yet.

**Revisit when** design cases are measured. Drop "or height" if D37 fails in
either family.
