// Self-tests. G5: the default focus ring passes (after); outline:none with no replacement fails (bad_after).
// G7: a header already see-through before is a note, not FAIL (T02); a see-through after header fails even
// when its text changed (T03 bad_after).
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
const d03 = get('D03'), d04 = get('D04'), d05 = get('D05'), d07 = get('D07'), d11 = get('D11');
const regressions = [
  [d03, 'entity-emoji', d03.after.replace('Fast sync', '&#x1F680; Fast sync'), false],
  [d04, 'retag-testimonial', d04.after.replace('</main>', '<div>"Best tool ever!" — Happy Customer</div></main>'), false],
  [d04, 'useful-section', d04.after.replace('<form>', '<section><form>').replace('</form>', '</form></section>'), true],
  [d05, 'retag-slogan', d05.before.replace('<p>Empower', '<div>Empower').replace('way.</p>', 'way.</div>'), false],
  [d05, 'move-reply-time', d05.after.replace('<p>We reply within 2 business days.</p>', '').replace('</main>', '<p>We reply within 2 business days.</p></main>'), true],
  [d07, 'equivalent-effects', d07.before.replace('#e5e7eb', 'rgb(229,231,235)').replace('0 10px 30px', '0px 10px 30px'), false],
  [d11, 'useful-wrapper', d11.after.replace('<form', '<div><span aria-hidden="true"> / </span><form').replace('</form>', '</form></div>'), true],
  [d11, 'renamed-surfaces', d11.before.replace('✨ Profile', '').replaceAll('rounded-xl', 'rounded-lg'), false],
];
const cases = regressions.map(([base, name, output]) => {
  const row = { ...base, id: name };
  writeFileSync(`${out}/${name}.with.out.md`, output);
  return row;
});
writeFileSync(fixture, JSON.stringify({ evals: cases }));
run([out], { LESS_CASES: fixture });
const results = JSON.parse(readFileSync(`${out}/design-with.json`, 'utf8'));
for (const [, name, , expected] of regressions) {
  const correct = expected ? results[name].startsWith('PASS') : /FAIL.*G8✗/.test(results[name]);
  console.log(`${name}: ${correct ? 'PASS' : 'FAIL'} (${results[name]})`);
  ok &&= correct;
}
console.log(ok ? 'self-test PASS'  : 'self-test FAIL');
process.exit(ok ? 0 : 1);
