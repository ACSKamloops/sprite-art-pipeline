#!/usr/bin/env bash
# Installs only this checkout's Python environment. Node/Godot are diagnosed separately.
set -euo pipefail
task_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
command -v uv >/dev/null || { echo 'Install uv before running this setup.' >&2; exit 2; }
if [[ -L "$task_root/.venv" ]]; then
  echo 'Refusing a symlinked .venv; preserve it and choose a separate checkout.' >&2
  exit 2
fi
if [[ ! -d "$task_root/.venv" ]]; then
  uv venv --python 3.14 "$task_root/.venv"
fi
uv pip install --python "$task_root/.venv/bin/python" --require-hashes -r "$task_root/requirements-local.lock"
uv pip install --python "$task_root/.venv/bin/python" --no-deps --no-build-isolation -e "$task_root"
uv pip check --python "$task_root/.venv/bin/python"
"$task_root/.venv/bin/python" -m sprite_workbench lab doctor
