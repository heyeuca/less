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
console.log(ok ? 'self-test PASS' : 'self-test FAIL');
process.exit(ok ? 0 : 1);
