// POST-HOC INFERRED VARIATION: deliberately changes one original distance helper.
// Never label these results recovered original client/server behavior.
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert/strict');
const sha = b => require('crypto').createHash('sha256').update(b).digest('hex');
const [root, output] = process.argv.slice(2);
const parts = ['srgb', 'distance', 'reducer'].map(n => fs.readFileSync(path.join(root, 'original-helper', n + '.original.js'), 'utf8'));
assert.equal(sha(parts[0]), '110f58094f1d594e008bb023037ee8c93c282999999257fe23a5876a6c47368e');
assert.equal(sha(parts[1]), '64c6a95c46eb5756d6ecffc1281cda48499cdd9061af0948fe905a320db84cff');
assert.equal(sha(parts[2]), 'f98a7aa044b03fbd50096ae0c8af0c6d9ea01f6565b75bd8326f1bfb6bd8fa61');
const distance = parts[1].replace('Math.hypot(e[0]-t[0],', 'Math.hypot(.5*(e[0]-t[0]),');
assert.notEqual(distance, parts[1]);
const reduce = vm.runInNewContext(`let ${parts[0]};let ${distance};(${parts[2]})`, {});
const histogram = new Map();
for (const name of ['A', 'B']) {
  const raw = fs.readFileSync(path.join(root, 'inputs', name + '.rgba'));
  for (let i = 0; i < raw.length; i += 4) {
    const rgb = raw[i] << 16 | raw[i+1] << 8 | raw[i+2];
    histogram.set(rgb, (histogram.get(rgb) || 0) + 1);
  }
}
const colors = Array.from(reduce(histogram, 0), c => [c >> 16 & 255, c >> 8 & 255, c & 255]);
fs.writeFileSync(output, JSON.stringify({label: 'post-hoc inferred variation; altered source, not recovered algorithm',
  source_distance_sha256: sha(parts[1]), altered_distance_sha256: sha(distance),
  altered_distance: distance, changes: 'Only distance helper L difference multiplied by.5; initialization, iterations and representative selection unchanged',
  variant: 'joint-ab-32', palette_rgb: colors}, null, 2) + '\n', {flag: 'wx'});
