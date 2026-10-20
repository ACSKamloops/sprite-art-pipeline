# Complete temporal review, baseline24

Decision: **changes requested**, not production art approval. Every adjacent-pair cell was actually visually inspected. `baseline-review.json` distinguishes that inspection from automated metrics and browser execution.

Baseline input: `pilot/rigged-character/generated/manifest.json`, SHA256 `a1089c42a9757e955e7bb410db33316fb92c8c6a47744b2cd2e1f62d01167ae5`,24bindings/1536frames. This is the original two-view CopperScout vector pilot, not extracted game art and not the upcoming front/back/detail revision.

## Reproduce

```sh
python qc/temporal/audit_pairs.py --out /tmp/copper-adjacent-fresh
python -m unittest discover -s qc/temporal -p 'test_*.py'
python qc/temporal/verify_review.py qc/temporal/baseline-v3/pairs.json qc/temporal/baseline-review.json pilot/rigged-character/generated/manifest.json
```

Outputs include every normal adjacent pair, declared loop seam, deliberate one-shot replay reset, and separate named idle/action and fall/recovery transitions. No pose is recentered; whole192canvas metrics and display retain weapon tips. Color-family masks describe composite colors, not anatomical segmentation or UV tracking. Scalar differences flag review; they cannot certify quality.

The v1 crop guard detected52frames whose weapon tips escaped the display crop. Its failed report is retained; v2 expanded to the complete canvas. V3 adds20named ready transitions and correct replay-boundary labels. V1/v2 image sheets remain locally preserved but are excluded from Git to avoid duplicate binary evidence; full v3 sheets are committed. Visual ledger0..767 references actual v2 views; those before/after RGBA bindings were checked identical to v3. All remaining v3 pairs, selected differences/overlays, and all192 chronological browser samples were actually viewed.

Eight meaningful adversarial metric checks include one-pixel off-palette texture, moved pivot without recentering, flipped asymmetry, material loss, wrong grip and joint jump. `coverage-gate-tests.json` verifies missing pair, missing direction, stale input and omitted source adjacency cannot pass completion. The validator also rehashes current rig/source and every referenced PNG. This gate certifies completeness of review evidence, never aesthetic approval.

## Findings and limits

* Shoot gun is a thin copper wedge at1x; clarify barrel/grip silhouette. Attachment consistency alone does not make it legible.
* Cast rear elbow jumps34.60px at9→10 and20.19px at54→55 despite small hand steps. Mostly occluded in side pixels; exposed new views require source continuity review.
* Idle/action transitions instantly add/remove equipment. Use an explicit equipped-ready/draw policy; do not advertise universal seamless idle transitions.
* Knockdown/recover opening unchanged holds deserve actual trigger/cadence review. A deliberate hold is not frame corruption.

All1556paircells were visually inspected in49bounded sheets. Automated flags358pairs include legitimate fast silhouette motion and occlusion. No detached identity/limb replacement or changed camera was found in this baseline review. That is a bounded consistency finding, not production approval, detailed-texture validation, collision/effect acceptance or moving-world contact proof.

## Actual browser playback

`capture_playback.mjs` ran the root-owned local exact-PNG player without editing it. Launch a localhost server for `/home/astra/projects/sprite-construction-lab` on38489, then:

```sh
node qc/temporal/capture_playback.mjs /tmp/copper-playback-fresh
```

The runner depends on the installed Playwright-core/Chromium paths written in the script; source paths and root server location are environment-specific. `playback-baseline/receipt.json` binds source/player hashes, all24actual routes, eight observed walltime/tick screenshots each, and raw drawn-frame records. Continuous screen recording is saved. The reviewer inspected all six chronological strips, not the entire video continuously. Screenshot overhead means sample times are not equally spaced source phases; terminal held frames are honestly included. Playback execution is separate from art judgment.

New48bindings require a fresh manifest hash, complete regenerated pair evidence, an independently recorded visual ledger and fresh timed playback. No baseline review aliases into a missing new direction.

## Fresh V2 review preparation

The analyzer retains each frame’s declared view, planar root, ground projection and material attachment contract separately from measured raster differences. A front/back planar boot reference does not imply that every boot must end on the side-view horizontal row. This metadata does not prove collision or actual moving-world sole contact.

Actual browser capture accepts a served checkout, pack URL and scale; it refuses to overwrite an earlier receipt and checks the manifest remains unchanged during capture. For the final local V2 viewer:

```sh
node qc/temporal/capture_playback.mjs qc/temporal/playback-final-v1 /home/astra/projects/sprite-construction-lab 'http://127.0.0.1:8144/pilot/review-player/?pack=../rigged-character-v2/generated/' 1
```

Wait for frozen producer sources and full generated manifest before running final evidence. Eight walltime samples include screenshot overhead and are not eight equally spaced phase samples. Review the actual captures and complete pair sheets separately; execution is not visual acceptance. Prior baseline changes_requested receipts remain unchanged.

## Persistent equipment and supported states

A full clip inspection does not prove supported controller transitions. `transition_contract.py` accepts a separately frozen `sprite.supported_state_review.v1` JSON contract containing `controller_source_bindings` (file paths and SHA256), and nonempty `transitions`. Each transition supplies a unique `id`, `kind` (`supported_state_transition` or `equipment_selection_transition`), exact `before_clip`/`after_clip`, zero-based `before_frame`/`after_frame`, explicit `before_state`/`after_state`, `before_equipment`/`after_equipment`, `policy`, and `evidence`. Missing variant/direction is an error; no default alias is substituted. Controller source hashes are checked when loading.

Pass `--state-contract PATH` to the analyzer, then include its SHA256 as `state_contract_sha256` in the independent visual review. The final gate accepts `--state-contract PATH --require-supported-states`; it fails if the contract, source hashes, or required comparison coverage is missing/stale. Baseline clip review correctly fails this stronger state gate because it contains no controller-state contract. All earlier baseline receipts remain historical evidence.

The producer's frozen f9bdcc3 candidate declares base48 inspection plus24 persistent-equipped locomotion bindings: `idle_sword`, `walk_sword`, `run_sword`, `idle_blaster`, `walk_blaster`, `run_blaster`, each in right/left/front/back. Matching sword actions and blaster shoot require explicit selection; cast requires none. The final controller's interrupt/stow transitions remain required evidence. These source declarations are not a final dense-frame visual review or executed controller proof.

Final producer scope has expanded to96 bindings: base48 plus24 sword/blaster idle/walk/run, and24 sword/blaster hurt/knockdown/recover, all four views. This is a pending export scope, not completed visual coverage. Explicit controller state comparisons must retain their exact bound equipment/state/policy metadata; changing it while keeping frame bindings now fails the gate. Synthetic positive contract tests certify validator behavior only.
