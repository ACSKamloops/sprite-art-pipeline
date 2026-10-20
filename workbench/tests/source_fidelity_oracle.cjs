// Test oracle: register factories by executing complete retained original chunks.
// Deliberately independent of the production slice loader and its manifest.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
process.on('uncaughtException', error => {process.stderr.write(error.message + '\n'); process.exitCode = 1;});
const originals = {
  'create-vfx-be26fa3e471fd274.js': '11a1ee402e10ddec3ebb1d558a3e699d7b06a605846b4ddc36f346c9aa7b9065',
  '4354-3a62375cb4c03823.js': 'cc7e87ddeb584f550ab863bc10792addab01469be1143ede0cded67a096284de',
  '7423-93e5d1cb073f2b5e.js': '86bc86bf3636523d279fcd03ce1d4e9368c52cd407f894699a6623617b313956',
  '3778-ef7c5cd0341f4223.js': '47c12e2b6e6e0e3f127b993260c72c720454e2624129e95d8632b398eeede609',
};
const factories = new Map(), cache = new Map(), executed = [];
const chunks = {push(chunk) {
  for (const [id, factory] of Object.entries(chunk[1])) {
    if (factories.has(Number(id))) throw Error('Duplicate original factory ' + id);
    factories.set(Number(id), factory);
  }
  // The page-bootstrap callback in chunk[2] is intentionally never invoked.
}};
const context = vm.createContext({self: {webpackChunk_N_E: chunks}, TextEncoder,
  TextDecoder, Blob});
for (const [name, hash] of Object.entries(originals)) {
  const bytes = fs.readFileSync(path.join(process.argv[2], 'website-art-bundles', name));
  if (crypto.createHash('sha256').update(bytes).digest('hex') !== hash)
    throw Error('Original bundle identity changed: ' + name);
  new vm.Script(bytes.toString('utf8'), {filename: name}).runInContext(context, {timeout: 10000});
}
function load(id) {
  if (cache.has(id)) return cache.get(id).exports;
  const factory = factories.get(id);
  if (!factory) throw Error('Unavailable original factory ' + id);
  const module = {exports: {}};
  cache.set(id, module); executed.push(id);
  factory(module, module.exports, load);
  return module.exports;
}
load.d = (target, definitions) => {
  for (const [name, get] of Object.entries(definitions))
    if (!Object.hasOwn(target, name)) Object.defineProperty(target, name, {enumerable: true, get});
};
load.r = target => {Object.defineProperty(target, '__esModule', {value: true});
  Object.defineProperty(target, Symbol.toStringTag, {value: 'Module'});};
load.o = (target, key) => Object.hasOwn(target, key);
load.g = context;
function raster(value) {
  if (value == null) return null;
  const bytes = Buffer.from(value.rgba_base64, 'base64');
  if (bytes.length !== value.width * value.height * 4) throw Error('Invalid oracle raster');
  return {width: value.width, height: value.height, data: new Uint8ClampedArray(bytes)};
}
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
if (input.action === 'normalize' || input.action === 'controls') {
  const api = load(47381);
  const normalized = api.W$(input.recipe);
  const result = {normalized, executed};
  if (input.action === 'controls') result.applied = api.uY(normalized);
  process.stdout.write(JSON.stringify(result));
  process.exit(0);
}
const output = load(39852).sY(input.recipe, raster(input.subject),
  Object.fromEntries(Object.entries(input.images || {}).map(([key, value]) => [key, raster(value)])));
const streams = {};
for (const name of ['frames', 'back', 'front'])
  streams[name] = output[name].map(frame => Buffer.from(frame.buffer, frame.byteOffset, frame.byteLength).toString('base64'));
process.stdout.write(JSON.stringify({recipe: output.recipe, subjectBox: output.subjectBox, streams, executed}));
