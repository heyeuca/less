# less

**Less, but better.** — Dieter Rams

An agent skill to keep only what has a reason to exist.

less has your agent cut what has no clear reason to exist from writing, code, and UI code, and keep correctness, needed context, safety, accessibility, and what you asked for.

![A landing page without less and with less](demo/landing/side-by-side-top.png)

A landing page grok-4.7 built for a made-up app, then the same page after `/less`: 42% fewer elements and words, invented testimonials and stats gone, price and App Store button kept. Unedited, one run: [demo/landing](demo/landing/).

```text
Before: Great question! You're asking how to undo the last Git commit. To undo it while keeping your changes, run `git reset --soft HEAD~1`. I hope this helps! Let me know if you have other questions.
After:  To undo the last commit and keep your changes, run `git reset --soft HEAD~1`.
```

```html
<!-- Before -->
<span class="badge">New</span>
<h2>Orders</h2>
<ul id="list"><li>#1042 · Shipped</li></ul>
<p id="loading" role="status" hidden>Loading orders…</p>
<p id="empty" hidden>No orders yet.</p>
<p id="error" role="alert" hidden>Couldn't load orders. Try again.</p>

<!-- After: badge gone; hidden loading, empty and error states kept -->
<h2>Orders</h2>
<ul id="list"><li>#1042 · Shipped</li></ul>
<p id="loading" role="status" hidden>Loading orders…</p>
<p id="empty" hidden>No orders yet.</p>
<p id="error" role="alert" hidden>Couldn't load orders. Try again.</p>
```

## Install

Any agent that supports skills:

```sh
npx skills add heyeuca/less
```

Add `-y` to skip the prompts (CI, no TTY).

Claude Code plugin:

```sh
claude plugin marketplace add heyeuca/less
claude plugin install less@heyeuca
```

Cursor: `.cursor-plugin/plugin.json` mirrors the Claude Code manifest and
points at `skills/`. less is not listed in the Cursor Marketplace yet; until it
is, install it with `npx skills add heyeuca/less` above.

Manual: from a clone of this repo, copy `skills/less` into your agent's skills folder (`~/.claude/skills` here, or `~/.agents/skills`):

```sh
mkdir -p ~/.claude/skills && cp -r skills/less ~/.claude/skills/
```

less runs when you ask for it (`/less`, or "cut", "trim", "remove", "strip", "simplify", "tighten", "shorten", "declutter", "too long", "too busy", "looks cluttered", "clean up AI-written output"), on writing, code, and UI code. It doesn't run while an agent writes a new draft
or new code.

To shape everything an agent writes, paste
[`always-on/AGENTS.md`](always-on/AGENTS.md) into your `AGENTS.md`. It is a
separate, shorter rule set for new output, not the editing skill. Its main risk
is leaving out explanation the reader needed, so its cases in
[`evals/always.json`](evals/always.json) grade that first. It hasn't been
measured yet. See [docs/DECISIONS.md](docs/DECISIONS.md).

## Results

**v0.3.4 held-out measurement** ([details](evals/results/0.3.4-heldout.md)):
10 unseen cases, claude-opus-5-5 and gpt-6.1-sol, 3 runs each, blind-graded by
the other family.

- Protected spans kept: 28/30 and 27/30 with the skill, 10/30 and 7/30 without.
- Outputs the grader marked as damaged: 0/30 and 3/30 with the skill, 15/30 and
  15/30 without.
- Clean inputs returned byte-for-byte: 6/12 and 5/12 with the skill, 0/12
  without.

The absolute gates (no lost span, every clean input unchanged, no damage) did
not pass. Most with-skill misses are measurement artifacts: trailing
newlines, code fences, and a capitalized span. The real misses are three
gpt-6.1-sol cases: a needed sentence cut (H01), a lowered keigo register
(H04), and an inlined variable in clean code (H06).

Measured with v0.3.3 on the 50 cases in [`evals/`](evals/), 2 runs with grok-4.7, against the same model without the skill.

- All cases: 50/50 in both runs (100%), with 0 must-keep misses in 100 outputs. Without the skill: 39/50 (78%), 10 misses in 50.
- Writing and code: 29–31% fewer words on 37 cases, with 0 must-keep misses and identical code behavior. Without the skill: 39% fewer, but must-keep content lost in 7 cases.
- UI: 17–18% fewer elements and 42% fewer CSS declarations on 13 cases, with 13/13 accessibility and semantics gates and 0 new axe violations in both runs. Without the skill: 10/13 on the gates and 9/13 by meaning.

A separate grading agent checks each case against its `must_keep` list; code is run and compared, and UI is checked with Playwright and axe. The runs were isolated from the repo. We tuned the skill on these evals, so read them as a regression test, not a benchmark, and only one model was tested.

These numbers predate the current evaluation protocol. The baseline arm was
asked to "Make this less verbose." while the skill arm got `/less`; the runner
now gives both arms the same task instruction, so only the skill context
differs. UI checks now also require fixture-specific removals (G8). The numbers
above have not been remeasured with these changes. The v0.3.3 runs predate
`run.json`, so their sampling settings and session isolation were not recorded
beyond what is stated above. Each future results directory includes a
`run.json` (written by `run.py prompts`) with input and prompt hashes, the
model, sampling, session setup, grader, and every attempt.

The current regression suite has 82 cases, including preservation pairs,
rule-coverage examples, and the newly encoded over-editing lessons. See the
[evaluation guide](evals/README.md) for separate removal, preservation, damage,
and exact no-op checks. The completed v0.3.4 measurement above used ten distinct
cases, repeated three times per family; repetitions are not independent cases.
A [protocol-v2 candidate experiment](evals/results/followups-v2.md) is also
complete, with failed absolute gates; its rule changes were not adopted. The
[lesson cases](evals/results/followups-lessons.md) reproduce two of the three
v0.3.4 misses with the v0.3.4 rules. A sentence for one of them (keep code
you don't remove as written) passed on both families and is now in the skill;
it has not been held-out measured. The Claude
runs in all three measurements loaded the account's MCP servers and memory;
`measure.json` now isolates them. The next optimization claim requires fresh
cases and frozen execution provenance. Organic installed-skill and always-on
measurements remain outstanding. Historical v0.3.3 figures use a different
protocol.

## License

[MIT](LICENSE)
