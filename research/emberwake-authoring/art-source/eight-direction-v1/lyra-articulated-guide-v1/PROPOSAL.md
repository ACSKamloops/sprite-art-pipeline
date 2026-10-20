# One articulated06 source-layout and pose guide

The reviewable proposal is `guide-final/source-and06-guide-256-light.png`, with native128 and84 versions on three grounds. `06-joint-foot-detail10x.png` shows the authored joint controls and fixed distal paint. This is a **guide**, not a finished sprite or a valid animation pose. No shaft/thigh texture or new joint paint has been synthesized.

The prior failed strip demonstrated a limit of one rigid full shaft-and-foot plus one continuous cloth field. This proposal instead separates three current04 visible source owners:

| Part | Literal source pixels | Proposed constraint |
|---|---:|---|
| Charcoal thigh/knee |167|Independent proximal part; may rotate/foreshorten and overlap calf. |
| Leather shaft/calf |142|Separate part with its own knee/ankle controls; may change projection and visibility. |
| Distal toe/sole |136|Protected source paint, rigid translation for this06 guide. |

The source parts are disjoint and reconstruct the entire existing445-pixel visible Q owner. Each source cutout, owner mask, native row guide and exact sourceRGBA sample is retained. The split between source rows104/105 is an **authored paint-owner boundary**, not a recovered anatomical ankle or proven boot seam. The irregular upper leather wrap may need further owner refinement or new coverage when articulated. Complete boot geometry is explicitly **not** invariant in this method; only the136 distal texels carry the protected-paint constraint.

For the representative06 guide, the distal part moves(-12,-12) from current04, matching the prior06 extra(-8,-8) sole target. The heel-paint witness is(41,101), forefoot(49,102), and the full protected distal part retains exact sourceRGBA. Its source shape stays unchanged. Current06 upper/identity paint is exact and remains foreground. The other visible leg is retained; hidden complete other-leg anatomy is not claimed.

The authored controls are hip H=(58,83), knee K=(52,92), ankle A=(43,93). H is a control below the current hem; the real hip is hidden. K and A are pose-design controls, not detected skeleton joints. The target thigh and calf control lengths are10.8167 and9.0554 native pixels. The source control proxies H=(58,85),K=(57,96),A=(55,105) are retained for a later part projection, without claiming they recover source anatomy.

The calf lies mainly behind the thigh/knee, with the distal toe/sole over its ankle end. This allows overlap and foreshortening instead of folding a flat cloth field through the torso. The proposed depth order, back to front, is:

1. Retained current06 other visible leg.
2. Separately articulated leather shaft/calf.
3. Protected distal toe/sole.
4. Charcoal thigh/knee over the proximal calf.
5. Unchanged torso, arms and gloves.

Cyan and orange target regions are annotations for those separate parts, not transformed source texture. The current guide therefore does not prove that the available142 leather or167 charcoal pixels can cover those regions convincingly. That is the next art/part-construction question. It also does not prove contact at158px/s or a complete support/swing schedule.

Yellow marks candidate **new** coverage near knee and ankle:44 knee coordinates and25 ankle coordinates, overlapping at2, for67 unique guide coordinates. The exact masks exclude protected distal paint, actual current upper ownership and the retained other visible leg. These are bounded proposal regions, not a determination that every coordinate is missing, a blanket fill, or authorization to conceal mapping losses. No sprite pixels have been authored there. Any future coverage must be declared as new joint/proximal paint, not recovered hidden anatomy.

`PROPOSED-JOINT-COVERAGE.json` records actual same-view charcoal and leather palette witnesses with source coordinates. Charcoal donors are checked against the charcoal owner, leather donors against the boot owner. They guide future shading; no new colors or hidden structure are inferred from them. An ImageGen or hand-painted completion would require this guide to be reviewed first, followed by a separately bounded art task. No model call was made.

Actual protected owners are saved as masks, including all alpha-positive current06 body pixels. Diagram overlays are excluded from the upper and distal protected masks, and both retain exactRGBA. The retained source cutouts and literal source/target witness list make the proposal inspectable without trusting a generic color classifier. The registration remains128×128, pivot(64,112), draw scale.66. There is no pose recentering, stage scaling, full loop, exposure-count change, engine/editor change, score or canonical write.

Portable guide reconstruction with Python3,NumPy and Pillow:

    python3 -B scripts/build_guide.py --output /absolute/fresh/output

The command reads retained local inputs only, verifies their hashes, exports the source split, places the protected distal pixels and reconstructs the annotated guide and JSON. `guide-v1` is an internal draft superseded by `guide-final`: the final version explicitly uses body alpha ownership and corrects one palette donor's material assignment. The joint/foot controls and single proposal did not change.
