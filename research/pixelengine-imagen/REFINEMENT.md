# Source-bound refinement after the first comparison

The target is original ImageGen paint with drawing and useful motion at least
as strong as the retained PixelEngine1.5 reference. **The9/10 target remains
unmet.** Transparency, exact exports and more frames do not establish parity.

Local evidence: `/home/astra/artifacts/pixelengine-imagen-refinement-20261020/`.
It preserves two additional actual ImageGen calls: an eight-key repaint using
the stronger1.5 torso/scarf guide, then two proposed full-body inbetweens.
`requests/` retains literal prompts, ordered input roles and raw/input hashes.
No H3, local generative model or new PixelEngine generation was used. Hosted
models/weights/hidden prompts remain unknown.

## Tested routes

| Route | Result / limit |
| --- | --- |
| Stronger guide | Restores the trailing scarf; no recovered cloth physics |
| Whole-sheet sampling/palette controls | Nearest/BOX and explicit alpha candidates change clusters; no per-pose fitting |
| Bounded palette fit |16/24 colors fail convergence;32 passes; no iteration extension/reseed |
| Owned head + richer body | Stabilizes face;52-color union preserves protected head/alpha/clock |
| Two leg bridges | Source-owned trousers/boots add poses but crowd limbs and hold the upper body |
| Five cloth midpoints |16Hz cloth against8Hz body; improves secondary chronology only |
| Painted bridges + head repair | Head consistency improves; chest/arm/boot volumes still change |
| Genuine client grid | Raw418px eight-source case infers76px; integer staging only; no hosted equality |

First cold reviews found the new drawing comparable at8/10. Later reviews
preferred the reference and rated candidates around7–7.8. Round5 scores are
Reference8.1, stable-head/cloth7.8, native-grid7.6 and head-repaired painted
bridges7.5. Retain this disagreement. These are source-bound static chronology
judgments, **not continuous playback acceptance**. Matte/alpha is separate.

The leg inserts remain experimental. A visible support boot can already be
80–83% through travel at the proposed half-time pose. More boot clearance can
improve a still without fixing its phase. Measure corresponding sole corners,
toe outlines and material edges; declare role/occlusion uncertainty. Controls,
alpha centroids and part-area equality do not prove the visible foot path.
A source-stage linear midpoint is a hypothesis, not world-space ground contact.

## Replay map

Use this repository's existing Pillow/NumPy environment and fresh output paths.
`--help` lists exact arguments; saved artifacts retain the actual source pins,
plans and requests. These scripts replay saved art without provider calls.

| Tool under `tools/` | Operation |
| --- | --- |
| `paint-refinement.py` | Registered sampling/palette controls |
| `author-pixel-candidates.py` | Guarded source-colored edits/native-editor proof |
| `compose-owned-track.py` | Visible ownership and source-attached tracks |
| `component-palette.py` | Palette union with protected head/alpha |
| `compose-tail-midpoints.py` | Tail split/reassembly, witnesses and independent clock |
| `probe-lowerbody-bridges.py` | Two source-map leg bridges and duplicate control |
| `probe-component-head-bridge.py` | Head-height midpoint and explicit neck cap |
| `replace-bridge-heads.py` | Owned head replacement in painted bridge frames |
| `repair-two-leg-slots.py` | Literal trouser clusters and measured distal rotation |
| `combine-owned-tracks.py` | Exact owner reassembly and rational clock union |
| `freeze-art-review.py` | Anonymous frozen comparison using each lane's holds |
| `comparison-video.py` | CFR preview with decoded-frame/PTS checks |
| `native-grid-production.py` | Pinned raw-cell batch replay with explicit52-color policy and integer staging |
| `diagnose-support-trajectory.py` | Visible material/outline probes and one midpoint trial |
| `coordinated-upper-pilot.py` | One source-owned head/collar/torso/arm intermediate with literal seam repair |
| `support-roll-probe.py` | One authored support-boot foreshortening using frozen nearest source samples |

The76px grid case uses [the optional genuine adapter](tools/README.md).
Alpha1–7 is removed and hidden alpha0RGB canonicalized explicitly; RGBA at
alpha>=8 stays exact before processing. Returned pixels are placed at(2,1)
on80px without resizing. These are measured case settings, not defaults.
A new shared-grid batch can alter all keys and cannot inherit prior source-key
preservation claims.

## Verification and open acceptance

Source keys, maps, journals, protected regions, editor and APNG clocks are
checked separately. LibreSprite63/62ms preview holds represent exact62.5ms
ticks retained in the sidecar. Browser checks cover actual Canvas2D pixels,
interior timing samples, stepping and wrap; CFR duplicate exposures are not
additional painted poses. Frozen art reviews inspect every pair/wrap at native
and nearest scales on light/dark backgrounds. Human normal-speed judgment is
still separate. No new candidate is installed in the game or accepted as a
complete character/action library.

Subsequent native-body/stable-head and rebased cloth tests preserve all visible
body and original key pixels. Round6 preferred this hybrid over the earlier
candidate but still preferred the reference; its apparent scarf break was
clarified as connected outline/shadow, not a structural defect. Round7 narrowly
preferred a coordinated-upper/boot-roll test; Round8 preferred the reference
over all candidates (8.3 versus7.5 for the most advanced part-based/cloth test).
No review establishes9/10. The remaining motion issue is the denser250–500ms
quarter against coarser opposite-passing and wrap phases. Get normal-speed
judgment before expanding that bank.

Current local comparison: `http://localhost:8900/delivery/current/`.
It is a human-labelled copy of frozen Round8 pixels, with an exact-CFR
five-second preview at `delivery/current-video/video/preview-exact.mp4`.
Windows localhost access was checked independently; browser rendering/clock
and lossy video transport checks remain separate from art acceptance.

Reusable guidance:
[component-refinement.md](../../skills/imagegen-sprite-animation/references/component-refinement.md).
