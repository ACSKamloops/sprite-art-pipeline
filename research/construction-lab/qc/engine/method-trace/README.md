# Passive native frame-control watchpoints

The original dirty `/home/astra/projects/som-runtime-snes9x` was never reset or edited. Its status, binary working/index patches, index contents and modified `cpuexec.cpp`, `libretro/libretro.cpp`, `libretro/link.T` were preserved privately in `/home/astra/artifacts/som-method-learning-private/core-original-snapshot`. File hashes, index hash and status were verified unchanged after the experiments.

A separate worktree `/home/astra/projects/som-method-learning-core`, branch `codex/som-method-learning-trace`, starts from upstream commit `fae2fea08f74180759ef540ee94259213f503480` and retains those three instrumentation files. Commit `fca8391d51af195cd16e26dc871885a00a1a7c86` adds only these five selected PCs to the existing bounded trace switch: C0:F590/F5A3/F5DB/F5EE/F52D. Before selected instructions the inherited hook copies PC,A,X,Y,P,DB,D, 512 actor WRAM bytes at E000+X and 256 direct-page/global bytes. ROM lower-bank mirrors are normalized to C0–FF for PC matching. Trace ring capacity is 8192 records and the harness drains/resets every video tick.

Build after checking available resources:

```sh
make -C /home/astra/projects/som-method-learning-core/libretro -j12
```

Observed resources:32 logical CPUs,49 GiB available memory. Fresh core copied to private `core-method-watchpoints-v2.so`, SHA256 `0c92c628d11a1440155ef77e23dabd38e81743c3e6d2d95cf8fbecc222d31804`. Source file hashes and command are bound in `watchpoint-comparison-v2.json`.

The copied runner changes only the core override and the private derived-ROM output filename, and adds explicit dropped-record metadata. It uses the same original ROM/checkpoint and native equip 9/180 ticks/8 right/20 neutral/2 B+58 release inputs as the earlier experiment. The inherited checkpoint is staged; no pose,HP or charge RAM edits are introduced. A private derived ROM changes exactly byte at PC116A9A/nativeD1:6A9A from 1C to 19; the original ROM is read only and its SHA is verified unchanged. Neither original ROM nor derived ROM is included in this repository.

```sh
python /home/astra/artifacts/som-method-learning-private/run_hold_experiment_v2.py --core /home/astra/artifacts/som-method-learning-private/core-method-watchpoints-v2.so --variant baseline --output /home/astra/artifacts/som-method-learning-private/baseline-v2
python /home/astra/artifacts/som-method-learning-private/run_hold_experiment_v2.py --core /home/astra/artifacts/som-method-learning-private/core-method-watchpoints-v2.so --variant hold-field-1 --output /home/astra/artifacts/som-method-learning-private/hold-field-1-v2
```

Output folders intentionally must be fresh; use new suffixes when repeating. Private full CPU trace,60 WRAM/VRAM/CGRAM/OAM/screenshots and experiment receipt accompany each route. Baseline contains 1756 CPU events(934 hero X0); derived 1742(920 hero X0). Both complete268 monitored video ticks and60 review capture ticks, with zero dropped records asserted after every retro_run.

Actual hero X0 instruction link: at frame 13891/C0F5DB baseline A=AB00 vs derivedAB01, P=24 (M8). At C0F5EE A=00AB/P04(M16); E012 is 0 vs 1. Script start 6A96 and pose 171 are unchanged. Pose 172 follows at 13896 baseline versus13901 derived: the first pose holds 5 versus 10 video ticks. The compact JSON includes all five watchpoint counts and20/22 selected instruction records within script 6A96, plus complete pose-run lengths.

This is one staged-checkpoint/private-ROM-intervention causal experiment, not natural gameplay or a universal frame-control proof. Watchpoints are before selected opcodes, not every instruction. Stored P reliably exposes M/X width flags here; arithmetic flags cached separately by the emulator were not synchronized by the passive hook. No raw ROM or full private snapshots are published by this recipe.
