# Native video to editable sprite poses

Use this route when a real image or video model supplies motion and the task needs deliberate pose selection, controlled pixel edits and engine export. It needs a usable reference image, not a 3D model. It does not recover an articulated rig or unseen surfaces. Independent image generations are not automatically a consistent animation.

## Freeze the comparison

Record exact ordered reference PNG bytes, literal prompt, direction/view, equipment, declared canvas and intended action. Keep first-frame, optional last-frame and identity references distinct. Whole-canvas padding or resize is a separate input derivative; do not fit each pose independently. A reference must actually show the intended character and needed equipment. Approval of its still design does not approve motion.

Record actual provider/tool/model and controls. Keep an agent identity separate from its image tool. An image-tool handoff and a native-video job have different capabilities; do not invent a shared checkpoint or seed. If the remote service exposes no seed, two differing outputs cannot establish a causal control advantage. The 2026-10-14 generic hero test used exactly two MiniMax-H3 requests, first-only versus the same PNG as first-and-last; first-and-last was the better authoring source in that pair, with no statistical efficacy claim.

Prepare the exact request before submission. Use persistent per-packet claims and per-run operation locks; an ambiguous POST must not automatically retry. Explicitly distinguish Prepare, Submit, Poll, Download and Decode. Reopening a run must show its actual attempted/completed state. It must not reset the paid submission count. This reference supplies no new spending authorization.

## Retain source clocks and bindings

Decode all native frames with integer PTS and rational time base. Derive each native hold from the next presentation timestamp, with a justified terminal duration. Do not replace this clock with an assumed sprite FPS. The observed H3 request for 4 seconds actually yielded 107 frames and 107/24 seconds; trimming to 96 frames would destroy evidence. Container/frame timestamps remain separate from the requested duration.

For a threaded server, external Linux `prlimit` avoids Python's unsafe threaded `preexec_fn` pattern. The local decoder has format/protocol allowlists, no crop/recenter/dedupe, and explicit encoded/decode/frame/pixel/time limits. Unsupported media should produce a structured failure rather than guessing timing.

**Attach provenance to the object that sampling consumes.** A native sequence wrapper can retain provider receipts while its extraction omits them; sampling only the extraction then loses the bindings from portable export. This occurred in v0.8. The correction binds upstream packet/admission/download or packaged request/reference records on the extraction itself, retains the prior extraction, and traverses those references during export. Test cold import after the complete decode → sample → condition → Studio chain. Verify exact wire bytes, reference PNGs, completion, download receipt, video and an unsampled frame. Keeping all raw pixels alone does not prove complete provenance.

The browser must carry `native_video` and `download_receipt` from Download into Decode, persist them across reload, and attach them only to the exact matching media ID. Manual replacement/upload must detach stale extraction/binding state. Backend receipt checks cannot help if the client silently drops the receipts. Older raw-only exports remain preserved; do not retroactively claim they contain missing bindings.

## Author poses and timing

Require explicit indices, one positive rational hold and a bounded role per selected pose, plus loop/one-shot policy. Reordered or repeated indices are legitimate authored decisions; do not silently sort/deduplicate. Source-derived holds require increasing indices. Hold selected poses until the next selected PTS when inspecting the native envelope; separately label compressed authored timing.

Inspect fast phases at full native resolution. Uniform 16-frame sampling of the retained attack omitted native 26/27; the revised candidate keeps both and gives them short explicit holds. Their inclusion repairs coverage, not blurry anatomy or a cropped sword. Local labels such as anticipation/strike/recovery are visual annotations; they do not establish contact or hit events. A loop checkbox does not establish a seamless cycle. The provisional walk `[18,58)` still changes sword/shield pose across its wrap.

## Condition and edit explicitly

Keep source RGBA and registration. Optional whole-canvas nearest resize, background removal and palette remap each need a named receipt with source/output hashes and parameters. Distinguish recovered code, calibrated mathematics, local engineering and unknown private methods:

- The recovered manual Godot seed selector is not the vendor's private automatic matte. A corner-connected selection can erase connected outlines and leave enclosed background pockets. Inspect every frame on light, dark, checker and saturated backgrounds.
- The calibrated fixed-palette rule uses Oklab distance with quarter-weight lightness and preserves alpha. Exact retained nondithered probes support that rule; they do not recover automatic clustering, high-color reduction, arbitrary tie rules or neural deflicker.
- Transparent-RGB normalization must be explicit in the editable derivative. Preserve raw inputs and visible RGBA/alpha. A composite cel is not an inferred body-part rig.

Use exact masks and guarded edits for local corrections. The demonstrated suspected arm/torso pocket used seedXY `[110,120]`, tolerance 0 and 207 pixels in only native 33/selected phase 3. The ambiguous next pocket was left unchanged. Outside-mask RGBA and the other seven frames stayed exact; undo/redo restored exact project IDs. The gap looked cleaner, but residual edges and motion remained unapproved. Do not generalize that coordinate or erase every dark region on another actor.

For semantic missing-pixel/anatomy repairs, use the selected art tool or image editor and separately review preservation, attachment and motion. A resize, key or palette cannot restore a sword tip cropped in the native video.

## Verify the actual consumer

For a shareable APNG, the bundled `scripts/exact_apng.py` consumes a portable manifest with `canvas`, boolean `loop` and ordered `frames` containing relative PNG `file`, mandatory byte `sha256` and positive rational `hold`. It supports2–512 static source frames. The output directory must be fresh and its parent must exist. The helper stores full-canvas RGBA, source blending, no disposal and exact reduced uint16 `fcTL` delay numerator/denominator; an unsupported delay rejects rather than rounds. `loop:true` gives infinite plays, `false` gives one. It changes no poses or native source pixels.

Before output creation it verifies source hashes/canvas, CRC/chunk/sequence/order/rectangles, exact encoded delays and every independently Pillow-decoded RGBA presentation. The retained synthetic three-frame test includes partial alpha and nonzero RGB beneath alpha0, asymmetric1/24,2/75,1/8s holds, single/infinite playback and stale-hash/delay/overwrite rejection under Python optimization. An installed-script forward run matched the tested APNG bytes. The actual27-frame H3 test preserved all1/24s holds. PNG encoding proof does not establish browser scheduling or art approval, and filesystem failure during final writes can leave a partial fresh output directory.

Do not use a hardcoded16-frame registration rule as proof that a cycle is complete. The local viewer now accepts declared complete8/27-frame clips with separate source, APNG and actual browser checks. Four-key studies remain studies regardless of a looping flag. Its actual readbacks covered all new source poses/scales and native boundaries; old browser receipts did not automatically extend to newly registered art.

One later H3 test retained native frames30..56 with57 as the excluded same-phase return witness:27 contiguous24fps poses, total9/8s. Actual support/passing/opposite/support progression made this a better motion source than arbitrary uniform phase bins. Blade orientation and apparent projected extent changed alongside torso/shield/head yaw; later independent inspection did **not** establish a detached grip or physical blade-length mutation. Foreshortening and coherent occlusion are valid explanations. The return was approximate and the recovered-host matte left halos and specks. A full canonical-upper replacement reduced natural articulation and scored below the raw motion in one paired review. Preserve identity without assuming identical head/upper pixels are necessary.

The matched-reference RR test used the original96px hero, whole-canvas3x padding onto a fixed matte, and identical first/last inputs. All107 native frames remained available; the observed cycle18..46 retained29 native1/24s holds with47 as a return witness. Initial/final holds meant the entire107-frame video was not a seamless walk. Both reference and endpoint conditioning changed from the earlier CC test, so improvement cannot be attributed to one control. A fresh paired reviewer preferred RR's identity and alternating gait, while keeping it below9. They found no demonstrated broken wrist, blade deformation or substantive anatomical failure; alpha/edge finishing and actual world contact were higher priorities than freezing the weapon swing.

Native-resolution corner flooding improved background removal but did not eliminate opaque pale fringe. Inspect light pixels on boot soles, calf edges and hair against dark and saturated colors, with per-pixel alpha visible. A mathematically valid binary matte can retain background-contaminated RGB at alpha255. Re-measure each clip's native corner colors; a threshold calibrated on another clip is not transferable evidence. Protect silver armor/blades rather than deleting every pale pixel. Local source-paste weapon repair also failed a review when a smoother tip trajectory created a flat bright strip over the shield: coordinate smoothness does not prove correct depth or paint.

Preload/decode candidate PNGs before timing a canvas. Per-frame network/image loads can hide short poses even when the clock index is correct. Inspect every selected native index against actual drawn pixels. Test short holds, pause/restart/final hold, stale asynchronous loads, reload and actual ZIP download. Browser scheduling can still skip short holds; callback count is not human smoothness approval.

Load the actual exported Godot project after an import pass, compare decoded texture regions to PNG RGBA, check frame order and rational-to-engine hold projections, then drive real elapsed playback through at least three cycles, pause and restart. Godot resource holds can have about 5e-9 float error for 5/24; keep the rational manifest authoritative and use a justified engine tolerance. A successful seek-only test does not prove normal playback. A three-cycle clock test does not measure planted feet, world contact, GPU appearance or artistic quality.

Review chosen frames, adjacent pairs, wrap, anatomy, gear, alpha, foot contact and intended game scale separately. Require actual normal/slow playback examination before production acceptance. Never convert test counts or pixel identity into a 9/10 art score.

## A polished source video still needs an improvement gate

One later test supplied the stronger unarmed sixteen-pose96px walk as both an appearance reference and a repeated actual sprite-video motion reference. One MiniMax-H3 request returned107768px frames at24Hz; all were retained. A fixed whole-canvas nearest96px bake with one declared green matte exposed residual green edges and small islands. Independent review found preserved identity and some transitional poses, but no convincing improvement in weight transfer or cloth/boot consistency. The branch stopped before loop selection or extensive edge cleanup. More returned frames and a successful service job are not evidence of better animation. Evidence: `h3-sprite-polish-CUCUCU`, `h3-sprite-bake-CXCXCX`, `cycle-review-CSCSCS/H3-delta.md` under the October15 case root.

Compare the actual same character before interpreting provider scores. The historical PixelLab armed-hero sample was not a matched baseline for this later unarmed hero. Record that gap explicitly. When replaying recovered client controls through a public endpoint, distinguish unchanged projection/calibration from an adapted image transport: the retained client used rawRGBA bytes, while the public REST route documented a PNG Base64Image. A manually authored eighteen-point reference is not recovered anatomy or a paid estimator result.

## Local tested implementation

Canonical project: `/home/astra/projects/pixellab-local-workbench`. Read `docs/motion-pipeline-20261014/README.md`, `CONDITIONED-WALK-REVIEW.md`, `BOUND-WALK-PROOF.md` and `docs/LATEST-VERIFICATION.json` for current package/evidence rather than trusting this historical version note. `examples/native-motion/plan.json` is a no-provider retained-media example. `scripts/verify_motion_package.py` runs an installed package outside the checkout and checks cold closure, precise edits and local CLI/JSONL/HTTP channels. The web UI is local Motion Lab and Studio, with explicitly enabled paid execution only when authorized for the task.

The implementation and credentials are environment-specific; another machine needs the package and host dependencies. Generic hero test artifacts live under `/home/astra/artifacts/pixellab-motion-pipeline-20261014`. No private PixelLab checkpoint, automatic matte/deflicker or complete service parity is claimed. The tested engineering route is reusable; these original video-derived walk candidates remain unfinished art. A later manually reconstructed guarded walk has separate 8/10 and 7/10 reviews; see [manual-sprite-delivery.md](manual-sprite-delivery.md). That does not retroactively approve the video candidates or establish service parity.
