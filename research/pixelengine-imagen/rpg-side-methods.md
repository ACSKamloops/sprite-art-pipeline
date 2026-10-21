# RPG E, W and SW ImageGen candidates, 2026-10-21

These are new, unaccepted animation-bank candidates for the user-preferred
Hybrid hero. The original Hybrid SE walk remains unchanged. The worker used
six actual built-in `image_gen.imagegen` calls: one initial call and one bounded
retry for each of E, W and SW. No H3, local generative model, CLI/API fallback,
weapon/effect artwork or publication was used. The underlying model identifier
was not returned; no specific model version is inferred.

Local evidence root:
`/home/astra/artifacts/hero-rpg-expansion-20261021/views-side/`.
Each direction owns `attempt-01/`, `attempt-02/` and `review.json`. Each attempt
contains literal `prompt.txt`, ordered paths/roles/input hashes in `request.json`,
untouched `raw.png` copied from the returned generated-images cache, and
`receipt.json` with actual dimensions, raw hash, cache path and tool metadata
without inline image data. The original cache files were left in place.

## Frozen request and actual layout

The shared contract is local `../CONTRACT.json`: 80 x 80 logical stage, target
painted height 64, origin `[40,72]`, unarmed body, top-down three-quarter camera.
Every call requested four columns, six rows, exactly 24 complete cels:

| Row | Four cells, left to right |
| --- | --- |
| 0 | Walk 0, 1, 2, 3 |
| 1 | Walk 4, 5, 6, 7 |
| 2 | Compact jab: guard, retract, same-arm extension, recover |
| 3 | Cast body: gather, aim, open release, recover; no painted effects |
| 4 | Idle A, idle B, hurt A, hurt B |
| 5 | Dodge anticipation, low dash, footing recovery, ready |

All six actual returns are **1024 x 1536 RGBA**, nominally 256-square cells.
Requested grid, source alignment and anatomical conformance are separate facts.
Some paint crosses nominal cell edges. At alpha >= 128, each raw has exactly
24 connected regions larger than 1000 source pixels, and none touches a
whole-sheet edge. The threshold is an analysis threshold only: the worker did
not threshold or clean any raw pixel. Connectedness does not establish anatomy.

Source-wide ownership or an explicitly recorded row-origin correction must
retain crossed-edge boots. Blind 256-square cropping can truncate them. Do not
resize or recenter individual poses. The downstream packer owns native-scale
registration, pixel/alpha policy, timing, editable exports and actual runtime
validation.

## Inputs and bounded retries

The original Hybrid appearance input is
`references/hybrid-eight-keys-5x.png`, SHA-256
`7f6c501d1d7c0f4cdd4b9c446383ff3734e10e70e55e43c64a1a06fb7aeabebc`.
The initial direction board was visually inspected and found to have an
incorrect nominal SW orientation and weak E/W profiles. It was not used as
facing authority. The corrected `references/direction-guide.png`, SHA-256
`42baba773373e4826a84a988328badd63e5b1853dba7e919f7858ffe0ba4546b`,
contains newly painted view context and a mirrored SW direction guide. Its SW
mirror does not authorize runtime-paint or lighting mirroring. The root worker
retains its actual guide recipe and sources.

| Direction / attempt | Actual ordered visual inputs | Demonstrated result |
| --- | --- | --- |
| SW 1 | Hybrid appearance; corrected board SW facing only | Walk and several idle/ready cels faced right, unlike left-facing combat. Retained as failed facing evidence. |
| SW 2 | SW 1 edit target/layout; Hybrid appearance; corrected board SW facing | Corrected the rightward cels to front-left. Passing 2/6 still repeat the same visible lifted-knee role. |
| E 1 | Isolated true-E profile guide; Hybrid appearance/style | Strong Hybrid view bias persisted: many heads/chests read front three-quarter. |
| E 2 | Isolated E profile guide alone | Narrower side view, one visible eye and right-facing nose/toes across the bank. Walk 2/6 still repeat the same visible raised knee. |
| W 1 | Isolated W profile guide alone | Broadly consistent true-left profile; repeated visible raised-knee role in the second walk row. |
| W 2 | W 1 edit target; isolated W profile guide | Requested only cells 4-7 to exchange leg roles. Cell 6 now clears a rear/right-side boot versus the front/left-side boot in cell 2. Contact depth ownership remains ambiguous. |

The W edit instruction does **not** prove that the other 20 cels survived
unchanged. Its complete returned sheet is newly generated paint; no
outside-mask equality or protected-pixel claim is made. No later compositing,
head restoration, mirroring or manual painting was performed by this worker.

The isolated guides are derived, newly painted reference art, not recovered
hidden anatomy from the original SE sheet. E/W profile quality improved after
omitting the original three-quarter sheet as an actual image input. This is a
bounded observation from these calls, not a universal ImageGen behavior claim.

## Raw output hashes

Paths below are relative to the local evidence root. Attempt 2 is the producer's
preferred candidate in each view, pending root review and human acceptance.

| Raw path | SHA-256 |
| --- | --- |
| `E/attempt-01/raw.png` | `d1090ea5e600a7f0f54ceb10c7897d1904b93b7c36ebe3a5f4a2edd3f4ff6022` |
| `E/attempt-02/raw.png` | `957640b244e99d8ba1c88b05b0ad894e7643068bc0c94041a52d57379ede9d85` |
| `W/attempt-01/raw.png` | `8bce8d08cd2c544317b9d0fe4033037d101883db96f8bf856593056bf12b2790` |
| `W/attempt-02/raw.png` | `ed3481cc79cecec210559a0af15c766e244a7622ef52be744d333ea0ce955ca0` |
| `SW/attempt-01/raw.png` | `9b671feded0ef016dab58f757ec8488cf17793372cfcebc46ef8f079591ede48` |
| `SW/attempt-02/raw.png` | `f0aad76fef4bd3793cbf94324eee5d8eee737a98a44720a180166670393b4771` |

## QA recipe and verification

Each attempt-02 `qa-logical2x-white.png` uses exactly this preview transport:

```python
small = raw_rgba.resize((320, 480), Image.Resampling.NEAREST)
white = Image.new("RGBA", small.size, "white")
white.alpha_composite(small)
preview = white.convert("RGB").resize((640, 960), Image.Resampling.NEAREST)
```

This is one whole-sheet nearest transform, white source-over composite and
nearest 2x enlargement. It is a QA proxy, not newly native-painted pixel art,
an export or an engine render. No independent frame fit, translation, alpha
normalization, palette conversion or paint edit is hidden in the preview.
The exact recipe and preview hashes are saved next to each candidate.

Verification read every raw PNG, checked its actual size, checked SHA-256 and
byte equality against its actual returned cache file, and checked that saved
`prompt.txt` equals the literal `request.json` prompt. Current reference hashes
matched the recorded input hashes. Alpha extrema are 0..254 for all six raw
returns: near-opaque interiors and faint off-body alpha remain untouched. Brown
RGB in the tool preview is largely under transparent/faint pixels; the white
composite is the relevant still-view QA, not evidence of a solid brown matte.

The producer inspected all 24 poses per view, every cyclic walk predecessor
pair including 7->0, action preparation/reach/recovery, idle/hurt/dodge sequences
and stance joins as ordered stills. `review.json` binds findings, raw hashes,
alpha analysis and source-region bounds. The principal remaining limits are:

- E/SW repeated passing roles and unclear opposite-contact ownership; W's
  improved clearance still needs an anatomical/timed gait review.
- Head/body ratio and glove/boot/tunic volumes drift from Hybrid. Direct 80px
  logical normalization makes most figures taller than the requested 64px;
  shared-scale registration remains necessary.
- SW idle/ready views are more frontal than its combat views.
- Static inspection does not establish continuous normal-speed fluidity,
  ground contact, exact protected pixels, art approval or a numerical score.

No baseline, runtime atlas, editable project, source pixel journal or exported
timing manifest was changed. No art binary was committed to this methods repo.

## Workspace handoff

This worker used exclusive branch `codex/rpg-combat` in
`/home/astra/projects/sprite-art-pipeline-rpg-combat`. The filesystem filled
before the first generation call. At the root worker's direction, this clean
temporary checkout adopted sparse paths `docs skills research scripts`, retaining
root files and recoverably omitting redundant tracked workbench/demo/example
copies. This freed 212 MB at that observation; no unique/shared data was deleted.
The worktree remains for root integration and review. The root worker owns its
cleanup after integrating this methods commit and preserving the handoff.
