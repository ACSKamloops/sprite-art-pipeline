from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,shutil,os
OUT=Path(__file__).resolve().parent
OLD=OUT.with_name('emberwake-bounded-action-review-v1')
old=json.loads((OLD/'review.json').read_text())
manifest=json.loads((OUT/'inputs.json').read_text())
records=[r for r in old['results'] if r['id'] not in ['brann-southeast-idle-A','brann-southeast-idle-B']]
records.append({'id':'brann-southeast-idle','preference':'trial','confidence':'medium','control':{'appearance':4,'identity':4,'motion_readability':3,'usefulness':3},'trial':{'appearance':4,'identity':4,'motion_readability':3,'usefulness':4},'visible_evidence':'The exact trial uses brann-eye-v1/22 and breath-v2/brann/southeast/23 together. Both frames keep the hands beside the thighs and the same relaxed stance. The chest/shoulders and head change only slightly in 22-to-23 and back, with no change into a raised guard. The bright eye is consistently readable at native size, while control 22 is visibly narrower/darker-eyed than control 23. The trial is a more useful relaxed idle pair.','remaining_limit':'At .66 the upper-body movement is very subtle, especially against dark; these stills cannot establish that the small breath reads at 580/580 ms. The preference concerns a relaxed idle, not a combat-ready guard. This supersedes only the v1 idle conclusions, which assessed incorrect hybrid pairs.'})
for r in records:r['ratings_0_to_10']={v:{k:2*n for k,n in r[v].items()} for v in ['control','trial']}
# Keep exact source observations and scores from v1 for the eight unchanged cases.
for before,after in zip(old['results'][:8],records[:8]):
 for k in ['id','preference','confidence','control','trial','visible_evidence','remaining_limit']:assert before[k]==after[k]
# Supplemental magnifications from unchanged cases are copied for audit continuity.
for p in OLD.rglob('*zoom2x.png'):
 q=OUT/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
p=OUT/'comparisons/brann-southeast-idle/light-native-sequence.png';im=Image.open(p);im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(p.with_name('light-native-sequence-zoom3x.png'))
checks=[]
for s in manifest['sources']:
 h=hashlib.sha256(Path(s['source_path']).read_bytes()).hexdigest();copy=hashlib.sha256((OUT/s['packet_path']).read_bytes()).hexdigest();assert h==copy==s['sha256']
 checks.append({'source_path':s['source_path'],'sha256':h,'copy_verified':True,'current_source_unchanged_from_packet':True})
expected={'art/brann-eye-v1/22.png':'789c7d5af8054bf9be2cf05c57238b0a068e49d877c3a0e71be25d02e1e9654e','art/breath-v2/brann/southeast/23.png':'17dcb74c073e82690f99d8f5417a3343a1e4fa1bb72d77ddb80a532e35d0b315'}
for s in manifest['sources']:
 short=s['packet_path'].removeprefix('sources/')
 if short in expected:assert s['sha256']==expected[short]
unchanged=0
for c in manifest['cases']:
 for bg in ['light','dark','ground']:
  for scale in ['native','066','066-nearest']:
   p=OUT/'comparisons'/c['id']/f'{bg}-{scale}-matched.gif'
   with Image.open(p) as im:
    d=[]
    for n in range(im.n_frames):im.seek(n);d.append(im.info.get('duration'))
   assert d==c['duration_ms'],(p,d)
 if c['action']!='idle':
  for p in (OLD/'comparisons'/c['id']).iterdir():
   q=OUT/p.relative_to(OLD)
   if p.is_file() and q.exists():assert p.read_bytes()==q.read_bytes();unchanged+=1
viewed=[v for v in old['method']['inspected_outputs'] if 'brann-southeast-idle/' not in v]
for c in manifest['cases']:viewed.append('comparisons/'+c['id']+'/nearest-066-overview.png')
for bg in ['light','dark','ground']:
 for scale in ['native','066']:viewed.append(f'comparisons/brann-southeast-idle/{bg}-{scale}-pairs.png')
now=datetime.now(timezone.utc).isoformat()
correction={'superseded_packet':str(OLD),'superseded_review_sha256':hashlib.sha256((OLD/'REVIEW.md').read_bytes()).hexdigest(),'superseded_review_json_sha256':hashlib.sha256((OLD/'review.json').read_bytes()).hexdigest(),'error':'The reviewer misread A22/B23 as independent substitutions. V1 compared A22+registered23 and registered22+B23, not the requested A22+B23 pair. The images were correctly sourced but the sequence construction was incorrect.','disposition':'V1 preserved unchanged; its idle scores and preference are withdrawn for the requested pair. Cast/hurt records are unchanged. V2 uses the exact two-frame trial.','correct_trial_source_paths':['/home/astra/projects/emberwake-demo/art-source/eight-direction-v1/brann-eye-v1/22.png','/home/astra/projects/emberwake-demo/art-source/eight-direction-v1/breath-v2/brann/southeast/23.png'],'correct_trial_sha256':list(expected.values()),'unchanged_cast_hurt_comparison_files_verified':unchanged}
(OUT/'CORRECTION.md').write_text('# Superseded idle pairing disclosure\n\nV1 is preserved at `'+str(OLD)+'`. Its idle comparison was constructed incorrectly: A22 was paired with registered23, and registered22 with B23. These were two hybrid sequences that the requester had not asked to assess.\n\nThe requested trial is **A22 + B23 together**:\n\n'+''.join(f'- `{p}`\n' for p in correction['correct_trial_source_paths'])+'\nTheir hashes are recorded in `inputs.json` and `review.json`. Both trial frames keep the hands down; the v1 guard-toggle objection and its idle ratings/preferences are withdrawn for this exact pair.\n\nV2 re-inspects the corrected pair. The eight cast/hurt results, evidence, ratings and preferences are preserved exactly; '+str(unchanged)+' existing comparison files for those cases also match v1 byte-for-byte. Nearest-neighbor .66 views have been added and inspected. V1 has not been rewritten.\n\nV1 REVIEW.md SHA256: `'+correction['superseded_review_sha256']+'`\n')
review={'status':'frozen-corrected-v2','reviewed_at_utc':now,'scope':'Specified source images and clocks only, plus explicit pairing/filter clarifications. No external art reviews, producer reports or desired scores read; own v1 review used to carry forward unchanged cast/hurt records. No canonical edits or image generation.','correction':correction,'method':{'kind':'independent still-sequence and all adjacent/recovery-pair visual review','reference_use':'identity only','backgrounds':['light','dark','ground'],'scales':{'native':'128x128 source pixels preserved','requested_0.66':'84x84 (.65625 actual rounded ratio)'},'small_resampling':['LANCZOS proxy','NEAREST to match supplied Godot filtering context'],'filter_context_provenance':'Requester reports _sprite.texture_filter NEAREST at hero.gd69 and project.godot24. Source code was not read within this bounded art review.','nearest_observation':'Hard pixel edges and palm/metal highlights are sharper than Lanczos; fine fingers remain small. Cast cue and SE hurt overshoot findings persist. Tiny NE hurt changes remain marginal, and corrected idle breathing is subtle. No cast/hurt preference or rating changes.','timed_gifs':'Synchronized variants in one GIF canvas; exact encoded durations verified for both filters. Actual-speed playback not reviewed.','inspected_outputs':viewed,'inspected_transitions':old['method']['inspected_transitions'],'unchanged_case_inspection_carry_forward':'All prior cast/hurt images actually inspected are retained byte-for-byte, plus additional nearest-filter inspection.','numeric_diagnostics':'Alpha bounds corroborated visible crown placement only; no score credit for source math.'},'rating_scale_0_to_5':{'0':'missing or wholly unusable','1':'fails the intended role','2':'weak; conspicuous limitation','3':'serviceable with visible limitations','4':'clear and strong within this bounded task','5':'exceptional within this bounded task'},'delivery_scale_0_to_10':{'conversion':'Exactly 2x the original 0-to-5 ordinal judgment, not a new independent rescore','anchors':{'0':'missing or wholly unusable','2':'fails role','4':'weak','6':'serviceable','8':'strong','10':'exceptional'}},'rating_policy':'Appearance, identity, motion readability and usefulness are separate ordinal judgments. No overall average. Small preferences can share ratings. No source-math, work-volume or producer-effort credit.','results':records,'summary':{'prefer_trials':[r['id'] for r in records if r['preference']=='trial'],'prefer_control':[r['id'] for r in records if r['preference']=='control'],'low_confidence_preferences':[r['id'] for r in records if r['confidence']=='low'],'no_blanket_hurt_swap':True},'limits':['Still-sequence review supports pose continuity, silhouette, inferred movement and registration judgments, not perceived fluidity at speed.','No actual-speed playback, runtime action triggers, VFX, camera, lighting, terrain, full direction set or transition into movement was reviewed.','Flat ground color tests contrast only.84px rounding and sampling can differ from fractional runtime sprite scaling even with NEAREST.','Looping hurt/cast GIFs are comparison aids; the neutral hurt context is untimed.','No actor-wide quality claim follows from these bounded cases.'],'source_verification':{'count':len(checks),'all_exact_copies':True,'all_current_sources_match':True,'inputs_manifest':'inputs.json','sources':checks},'freeze':{'hash_manifest':'SHA256SUMS','self_hash_policy':'Covers every packet file except itself; own digest reported separately','read_only_core_files':['REVIEW.md','review.json','inputs.json','CORRECTION.md','SHA256SUMS']}}
(OUT/'review.json').write_text(json.dumps(review,indent=2)+'\n')
def score(r,v):return '/'.join(str(r['ratings_0_to_10'][v][k]) for k in ['appearance','identity','motion_readability','usefulness'])
lines=['# Independent bounded action review - corrected v2','',f'Frozen {now}. [Inputs](inputs.json), [replay/stills](index.html), [pairing disclosure](CORRECTION.md).','',
'**Ratings use 0–10 in this report:** 0 unusable,2 fails role,4 weak,6 serviceable,8 strong,10 exceptional. This is a linear 2× display of the original 0–5 ordinal judgments (also retained in JSON): 0 unusable,1 fails,2 weak,3 serviceable,4 strong,5 exceptional. Appearance, identity, motion readability and usefulness are separate; there is no overall score.','',
'Prefer both Rowan cast trials and the corrected Brann relaxed-idle trial. Hurt changes merit selective use: prefer Rowan SE and, weakly, the three NE trials; retain Lyra/Brann SE controls.','',
'**Correction:** V1 misread A22/B23 as separate alternatives and assessed A22+registered23 and registered22+B23. Its idle conclusion is withdrawn for the requested pair. This packet uses **brann-eye-v1/22 + breath-v2/brann/southeast/23 together**. V1 is preserved unchanged. The eight cast/hurt findings and ratings are unchanged; their prior comparison files match byte-for-byte.','',
'## Separate judgments','',
'Each cell lists **appearance / identity / motion readability / usefulness**, all on 0–10. Equal coarse ratings can accompany a small preference.','',
'| Comparison | Control | Trial | Prefer | Confidence |','|---|---|---|---|---|']
for r in records:lines.append(f"| {r['id']} | {score(r,'control')} | {score(r,'trial')} | {r['preference']} | {r['confidence']} |")
lines += ['', '## Visible evidence','']
for r in records:lines.extend([f"**{r['id']}:** {r['visible_evidence']} {r['remaining_limit']}",''])
lines += ['## Coverage, filter and limits','',
'All adjacent and return pairs were inspected: cast 22→17→18→19→20→22 plus 22→22 boundary; hurt neutral 22→24 context, 24→25→22 and 22→24 boundary; idle 22↔23. Native 128px and requested .66 at 84px were inspected on light, dark and flat muted-ground backgrounds. The corrected idle pair was inspected in all six native/Lanczos-scale pair sheets. Every case also received new NEAREST .66 views on all backgrounds. Appearance references informed identity only.','',
'NEAREST gives sharper pixel edges and highlights than Lanczos. The open cast palm and southeast hurt overshoots persist; northeast hurt gains remain marginal. Corrected Brann idle keeps both hands down, with only a subtle upper-body change. No cast/hurt finding or preference changed after the filter check. The supplied runtime-filter context was not independently inspected in code.','',
'Matched GIFs encode cast 60/80/100/80/80/100ms; hurt 90/100/100ms; idle 580/580ms. Durations were checked for both filters; variants share one clock. Neutral hurt context is untimed. GIFs are replay aids: these judgments come from still/pair inspection, not actual-speed playback.','',
'This does not establish fluidity at speed, VFX integration, runtime triggers, movement transitions, full-direction consistency or terrain appearance. Flat backgrounds test contrast ; 84px rounding/sampling may differ from fractional engine scaling. Tiny NE gains need runtime confirmation. Source math and work volume earned no score.','',
'All 44 exact input copies match their current sources. No canonical edits or image generation occurred. `review.json` records evidence and verification; `SHA256SUMS` covers every other packet file. Core reports/manifests are read-only after freeze.','']
(OUT/'REVIEW.md').write_text('\n'.join(lines))
files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
(OUT/'SHA256SUMS').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(OUT).as_posix()}\n' for p in files))
for name in review['freeze']['read_only_core_files']:os.chmod(OUT/name,0o444)
print(json.dumps({'status':review['status'],'sources':len(checks),'cases':len(records),'unchanged_cast_hurt_comparison_files':unchanged,'hash_manifest_entries':len(files),'hashes':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in ['REVIEW.md','review.json','inputs.json','CORRECTION.md','SHA256SUMS']}},indent=2))
