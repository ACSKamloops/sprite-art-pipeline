# Rowan whole-painted8 method trial

Authoritative selected cels are `candidate-v1/frames/00.png` through `07.png`. All eight are complete provider-painted bodies. The only edits are810 explicitly recorded isolated alpha1 background removals. No limb, cloth, boot, cuff, glove, head, body-loading, registration or timing correction was made. No art score or motion winner is assigned; root will arrange a fresh full-cycle review after freeze.

`REVIEW.html` is the local450ms player. `candidate-v1/proof/loop-SE-84-game.apng` compares the previous four-key/bridge cycle on the left with this whole8 on the right. That comparison bank remains read-only and supplies no paint to this candidate. Actual SEidle22 and neighboring cardinal idle/walk paint are included for identity/transition inspection.

## Source and registration

`inputs/provider/` preserves root's exact request, single eight-pose guide, guide inputs, raw1774×887 provider output, normalized512×256 whole sheet and fixed128 native cells. Raw original SHA256 is `d8b993a4b9e82dca53c7837e76ea744f9965e62527b8e5fd34ced2de442f4ca0`. Rebuild verifies one whole-sheet nearest resize, then fixed4×2 reading-order crops00..07. There is no per-pose fit, recenter, scale adjustment or head restoration. No generation was performed in this lane; semantic provider re-execution is not claimed reproducible.

The actual00/04 contact reversal and02/06 opposite passing are retained. `REGISTRATION-FINDINGS.json` records fixed-stage head/eye/buckle paint diagnostics against actual idle. Top-row hair alpha128 startsy15; bottom-row startsy13. Bottom-row eye paint is about1px higher, while the inspected buckle-base gold remainsy76 across all8, versusy75 on actual idle. This is not a uniform whole-body shift and does not establish camera drift. The differences may reflect pose or paint; all registration is retained for review.

## Exact cleanup and RGBA scopes

`inputs/ISOLATED-ALPHA1-CLEANUP.json` lists every removed coordinate and old/new RGBA. Counts are43/115/163/79/62/156/115/77. Removal is limited to alpha1 outside Chebyshev radius4 of alpha≥20 paint, using a9×9 maximum-filter body-edge guard. All other RGBA, all alpha≥2, and all94 source alpha0 hidden-RGB samples remain exact. There is no alpha hardening or palette cap. All76 raw positive stage-edge pixels are alpha1 and fall in this declared background cleanup.

`candidate-v1/raw-flat-project.json` retains the raw native crop cels, including hidden RGB. `candidate-v1/project.json` is the cleaned, honest one-layer8cel editable primary. `cleanup-journal.json` contains eight real guarded cleanup transactions; full undo/redo and saved-journal replay pass. No pencil strokes, source-part rig, hidden anatomy or corrective body paint are invented. The editor is `toolkit/editor/index.html`; load `candidate-v1/project.json`.

Authoritative `frames/`, `render_cel(project.json)`, decoded native cels and the actual LibreSprite PNG sheet retain all source RGBA outside cleanup, including the94 hidden-RGB samples. `display-frames/` is a separately labelled standard alpha-composited preview; its only differences are those94 alpha0 RGB values normalized tozero, listed exactly in `BUILD-RECEIPT.json`. Opaque-ground proof and browser display do not claim source-RGBA equality.

Conditional SW is direct integer x′=128−x about pivot64. All in-bounds source RGBA, including hidden RGB, is copied exactly; clipped sourcex0 is allzeroRGBA. `BORDER-MIRROR-QUALIFICATION.json` verifies alpha0 on every edge of all16 authored/mirrored cels. No extra cleanup, mirror fitting or relaxed guard is used. SW is a conditional mirror, not separately painted art.

## Clock, native exchange and replay

The shared stage is128×128, pivot(64,112), supplied game scale.66.84px is the rounded whole-stage proxy;256 is nearest2×. Every exposure is9/160 second,8exposures=72/160=450ms, loop=true, events empty. No timing experiment was made.

`candidate-v1/native/rowan-SE-whole8.aseprite` and its required adjacent `.sprite-lab.json` sidecar were actually saved/reopened/rendered by LibreSprite. All16 decoded saved/reopened cels, all8 rendered PNG cells and both sidecar reimport projects match authoritative source RGBA exactly, including hiddenRGB. `native/VERIFY.json` records commands/software/hashes. Native millisecond holds are[56,57,56,56,56,57,56,56], cumulative total450ms. Per-exposure preview errors are−.25/+.75ms; cumulative boundaries stay within.5ms. The sidecar preserves the exact160Hz×9tick clock, loop, pivot and empty events; no custom native loop/event tag is invented.

The author inspected all eight cels, every neighbor including07→00, SE/conditionalSW,84/128/256 and light/dark/game grounds, plus actual idle/cardinal context. `proof/INSPECT-*` are full literal atlases. `candidate-v1/proof/PROOF-MANIFEST.json` binds45 individual stills and18 APNGs to final frame hashes. Every APNG decodes all8 frames exactly and independently parses9/160 fcTL holds. These static/encoded checks do not claim continuous human normal-speed perception or engine contact.

`FRESH-REPLAY.json` binds a fresh rebuild from only the original/normalized whole-sheet PNGs, literal cleanup, helpers and toolkit. No native128 keys, final frame PNGs, projects or native outputs seed that rebuild. Twenty generated source outputs match byte-for-byte; the retained eight cleanup receipts separately replay exactly. Fresh actual native save/reopen/render/reimport also passes exact source RGBA.

Safe fresh replay command, using a folder that does not exist:

```bash
python /home/astra/artifacts/emberwake-rowan-full8-painted-cycle-v1/fresh_replay.py --out /tmp/emberwake-rowan-full8-replay-NEW
```

It reads this frozen package and writes only the fresh output folder, including `REPLAY-RECEIPT.json`. NumPy/Pillow versions are pinned in `requirements.txt`; native verification also requires LibreSprite on PATH.

## Limits retained for the critic

00/01 and04/05 remain close silhouettes; guide body loading is underplayed.03 has a crossed approach and07 a wide approach into the wrap. Identity, projected boot reach and top/bottom sheet-row head differences remain whole-cycle/idle-transition review questions. All8 drawn does not prove8strongly separated phases, smoothness, a reliable prompt method or superiority to the four-key construction.

Root's source bank, older banks and canonical remain untouched. No additional generation, H3, local model, broad rig, engine packaging or publication was used. The selected freeze excludes only duplicate fresh-replay working files; its completed receipt is retained separately. No edits follow freeze.
