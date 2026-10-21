#!/usr/bin/env node
'use strict';

// Explicit smoke/guard test. Actual external artifacts are mandatory; no mock.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const zlib = require('node:zlib');
const { spawnSync } = require('node:child_process');

const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
function crc32(bytes) {
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc ^= byte;
    for (let i = 0; i < 8; i++) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
  }
  return (crc ^ 0xffffffff) >>> 0;
}
function chunk(type, bytes) {
  const out = Buffer.alloc(bytes.length + 12);
  out.writeUInt32BE(bytes.length); out.write(type, 4); bytes.copy(out, 8);
  out.writeUInt32BE(crc32(out.subarray(4, -4)), out.length - 4);
  return out;
}
function png(width, height, pixel) {
  const header = Buffer.alloc(13), rows = Buffer.alloc(height * (1 + width * 4));
  header.writeUInt32BE(width); header.writeUInt32BE(height, 4); header[8] = 8; header[9] = 6;
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    Buffer.from(pixel(x, y)).copy(rows, y * (1 + width * 4) + 1 + x * 4);
  }
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
    chunk('IHDR', header), chunk('IDAT', zlib.deflateSync(rows)), chunk('IEND', Buffer.alloc(0))]);
}

function main() {
  const argv = process.argv.slice(2), args = {};
  for (let i = 0; i < argv.length; i += 2) {
    assert(['--wrapper', '--wasm', '--artifacts-dir'].includes(argv[i]) && argv[i + 1], 'Expected --wrapper FILE --wasm FILE --artifacts-dir NEW_DIRECTORY');
    assert(!args[argv[i]], 'Duplicate test option');
    args[argv[i]] = path.resolve(argv[i + 1]);
  }
  for (const flag of ['--wrapper', '--wasm', '--artifacts-dir']) assert(args[flag], `Required ${flag}`);
  const artifacts = args['--artifacts-dir'];
  fs.mkdirSync(artifacts);
  const fixture = (name, bytes) => {
    const file = path.join(artifacts, name); fs.writeFileSync(file, bytes, { flag: 'wx' }); return file;
  };
  const gradient = fixture('gradient16.png', png(16, 16, (x, y) => [x * 17, y * 17, (x + y) * 8, 255]));
  const reverse = fixture('reverse16.png', png(16, 16, (x, y) => [(15 - x) * 17, y * 17, (15 - x + y) * 8, 255]));
  const small = fixture('small8.png', png(8, 8, () => [255, 0, 0, 255]));
  const transparent = fixture('transparent8.png', png(8, 8, () => [0, 0, 0, 0]));
  const timing = fixture('opaque.timing', Buffer.from([0, 255, 32, 123, 10, 13, 0]));
  const protectedFiles = [gradient, reverse, small, transparent, timing, args['--wrapper'], args['--wasm']];
  const before = protectedFiles.map(file => hash(fs.readFileSync(file)));
  const cli = path.join(__dirname, 'offline-pixelengine.cjs');
  const common = ['--wrapper', args['--wrapper'], '--wasm', args['--wasm']];
  let passed = 0;
  function invoke(name, command, extra, expectedError, overrides = []) {
    const output = path.join(artifacts, name);
    const result = spawnSync(process.execPath, [cli, command, ...common, '--output-dir', output, ...extra, ...overrides], { encoding: 'utf8', timeout: 20000 });
    assert.ifError(result.error);
    assert.equal(result.status, expectedError ? 1 : 0, result.stderr);
    if (expectedError) {
      assert.match(result.stderr, expectedError);
      if (name !== 'transparent-error') assert(!fs.existsSync(output), 'Validation must precede output directory creation');
      passed++;
      return output;
    }
    const receipt = JSON.parse(fs.readFileSync(path.join(output, 'receipt.json')));
    assert.equal(receipt.status, 'ok');
    for (const record of receipt.outputs) {
      const bytes = fs.readFileSync(path.join(output, record.file));
      assert.equal(bytes.length, record.bytes); assert.equal(hash(bytes), record.sha256);
    }
    if (receipt.metadata) assert.deepEqual(JSON.parse(fs.readFileSync(path.join(output, 'metadata.json'))), receipt.metadata);
    passed++;
    return { receipt, output };
  }
  const classification = invoke('classify', 'classify', ['--input', gradient]);
  assert.equal(classification.receipt.classification.classification, 'real_pixel_art');
  assert.equal(classification.receipt.classification.width, 16);
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(classification.output, 'classification.json'))), classification.receipt.classification);
  const image = invoke('image', 'process-image', ['--input', gradient, '--colors', '2']);
  assert.deepEqual(image.receipt.metadata.output_size, [13, 13]);
  // Exact retained procedural gradient/colors=2 result from the genuine harness.
  assert.equal(hash(fs.readFileSync(path.join(image.output, 'image.png'))), 'b1f9411d2b11b460b3569043d0f14eb7e257270e341fb8e0d37b3e7b9a3feb4d');
  const frames = invoke('frames', 'process-frames', ['--input', gradient, '--input', reverse,
    '--palette', '["#000000","#ffffff"]', '--timing-sidecar', timing]);
  assert.equal(frames.receipt.metadata.frame_count, 2);
  assert.equal(frames.receipt.outputs.filter(record => record.file.endsWith('.png')).length, 2);
  assert.deepEqual(frames.receipt.inputs.map(record => record.path), [gradient, reverse]);
  assert.deepEqual(fs.readFileSync(path.join(frames.output, 'timing.sidecar')), fs.readFileSync(timing));
  assert.equal(frames.receipt.timing_sidecar.input.sha256, frames.receipt.timing_sidecar.output.sha256);
  invoke('mixed', 'process-frames', ['--input', gradient, '--input', small, '--colors', '2'], /Mixed frame dimensions/);
  invoke('empty-palette', 'process-image', ['--input', gradient, '--palette', '[]'], /six-digit RGB hex/);
  invoke('zero-colors', 'process-image', ['--input', gradient, '--colors', '0'], /integer from 1 to 256/);
  invoke('missing-options', 'process-image', ['--input', gradient], /exactly one of/);
  invoke('both-options', 'process-image', ['--input', gradient, '--colors', '2', '--palette', '["ffffff"]'], /exactly one of/);
  const corrupt = fixture('not-the-wrapper.js', Buffer.from('throw new Error("must never execute");'));
  const wrongWrapper = common.slice(); wrongWrapper[1] = corrupt;
  common.splice(0, common.length, ...wrongWrapper);
  invoke('wrong-wrapper', 'classify', ['--input', gradient], /wrapper SHA-256 mismatch/);
  common[1] = args['--wrapper']; common[3] = corrupt;
  invoke('wrong-wasm', 'classify', ['--input', gradient], /wasm SHA-256 mismatch/);
  common[3] = args['--wasm'];
  const errorDir = invoke('transparent-error', 'process-image', ['--input', transparent, '--colors', '2'], /no opaque pixels/);
  assert.equal(JSON.parse(fs.readFileSync(path.join(errorDir, 'receipt.json'))).status, 'error');
  const existing = spawnSync(process.execPath, [cli, 'classify', ...common, '--input', gradient, '--output-dir', image.output], { encoding: 'utf8' });
  assert.equal(existing.status, 1); assert.match(existing.stderr, /EEXIST/); passed++;
  protectedFiles.forEach((file, i) => assert.equal(hash(fs.readFileSync(file)), before[i], `Source changed: ${file}`));
  const report = { status: 'ok', cases: passed, node: process.version, artifacts,
    scope: 'Actual pinned module smoke/replay plus validation guards; no art-quality or hosted-parity acceptance',
    protected_sources: protectedFiles.map((file, i) => ({ path: file, sha256: before[i] })) };
  fs.writeFileSync(path.join(artifacts, 'TEST-RESULTS.json'), JSON.stringify(report, null, 2) + '\n', { flag: 'wx' });
  process.stdout.write(JSON.stringify(report, null, 2) + '\n');
}

try { main(); } catch (error) { process.stderr.write(`${error.stack}\n`); process.exitCode = 1; }
