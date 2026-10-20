from pathlib import Path
from fractions import Fraction
from datetime import datetime,timezone
import json,hashlib
out=Path('/home/astra/artifacts/emberwake-brann-contact-cold-review-v1')
p=Path('/home/astra/artifacts/emberwake-brann-contact-review-v1/input')
data=json.loads((p/'INPUTS.json').read_text())
fps=json.loads((out/'fingerprints.json').read_text());sheets=json.loads((out/'sheet-manifest.json').read_text())
now=datetime.now(timezone.utc).isoformat();clips=[]
for variant,dirs in data['variants'].items():
 for direction,frames in dirs.items():
  timeline=[];cursor=Fraction(0)
  for i,hold in enumerate(data['holds']):
   timeline.append({'frame':i,'path':frames[i]['path'],'start_seconds_rational':[cursor.numerator,cursor.denominator],'start_seconds':float(cursor),'hold_seconds_rational':hold,'hold_seconds':float(Fraction(*hold))})
   cursor+=Fraction(*hold)
  assert cursor==Fraction(9,20)
  clips.append({'variant':variant,'direction':direction,'frames':len(frames),'reviewed_frames':list(range(len(frames))),'reviewed_adjacent_pairs':[[i,(i+1)%len(frames)] for i in range(len(frames))],'duration_seconds_rational':[9,20],'timeline':timeline})
ratings=[
 {'variant':'A','directions':['northeast','northwest'],'scores_out_of_10':{'drawing_appearance':7.5,'temporal_identity':8.0,'motion_readability':7.0,'game_use':7.0,'overall':7.5}},
 {'variant':'B','directions':['northeast','northwest'],'scores_out_of_10':{'drawing_appearance':8.5,'temporal_identity':8.5,'motion_readability':8.0,'game_use':8.0,'overall':8.0}}
]
issue={
 'id':'A1','variant':'A','directions':['northeast','northwest'],'severity':'moderate localized readability weakness','kind':'demonstrated visible overlap/readability issue; hidden anatomy unproven',
 'frames_pairs':['01->02','02->03','03->04'],'source_region_approximate':{'northeast':[42,80,86,116],'northwest':[41,80,85,116]},
 'finding':'The sole-on boot in01-02 turns into a compact dark boot/leg cluster in03 before the reach becomes clear again in04. Toe, cuff and opposite trouser/boot boundaries are hard to distinguish at84px, especially on the dark and textured green grounds. A03 is the least explicit near/far foot silhouette; B02-04 maintains a more legible cuff, toe and trouser division.',
 'not_claimed':'Occlusion may legitimately merge leg silhouettes. This is not proof of a missing foot, detached limb, reversed limb role, impossible joint or physical contact failure. Alternating steps need not mirror.',
 'expected_benefit':'Make the passing/overlap phase easier to follow at game scale while retaining this character\'s weight and small-sprite style.',
 'smallest_next_repair_experiment':'One drawing alternative for A03 only: preserve overall foot positions and occlusion, clarify the visible cuff-to-boot boundary with a short value edge and give the visible toe/sole a deliberate contour. Review02->03->04 and the complete8-pose loop at84px with identical holds before extending changes to any neighboring cel. Do not widen the legs merely to force a gap.'
}
verdicts={
 'A':'Good detailed character rendering, compatible with the cardinal identity context. The rounded textured black hair, blue tunic, gold shoulders/cuffs and red sash persist through all8poses. Alternating reach/lift silhouettes are visible across the whole cycle, but the01-04 overlap weakens foot-role readability; the07->00 wrap is not a distinct reset failure. Both diagonal directions have the same concern. Usable, with a localized leg-drawing refinement warranted.',
 'B':'Stronger control of boot volumes, cuff bands, trouser boundaries and bright armor/trim contours across all8poses. These features remain easier to parse at84px on all contrasted grounds. Hair silhouette/texture, shoulder armor, tunic and red sash stay recognizably consistent across the cycle. Alternate reach/lift states and07->00 continuation are legible in chronology. No material defect I can substantiate from this scope; the next check is human normal-clock/game-velocity playback, not an invented drawing repair.'
}
report={
 'title':'Brann anonymous contact cold review v1','frozen':True,'frozen_at_utc':now,
 'blind_status':'No Brann producer report, prior grade, method mapping or provenance consulted; A/B methods remain unknown at freeze.',
 'prior_exposure':'The reviewer previously assessed anonymous X/Y packets for different actors in the same session. Those reports remain frozen and were not reopened. No Brann grade was shown. This is a fresh Brann packet review, not a claim of no prior review activity.',
 'rubric':'/home/astra/.codex/skills/sprite-animation-pipeline/references/blind-review-card.md',
 'style_brief':'Detailed small modern top-down RPG sprites. No limited-palette or retro purity requirement.',
 'read_scope':{'allowed':['nominated Brann input folder, ledger and PNGs','same blind-review card already read'],'excluded':['parent folders/maps','provenance','producer reports','old grades','skill case histories','other actor packets during this Brann pass'],'production_actions':'None. No provider/model/editor call, external search, source edit or input mutation.'},
 'perception':{'method':'Ordered full-cycle stills/chronology with every predecessor/current pair and wrap.','continuous_video_perception':False,'normal_speed_playback_claim':False,'optional_player_accessed':False,'actual_renderer_timestamps_sampled':False,'timing_evidence':'Exact declared rational holds and derived frame start times from INPUTS.json. Not measured live presentation timestamps.','limits':'No controller feel, ground-contact physics, measured foot sliding, stride-to-travel-velocity match or continuous normal-clock smoothness verdict. No score points for successful exports or hidden production methods.'},
 'coverage':{'stage':[128,128],'pivot':[64,112],'scales':[84,128,256],'resampling':'nearest','game_proxy':'84px whole-stage resize;0.66*128=84.48px before raster rounding.','backgrounds':{'light':[222,221,211],'dark':[27,31,41],'game_ground':'Synthetic textured green ground, base66,82,57 with patches74,88,63 and58,73,51; contrast probe, not actual game integration.'},'clips':4,'variant_frames':32,'directed_adjacent_pairs_including_wrap':32,'wraps':4,'sheets_inspected':len(sheets),'all_requested_combinations_inspected':True,'context':'Appearance strip and all30supplied cardinal idle/walk frames inspected for identity/turn context only.'},
 'timing_summary':'Both variants8cels with9/160s each, total9/20s (0.45s). No duration/frame-count advantage between variants.',
 'input_fingerprints':fps,'clips':clips,'ratings':ratings,
 'uncertainty':{'drawing_and_identity_plus_minus':0.5,'motion_game_use_overall_plus_minus':0.75,'confidence':'Moderate drawing/readability preference for B. Normal-speed feel remains unverified, and the0.5overall gap is smaller than the overall uncertainty band.'},
 'score_anchor':'Subjective10-point broad bands:5functional but rough;7good usable work with noticeable limitations;8strong polished small-sprite candidate;9exceptional control;10virtually no useful scoped improvement. Overall is an artistic judgment, not arithmetic or release certification.',
 'whole_cycle_verdicts':verdicts,'issues':[issue],
 'preference':'B for drawing and visible step readability in both directions. This is not a demonstrated smoother normal-clock playback result or a contact-physics certification.',
 'next_experiments':{'A':issue['smallest_next_repair_experiment'],'B':'Human compare both existing full loops at84px and the same0.45s duration with identical game travel velocity. Check whether the clearer still silhouettes translate to better normal-speed stepping before changing any B drawing.'},
 'non_findings':['No demonstrated missing limb, detached joint, catastrophic identity change, crop or alpha-halo failure.','No exceptional07->00loop-boundary defect identified in either variant/direction.','Merged leg silhouettes alone do not prove hidden-anatomy or contact failure.','No requirement that opposite step silhouettes mirror.','No material B defect was established, so no arbitrary corrective redraw is prescribed.','No certification of other directions, equipment, actions, transitions or physical contact; changed art/timing needs a new review.']
}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
md=['# Brann anonymous contact cold review v1','',f'Frozen before unblinding at {now}.','',
 '**B is stronger in drawing and visible step readability.** A is usable with a localized overlap-phase weakness. B\'s clearer boot/cuff/trouser divisions survive the84px game proxy. This preference does not prove smoother continuous playback or better physical foot contact.','',
 '**Prior exposure:** I previously reviewed anonymous X/Y packets for different actors in this session. Those reports remain frozen and were not reopened. No Brann grade, method mapping, producer report or provenance was shown.','',
 '**Perception limit:** I inspected ordered stills and full chronology using exact declared holds. I did not perceive continuous video, access the optional player, measure browser presentation timestamps or test controller feel. Motion judgments reconstruct chronology; contact physics, foot sliding and stride-to-velocity fit remain unverified.','',
 '## Scores','',
 '| Variant | Drawing/appearance | Temporal identity | Motion/readability | Game use | Overall |','|---|---:|---:|---:|---:|---:|']
for r in ratings:
 s=r['scores_out_of_10'];md.append(f"| {r['variant']} | {s['drawing_appearance']:.1f} | {s['temporal_identity']:.1f} | {s['motion_readability']:.1f} | {s['game_use']:.1f} | {s['overall']:.1f} |")
md+=['','Approximate uncertainty: drawing/identity±0.5; motion/game use/overall±0.75. The B drawing/readability preference has moderate confidence; the0.5overall score gap is within the overall uncertainty band. Scores are broad subjective tiers, not arithmetic or release acceptance.7means good usable work with limitations,8a strong polished small-sprite candidate,9exceptional control. Neither identical frame count nor any guessed production method earns points.','',
 '## Whole-cycle findings','']
for key,val in verdicts.items(): md.extend(['**'+key+':** '+val,''])
md+=['NE and NW were inspected separately at every scale/background. The direction-level quality tier is the same, with reflected evidence. The supplied cardinal context supports compatible costume/character identity; it does not establish unreviewed transition behavior.','',
 '## Actionable issue','',
 '**A1 — Overlap-phase foot readability (moderate, localized).** '+issue['finding'],'',
 'Evidence:01→02,02→03,03→04. Approximate128px source regions: NEx42–86,y80–116; NWx41–85,y80–116.','',
 issue['not_claimed'],'','Expected benefit: '+issue['expected_benefit'],'',
 'Smallest repair experiment: '+issue['smallest_next_repair_experiment'],'',
 '**B:** No material localized defect was established. First obtain a human normal-clock comparison of the existing loops at84px, identical0.45s duration and identical game movement velocity. That resolves the remaining temporal/grounding question without inventing a drawing fix.','',
 '## Bound evidence','',
 '- Only the nominated Brann input folder and the same supplied blind-review card were used for this pass. No parent maps, provenance, producer reports, previous Brann grades or case histories consulted. No known accidental Brann exposure.','- All63nominated PNGs match their ledger hashes:32variant frames plus31appearance/cardinal context images. Full per-file SHA-256 values are in fingerprints.json and report.json.','- Four clips,32variant frames and32directed adjacent pairs including four07→00wraps inspected. All36clip×scale×background views inspected. Chronology rows repeat their next frame so row boundaries and wraps stay adjacent.','- Native128px stage;84px nearest proxy;256px nearest enlargement. Pivot64,112. Declared game factor0.66is84.48px before rounding.','- LightRGB222,221,211; dark27,31,41; synthetic green ground base66,82,57 with74,88,63 and58,73,51 patches. Contrast probes do not certify actual game integration.','- Both variants use8×9/160s holds, totaling9/20s (0.45s). Exact rational derived start times are in report.json. These are declared PNG timeline holds, not sampled renderer timestamps.','- No material halo/framing failure, catastrophic identity/anatomy failure or exceptional wrap defect demonstrated. Occlusion and perspective are allowed; opposite steps need not mirror.','- No provider/model/editor calls, external search, production edits or input/source mutation. All generated work is confined to this new review folder.','- Other actions, equipment, directions, transitions and physical foot contact remain outside scope. Changed art/timing requires a new review.','',
 'INPUTS.json SHA-256: '+fps['ledger_sha256'], '',
 'report.json contains ratings, findings, full input fingerprints and chronology. sheet-manifest.json lists the36reviewed views. FROZEN.sha256 freezes the four report/evidence ledgers.','',
 'Review complete within the stated still/chronology perception limit.']
# Keep human-facing prose readable around compact numeric source notation.
replacements={'the84px':'the 84px','the0.5':'the 0.5','7means':'7 means','8a strong':'8 a strong','9exceptional':'9 exceptional','Evidence:01':'Evidence: 01','regions: NE':'regions: NE ','; NWx':'; NW x','NEx':'NE x','identical0.45s':'identical 0.45s','All63nominated':'All 63 nominated','32variant':'32 variant','31appearance':'31 appearance','All36clip':'All 36 clip','four07':'four 07','07→00wraps':'07→00 wraps','Native128px':'Native 128px','factor0.66is84.48px':'factor 0.66 is 84.48px','LightRGB222':'Light RGB 222','dark27':'dark 27','base66':'base 66','with74':'with 74','and58':'and 58','use8×':'use 8×','totaling9/20s':'totaling 9/20s','the36reviewed':'the 36 reviewed','128px source':'128px source','at84px':'at 84px'}
text='\n'.join(md)+'\n'
for a,b in replacements.items():text=text.replace(a,b)
(out/'report.md').write_text(text)
freeze=[]
for name in ['report.json','report.md','fingerprints.json','sheet-manifest.json']:
 freeze.append(hashlib.sha256((out/name).read_bytes()).hexdigest()+'  '+name)
(out/'FROZEN.sha256').write_text('\n'.join(freeze)+'\n')
print('Frozen',now,'clips',len(clips),'sheets',len(sheets))
print('\n'.join(freeze))
