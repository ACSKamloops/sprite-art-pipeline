# Reliable studio acceptance: independent workstream

Baseline reviewed: `0a08d00`. Existing mechanical checks are useful evidence, not art approval or a demonstrated integrated product. This review owns a focused preservation fix and acceptance tests; root owns studio orchestration, export/player changes and actual browser integration. No provider, credential or network calls are involved.

## Material baseline findings and action

1. **Construction metadata loss, fixed in this workstream.** `construction.from_sequence` rebuilt frame IDs, cleared events/landmarks and substituted render pivot for ground pivot. A render-produced sequence could therefore lose its own semantics on editable reopen. The fix preserves explicit FPS/ticks, ordered/repeated frame IDs, landmarks, events and independent ground pivot. Inconsistent declarations reject before creating new artifacts. An explicit FPS override conflicting with the source clock rejects; it does not silently retime events. Plain supplied sequences retain their existing exact auto-clock/default policies.
2. **Linked-cel scope needs an explicit product choice.** Import deliberately shares cels for equal rasters; a cel edit changes every alias. This is valid toolkit behavior, but a frame-local UI action must either disclose linked scope or explicitly detach. Root/selection workstream is handling alias reporting; this reviewer does not change that policy.
3. **Export/player acceptance needs actual readback.** The baseline Godot driver handles pivots/play counts, without event dispatch. Editable CAS reopen verifies a different artifact than exported PNG/sheet/APNG files. A concrete APNG roundtrip preserves pixels but changes exact holds `1/7,2/9` to decimal-derived fractions because acquisition reads Pillow float milliseconds. Root was notified and owns export/player/import correction.

The APNG counterexample is retained privately at `/home/astra/artifacts/pixellab-reliable-acceptance-20261014/baseline/clock-gap.json`. It is a timing equality failure, not a visual judgment. No changes to `export.py` or acquisition were made here.

## Acceptance matrix

| Area | Required observable evidence | Baseline / ownership |
|---|---|---|
| Raw import | Original encoded bytes and every decoded RGBA byte retained, including hidden RGB and partial alpha; source hash bound | Existing acquisition/CAS; independent test pending studio entrypoint |
| Editable normalization | Explicit user policy produces a separate normalized derivative; raw sequence remains addressable; receipt lists exact changed alpha-zero RGB and keeps all nonzero-alpha RGBA exact | Root studio implementation; hidden-RGB rejection in current construction import is correct |
| Reference frame | PixelLab returned slot0 retained as reference; generated clip indices1..16 selected explicitly, never by duplicate removal or guessed semantics | Root studio import contract pending |
| Clip metadata | Rational holds, pivot, independent ground pivot, authored events, frame order/identity, direction and loop/one-shot preserved or unsupported values rejected | Construction preservation regression below; actual export/player coverage pending |
| Stale mask | Mask bound to source/project/frame/cel hash; an intervening edit invalidates application even if dimensions match | Selection workstream; adversarial tests pending API |
| Mask ownership | Edits touch only allowed pixels; compare full RGBA outside mask including hidden RGB; candidate image canvas retained | Existing toolkit candidate guard; product-path verification pending |
| Locked and shared cels | Locked layer rejects edits atomically; alias list is visible; frame-only edit detaches deliberately or requires linked scope | Existing toolkit; selection/UI integration pending |
| Undo and reopen | Multi-operation failure changes no current state; undo/redo and head compare-and-swap survive fresh Store/process reopen | Existing history; integrated session path pending |
| Export integrity | Decode written PNGs, sheet regions and APNG, compare actual RGBA/order/holds/loop against authoritative sequence; reopen editable into fresh store | Root full export verification planned |
| Broken export | Missing/corrupted/reordered images, altered sheet, changed manifest holds or incomplete closure reject verification with no accepted publication | Root verifier contract pending; negative tests to follow |
| Preview parity | Actual displayed frame samples equal stored frame RGBA at the same source time; pause freezes; speed scales presentation only | Root browser evidence pending |
| Godot playback | Reload real resource, inspect actual texture regions/pivots/durations/loop and timed transitions; loop wraps and one-shot completion/replay observed | Root engine/player changes pending; test proposal below |
| Event crossings | Start/boundary/last-hold events emitted once per crossed source time; large delta crosses every event; pause emits none; restart scopes a new play | Baseline driver gap, root owns fix |
| Art acceptance | Native-size adjacent poses, wrap, attack anticipation/strike/recovery and actual normal-speed playback reviewed by a human | Static candidate sheet inspection only; no art approval or numeric score |

## Executable verification so far

`python -m pytest -q tests/test_reliable_acceptance_construction.py tests/test_construction_core.py tests/test_construction_adversarial.py tests/test_construction_channels.py` completed **107passed** in0.96s. The new file contributes21cases. Existing Pillow deprecation warnings remain. This selected run is not a rerun or replacement count for the previously reported full suite.

New cases exercise a120FPS project with2/6ticks, repeated frame IDs, three authored event positions, independent ground/render pivots, landmarks and partial alpha. The sequence→construction→sequence roundtrip preserves all those values and pixels for loop and one-shot. Invalid clocks/ticks, conflicting repeats, malformed landmarks/events and unsupported ground pivots reject without adding blobs. Plain supplied-image import still derives exact63FPS for holds1/7and2/9.

## Proposed engine contract tests for root's player

Use a tiny three-entry clip `contact,passing,contact`, holds2/6/2ticks at120FPS, events at0/2/9ticks and unequal render/ground pivots. The exported player should expose source-time/frame/completed/loop-count state and an observable event signal or receipt. At source time2/120it must show the passing frame and emit the boundary event. At10/120a loop must return to frame0and emit the next start once; a one-shot must hold the final entry and mark completed. Play on a completed one-shot must follow a documented policy; explicit Replay must reset it. A single large step crossing several holds/wraps must emit every crossed event, not only the final displayed frame. Pause must freeze both pixels and event clock. Speed2must halve wall-time holds without changing source event times.

After actual timed playback, read SpriteFrames and the active AtlasTexture region back from Godot; inspect sampled RGBA against the exported source pixels. Merely setting a frame variable or checking generated `.tres` text does not demonstrate playback or texture parity. Keep rational source timing authoritative and record float-engine tolerance separately. Root will implement/export these interfaces before this reviewer adds adversarial integration tests.

## Candidate review status

Only the generic RPG hero PixelLab walk-v1and slash-margin-v2generated slots1..16are in scope. Slot0is a separately retained reference; no Captain assets were used. Their checkerboard contact sheets were actually inspected in chronological grid order. This is static coverage, not continuous native video or normal-speed playback.

Walk shows recognizable contact/passing/raised-foot poses with attached sword/shield, but torso/shield depth and stance width vary across the cycle. Foot support and wrap smoothness require actual timed review; no planting or stable anatomy claim follows from the sheet. Slash shows anticipation, a forward strike and recovery, but the visible white sweep in generated slot6conflicts with the retained prompt's “no magic or motion effects.” Several adjacent strike/recovery poses look similar, so holds and the readable strike window need temporal inspection. The static sheets alone do not approve either clip for gameplay, infer hit timing or justify a9/10rating.

Both are useful product stress-test candidates: soft alpha and color variety exercise raw import/normalization; weapon reach and foot placement exercise fixed registration and framing. Actual integration export/reload and normal-speed review remain required before a product or art acceptance claim.
