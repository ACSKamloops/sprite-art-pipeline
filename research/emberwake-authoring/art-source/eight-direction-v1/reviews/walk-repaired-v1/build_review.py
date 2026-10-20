from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
OUT=Path('.')
manifest=json.loads(Path('../input-v1/INPUTS.json').read_text())
when=datetime.now(timezone.utc).isoformat(timespec='seconds')
ratings=[]
for actor in ('rowan','lyra'):
 for direction in ('southeast','northeast','southwest','northwest'):
  front=direction.startswith('south')
  ratings.append({'actor':actor,'direction':direction,'appearance':(7.0 if actor=='rowan' else 6.5) if front else 7.5,'identity':8.5,'motion':5.5 if front else 6.5,'usefulness':(6.5 if actor=='rowan' else 6.0) if front else 7.0})
means={k:round(sum(r[k] for r in ratings)/len(ratings),3) for k in ('appearance','identity','motion','usefulness')}
def paths(actors,dirs,keys):
 return [f'{a}/{d}/{k:02d}.png' for a in actors for d in dirs for k in keys]
findings=[
 {'id':'V1','kind':'visible','severity':'moderate local surface defect','actors':['rowan'],'directions':['southeast','southwest'],'keys':[1,7], 'region':'inner edge of raised/far cream thigh, immediately below the foreground glove and above/alongside its boot','observation':'The cream edge folds into a squared, bracket-like notch with a flat dark slit. Key 07 has the clearest rectangular opening. This edge looks cut out beside the rounded shaded near thigh; it is a local contour/material problem, not proof of a missing limb.','game_scale':'The precise notch is reduced at game scale; the angular light/dark flash remains easier to see on light and ground than on dark.','evidence':paths(['rowan'],['southeast','southwest'],[1,7]),'sheets':['diagnostics/rowan-southeast-nearest2x.png','diagnostics/rowan-southwest-nearest2x.png','diagnostics/rowan-local-lowerbody-4x.png']},
 {'id':'V2','kind':'visible','severity':'moderate local surface defect','actors':['lyra'],'directions':['southeast','southwest'],'keys':[1,7], 'region':'far upper trouser leg below the coat hem; screen-left for southeast and screen-right for southwest','observation':'Key 01 has a flat charcoal horizontal block across the far thigh; key 07 expands it into a squared dark tab with a thin vertical spur at the inner edge. These planes do not share the curved shading/volume of the adjacent trouser leg and boot. The blocky seam is particularly clear against light and ground.','game_scale':'At game scale it becomes a dark bar under the coat rather than a clear bent thigh.','evidence':paths(['lyra'],['southeast','southwest'],[1,7]),'sheets':['diagnostics/lyra-southeast-nearest2x.png','diagnostics/lyra-southwest-nearest2x.png','diagnostics/lyra-local-lowerbody-4x.png']},
 {'id':'V3','kind':'visible pose progression','severity':'moderate cycle readability defect','actors':['rowan','lyra'],'directions':['southeast','southwest'],'keys':[4,5,6,7], 'region':'shoulders, near forearm/glove, waist, raised knee','observation':'At 04 to 05 the broad chest/arm presentation changes to a much narrower, strongly side-presented pose. The near forearm crosses the waist and crowds the raised thigh; 05 to 06 separates the knee, then 06 to 07 restores the earlier arm/body presentation. The change is larger than the neighboring increments and reads as a body swivel in the static chronology.','game_scale':'This silhouette change remains visible at game scale, even when the small surface defects are reduced.','evidence':paths(['rowan','lyra'],['southeast','southwest'],[4,5,6,7]),'sheets':['diagnostics/rowan-southeast-game066.png','diagnostics/rowan-southwest-game066.png','diagnostics/lyra-southeast-game066.png','diagnostics/lyra-southwest-game066.png']},
 {'id':'V4','kind':'visible anatomy readability','severity':'minor to moderate passing-pose defect','actors':['rowan','lyra'],'directions':['northeast','northwest'],'keys':[5], 'region':'crossed lower legs and boots below the coat/tunic hem','observation':'Key 05 gathers the two boot shafts into a tight crossed brown cluster at lower center. The inner thigh/shin connections are harder to follow than at 02, 03, or 06; at game scale the feet nearly merge into one lower mass. This is weak limb separation, not an asserted extra limb or impossible pose.','game_scale':'The merged lower silhouette is visible on all three backgrounds, most strongly on dark.','evidence':paths(['rowan','lyra'],['northeast','northwest'],[5]),'sheets':['diagnostics/rowan-northeast-nearest2x.png','diagnostics/rowan-northwest-nearest2x.png','diagnostics/lyra-northeast-nearest2x.png','diagnostics/lyra-northwest-nearest2x.png']}
]
front_notes=[
 '07→00: similar upper-body presentation; boot extension gives a small cycle-boundary change. No conspicuous wrap-only discontinuity in the static pair.',
 '00→01: near boot extends/downward while far leg compresses. The local thigh contour/tab changes described in V1/V2 are exposed here.',
 '01→02: stance and shoulder/arm presentation open noticeably; readable stride change, but body exposure changes more than in the prior edge.',
 '02→03: legs narrow toward passing; the near boot and glove placement progress in a comprehensible direction.',
 '03→04: legs cross the body center while the broad torso presentation is retained. Occlusion increases but the leg order can still be inferred.',
 '04→05: largest arm/waist silhouette change; chest narrows, forearm crosses the abdomen, knee crowds it. V3 is most evident here.',
 '05→06: raised knee separates and the other boot extends; the high knee reads clearly as a pose, though the body remains strongly side-presented.',
 '06→07: upper body returns to its earlier oblique presentation and the far leg swings back. This edge deserves more interpolation than the relatively quiet 07→00 wrap.'
]
rear_notes=[
 '07→00: oblique back view remains stable; a modest boot extension closes the cycle without a conspicuous wrap-only jump in the static pair.',
 '00→01: legs compress toward passing while back/hair identity remains consistent.',
 '01→02: rear boot sole becomes more exposed and the other leg lengthens; shoulder/back presentation also straightens slightly.',
 '02→03: legs narrow; one longer supporting-looking boot remains readable. Actual support/contact cannot be established from this alone.',
 '03→04: the advancing boot crosses the center line; tighter but still traceable.',
 '04→05: both boot shafts collect at lower center; this is the least legible passing pose (V4).',
 '05→06: the silhouette opens into a long leg and a bent other leg; the release from the preceding knot is fairly large.',
 '06→07: legs return to the wide oblique stance and the back rolls toward its initial angle; a comprehensible but visible body/leg reset.'
]
transitions=[]
for r in ratings:
 front=r['direction'].startswith('south')
 notes=front_notes if front else rear_notes
 for key,note in enumerate(notes):
  transitions.append({'actor':r['actor'],'direction':r['direction'],'predecessor':(key-1)%8,'key':key,'observation':note})
review={
 'schema_version':1,'review_id':'emberwake-walk-repaired-review/review-v1','frozen_at_utc':when,
 'reviewer_mode':'Cold independent adversarial visual review; no producer folders, prior reviews, parent history, or desired score read.',
 'scope':{'input_root':'/home/astra/artifacts/emberwake-walk-repaired-review/input-v1','output_root':'/home/astra/artifacts/emberwake-walk-repaired-review/review-v1','authority':'INPUTS.json','authority_sha256':hashlib.sha256(Path('../input-v1/INPUTS.json').read_bytes()).hexdigest(),'review_card_present':False,'diagonal_loops':8,'diagonal_keys':64,'cyclic_edges_inspected':64,'stage':[128,128],'pivot':[64,112],'hold_seconds':0.05625,'cycle_seconds':0.45,'cardinal_use':'identity and view-turn context only'},
 'coverage':{'chronology':'07,00,01,02,03,04,05,06,07,00 in each scale/background sheet','scales':['native 128 px stage','nearest 2x, alpha-enclosing crop (24,8,104,120)','nominal .66 game draw, nearest rounded 84 px stage (84/128=.65625; exact nominal stage would be84.48 px)'],'backgrounds':['light RGB233,228,215','dark RGB25,30,36','patterned ground base RGB86,105,72'],'expected_source_png_hashes':144,'expected_hash_matches':144,'reference_pngs_hashed_without_supplied_expected_hash':2,'source_ledger_entries_including_manifest':147,'diagnostic_pngs':30},
 'playback_limits':{'continuous_playback_observed':False,'engine_playback_observed':False,'motion_score_basis':'All ordered static keys and every cyclic predecessor, including wrap. Scores measure pose progression and legibility; real-time smoothness is unverified.','unverified':['perceptual cadence at 450 ms','actual ground contact','foot sliding against world translation','engine filtering/pixel snapping','direction changes while moving'],'aid':'playback.html is a self-contained optional aid at exact nominal56.25 ms holds; it was not observed running by this reviewer.'},
 'rating_scale':'0 unusable/unreadable;5 serviceable with conspicuous issues;8 strong with minor remaining issues;10 exceptional polished result. Categories are independently judged, not averaged into an acceptance score.',
 'ratings':ratings,'category_means':means,'rating_confidence':{'appearance':'high','identity':'high','motion':'moderate; static chronology only','usefulness':'moderate; no runtime/world-motion test'},
 'visible_strengths':['Both actors retain the reference and adjacent-cardinal hair, palette, costume, and proportion cues. Rowan and Lyra remain easy to distinguish at game scale.','Hair, armor, gloves, coat/tunic and boots generally have coherent shaded volume. Rear upper-body masses remain stable through the cycle.','Diagonal intent and alternating stride are readable; game-scale readability survives all three test backgrounds.'],
 'visible_findings':findings,
 'hypotheses_not_confirmed_findings':[{'id':'H1','hypothesis':'The front 04→05 and 06→07 exposure changes may produce a swivel/pop during rapid looping.','basis':'V3 and complete static chronology','requires':'watch timed playback at 0.45 s and test in engine'},{'id':'H2','hypothesis':'The high knees and compressed passing poses may read as a brisk march/skip rather than a relaxed walk.','basis':'front05/06 and rear 05','requires':'continuous playback at intended world translation speed'},{'id':'H3','hypothesis':'Support may slide or alternate unclearly while moving.','basis':'No translated ground/contact test was supplied or observed; isolated pictures cannot establish this.','requires':'in-engine or translated-ground playback; this is an unverified integration question, not a reported defect'}],
 'transition_ledger':transitions,
 'result':{'scope':'These eight diagonal loops only; no full character library, runtime, gameplay, or production-history judgment.','status':'Suitable for provisional game/prototype use; targeted visual cleanup remains before polished final-art acceptance.','next_art_actions':['Repair Rowan front 01/07 cream thigh/boot contour so it reads as a rounded bent limb.','Replace Lyra front 01/07 flat charcoal tabs with coherent shaded far-thigh volume and a clean inner seam.','Reduce the front 04→05→06→07 changes in body presentation, and keep forearm/waist/raised-knee boundaries legible.','Separate rear 05 thigh/shin/boot connections at game scale.'],'next_validation':'Then watch all eight loops at exact 450 ms with .66 draw on moving ground and confirm contact/cadence; no new score should be inferred from this unperformed check.'}
}
(OUT/'review.json').write_text(json.dumps(review,indent=2)+'\n')
lines=['# Cold independent diagonal-walk review','',f'Frozen: {when}','',
'These are recognizable, attractive provisional game sprites. I would use the set in a playable prototype. Polished final-art acceptance still needs targeted front-thigh cleanup, clearer front pose progression, and clearer rear passing legs. Identity is the strongest category; motion is the weakest.','',
'| Loop | Appearance | Identity | Motion* | Usefulness* |','|---|---:|---:|---:|---:|']
for r in ratings: lines.append(f"| {r['actor'].title()} {r['direction']} | {r['appearance']:.1f} | {r['identity']:.1f} | {r['motion']:.1f} | {r['usefulness']:.1f} |")
lines.extend([f"| Category mean | {means['appearance']:.1f} | {means['identity']:.1f} | {means['motion']:.1f} | {means['usefulness']:.1f} |",'',
'All scores are independent judgments out of 10. 5 means serviceable with conspicuous issues; 8 means strong with minor issues; 10 means exceptional polish. File counts, metadata, process effort, and correctness of packaging earn no art credit.','',
'*Motion and usefulness are qualified: I inspected the full static chronology, including every cyclic predecessor, but did **not** observe continuous playback. I did not watch the 450 ms loop running or see translated in-engine motion. These scores judge pose continuity and readability; smoothness, cadence, contact, and sliding remain unverified. `playback.html` is an offline aid for a subsequent human check, not evidence of a performed playback check.*','',
'## Scope and coverage','',
'Only sibling `input-v1/INPUTS.json`, its listed PNGs, and `rowan-reference.png` / `lyra-reference.png` were read. No `REVIEW-CARD.md` was present. No producer reports, prior scores/reviews, parent history, or other producer folders informed this review.','',
'All 64 diagonal keys and all 64 ordered cyclic edges were inspected in the order **07→00→01→02→03→04→05→06→07→00**. Each loop was viewed on light, dark, and patterned ground at native size, nearest 2×, and game size. Native sheets retain the 128×128 stage; 2× sheets enlarge an alpha-enclosing 80×112 crop, with no sprite alpha clipped. Game sheets use a nearest-rounded84 px stage, an effective .65625 scale: the nominal .66 stage is84.48 px. Fractional engine sampling and pixel snapping were not tested. The HTML aid uses exact .66 CSS dimensions.','',
'Timing authority is eight equal 9/160-second holds (56.25 ms), total 9/20 second (450 ms), pivot (64,112). Adjacent cardinal art was examined for identity and view-turn context only. All 144 supplied expected PNG hashes match. The two reference PNGs were also hashed; no expected reference hashes were supplied. See `source-hash-ledger.json` / `.tsv`.','',
'## What reads well','',
'Rowan retains the warm spiky hair, blue-and-gold costume, pale trousers, and silver armor. Lyra retains the silver hair, dark green/teal clothing, scarf/cape and brown boots. Both match the reference and cardinal family and remain distinguishable at game scale. Hair and armor/glove/boot shading generally describe solid forms; the rear upper bodies stay especially stable. The directions and alternating strides are usable.','',
'## Remaining visible local defects',''])
for f in findings:
 lines.extend([f"**{f['id']} — {', '.join(f['actors'])}, {', '.join(f['directions'])}, keys {', '.join(f'{k:02d}' for k in f['keys'])}.** {f['observation']} {f['game_scale']}",f"Region: {f['region']}. Evidence: "+', '.join(f'`{p}`' for p in f['sheets'])+'.',''])
lines.extend(['These observations concern the actual visible anatomy, surfaces and pose changes. They do not establish broken rigging, missing limbs, or a particular production method. The bright/dark thigh defects are local; they do not invalidate the otherwise readable character identities.','',
'## Full-chronology motion account','',
'Both southeast and southwest loops were inspected independently for each actor. Their visible progression has the same broad strengths and weaknesses:','',
'| Cyclic edge | Front-diagonal observation |','|---|---|'])
for key,n in enumerate(front_notes): lines.append(f"| {(key-1)%8:02d}→{key:02d} | {n.split(': ',1)[1]} |")
lines.extend(['','Both northeast and northwest loops were likewise inspected independently for each actor:','','| Cyclic edge | Rear-diagonal observation |','|---|---|'])
for key,n in enumerate(rear_notes): lines.append(f"| {(key-1)%8:02d}→{key:02d} | {n.split(': ',1)[1]} |")
lines.extend(['',
'The relatively small 07→00 change does not prove a smooth loop. The larger internal changes at 04→05 and 06→07 must be evaluated as part of the complete cycle. The machine-readable transition ledger contains an entry for every actor/direction/key and its predecessor.','',
'## Playback and contact hypotheses','',
'The front body-exposure changes may produce a swivel/pop when looped, and the high knees may read as a brisk march or skip. Those are playback hypotheses based on the full chronology. I cannot confirm their perceptual strength at 450 ms without watching timed playback. Foot sliding and actual supporting-foot contact cannot be judged from isolated stage images without world translation and ground contact evidence.','',
'## Scoped result and next work','',
'Use the set provisionally. Repair Rowan front 01/07 thigh contours and Lyra front 01/07 flat trouser tabs; soften the front 04→05→06→07 body/arm change; separate the rear 05 boot/shin connections. Then watch all eight loops at exact 450 ms, .66 draw, with translated ground and intended walking speed. This review does not grant runtime/contact acceptance.','',
'`diagnostics/` contains 24 scale/background chronology sheets, two complete cardinal context sheets, two reference copies, and two supplementary 4× lower-body sheets. `SHA256SUMS` freezes the report, JSON, ledgers, diagnostics and local reproduction/playback aids. Hash verification is evidence of artifact integrity only.',''])
(OUT/'REVIEW.md').write_text('\n'.join(lines))
# Freeze the complete review output. SHA256SUMS excludes itself by convention.
files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
(OUT/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.as_posix()+'\n' for p in files))
print(json.dumps({'frozen_at_utc':when,'ratings':means,'transition_entries':len(transitions),'output_files_hashed':len(files),'report_sha256':hashlib.sha256((OUT/'REVIEW.md').read_bytes()).hexdigest(),'review_json_sha256':hashlib.sha256((OUT/'review.json').read_bytes()).hexdigest(),'sha256sums_sha256':hashlib.sha256((OUT/'SHA256SUMS').read_bytes()).hexdigest()},indent=2))
