# Three-key source-rig test: late06 rejected

The bounded04/05/06 test fails at06. Moving the same rigid shaft-and-foot master through the hypothesized range makes41 cloth triangles invert. The field minimum determinant is-5.624475. The failed cloth was **not rasterized**;06 is labeled a rejected boot-only diagnostic. No scaling, clamping, pixel fill or smaller amplitude was substituted to make it pass.

Review `strip-final/three-key-256-light.png`; native128 and84 versions are supplied on light, dark and game-green grounds. `06-inverted-field-on-current-reference-5x.png` shows the actual inverted target triangles over the current06 reference. These are construction and anatomy diagnostics, not an animation or a planted-contact demonstration.

All three keys use the exact same278-texel visible boot master from the frozen04 pilot. The master placements are(+8,+8),(-2,-2),(-12,-12), giving extras(+8,+8),(0,0),(-8,-8) relative to the existing distal sole path. The current upper/body source layers for04,05,06 are retained. The same04 cloth master and demonstrated source-field weights are used, with hip vertical registration0,-1,-2 respectively. This is one rigid full-shaft/foot plus continuous cloth representation; it does not exhaust possible articulated motion or new drawings.

| Key | Field | Minimum triangle determinant | Full boot bbox | Upper overlap |
|---|---|---:|---|---:|
|04 extra(+8,+8)|positive|.174741|x54..71,y96..122|0|
|05 extra(0,0)|positive|.337552|x44..61,y86..112|0 boot;1 cloth edge|
|06 extra(-8,-8)|rejected;41 inverted|-5.624475|x34..51,y76..102|1 boot edge|

The first failing source texel is(50,86). Its triangle begins with source vertices(49.5,85.5),(50.5,85.5),(50.5,86.5). The hip-pinned edge becomes(49.5,83.5),(50.5,83.5), while the third point moves to(42.55063,77.87552), crossing above that edge and reversing orientation. The fixed upper/hip and boot cuff have consumed the available continuous cloth span. `06-FIELD.json` retains every source and target triangle, not just this example.

The full boot layer keeps its geometry and RGBA at every placement; that does not mean every texel remains visible.06's boot master texel(51,93),RGBA(87,39,20,255), lies beneath a partial-alpha upper edge at target(39,81). The upper source there is(24,14,9,53). Normal foreground source-over yields the declared new displayed color while both source layers stay exact.05 similarly has one cloth/upper intersection at(54,83). The final strip uses natural alpha composition at these two intersections, rather than restoring old displayed upperRGBA and cutting a translucent hole. All upper displayed pixels outside the declared intersections remain exact.

`*-BOOT-OCCLUSIONS.json` and `*-LOWER-UPPER-OVERLAP.json` retain these literal witnesses. `*-OTHER-LOWER-OCCLUSIONS.json` records where new foreground Q paint covers retained other visible lower paint. Only the visible other-leg source is available; no hidden complete other-leg master or recovered anatomy is claimed. Original Q removal follows retained part/source maps with body ownership excluded, and the exact resulting row owners are serialized in `LITERAL-OLD-PART-OWNERS.json`. No generic color segmentation is used.

04 remains byte-identical to the frozen representative pilot.05 is a construction-feasible intermediate, not independent motion approval.06 has no completed cloth layer and is not a viable pose. The source-color/sample checks, positive04/05 fields and preserved boot pixels cannot override that failure. The prior source and actual-GPU studies remain frozen, and there is no full24/32 bank, editor package, engine change, score, model call or canonical write.

A genuine alternative would need a different articulated part/depth or authored-pose representation: the rigid full shaft-and-foot and single cloth field cannot perform this fold. Missing coverage must be declared as new joint/proximal paint if introduced. This report neither declares animation impossible nor proposes changing gameplay speed.

Portable reconstruction, requiring Python3,NumPy and Pillow:

    python3 -B scripts/build_strip.py --output /absolute/fresh/output

`scripts/audit_strip.py` independently reconstructs the saved final strip from its literal source maps and reports scope/depth witnesses. `strip-proof-v1` preserves the earlier diagnostic that restored old visible upperRGBA at overlap pixels; `strip-final` corrects those two partial-alpha intersections. The field geometry and failed06 result are identical between them.
