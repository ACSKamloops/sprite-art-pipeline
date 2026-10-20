#!/usr/bin/env python3
"""Offline replay of pinned shipped client methods, not private generation code.

Uses an already installed LuaJIT shared library and Node. No installs, network,
credentials, native editor runtime, or source mutation. JSON/renderer/UI stubs
are explicitly symbolic; they do not prove native host codec or raster behavior.
"""
import argparse
import ctypes
import ctypes.util
import hashlib
import json
from pathlib import Path
import subprocess


PINS = {
    'extension-extracted/PixelLab/pixminimax.lua': 'eabce383a55e68344a311c242e7979464318169c6077323903311b650ffd1f52',
    'extension-extracted/PixelLab/dialog-settings.lua': 'ff215847d56ad935f0e73608d2b69e7582f703190557a39350bda0dc6f44489c',
    'extension-extracted/PixelLab/create-json.lua': 'fa23648cca2b31681f97be145328d9ae6f488b0bac8e13fe0fc1575b9944b87d',
    'extension-extracted/PixelLab/place-image.lua': 'ea5db9151320986edc1e8c4246cc00b3d18c126dde372c353f4e405ebe3816ff',
    'extension-extracted/PixelLab/prepare-for-generation.lua': '454952bd080bbe58ec2a87134fa8a4f4e6bb31375e06965bedc09b710f3d61da',
    'website-art-bundles/create-677791a6e206dafa.js': '3938b48d590633a6c1f6549609404c96ca12c81909433f2b915b153d3538e70a',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def lua_replay(sources, harness):
    name = ctypes.util.find_library('luajit-5.1')
    if not name:
        raise RuntimeError('Installed LuaJIT shared library unavailable; no replacement or install attempted')
    lib = ctypes.CDLL(name)
    state_type = ctypes.c_void_p
    lib.luaL_newstate.restype = state_type
    lib.luaL_openlibs.argtypes = [state_type]
    lib.luaL_loadbuffer.argtypes = [state_type, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p]
    lib.lua_pcall.argtypes = [state_type, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    lib.lua_pushlstring.argtypes = [state_type, ctypes.c_char_p, ctypes.c_size_t]
    lib.lua_setfield.argtypes = [state_type, ctypes.c_int, ctypes.c_char_p]
    lib.lua_tolstring.argtypes = [state_type, ctypes.c_int, ctypes.c_void_p]
    lib.lua_tolstring.restype = ctypes.c_char_p
    lib.lua_close.argtypes = [state_type]
    state = lib.luaL_newstate()
    if not state:
        raise RuntimeError('Unable to allocate isolated Lua state')
    try:
        lib.luaL_openlibs(state)
        for key, raw in sources.items():
            lib.lua_pushlstring(state, raw, len(raw))
            lib.lua_setfield(state, -10002, key.encode())  # Lua 5.1 GLOBALSINDEX.
        if lib.luaL_loadbuffer(state, harness, len(harness), b'@prompt_frame_replay.lua') or lib.lua_pcall(state, 0, 1, 0):
            raise RuntimeError(lib.lua_tolstring(state, -1, None).decode('utf8', errors='replace'))
        return {**json.loads(lib.lua_tolstring(state, -1, None)), 'library_soname': name,
            'boundary': 'Actual original Lua methods; Image, app, JSON codec and timeline APIs are symbolic local stubs, not native editor execution'}
    finally:
        lib.lua_close(state)


def replay(research):
    raw_sources = {}
    for relative, expected in PINS.items():
        raw = (research/relative).read_bytes()
        if sha(raw) != expected:
            raise ValueError('Original source identity changed: '+relative)
        raw_sources[relative] = raw
    root = Path(__file__).parent/'recovery_depth'
    lua = lua_replay({
        'SOURCE_SAFE_STRING': b''.join(raw_sources['extension-extracted/PixelLab/dialog-settings.lua'].splitlines(keepends=True)[7:18]),
        'SOURCE_PIXMINIMAX': raw_sources['extension-extracted/PixelLab/pixminimax.lua'],
        'SOURCE_CREATE_JSON': raw_sources['extension-extracted/PixelLab/create-json.lua'],
        'SOURCE_PLACE_IMAGE': raw_sources['extension-extracted/PixelLab/place-image.lua'],
        'SOURCE_PREPARE': raw_sources['extension-extracted/PixelLab/prepare-for-generation.lua'],
    }, (root/'prompt_frame_replay.lua').read_bytes())
    original_web = raw_sources['website-art-bundles/create-677791a6e206dafa.js'][13133:14631]
    if sha(original_web) != '577841f27adf5f03ff8acdac3667dccea188eb7afd14f1a9affa7e79d3d6237a':
        raise ValueError('Original web method range identity changed')
    node = subprocess.run(['node', str(root/'prompt_frame_web_replay.cjs')],
        input=json.dumps({'source': original_web.decode()}), text=True, capture_output=True, timeout=20)
    if node.returncode:
        raise RuntimeError(node.stderr)
    web = json.loads(node.stdout)
    return {'version': 1, 'passed': lua['passed'] and web['passed'], 'lua': lua, 'web': web,
        'sources': [{'path': relative, 'sha256': value} for relative, value in PINS.items()],
        'harnesses': [{'file': str(p.relative_to(Path(__file__).parents[1])), 'sha256': sha(p.read_bytes())}
            for p in [Path(__file__), root/'prompt_frame_replay.lua', root/'prompt_frame_web_replay.cjs']],
        'model_or_provider_calls': 0, 'credentials_loaded': False, 'native_editor_executed': False,
        'private_prompt_or_frame_sampling_algorithm_recovered': False,
        'scope': 'Deterministic isolated replay of selected original client methods only; no artwork or universal client acceptance'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--research-root', type=Path, default=Path('/home/astra/projects/pixellab-local-test-20261011'))
    args = parser.parse_args()
    print(json.dumps(replay(args.research_root.resolve()), indent=2))


if __name__ == '__main__':
    main()
