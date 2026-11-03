---
name: less
description: Removes elements without a clear reason to exist from writing and code, keeping correctness, needed context, safety, and everything the user asked for. Use when the user asks to cut, trim, simplify, tighten, or shorten something, says it is "too long", or asks to clean up AI-written output.
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

Check every candidate against "Never remove" first.

Writing:
1. Preamble and restated question.
2. Closing recap and offers ("Let me know if...").
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

## Never remove

- Correctness: numbers, units, dates, conditions, exceptions, negations.
- Needed context: what the reader needs to act (prerequisites, steps, versions).
- Safety: data-loss, security, money, legal, irreversible-action warnings.
- The user's ask: requested content, format, length, constraints.
- Attribution and citations.
- The user's voice when editing their text. Don't rewrite style.
- Politeness level and honorifics.
- Code: behavior (output, side effects, errors); error handling at real
  boundaries (I/O, network, user input); "why" comments, constraints, safety
  notes; public API and signatures unless asked; type annotations that affect
  checking or runtime; test-only hooks and seams.
- Anything whose purpose you can't determine.

## Stop

Stop when every element passes the test, or when the next cut would cost
meaning or require guessing. Never cut to hit a length.

## Output

The reduced text or code only, in the same format and language. Exception:
the one-line reason under Don't apply. Don't comment
on what was cut unless the user asks; then list it. If nothing should change,
return it unchanged.
