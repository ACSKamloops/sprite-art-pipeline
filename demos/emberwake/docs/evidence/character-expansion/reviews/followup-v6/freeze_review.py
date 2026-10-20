from pathlib import Path
import hashlib,json,datetime
OUT=Path(__file__).resolve().parent
ROOT=Path('/home/astra/projects/emberwake-demo/art-source/characters-v2')
e=json.loads((OUT/'EVIDENCE.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
head={'south':{'frames':[26,128,27],'alpha_top_y':[24,20,16]},'east':{'frames':[54,129,55],'alpha_top_y':[24,20,17]},'north':{'frames':[82,130,83],'alpha_top_y':[24,20,18]},'west':{'frames':[110,131,111],'alpha_top_y':[25,21,17]}}
(OUT/'HEAD-MEASUREMENTS.json').write_text(json.dumps({'measurement':'Alpha>128 within fixed native x38..91, y12..41; source cells, no independent recentering','lyra_dodge':head},indent=2)+'\n')
for n,ss,cc in [('lyra',[8.0,7.7,7.9,7.3,7.9,7.8],[.85,.68,.84,.68,.79,.78]),('brann',[7.8,7.6,7.7,7.0,7.7,7.6],[.85,.68,.86,.69,.80,.79])]:
 dims=['drawing','reference_fit','consistency','motion','usefulness','overall']
 d={'character':n,'version':'bake-v6','scale':'0 to 10; holistic overall, not an arithmetic mean','scores':dict(zip(dims,ss)),'confidence':dict(zip(dims,cc)),'input_fingerprint':e['input_fingerprint'],'input_hashes':e['input_hashes'][n],'scope':{'full_set_clips':24,'directions':['south','east','north','west'],'actions':['idle','walk','attack','cast','hurt','dodge'],'fresh_complete_clips':e['comparison_v5'][n]['fresh_clips'],'exact_transfer_complete_clips':e['comparison_v5'][n]['transfer_clips'],'unchanged_idle_endpoint_joins':76,'fresh_idle_endpoint_joins':4,'stored':e['counts'][n]},'assessment':'Keep the selected v6 repairs; coherent and useful compact-game art. No new anatomical defect or patch seam demonstrated. Full normal-speed motion polish remains unverified.','score_rationale':'Drawing and reference-fit scores remain fixed. Consistency and practical use improve only for the selected repairs. Motion improvement is limited to visible chronology/readability, not source preservation or runtime QA.','remaining_priorities':[{'priority':1,'kind':'human playback uncertainty, not a demonstrated defect','target':('Lyra all four dodge recovery triples, especially north f82>130>83 and west f110>131>111' if n=='lyra' else 'Brann south_walk f120>121>129 and loop f130>0'),'action':'Use the unchanged-clock media in a real-time equal-scale comparison before commissioning further pixels. The still evidence supports keeping v6; no timed hitch is claimed.'},{'priority':2,'kind':'minor rendering variation; no repair currently required','target':('Lyra east_attack f41>117>42 and west_attack f97>119>98' if n=='lyra' else 'Brann east_attack f41>117>42 and west_attack f97>119>98'),'action':'If a brief cuff/trim rendering flash is confirmed in playback, refine only that demonstrated feature. Do not broadly redesign stance or recolor intact clips.'}],'limits':['Decoded still chronology and known exact holds; no continuous normal-speed human perception.','No browser, gameplay, spell behavior, export or controller-feel validation.','84-pixel nearest review cell approximates draw_scale 0.66; engine sampling is not tested.','Follow-up reviewer with disclosed v1 incidental general-skill/early-lineage exposure; not a cold blind review.','No communication with the separate cold reviewer before freeze.'],'frozen_at_utc':now}
 (OUT/n/'scores.json').write_text(json.dumps(d,indent=2)+'\n')
rows='\n'.join(f'| {n} | {fn} | `{v}` |' for n,files in e['input_hashes'].items() for fn,v in files.items())
report='''# Frozen v6 whole-bank art review

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

Eight-input fingerprint: **`FINGERPRINT`**.

| Character | Nominated input | SHA-256 |
|---|---|---|
ROWS

`VERIFICATION.json` binds the report and scores to the source hashes at freeze. Later changed pixels or holds require new affected-scope review; this result does not silently transfer.
'''.replace('FINGERPRINT',e['input_fingerprint']).replace('ROWS',rows)
(OUT/'REPORT.md').write_text(report)
verification={'frozen_at_utc':now,'input_fingerprint':e['input_fingerprint'],'source_files':{},'baseline_v5_files':{},'v5_review_unchanged':{},'review_files':{}}
for n,files in e['input_hashes'].items():
 for fn,h in files.items():
  actual=sha(ROOT/'bake-v6'/n/fn);assert actual==h
  verification['source_files'][f'{n}/{fn}']={'sha256':actual,'matches_initial':True}
for n,files in e['baseline_hashes'].items():
 for fn,h in files.items():
  actual=sha(ROOT/'bake-v5'/n/fn);assert actual==h
  verification['baseline_v5_files'][f'{n}/{fn}']={'sha256':actual,'matches_frozen_v5':True}
oldreport=OUT.parent/'v5'/'REPORT.md';assert sha(oldreport)=='4b2223cb233b1e7fc8b55ba88232f0fddbe3c58c85198fcb73b385a9948f212a'
verification['v5_review_unchanged']['REPORT.md']=sha(oldreport)
for p in sorted(OUT.rglob('*')):
 if p.is_file() and p.name not in ['VERIFICATION.json','OUTPUT.sha256']:verification['review_files'][str(p.relative_to(OUT))]=sha(p)
(OUT/'VERIFICATION.json').write_text(json.dumps(verification,indent=2)+'\n')
(OUT/'OUTPUT.sha256').write_text(''.join(f'{sha(p)}  {p.relative_to(OUT)}\n' for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='OUTPUT.sha256'))
print(json.dumps({'report_sha256':sha(OUT/'REPORT.md'),'input_fingerprint':e['input_fingerprint'],'files_hashed':len(verification['review_files']),'scores':{n:json.loads((OUT/n/'scores.json').read_text())['scores'] for n in ['lyra','brann']}},indent=2))
