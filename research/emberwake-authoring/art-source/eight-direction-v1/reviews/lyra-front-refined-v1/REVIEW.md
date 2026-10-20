# Frozen independent sprite review 5

**Verdict: A 8.0/10; B 8.0/10. Both are strong polished candidates in this still-image scope. No confident A/B preference.** The shared character design and most shared cels dominate the result; the local lower-body differences do not establish a consistent practical advantage at the 84 px game proxy across both directions.

| Category (/10) | A | B | Plausible uncertainty band, either variant |
| --- | ---: | ---: | --- |
| Appearance, materials and anatomy | 8.3 | 8.3 | 7.8–8.7 |
| Temporal identity | 8.2 | 8.2 | 7.6–8.7 |
| Motion readability | 7.7 | 7.7 | 6.7–8.5 |
| Practical game use | 8.0 | 8.0 | 7.2–8.6 |
| Overall | 8.0 | 8.0 | 7.4–8.5 |

These are holistic judgments, not an arithmetic mean or statistical confidence intervals. No target score was supplied. Hashes, successful exports and frame counts earn no art points. The motion and practical-use bands are wider because continuous playback, controller use and physical contact were not observed.

## Independence and exposure

A procedural exposure occurred: while opening supplied context files, I read `context/ACTUAL-IDLE-EXTRACTION.json`, containing source atlas location, atlas/manifest hashes, extraction indices and rectangles. That exceeded the instruction against source provenance. I did not follow any referenced external path. It revealed no A/B method mapping, producer judgment or previous grade. Method blindness remains intact; strict provenance blindness cannot be claimed. The task already identified the diagonal idles as matching project-atlas context, so the metadata added no comparative quality evidence. No producer reports, method mappings, prior scores, skill histories or relevant memories were opened or consulted.

## What was actually inspected

All 32 actual 128×128 RGBA cels: A/B × southeast/southwest × 00–07. Every clip was visually inspected in every supplied sequence sheet and predecessor/current pair sheet at 84, 128 and nearest 256 whole-stage pixels, on light RGB(224,222,209), dark RGB(25,29,39) and flat game RGB(72,86,59). All 72 proof PNGs were viewed. Every pair was covered: 00→01, 01→02, 02→03, 03→04, 04→05, 05→06, 06→07 and wrap 07→00.

Every cel slot in those proofs was also verified as an exact nearest-scaled alpha composite of its nominated actual PNG (864/864 slot matches). This binds the visible proof review to the source cels; it is not aesthetic credit. The appearance reference and all 13 individual context PNGs were inspected, including both supplied matching southeast/southwest idle phases; `southeast-idle22.png` duplicates southeast phase00. Derived context and lower-body inspection composites are retained in `inspection/`.

The 84 px view is a whole-stage proxy, so the actual character is smaller than 84 px tall. The supplied game background is a flat color, not actual game terrain. The static matching diagonal idles support identity/camera comparison only; they do not accept idle↔walk or direction transitions.

## Visible result

**Drawing, material and anatomy:** In both variants and both directions, white hair retains shaded clumps, teal shoulder/clothing volumes remain rounded, gold trim/cuffs separate from the tunic, and warm leather boots remain distinct from the charcoal trousers. Face, hair, collar, shoulder armor, belt/tunic trim and gloved-hand identities remain coherent across 00–07. The large head and compact limbs agree with the supplied character context. Visible wrist and leg attachments are plausible for this style. I found no defensible major anatomical failure, detached limb or material/palette failure. Crisp clusters with soft RGBA shading fit the stated brief; no restricted-palette rule is applied. No conspicuous matte halo or stage clipping appeared on the contrasting backgrounds.

At 84, the bright hair, face and teal/gold costume carry recognition. Fine boot folds and trouser shading compress on dark backgrounds, but the broad lower-body silhouette remains usable. This is a bounded visibility limitation, not evidence of a missing leg. Passing/crossing silhouettes at 03 and 07 legitimately occlude portions of the limbs; an open leg gap or a visible toe is not required.

**Chronology and identity:** Forward boot reach alternates across the two half-cycles, with close/crossing silhouettes around 03 and 07 and broader reach around 00 and 04. Head/torso orientation and arm changes remain coherent with the character. Adjacent leg configurations around 01/02 and 05/06 change less than the following close-to-extended changes around 03→04 and 07→00. That displacement distribution is visible in the sheets; a perceptual hitch at speed remains a hypothesis. The wrap does not exhibit an isolated identity jump or special seam beyond the gait changes seen elsewhere. This is not a claim that normal-speed looping has been perceived.

**A/B evidence:** Cels 00, 02, 04, 06 and 07 are identical between A and B in each direction. Cel01 differs by 873 RGBA pixels per direction, with alpha changes in 490 pixels, inside native x43–85/y83–116. Cel05 differs by 280 RGBA pixels per direction, with alpha changes in 150 pixels, inside southeast x64–84/y84–102 or southwest x44–64/y84–102. These are visible lower-body geometry/shading changes, not merely different holds. Cel03 differs by only two RGB pixels with identical alpha at southeast x66/y101–102 or southwest x62/y101–102. The enlarged local appearances differ, but I cannot defend a consistent whole-cycle winner at the game proxy. Equal scores reflect that limit, not proof that the variants are perceptually identical.

## Timing and motion-perception boundary

`INPUTS.json` declares eight equal holds of **9/160 s = 0.05625 s**. Exactly **8 × 9/160 s = 9/20 s = 0.45 s** per cycle. Reconstructed exposure starts are:

| Cel | Start (s) | End (s) |
| --- | ---: | ---: |
| 00 | 0.00000 | 0.05625 |
| 01 | 0.05625 | 0.11250 |
| 02 | 0.11250 | 0.16875 |
| 03 | 0.16875 | 0.22500 |
| 04 | 0.22500 | 0.28125 |
| 05 | 0.28125 | 0.33750 |
| 06 | 0.33750 | 0.39375 |
| 07 | 0.39375 | 0.45000 |

07 should end at 0.45000 s and 00 resume immediately. These times come from the declared ledger, not measured encoded-video presentation timestamps. The packet contains static PNGs/proofs; no continuous video was supplied or viewed. Motion judgments reconstruct still chronology and declared holds. No human normal-speed playback, human smoothness judgment, controller feel, ground speed or physical support/contact acceptance is claimed. An alpha-bound change or short projected foot reach cannot by itself prove lost contact.

## Smallest justified next experiments

No demonstrated material defect presently justifies a mandatory repaint.

1. **Cadence hypothesis:** For both variants/directions, inspect the exact unchanged 0.45 s loop in a blind human normal-speed comparison at nearest 84 px on the flat game background. Focus on 01→02/05→06 relative to 03→04/07→00. The expected benefit is to determine whether the uneven displacement distribution is actually perceptible. Only if a repeatable hitch is observed should one intermediate cel be isolated for a drawing experiment; stills alone do not justify retiming or repainting.
2. **Dark lower-body visibility:** Put one unchanged exact loop over the darkest intended actual terrain with the existing camera/filter settings. Focus on the tucked/receding boots around 01/02 and 05/06. This checks whether compressed dark material detail affects play. If it does not, preserve the art; if it does, try one localized boot/trouser value adjustment before a broader redesign.

Physical foot planting, intended diagonal translation speed, idle↔walk and direction switching need their own in-game observation. This review does not accept other directions, actions, equipment or characters.

## Frozen input binding

All **122/122** entries in the supplied `SHA256SUMS` and **46/46** image entries in `INPUTS.json` matched at opening and before report creation. The manifest's own hash is recorded here, not claimed to have an external trust anchor. External source-atlas/manifest hashes mentioned by the encountered metadata were not checked because their files are outside the allowed input.

- `INPUTS.json`: `1eea70c8591a2e4d91269d227638f17ee1b42c206f7469b647550ba129ba33ec`
- Input `SHA256SUMS`: `83e6ec353fb1f0763ae262acbfe21c9d9ff30cf420ee4be8a85d56b42195adf4`
- `STYLE.txt`: `66f7aed9c6a47a3e0d7edf17bd51775dc7e19fa2b20826bcee02dcb31bef1555`
- `RUBRIC.md`: `a7d9e49833b4c1387b06bc13d936db11fb91e93aac70a2939f2b4679560aec43`
- A cel-set fingerprint: `4f79db29a80ebc70159cd843192566a0656b7824a5ca47c1b77c221a9c92e727`
- B cel-set fingerprint: `6560d448f749ae12bd6c25fb643fdffddf197ba5283477ed9f0a5aa4689670c1`

Cel-set fingerprints hash concatenated lines of lowercase SHA256, two ASCII spaces, relative PNG path and LF, ordered southeast 00–07 then southwest 00–07; the variant letter is retained in each path. `REVIEW.json` contains the complete verified manifest, exhaustive proof coverage, reconstructed timeline, evidence and exposure disclosure.

Only this new review directory was written. No production edits, provider/model calls, web research or sub-agents were used. Reports and inspection composites are frozen read-only and bound by the adjacent `SHA256SUMS`; that checksum file is also read-only.
