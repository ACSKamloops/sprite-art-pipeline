#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
site=/home/astra/projects/som-sprite-lab-site/native-godot
renderer=/home/astra/projects/som-native-effect-renderer
mkdir -p .godot evidence scripts
cp "$site/scripts/native_obj_player.gd" scripts/
cp "$site/scripts/indexed_object.gdshader" scripts/
cp "$site/capture-index.json" .
ln -sfn "$site/routes" routes
ln -sfn "$site/assets" assets
ln -sfn "$site/.godot/imported" .godot/imported
ln -sfn "$renderer/evidence/expected" evidence/expected
python3 scripts/scalar_samples.py > evidence/scalar.log
xvfb-run -a godot --path . --rendering-method gl_compatibility --audio-driver Dummy --script scripts/sample_render.gd > evidence/run.log 2>&1
python3 finalize_bridge.py
