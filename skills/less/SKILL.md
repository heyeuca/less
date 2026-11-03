---
name: less
description: Removes elements without a clear reason to exist from writing, code, and UI code (HTML/CSS, JSX, Tailwind), keeping correctness, needed context, safety, accessibility, and everything the user asked for. Use when the user asks to cut, trim, remove, strip, simplify, tighten, shorten, or declutter something, says it is "too long", "too busy", or "looks cluttered", or asks to clean up AI-written output. Not for building or adding UI features, accessibility audits, or performance refactors.
license: MIT
---

# less

Less, but better. Keep only what has a reason to exist.

## The test

For each element (sentence, caveat, heading, bullet, comment, function,
parameter, option), ask: **Does this have a clear reason to exist?**
If not, remove it. Clarity beats brevity. When unsure, keep it.

## When

Only on request or a clear cue, not when merely writing a draft or new code.
Removal only: no style or voice rewrites, translation, fixed-length summaries,
or fact-checking; in code, no refactors beyond removal, performance work, or
style rewrites.

## Don't apply

Return the input unchanged plus one line naming the reason for:
- Legal, contractual, or other verbatim text; quotations and transcripts.
- Code, config, or commands the user didn't point at.

Change only the code the user pointed at. A user-set length or format is not
an exclusion: work inside it.

## Removal order

Check every candidate against "Never remove" first, especially the user's own
greetings and closings.

Writing:
1. Preamble, restated question, and greetings you added ("Great question!").
2. Closing recaps and offers you added, or that end a PR description, commit,
   or doc ("Hope this helps", "Want me to...").
3. Hedges and filler that change nothing.
4. Duplicate points (keep the clearest).
5. Unrequested caveats and alternatives that don't change what the reader does.
6. Decoration on answers under ~5 sentences: headers, bold, bullets.
7. Merge and shorten the rest, keeping complete sentences. When editing the
   user's text, remove only; don't merge or reword.

Code:
1. Comments that restate the code.
2. Unrequested abstractions: single-use helpers, wrappers, interfaces, factories.
3. Unrequested options, flags, config.
4. Defensive code for cases that provably can't happen from the visible code.
   Otherwise keep it.

Documents: apply the test section by section. Keep the structure readers
navigate by: headings, TOC and anchors, numbered steps referenced elsewhere,
tables that carry data. Remove a whole section only when it fails the test.
Keep every heading and its TOC entry unless the whole section is cut; never
merge a section into the intro.

Design: for UI code the user points at, apply the test to elements and
styles. Remove only after checking [references/design.md](references/design.md)
(removal order and never-remove list). Unrequested content there means what
the agent added, not what the user wrote. Change markup and styles only; no new
aesthetic. Not for building new UI, screenshots, or Figma files.

## Never remove

- Correctness: numbers, units, dates, conditions, exceptions, negations.
- Needed context: what the reader needs to act (prerequisites, steps, versions).
- Safety: data-loss, security, money, legal, irreversible-action warnings.
- The user's ask: requested content, format, length, constraints.
- Attribution and citations.
- The user's voice when editing their text. Don't rewrite style.
- In a message to people (email, chat, letter) the user wrote: greetings,
  sign-offs, and lines asking for a reply or questions ("Let me know if...").
  E.g. "Do reach out anytime if anything is still unclear." stays; you may trim
  "anytime" and "still". Only greetings and closings are protected: other
  filler in the user's text ("basically", "literally", "just") is still cut,
  keeping their voice.
- Politeness register: 존댓말/敬語 forms, 様, greetings, sign-offs. Stacked
  softeners and intensifiers inside it (정말, 혹시, 大変, 誠に, 何卒) are filler.
- Code: behavior (output, side effects, errors); error handling at real
  boundaries (I/O, network, user input); "why" comments, constraints, safety
  notes; public API and signatures unless asked; type annotations that affect
  checking or runtime; test-only hooks and seams.
- Anything whose purpose you can't determine.

## Stop

Stop when every element passes the test, or when the next cut would cost
meaning or require guessing. Never cut to hit a length. If the user asked to
shorten their text, filler that fails the test goes; unchanged needs a reason.

## Output

The reduced text or code only, in the same format and language. Exception:
the one-line reason under Don't apply. Don't comment on what was cut unless
the user asks; then list it. If nothing should change, return it unchanged.
