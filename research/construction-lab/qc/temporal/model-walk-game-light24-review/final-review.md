# Fresh v11 visual decision: bow-carry walk foundation only

Manifest `03fa079e0495dd83f81ad6a00d1778f57e4b7effa885c4d5d54498ebd7c226c8` is a convincing four-direction modern RPG prerendered bow-carry walk foundation. This judgment follows fresh image viewing, not mechanical test counts or inheritance from v10. It is not production art, user art-direction approval, an original CopperScout design, pixel-painted art, or a complete animation library.

The dimensional hood, costume and anatomy remain coherent across true front/right/back/left views. Bent knees pass under a stable torso; stride alternation and modest bob carry body mass more credibly than the rejected contour rig, inconsistent AI pose sheet or short-armed painted cutout. The constrained arm now visibly carries its intended bow while the free arm counters the gait. I found no visible grip detachment, direction-dependent anatomical ownership swap or abrupt loop reset in the reviewed keys and chronological states.

The lighting repair visibly improves right-side calf and forearm readability and reduces the conspicuous side brightness imbalance noted in v10. Cloth, hood and leather remain recognizable without adjacent-frame material flicker. Different exposed surfaces and asymmetric accessories still differ in tone; equal whole-sprite brightness would be an inappropriate criterion. Independently recomputing the recorded camera-relative lamp matrices gives a maximum cross-view residual of `2.382249048e-6`, consistent with float32 precision. This supports the stated fixed-screen baked studio lighting convention, not dynamic world illumination.

Remaining limits matter: the thin olive bow is faint on the dark audition background, particularly behind the body; narrow feet and sparse face detail reduce native-scale readability. The carry walk is restrained, not a relaxed unarmed performance. Gameplay backgrounds, moving-world planted-foot slip, speed calibration, sole/toe contact, terrain clearance, collisions and transitions need separate evidence. Bow clearance above the lowest foot region is only an observation of these projected images. No inferred anatomical toe/contact certification is attached to the exported control landmarks.

## Actual viewing coverage

- Freshly viewed all 48 poses and all 44 ordinary adjacent pairs plus four loop wraps at native 1x and exact nearest 2x, in 32 pair sheets. Fixed canvas/origin; no per-pose recentering.
- Freshly viewed all **43** actual chronological browser screenshots: **22 native and 21 at 2x**, each containing four synchronized directions, plus all 12 paused pose screenshots. These are 172 chronological and 48 paused direction cells, assembled into 21 viewed strips. The actual capture count is lower than the announced 46; the receipt records the files that exist.
- Both capture modes ran for three complete 1.25-second clock cycles: 3.8196 and 3.8338 seconds. Screenshot before/after clock states may cross a pose boundary. I reviewed chronological screenshots and source clock logs; I do not claim continuous video ingestion.

Source timing is the actual 24fps Walk action, frames 0–30, with 12 unique sampled keys. Duplicate endpoint 30 is excluded. GIF centisecond holds approximate individual key times; the complete cycle remains 1250ms.

## Evidence and reproduction

`final-review.json` binds producer and MAIN manifests, all 48 PNG hashes, all five original source inputs, the exact frozen v11 renderer, packed scene, landmarks, producer reopen/byte reports, current browser HTML/config and fresh screenshot capture. All eight packed-scene reopen endpoints are reported exact by the producer; this independent review checks those report bindings rather than claiming a new Blender rerender. The separate unpromoted fine-edit demonstration is excluded.

From this worktree:

```sh
python qc/temporal/model-walk-final24-review/build_static_review.py /home/astra/projects/sprite-construction-lab-art-expansion/pilot/model-sprite-quality-v1/candidate-walk-bow160-game-light-v11 qc/temporal/model-walk-game-light24-review/pairs
python qc/temporal/model-walk-bow24-review/build_capture_strips.py /home/astra/artifacts/model-walk-game-light-final24-timed/capture.json qc/temporal/model-walk-game-light24-review/timed --manifest 03fa079e0495dd83f81ad6a00d1778f57e4b7effa885c4d5d54498ebd7c226c8
python qc/temporal/model-walk-game-light24-review/bind_review.py
```

The binding script verifies inputs and assembles a personally viewed decision; running it alone cannot perform or grant visual approval. Earlier rejections and v9/v10 receipts remain unchanged. The stronger walk derives from the licensed Quaternius model and authored performance, with declared presentation adaptations. It does not retroactively validate the rejected AI or cutout animation methods.
