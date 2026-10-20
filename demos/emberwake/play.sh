#!/usr/bin/env bash
# Local static host for the already exported browser game.
set -euo pipefail
game_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
game_port="${EMBERWAKE_PORT:-8896}"
if [[ ! -s "$game_root/web/index.pck" || ! -s "$game_root/web/index.wasm" ]]; then
  printf 'The Web export is missing. Follow the rebuild commands in %s/README.md\n' "$game_root" >&2
  exit 1
fi
printf 'Open http://localhost:%s/index.html\nKeep this terminal open; Ctrl-C stops this server.\n' "$game_port"
exec python3 -m http.server "$game_port" --bind 127.0.0.1 --directory "$game_root/web"
