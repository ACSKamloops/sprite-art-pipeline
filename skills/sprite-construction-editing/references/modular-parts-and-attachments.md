# Modular painted parts, equipment and sprite baking

Use when the character should reuse motion while changing weapons, shields, clothing or accessories. Keep this route separate from whole-frame neural redraws and from a copied rigid upper body. The retained hero case showed that preserving an entire upper assembly can remove useful shoulder and equipment articulation.

## Choose the smallest useful representation

1. **Baked body plus equipment tracks.** Keep approved body cels and extract visible equipment, hand-over-grip masks and attachment sockets for each pose. Replace equipment and composite it using the existing phase clock. This preserves the strongest existing gait, but requires per-pose masks, perspective variants and explicitly painted body regions exposed by a smaller replacement.
2. **Hybrid painted rig.** Animate source-painted upper/lower limbs and equipment with bones or meshes; use alternate painted hands, feet, elbows and direction-specific shape keys at difficult angles. Preserve coherent natural head, hip and shoulder motion. A single rotated cutout cannot supply every projected shape.
3. **Full cutout rig.** Begin with a directional neutral pose designed for separation and a complete part library. This offers reusable motion and equipment swaps, but needs the most missing paint and anatomical authoring. A front image does not supply a back view.

Select by the actual source, not by tool availability. A high-quality generated walk may be a better body source for route1 than a new full rig. Test the distinction before expanding to more actions or directions.

## Author a source-bound part contract

For each part record a persistent ID, anatomical or equipment role, directional variant, source PNG hash, canvas/offset, visible-pixel ownership mask, pivot/socket, parent, local transform, palette/material and default draw order. Store source-visible paint separately from newly authored hidden paint. Keep uncertain visible ownership separate from confident body/equipment labels.

Partition visible pixels into disjoint owners and verify their alpha composite reconstructs the source. This proves the partition, not the correctness of its anatomy, depth or future motion. Hiding a weapon or arm exposes an **unknown-underlap footprint**; transparency in that footprint does not mean the character has a hole. Generate or paint the missing region as a new asset and retain its source/mask/provenance. Never describe invented anatomy as extracted.

For a parameterized mesh rig, retain the actual vertices, UVs, triangle indices, per-parameter key values and vertex offsets, coordinate conventions, combination rule and valid simultaneous-parameter domain. Test combinations as well as separate axes: individually acceptable controls can pull layers apart when combined. Keep persistent layer IDs distinct from draw-order positions. A baked image grid or seekable video preview does not expose or verify the underlying geometric evaluator.

Equipment needs more than one overlaid image. A hand may cover the grip while the blade lies in front of a boot; a shield can hide the far arm. Use explicit front/back item pieces or hand-over-item masks, per-pose draw order and view-specific textures. A same-size alpha-preserving RGB retexture can reuse a verified mesh/UV/deformation asset; a different silhouette does not inherit that guarantee. Remesh/retarget or supply a compatible replacement drawing and recheck contacts/underlaps. Define the grip in both item-local and hand-local coordinates. A numeric socket match does not prove that the fingers grasp the item convincingly.

Separate interchangeable equipment from motion-profile compatibility. A one-handed slash, two-handed swing, punch and ranged release may need different body/hand drawings; reuse item tracks only where grip and pose constraints match. Bind each anchor/mask track to current body-frame hashes and invalidate it when those frames change. Held visuals, collision/damage windows and independent effects have different data and lifetimes. Unknown hand/grip coordinates must not be replaced with the centroid of whichever glove is most visible.

The generic-hero preparation at `/home/astra/projects/rpg-hero-animation` includes `actions/attachments.schema.json`, an example and `docs/equipment-tracks.md`. They describe planned contracts with null unmeasured anchors, not an implemented attachment renderer. Both initial new body actions are unarmed. The companion animation skill's `references/approved-character-new-actions.md` covers the action/transition preparation.

## Separate paint, motion and rendering

Use the approved image tool for neutral designs, missing underlaps and alternate pose paint. Keep prompts, references and native outputs. Restore known source pixels outside the accepted edit mask. A generated exploded atlas is a newly painted proposal, not lossless segmentation; check proportions and semantic IDs before rigging.

Motion may come from authored keys, recovered client controls or retained video observations. Retarget with explicit joint/paint anchors: patella, boot cuff, ankle and sole are different points. Keep persistent leg identity through crossings and mark occluded landmarks unknown. A reasoning model may draft joint JSON; correct angles do not establish good movement. A rig may preserve its authored rest/model-space lengths while projected lengths change with foreshortening and replacement drawings. Do not enforce constant screen-space lengths on painted poses.

Animate parameters/bones and equipment sockets, then bake into one fixed canvas with declared rational holds. Keep the physical root, whole-actor presentation offset and individual part transforms distinct. Check sampling: continuous rotations, bilinear filtering and supersampling can soften pixel clusters or add palette colors. Nearest display scaling after a soft bake does not recover the original pixels. Choose and verify a raster policy at the intended native resolution.

## Verify progressively

- At rest: source hashes, ownership, exact visible reconstruction, meaningful joint positions, and explicit missing-underlap areas.
- At angle extremes: ±30° limb/accessory studies, joints/caps, cloth deformation, grip, draw order, silhouette and newly exposed paint. Use actual rendered pixels as well as anchors.
- Across a short action: opposing leads, contacts, passing, recovery and wrap; persistent equipment/limb identity; temporal pixel clusters at1× and2×.
- After an equipment swap: body pixels outside the declared item/occlusion/underlap union remain exact; item sockets and hand coverage remain correct. Include a deliberate displaced-item negative control.
- In the engine: actual import/GPU fidelity, live pose clocks, physical-versus-visual root behavior, contact evidence, interruption/start/stop behavior and the final encoded motion presentation. Independent art review remains separate.

A layer/mask identity pass, a zero-error socket or a deterministic renderer is not an art score. Keep the strongest single-view/action acceptance narrow until other views and actions are actually made and reviewed.

## Source-painted part reuse: checked case and limits

A registered clean head drawing can replace a single soft generated head while retaining the body's existing motion. Establish alignment from visible features, trace the whole head/neck ownership seam, protect shoulder/collar paint, and explicitly count silhouette/alpha changes. Do not assume identical cropping means identical anatomical registration. A reused head held across two body cels is a real motion decision requiring timed review; it is different from replacing the whole animated upper body with one fixed image.

Keep the pre-downsample native video. In the retained96px case, higher-resolution source frames showed an inter-boot boundary weakened by the fixed8:1 sample. Source-guided pencil drawings clarified two overlapping boot volumes without changing their alpha. Their near/far labels were working visible tracks, not recovered hidden knees or full boot masters. Native-pixel authorship, source paint and uncertain anatomy remained separately recorded.

The combined head/boot candidate passed guarded composition, full undo/replay, actual external editor exchange, independent reproduction, exact source/APNG clocks and actual Godot source-pixel checks. Local part reviews passed, but a fresh full-cycle review remained7.8/10: broader boot-shell continuity and loaded body response still limited the walk. Local improvement does not prove a complete rig or high-quality motion. When whole-cycle quality stalls after local passes, revisit projected shapes and body mechanics rather than counting more cosmetic repairs as progress toward acceptance.

Evidence: `rr-head-reuse-PPP/`, `rr-boot-parts-MMM/`, `rr-part-integrated-QQQ/`, `independent-review-MMM-NNN/` and `independent-review-QQQ/` under the retained local case path below. The first two are bounded part studies; a full modular animation and arbitrary equipment library remain unmade.

## Recent source research and limits

### A correct reconstruction can conceal an incorrect part boundary

Trace articulated foot ownership by the painted shape, not a horizontal ankle row. In the later neutral-master test, a heel-strike drawing's raised vamp/toe extended above its ankle row. A row split assigned those foot pixels to the calf; the calf warp then pulled an extra pointed toe away from the rigid foot. Exact RGBA reconstruction, opaque anchor witnesses and an editable ORA all passed. Independent inverse source tracing identified the wrong ownership. Keep ankle, cuff, heel and toe witnesses, and inspect each part independently at the pitched extremes before animating a bank. Evidence: local `neutral-rig-review-BBBB/CUFF-FOOT-SPLIT-TRACE.json` under the retained case root.

An unarmed directional neutral master made visible-part ownership easier, but did not supply missing shell views. The tested four-key rig still merged one passing silhouette, elongated the other shin and warped planar armour. Newly generated boot shape drawings improved individual volumes without solving their integration. The independent gate rejected cycle expansion. Do not turn these prototype capabilities into an approved full-rig recipe.

### Diagnose the raster before replacing plausible anatomy

Preserve the generated native video before reducing it to game scale. In the later unarmed H3 test, a fixed native matte followed by one nearest reduction left pale edge fragments that changed the apparent boot mass. A bounded alternative used each native 8×8 block's majority coverage and an actual foreground RGB donor, retaining nearest-center RGB in fully interior blocks. Donor membership, alpha decisions and changed pixels were recorded. This improved several contours, but a fresh whole-cycle reviewer still rejected the gait and pixel finish. It is a source-bound raster experiment, not a universal best bake or an art approval.

Reassess the original defect after changing that bake. A proposed 38-pixel same-phase boot-paint reuse passed guarded edits and left silhouette/geometry exact, yet showed no meaningful motion benefit and risked brightness pulses beside unedited neighbours. It was not promoted. An overlapping boot can legitimately disappear behind the nearer one; filling a supposed missing volume or forcing a visible gap can make the drawing wrong. Keep structural pose defects, edge contamination and legitimate occlusion separate. Local evidence: `h3-neutral-ZZZ`, `pixel-bake-HHHH`, `neutral-bake-review-MMMM` and `boot-continuity-LLLL`.

Research window for the retained2026-10-14 task was2026-04-14 through2026-10-14. Verify publication or substantive code-change dates; crawl dates and a recent repository update do not redate an old algorithm.

- [Rev2D's October6 implementation](https://github.com/RevStudio/Rev2D/commit/f144581cdf1f12d781379c4df90d262b8c2dfa3d) provides text rigs, bones/warps, attachments and agent-oriented render/inspect operations. Its avatar path targets larger front-facing busts; code uses smooth hole filling and bilinear texture sampling. It is not established as a96px locomotion generator. The pinned local raster/recipe tests passed79 checks. A separate two-equipment raster probe found default supersampling changed215 pixels at rest in one fixture, adding50 visible RGB colours and93 partial-alpha pixels. Single-sample rest/integer translations/90° rotations were exact; fractional translations and arbitrary rotations still added colours/partial alpha. Repeated output and socket transforms were correct, which did not make the raster pixel-preserving. Tool evidence does not establish hero acceptance.
- [AI-Sprite-Animation's October5 update](https://github.com/JatCool/AI-Sprite-Animation/commit/3818664861613905a377eca26c4ea940c06a646d) supplies a deterministic mask/underlay rig route. Its optional local-model branches were outside the retained task constraints. Unity/Windows claims were not treated as verified Godot/WSL support.
- [Bunraku, July29](https://arxiv.org/abs/2607.27348), predicts completed ordered layers and coordinated mesh keyposes. The inspected release was paper/demo plus a README-only repository, not an available executable pipeline. A bounded one-case public study found20 ordered alpha-layer previews, but no native mesh/UV/triangle/keypose arrays. The frontend seeks prerecorded video and blends baked grid images; it does not run the deformation predictor. These preview textures are resized/lossy presentation assets, not source-exact parts. Its avatar demonstrations do not prove small game locomotion.
- Recent parts-DAG and reskin implementations are catalogued with dates, licenses, actual code behavior and older exclusions in the retained research ledger. A February splitter stayed outside the window despite later reskin commits. Image resizing and generation were not called pixel-preserving operations.

Local evidence: `/home/astra/artifacts/pixellab-hybrid-walk-20261015/game-ready-v6/modular-research-20261014/`. Read `ai-recent/REPORT.md`, `ai-recent/source-ledger.json`, `local-feasibility/` and `rev2d-evaluation/` for the current checked/proposed boundary. The papers/tools above inform an experimental route; they do not establish recovered private PixelLab architecture or full service parity.


### October15 follow-up: useful author cases, bounded claims

[Riggy's October7 pixel-art case](https://riggyapp.com/blog/spine-pixel-art-animation) describes native-resolution rasterization before nearest enlargement, centred overlapping joints and converting desired screen angles into offsets from each part's actual rest angle. Its single-image automatic cutting was explicitly untested on pixel art. These are author-reported preparation/runtime lessons, not a verified replacement for our art gate. [PixelART, September19](https://arxiv.org/abs/2609.22789), studies editable RGBA decomposition of design images; it does not demonstrate humanoid gait construction. The dated primary-source scope and availability ledger is `modular-research-BZBZBZ/REPORT.md` under the local case root. No extra local model was installed or tested.

The current retained walk also has a real13-layer LibreSprite project, including actual reusable arms, torso, head, proximal trousers, combined distal-leg cels and a separate support correction. Save/reopen/export preserves alpha and visible RGBA for all16 poses; it does not turn combined distal-leg drawings into a complete hidden-anatomy rig. The native5/64-second clock is restored from the sidecar. Integer editor milliseconds use a balanced78/79ms distribution totaling1250ms, at most0.5ms prefix error; the editor preview is still not the native rational clock. Case: `editable-v7-BVBVBV/README.md` and root check `EDITABLE-ROOT-CHECK.json`. These operations preserve the retained art; its provisional motion rating remains7.5/10.


### Source preservation is different from fixed final visibility

When a near limb moves across a far limb, preserve the far source layer and permit the new foreground occlusion. Do not clip the moving near geometry against every formerly visible far pixel. A retained repair lost38 transformed samples under that mistaken guard; a separate revision explicitly recorded37 new near-over-far intersection pixels while keeping the underlying far source unchanged. Upper-body and unrelated materials remained protected. Newly revealed hidden far anatomy was still unknown; literal background is not proof of its shape. Review that exposure before acceptance. Case: `pose-repair-phase7-CMCMCM/r2`.
