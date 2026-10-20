from pathlib import Path
import json,hashlib,datetime
R=Path('/home/astra/artifacts/emberwake-brann-025-seam-followup-review-v1/review')
proof=json.loads((R/'anchor-repair-and-timing-proof.json').read_text())
before=json.loads((R/'input-hashes-before.json').read_text())
after=json.loads((R/'input-hashes-after.json').read_text())
assert before['all_match'] and after['all_match_before'] and after['manifest_unchanged'] and after['prior_mid_files_unchanged']
assert len(proof['anchor_checks'])==16 and all(x['new_A_equals_prior8_anchor'] and x['B_original_drawing_unchanged'] for x in proof['anchor_checks'])
assert all(len(x['changed_pixels'])==7 and x['all_other_mid_pixels_exact'] for x in proof['repair'])
assert proof['timing_unchanged_from_old9'] and proof['all_original_key_start_times_fixed']
A={'appearance':7.5,'identity':8.5,'motion_readability':7.5,'game_usefulness':7.5}
old={'appearance':7.0,'identity':8.5,'motion_readability':7.5,'game_usefulness':7.0}
B={'appearance':7.5,'identity':8.5,'motion_readability':7.5,'game_usefulness':7.5}
base_pairs=[
 ('00','01','P remains the prominent forward boot; Q draws inward beneath the hem. Cuff and boot volumes persist.'),
 ('01','02','P narrows in projection while Q tucks high. Occlusion explains the smaller visible Q boot; no screen-side identity swap assumed.'),
 ('02','03','Q returns down and forward in one relatively large projection change. The endpoint is attached, but the path is less explicit than the repaired B midpoint.'),
 ('03','04','Q advances through the close overlap into the forward role. Differing sole heights and depth overlap are plausible; no disconnected heel or toe found.'),
 ('04','05','Forward boot settles while the other foot withdraws. The rounded toe, cuff width and dark pants volume remain coherent.'),
 ('05','06','Close overlap hides much of the withdrawing leg. The stable front boot supplies a support candidate, without proving a world contact.'),
 ('06','07','The tucked leg becomes visibly separated and its sole pitch changes briskly. This unchanged exchange remains a larger chronological uncertainty than the repaired cuff.'),
 ('07','00','The front boot extends and the bent boot returns to the opening relation. Closure retains attachment and identity without an extra pixel or pose discontinuity.')
]
b_pairs=[
 ('00','01',base_pairs[0][2]),
 ('01','02',base_pairs[1][2]),
 ('02','03','Q descends from the tucked old02 position into a plausible intermediate position. The repaired dark cuff now connects to the boot; the larger adjacent inter-leg gap stays open.'),
 ('03','04','The repaired midpoint progresses into old03 overlap. Knee/cuff/heel/toe form a readable attached chain; toe and calf volume are retained rather than shaved away to gain separation.'),
 ('04','05',base_pairs[3][2]),
 ('05','06',base_pairs[4][2]),
 ('06','07',base_pairs[5][2]),
 ('07','08',base_pairs[6][2]),
 ('08','00',base_pairs[7][2])
]
pair_checks=[]
for direction in ['southeast','southwest']:
 for variant,rows in [('A',base_pairs),('B',b_pairs)]:
  for start,end,note in rows:pair_checks.append({'direction':direction,'variant':variant,'pair':start+'->'+end,'finding':note})
assert len(pair_checks)==34
report={
 'review':'Brann 02.5 midpoint cuff-seam repair follow-up',
 'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'Frozen once; no unchanged-art rerating',
 'source_scope':{'current_input':'/home/astra/artifacts/emberwake-brann-025-seam-followup-review-v1/input','previous_input_exception':proof['prior_input_read_scope'],'excluded':'Producer files, project source, other reviewers, other reports and skills were not read.'},
 'ratings_scale':'Absolute 0-10; appearance, identity, inferred motion readability and inferred game usefulness are separate. No points for exposure count, hash exactness or correct clock.',
 'ratings':{'A8_carried_unchanged':A,'previous_B9_carried_unchanged':old,'repaired_B9_new_scoped_judgment':B},
 'preference':{'choice':'B','strength':'slight','basis':'The repaired midpoint gives Q a more explicit attached down/forward recovery path between old02 and old03. Overall score tiers tie A; this is a local static-chronology preference, not observed timed smoothness.'},
 'delta_judgment':{'versus_old_B9':'The cuff attachment defect is corrected, restoring appearance and game usefulness to 7.5. Identity and motion score remain unchanged. The old B9 anchor is carried, not rerated.','versus_A8':'Repaired B matches all four carried A score tiers. Its one local path advantage is too bounded to earn another whole-loop half-point in inferred motion or game usefulness.'},
 'verification':{'current_pngs':65,'all_png_hashes_match_manifest_before':True,'all_png_hashes_unchanged_after':True,'manifest_unchanged':True,'A_anchor_hashes_verified':16,'B_original_drawing_hashes_verified':16,'repair_pixels_per_view':7,'repair_total_pixels':14,'repair_old_alpha':0,'repair_new_alpha':255,'all_other_midpoint_pixels_exact':True,'previous_midpoint_files_unchanged_after':True,'timing_unchanged':True,'original_key_start_times_fixed':True},
 'clock':proof['clock'],
 'index_mapping':'B00/01/02 = old00/01/02; B03 = new02.5 midpoint; B04/05/06/07/08 = old03/04/05/06/07. Both loops 450 ms. Only old02 hold is split into 28.125 ms old02 plus 28.125 ms midpoint.',
 'coverage':{'animation_cels':34,'cyclic_pairs':34,'A_pairs_per_view':8,'B_pairs_per_view':9,'views':['southeast','southwest'],'scales':['128px native','nearest-neighbor 2x','84px nearest-neighbor game-size proxy','84px bilinear ground cross-check'],'backgrounds':['light','dark','muted ground grid'],'own_diagnostic_pngs':25,'context':'All 30 cardinal context PNGs plus appearance image inspected for identity and facing only; no cardinal walk quality used to score diagonal motion.'},
 'tracking_method':'P is the projected boot prominent forward/lower in old00; Q is the other projected boot. Track these across occlusion and support/swing exchange, without inferring anatomical left/right from screen side. Mirrored SE/SW observations agree.',
 'joint_and_volume_findings':[
  'The prior seven-pixel enclosed horizontal under-cuff slit in the new midpoint is fully filled with compatible dark cuff/pants colors. Q reads as connected rather than cut across.',
  'The larger neighboring transparent inter-leg clearance remains pixel-exact. It separates two projected legs; filling it would not be justified by its being enclosed.',
  'Midpoint shin, calf, cuff width, heel/toe contour and boot pitch are otherwise identical to the prior midpoint. No remnant extra foreleg, detached boot or new volume loss found.',
  'P remains coherent while Q changes position. Q moves down/forward between old02 and old03, then accepts depth overlap at old03; differing sole heights alone are not faults.',
  'Body and arms remain at old02 in the midpoint and advance at old03. This supplies no new upper-body weight cue; the local lower-leg repair does not claim one.',
  'The unchanged old07 repair and old07->00 closure survive at B08->00. No new closure cost found.'
 ],
 'remaining_limits':[
  {'issue':'Brisk old06->old07 leg reveal and sole-pitch exchange','where':'A06->07; B07->08; both views','severity':'minor chronological limit, unchanged','minimum_meaningful_action':'No further seam cleanup is indicated. Determine whether this exchange is conspicuous in actual normal-speed playback before changing an otherwise attached closing pose.'},
  {'issue':'Restrained shoulder/hip weight response and dark lower-body contrast','where':'whole loop, especially dark ground and 84px proxy','severity':'unchanged style/readability limits','minimum_meaningful_action':'No additional local cuff pixels address these broader limits; no new drawing trial is recommended from this static-only comparison.'}
 ],
 'pair_checks':pair_checks,
 'perception_and_contact_limits':{
  'actually_observed':'Static individual cels, chronological strips, adjacent cyclic-pair sheets and enlarged attachment/alpha diagnostics.',
  'not_observed':'Actual normal-speed continuous human playback of these loops. No timed playback gain, lack of flicker or subjective visibility at 28.125 ms is claimed.',
  'timing_fact':'The midpoint exists for 9/320 s = 28.125 ms inside a 450 ms loop. Exact arithmetic does not establish perceptual smoothness or presentation-frame pacing.',
  'game_contact':'World translation, root/ground registration, foot locking, skating, contact timing and engine display sampling were not tested. Ground grids are static contrast aids, not contact evidence.',
  'scores':'Motion and game scores are bounded inferences from static art and chronology; appearance and identity are direct still-image judgments.'
 },
 'art_credit':'The seven-pixel count establishes scope. The visible repaired attachment earns the recovery in drawing/usefulness judgment. Exposure count, correct hold fractions and fidelity alone earn no art credit.',
 'smallest_repair_result':'The nominated repair is sufficient for the identified cuff slit. No additional pixel repair is required by this review.'
}
md='''Brann 02.5 cuff-seam repair: frozen follow-up review

Repaired B matches the eight-key A control overall, with a slight preference for B's more explicit static recovery path. The seven-pixel cuff repair per view removes the drawing flaw that penalized the prior nine-exposure version. It does not demonstrate a normal-speed smoothness gain.

| Version | Appearance | Identity | Motion readability* | Game usefulness* |
|---|---:|---:|---:|---:|
| A: eight keys, carried unchanged | 7.5 | 8.5 | 7.5 | 7.5 |
| Prior B: nine exposures, carried unchanged | 7.0 | 8.5 | 7.5 | 7.0 |
| Repaired B: new scoped judgment | 7.5 | 8.5 | 7.5 | 7.5 |

*Motion and game scores are static-chronology inferences. The local path advantage is too bounded to raise the whole-loop score another half-point. Prior anchors were carried, not rerated. Extra exposures, exact timing and hash equality earn no art points.

All 65 current PNG hashes match INPUTS.json before review and remain identical afterward; the manifest and two permitted prior midpoint files also remain unchanged. All 16 A cels equal the prior eight-key anchor. All 16 original B cels remain byte-identical. Only seven midpoint pixels in each view change, each alpha 0 to 255; every other midpoint pixel is exact. The proof records their coordinates and colors.

The repaired under-cuff slit now reads as connected dark material. Q's shin/cuff/boot chain is readable through the down/forward recovery without losing calf, heel or toe volume. The larger adjacent gap between the projected legs remains intact and is legitimate clearance. No extra foreleg remnant or new disconnected boot was found. P and Q are persistent projected feet, defined from old00 and followed through occlusion; they are not anatomical left/right labels inferred from screen side. The mirrored views agree.

All 34 animation cels and all 34 cyclic pairs were inspected in both views: A eight pairs per view, B nine pairs per view, including A07->00 and B08->00. Coverage used native 128px, nearest 2x, 84px nearest, and an 84px bilinear cross-check on light, dark and muted ground. Twenty-five bounded diagnostic PNGs retain this evidence. Appearance/cardinal images served identity and facing only.

B00/01/02 retain old00/01/02; B03 is the new 02.5 midpoint; B04/05/06/07/08 retain old03/04/05/06/07. Both loops are 450 ms. B splits only old02's 56.25 ms into 28.125 ms old02 plus 28.125 ms midpoint. Original key start times and all prior nine-exposure holds are exact.

The repaired B02->03->04 sequence gives the recovering Q boot a plausible intermediate position and an attached cuff. Its larger inter-leg clearance closes naturally into old03 overlap. The body's old02 hold remains unchanged; it supplies no new upper-body weight cue. The other seven original drawings, including old07 and closure, preserve their earlier strengths and limits.

The remaining minor chronological limit is the brisk old06->old07 leg reveal/sole-pitch change (B07->08). Shoulder/hip weight response stays restrained, and dark pants/boots still merge somewhat on dark ground at game size. No further seam repair is indicated. Actual playback evidence would be needed before deciding whether the unchanged closing-leg exchange needs another drawing edit.

This review observed static cels and chronological/pair sheets. It did not observe continuous normal-speed human playback. A 28.125 ms exposure may have different perceptual effect under actual display sampling; neither its visibility nor a smoothness gain is certified. Static ground grids establish contrast only. World translation, foot locking/skating, root registration and actual contact timing remain untested.

Source scope was limited to this nominated input, plus the preceding input manifest and two old midpoint PNGs solely for exact repair/clearance verification. No producer files, project source, other reports or skills were read. This judgment and output ledger are frozen once. See report.json for all 34 pair findings, anchor-repair-and-timing-proof.json for exact repair/mapping/clock proof, and input-hashes-before/after.json for preservation evidence.
'''
for name,data in [('report.json',json.dumps(report,indent=2)+'\n'),('report.md',md)]:
 with (R/name).open('x') as f:f.write(data)
files=sorted(p for p in R.iterdir() if p.is_file() and p.name!='SHA256SUMS')
with (R/'SHA256SUMS').open('x') as f:
 for p in files:f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
for name in ['report.md','report.json','SHA256SUMS']:(R/name).chmod(0o444)
print(json.dumps({'files_in_ledger':len(files),'diagnostic_pngs':len(list(R.glob('*.png'))),'cyclic_pairs':len(pair_checks),'ratings':report['ratings'],'preference':report['preference']},indent=2))
