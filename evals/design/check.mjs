// Design checker for less D cases (spec-v0.3 §5, K-G1..K-G6, plus G7 overlay legibility and G8 required removals).
//   node check.mjs self      checks each case's before, after and bad_after against before
//   node check.mjs OUT [ID] [--suffix without]  checks OUT/<id>.<suffix>.out.md (default with; HTML, fences allowed)
//   against before and writes OUT/design-<suffix>.json, which run.py sheet shows in the pass columns
// Gates decide PASS/FAIL; element and CSS declaration counts are printed for reference only.
import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { chromium } from 'playwright';
import { AxeBuilder } from '@axe-core/playwright';

const cases = JSON.parse(readFileSync(process.env.LESS_CASES || new URL('../evals.json', import.meta.url))).evals.filter(c => c.format === 'html' || c.format === 'jsx');
// JSX cases are static markup: render the returned tree to HTML with the precompiled Tailwind fixture.
const TAILWIND = readFileSync(new URL('./fixtures/tailwind.css', import.meta.url), 'utf8');
const jsx = src => {
  const body = src.slice(src.indexOf('return (') + 8, src.lastIndexOf(');'))
    .replace(/\{\/\*[\s\S]*?\*\/\}/g, '').replace(/\sclassName=/g, ' class=').replace(/\shtmlFor=/g, ' for=')
    .replace(/\s\w+=\{[^}]*\}/g, '').replace(/<(\w+)([^>]*?)\s*\/>/g, '<$1$2></$1>');
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Case</title><style>${TAILWIND}</style></head><body>${body}</body></html>`;
};
const VIEWPORTS = [{ width: 1280, height: 800 }, { width: 320, height: 640 }];
const TAGS = ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'];
const INTERACTIVE = /^(button|link|textbox|searchbox|checkbox|radio|combobox|slider|spinbutton|switch|tab|menuitem|option|listbox)$/;
// Dynamic pseudo-classes never match a static page, so such strings are CSS text, as are strings that aren't selectors.
const STATEFUL = /:(hover|focus|focus-visible|focus-within|active|visited)\b/;
// Smallest backdrop blur (px) that G7 accepts in place of an opaque fill.
const MIN_BLUR = 4;
// Rendered-text removals match whole words: "New" must not match "renew" or "news". A boundary applies
// only at an end that is a word character, so an emoji glued to a word ("🚀Fast") still matches.
const wordMatch = (text, snippet) => {
  // Letters, digits, and combining marks are word characters ("cafe\u0301" must not match "cafe\u0301teria").
  const esc = snippet.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), chars = [...snippet], word = /[\p{L}\p{N}\p{M}]/u;
  const pre = word.test(chars[0]) ? '(?<![\\p{L}\\p{N}\\p{M}])' : '', post = word.test(chars.at(-1)) ? '(?![\\p{L}\\p{N}\\p{M}])' : '';
  return new RegExp(pre + esc + post, 'u').test(text);
};
const norm = s => s.replace(/\s+/g, ' ').replace(/\s*([{}:;,()>])\s*/g, '$1').trim();

async function measure(page, src, c) {
  const html = c.format === 'jsx' ? jsx(src) : src;
  // The pointer survives setContent; park it outside the page so an earlier hover check can't leave
  // this page's axe, focus, and style measurements in a hovered state ((0, 0) may be on an element).
  await page.mouse.move(-1, -1);
  await page.setContent(html);
  // Let entrance animations settle so axe sees final colors (infinite ones are capped at 2 s).
  await page.evaluate(() => Promise.race([Promise.all(document.getAnimations().map(a => a.finished.catch(() => {}))), new Promise(r => setTimeout(r, 2000))]));
  const roles = [];
  for (const [role, name] of c.must_keep_roles || [])
    roles.push((name ? await page.getByRole(role, { name, exact: true }).count() : await page.getByRole(role).count()) >= 1);
  const sels = [];
  for (const s of c.must_keep_selectors || []) {
    let n = null;
    if (!STATEFUL.test(s)) n = await page.evaluate(s => { try { return document.querySelectorAll(s).length; } catch { return null; } }, s);
    sels.push(n === null ? norm(src).includes(norm(s)) : n >= 1);
  }
  // Visible text that must survive, such as an arrow that is data rather than chrome.
  const shown = norm(await page.locator('body').innerText()).toLowerCase();
  for (const s of c.must_keep_rendered_text || []) sels.push(shown.includes(norm(s).toLowerCase()));
  // Reading order (K15): these texts still appear in this order in the page's visible text.
  if (c.must_keep_order) {
    const at = c.must_keep_order.map(s => shown.indexOf(norm(s).toLowerCase()));
    sels.push(at.every((i, n) => i >= 0 && (n === 0 || i > at[n - 1])));
  }
  // Focus order (K15): pressing Tab from the top reaches these names in this order, so a tabindex or other
  // change that reorders focus fails even when the visible text keeps its order. Names are aria-label,
  // label text, or text content.
  if (c.must_keep_focus_order) {
    await page.evaluate(() => document.activeElement?.blur());
    const reached = [];
    for (let n = 0; n < 50; n++) {
      await page.keyboard.press('Tab');
      const name = await page.evaluate(() => {
        const e = document.activeElement;
        if (!e || e === document.body) return null;
        return norm(e.getAttribute('aria-label') || e.labels?.[0]?.textContent || e.textContent || '');
        function norm(s) { return s.replace(/\s+/g, ' ').trim(); }
      });
      if (name === null || reached.includes(name)) break;
      reached.push(name);
    }
    const at = c.must_keep_focus_order.map(s => reached.indexOf(s));
    sels.push(at.every((i, n) => i >= 0 && (n === 0 || i > at[n - 1])));
    await page.evaluate(() => document.activeElement?.blur());
  }
  const axe = (await new AxeBuilder({ page }).withTags(TAGS).analyze()).violations
    .flatMap(v => v.nodes.map(n => v.id + ' ' + n.target.join(' ')));
  const nodes = (await page.locator('body').ariaSnapshot()).split('\n')
    .map(l => l.match(/^\s*- (\w+)(?: "([^"]*)")?/)).filter(m => m && INTERACTIVE.test(m[1])).map(m => `${m[1]} "${m[2] || ''}"`);
  const focus = [];
  const els = page.locator('a[href],button,input,select,textarea,[tabindex]:not([tabindex="-1"])');
  for (let i = 0; i < await els.count(); i++) {
    const el = els.nth(i);
    if (!(await el.isVisible())) continue;
    const key = (await el.evaluate(e => e.tagName + ' ' + (e.getAttribute('aria-label') || e.textContent || e.id).trim()));
    const box = await el.boundingBox();
    const style = () => el.evaluate(e => { const s = getComputedStyle(e); // An outline with style none or zero width is invisible, whatever its width and color.
      const outline = s.outlineStyle === 'none' || parseFloat(s.outlineWidth) === 0 ? 'none' : [s.outlineStyle, s.outlineWidth, s.outlineColor].join(' ');
      return [outline, s.boxShadow, s.borderColor].join('|'); });
    const plain = await style();
    await page.keyboard.press('Tab'); // makes :focus-visible apply
    await el.focus();
    const ring = (await style()) !== plain;
    await el.evaluate(e => e.blur());
    focus.push({ key, ring, target: Math.min(box.width, box.height) >= 24 });
  }
  const reflow = await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1);
  // G7: scroll so content sits under each fixed/sticky element with text; its text counts as legible only if
  // its own fill is opaque or its backdrop-filter blurs by at least MIN_BLUR px (computed style, not pixels,
  // so it isn't flaky). blur(0) or a filter without blur doesn't count. This is a heuristic, not a contrast
  // measurement: it can't tell whether the text reads well over what shows through.
  const overlays = await page.evaluate(minBlur => {
    // Force instant scrolling so a page's `scroll-behavior: smooth` can't leave the probe mid-scroll.
    const root = document.documentElement, saved = [root.style.scrollBehavior, document.body.style.scrollBehavior];
    root.style.scrollBehavior = document.body.style.scrollBehavior = 'auto';
    const jump = y => {
      const top = Math.max(0, Math.min(y, root.scrollHeight - root.clientHeight));
      window.scrollTo({ top, behavior: 'instant' });
      if (Math.abs(scrollY - top) > 1) throw new Error(`G7 scroll stuck at ${scrollY}, wanted ${top}`);
    };
    const out = [];
    for (const e of document.querySelectorAll('body *')) {
      const s = getComputedStyle(e);
      if (!['fixed', 'sticky'].includes(s.position) || !e.innerText.trim()) continue;
      // Scroll each text block in turn to the element's middle; it overlaps if any block ends up under it.
      const texts = [...document.querySelectorAll('body *')].filter(u => !e.contains(u) && !u.contains(e)
        && [...u.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())).slice(0, 50);
      let rect = e.getBoundingClientRect();
      const overlaps = texts.some(u => {
        jump(u.getBoundingClientRect().top + scrollY - e.offsetHeight / 2);
        const r = e.getBoundingClientRect(), t = u.getBoundingClientRect();
        rect = r;
        return t.top < r.bottom && t.bottom > r.top && t.left < r.right && t.right > r.left;
      });
      // rgba(r, g, b, a) or modern syntax with a slash alpha, e.g. color(display-p3 1 1 1 / 0.6).
      const alpha = (s.backgroundColor.match(/(?:rgba\([^)]*,\s*|\/\s*)([\d.]+)\)/) || [, 1])[1] * s.opacity;
      const blur = Math.max(0, ...[...s.backdropFilter.matchAll(/blur\(([\d.]+)px\)/g)].map(m => +m[1]));
      out.push({ key: e.tagName + ' ' + e.innerText.replace(/\s+/g, ' ').trim().slice(0, 40), tag: e.tagName,
        top: rect.top, bottom: rect.bottom, width: rect.width, overlaps, legible: alpha >= 0.99 || blur >= minBlur });
      jump(0);
    }
    [root.style.scrollBehavior, document.body.style.scrollBehavior] = saved;
    return out;
  }, MIN_BLUR);
  const info = await page.evaluate(() => ({ elements: document.querySelectorAll('body *').length, decls: [...document.styleSheets].flatMap(s => [...s.cssRules]).reduce((n, r) => n + (r.style ? r.style.length : 0), 0) }));
  const removed = [];
  for (const selector of c.must_remove_selectors || [])
    removed.push(await page.locator(selector).count() === 0);
  for (const snippet of c.must_remove_text || [])
    removed.push(!norm(src).includes(norm(snippet)));
  // Browser text decodes entities, so markup spelling cannot hide visible copy.
  const text = norm(await page.locator('body').innerText()).toLowerCase();
  // Also each visible element that CSS sets apart (not display:inline, or with side margin, padding, or
  // border): that spacing doesn't reach innerText, so a styled "01" next to "Send" would otherwise read
  // as "01send". Plain inline runs stay joined, so <b>New</b>ark is still the word "Newark".
  const pieces = (await page.locator('body *:visible').evaluateAll(els => els.filter(e => {
    const s = getComputedStyle(e);
    return s.display !== 'inline' || ['marginLeft', 'marginRight', 'paddingLeft', 'paddingRight',
      'borderLeftWidth', 'borderRightWidth'].some(k => parseFloat(s[k]) > 0);
  }).map(e => e.innerText || ''))).map(t => norm(t).toLowerCase());
  for (const snippet of c.must_remove_rendered_text || [])
    removed.push(![text, ...pieces].some(t => wordMatch(t, norm(snippet).toLowerCase())));
  if (c.must_remove_computed_background) {
    removed.push(await page.evaluate(() => ![...document.querySelectorAll('*')].some(el =>
      [null, '::before', '::after'].some(pseudo =>
        /(linear|radial|conic)-gradient/i.test(getComputedStyle(el, pseudo).backgroundImage)))));
  }
  for (const { selector, properties, hover, reduced_motion } of c.must_have_styles || []) {
    // reduced_motion: check the styles a visitor who asked for reduced motion gets.
    if (reduced_motion) await page.emulateMedia({ reducedMotion: 'reduce' });
    const matches = page.locator(selector);
    removed.push(await matches.count() > 0);
    for (let i = 0; i < await matches.count(); i++) {
      const el = matches.nth(i);
      if (hover) await el.hover();
      removed.push(await el.evaluate((el, properties) => Object.entries(properties).every(
        ([key, expected]) => getComputedStyle(el).getPropertyValue(key) === expected), properties));
    }
    if (reduced_motion) await page.emulateMedia({ reducedMotion: 'no-preference' });
  }
  // Separation (K14): every match after the first starts at least `min` px below the nearest text above it
  // in its column, however the space is made (gap, margin, padding), so items stay apart once borders go.
  for (const { selector, min } of c.must_separate || []) {
    removed.push(await page.evaluate(([selector, min]) => {
      const els = [...document.querySelectorAll(selector)];
      const texts = [...document.querySelectorAll('body *')].filter(u =>
        [...u.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()));
      return els.length > 1 && els.slice(1).every(el => {
        const r = el.getBoundingClientRect();
        const above = texts.filter(u => !el.contains(u) && !u.contains(el)
          && (u.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING)).map(u => u.getBoundingClientRect())
          .filter(t => t.left < r.right && t.right > r.left);
        return above.length > 0 && r.top - Math.max(...above.map(t => t.bottom)) >= min;
      });
    }, [selector, min]));
  }
  // Consolidation (C14): all matches share one computed value per property; which value is up to the edit.
  for (const { selector, properties } of c.must_share || []) {
    removed.push(await page.evaluate(([selector, properties]) => {
      const els = [...document.querySelectorAll(selector)];
      return els.length > 1 && properties.every(p => new Set(els.map(e => getComputedStyle(e).getPropertyValue(p))).size === 1);
    }, [selector, properties]));
  }
  // Restructure (C15): each match fills at least `min_ratio` of main's content width, so content doesn't
  // stay in a column beside an emptied track.
  for (const { selector, min_ratio } of c.must_span || []) {
    removed.push(await page.evaluate(([selector, ratio]) => {
      const host = document.querySelector('main') || document.body, s = getComputedStyle(host);
      const width = host.clientWidth - parseFloat(s.paddingLeft) - parseFloat(s.paddingRight);
      const els = [...document.querySelectorAll(selector)];
      return els.length > 0 && els.every(e => e.getBoundingClientRect().width >= ratio * width);
    }, [selector, min_ratio]));
  }
  if (c.must_remove_nested_surfaces) {
    removed.push(await page.evaluate(() => {
      const surface = el => {
        const s = getComputedStyle(el);
        return s.boxShadow !== 'none' || ['Top', 'Right', 'Bottom', 'Left'].some(side =>
          s[`border${side}Style`] !== 'none' && parseFloat(s[`border${side}Width`]) > 0);
      };
      return ![...document.querySelectorAll('div,section,article,aside,main')].some(el => surface(el) &&
        [...el.querySelectorAll('div,section,article,aside,main')].some(surface));
    }));
  }
  return { roles, sels, axe, nodes, focus, reflow, overlays, info, removed };
}

function gates(b, a, c, width) {
  const hints = (c.must_remove_hint || []).join(' ').toLowerCase();
  const missingNodes = b.nodes.filter(n => !a.nodes.includes(n) && !hints.includes(n.split('"')[1].toLowerCase() || '\0'));
  const worse = b.focus.filter(f => { const g = a.focus.find(x => x.key === f.key); return g && ((f.ring && !g.ring) || (f.target && !g.target)); });
  // G7 judges every after-page overlay on its own. A see-through one fails unless the before page already had
  // a see-through overlapping one with the same tag at about the same place (top or bottom edge and width
  // within 16 px); that only labels it pre-existing, it never skips the check.
  const near = (x, y) => Math.abs(x - y) <= 16;
  const seeThrough = o => o.overlaps && !o.legible;
  const preExisting = o => b.overlays.some(p => seeThrough(p) && p.tag === o.tag
    && (near(p.top, o.top) || near(p.bottom, o.bottom)) && near(p.width, o.width));
  const unreadable = a.overlays.filter(o => seeThrough(o) && !preExisting(o));
  const already = a.overlays.filter(o => seeThrough(o) && preExisting(o));
  return {
    G1: a.roles.every(Boolean), G2: a.sels.every(Boolean),
    G3: a.axe.every(v => b.axe.includes(v)), G4: missingNodes.length === 0,
    G5: worse.length === 0, G6: width !== 320 || !b.reflow || a.reflow, G7: unreadable.length === 0,
    G8: a.removed.every(Boolean),
    why: [...(a.removed.every(Boolean) ? [] : ['required removal remains']), ...a.axe.filter(v => !b.axe.includes(v)), ...missingNodes.map(n => 'lost ' + n), ...worse.map(f => 'worse ' + f.key), ...unreadable.map(o => 'see-through ' + o.key), ...already.map(o => 'note: pre-existing see-through ' + o.key)],
  };
}

const strip = s => s.replace(/^[\s\S]*?```\w*\n/, '').replace(/\n```[\s\S]*$/, '');
const argv = process.argv.slice(2);
const si = argv.indexOf('--suffix');
const suffix = si >= 0 ? argv.splice(si, 2)[1] : 'with';
const [mode, ...ids] = argv;
const results = {};
if (!mode) { console.log('usage: node check.mjs self | OUT [ID...]'); process.exit(2); }
// Grade only with the inputs the prompts were made from (run.py prompts records them in OUT/run.json).
// A run with run.json is checked against every recorded input; one without is graded but marked unverified.
const recorded = mode !== 'self' && existsSync(`${mode}/run.json`)
  ? JSON.parse(readFileSync(`${mode}/run.json`, 'utf8')).inputs || {} : null;
if (recorded) {
  const root = new URL('../../', import.meta.url);
  const hash = name => existsSync(new URL(name, root)) && createHash('sha256').update(readFileSync(new URL(name, root))).digest('hex');
  // The checker's own inputs must all be recorded, and every recorded input and prompt must still match.
  const own = ['evals/evals.json', 'evals/design/check.mjs', 'evals/design/fixtures/tailwind.css',
    'evals/design/package.json', 'evals/design/package-lock.json'];
  const prompts = JSON.parse(readFileSync(`${mode}/run.json`, 'utf8')).prompts || {};
  const promptHash = name => existsSync(`${mode}/${name}`) && createHash('sha256').update(readFileSync(`${mode}/${name}`)).digest('hex');
  const changed = [...own.filter(name => !(name in recorded)),
    ...Object.entries(recorded).filter(([name, digest]) => hash(name) !== digest).map(([name]) => name),
    ...Object.entries(prompts).filter(([name, digest]) => promptHash(name) !== digest).map(([name]) => name)];
  const refuse = process.env.LESS_CASES ? 'LESS_CASES would grade a recorded run with other cases'
    : !Object.keys(recorded).length ? `${mode}/run.json records no inputs`
    : changed.length ? `${changed.join(', ')} changed since ${mode}/run.json was written; grade at the commit that wrote it` : '';
  if (refuse) { console.log(refuse); process.exit(2); }
} else if (mode !== 'self') {
  console.log(`warning: no run.json in ${mode}; results are marked unverified`);
  results._unverified = true;
}
const browser = await chromium.launch();
let failed = 0;
for (const c of cases.filter(c => !ids.length || ids.includes(c.id))) {
  const cand = mode === 'self'
    ? [['before', c.before], ['after', c.after === 'unchanged' ? c.before : c.after], ...(c.bad_after ? [['bad_after', c.bad_after]] : [])]
    : [['output', existsSync(`${mode}/${c.id}.${suffix}.out.md`) ? strip(readFileSync(`${mode}/${c.id}.${suffix}.out.md`, 'utf8')) : null]];
  for (const [label, html] of cand) {
    if (html === null) { console.log(`${c.id} ${label} missing`); results[c.id] = 'missing'; failed++; continue; }
    const res = {}; const why = []; const info = [];
    for (const vp of VIEWPORTS) {
      const ctx = await browser.newContext({ viewport: vp }), page = await ctx.newPage();
      const b = await measure(page, c.before, c), a = await measure(page, html, c);
      const g = gates(b, a, c, vp.width);
      // The original is a preservation control, not a reduced candidate.
      if (label === 'before') {
        g.G8 = true;
        g.why = g.why.filter(w => w !== 'required removal remains');
      }
      for (const k of ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8']) res[k] = (res[k] ?? true) && g[k];
      why.push(...g.why.map(w => `${vp.width}: ${w}`));
      if (!a.roles.every(Boolean)) why.push(`${vp.width}: roles ${JSON.stringify(c.must_keep_roles.filter((_, i) => !a.roles[i]))}`);
      if (!a.sels.every(Boolean)) why.push(`${vp.width}: kept ${JSON.stringify([...(c.must_keep_selectors || []), ...(c.must_keep_rendered_text || []), ...(c.must_keep_order ? ['order: ' + c.must_keep_order.join(' > ')] : []), ...(c.must_keep_focus_order ? ['focus order: ' + c.must_keep_focus_order.join(' > ')] : [])].filter((_, i) => !a.sels[i]))}`);
      info.push(`${vp.width}px elements ${b.info.elements}->${a.info.elements} decls ${b.info.decls}->${a.info.decls} axe(before) ${b.axe.length}`);
      await ctx.close();
    }
    const pass = Object.values(res).every(Boolean);
    if ((!pass && label !== 'bad_after') || (pass && label === 'bad_after')) failed++;
    if (label === 'output') results[c.id] = `${pass ? 'PASS' : 'FAIL'} ${Object.entries(res).map(([k, v]) => k + (v ? '✓' : '✗')).join(' ')}`;
    console.log(`${c.id} ${label.padEnd(9)} ${pass ? 'PASS' : 'FAIL'} ${Object.entries(res).map(([k, v]) => k + (v ? '✓' : '✗')).join(' ')}${why.length ? '  ' + [...new Set(why)].join('; ') : ''}`);
    console.log(`    info: ${info.join(' | ')}`);
  }
}
await browser.close();
if (mode !== 'self') writeFileSync(`${mode}/design-${suffix}.json`, JSON.stringify(results, null, 1) + '\n');
process.exit(failed ? 1 : 0);
