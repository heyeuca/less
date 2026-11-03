# Landing page, before and after less

A marketing demo for the `less` skill. `before.html` is a landing page for Tally, written with the skill files closed. `after.html` is that same page after one less pass. Neither file was edited by hand after it was written. This is one run, model **grok-4.7**.

Tally is a made-up product. The App Store URL uses a made-up app id. It is a link, not a real listing.

## Prompts

Step 1, before anything under `skills/`, `evals/`, or `demo/` was opened, and before this README was read:

> Build a landing page for Tally, a habit tracker app for iPhone. It lets you track daily habits with one tap and see streaks. Free, with an optional $4.99 one-time Pro unlock for unlimited habits. Single self-contained HTML file with inline CSS and JS, no external assets.

Step 2, after reading `skills/less/SKILL.md` and `skills/less/references/design.md` and following them, with no extra instruction:

> /less this page

## Numbers

Measured with Playwright and axe-core the same way as `evals/design/check.mjs`: `setContent`, then the checker's element count (`body *`), its CSS declaration count (`CSSStyleDeclaration.length` on top-level style rules), axe tags `wcag2a`, `wcag2aa`, `wcag21aa`, and `wcag22aa`, reflow as `scrollWidth <= clientWidth + 1`, and the G7 sticky-overlay check. Chromium expands shorthand properties, so the declaration counts are larger than the number of lines typed in the file. Visible words are `document.body.innerText`, split on whitespace. The same counts came back at 1280×800 and at 320×640.

| | Before | After |
|---|---:|---:|
| DOM elements | 236 | 137 |
| CSS declarations (checker) | 814 | 598 |
| CSS declarations, including rules inside `@media` | 839 | 621 |
| Visible words | 518 | 298 |
| axe violations | 3 | 0 |
| New axe violations in the after page | | 0 |
| 320px reflow | pass (320 = 320) | pass (320 = 320) |
| Product name, Tally | kept | kept |
| Price, $4.99 | kept | kept |
| Pro unlock | kept | kept |
| App Store link | 6 links | 4 links |

The checker does not count declarations nested in `@media`. The third row does. There are no `@keyframes` in either page.

The three before-page violations are the same at both widths: serious `aria-prohibited-attr` on each testimonial star line, an `aria-label` on a `<p>`. Those paragraphs are gone in the after page. The after page adds no violation.

The four App Store links that remain are "Get the app", "Download on the App Store", "Download free", and "Unlock Pro". All use `https://apps.apple.com/app/tally-habit-tracker/id6478901234`. The two that were cut are the closing banner's download button and the footer "App Store" link.

### G7, sticky header

The gate applies. Both pages have a sticky header with text. Its fill is opaque `rgb(243, 238, 230)` (alpha 1). There is no `backdrop-filter`. G7 passes at 1280 and at 320: the after page does not take a legible overlay and make it see-through.

`check.mjs` decides overlap by scrolling each text block under the header. It now forces instant scrolling (`scroll-behavior: auto`, `behavior: 'instant'`) and confirms `scrollY` reached the target before it reads, so these pages' `scroll-behavior: smooth` no longer matters. Content passes under the header on both pages at 1280 and 320, the same over 5 runs. The fill is opaque, and frames from the scroll videos show the header text sitting on the paper color, not on the type underneath.

## What was cut

- The small line "Habit tracker for iPhone" above the headline
- The fake phone status bar (9:41 and the dots)
- The "See pricing" button. The Pricing link in the header is still there
- The ratings, the "48,000 people tracking" line, and the "As seen in" press names
- The sentence "Open it, tap, and put the phone down."
- The dark "By the numbers" band
- The three testimonials
- The pricing sentence that said you pay once to go past three habits
- The "Start here" and "One-time unlock" pills
- The word "forever" on the $0 price
- The "Up to 3 habits" line
- The questions section, including its five disclosures
- The closing "Start with one habit" banner and its download button
- The footer links (Features, Streaks, Pricing, FAQ, App Store)
- The CSS that only styled those pieces

The preview habits still toggle, and the script that does that is unchanged. "It is not a subscription" and "One purchase, no renewal" are still on the page. The footer still says Pro is a one-time unlock for $4.99. The FAQ sentence "You are not billed again" was cut with that section.

## What the before page invented

These were not in the build prompt. Sample numbers inside the phone, and the tally drawing captioned "Example: a 12-day streak", are labeled as a preview. They are not counted below as user statistics. Both pages keep them.

| Claim | Before | After |
|---|---|---|
| Testimonials from Maya Chen, James Okonkwo, and Priya Shah, each with five stars | invented | removed |
| 48,000 people tracking | invented | removed |
| 4.9 out of 5 from 2,400 App Store ratings | invented | removed |
| Press names: The Verge, WIRED, Lifehacker | invented | removed |
| 12 million habits checked off | invented | removed |
| 86% still tracking after 30 days | invented | removed |
| 64 days, the longest streak logged this month | invented | removed |
| Free plan capped at 3 habits, including Priya's "fourth habit" | invented | removed |
| The free price lasts "forever" | invented | removed |
| Missing a day resets that streak | added rule | kept |
| "No note to write and no timer to start." | added limit | kept |

Keeping an invented claim would count as a failure to report. The last two rows are the ones the after page still shows. "Not a subscription" and "no renewal" restate the one-time price from the prompt. They stayed.

## What this run did not patch

Nothing the prompt asked for was dropped. The name, the $4.99 price, the Pro unlock, and an App Store download button are all still on the after page.

The two added lines in the table above were left in place. The streak sentence is there because the prompt asked the page to show streaks, and a streak is a run of days. The "no note, no timer" sentence is there because it says what "one tap" is not. Neither was removed as a false claim. The skill pass does not fact-check.

Card borders, corner radius, and the phone's drop shadow stayed. The skill's decoration cut is aimed at a gradient, or at a shadow, border, and radius stacked on every surface. These pages have no gradient. The shadow is only on the phone.

## Files

- `before.html`, `after.html` — unedited output from this run
- `before.png`, `after.png` — full-page stills, 1280px wide
- `side-by-side.png` — both stills, labeled "Without less" and "With less"
- `before.mp4`, `after.mp4` — about 6 seconds, 1280×800, scroll from top to bottom
