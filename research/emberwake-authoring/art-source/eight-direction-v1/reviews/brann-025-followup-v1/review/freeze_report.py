from pathlib import Path
import hashlib,json,datetime
ROOT=Path('/home/astra/artifacts/emberwake-brann-025-followup-review-v1');INP=ROOT/'input';OUT=ROOT/'review';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
before=json.loads((OUT/'input-hashes-before.json').read_text());m=json.loads((INP/'INPUTS.json').read_text());es=[e for v in m['variants'].values() for seq in v.values() for e in seq]+m['context'];rs=[]
for e in es:
 h=hashlib.sha256((INP/e['path']).read_bytes()).hexdigest();assert h==e['sha256'];assert h==next(x['sha256'] for x in before['images'] if x['path']==e['path']);rs.append({'path':e['path'],'sha256':h})
assert len(rs)==65;mh=hashlib.sha256((INP/'INPUTS.json').read_bytes()).hexdigest();assert mh==before['manifest_sha256']
with (OUT/'input-hashes-after.json').open('x') as f:json.dump({'utc':now,'count':65,'all_match':True,'all_unchanged':True,'manifest_sha256':mh,'images':rs},f,indent=2);f.write('\n')
A={'appearance':7.5,'identity':8.5,'motion_readability':7.5,'game_usefulness':7.5};B={'appearance':7.0,'identity':8.5,'motion_readability':7.5,'game_usefulness':7.0}
A_pairs={
'00->01':'Carried coherent small tuck/lift, P forward/Q back.',
'01->02':'Carried P retraction/narrowing while Q stays tucked.',
'02->03':'Carried brisk Q recovery despite improved rounded boot/upper; joined old03 shape remains useful.',
'03->04':'Carried coherent alternate support with substantial Q boot and overlapping feet.',
'04->05':'Carried plausible Q retraction/P rear visibility, some merged brown mass.',
'05->06':'Carried broad Q lower-boot volume.',
'06->07':'Carried improved shorter P shin/reduced sole-pitch jump, though one-hold reveal remains substantial.',
'07->00':'Carried improved P-forward/Q-rear closure and less roll/flattening.'}
B_pairs={
'00->01':'Same old00->01 drawings, holds and start times.',
'01->02':'Same old01->02 entry; old02 now holds28.125ms.',
'02->03':'Old02->newmid: Q moves down/forward into an intermediate boot position, but new horizontal under-cuff slit weakens continuous thigh/cuff attachment. Body remains the old02 upper pose.',
'03->04':'Newmid->old03: a plausible positional bridge into broad old03 boot, but the new cuff opening disappears again and remaining change occurs over28.125ms. No observed normal-speed smoothness gain.',
'04->05':'Same old03->04 support exchange, original key times unchanged.',
'05->06':'Same old04->05 retraction and overlapping boot mass.',
'06->07':'Same old05->06 broad-boot exit.',
'07->08':'Same improved old06->07 shin/sole transition.',
'08->00':'Same improved old07->00 closure; no new closure defect introduced by the inserted exposure.'}
report={
'actor':'brann','review':'02.5 drawing plus split-hold whole-loop follow-up, one frozen judgment','frozen_utc':now,
'anchor':{'A_equals_prior07_followup_B':True,'verified_hash_matches':16,'source':'Own prior07-followup B hash values/scores from earlier conversation; no prior files/reports reopened.','A_scores_carried_without_rerating':A,'all_original16_PNGs_preserved_in_B':True,'B_new_exposure_index':3,'B_new_drawing_label':'mid02.5','B_old03_to07_indices':[4,5,6,7,8],'evidence':'anchor-and-image-map.json'},
'sources':'Only this packet\'s65 nominated PNGs, INPUTS.json and clock, plus own anchor values already in conversation. No producer docs/maps/history/source, project source, other reports or skills.',
'coverage':{'walk_exposures_inspected':34,'A_cyclic_pairs_per_view':8,'B_cyclic_pairs_per_view':9,'total_cyclic_pairs_inspected':34,'includes_A07to00_and_B08to00':True,'contexts_identity_only':31,'scales':['native128','nearest2x256','nearest84 proxy at0.66','extra bilinear84 ground row'],'grounds':['light','dark','diagnostic green grid'],'diagnostic_sheets':25,'local_checks':'02/mid/old03 lower detail, light/dark/alpha, plus exact local alpha samples.'},
'hashes':{'before65_match':True,'after65_match':True,'all65_unchanged':True,'INPUTS_json_unchanged':True},
'clock_verification':{'A_holds_source':'holds default:8x9/160','B_holds_source':'variant_holds.B override, normalized18/320=9/160 except9/320 atindices2,3','B_holds_ms':[56.25,56.25,28.125,28.125,56.25,56.25,56.25,56.25,56.25],'B_starts_ms':[0,56.25,112.5,140.625,168.75,225,281.25,337.5,393.75],'both_loop_ms':450,'all_original_key_start_times_fixed':True,'only_old02_hold_split':True,'evidence':'exact-timing-and-index-map.json','earns_art_points':False},
'limits':['Static exposures/chronological/cyclic sheets only. No observed normal-speed continuous human playback is claimed.','The new drawing is held28.125ms, not56.25ms. Static strips cannot certify how much it is perceived or whether it reduces timed jerk.','No engine, world translation, root speed or physical foot-lock/contact testing occurred. Diagnostic grounds are contrast backgrounds, not contact planes.','Normal depth overlap, differing sole Y and inter-leg negative space are accepted. Not every transparent pixel is a drawing defect.','Scores describe inferred drawing/chronology/game utility with moderate confidence; actual-speed smoothness and world contacts remain unverified.'],
'scores':{'A':A,'B':B},'score_delta_B_minus_A':{'appearance':-0.5,'identity':0.0,'motion_readability':0.0,'game_usefulness':-0.5},
'direction_scores':{'A':{d:A for d in ['southeast','southwest']},'B':{d:B for d in ['southeast','southwest']}},
'preference':{'variant':'A','strength':'prefer as supplied; B positional idea useful but drawing needs repair','confidence':'moderate from static drawings, no timed human validation','reason':'B provides a meaningful intermediate Q boot position, but introduces a horizontal under-cuff background slit that weakens the recovering leg join. Added exposure/correct clock do not compensate for the drawing defect or establish timed smoothness.','baseline_not_rerated':True,'no_extra_exposure_or_clock_bonus':True,'why_motion_ties':'Positional bridging is offset by weaker attachment and unverified28.125ms perception; no whole-loop motion gain is established.','why_game_drops':'New contrast-dependent joint break needs art cleanup before replacing a previously coherent baseline.'},
'foot_key':{'P':'Boot lower/forward atold00:screen-right in SE,screen-left in SW; tracked through pant/cuff and cycle, not relabeled by screen side.','Q':'Other boot initially tucked behind, recovering betweenold02 andold03. Newmid attempts to bridge this Q recovery.'},
'local_findings':{'positive':'Q boot moves to a plausible intermediate down/forward position and remains recognizably brown/chunky. P front boot and the unchanged upper body retain identity/volume. This is a useful drawing intent beyond mere exposure count.','body':'Newmid reuses old02 upper-body pose; no added body/arm weight cue. That is acceptable for a short in-between, but earns no weight-response gain.','primary_defect':'At the recovering Q cuff/knee, a horizontal enclosed background slit is visible on light/ground and alpha. It makes the boot/calf appear incompletely joined to its pants above, rather than just providing separation between two legs. No claim of a completely detached boot is made.','slit_coordinates':{'SE_xy':[[53,90],[53,91],[54,90],[54,91],[55,90],[55,91],[56,91]],'SW_xy':[[72,91],[73,90],[73,91],[74,90],[74,91],[75,90],[75,91]],'all_alpha':0},'negative_space_boundary':'Larger neighboring inter-leg transparent region is not automatically counted as a defect. The judgment targets the visible horizontal slit under Q cuff, not total alpha-hole count.','old_anchor_alpha':'Old02 already has a few tiny alpha openings; baseline is not rerated. Newmid enlarges/repositions a more conspicuous under-cuff break; old03 is joined through this region.','volume':'Toe/heel mass is usable, but continuous knee/cuff/calf volume is not retained cleanly because of that opening. No broader face/armor identity loss.'},
'cyclic_pair_observations':{'A':{d:A_pairs for d in ['southeast','southwest']},'B':{d:B_pairs for d in ['southeast','southwest']}},
'unchanged_limits':['Modest hip/shoulder weight response remains.','Dark hair/pants/rear-boot separation remains weaker on dark ground.','Previously improved old06->07 andold07->00 remain unchanged; inserting mid does not fix or invalidate those earlier results.'],
'minimum_meaningful_repair':'Reconnect the newmid Q knee/cuff/calf across the horizontal slit using coherent pants/boot volume and shading. Preserve legitimate inter-leg clearance and the useful intermediate toe/heel position. Do not fill every alpha gap indiscriminately. No art mutation or additional trial is performed in this review.',
'evidence_files':['local-alpha-hole-evidence.json','new-drawing-scope.json','exact-timing-and-index-map.json'],
'freeze_policy':'One frozen comparison; unchanged baseline not rerated and no target chasing.'}
md=f'''# Brann 02.5 whole-loop follow-up

Frozen once at {now}. **Prefer A as supplied.** B adds a useful intermediate boot position, but a visible horizontal background slit under the recovering cuff weakens attachment. Correct timing and an extra exposure do not establish an art or timed-smoothness improvement.

| /10 | A: carried frozen baseline | B |
|---|---:|---:|
| Appearance | 7.5 | 7.0 |
| Identity | 8.5 | 8.5 |
| Motion readability | 7.5 | 7.5 |
| Game usefulness | 7.5 | 7.0 |

A was **not rerated**. All 16 A hashes match my last 07-follow-up B; all 16 original drawings are preserved in B. Motion ties because positional bridging is offset by the weaker new join and unverified perception of its short hold. Appearance/usefulness drop modestly because that drawing requires cleanup. These are inferred static judgments, not observed playback scores.

## Mapping and actual clock

B uses `variant_holds.B`, not the default eight-entry hold list. Its 18/320 entries equal 9/160; only old02's hold is split into two 9/320 exposures. Both loops remain 450 ms and every original key starts at its previous time.

| B file index | Drawing | Start ms | Hold ms |
|---|---|---:|---:|
| 00 | old00 | 0 | 56.25 |
| 01 | old01 | 56.25 | 56.25 |
| 02 | old02 | 112.5 | 28.125 |
| 03 | new mid02.5 | 140.625 | 28.125 |
| 04 | old03 | 168.75 | 56.25 |
| 05 | old04 | 225 | 56.25 |
| 06 | old05 | 281.25 | 56.25 |
| 07 | old06 | 337.5 | 56.25 |
| 08 | old07 | 393.75 | 56.25 |

Verified with exact fractions in `exact-timing-and-index-map.json`. This clock correctness and preservation earn no art points.

## Evidence and limits

Only this packet's 65 PNGs/INPUTS.json and clock were read; own anchor hashes/scores were already in the conversation. No prior files/reports, producer docs/maps/history/source, project source or skills were read. All 65 input hashes match before/after; images and INPUTS.json remain unchanged.

All 34 exposures and 34 cyclic pairs were inspected: A has eight per view, B nine per view, including A07→00/B08→00. Coverage is SE/SW at native128, nearest2× and nearest84 proxy of0.66, on light/dark/diagnostic green backgrounds, with extra bilinear84 and local alpha detail in25 bounded diagnostic PNGs. Context supports identity/facing only.

**No observed normal-speed continuous human playback occurred.** The new pose lasts28.125ms, so equally spaced stills cannot certify its perceptual visibility or timed smoothness. No engine, world translation, root speed or foot-lock/contact test occurred. Backgrounds are contrast diagnostics, not contact planes. Scores have moderate static-evidence confidence; actual-speed smoothness and world contacts remain unverified.

## Recovery drawing and attachment

P is lower/forward at old00 (screen-right inSE, screen-left inSW), traced through cuff/cycle rather than current side. Q starts tucked behind and recovers between old02 and old03.

Newmid moves Q down/forward to a plausible intermediate boot position. Toe/heel mass remains chunky, P retains its front boot, and the head/torso/arms retain old02's pose. Reusing that upper pose is acceptable for a short in-between but adds no new weight cue. The proposed positional bridge is useful in principle.

The problem is a **horizontal enclosed transparent slit immediately under Q's cuff/knee**, visible on light/ground and alpha views: SE x53–56,y90–91, SW x72–75,y90–91 (seven alpha-zero pixels in each view; exact samples in `local-alpha-hole-evidence.json`). It weakens continuous pants→cuff→calf reading. The count locates the defect; the visible join drives the judgment. I do not claim the whole boot is completely detached.

The larger neighboring transparent space between the two legs can be legitimate clearance and is not automatically treated as an error. Old02 also contains a few tiny alpha openings; A stays at its frozen score. The newmid makes the under-cuff break more conspicuous, while old03 is joined through that region.

## Full cyclic chronology

A retains all eight previously judged pairs. B00→01 and01→02 are the same original entry; B02→03(old02→mid) gives the intermediate position with a weak cuff join; B03→04(mid→old03) restores a joined larger boot after another28.125ms. B04→05,05→06,06→07,07→08 and08→00 are old03→04,04→05,05→06,06→07 and07→00, with unchanged drawings and key times. All were inspected in both facings. Prior closure/07 improvements remain; the new exposure does not improve unrelated pairs.

Modest upper-body weight response and dark-ground hair/pants/rear-boot contrast remain unchanged.

## Smallest meaningful repair

Reconnect newmid's Q knee/cuff/calf across the horizontal slit with coherent volume and shading, preserving legitimate inter-leg clearance and the useful intermediate toe/heel position. Filling every alpha gap would be inappropriate. No images were edited and no additional trial is performed here. This is one frozen judgment.
'''
# Normal word/number spacing for prose only.
import re
md=re.sub(r'\b(in|per|under|after|another|lasts|native|nearest|proxy of|detail in|has|B|A)(?=\d)',r'\1 ',md)
for name,content in [('report.md',md),('report.json',json.dumps(report,indent=2)+'\n')]:
 with (OUT/name).open('x') as f:f.write(content)
files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='SHA256SUMS')
with (OUT/'SHA256SUMS').open('x') as f:
 for p in files:f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
for name in ['report.md','report.json','SHA256SUMS']:(OUT/name).chmod(0o444)
print('65 inputs unchanged. Frozen once. Ledger entries:',len(files))
for name in ['report.md','report.json','SHA256SUMS']:print(name,hashlib.sha256((OUT/name).read_bytes()).hexdigest())
