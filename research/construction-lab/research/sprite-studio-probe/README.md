# Recent implementation test: Sprite Studio

Upstream [v0.3.3](https://github.com/JohnKinyanjui/sprite-maker/releases/tag/v0.3.3) was published September 24, 2026. The tested source is `9de73a6136a1a045af2e8769349fbadc17dbef69`, the release target. Its MIT source remains in the separate read-only research checkout; no third-party skill or agent configuration was installed.

This is a **bounded renderer comparison**, not a full application evaluation. We exercised four Python raster/hierarchy poses with four structural rejection checks, then compiled the unchanged upstream Rust IK, mesh and skin modules in an isolated Cargo harness. The harness removes application-only records and MCP schema reflection from the data types; rendering modules are copied byte for byte and their hashes are recorded. Two upstream IK tests pass. Five native frames render identically with one and eight Rayon workers, and a held frame equals its predecessor. Full Tauri UI, AI providers, and the application's quality validator were not run.

The reference is our existing cutout's isolated arm, not original-game artwork. The rest pose preserves every source RGBA pixel. A severe folded pose compresses 360 opaque pixels to **176**, and the arm visibly loses useful form. Both Python and Rust outputs are available at actual pixel resolution and enlarged in `evidence/`. The Python bent arm stays one alpha component, despite poor joint appearance: connected silhouette is insufficient as an artistic gate. The analytic contact counterexample illustrates raster rounding; it is **not** a new GPU/world-motion measurement.

## Repeat

Requires Python with Pillow, Cargo, and the pinned upstream checkout:

```sh
python3 research/sprite-studio-probe/probe.py --repository /home/astra/projects/sprite-maker-research
python3 research/sprite-studio-probe/native_probe.py --repository /home/astra/projects/sprite-maker-research --build-dir /home/astra/artifacts/sprite-studio-native-probe --execute
```

The second command captures Cargo logs, actual PNG readbacks, one/eight-thread comparisons, source bindings and the measured report. Do not treat deterministic equality, passing IK tests or `finalize-degraded` as art approval.

## What we adopt

Keep a stable master, explicit named joints, separate rigid equipment and declared contact phases. Source masks need overlapping or completed hidden anatomy. Restrict unsupported bends and use a continuous authored contour, carefully weighted mesh, or replacement joint cel when the rigid split fails. Bake timing from the motion plan, then review actual frames and playback; preserve localized correction masks and invalidate downstream edits when source art changes. Our new Godot pilot uses authored continuous polygon strips, **not** this upstream skinning algorithm or a claim of automatic anatomical segmentation.
