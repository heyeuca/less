# Bakery page, before and after less

A demo for the `less` skill on a page an agent built. `before.html` is a
website for Oven Door, a made-up bakery, written by gpt-5.6-sol with no skill
loaded. `after.html` is that page after one `/less` pass by the same model.
Neither file was edited by hand. `before-after.png` boxes the main cuts; the
pages themselves carry no boxes. One of four topics in [demo/](../README.md);
it led the main README until the dental demo replaced it.

Oven Door, its address, and its phone number are made up.

## Prompts

Step 1, in a fresh `codex exec` process in an empty directory:

> Build a website for my bakery, Oven Door. We're at 214 Elm Street. Open
> Tuesday to Sunday, 7am to 3pm, closed Mondays. Phone (555) 014-2290. We sell
> sourdough loaf $9, croissant $4, cinnamon roll $5, baguette $4, and a seasonal
> fruit tart $6. Single self-contained HTML file with inline CSS and JS, no
> external assets.

Step 2, in another fresh process with `index.html` from step 1 in its
directory. The prompt held `skills/less/SKILL.md` and
`references/design.md` from `main` at `414fc8b`, in the same `<skill>`
wrapper `evals/run.py` uses, then the step 1 request as "The user's original
request", then:

> You built index.html for that request. Now:
>
> /less index.html

Both steps: `codex exec --ephemeral --ignore-user-config --ignore-rules
--skip-git-repo-check -s workspace-write -m gpt-5.6-sol`, codex-cli 0.160.0,
CLI default sampling. That is the `measure.json` setup with a writable
sandbox so the model can save the file.

## Numbers

Counts use Playwright the way `evals/design/check.mjs` does: `setContent`, elements are `body *`, CSS
declarations are `CSSStyleDeclaration.length` on top-level style rules (the
third row adds rules inside `@media`), and words are `document.body.innerText`
split on whitespace.

| | Before | After |
|---|---:|---:|
| Visible words (1280 / 320) | 222 / 220 | 71 / 69 |
| DOM elements | 114 | 65 |
| CSS declarations (checker) | 974 | 405 |
| CSS declarations, including `@media` | 1079 | 482 |
| Page height at 1280px | 3467px | 2587px |
| Page height at 320px | 4495px | 2340px |
| axe violations, scroll-reveal content shown | 14 | 2 |
| 320px reflow | pass | pass |
| Phone links (`tel:`) | 3 | 2 |
| Name, address, hours, Monday closed, phone, five items and prices, Seasonal | all | all |
| `@media` blocks, including `prefers-reduced-motion` | 3 | 3 |

The before page hides its menu, story, and visit sections at `opacity: 0`
until they scroll into view. axe skips them in that state, so a plain
`setContent` run reports 1 violation for the before page. With the viewport as
tall as the page, so every section is revealed, it reports 14, all
`color-contrast`. The 2 left in the after page are the red "Monday / Closed"
text on yellow, which failed in the before page too. The screenshots are taken
the same way, so they show what a visitor sees after scrolling.

## What the before page invented

None of these were in the request.

| Claim | After |
|---|---|
| Hero: "Slow-fermented loaves, flaky morning pastries" | **kept**, as "Slow-fermented loaves and flaky morning pastries." |
| Hero: "the kind of counter where everybody knows what you came in for" | removed |
| Badge on the illustration: "Baked here, every morning" | removed |
| Ticker: "Sourdough daily", "Butter-forward pastries" | removed |
| Menu: a taste line for four items ("Crackly · tangy · tender", …) | removed |
| Story: "the best baking starts before sunrise" | removed |
| Story: "every pastry is folded by hand" | removed |
| Story: "every batch is made right here behind the oven door" | removed |
| Hours card: "Best selection: Before 11am" | removed |

Slogans that state no fact ("Good days start with dough.", "A small menu, made
properly.", "Follow the smell of fresh bread.") are not counted. All three
stay in the after page.

## What was cut

- The top bar repeating the hours, and the "Our story" nav link
- The "Your neighborhood bread stop" label, and the other small labels above
  headings ("From the oven", "Made by hand", "Find us")
- The illustration: sunburst, loaf, and "Baked here, every morning" badge
- The round "See the menu" link, which repeats the "Today's bake" nav link
- The scrolling ticker
- Menu numbers 01–05 and the taste lines; "Seasonal" stays
- The whole "Nothing fancy. Just honest." story section, its stamp, and its
  drawing
- "Call the bakery →", which repeats the phone link above it
- The "Best selection" row
- The grain texture, the "214" behind the visit section, and the scroll-reveal
  animation and its script
- The CSS that only styled those pieces

## What the pass missed

- "Slow-fermented" stays in the hero, a fact the request never gave.
- The hero keeps the `min-height` it had beside the illustration. The heading
  and one line now fill most of it, so it doesn't read as empty, but 254px of
  it is uncovered at 1280px. That is over the 120px D36 allows.
- The hours card still stretches to the height of the column beside it, so
  it has empty space under Monday.

## Every attempt

The same build prompt went to four models before one page was picked for
having the most to cut. Every run is listed, including ones not used.

| # | Step | Model | Notes | Used |
|---|---|---|---|---|
| 1 | build | claude-opus-5-5 | `claude -p` with no tools: the model said it saved a file but returned no HTML | no |
| 2 | build | claude-opus-5-5 | `claude -p` with Write: 164 elements, 2074px, no invented reviews or numbers | no |
| 3 | /less | claude-opus-5-5 | on run 2, original request not included: elements −29%, words −11%, height −7% | no |
| 4 | – | gpt-5.6-terra | one-word call to check the rate limit | – |
| 5 | build | gpt-5.6-terra | 119 elements, 2576px | no |
| 6 | build | gpt-5.6-sol | 114 elements, 3467px | **before.html** |
| 7 | build | gpt-6.1-terra | 75 elements, 2005px | no |
| 8 | /less | gpt-5.6-sol | stopped before it finished, to wait for a skill change | no |
| 9 | /less | gpt-5.6-sol | skill at `f25f7af`, original request not included: words 222→161, height −7%; kept every invented claim, since it couldn't tell what the owner had said | no |
| 10 | /less | gpt-5.6-sol | skill at `f25f7af` with the request: words 222→42, height 3467→2158px, but the hero kept its `min-height` around one heading | `after-before-fix.html` |
| 11 | /less | gpt-5.6-sol | skill at `414fc8b` with the request | **after.html** |

Run 10's empty hero showed that C15 named padding, margin, and width limits
but not heights. That became case D36 and a one-phrase rule change (#63).
Run 11 is the one run made after that change. Runs 10 and 11 differ in more
than the hero: run 10 cut the slogan and every hero sentence, and run 11 kept
the slogan and one line. Expect that much spread from run to run.

## The image

`before-after.png` is built from full-page screenshots at 1280px wide, taken
with the viewport as tall as the page. Boxes are overlays drawn at render
time: red for an invented fact, gray for decoration or a repeat, dashed red
for the invented line the pass kept. They mark the main cuts, not all of
them; the lists above are complete. Both pages are shown at the same scale
and top-aligned, so the difference in length is real.
