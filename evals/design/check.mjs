// Design checker for less D cases (spec-v0.3 §5, K-G1..K-G6, plus G7 overlay legibility).
//   node check.mjs self      checks each case's before, after and bad_after against before
//   node check.mjs OUT [ID] [--suffix without]  checks OUT/<id>.<suffix>.out.md (default with; HTML, fences allowed)
//   against before and writes OUT/design-<suffix>.json, which run.py sheet shows in the pass columns
// Gates decide PASS/FAIL; element and CSS declaration counts are printed for reference only.
import { readFileSync, existsSync, writeFileSync } from 'node:fs';
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
const norm = s => s.replace(/\s+/g, ' ').replace(/\s*([{}:;,()>])\s*/g, '$1').trim();

async function measure(page, src, c) {
  const html = c.format === 'jsx' ? jsx(src) : src;
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
  // G7: scroll so content sits under each fixed/sticky element with text; its text stays legible only if
  // its own fill is opaque or a backdrop-filter is set (computed style, not pixels, so it isn't flaky).
  const overlays = await page.evaluate(() => {
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
      const overlaps = texts.some(u => {
        jump(u.getBoundingClientRect().top + scrollY - e.offsetHeight / 2);
        const r = e.getBoundingClientRect(), t = u.getBoundingClientRect();
        return t.top < r.bottom && t.bottom > r.top && t.left < r.right && t.right > r.left;
      });
      const alpha = (s.backgroundColor.match(/rgba\([^)]*,\s*([\d.]+)\)/) || [, 1])[1];
      out.push({ key: e.tagName + ' ' + e.innerText.replace(/\s+/g, ' ').trim().slice(0, 40), overlaps, legible: +alpha >= 0.99 || s.backdropFilter !== 'none' });
      jump(0);
    }
    [root.style.scrollBehavior, document.body.style.scrollBehavior] = saved;
    return out;
  });
  const info = await page.evaluate(() => ({ elements: document.querySelectorAll('body *').length, decls: [...document.styleSheets].flatMap(s => [...s.cssRules]).reduce((n, r) => n + (r.style ? r.style.length : 0), 0) }));
  return { roles, sels, axe, nodes, focus, reflow, overlays, info };
}

function gates(b, a, c, width) {
  const hints = (c.must_remove_hint || []).join(' ').toLowerCase();
  const missingNodes = b.nodes.filter(n => !a.nodes.includes(n) && !hints.includes(n.split('"')[1].toLowerCase() || '\0'));
  const worse = b.focus.filter(f => { const g = a.focus.find(x => x.key === f.key); return g && ((f.ring && !g.ring) || (f.target && !g.target)); });
  const unreadable = b.overlays.filter(o => o.legible && a.overlays.some(x => x.key === o.key && x.overlaps && !x.legible));
  return {
    G1: a.roles.every(Boolean), G2: a.sels.every(Boolean),
    G3: a.axe.every(v => b.axe.includes(v)), G4: missingNodes.length === 0,
    G5: worse.length === 0, G6: width !== 320 || !b.reflow || a.reflow, G7: unreadable.length === 0,
    why: [...a.axe.filter(v => !b.axe.includes(v)), ...missingNodes.map(n => 'lost ' + n), ...worse.map(f => 'worse ' + f.key), ...unreadable.map(o => 'see-through ' + o.key)],
  };
}

const strip = s => s.replace(/^[\s\S]*?```\w*\n/, '').replace(/\n```[\s\S]*$/, '');
const argv = process.argv.slice(2);
const si = argv.indexOf('--suffix');
const suffix = si >= 0 ? argv.splice(si, 2)[1] : 'with';
const [mode, ...ids] = argv;
const results = {};
if (!mode) { console.log('usage: node check.mjs self | OUT [ID...]'); process.exit(2); }
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
      for (const k of ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7']) res[k] = (res[k] ?? true) && g[k];
      why.push(...g.why.map(w => `${vp.width}: ${w}`));
      if (!a.roles.every(Boolean)) why.push(`${vp.width}: roles ${JSON.stringify(c.must_keep_roles.filter((_, i) => !a.roles[i]))}`);
      if (!a.sels.every(Boolean)) why.push(`${vp.width}: selectors ${JSON.stringify(c.must_keep_selectors.filter((_, i) => !a.sels[i]))}`);
      info.push(`${vp.width}px elements ${b.info.elements}->${a.info.elements} decls ${b.info.decls}->${a.info.decls} axe(before) ${b.axe.length}`);
      await ctx.close();
    }
    const pass = Object.values(res).every(Boolean);
    if (!pass && label !== 'bad_after') failed++;
    if (label === 'output') results[c.id] = `${pass ? 'PASS' : 'FAIL'} ${Object.entries(res).map(([k, v]) => k + (v ? '✓' : '✗')).join(' ')}`;
    console.log(`${c.id} ${label.padEnd(9)} ${pass ? 'PASS' : 'FAIL'} ${Object.entries(res).map(([k, v]) => k + (v ? '✓' : '✗')).join(' ')}${why.length ? '  ' + [...new Set(why)].join('; ') : ''}`);
    console.log(`    info: ${info.join(' | ')}`);
  }
}
await browser.close();
if (mode !== 'self') writeFileSync(`${mode}/design-${suffix}.json`, JSON.stringify(results, null, 1) + '\n');
process.exit(failed ? 1 : 0);
