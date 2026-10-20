# Frozen v5 follow-up art review

**Recommendation: keep B and the new settles.** The selected bridges improve decoded swing-leg progression over equal-time v4. I found no demonstrated anatomical regression that warrants reverting B. Lyra scores **7.6/10 overall**; Brann **7.4/10**. These remain useful prototype sets, with human normal-speed acceptance outstanding.

| Character | Drawing | Brief fit | Consistency | Motion | Usefulness | Overall |
|---|---:|---:|---:|---:|---:|---:|
| Lyra | 8.0 | 7.7 | 7.7 | 7.1 | 7.7 | 7.6 |
| Brann | 7.8 | 7.6 | 7.5 | 6.9 | 7.5 | 7.4 |

Drawing and brief-fit scores do not increase. Whole-set gains reflect the altered gait/recovery and two final tab repairs. Untouched clips earn no new art points. Confidence is recorded separately in each `scores.json`; motion confidence is about 0.66–0.67 because this is reconstructed chronology rather than human normal-speed perception. Scores are holistic, not a producer target or arithmetic formula.

## Exact scope and clocks

All nominated v5 atlases/manifests/receipts were hashed; receipts were not used as visual approval. V3's eight frozen source hashes still match. Every first-120 cell in v5 matches v4 exactly; only eight bridge cells 120–127 and their walk selections differ from v4. Against v3, original cells 0–115 remain exact except Brann f24/f26's bounded tab changes. V3's four unused padded cells become settle drawings 116–119.

**Fourteen complete clips per character transfer from v3** by exact selected RGBA sequence plus holds/loop equality: every idle/cast/hurt, plus east/west walk. The ten fresh clips per character are south/north walk, all attacks and all dodges. All changed pairs, wraps, recovery joins and both idle phases were inspected; the full 80 idle/action endpoint joins per character were viewed. There are 24 clips, 128 stored atlas cells, 128 timeline presentations and 116 distinct selected cell IDs per character. Stored alternatives and reused idle/settle cels are not extra unique motion.

Attack's first 0.305 s remains exact, followed by 0.035 s guard + 0.035 s new settle + 0.035 s existing idle, retaining **0.41 s**. Dodge's final 0.055 s becomes 0.0275 s settle + 0.0275 s existing neutral, retaining **0.26 s**. Walks remain eight holds of **56.25 ms**, totaling **0.45 s**. Exact-hold APNGs were decoded/pixel-compared and their actual rational delays checked.

Native/nearest 2× pair sheets, 4× lower-body comparisons, dark teal and light-gray draw-scale sheets were inspected. Draw scale 0.66 is approximated by an 84 px review cell, not engine sampling validation. **I did not perceive continuous normal-speed playback or run a browser, gameplay, effects or export test.** Timed media creation, source-map preservation and root's separate ordinary-input QA earn no art points. This is a disclosed follow-up, not a blind review; the prior v1 incidental general-skill/early-lineage exposure qualification persists.

## Gait B versus equal-clock v4

B supplies a more readable progressive lowering of the swing leg at phases 1/2/5/6 instead of holding essentially extended-contact silhouettes until the passing key. The source boot texture and material remain recognizable, and the pelvis/thigh/ankle connections remain plausible. No gross detached foot, clipped owned boot or foot-role reversal was demonstrated in the selected B cels. This is modest visual chronology credit, not credit for having more frames or preserving texels.

The strongest path caution is **Brann south f120→121→112**: f121 moves the swing leg farther outward before it returns toward the passing position. This can be a valid clearance arc. I have not observed a normal-speed lateral hitch and will not invent one from the offset alone. Keep B for the current prototype; use equal-clock human A/B before claiming the path is polished.

The flagged enclosed alpha spaces were inspected in raw pixels on white/light and dark backgrounds, with separate marked copies. In Brann south f121 and Lyra north f125 they read as **interleg openings between overlapping boots/legs**, not punctures through an ankle or thigh. Thin openings can be enclosed when the front boot overlaps below them. Hole counts vary with alpha threshold and are not an anatomical pass/fail rule. `TOPOLOGY.json` and `bridge-topology-raw-marked.png` preserve the actual diagnostic. No rejected A source or producer mapping was opened.

The **compact, rounder passing boots f112–115 remain unchanged from v3**. They still contrast a little with the long original boots at f121→112, f123→113, f125→114 and f127→115. B improves the approach but does not fix that volume/highlight difference. Some change is foreshortening; it is less intrusive at draw scale. The smallest remaining gait experiment is to match passing boot cuff/width/heel volume and shading to the neighboring poses while preserving the useful passing relationship, then compare the unchanged 0.45 s loops.

## Settles, garments and joins

The new settles provide intermediate arm lowering and stance closure before existing idle. The final attack→idle join now uses the actual idle drawing rather than ending in a broad raised guard. Acting hands remain attached and character identity stays coherent. Dodge reuse is explicit: a shared settle is useful coverage, not a separately authored dodge recovery.

Brann's two exposed south-dodge gold-fork remnants f24/f26 now show the chosen red-orange cloth tab, closing the concrete v3 mismatch. F25 is pixel-identical to v3 and the glove remains intact; the feature is partly occluded there. The tab stays attached through the new f116 and neutral f27. No remaining gold-to-cloth identity change was demonstrated in that dodge sequence.

New settle bodies have minor drawing differences: Brann's f116–119 neckline/trim and cuff shapes are simpler/brighter than some neighboring source poses. This remains recognizably the same costume, not a gross identity break. A source-preserved head does not automatically preserve the rest of the costume; if a flash is perceived in real-time playback, refine only those body details.

**Top concrete recovery polish issue: most of Lyra's dodge head rise still occurs in one switch.** Hair-top y in a fixed x38..91 native crop is south f26→116→27: **24→17→16**; east f54→117→55: **24→17→17**; north f82→118→83: **24→16→18**; west f110→119→111: **25→17→17**. Hands/stance now bridge, but head height does not evenly bridge the crouch. Brann's rise is more distributed, e.g. south **19→16→13**. This is low-to-medium polish, not a rejection of the useful attack settle. Test a direction-specific dodge rise with the same-view head at an intermediate height while keeping the 0.26 s total; do not silently move the attack settle if it needs a different trajectory.

## Evidence and reproduction

- `EVIDENCE.json`: six nominated input hashes, v3/v4/v5 baseline atlas/manifest hashes, every clip's exact comparison and APNG delay/hash ledger.
- `lyra/scores.json`, `brann/scores.json`: independent dimensions, confidence, scope and ranked remaining work.
- `*/{south,north}-v4-v5-gait-2x.png`: equal-clock phase comparisons including wraps.
- `*/{south,north}-lower-v4-v5-4x.png`, `*/bridge-topology-raw-marked.png`: anatomy/negative-space inspection with unchanged registration.
- `*/pairs/*_{walk,attack,dodge}-2x.png`: every current changed-clip adjacency and wrap/diagnostic endpoint.
- `*/pairs/*-joins-native.png`, `*-joins-2x.png`: all idle endpoint joins.
- `*/recovery-2x.png`, `brann/south-dodge-v3-v5-2x.png`: settle and tab changes.
- `*/media/*.png`: exact-hold current APNGs. Nonloop last→first sheets are diagnostic, not a claim of production wrapping.

Run with installed Pillow; all writes stay in this review folder:

```bash
python3 /home/astra/artifacts/emberwake-character-review/v5/build_review.py
python3 /home/astra/artifacts/emberwake-character-review/v5/topology_inspect.py
python3 /home/astra/artifacts/emberwake-character-review/v5/freeze_review.py
```

Frozen v5 six-input fingerprint: `4f1e32a794f89e029cb20776695841020e343fcb8220c50947efbdacd4a6d7d4`.

| Character | Input | SHA-256 |
|---|---|---|
| lyra | atlas.png | `ab6250e483b538a626fa54d4140a4436e7d8e8ebd1ab8ae252e81c09516e0bf1` |
| lyra | animations.json | `70965e15fa670d9b2c004aed9b3dfd5dbeb2df40b667a45f22972ffc2e58b9d7` |
| lyra | receipt.json | `c732023fd9e7ce67c8ab9bf58198926a56adcfe0294574354979af504f2980d8` |
| brann | atlas.png | `1ef38acfc4a45c448fbb79cac35ec13880241eeabb7beb0744ef24f4d85980f9` |
| brann | animations.json | `f1e027c3e04f989645ea18f3de5d4d73a83287cf880439543a5aad3e6e613a02` |
| brann | receipt.json | `d020bb74c29c632018a8fcc6201f286871abfeca1636153801c11cd55c67da6f` |

All nominated v5 and comparison-baseline hashes matched at freeze. Changed pixels or timing invalidate the affected review scope; approval does not silently transfer to later candidates.
