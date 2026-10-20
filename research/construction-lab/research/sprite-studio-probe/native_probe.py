#!/usr/bin/env python3
"""Build upstream Rust raster/IK/mesh core without its Tauri application."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repository', type=Path, required=True)
    p.add_argument('--build-dir', type=Path, required=True)
    p.add_argument('--execute', action='store_true')
    args = p.parse_args()
    upstream = args.repository.resolve()
    output = Path(__file__).parent / 'evidence'
    build = args.build_dir.resolve()
    source = build / 'src'
    rig_dir = source / 'rig'
    rig_dir.mkdir(parents=True, exist_ok=True)
    copied = {}
    for name in ['ik.rs', 'skin.rs', 'mesh.rs', 'ik_tests.rs']:
        original = (upstream / 'src-tauri/src/rig' / name).read_bytes()
        (rig_dir / name).write_bytes(original)
        copied[name] = hashlib.sha256(original).hexdigest()
    types = (upstream / 'src-tauri/src/rig/types.rs').read_text()
    # Discard application-only records and MCP reflection; keep all render data fields.
    types = types[:types.index('#[derive(Debug, Clone, Deserialize, schemars::JsonSchema)]\n#[serde(rename_all = "camelCase")]\npub struct RigInput')]
    types = types.replace('use rmcp::schemars;\n', '').replace(', schemars::JsonSchema', '')
    (rig_dir / 'types.rs').write_text(types)
    (rig_dir / 'mod.rs').write_text('''mod types;
mod ik;
mod mesh;
mod skin;
pub use types::{Rig, RigPoint, RigBone};
pub fn render(master: &image::RgbaImage, rig: &Rig) -> Vec<image::RgbaImage> {
    skin::render_frames(master, rig)
}
#[cfg(test)] mod ik_tests;
''')
    (source / 'main.rs').write_text('''mod rig;
fn main() {
    let args: Vec<String> = std::env::args().collect();
    let master = image::open(&args[1]).unwrap().into_rgba8();
    let spec: rig::Rig = serde_json::from_slice(&std::fs::read(&args[2]).unwrap()).unwrap();
    let frames = rig::render(&master, &spec);
    std::fs::create_dir_all(&args[3]).unwrap();
    for (i, frame) in frames.iter().enumerate() {
        frame.save(format!("{}/{:02}.png", args[3], i)).unwrap();
    }
    println!("rendered {} actual native core frames", frames.len());
}
''')
    (build / 'Cargo.toml').write_text('''[package]
name = "sprite-studio-native-probe"
version = "0.1.0"
edition = "2021"
[dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
image = { version = "0.25", default-features = false, features = ["png"] }
rayon = "1.10"
''')
    point = lambda name, x: {'id': name, 'name': name, 'kind': 'joint', 'x': x, 'y': 46, 'confidence': 1, 'source': 'user'}
    bones = [
        {'id': 'upper', 'name': 'upper', 'startPoint': 'shoulder', 'endPoint': 'elbow', 'radius': 9, 'z': 1},
        {'id': 'lower', 'name': 'lower', 'startPoint': 'elbow', 'endPoint': 'wrist', 'radius': 9, 'parent': 'upper', 'z': 2},
    ]
    frames = [
        {'phase': 'rest', 'transforms': []},
        {'phase': 'rigid', 'transforms': [{'bone': 'upper', 'rotate': 35}]},
        {'phase': 'bent', 'transforms': [{'bone': 'upper', 'rotate': 35}, {'bone': 'lower', 'rotate': -70}]},
        {'phase': 'folded', 'transforms': [{'bone': 'upper', 'rotate': -30}, {'bone': 'lower', 'rotate': -120}]},
        {'phase': 'held', 'hold': True},
    ]
    spec = {'id': 'probe', 'workspaceId': 'probe', 'name': 'arm-experiment', 'morphology': 'biped',
            'fps': 60, 'looping': False, 'points': [point('shoulder', 35), point('elbow', 44), point('wrist', 56)],
            'bones': bones, 'frames': frames, 'createdAt': '', 'updatedAt': ''}
    spec_path = output / 'native-rig.json'
    spec_path.write_text(json.dumps(spec, indent=2) + '\n')
    (output / 'native-build-provenance.json').write_text(json.dumps({
        'scope': 'Isolated unchanged Rust IK, mesh and skin modules; Tauri app and quality validator not included.',
        'upstream_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=upstream, text=True).strip(),
        'unchanged_module_sha256': copied,
        'adaptations': ['types.rs truncated after Rig; rmcp schemars import and reflection derives removed.',
                        'Cargo runner and serde input/output harness added; original repo remains unchanged.'],
        'cargo_dependencies': ['serde', 'serde_json', 'image 0.25 (PNG)', 'rayon'],
        'build_directory': str(build),
        'commands': [['cargo', 'test', '-j', '8'], ['cargo', 'run', '-j', '8', '--',
                    str(output / 'master.png'), str(spec_path), str(output / 'native-frames')]],
    }, indent=2) + '\n')
    print(build)
    if args.execute:
        from PIL import Image, ImageDraw
        tests = subprocess.run(['cargo', 'test', '-j', '8', '--quiet'], cwd=build,
                               text=True, capture_output=True, check=True)
        (output / 'native-tests.log').write_text(tests.stdout + tests.stderr)
        commands = ['cargo', 'run', '-j', '8', '--quiet', '--', str(output / 'master.png'), str(spec_path)]
        for threads, destination in [(8, 'native-frames'), (1, 'native-repeat')]:
            env = dict(os.environ, RAYON_NUM_THREADS=str(threads))
            run = subprocess.run(commands + [str(output / destination)], cwd=build,
                                 env=env, text=True, capture_output=True, check=True)
            (output / f'native-run-{threads}.log').write_text(run.stdout + run.stderr)
        master = Image.open(output / 'master.png').convert('RGBA')
        sheet = Image.new('RGB', (480, 114), '#20303e')
        draw = ImageDraw.Draw(sheet)
        rows = []
        images = []
        for i, frame in enumerate(frames):
            image = Image.open(output / 'native-frames' / f'{i:02}.png').convert('RGBA')
            repeated = Image.open(output / 'native-repeat' / f'{i:02}.png').convert('RGBA')
            assert image.tobytes() == repeated.tobytes(), 'thread count changed rendered RGBA'
            images.append(image)
            sheet.paste(image, (i * 96, 0), image)
            draw.text((i * 96 + 4, 98), frame['phase'], fill='white')
            colors = list(image.get_flattened_data())
            rows.append({'frame': i, 'rgba_sha256': hashlib.sha256(image.tobytes()).hexdigest(),
                         'opaque_pixels': sum(c[3] > 0 for c in colors),
                         'source_differing_pixels': sum(a != b for a, b in zip(master.get_flattened_data(), colors)),
                         'repeat_1_vs_8_threads_equal': True})
        sheet.resize((1440, 342), Image.Resampling.NEAREST).save(output / 'native-comparison-3x.png')
        report = {'scope': 'Unchanged upstream Rust skin/IK/mesh modules in an isolated adapted data wrapper; app, agent generation and full quality validator not executed.',
                  'upstream_ik_tests_passed': 2, 'frames': rows,
                  'hold_equals_previous': images[3].tobytes() == images[4].tobytes(),
                  'rest_source_equal': images[0].tobytes() == master.tobytes(),
                  'art_status': 'changes_requested: severe folded arm compressed and visually damaged',
                  'source_binding': json.loads((output / 'native-build-provenance.json').read_text()),
                  'source_png_sha256': hashlib.sha256((output / 'master.png').read_bytes()).hexdigest(),
                  'rig_sha256': hashlib.sha256(spec_path.read_bytes()).hexdigest()}
        (output / 'native-report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'ik_tests': 2, 'rendered': len(rows), 'thread_repeats': len(rows), 'art_status': report['art_status']}))


if __name__ == '__main__':
    main()
