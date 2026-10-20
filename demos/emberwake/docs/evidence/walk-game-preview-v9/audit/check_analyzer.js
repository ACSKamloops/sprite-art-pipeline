// Offline only: replay retained snapshots through the exact current analyzer.
const fs = require('node:fs');
const vm = require('node:vm');
const root = '/home/astra/projects/emberwake-demo';
const output = '/home/astra/artifacts/emberwake-v9-evidence-audit-v1';
const source = fs.readFileSync(root + '/tests/browser_eight_directions.js', 'utf8');
const start = source.indexOf('const analyzeActionTrace = function analyzeActionTrace(trace) {');
const end = source.indexOf('  const onConsole', start);
if (start < 0 || end < 0) throw Error('Analyzer extraction failed');
const analyze = vm.runInNewContext(source.slice(start, end) + '\nanalyzeActionTrace;');
const report = JSON.parse(fs.readFileSync(root + '/docs/evidence/walk-game-preview-v9/BROWSER-EIGHT-DIRECTIONS.json'));
const assert = require('node:assert/strict');
const clone = value => JSON.parse(JSON.stringify(value));
const locked = t => t.samples.filter(x => x.snapshot.mode === 'play' && x.snapshot.hero.state === t.context.pose && x.snapshot.hero.state_left > 0);
const compact = s => ({mode:s.mode,test_mode:s.test_mode,position:s.position,physics_tick:s.physics_tick,physics_hz:s.physics_hz,hero:s.hero,projectiles:s.projectiles});
const rows = report.actionTraces.map(t => {
  const value = analyze(t), c = t.context;
  const receipt = text => report.receipts.find(r => r.note === text + c.id + ' ' + c.view);
  assert.deepStrictEqual(receipt('ordinary ' + c.pose + ' commits requested diagonal ').data, clone(compact(value.started)));
  assert.deepStrictEqual(receipt('opposite held input cannot swivel ' + c.pose + ' through recovery ').data, clone({...compact(value.recovery), observed_locked:value.locked_count, observed_released:value.released_count, observed_opposed:value.opposed_count, observed_late:value.late_count}));
  assert.deepStrictEqual(receipt('pending ' + c.pose + ' releases at its unchanged gameplay clock ').data, clone(compact(value.recovery)));
  if (c.pose === 'cast') assert.equal(receipt('observed live firebolts retain committed diagonal ').data.observed_projectile_samples, value.projectile_observations);
  return {context: c, ...value};
}).map(x => ({...x, started: {physics_tick: x.started.physics_tick, time: x.started.hero.state_time}, recovery: {physics_tick: x.recovery.physics_tick, time: x.recovery.hero.state_time}}));
const basis = report.actionTraces.find(t => t.context.pose === 'cast');
const tests = [];
function reject(name, mutate, expected) {
  const trace = clone(basis);
  mutate(trace);
  let actual = 'ACCEPTED';
  let message = '';
  try { analyze(trace); } catch (error) { actual = error.name; message = error.message; }
  tests.push({name, expected, actual, passed: expected === actual, message});
}
reject('timeout is incomplete', t => { t.status = 'timeout'; }, 'IncompleteObservation');
reject('no action samples is incomplete', t => { t.samples = t.samples.filter(x => x.snapshot.hero.state !== t.context.pose); }, 'IncompleteObservation');
reject('no snapshot at initial minimum is incomplete', t => { for (const s of locked(t)) s.snapshot.hero.state_time = .01; }, 'IncompleteObservation');
reject('test mode in one locked sample fails', t => { locked(t)[0].snapshot.test_mode = true; }, 'ObservedBehaviorFailure');
reject('actor mismatch in one locked sample fails', t => { locked(t)[0].snapshot.hero.character = 'other'; }, 'ObservedBehaviorFailure');
reject('facing corruption in one early locked sample fails', t => { locked(t)[0].snapshot.hero.facing = 'south'; }, 'ObservedBehaviorFailure');
reject('committed aim corruption in one locked sample fails', t => { locked(t)[1].snapshot.hero.action_aim = [0, 1]; }, 'ObservedBehaviorFailure');
reject('one bad pending hit among clean released samples fails', t => { locked(t).find(s => s.snapshot.hero.state_time >= t.context.release).snapshot.hero.pending_hit = 'firebolt'; }, 'ObservedBehaviorFailure');
reject('no actual opposite input is incomplete', t => { for (const s of locked(t)) s.snapshot.hero.movement_input = t.context.aim; }, 'IncompleteObservation');
reject('released samples without old late window are incomplete', t => { t.samples = t.samples.filter(x => !(x.snapshot.hero.state === t.context.pose && x.snapshot.hero.state_left > 0 && x.snapshot.hero.state_time >= t.context.duration - .11)); }, 'IncompleteObservation');
reject('unexpected action end fails', t => { t.samples.at(-1).snapshot.hero.state = 'hurt'; }, 'ObservedBehaviorFailure');
reject('no current cast projectile is incomplete', t => { for (const s of t.samples) s.snapshot.projectiles = []; }, 'IncompleteObservation');
reject('one wrong current projectile among good samples fails', t => {
  const baseline = analyze(t);
  const startTick = baseline.started.physics_tick - baseline.started.hero.state_time * baseline.started.physics_hz;
  const row = t.samples.find(s => s.snapshot.projectiles.some(b => !b.hostile && b.elapsed >= 0 && b.elapsed < .31 && s.snapshot.physics_tick - b.elapsed*s.snapshot.physics_hz > startTick + 1));
  row.snapshot.projectiles.find(b => !b.hostile && b.elapsed >= 0 && b.elapsed < .31 && row.snapshot.physics_tick - b.elapsed*row.snapshot.physics_hz > startTick+1).direction = [0, 1];
}, 'ObservedBehaviorFailure');
const result = {scope: 'Offline exact analyzer replay and mutated snapshot rejection; no browser, engine, action or gameplay state was changed.', replayed_actual_traces: rows.length, corresponding_receipt_data_matches_exact: true, rows, rejection_checks: tests, all_rejections_passed: tests.every(x => x.passed)};
fs.writeFileSync(output + '/ANALYZER-REPLAY.json', JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({actual_traces: rows.length, rejection_checks: tests.length, all_passed: result.all_rejections_passed, summary: rows.map(r => ({id:r.context.id,view:r.context.view,pose:r.context.pose,recovery:r.recovery.time,locked:r.locked_count,late:r.late_count,projectiles:r.projectile_observations}))}, null, 2));
if (!result.all_rejections_passed) process.exitCode = 1;
