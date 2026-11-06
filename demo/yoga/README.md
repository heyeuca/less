# Yoga studio page, before and after less

`before.html` is a website for Still Point Yoga, a made-up studio, written by
gpt-5.6-sol with no skill loaded. `after.html` is that page after one `/less`
pass by the same model. Neither file was edited by hand. One of four topics in
[demo/](../README.md).

Still Point Yoga, its address, and its phone number are made up.

## Prompts

Step 1:

> Build a website for my yoga studio, Still Point Yoga. We're at 9 Mill Lane,
> second floor. Classes Monday to Saturday at 7am and 6pm, Sunday at 10am
> only. Phone (555) 014-5520. Drop-in class $20, 5-class pass $90, monthly
> unlimited $140, private session $75, and your first class is free. Single
> self-contained HTML file with inline CSS and JS, no external assets.

Step 2 is the [demo/dental](../dental/) step 2 prompt with this request in
place of the dental one. The commands, model, skill version (`414fc8b`), and
codex-cli version are the same.

The model wrote the page to `still-point-yoga/dist/index.html` instead of
`index.html`, and tried to publish it to a hosting service. The sandbox
blocked the network, so nothing was published. That file is `before.html`.

## Numbers

Counts follow `demo/bakery`.

| | Before | After |
|---|---:|---:|
| Visible words (1280 / 320) | 405 / 405 | 95 / 95 |
| DOM elements | 227 | 107 |
| CSS declarations (checker) | 1215 | 624 |
| CSS declarations, including `@media` | 1362 | 716 |
| Page height at 1280px | 4745px | 3250px |
| Page height at 320px | 7245px | 4320px |
| axe violations, scroll-reveal content shown | 2 | 0 |
| Phone links (`tel:`) | 3 | 2 |
| Name, address, second floor, class times, phone, four prices, first class free | all | all |

## What the before page invented

None of these are in the after page.

- A booking form, "Choose a time and we'll hold your spot. No payment
  needed.", that sends nothing anywhere; its note says it keeps your
  information in the browser
- "Slow flow" as the name of the Sunday class
- "A grounded neighborhood practice for every body"
- What every class contains: "Clear, considered sequences create warmth and
  mobility", "Every class makes space to soften, integrate, and notice…"
- What each price covers: "any regularly scheduled time", "All scheduled
  group classes for one month", "Individual attention and a practice shaped
  around you"
- "Second floor, where the street noise softens."

## What was cut

- The announcement bar and the "First class free" nav button, which repeat
  the free class
- The "Practice" nav link and the label above each heading
- The scrolling slogan strip ("Breathe in", "Move gently", …)
- "Morning" and "Evening" under each class time
- The whole "Enough effort to feel alive" section and its three principles
- The line under each price and the "Choose a class" button
- The booking form and the script behind it
- The map drawing and its caption

## What the pass missed

- The hero illustration (an arch, a sun, and a figure) stays. Nothing else
  on the page refers to it.
- The hero keeps `min-height: calc(100vh - 76px)`, so at a tall viewport it
  grows with the window. That held for the illustration beside it too, so it
  isn't a height reserved for something removed.

## Every attempt

| # | Step | Model | Notes | Used |
|---|---|---|---|---|
| 1 | build | gpt-5.6-sol | 2026-11-06, 58 min, wrote `still-point-yoga/dist/index.html`, publish blocked | **before.html** |
| 2 | /less | gpt-5.6-sol | skill at `414fc8b` with the request, 29 min | **after.html** |

`before.png` and `after.png` are full-page screenshots at 1280 × 800, taken
after scrolling to the bottom so every section is revealed. The bakery
method (viewport as tall as the page) doesn't work here: the hero is sized
in `vh` and would fill the whole shot.
