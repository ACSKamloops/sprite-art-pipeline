#!/usr/bin/env node
// Replay unchanged shipped palette-image helper. No provider/network code.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const vm = require('vm');
const assert = require('assert/strict');
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const [asset, root] = process.argv.slice(2);
if (!asset || !root) throw Error('usage: node replay_palette_helper.cjs ORIGINAL_CREATE_JS PREPARED_ROOT');
const bytes = fs.readFileSync(asset);
assert.equal(sha(bytes), '819962c897d4640c126a5efa4b6c5a194819e7eeaf023b242d852a64df74779d');
const source = bytes.toString('utf8');
const pieces = [
  {name: 'srgb', from: 125936, to: 126009, hash: '110f58094f1d594e008bb023037ee8c93c282999999257fe23a5876a6c47368e'},
  {name: 'distance', from: 126010, to: 126061, hash: '64c6a95c46eb5756d6ecffc1281cda48499cdd9061af0948fe905a320db84cff'},
  {name: 'reducer', from: 133187, to: 134661, hash: 'f98a7aa044b03fbd50096ae0c8af0c6d9ea01f6565b75bd8326f1bfb6bd8fa61'}
].map(p => {
  const text = source.slice(p.from, p.to);
  assert.equal(sha(text), p.hash);
  return {...p, text, utf8_range: [Buffer.byteLength(source.slice(0, p.from)), Buffer.byteLength(source.slice(0, p.to))]};
});
const output = path.join(root, 'original-helper');
fs.mkdirSync(output, {recursive: false});
for (const p of pieces) fs.writeFileSync(path.join(output, p.name + '.original.js'), p.text);
function original() {
  return vm.runInNewContext(`let ${pieces[0].text};let ${pieces[1].text};(${pieces[2].text})`, {}, {timeout: 1000});
}
const plan = JSON.parse(fs.readFileSync(path.join(root, 'PLAN.json'), 'utf8'));
const fixtureManifest = JSON.parse(fs.readFileSync(path.join(root, 'FIXTURES.json'), 'utf8'));
const fixtures = new Map(fixtureManifest.fixtures.map(f => [f.name, f]));
const results = [];
for (const request of plan.requests) {
  // This multi-frame histogram adapter is experimental, not shipped multi-frame code.
  const histogram = new Map();
  const perFrame = [];
  for (const name of request.frames) {
    const fixture = fixtures.get(name);
    const rgba = fs.readFileSync(path.join(root, fixture.rgba_file));
    assert.equal(sha(rgba), fixture.rgba_sha256);
    const frameHistogram = new Map();
    for (let i = 0; i < rgba.length; i += 4) {
      if (rgba[i + 3] === 0) continue; // Original palette-import canvas loop skips alpha0.
      const color = rgba[i] << 16 | rgba[i + 1] << 8 | rgba[i + 2];
      histogram.set(color, (histogram.get(color) || 0) + 1);
      frameHistogram.set(color, (frameHistogram.get(color) || 0) + 1);
    }
    const value = original()(frameHistogram, 0);
    perFrame.push({name, palette_rgb: Array.from(value, v => [v >> 16 & 255, v >> 8 & 255, v & 255])});
  }
  assert(histogram.size > 256, 'fixture must enter original UI reduction branch');
  const reduced = original()(histogram, 0);
  assert.equal(JSON.stringify(reduced), JSON.stringify(original()(histogram, 0)), 'fresh VM replay mismatch');
  // The original helper ignores its second argument; do not replace its hardcoded32.
  assert.equal(JSON.stringify(reduced), JSON.stringify(original()(histogram, 4)));
  assert.equal(JSON.stringify(reduced), JSON.stringify(original()(histogram, 32)));
  const rgb = Array.from(reduced, v => [v >> 16 & 255, v >> 8 & 255, v & 255]);
  assert(rgb.length <= 32 && rgb.length >= 2);
  for (const v of reduced) assert(histogram.has(v), 'representative must come from input');
  results.push({variant: request.variant, requested_num_colors: request.num_colors,
    comparison_eligible_same_requested_size: request.num_colors === 32,
    unique_input_colors: histogram.size, histogram_total_pixels: Array.from(histogram.values()).reduce((a, b) => a + b, 0),
    palette_rgb: rgb, palette_count: rgb.length, palette_order_role: 'original helper ascending Oklab lightness; public API documents frequency order',
    original_fresh_context_equal: true, original_second_argument_ignored: true, per_frame_original_results: perFrame});
}
const report = {schema: 1, label: 'supplied diagnostic; original shipped client helper replay; not server recovery',
  original_asset: path.resolve(asset), original_asset_sha256: sha(bytes),
  source_parts: pieces.map(({text, ...p}) => p), node: process.version,
  adapter: 'count each nonzero-alpha RGB in first-seen frame/pixel order into one Map; this joint adapter is not recovered multi-frame client behavior',
  role: 'original single palette-image import, >256 distinct colors, at most32 representatives; no arbitrary num_colors API',
  results};
fs.writeFileSync(path.join(root, 'ORIGINAL-HELPER-REPLAY.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(results.map(r => ({variant: r.variant, palette_count: r.palette_count}))));
