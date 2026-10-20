# Local sprite Studio

This release joins the supplied-art workflow into one local interface. Its acceptance target is a reproducible edit/playback/export cycle. Artwork still requires a separate visual decision. Test results and installation identity belong in VERIFICATION.json, not in an assumed quality score.

Open **Studio** in the local web controller. Load the walk loop or one-shot sword slash, or bring your own project/sequence through Workspace. The two packaged examples contain 16 generated frames each. Their 8FPS clock is explicitly authored for inspection: the recorded provider response did not supply native timing. Returned reference slot0 and the original submitted reference remain separate, retained sources. Nothing is cropped, rescaled, aligned, deduplicated or assigned an inferred ground contact during import.

1. Choose a frame at native resolution or 2×. Play, pause and step through it. Compare the working copy to the retained source.
2. Choose an unlocked cel/layer. Enter a seed and normalized tolerance, then create a selection. The mask uses alpha; transparent white is unselected.
3. Erase or paint using a declared palette index. A mask is tied to its source project and cel. Changing a frame, layer, project, seed or tolerance invalidates the UI mask; the backend also rejects stale applications. Shared cels stay shared, with affected frames listed.
4. Use the fine editor for individual pixel and palette changes. Undo/redo operates on validated immutable history. Reopening the browser restores the project/history identities, never an old selection mask.
5. Run mechanical checks and export. The package includes frame PNGs, a full-canvas sheet, rational timing/pivots/events metadata, APNG, editable artifact closure, review material and a Godot preview project. The exporter reads its output back before exposing a download.

The raw-to-editable boundary is explicit. The indexed compositor normalizes RGB beneath fully transparent pixels. Own imports with nonzero hidden RGB require an opt-in editable derivative; visible RGBA and all alpha remain unchanged, and the original encoded and decoded sources stay available. This is a host editing policy, not a claim about PixelLab's private conversion method.

## Repeatable verification

The installed-package exercise is `scripts/verify_reliable_system.py`. Run it with the isolated environment's Python using `-I`, an absent output directory and `--expected-prefix` pointing to that environment. It executes the recovered Godot selector, makes a real hero edit, checks outside-mask indices, undoes/redoes, rejects a stale mask, replays the selection receipt, exports and cold-reimports, and checks CLI/JSONL/HTTP/plan channels. It launches no generator and makes no provider calls.

`tests/test_reliable_godot.py` covers the emitted preview project with real headless Godot. The authoritative stored clock is rational; engine/browser playback uses admitted floating-point seconds. Declared gameplay events are dispatched by the Godot driver. The exporter does not infer hits, foot plants, hurtboxes or sockets from image pixels.

`PACKAGE.json` inventories every other ZIP member with byte count and SHA256. `verification.json` records the format readbacks. The editable closure retains the original sources, indexed projects, history checkpoints, masks and selection receipts. A successful package check certifies those mechanical properties. It does not certify anatomy, directional consistency, attractive motion or private-model equivalence.

## Generation and model comparison

Model Lab remains the explicit interchange point for Codex and Hermes tasks. It retains the actual generator/executor identities, brief, reference rasters and imported raw results. Import a supplied PNG/APNG or model-result sequence into Studio after admission. A MiniMax text model is not silently relabelled an image model. A task packet is not a completed generation. New providers require demonstrated capability mappings and preserved raw output before any comparison.

Recovered source VFX and the manual host selector are available locally with pinned source hashes. Manual selection is not automatic neural cutout. The selector executes recovered Pixelorama host GDScript with the documented no-active-selection fixture; compiled-bytecode identity and all possible host states are not established.

Private PixelLab weights, exact high-palette quantization, dither rule, animation sampling, neural cutout and deflicker remain unresolved. The previous black-box findings remain in [recovery round3](../recovery-round3-20261014/README.md). No new local orchestration is presented as one of those recovered private methods.

## Remaining art acceptance

The supplied walk/slash are useful regression fixtures, not approved production assets. Review native-size timed playback, every adjacent pair, first/last wrap for loops, one-shot endpoint, equipment ownership, silhouette, surface details, foot contact and effect separation. In particular the recorded slash contains a sweep despite a no-effects prompt, and the walk ends in repeated frames. Keep these observations visible rather than treating a working exporter as a 9/10 animation result.
