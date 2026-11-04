// Self-tests. G5: the default focus ring passes (after); outline:none with no replacement fails (bad_after).
// G7: a header already see-through before is a note, not FAIL (T02); a see-through after header fails even
// when its text changed (T03 bad_after). G7 needs a real blur: blur(8px) passes, blur(0) fails (T04). A hover
// check on one page leaves nothing hovered when the next page is measured (T05).
// --suffix: OUT mode reads <id>.with.out.md by default and <id>.without.out.md with --suffix without.
import { execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
const run = (args, env = {}) => { try { return execFileSync('node', ['check.mjs', ...args], { env: { ...process.env, ...env }, encoding: 'utf8' }); } catch (e) { return e.stdout; } };
const env = { LESS_CASES: 'test/fixtures.json' };
const self = run(['self'], env);
const [c] = JSON.parse(readFileSync('test/fixtures.json', 'utf8')).evals;
const out = mkdtempSync(tmpdir() + '/less-');
writeFileSync(`${out}/T01.with.out.md`, '```html\n' + c.after + '\n```\n');
writeFileSync(`${out}/T01.without.out.md`, c.bad_after);
const w = run([out, 'T01'], env), wo = run([out, 'T01', '--suffix', 'without'], env);
console.log([self, w, wo].join('').split('\n').filter(l => !l.includes('info:')).join('\n').trim());
const json = s => JSON.parse(readFileSync(`${out}/design-${s}.json`, 'utf8')).T01;
let ok = /T01 after\s+PASS/.test(self) && /T01 bad_after FAIL.*G5✗/.test(self)
  && /T02 after\s+PASS.*note: pre-existing see-through/.test(self)
  && /T03 after\s+PASS/.test(self) && /T03 bad_after FAIL.*G7✗.*see-through HEADER Acme Docs/.test(self)
  && /T04 after\s+PASS/.test(self) && /T04 bad_after FAIL.*G7✗/.test(self)
  && /T05 before\s+PASS/.test(self) && /T05 after\s+PASS/.test(self) && /T06 bad_after FAIL.*G7✗/.test(self)
  && json('with').startsWith('PASS') && /^FAIL.*G5✗/.test(json('without'));
// An unchanged candidate must fail a required removal; an accepted negative
// fixture must make self mode exit nonzero.
const fixture = `${out}/cases.json`;
writeFileSync(fixture, JSON.stringify({ evals: [{ ...c,
  must_remove_selectors: ['main'], bad_after: c.after }] }));
writeFileSync(`${out}/T01.with.out.md`, c.before);
run([out], { LESS_CASES: fixture });
ok &&= /FAIL.*G8✗/.test(json('with'));
writeFileSync(fixture, JSON.stringify({ evals: [{ ...c, bad_after: c.after }] }));
let rejected = false;
try { execFileSync('node', ['check.mjs', 'self'], {
  env: { ...process.env, LESS_CASES: fixture }, stdio: 'pipe' }); }
catch (e) { rejected = e.status === 1; }
ok &&= rejected;
// Exercise rendered-content and computed-style checks against equivalent markup.
const design = JSON.parse(readFileSync('../evals.json', 'utf8')).evals;
const get = id => design.find(row => row.id === id);
const d03 = get('D03'), d04 = get('D04'), d05 = get('D05'), d07 = get('D07'), d11 = get('D11'), d13 = get('D13');
const d01 = get('D01'), d02 = get('D02'), d06 = get('D06'), d09 = get('D09'), d10 = get('D10'), d12 = get('D12');
const d18 = get('D18'), d14 = get('D14'), d22 = get('D22');
// Custom CSS keeps alternate effects real even when their utility classes are
// absent from the precompiled Tailwind fixture.
const toolbarHTML = src => `<html lang="en"><head><title>Toolbar</title><meta name="viewport" content="width=device-width"><style>${readFileSync('fixtures/tailwind.css', 'utf8')}</style></head><body>${src.slice(src.indexOf('return (') + 8, src.lastIndexOf(');')).replaceAll('className=', 'class=')}</body></html>`;
const toolbar = { ...d12, format: 'html', before: toolbarHTML(d12.before), after: toolbarHTML(d12.after) };
const effect = css => toolbar.after.replace('</head>', `<style>${css}</style></head>`);
const regressions = [
  [d01, 'renamed-inner-card', d01.before.replace('<div class="card"><div class="card">', '<div class="card"><section class="inner">').replace('}</style>', '}.inner{border:1px solid #ddd}</style>').replace('</div></div>', '</section></div>'), false],
  [d02, 'uppercase-gradient', d02.after.replace('</style>', '.hero{background:LINEAR-GRADIENT(135deg,#f5f0ff,#e0f2ff)}</style>'), false],
  [d02, 'escaped-gradient', d02.after.replace('</style>', String.raw`.hero{background:\6c inear-gradient(135deg,#f5f0ff,#e0f2ff)}</style>`), false],
  [d04, 'retained-logos', d04.after.replace('</main>', '<img src="data:," alt="Logo"><img src="data:," alt="Logo"></main>'), false],
  [d02, 'radial-gradient', d02.after.replace('</style>', '.hero{background:radial-gradient(circle,#f5f0ff,#e0f2ff)}</style>'), false],
  [d02, 'conic-gradient', d02.after.replace('</style>', '.hero{background:repeating-conic-gradient(#f5f0ff 0 10%,#e0f2ff 0 20%)}</style>'), false],
  [d06, 'heading-animation', d06.after.replace('</style>', '@keyframes rise{from{opacity:0}to{opacity:1}}h2{animation:rise .6s}</style>'), false],
  [d06, 'renamed-animation', d06.after.replace('</style>', '@keyframes rise{from{opacity:0}to{opacity:1}}section{animation:rise .6s}</style>'), false],
  [d09, 'renamed-eyebrow', d09.after.replace('<h2', '<span class="label">HEADS UP</span><h2'), false],
  [d10, 'renamed-badge', d10.after.replace('<h2', '<span class="label">New</span><h2'), false],
  [d11, 'retagged-surfaces', d11.before.replace('✨ Profile', '').replace('<div', '<section').replace('</div>\n    </main>', '</section>\n    </main>'), false],
  [toolbar, 'alternate-shadow', effect('button{box-shadow:0 1px 2px #555}'), false],
  [toolbar, 'alternate-gradient', effect('nav{background-image:linear-gradient(red,blue)}'), false],
  [toolbar, 'alternate-transition', effect('button{transition:box-shadow .3s}'), false],
  [toolbar, 'alternate-hover', effect('button:hover{scale:1.1}'), false],
  [d03, 'entity-emoji', d03.after.replace('Fast sync', '&#x1F680; Fast sync'), false],
  [d04, 'retag-testimonial', d04.after.replace('</main>', '<div>"Best tool ever!" — Happy Customer</div></main>'), false],
  [d04, 'useful-section', d04.after.replace('<form>', '<section><form>').replace('</form>', '</form></section>'), true],
  [d05, 'retag-slogan', d05.before.replace('<p>Empower', '<div>Empower').replace('way.</p>', 'way.</div>'), false],
  [d05, 'move-reply-time', d05.after.replace('<p>We reply within 2 business days.</p>', '').replace('</main>', '<p>We reply within 2 business days.</p></main>'), true],
  [d07, 'equivalent-effects', d07.before.replace('#e5e7eb', 'rgb(229,231,235)').replace('0 10px 30px', '0px 10px 30px'), false],
  [d11, 'useful-wrapper', d11.after.replace('<form', '<div><span aria-hidden="true"> / </span><form').replace('</form>', '</form></div>'), true],
  [d11, 'renamed-surfaces', d11.before.replace('✨ Profile', '').replaceAll('rounded-xl', 'rounded-lg'), false],
  [d13, 'renamed-blob', d13.after.replace('</style>', '.orb{position:absolute;width:320px;height:320px;filter:blur(60px);z-index:-1}</style>').replace('<main>', '<main><div class="orb"></div>'), false],
  [d14, 'renamed-marker', d14.before.replaceAll('class="num"', 'class="n"'), false],
  [d14, 'glued-marker', d14.before.replace('.num{', '.n{').replaceAll('class="num"', 'class="n"').replaceAll('</span> ', '</span>'), false],
  [d22, 'hero-only-opt-out', d22.after.replace('*{animation:none!important}', '.hero{animation:none}'), false],
  [d18, 'route-arrow-removed', d18.after.replace('Tokyo → Osaka', 'Tokyo to Osaka'), false, 'G2'],
  [d13, 'unstuck-header', d13.after.replace('position:sticky;top:0;', ''), false],
  [d03, 'glued-emoji', d03.after.replace('Fast sync', '🚀Fast sync'), false],
  [d10, 'split-word', d10.after.replace('<h2>Orders</h2>', '<h2>Orders</h2><p>Ships from our <b>New</b>ark office.</p>'), true],
  [d10, 'renew-copy', d10.after.replace('<h2>Orders</h2>', '<h2>Orders</h2><p>Renew your plan. See the news.</p>'), true],
  [d13, 'opaque-header', d13.after.replace('background:rgba(255,255,255,.88);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)', 'background:#fff'), true],
];
const cases = regressions.map(([base, name, output]) => {
  const row = { ...base, id: name };
  writeFileSync(`${out}/${name}.with.out.md`, output);
  return row;
});
writeFileSync(fixture, JSON.stringify({ evals: cases }));
run([out], { LESS_CASES: fixture });
const results = JSON.parse(readFileSync(`${out}/design-with.json`, 'utf8'));
// A rejected output must fail the named gate (G8, required removals, unless stated).
for (const [, name, , expected, gate = 'G8'] of regressions) {
  const correct = expected ? results[name].startsWith('PASS') : new RegExp(`FAIL.*${gate}✗`).test(results[name]);
  console.log(`${name}: ${correct ? 'PASS' : 'FAIL'} (${results[name]})`);
  ok &&= correct;
}
// OUT mode refuses to grade once a recorded input has changed since run.py prompts.
const stale = mkdtempSync(tmpdir() + '/less-');
writeFileSync(`${stale}/run.json`, JSON.stringify({ inputs: { 'evals/evals.json': 'stale' } }));
const { LESS_CASES, ...plain } = process.env;
let refused = false;
try { execFileSync('node', ['check.mjs', stale], { env: plain, stdio: 'pipe' }); }
catch (e) { refused = e.status === 2 && /changed since/.test(e.stdout); }
console.log(`stale-inputs: ${refused ? 'PASS' : 'FAIL'}`);
ok &&= refused;
console.log(ok ? 'self-test PASS'  : 'self-test FAIL');
process.exit(ok ? 0 : 1);
