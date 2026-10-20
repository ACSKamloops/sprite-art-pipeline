#!/usr/bin/env bash
set -euo pipefail
task_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
command -v uv >/dev/null || { echo 'Install uv, then rerun this script.' >&2; exit 2; }
[[ ! -L "$task_root/.venv" ]] || { echo 'Refusing a symlinked .venv.' >&2; exit 2; }
if [[ ! -d "$task_root/.venv" ]]; then
  uv venv --python 3.14 "$task_root/.venv"
fi
uv pip install --python "$task_root/.venv/bin/python" --require-hashes -r "$task_root/workbench/requirements-local.lock"
uv pip install --python "$task_root/.venv/bin/python" --no-deps --no-build-isolation -e "$task_root/workbench"
uv pip check --python "$task_root/.venv/bin/python"
echo 'Local tooling installed. No provider jobs or servers were started.'

