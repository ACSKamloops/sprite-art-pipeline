# Tested case and portability

This is an ImageGen-assisted modern RPG hero, not a universal animation recipe. The selected result is one compact unarmed guard-to-guard jab in one right-three-quarter view. The user chose the compact style. No model weights, proprietary vendor backend or hidden anatomy were recovered by this authoring case.

## What the example retains

- `assets/source-hand-fixture/appearance-reference.png`: appearance reference only; the approved walk pose is not an approved neutral/attack pose.
- Three frozen native key PNGs, two source maps and explicit control/triangle specs: enough to reconstruct extension and recoil without the original project.
- Raw expected extension/recoil and a finished recoil expected image. The first two are before the final local cuff repair; do not assign the final animation's score to those alone.
- `assets/selected-animation/manifest.json`, ten native frames and exact APNG: the actual selected whole sequence, not just its best still. Source manifest SHA256 is `61e85d0a88d5c021d8d26225b7bac1b20acf937d295c9e34fd9f4dab4359c45d`.
- `assets/prompts/`: three literal submitted requests, with source paths/hashes/roles in `index.json`. The complete-arm requests informed the useful keys. The final bridge-paint request produced an unused alternative; its prompt specificity did not guarantee compliant reach or matching volume.
- `assets/compact-jab-quality-result.json` and `assets/review-evidence/`: exact scoped score record and frozen reports. Paths inside the copied original quality record resolve against the original case root below; the report copies are indexed locally by `index.json`.

The fixture's192px stage, roughly99px painted body, arm ROI and hand shifts are measured example parameters. Generate a new spec for another character. These helper assets are not every image needed for a new action; a new character still needs accepted appearance and the required pose coverage.

## Actual outcome

The final ten exposures contain nine unique renderedRGBA states, not ten newly painted poses. Original eight key starts and total7/12s stay fixed. Contact-arm glove translation(-4,-1) reachesx142; early-recoil translation(-6,-2) reachesx134. Full glove rectangles are exact source RGBA. Complete connected proximal arm surfaces are deformed under a protected-body ROI. Two literal cuff passes changed10 then8 additional pixels, preserving all other frames, glove/path and holds.

Final frame-by-frame independent reviews:

| Reviewer | Consistency | Reference | Drawing | Motion | Usefulness | Overall |
|---|---:|---:|---:|---:|---:|---:|
|1|8.0|8.3|8.0|8.1|8.0|8.0|
|3|8.6|8.2|8.1|8.0|8.1|8.0|
|4|8.7|8.8|8.5|8.2|8.4|8.3|

All categories nominally reach8. Two reviewers weakly prefer the final cuff locally; one prefers the preceding ten-pixel cuff while keeping the same whole-clip score. The 0.1 drawing distinction is below stated absolute judgment uncertainty. Reviews are history-aware with masked labels and reconstruct still chronology; continuous human playback/controller approval is not established. Do not pass this scored history to a cold art reviewer.

The actual case separately verified full project journal replay/undo/redo, external LibreSprite layered save/reopen with native timing sidecar, exact rational APNG, actual28-frame48Hz MP4 timestamps/pose order, Godot resource/load/playback/input and20exact GPU captures. Browser checks covered483paused pose/background comparisons across16clips and every live exposure on seven refined clips. An actual pointer Pencil stroke on the final project was undone/redone/undone; its journal also replayed exactly in Python. Those case checks are not automatically rerun by this skill or inherited by another sprite.

## Failures that change decisions

| Tested route | Observed failure | Working consequence |
|---|---|---|
| Independent painted inbetweens | Fuller glove/bracer and mismatched edge treatment | Preserve a good key bank; compare complete source-pixel bridges |
| Whole-arm affine | Flattened fist despite connectivity | Rigid distal plateau, deform proximal connection only |
| Separate clipped limb pieces | Detached glove/joint gaps and wrong overlaps | Use complete connected donor surface, inspect actual joints |
| Pasted fixed soles | Calf shear | Keep full limb/contact geometry coherent, not only toe coordinates |
| Proxy-to-whole-body repaint | Abrupt guard/torso occlusion changes | Treat proxy as pose reference, not guaranteed production identity |
| Brighter flat buckle | Lost metal depth | Source-shaded edge repair and retained interior |
| More slots / shorter guard padding | Correct clocks without demonstrated motion gain | Equal-duration/key-time controls; inspect active phase rates |
| Exact source-hand map | Narrower-looking cuff still scored7.9 drawing with one reviewer | Local material-plane repair and fresh review, not math-only approval |

Four new built-in OpenAI ImageGen calls were explored in the case; there were zero new H3 calls and no local generative model. The selected bridge route does not require the unselected proxy/bridge repaint calls. An actual ImageGen request remains stochastic; the retained pixels and their offline reconstruction are reproducible.

## Original local evidence

Case root: `/home/astra/projects/rpg-hero-animation/work/motion-quality-v1`.

- `README.md`, `PIPELINE.md`, `REPRODUCE.md`: selected source, commands, rejected routes and coverage.
- `QUALITY-RESULT.json`, `FINAL-VERIFICATION.json`, `DELIVERY-FILES.sha256`: scoped judgments, actual selected checks and2665-file snapshot.
- `cuff-volume-editable-v1`: full layered project, journals, actual ASE/sidecar.
- `cuff-volume-delivery-v1`: actual Godot preview, PNG/atlas/manifest/APNG and test receipts.
- Sibling `compact-jab-rigid-hand-bridges-v1`: full producer controls/maps, rawRGBA, source ownership and read-only replay.

These paths are optional deeper local evidence, not dependencies of the portable helper/fixture. The full external editor/runtime toolchain comes from the installed companion skills. Other animations/views, world motion, equipment, hitboxes, game-controller integration and H3/PixelLab quality parity remain separate work.

## Skill package verification

The packaged helper was actually run for all three replay/bake specs against retained expectedRGBA. Negative cases rejected an incorrect expected image and a changed protected-body source address. An independent agent then followed the written skill in a fresh workspace: extension and finished recoil matched everyRGBA pixel and frozen map, all18 repairs reproduced, and existing populated/empty outputs were refused unchanged. No new generation, network request or source-project access was used. See [the independent report](../assets/validation/forward-test.md) and its adjacent JSON receipts. This tests the packaged workflow, not new-character art quality or a new runtime export.
