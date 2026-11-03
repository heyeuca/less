// G5 self-test: the default focus ring passes (after); outline:none with no replacement fails (bad_after).
import { execFileSync } from 'node:child_process';
const out = execFileSync('node', ['check.mjs', 'self'], { env: { ...process.env, LESS_CASES: 'test/fixtures.json' }, encoding: 'utf8' });
console.log(out.trim());
const ok = /T01 after\s+PASS/.test(out) && /T01 bad_after FAIL.*G5✗/.test(out);
console.log(ok ? 'self-test PASS' : 'self-test FAIL');
process.exit(ok ? 0 : 1);
