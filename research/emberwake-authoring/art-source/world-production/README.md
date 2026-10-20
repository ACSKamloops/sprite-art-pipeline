# Emberwake art production

Selected ready-to-copy game assets are in `output/assets/world/` and
`output/assets/enemies/`. The game checkout is owned by the integrating agent;
this workspace does not modify it.

All source art was generated with the built-in `tools.image_gen__imagegen` tool.
No local model, H3, image API CLI, public upload, asset download, or extracted
third-party game art was used. The blue/gold original hero image was the initial
style reference. World sprites, then enemies, ground textures, lit ward and
title illustration were generated for this game.

`ART-SOURCES.json` contains the exact prompts, source hashes, asset hashes,
crop boxes, source foot coordinates, scaling, paste coordinates, alpha checks,
and generation jobs. `IMAGEGEN-JOBS.json` retains the built-in returned file
locations. The original PNGs are preserved without modification in `raw/`.
Reference PNGs are preserved in `references/`.

Run `python scripts/prepare_assets.py` to reproduce the selected assets using
Pillow and NumPy. Source sprites are cropped and uniformly fitted, once, with
LANCZOS onto exact transparent game canvases; original generated alpha is
retained. The grass, path and water tiles use source raster crops downsampled
to 48x48 and six-pixel opposing-edge conditioning for exact matching seams.
The title is a center-fitted 960x540 copy of the selected second panorama.
The first panorama is an unselected source variant preserved for audit.

Visual proofs: `proof/contact-sheet.png` shows final props and enemies on a
checkerboard; each `proof/*-3x3-repeat.png` shows tile repetition. All selected
results were viewed at source and/or game output size. Base enemy art consists
of one original neutral sprite per kind; the additional authored key poses
described below add step, windup and strike images. Gameplay systems implement
timing, movement, hurt and defeat transforms.

World dimensions / foot pivots follow the shared contract: tree 192x256 /96,240;
cottage 320x320 /160,290; rock 128x96 /64,82; shrine 256x256 /128,230;
ward and ward_lit 96x160 /48,144; NPC 128x128 /64,112. Enemy dimensions /
pivots: scout 128x128 /64,112; brute 160x160 /80,144; warden 256x256 /128,224.

Additional authored enemy key poses are in `output/enemies-animation/`: each
enemy has `step.png`, `windup.png`, and `strike.png`, plus an optional matching
`neutral.png`. They come from one nine-pose ImageGen call recorded in
`ENEMY-ANIMATION-SOURCES.json` and `ENEMY-ANIMATION-JOB.json`. The atlas has
three characters by three poses, and alpha components are isolated because
raised weapons cross nominal cell boundaries. Every enemy uses one shared
row scale, with manually registered feet and no individual pose fitting.
The original neutral sprites filled their canvases to about y=6, so the new
poses require 12-14 percent smaller body heights to include raised weapons.
The compatible optional neutral variants match that size; original assets
remain unchanged. `scripts/prepare_enemy_animation.py` reproduces this set;
`proof/enemy-animation-keyposes.png` shows registration and all 12 frames.
These are authored key poses with runtime timing; they are not fully
inbetweened walk or attack cycles.

Accepted rear poses now sit beside front poses as `back_neutral.png`,
`back_step.png`, `back_windup.png`, and `back_strike.png` for scout/brute.
Warden has only the first three accepted rear poses. Its generated rear strike
swapped the club into the wrong anatomical hand and remains rejected at
`output/rejected-enemy-animation/warden/back_strike.png`. Two repair attempts
are preserved as raw evidence; the brute repair succeeded, Warden repair did
not. Generation is frozen. A runtime can use Warden back windup, phase effects,
and neutral rather than claiming the rejected strike obeys handedness.

Apply these exact scale multipliers to the whole back bank, around the existing
foot pivot, for matching front-animation body height: scout
`1.0017050298380223`, brute `1.1092468307233407`, Warden
`0.9989121794067194`. Scaling is shared per character row; poses are not fitted
individually. `ENEMY-BACK-SOURCES.json` records all source/prompt hashes,
landmark registration, per-pose validity and transform details. The script is
`scripts/prepare_enemy_back_animation.py`; proof is
`proof/enemy-back-keyposes.png`. Runtime mirroring for left quadrants is an
explicit symmetry choice. Actual back views were authored for upper-right;
they show rear heads/armor and omit eyes, faces and the Warden chest heart.
