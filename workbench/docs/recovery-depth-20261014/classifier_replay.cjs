#!/usr/bin/env node
// Diagnostic fixtures only. Classifier and worker source are executed unchanged.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');
const acorn = require('acorn');
const assert = require('assert/strict');
const root = process.argv[2];
const output = process.argv[3];
if (!root || !output) throw Error('usage: node classifier_replay.cjs ASSETS_DIR NEW_OUTPUT_DIR');
fs.mkdirSync(output, {recursive: false});
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
const sources = [
  ['fd910d1fc77a-6428-00f1c1ac0ad70f79.js', 66428, '077cbc8f10724502107814a7a206a1dc24211a1125b7e6e301aadd941b3f4a64'],
  ['8adb1b509159-5259.712f0977c9cb2d1d.js', 65259, '3f3e971002fd609ff75739b85cfd1ce71706ac553911e9a2b1c1084834024628']
].map(([name, id, expected]) => {
  const bytes = fs.readFileSync(path.join(root, name));
  assert.equal(sha(bytes), expected, 'source hash drift');
  const source = bytes.toString('utf8');
  let factory;
  function walk(node) {
    if (node.type === 'Property' && String(node.key.value) === String(id)
        && node.value.type === 'FunctionExpression') factory = node.value;
    for (const value of Object.values(node)) {
      if (Array.isArray(value)) value.forEach(x => x && x.type && walk(x));
      else if (value && value.type) walk(value);
    }
  }
  walk(acorn.parse(source, {ecmaVersion: 'latest'}));
  assert(factory, `missing original factory ${id}`);
  const text = source.slice(factory.start, factory.end);
  fs.writeFileSync(path.join(output, `${id}.factory.js`), text);
  return {name, id, source, text, sha256: sha(bytes),
    factory_sha256: sha(text), utf16_range: [factory.start, factory.end],
    utf8_range: [Buffer.byteLength(source.slice(0, factory.start)),
      Buffer.byteLength(source.slice(0, factory.end))]};
});
function direct() {
  const exports = {};
  const requireStub = id => {throw Error(`unexpected import ${id}`);};
  requireStub.d = (target, definitions) => {
    for (const [key, getter] of Object.entries(definitions))
      Object.defineProperty(target, key, {enumerable: true, get: getter});
  };
  const factory = vm.runInNewContext(`(${sources[0].text})`, {}, {timeout: 1000});
  factory({exports}, exports, requireStub);
  assert.equal(typeof exports.x, 'function');
  return exports.x;
}
async function worker() {
  const messages = [];
  const context = vm.createContext({self: {postMessage: value => messages.push(value)}});
  // A local importScripts host resolves exactly the original linked dependency.
  context.importScripts = url => {
    assert.equal(url, '/_next/static/chunks/6428-00f1c1ac0ad70f79.js');
    vm.runInContext(sources[0].source, context, {timeout: 1000});
  };
  vm.runInContext(sources[1].source, context, {timeout: 1000});
  await context._N_E;
  assert.equal(typeof context.self.onmessage, 'function');
  return image => {
    context.self.onmessage({data: {id: messages.length, width: image.width,
      height: image.height, buffer: image.data.buffer.slice(0)}});
    return messages.at(-1).result;
  };
}
function fixture(name, width, height, pixel) {
  const data = new Uint8ClampedArray(width * height * 4);
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++)
    data.set(pixel(x, y), 4 * (y * width + x));
  fs.writeFileSync(path.join(output, name + '.rgba'), data);
  return {name, width, height, data};
}
const palette = [[18, 26, 40, 255], [211, 83, 53, 255], [229, 193, 98, 255], [63, 143, 118, 255]];
const pixel = (x, y) => palette[(x * 7 + y * 11 + ((x * y) % 3)) % 4];
const fixtures = [
  fixture('flat-blank', 64, 64, () => [0, 0, 0, 255]),
  fixture('transparent-blank', 64, 64, () => [0, 0, 0, 0]),
  fixture('hard-pixel-grid', 64, 64, pixel),
  fixture('soft-gradient', 128, 128, (x, y) => [2 * x, 2 * y, x + y, 255]),
  fixture('upscaled-pixel-image', 128, 128, (x, y) => pixel(Math.floor(x / 4), Math.floor(y / 4)))
];
(async () => {
  const classify = direct();
  const repeat = direct();
  const classifyWorker = await worker();
  const rows = fixtures.map(image => {
    const before = sha(image.data);
    const result = classify(image);
    assert.equal(sha(image.data), before, 'input mutation');
    const repeated = repeat(image);
    const throughWorker = classifyWorker(image);
    // VM objects have different prototypes; compare their serialized public value.
    assert.equal(JSON.stringify(result), JSON.stringify(repeated), 'fresh VM mismatch');
    assert.equal(JSON.stringify(result), JSON.stringify(throughWorker), 'original worker mismatch');
    assert.equal(JSON.stringify(result), JSON.stringify(image.name === 'upscaled-pixel-image'
      ? {kind: 'upscaled', scale: [4, 4]} : null), 'pinned diagnostic output drift');
    assert.equal(sha(image.data), before, 'worker input mutation');
    return {name: image.name, width: image.width, height: image.height,
      rgba_sha256: before, result, repeat_equal: true, original_worker_equal: true,
      input_unchanged: true};
  });
  const report = {schema: 1, label: 'supplied diagnostic; no generated art',
    captured_at: new Date().toISOString(), node: process.version,
    acorn_version: acorn.version, no_http: true,
    oracle: 'unchanged original factory 66428 plus unchanged full worker 5259',
    host_stubs: ['webpack exports.d for direct factory', 'local importScripts exact linked chunk', 'self.postMessage capture'],
    sources: sources.map(({name, id, sha256, factory_sha256, utf16_range, utf8_range}) =>
      ({name, id, sha256, factory_sha256, utf16_range, utf8_range})), fixtures: rows};
  fs.writeFileSync(path.join(output, 'CLASSIFIER-REPLAY.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(rows.map(({name, result}) => ({name, result}))));
})().catch(error => {console.error(error); process.exitCode = 1;});
