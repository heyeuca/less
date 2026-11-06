# Dental clinic page, before and after less

A demo for the `less` skill on a page an agent built. `before.html` is a
website for Brightside Dental, a made-up clinic, written by gpt-5.6-sol with
no skill loaded. `after.html` is that page after one `/less` pass by the same
model. Neither file was edited by hand. `before-after.png` boxes the main cuts
for the README; the pages themselves carry no boxes.

This is the README demo. It was picked from four topics, each built and cut
once with the same setup, because it lost the most; all four are in
[demo/](../README.md).

Brightside Dental, its address, and its phone number are made up.

## Prompts

Step 1, in a fresh `codex exec` process in an empty directory:

> Build a website for my dental clinic, Brightside Dental. We're at 88 Harbor
> Road. Open Monday to Thursday, 8am to 5pm, Friday 8am to noon, closed
> weekends. Phone (555) 014-3368. We offer checkup and cleaning $140, filling
> $180, teeth whitening $350, emergency visit $95, and kids' checkup $90.
> Single self-contained HTML file with inline CSS and JS, no external assets.

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
CLI default sampling. This is the same setup as [demo/bakery](../bakery/).

## Numbers

Counts follow `demo/bakery`.

| | Before | After |
|---|---:|---:|
| Visible words (1280 / 320) | 347 / 338 | 71 / 65 |
| DOM elements | 256 | 81 |
| CSS declarations (checker) | 1326 | 451 |
| CSS declarations, including `@media` | 1445 | 531 |
| Page height at 1280px | 4753px | 1999px |
| Page height at 320px | 7388px | 2341px |
| axe violations, scroll-reveal content shown | 18 | 2 |
| Page wider than the viewport (1280 / 320) | yes / yes | no / no |
| Phone links (`tel:`) | 6 | 4 |
| Name, address, hours, weekends closed, phone, five items and prices | all | all |

All axe violations are `color-contrast`. The 2 left in the after page are
the footer copyright line and year, which failed in the before page too. The
before page is wider than the viewport at both sizes because of its
scrolling slogan strip.

## What the before page invented

None of these were in the request. None are in the after page.

| Claim |
|---|
| Hero: "Modern, straightforward dental care for the whole family", "delivered with a gentle touch" |
| Hero checklist: "Family friendly" |
| Slogan strip: "Gentle care", "Healthy smiles", "All ages welcome" |
| A line under each service: "A thorough exam and fresh, polished smile", "Comfortable care to repair and protect", "Fast attention when your smile can't wait", … |
| A three-step visit process: "Start with a conversation", "Understand your options", "Leave a little brighter" |
| Location: "Find your brighter smile just down the road" |

Slogans that state no fact ("Feel good about your smile.", "Simple care.
Upfront prices.", "Right here on Harbor Road.") stay in the after page.

## What was cut

- The "Plan your visit" nav link and the label above each heading
- The hero line, its checklist, and the "View services" link
- The illustration: tooth, rings, the "Open today" status note, and the
  "Checkup + cleaning $140" note, which repeats a price
- The scrolling slogan strip
- The service icons and the line under each service
- The whole "Build a simple estimate" section: a checkbox list of the same
  five services and prices with a running total
- The map drawing and the line under the address
- The whole "Care that feels clear, calm, and human" section and its smiley
  drawing
- The closing "Ready to find your Brightside?" band, which repeats the phone
  link
- Scroll-reveal animation, the open-status and estimate scripts, and the CSS
  that only styled those pieces

## What the pass missed

Nothing we could find in the after page is invented, broken, or left
reserving space for something removed. The address card now holds only the
address, so it is shorter than the hours card beside it.

## Every attempt

Four topics were each built and cut once; see [demo/](../README.md). For this
topic:

| # | Step | Model | Notes | Used |
|---|---|---|---|---|
| 1 | build | gpt-5.6-sol | 2026-11-06, 30 min, wrote `index.html` as asked | **before.html** |
| 2 | /less | gpt-5.6-sol | skill at `414fc8b` with the request, 30 min | **after.html** |

## The image

`before-after.png` is built the same way as the bakery one: full-page
screenshots at 1280px wide with the viewport as tall as the page, so every
section is revealed, cropped to 1280px. Boxes are overlays drawn at render
time: red for an invented claim, gray for decoration or a repeat. They mark
the main cuts, not all of them; the lists above are complete. Both pages are
shown at the same scale and top-aligned.
