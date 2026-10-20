# Anonymous art review: A and B rear-diagonal walks

Frozen review time: 2026-10-17T05:02:34.541362+00:00. Methods remain unknown. Input: `/home/astra/artifacts/emberwake-lyra-rear-painted-review-v2/input`.

Both sets are good, recognizable small RPG character drawings. I have a **modest preference for A** because its legs are easier to follow at the intended 84-pixel whole-stage proxy. I did not find evidence sufficient to call either set anatomically broken or temporally off-identity. A is my preferred next playback candidate; this is not a claim that it is the smoother animation at real speed.

## Independence and evidence

Only the nominated input packet was read. No target-specific producer reports, prior grades, source provenance, method mappings, skill histories, memory files or parent-folder content were accessed. No accidental target-specific exposure occurred. General inherited workspace/environment instructions were unrelated to the art judgment. No unblinding, external research or sub-agent review was used. The input was never modified.

All **129 frozen ledger entries passed SHA-256 verification**, including all 32 candidate cels, 22 context PNGs, 72 proof PNGs and the three text/JSON documents. The 54 image fingerprints in INPUTS.json also matched. Successful verification establishes which art was reviewed; it earns no art credit.

| Input | SHA-256 |
|---|---|
| INPUTS.json | `ef66a631abe4d7a98dfa08db37502f8c6dab6ad083aec7966741b9fb30bcb4fb` |
| STYLE.txt | `66f7aed9c6a47a3e0d7edf17bd51775dc7e19fa2b20826bcee02dcb31bef1555` |
| RUBRIC.md | `a7d9e49833b4c1387b06bc13d936db11fb91e93aac70a2939f2b4679560aec43` |
| input SHA256SUMS | `d6408fc459bba759e90f76e0121da9b13d2f3e33b5818063529cfb92234ce124` |

Full per-file fingerprints and PNG metadata are in `INPUT-VERIFICATION.json`. Explicit visual coverage is in `COVERAGE.json`.

## Coverage and perception limits

I visually inspected all 72 supplied proof sheets: A and B, northeast and northwest, complete00–07 sequence sheets and every adjacent pair00→01,01→02,02→03,03→04,04→05,05→06,06→07 and07→00; each at native128, intended84 proxy and nearest256 on light, dark and game grounds. I also inspected the supplied appearance, northeast idle, east/north idles and all east/north walk context. The extra context sheets and lower-body crops in this report folder are review aids made from the supplied PNGs, with nearest enlargement and no repainting. Context establishes identity and camera only; it does not certify a transition.

**Motion judgments reconstruct chronology from decoded stills and the known holds. Continuous video perception was unavailable. There was no human normal-speed playback, controller testing or physical foot-contact acceptance.**

Timing evidence is limited to INPUTS.json. All126 PNGs are single-frame images with no embedded animation timing; the packet has no time-bearing media from which to inspect actual presentation timestamps. All eight declared holds are9/160s =56.25ms;8×9/160s =9/20s =0.45s per loop, identically for all four reviewed strips. The checked schedule is:

| Cel | Start (s) | End (s) |
|---|---:|---:|
|00|0|0.05625|
|01|0.05625|0.11250|
|02|0.11250|0.16875|
|03|0.16875|0.22500|
|04|0.22500|0.28125|
|05|0.28125|0.33750|
|06|0.33750|0.39375|
|07|0.39375|0.45000|

The next00 starts at0.45s. These are arithmetically verified manifest holds, not independently observed video timestamps. Distinct cels are not assumed to create equally distinct perceived poses.

## Separate judgments

| Area | A | B |
|---|---|---|
| Appearance | Good rear-diagonal drawing. Broad, readily separated boots and thighs suit the character's compact proportions. | Good recognizable drawing. Tighter and more crossed lower-body silhouettes reduce immediate leg separation. |
| Materials | Silver hair, teal cloth, gold trim, silver bracer and brown boots remain clear, with crisp shaded clusters and acceptable softness. | The same material vocabulary remains coherent. Narrow or tilted boot views do not by themselves demonstrate volume inconsistency. |
| Anatomy and attachment | Visible thighs and boots connect plausibly beneath the tunic; no demonstrated detached limb or impossible joint. | Concealed far-leg joints are unknown.03–05 are harder to parse, but an overlapping leg and lifted heel are plausible explanations. No proven joint failure. |
| Temporal identity | Hair shape/highlights, face sliver, scarf, belt and bracer remain coherent through the whole chronology and wrap. | The same landmarks remain coherent through the tighter passing phases and wrap. No demonstrated identity collapse. |
| Motion readability | A plausible alternating stride can be reconstructed, with more immediately traceable leg masses.02→03 and06→07 are near-held silhouettes that may serve valid support intervals. | A plausible stride can also be reconstructed.03–05 make individual leg roles harder to follow;07→00 keeps a similar extended-leg silhouette. Real-time rhythm remains uncertain. |
| Practical game use | My preferred candidate for the next exact-timing84px playback test. Static drawing and direction are readable on the supplied grounds. | Visually usable candidate with a passing-phase readability concern. It may become clearer in motion; that has not been tested here. |

Both retain recognizable silhouettes on the three grounds. Hair and bracer highlights remain distinct on dark; light shows no conspicuous rectangular matte or broad light fringe. Teal cloth is lower contrast on the green game ground, but trim and silhouette still separate it. Fine scarf folds and trouser details naturally become less explicit at84. I did not penalize retained RGBA softness, color count, or a lack of retro palette purity. I found no obvious off-stage clipping or isolated wrap-only head/costume jump.

## Demonstrated concerns and their limits

**R1: B03–05 compress the leg read (moderate static readability concern).** In both `B/northeast/03.png` through05 and `B/northwest/03.png` through05, the lower body changes from a narrow stem to a bent/crossed boot bundle. The useful native region is approximately x44–84,y78–113, with the crossing central under the hem. Pairs02→03,03→04,04→05 and05→06 show the loss and return of separated boot masses. It is visible at84 on all three grounds and clearer at128/256. Compared with A, it is harder to assign two leg roles instantly.

This is **not proof of a missing limb, detached foot, inverted knee, nonalternating gait or clipping joint**. Far-leg occlusion and heel lift plausibly explain the concealed parts. The smallest useful art experiment is one disposable B03–05 alternative with a small contour or value separation at the visible crossing, preserving timing and legitimate occlusion. Its expected benefit is faster step recognition at84. Keep it only if actual-speed84px comparison improves.

**R2: small pointed shorts-edge contours (low-priority drawing concern).** Examples are `A/northeast/04.png` around x72–85,y79–89 and `A/northwest/04.png` around x42–55,y79–89; also `B/northeast/05.png` around x42–56,y80–89 and `B/northwest/05.png` around x71–85,y80–89. Small sideways dark points make these thigh overlaps more ragged than adjacent rounded contours. The extra native-coordinate crops expose them. They may be intentional cloth folds and mostly merge at84; they are not proof of bad anatomy or a game-blocking defect. An optional one- or two-pixel contour-trimming comparison on those four cels would test whether any cleanup benefits the intended scale.

I found no further defect with enough evidence to make a firm allegation. In particular, I would not infer bad hidden joints from a concealed toe, demand mirrored step silhouettes, or label similar stance poses as accidental duplicate drawings.

## Full pair sweep

Each entry below was checked independently for both directions, at every supplied scale/background combination. Screen-side relationships reverse in northwest.

| Pair | A | B |
|---|---|---|
|00→01|The extended low boot draws closer under the body; opposite boot is more exposed.|Both boot masses remain visible and move toward a more compact stance.|
|01→02|The opposite low leg becomes long and the other boot rises; leg roles remain readable.|A long low shin/boot contrasts with a short lifted boot; stronger silhouette change.|
|02→03|Very similar lower-body silhouette with small changes; a near-held support phase, not an identical drawing claim.|The short lifted boot closes behind the long leg and becomes much less separately legible.|
|03→04|The low boot bends/changes angle while the other boot stays raised; a more compact phase.|The narrow one-stem silhouette becomes a bent/crossed boot shape; hidden far-leg role remains ambiguous.|
|04→05|Boots open into two separate masses beneath the hem; no visible attachment break.|The tight crossing changes angle; lower-body separation remains weak at84.|
|05→06|The other low leg lengthens while its partner lifts; the next half-stride is readable.|The crossing opens into a low straight boot and a raised boot, restoring two leg masses.|
|06→07|Very similar extended-leg silhouettes; may form a deliberate support interval.|The extended boot shifts to a diagonal and the raised boot lowers; plausible continuing stride.|
|07→00|The principal extended boot remains on the same screen side while the other boot changes height/angle. No isolated head/costume snap is apparent.|Similar extended-leg silhouettes bridge the boundary; no isolated identity jump is apparent. Whether the settle is too long needs playback.|

The main remaining performance question is whether those near-held and compressed silhouettes feel rhythmic at56.25ms per cel. A contact sheet cannot settle that. Run both unchanged loops at84, with the exact holds and no interpolation, over several repetitions and a moving-ground reference. That would distinguish a legitimate support dwell from a perceived hitch before changing drawings or exposure timing.

## Scoped verdict

A has a moderate-confidence advantage in static and pairwise leg readability at84. Both sets retain good appearance, materials and identity; neither has a demonstrated catastrophic anatomical defect. Comparative smoothness, human normal-speed readability, controller feel, physical foot contact and transitions remain unaccepted. No numerical score is given because no numerical scale was specified and the available motion evidence does not justify that precision. This review certifies no other direction, action, equipment or changed art/timing.
