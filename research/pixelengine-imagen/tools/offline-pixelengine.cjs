#!/usr/bin/env node
'use strict';

// Optional adapter for the retained, hash-bound client artifact. No downloads.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');

const EXPECTED = Object.freeze({
  wrapper: 'd825c148b2dec6067f8d33754d40151582b3ece33ac27d8ec3dbeaaf8abae99b',
  wasm: '29a31b9f9c5fc4ab28b5830d2a73a7182601f40c483ab350059b313ba6efe14a',
});
const HELP = `Usage: node offline-pixelengine.cjs COMMAND [options]
Commands: classify, process-image, process-frames
Required: --wrapper FILE --wasm FILE --input PNG --output-dir NEW_DIRECTORY
Processing requires exactly one: --colors INTEGER (1..256)
                                --palette '["#000000","#ffffff"]'
For process-frames, repeat --input in frame order; optional --timing-sidecar FILE
copies opaque bytes unchanged. The output parent directory must already exist.
No generation, timing interpretation, automatic classification routing or fetch.
`;

const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const binding = (file, bytes) => ({ path: path.resolve(file), bytes: bytes.length, sha256: sha256(bytes) });
const fail = message => { throw new Error(message); };

function parseArgs(argv) {
  if (argv.length === 1 && ['--help', '-h'].includes(argv[0])) return null;
  const [command, ...args] = argv;
  if (!['classify', 'process-image', 'process-frames'].includes(command)) fail('Expected classify, process-image or process-frames; use --help');
  const values = { command, input: [] };
  const flags = ['wrapper', 'wasm', 'input', 'output-dir', 'colors', 'palette', 'timing-sidecar'];
  for (let i = 0; i < args.length; i += 2) {
    const name = args[i].slice(2), value = args[i + 1];
    if (!args[i].startsWith('--') || !flags.includes(name)) fail(`Unknown argument: ${args[i]}`);
    if (!value || value.startsWith('--')) fail(`Missing value for --${name}`);
    if (name === 'input') values.input.push(value);
    else {
      if (Object.hasOwn(values, name)) fail(`Duplicate --${name}`);
      values[name] = value;
    }
  }
  for (const name of ['wrapper', 'wasm', 'output-dir']) if (!values[name]) fail(`Required --${name}`);
  if (!values.input.length) fail('At least one --input PNG is required');
  if (command !== 'process-frames' && values.input.length !== 1) fail(`${command} requires exactly one --input`);
  if (command !== 'process-frames' && values['timing-sidecar']) fail('--timing-sidecar is only supported by process-frames');
  const hasColors = Object.hasOwn(values, 'colors'), hasPalette = Object.hasOwn(values, 'palette');
  values.options = {};
  if (command === 'classify') {
    if (hasColors || hasPalette) fail('classify does not accept --colors or --palette');
  } else {
    if (hasColors === hasPalette) fail('Processing requires exactly one of --colors or --palette');
    if (hasColors) {
      if (!/^[1-9][0-9]*$/.test(values.colors) || Number(values.colors) > 256) fail('--colors must be an integer from 1 to 256');
      values.options.colors = Number(values.colors);
    } else {
      let palette;
      try { palette = JSON.parse(values.palette); } catch { fail('--palette must be a JSON array of RGB hex strings'); }
      if (!Array.isArray(palette) || !palette.length || palette.length > 256 ||
          !palette.every(color => typeof color === 'string' && /^#?[0-9a-fA-F]{6}$/.test(color))) {
        fail('--palette must contain 1..256 six-digit RGB hex strings');
      }
      values.options.palette = palette;
    }
  }
  return values;
}

function readArtifact(file, name) {
  const bytes = fs.readFileSync(file), record = binding(file, bytes);
  if (record.sha256 !== EXPECTED[name]) fail(`${name} SHA-256 mismatch; refusing to execute`);
  return { bytes, record };
}

function pngDimensions(bytes) {
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  if (bytes.length < 33 || !bytes.subarray(0, 8).equals(signature) ||
      bytes.readUInt32BE(8) !== 13 || bytes.toString('ascii', 12, 16) !== 'IHDR') fail('Input must be an encoded PNG with an IHDR header');
  const width = bytes.readUInt32BE(16), height = bytes.readUInt32BE(20);
  if (!width || !height) fail('PNG dimensions must be positive');
  // A sequence entry must be one image, never an APNG whose clock we would lose.
  let offset = 8;
  while (offset + 12 <= bytes.length) {
    const size = bytes.readUInt32BE(offset), type = bytes.toString('ascii', offset + 4, offset + 8);
    if (offset + 12 + size > bytes.length) fail('Truncated PNG chunk');
    if (type === 'acTL') fail('Animated PNG is not supported; provide independently encoded PNG frames');
    offset += size + 12;
    if (type === 'IEND') break;
  }
  return { width, height };
}

async function loadRuntime(wrapper, wasm, logs) {
  const chunks = [];
  const sandbox = {
    TURBOPACK: chunks, TextEncoder, TextDecoder, Uint8Array, DataView,
    WebAssembly, FinalizationRegistry, Response, Request, URL,
    console: Object.fromEntries(['warn', 'error'].map(level => [level, (...args) => logs.push({ level, message: args.join(' ') })])),
    fetch: () => { throw new Error('Network disabled by offline PixelEngine adapter'); },
  };
  vm.runInNewContext(wrapper.bytes.toString('utf8'), sandbox, { filename: wrapper.record.path, timeout: 5000 });
  const factories = chunks.flatMap(chunk => {
    const index = chunk.indexOf(21436);
    return index >= 0 && typeof chunk[index + 1] === 'function' ? [chunk[index + 1]] : [];
  });
  if (factories.length !== 1) fail('Could not uniquely select genuine wrapper module 21436');
  const api = {};
  factories[0]({ s: rows => {
    for (let i = 0; i < rows.length; i += 3) {
      if (rows[i + 1] !== 0) fail('Unexpected genuine-wrapper export shape');
      api[rows[i]] = rows[i + 2];
    }
  } });
  // Supplying bytes deliberately takes the wrapper's local instantiation path.
  await api.default(wasm.bytes);
  return api;
}

function processOptions(api, values) {
  const options = new api.ImageProcessOptions();
  if (values.colors !== undefined) options.colors = values.colors;
  if (values.palette !== undefined) options.palette = JSON.stringify(values.palette);
  // process_image/process_frames consume this object; do not free/reuse it.
  return options;
}

async function run(args) {
  // Verify both byte buffers before running any third-party JavaScript or WASM.
  const wrapper = readArtifact(args.wrapper, 'wrapper'), wasm = readArtifact(args.wasm, 'wasm');
  const inputs = args.input.map(file => {
    const bytes = fs.readFileSync(file);
    return { bytes, record: { ...binding(file, bytes), ...pngDimensions(bytes) } };
  });
  if (args.command === 'process-frames' && inputs.some(input =>
    input.record.width !== inputs[0].record.width || input.record.height !== inputs[0].record.height)) {
    fail('Mixed frame dimensions are rejected; register the sequence on one fixed canvas first');
  }
  const timing = args['timing-sidecar'] ? fs.readFileSync(args['timing-sidecar']) : null;
  const outputDir = path.resolve(args['output-dir']);
  // mkdir without recursive/overwrite refuses any existing path, even if empty.
  fs.mkdirSync(outputDir);
  const receipt = {
    schema: 'offline-pixelengine/v1', status: 'running', command: args.command,
    artifact_boundary: 'Retained PixelEngine client wrapper module 21436 and pinned WASM; no hosted equivalence claim',
    adapter: binding(__filename, fs.readFileSync(__filename)),
    runtime: { node: process.version, platform: process.platform, arch: process.arch, network: 'fetch throws; no generation/API/account calls' },
    wrapper: wrapper.record, wasm: wasm.record, inputs: inputs.map(input => input.record),
    requested_options: args.options, outputs: [], logs: [],
  };
  const save = (name, bytes, extra = {}) => {
    const file = path.join(outputDir, name);
    fs.writeFileSync(file, bytes, { flag: 'wx' });
    const record = { file: name, bytes: bytes.length, sha256: sha256(bytes), ...extra };
    receipt.outputs.push(record);
    return record;
  };
  try {
    if (timing !== null) {
      receipt.timing_sidecar = {
        input: binding(args['timing-sidecar'], timing),
        output: save('timing.sidecar', timing),
        interpretation: 'Opaque unchanged bytes; no parsing, clock validation or retiming',
      };
    }
    const api = await loadRuntime(wrapper, wasm, receipt.logs);
    if (args.command === 'classify') {
      const exactJson = api.classify_image(new Uint8Array(inputs[0].bytes));
      receipt.classification = JSON.parse(exactJson);
      save('classification.json', Buffer.from(exactJson, 'utf8'));
    } else {
      const options = processOptions(api, args.options);
      const result = args.command === 'process-image'
        ? api.process_image(new Uint8Array(inputs[0].bytes), options)
        : api.process_frames(inputs.map(input => new Uint8Array(input.bytes)), options);
      try {
        const exactJson = result.metadata;
        receipt.metadata = JSON.parse(exactJson);
        save('metadata.json', Buffer.from(exactJson, 'utf8'));
        const count = args.command === 'process-image' ? 1 : result.frame_count;
        if (count !== inputs.length) fail('Runtime output count differs from input count');
        for (let i = 0; i < count; i++) {
          const bytes = Buffer.from(args.command === 'process-image' ? result.image_data : result.get_frame(i));
          save(args.command === 'process-image' ? 'image.png' : `frame-${String(i).padStart(6, '0')}.png`, bytes,
            { input_index: i, ...pngDimensions(bytes) });
        }
      } finally { result.free(); }
    }
    receipt.status = 'ok';
  } catch (error) {
    receipt.status = 'error';
    receipt.error = error.message || String(error);
    throw error;
  } finally {
    fs.writeFileSync(path.join(outputDir, 'receipt.json'), JSON.stringify(receipt, null, 2) + '\n', { flag: 'wx' });
  }
  return { status: receipt.status, receipt: path.join(outputDir, 'receipt.json'), outputs: receipt.outputs };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args) { process.stdout.write(HELP); return; }
  process.stdout.write(JSON.stringify(await run(args), null, 2) + '\n');
}

if (require.main === module) main().catch(error => {
  process.stderr.write(JSON.stringify({ status: 'error', error: error.message || String(error) }) + '\n');
  process.exitCode = 1;
});
