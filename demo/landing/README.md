# Landing page, before and after less

A marketing demo for the `less` skill. `before.html` is a landing page written with no knowledge of the skill. `after.html` is that same page after one less pass. Neither file was edited by hand after it was written. This is one run, model **grok-4.7**.

## Prompts

Step 1, before the skill files were opened:

> Build a landing page for less, an open-source agent skill that makes AI coding agents cut what has no reason to exist from their writing, code, and UI. Install: `npx skills add heyeuca/less`. Repo: https://github.com/heyeuca/less. Single self-contained HTML file with inline CSS, no external assets.

Step 2, after reading `skills/less/SKILL.md` and `skills/less/references/design.md` and following them:

> /less this page

The pass also had this constraint: keep every real interactive element, the install command, and the repo link. Saved as `after.html` with no further edits.

## Numbers

Measured with Playwright and axe-core the same way as `evals/design/check.mjs`: `setContent`, the checker's element count (`body *`), its CSS declaration count (declarations on top-level style rules only), axe tags `wcag2a`, `wcag2aa`, `wcag21aa`, and `wcag22aa`, and reflow as `scrollWidth <= clientWidth + 1`. Counts match at 1280×800 and 320×640.

| | Before | After |
|---|---:|---:|
| DOM elements | 135 | 77 |
| CSS declarations (checker) | 500 | 309 |
| CSS declarations, including rules inside `@media` and `@keyframes` | 538 | 316 |
| axe violations | 0 | 0 |
| New axe violations in the after page | | 0 |
| 320px reflow | pass (320 = 320) | pass (320 = 320) |
| Install command `npx skills add heyeuca/less` | kept | kept |
| Repo link `https://github.com/heyeuca/less` | kept (5 links) | kept (5 links) |

The checker does not count declarations nested in `@media` or `@keyframes`. The third row includes those. The before page's entrance and drift animations sit in keyframes, so the checker number under-counts that CSS.

The install command is in the hero, in the Install section, and in the "How do I install it?" answer. Both Copy buttons are still there. On a local page they write `npx skills add heyeuca/less` to the clipboard. The five repo links are the nav, the hero, the questions answer, the install section, and the footer.

Tracked interactive controls (skip link, nav, both Copy buttons, repo links, back to top) are the same list on both pages. The three question disclosures are still there, and the first one opens.

## What was cut

- Decorative gradient blobs, the background grid, and the giant "less" watermark
- Fake terminal chrome: traffic-light dots, the "install" label, and the `$` prompt
- Eyebrow labels and the 01 / 02 / 03 / 04 badges
- Decorative icons on Writing, Code, and UI
- Card frames around those three columns
- Drop shadow and rounded corners on the command box
- Header blur
- Entrance motion and the floating glow
- The line "One standard, in writing, code, and UI."
- The whole "What the extra looks like" section

## What the before page invented

No testimonials, no people's names, no ratings, no "trusted by" row, and no statistics.

The examples section is labeled on the page as made up: "Not a quote. Not a measured result." Inside it:

- An invented marketing paragraph ("We're excited to announce a powerful new skill…")
- An invented `nameOf` function that only returns `user.name`
- An invented cluttered UI (welcome banner, search box, upgrade pill, tips carousel, learn-more button)

The Writing, Code, and UI cards state specific cuts (warm-ups, a wrapper nothing calls, a comment that repeats the line, decoration, a second control) as what less does. Those details are not in the build prompt. They were written before the skill files were opened. They are interpretation, not a measurement.

## What the after page kept on purpose

The skill would normally treat a second call to action, and a questions block that repeats the definition, as cuts. Both Copy buttons and the questions disclosures stayed, because this run was told to keep every real interactive element. The footer sentence also stayed. It repeats the definition, and after the eyebrow was removed it is the sentence on the page that says "open-source agent skill."

## What went wrong

Nothing that this run was told to keep was dropped. The command, the repo link, both Copy buttons, the nav, the skip link, the questions, and back to top are all still there.

While scrolling, the headline shows through the sticky header. The less pass removed the header blur and left the header fill at 88% opacity. That was not patched afterward. The full-page stills are taken at the top, so they do not show it. The scroll videos do.

## Files

- `before.html`, `after.html` — unedited model output
- `before.png`, `after.png` — full-page stills, 1280px wide
- `side-by-side.png` — both stills, labeled "Without less" and "With less"
- `before.mp4`, `after.mp4` — about 6 seconds, 1280×800, scroll from top to bottom
