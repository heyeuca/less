# Plumbing page, before and after less

`before.html` is a website for Fairline Plumbing, a made-up business, written
by gpt-5.6-sol with no skill loaded. `after.html` is that page after one
`/less` pass by the same model. Neither file was edited by hand.
`before-after.png` boxes the main cuts and what the pass missed; the pages
themselves carry no boxes. One of four topics in [demo/](../README.md), and
the one that was cut least.

Fairline Plumbing and its phone number are made up.

## Prompts

Step 1:

> Build a website for my plumbing business, Fairline Plumbing. We serve Maple
> County. Open Monday to Friday, 8am to 6pm, Saturday 9am to 1pm, closed
> Sundays. Phone (555) 014-7731. Prices: drain cleaning $120, faucet repair
> $95, toilet repair $110, water heater flush $150, and leak inspection $80.
> Single self-contained HTML file with inline CSS and JS, no external assets.

Step 2 is the [demo/dental](../dental/) step 2 prompt with this request in
place of the dental one. The commands, model, skill version (`414fc8b`), and
codex-cli version are the same.

The model wrote the page to `fairline-plumbing/dist/index.html` instead of
`index.html`, and tried to deploy it to a hosting service. The sandbox
blocked the network, so nothing was deployed. That file is `before.html`.

## Numbers

Counts follow `demo/bakery`.

| | Before | After |
|---|---:|---:|
| Visible words (1280 / 320) | 325 / 309 | 166 / 152 |
| DOM elements | 161 | 83 |
| CSS declarations (checker) | 1046 | 545 |
| CSS declarations, including `@media` | 1180 | 647 |
| Page height at 1280px | 3343px | 2111px |
| Page height at 320px | 5771px | 2973px |
| axe violations, scroll-reveal content shown | 2 | 1 |
| Phone links (`tel:`) | 7 | 5 |
| Name, Maple County, hours, Sunday closed, phone, five services and prices | all | all |

The 1 axe violation left is the service-area paragraph, which failed in the
before page too.

## What the before page invented

Little. This model mostly restated the request instead of adding to it:
"Our five most common services are listed clearly", "One phone number
connects you with Fairline Plumbing", "Weekday hours plus a Saturday morning
window". The one promise beyond it, "No long forms or complicated booking
flow", is gone from the after page.

## What was cut

- The "Why Fairline" nav link and the label above each heading
- The hero checklist ("Clear pricing", "Local service area", "Saturday hours")
- The illustration, its "$80 Leak inspections start here" note, and its
  "Proudly serving Maple County" badge
- The service icons and the "Service price" label under each price
- The whole "Good plumbing starts with a straight answer" section and its four
  points
- The closing "Let's get your plumbing back on track" band, which repeats the
  phone link
- The CSS that only styled those pieces

## What the pass missed

- The top bar repeats the hours, which are listed in full below it.
- Five phone links stay: the nav, the hero, the service picker, the
  service-area card, and the footer.
- "Maple County" still appears four times in visible text, down from five.
- The hero keeps `min-height: 520px` (down from 650px) after its
  illustration was removed, so it has empty space above and below the text.

## Every attempt

| # | Step | Model | Notes | Used |
|---|---|---|---|---|
| 1 | build | gpt-5.6-sol | 2026-11-06, 55 min, wrote `fairline-plumbing/dist/index.html`, deploy blocked | **before.html** |
| 2 | /less | gpt-5.6-sol | skill at `414fc8b` with the request, 3 min | **after.html** |

## The images

`before.png`, `after.png`, and both halves of `before-after.png` are
full-page screenshots at 1280px wide, taken with the viewport as tall as the
page, as in demo/bakery. Boxes are overlays drawn at render time: red for an
invented claim, gray for decoration or a repeat, dashed red on the after page
for what the pass missed. They mark the main cuts, not all of them.
