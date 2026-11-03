// Self-tests. G5: the default focus ring passes (after); outline:none with no replacement fails (bad_after).
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
const w = run([out], env), wo = run([out, '--suffix', 'without'], env);
console.log([self, w, wo].join('').split('\n').filter(l => !l.includes('info:')).join('\n').trim());
const json = s => JSON.parse(readFileSync(`${out}/design-${s}.json`, 'utf8')).T01;
const ok = /T01 after\s+PASS/.test(self) && /T01 bad_after FAIL.*G5✗/.test(self)
  && json('with').startsWith('PASS') && /^FAIL.*G5✗/.test(json('without'));
console.log(ok ? 'self-test PASS' : 'self-test FAIL');
process.exit(ok ? 0 : 1);
