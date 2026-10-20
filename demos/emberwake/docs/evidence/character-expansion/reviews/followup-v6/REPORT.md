# Frozen v6 whole-bank art review

**Keep the selected v6 repairs.** Lyra is **7.8/10 overall** and Brann **7.6/10** as complete 24-clip banks. Both are coherent, useful compact-game character sets. The combined changes resolve the specific v5 head-rise, boot-volume and south-chest concerns without a demonstrated new anatomical or patch-seam defect. These are art judgments with limited motion confidence, not runtime acceptance.

| Character | Drawing | Reference/brief fit | Consistency | Motion | Usefulness | Overall |
|---|---:|---:|---:|---:|---:|---:|
| Lyra | 8.0 | 7.7 | 7.9 | 7.3 | 7.9 | 7.8 |
| Brann | 7.8 | 7.6 | 7.7 | 7.0 | 7.7 | 7.6 |

Drawing and reference-fit scores stay fixed. The gains concern only the selected repair pixels and their clip contexts; untouched art does not score higher. Overall is holistic, not an arithmetic formula or a requested threshold. Overall confidence is 0.78 Lyra / 0.79 Brann; motion confidence is 0.68 / 0.69.

## Exact coverage and transfer

All 48 current clips are represented in native, nearest 2× and approximate 0.66 draw-scale sheets, every adjacent pair and wrap/diagnostic endpoint, both idle-phase endpoint joins, and exact-hold APNGs. I inspected all eight current direction sheets at native and draw scale, all ten changed complete clips' 2× pairs, four changed walk wraps, the new recovery triples, light-background ankle/negative-space and neck details, and eight changed walk-to-idle endpoints. Unchanged pair/clip coverage transfers from the frozen v5 review only after exact selected RGBA sequence plus holds/loop equality.

- **Lyra: 18 complete clips transfer; six are fresh:** south/north walk and all four dodges.
- **Brann: 20 complete clips transfer; four are fresh:** south/north walk, south attack and south dodge.
- All **first 128 cells remain byte-identical as decoded RGBA** to v5. All **13 appended repair cells exactly match** the previously preferred narrow candidate PNGs.
- **76 of 80 idle/action endpoint joins per character transfer exactly.** Four changed endpoints per character are the new south/north walk final passing pose into each idle phase; these were freshly inspected. The new internal recovery joins do not change the other idle endpoints.
- Lyra stores 136 nonempty cells; Brann stores 133 nonempty cells in a 136-slot atlas, with three transparent padding cells. Both have 128 timeline presentations. Lyra selects 120 distinct IDs; Brann 116. Appended storage is not extra unique motion credit.

The v5 atlas/manifest/receipt hashes still match that review's frozen ledger. Cell size, pivot, draw scale, cast-hand points and release index are unchanged. All clip holds/loop flags match v5. Walk remains 0.45 s (8 × 56.25 ms), attack 0.41 s, dodge 0.26 s, cast 0.50 s, hurt 0.29 s and idle 1.16 s. Each generated APNG was decoded against the actual selected pixels and checked for its exact rational presentation delays.

## Combined pixels in their clip contexts

**Lyra dodge:** south f26→128→27, east f54→129→55, north f82→130→83 and west f110→131→111 now distribute the visible head rise more evenly. Fixed-crop hair alpha tops are respectively **24→20→16, 24→20→17, 24→20→18 and 25→21→17** native y. The same head scale, hair silhouette and identity remain recognizable. The lower head reads as a short tuck into the scarf/shoulder area; I found no old-head ghost, exposed clear patch, broken neck or new shoulder seam on either background. Attack f116–119 remain unchanged. This is useful chronology improvement, not a claim that 27.5 ms of settling is perceived smoothly in real time.

**Passing boots:** the exact new adjacency groups are Lyra south **121→132→4**, **123→133→0** (wrap), north **125→134→61**, **127→135→56** (wrap); Brann south **121→129→5**, **123→130→0** (wrap), north **125→131→61**, **127→132→56** (wrap). Front toe mass and darker rear heel/sole shading now agree better with neighboring boots, especially Brann north. They no longer read as conspicuously small, rounded bright boot ends at the passing keys. Some size change remains legitimate foreshortening. Cuffs/ankles/thighs stay attached and pelvis registration is unchanged; no detached sole, owned-boot clipping or visible pasted edge was demonstrated. Thin light negative spaces in the bridge phases still read as interleg openings, not punctures through a leg. The changed walk-to-idle endpoints preserve material identity while changing from a narrow stride to the wider idle stance.

The lower-leg path and clock before those keys are unchanged. Brann south **f120→121→129** still takes an outward clearance path before closing into passing. That is anatomically plausible in these stills. I have not perceived a normal-speed lateral hitch and do not recommend a revert based on the offset alone.

**Brann chest:** south attack **13→128→14** and dodge **26→128→27** retain the useful arm lowering while reducing the old settle's large bright Y/long central gold strip toward idle's smaller fastening/trim vocabulary. Blue chest shading remains rounded; no conspicuous polygon boundary or volume collapse is visible. Head, limbs and the repaired red-orange waist tab remain coherent. This is a local improvement, not approval of all costume details by provenance.

## Whole-set judgment and remaining work

The modern chibi treatment, character identity, top-down cardinal camera and material palette remain coherent across each bank. Lyra's silver hair/teal scarf/green coat and Brann's dark hair/navy/gold armor are readable at reduced scale. Unarmed attack, hurt, dodge and open-hand casting remain distinguishable. The transferred cast drawings still show attached acting hands and open palms at release; no new spell/effect alignment or gameplay assertion is made. Brann west remains the disclosed symmetric east mirror, not independent pose coverage or eight-direction art.

Minor rendering variation persists between original poses and some existing settle bodies, e.g. **Lyra and Brann east f41→117→42, west f97→119→98**: glove/cuff/trim shapes become smoother or broader in the settle and more textured in idle. They remain the same costume, and pose angle can explain part of the difference. I do not have a strong preference for further pixel surgery from this evidence; a claimed real-time flash would need actual playback confirmation. There is no demonstrated large remaining anatomical defect to nominate merely to justify a score below 8.

The highest-value remaining step is **human normal-speed, equal-scale review** of the supplied 0.45 s walks and 0.26 s dodge recoveries. For Lyra, check the north/west recovery triples above; for Brann, check the south clearance path and wraps. If those are acceptable, retain v6 rather than produce cosmetic variants. If a flash or hitch is actually observed, isolate that exact pair/feature and preserve the current useful support/passing relationships. I am not certifying final animation polish from still chronology alone.

## Limits, evidence and reproduction

This is a disclosed follow-up, not a cold blind review. The v1 incidental general-skill/historical-anecdote and early-lineage exposure qualification persists. I did not consult another review, producer score or rejected comparison source, and did not communicate with the separate cold reviewer before this freeze. Receipts were hashed only; preservation, replay and root's separate browser/input checks earn no art points.

**No continuous normal-speed visual perception, browser, gameplay, spell behavior, controller feel or export validation occurred here.** Motion judgments reconstruct decoded chronology with exact known holds. The 84 px nearest review cell approximates draw_scale 0.66; it does not validate engine sampling. No new reference image was introduced; reference-fit remains fit to the supplied style/camera brief and prior reviewed candidate, not a new reference comparison.

`EVIDENCE.json` records every clip, comparison, delay, source hash and preferred-PNG match. `*/pairs/*-2x.png` includes actual current adjacency and wraps; nonloop last→first is labeled diagnostic. `*/{south,north}-v5-v6-gait-2x.png` and `*-lower-v5-v6-4x.png` preserve registered before/after comparisons. `*/changed-idle-endpoints-2x.png`, `lyra/head-neck-joins-light-4x.png`, `*/lower-negative-spaces-light-4x.png` and recovery comparison sheets show the bounded checks. `*/media/*.png` are exact-hold APNGs. Per-character scores/confidence are in `*/scores.json`.

All writes are confined to this v6 review folder. Commands with installed Pillow:

```bash
python3 /home/astra/artifacts/emberwake-character-review/v6/build_review.py
python3 /home/astra/artifacts/emberwake-character-review/v6/details.py
python3 /home/astra/artifacts/emberwake-character-review/v6/freeze_review.py
```

Eight-input fingerprint: **`ee1476d39b69e89045c63f23b8e8e7584fce348d767b004d70654fe7f5af9ca1`**.

| Character | Nominated input | SHA-256 |
|---|---|---|
| lyra | atlas.png | `f177d69482bac4c4a6c1c171e5679e5da1c1c45fa11fbf6b56a0fbf4f5fae901` |
| lyra | animations.json | `70b8de14097ecb82ba0ff9aec2d92e1c965c67f8010fbeffa82b50236658123f` |
| lyra | BAKE-RECEIPT.json | `2043934dc3b3dd39dec641dff2171d7973be74da23e0158615a798aa9e8cf257` |
| lyra | GAIT-REPAIR-RECEIPT.json | `3e929f36062280c99438dc2daad8a1b427701995320691b082201719af76f3ba` |
| brann | atlas.png | `69dd1bf4061ee0f7c740bb6f2f9ec44166f13ca8d651293aa5e23b003d6451f4` |
| brann | animations.json | `2c9d6d1212eba569c8d705851a129180b633aaeccf2eac643c30acb964f35921` |
| brann | BAKE-RECEIPT.json | `254e8c94fea46ca326424c3a821ef057f64eb338462c0c56b8f7fcd7e7865b3a` |
| brann | GAIT-REPAIR-RECEIPT.json | `d874df2604e6cfd99c652fea5893c456e16a8993304882018721886e9f2503a8` |

`VERIFICATION.json` binds the report and scores to the source hashes at freeze. Later changed pixels or holds require new affected-scope review; this result does not silently transfer.
