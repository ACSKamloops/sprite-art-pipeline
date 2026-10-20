from pathlib import Path
from fractions import Fraction
from datetime import datetime, timezone
import json, hashlib
out=Path('/home/astra/artifacts/emberwake-gait-methods-cold-review-v1')
fps=json.loads((out/'fingerprints.json').read_text())
sheets=json.loads((out/'sheet-manifest.json').read_text())
clips=[]
for code, entry in fps.items():
 data=json.loads((Path(entry['packet'])/'INPUTS.json').read_text())
 for variant, dirs in data['variants'].items():
  for direction, frames in dirs.items():
   holds=data.get('variant_holds',{}).get(variant,data['holds'])
   assert len(holds)==len(frames)
   cursor=Fraction(0); timeline=[]
   for i, hold in enumerate(holds):
    duration=Fraction(*hold)
    timeline.append({'frame':i,'path':frames[i]['path'],'start_seconds_rational':[cursor.numerator,cursor.denominator],'start_seconds':float(cursor),'hold_seconds_rational':hold,'hold_seconds':float(duration)})
    cursor+=duration
   assert cursor==Fraction(9,20)
   clips.append({'packet':code,'actor':entry['actor'],'variant':variant,'direction':direction,'frames':len(frames),'reviewed_frames':list(range(len(frames))),'reviewed_adjacent_pairs':[[i,(i+1)%len(frames)] for i in range(len(frames))],'timeline':timeline,'duration_seconds_rational':[9,20]})
ratings=[]
for code, variants in [('X',['A','B','C']),('Y',['A','B'])]:
 for variant in variants:
  ratings.append({'packet':code,'actor':fps[code]['actor'],'variant':variant,'directions':['southeast','southwest'],'scores_out_of_10':{'appearance':8.0,'temporal_identity':8.0,'motion_readability':7.0 if code=='X' or variant=='B' else 7.5,'game_use':7.0 if code=='Y' and variant=='B' else 7.5,'overall':7.5},'uncertainty':{'appearance_and_identity_plus_minus':0.5,'motion_game_and_overall_plus_minus':0.75,'ranking_confidence':'low; chronology perception only'}})
issues=[
 {'id':'X1','kind':'demonstrated readability concern; not proven anatomy failure','severity':'moderate, localized','actor':'rowan','variants':['A','B','C'],'directions':['southeast','southwest'],'evidence':{'A':['05->06','06->07','07->00'],'B':['20->24','24->28','28->31->00'],'C':['20->24','24->28','28->31->00']},'source_region_approximate':{'southeast':[48,80,89,112],'southwest':[38,80,79,112]},'finding':'The lifted cream knee becomes a large round light mass, then the pale trouser overlap spreads beneath the belt before the boot extends again. The knee/upper-boot and opposite thigh are harder to track than face or armor at84px. Dense variants carry the same silhouette progression.','limit':'Foreshortening and occlusion can explain hidden leg sections. No extra limb, detached knee, reversed phase or impossible anatomy is demonstrated. The high-knee performance itself may be intentional.','benefit':'Clearer leg-role and knee-to-boot tracking in the second half of the stride.','smallest_next_experiment':'One lower-body-only drawing alternative for A06 and A07, preserving trajectories and holds. Clarify overlap crease and knee-to-boot silhouette; compare complete original/altered8-pose loops at84px and9/20s with a human before propagation into B/C.'},
 {'id':'Y1','kind':'demonstrated amplitude/readability difference; playback consequence uncertain','severity':'minor to moderate, conditional on game speed','actor':'lyra','variants':['B'],'directions':['southeast','southwest'],'evidence':{'B':['00->06','06->12','12->18','18->23->00'],'comparison':'A00/02/04/06 versus B00/06/12/18'},'source_region_approximate':{'southeast':[48,84,87,113],'southwest':[40,84,79,113]},'finding':'B keeps both boots nearer the resting stance. Reaching versus lifted-foot contrast and stride direction are less explicit at84px than A; character rendering stays coherent.','limit':'Compact stepping is valid. The stills do not prove shuffling, sliding, worse fluidity or better fluidity. No travel velocity/contact behavior observed.','benefit':'Choose gait amplitude for the actual movement velocity without first increasing frame count.','smallest_next_experiment':'Human compare existing A/B at84px, identical9/20s duration and identical travel velocity on a game ground. If B reads as shuffling, test2-3native pixels of extra toe reach at the two contact extremes and repair their immediate neighbors.'}
]
verdicts={
 'X-A':'Coherent hair, face, armor, tunic, gloves and boots across8poses. Alternate lifted/reaching leg states are present. Second-half pale overlap limits leg-role clarity.07->00 is a plausible continuing reach, not an exceptional reset fault.',
 'X-B':'All32poses retain character/costume identity. Smaller chronological changes do not resolve the pale overlap or establish superior normal-speed motion. No exceptional31->00 fault; same overall tier as A.',
 'X-C':'All32poses retain identity. Small intermediate contour/detail changes do not justify a higher/lower overall art tier at84px. No demonstrated unique structural or31->00 failure. No confident B-versus-C preference.',
 'Y-A':'Coherent silver hair, teal scarf/cape, costume and limbs across8poses. Wider boot excursion gives a clearer step at84px.04-06 overlap is a compact stylized turn, not evidence of a missing leg. No exceptional07->00 failure.',
 'Y-B':'All24poses preserve identity. Nearer-resting boot positions yield a restrained step and subtler stride contrast at84px. Could suit a compact performance. No demonstrated structural breakdown or exceptional23->00 failure; normal-speed superiority/inferiority unverified.'
}
now=datetime.now(timezone.utc).isoformat()
report={
 'title':'Anonymous gait-method cold review v1','frozen':True,'frozen_at_utc':now,
 'blind_status':'Frozen before method reveal. Methods unknown. Actor names appear in permitted ledgers/paths. No known accidental exposure.',
 'rubric':'/home/astra/.codex/skills/sprite-animation-pipeline/references/blind-review-card.md',
 'style':'Detailed small modern top-down RPG sprites; no limited-palette or retro purity requirement.',
 'read_scope':{'allowed':['blind-review-card.md','both nominated input folders and ledger-nominated PNGs'],'excluded':['parent folders/maps','producer reports','previous grades','skill case histories','other assets'],'production_actions':'None. No provider/model/editor calls, external search or input/source mutation.'},
 'perception':{'method':'Ordered stills/full-cycle chronology. Every frame, every predecessor/current pair and wrap, all three scales/backgrounds.','continuous_video_perception':False,'normal_speed_playback_claim':False,'optional_players_accessed':False,'actual_renderer_timestamps_sampled':False,'timing_evidence':'Declared exact rational ledger holds; derived frame start times included. Not measured browser presentation timestamps.','limits':'No controller feel, physical contact, stride-to-velocity match or normal-clock smoothness certification. More frames receive no automatic art score.'},
 'coverage':{'stage':[128,128],'pivot':[64,112],'scale_pixels':[84,128,256],'resampling':'nearest','game_proxy_note':'84px nearest resize of128px stage; declared0.66scale gives84.48px before raster rounding.','backgrounds':{'light':[222,221,211],'dark':[27,31,41],'game':'Synthetic textured green ground: base66,82,57 with small74,88,63 and58,73,51 patches; contrast probe, not actual game integration.'},'clips':len(clips),'variant_frames':sum(c['frames'] for c in clips),'directed_adjacent_pairs_including_wrap':sum(c['frames'] for c in clips),'wraps':len(clips),'sheets_inspected':len(sheets),'all_requested_combinations_inspected':True,'cardinal_context':'Both appearance strips and all supplied cardinal context frames inspected for identity/turn context only.'},
 'score_anchor':'Subjective10-point broad bands:5 functional but rough;7 good usable work with noticeable limitations;8 strong polished small-sprite candidate;9 exceptional control;10 virtually no useful scoped improvement. Overall is not a mathematical average or release certification.',
 'input_fingerprints':fps,'clips':clips,'ratings':ratings,'issues':issues,'whole_cycle_verdicts':verdicts,
 'preferences':{'X':'No confident overall preference among A/B/C; differences smaller than uncertainty.','Y':'Weak A preference for explicit step readability at84px. No confident temporal-feel or final-game-use preference without human playback/velocity context.'},
 'non_findings':['No demonstrated catastrophic anatomy or identity failure.','No material alpha halo, crop or framing failure identified on contrasted grounds. Light slivers in joint gaps follow the background and are not counted as pale outline contamination.','Mirrored step silhouettes are not required; perspective and occlusion allowed.','No acceptance transfer to other directions, equipment, actions, transitions or physical foot contact. Changed art/timing needs a new scoped review.']
}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
md=['# Anonymous gait-method cold review v1','',f'Frozen before unblinding at {now}.','',
 'All five variants are good, usable detailed RPG sprites in the **7.5/10 overall** band. Character identity is stronger than leg-motion clarity. No confident overall winner among X-A/B/C. Y-A makes the step clearer than Y-B at84px; that is a weak readability preference, not a verified playback win.','',
 '**Perception limit:** Ordered stills and full-cycle chronology with exact declared holds. I did not perceive continuous video, run optional players, measure browser presentation timestamps or test controller feel. Motion judgments reconstruct chronology from PNGs and known holds.','',
 '## Ratings','',
 '| Actor packet | Variant | Appearance | Temporal identity | Motion/readability | Game use | Overall |','|---|---:|---:|---:|---:|---:|---:|']
for r in ratings:
 s=r['scores_out_of_10'];md.append(f"| {r['packet']} ({r['actor']}) | {r['variant']} | {s['appearance']:.1f} | {s['temporal_identity']:.1f} | {s['motion_readability']:.1f} | {s['game_use']:.1f} | {s['overall']:.1f} |")
md+=['','Drawing/identity uncertainty approximately±0.5; motion, game use and overall approximately±0.75. No automatic points for denser frame counts, export correctness or an assumed method. Overall is a broad scoped judgment, not arithmetic or release certification.7 means good usable work with noticeable limitations;8 strong polished small-sprite candidate;9 exceptional control.','',
 '## Full-cycle verdicts','']
for key,val in verdicts.items(): md.extend(['**'+key+':** '+val,''])
md+=['Both SE and SW were inspected separately for every variant and occupy the same quality tier. The concerns reflect to the opposite side. No missing limb, detached joint, catastrophic identity change, crop failure or material halo was demonstrated. Cardinal context supports identity consistency, but does not certify transitions or other clips.','',
 '## Strongest actionable findings','']
for issue in issues:
 md.extend(['**'+issue['id']+' — '+issue['severity']+'.** '+issue['finding'],'',
 'Evidence: '+json.dumps(issue['evidence'])+'. Approximate source regions (x0,y0,x1,y1): '+json.dumps(issue['source_region_approximate'])+'.','',
 issue['limit'],'','Expected benefit: '+issue['benefit'],'','Smallest useful next experiment: '+issue['smallest_next_experiment'],''])
md+=['## Evidence and scope','',
 '- Read only the supplied blind-review card and nominated X/Y input folders. No parent maps, producer reports, previous grades, skill histories or other assets consulted. No known accidental exposure. Actor names occur in permitted ledgers; methods remain anonymous.','- Verified175 X files and95 Y files against ledger SHA-256 values, including context. All per-file hashes are in fingerprints.json and report.json.','- Reviewed10 diagonal clips,208 variant frames and208 directed adjacent pairs, including10 wraps. All90 clip×scale×background views inspected. Each chronology row repeats its next frame so row transitions and wraps remain adjacent.','- Scales:128px native stage,84px nearest game proxy,256px nearest enlargement. Pivot64,112. Declared0.66scale is84.48px before raster rounding.','- LightRGB222,221,211; dark27,31,41; synthetic textured green ground base66,82,57 with74,88,63 and58,73,51 patches. These are contrast probes, not live game integration.','- Every loop declares9/20s (0.45s): A8×9/160s; X-B/C32×9/640s; Y-B24×3/160s. Exact rational start times and holds are in report.json. Renderer presentation timing was not measured.','- Both appearance strips and all supplied cardinal context frames inspected for identity/turn context only. No provider/model/editor calls, external search, production edits or input mutation performed.','- Other directions, equipment, actions, start/stop/turn transitions, actual movement velocity and physical foot contact remain outside scope. Changed art/timing needs a new review.','',
 'Ledger fingerprints:','',
 '| Packet | INPUTS.json SHA-256 |','|---|---|',
 '| X | '+fps['X']['ledger_sha256']+' |','| Y | '+fps['Y']['ledger_sha256']+' |','',
 'Files: report.json contains findings, ratings, full fingerprints and chronology; fingerprints.json binds the inputs; sheet-manifest.json lists all90 reviewed views; FROZEN.sha256 freezes these four records. Generated material is confined to this fresh review folder.','',
 'Review complete within the stated still/chronology perception limit.']
(out/'report.md').write_text('\n'.join(md)+'\n')
freeze=[]
for name in ['report.json','report.md','fingerprints.json','sheet-manifest.json']:
 freeze.append(hashlib.sha256((out/name).read_bytes()).hexdigest()+'  '+name)
(out/'FROZEN.sha256').write_text('\n'.join(freeze)+'\n')
print('Frozen',now,'clips',len(clips),'frames',sum(c['frames'] for c in clips),'sheets',len(sheets))
print('\n'.join(freeze))
