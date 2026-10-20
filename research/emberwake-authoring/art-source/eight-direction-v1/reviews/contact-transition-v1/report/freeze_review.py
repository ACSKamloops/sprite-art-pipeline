from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
BASE=Path('/home/astra/artifacts/emberwake-rowan-contact-transition-review-v1')
OUT=BASE/'review'
INPUT=BASE/'input/INPUTS.json'
data=json.loads(INPUT.read_text())
items=[x for v in data['variants'].values() for seq in v.values() for x in seq]+data['context']
checks=[]
for item in items:
 actual=hashlib.sha256((BASE/'input'/item['path']).read_bytes()).hexdigest()
 checks.append({'path':item['path'],'expected':item['sha256'],'actual':actual,'ok':actual==item['sha256']})
assert len(checks)==63 and all(x['ok'] for x in checks)
initial=json.loads((OUT/'input-verification-before.json').read_text())
assert initial['inputs_json_sha256']==hashlib.sha256(INPUT.read_bytes()).hexdigest()
assert not (OUT/'report.md').exists() and not (OUT/'report.json').exists() and not (OUT/'OUTPUTS.sha256').exists()
now=datetime.now(timezone.utc).isoformat()
(OUT/'input-verification-after.json').write_text(json.dumps({'count':63,'all_match':True,'unchanged_since_before':True,'inputs_json_sha256':hashlib.sha256(INPUT.read_bytes()).hexdigest(),'files':checks},indent=2)+'\n')
score_A={'appearance':7.0,'identity':8.5,'motion_readability':4.5,'game_usefulness':5.5}
score_B={'appearance':6.7,'identity':8.4,'motion_readability':5.0,'game_usefulness':5.6}
pairs=[
 {'pair':'00->01','A':'First dominant extended foot continues; the other remains tucked. Small ankle/torso progression, no apparent support exchange.','B':'Identical to A.'},
 {'pair':'01->02','A':'Extended shin straightens and toe draws inward; tucked foot stays on the same side. A plausible passing approach, with the same dominant support track.','B':'Identical to A.'},
 {'pair':'02->03','A':'Legs narrow into overlap under the pelvis. Boot contours remain drawable, but overlap obscures which knee feeds which boot.','B':'Identical to A.'},
 {'pair':'03->04','A':'Continues the crossed/overlapped stance with the first dominant boot still extended; opposite support is weak.','B':'Opposite boot is now clearly lower and extended, a better counterphase silhouette. Exchange occurs abruptly; enlarged rounded boot and newly broad light thigh pop against 03.'},
 {'pair':'04->05','A':'Moves into a compact two-knee shape; the alternate lower boot becomes easier to read, but the support handoff arrives late and is cramped.','B':'Opposite-foot role continues into 05 more intelligibly. The 04 boot shrinks/changes toe and cuff volume at 05, reducing material continuity.'},
 {'pair':'05->06','A':'One knee visibly rises while the other boot remains lower. This is the clearest alternate half-cycle hint, but compressed depth and little longitudinal travel make it read partly as a knee lift.','B':'Identical to A.'},
 {'pair':'06->07','A':'Returns quickly to the first extended-foot silhouette. A readable extension, but alternate support has a short, compressed interval.','B':'Both thighs and boot cuffs become more exposed and regular. Better leg separation in a still, but a new pants/boot construction appears suddenly; roles are less persistent than the silhouette alone suggests.'},
 {'pair':'07->00','A':'Relatively compatible pose family: extended toe settles and tucked leg stays recognizable. Closure is visually less disruptive, but repeats the dominant-foot emphasis.','B':'The broad exposed shorts/cuffs at 07 collapse back into 00\'s tucked rear leg and slimmer boot construction. No head/root snap, but a lower-body shape/contact-intent pop remains.'}
]
report={
 'review_type':'Independent anonymous full-cycle visual review',
 'frozen_utc':now,
 'status':'Frozen once; no unchanged rerating authorized or performed.',
 'allowed_inputs':{'manifest':str(INPUT),'nominated_png_count':63,'hashes_before':True,'hashes_after':True,'input_manifest_unchanged':True,'other_mapping_history_project_docs_skills_or_grades_read':False},
 'conditions':{'stage':[128,128],'pivot':[64,112],'game_scale':0.66,'proxy_pixels':[84,84],'hold_seconds':9/160,'loop_seconds':0.45,'views':['native','nearest-neighbor 2x','84-pixel nearest-neighbor proxy'],'backgrounds':['light','dark','ground grid with pivot-height reference'],'every_cel_and_cyclic_pair_including_07_to_00_inspected':True},
 'scope':{'test_walks':'A and B southeast and southwest, eight cels each','context_only':'Appearance and east/south/west idle and walk imagery; no context-cycle ratings','continuous_human_playback_observed':False,'world_contact_verified':False},
 'verdict':'No clean whole-cycle winner. B improves opposite-support intent at 04 and has a slight whole-cycle legibility advantage, while A has more consistent boot/pants rendering and a less disruptive closure. Neither demonstrates a fully convincing alternating walk from this evidence.',
 'scores_0_to_10':{'A':score_A,'B':score_B},
 'score_basis':{'appearance':'Rendering, silhouette and material/volume coherence across the whole cycle; no reward for changed pixels, movement amplitude, cel count, or export correctness.','identity':'Retention of the supplied hair, face, blue/gold tunic, silver armor, cream trousers and brown leather vocabulary.','motion_readability':'Persistent projected support/swing roles and transitions across all eight steps, including closure.','game_usefulness':'Readability and consistency at 84-pixel proxy under all three backgrounds. No runtime or world-contact certification.'},
 'directional_assessment':{'southeast':'Same principal defects and preference pattern as southwest. First dominant extended boot is on screen right; use screen-space descriptions rather than assigning anatomical left/right through overlaps.','southwest':'Same principal defects and preference pattern as southeast, mirrored in projection. First dominant extended boot is on screen left. No warranted score difference from southeast.'},
 'local_pose_preferences':{'04':'Prefer B for blocked support-role intent and separation; prefer A\'s established boot/material vocabulary. This is not an endorsement of B\'s 03->04->05 transition.','07':'B is easier to parse as two legs in a still. Prefer A for volume and 07->00 continuity. B\'s isolated separation does not warrant a whole-cycle art advantage.'},
 'whole_cycle_findings':[
  'First dominant foot remains visually favored through 00,01,02 and the overlapped 03. A carries this through 04; B starts opposite apparent support at 04. Neither supplies equally convincing sustained longitudinal swing and support travel for both tracked feet.',
  '05->06 shows a brief knee lift, which is useful but does not by itself establish the full hip-knee-ankle-foot trajectory or planted weight transfer.',
  'B04 introduces a larger, rounder boot and broad light thigh; B07 changes cuff/shorts construction. Brown/cream palette remains, but boot/pants volume is not conserved through their neighboring cels.',
  'In 02->03->04, overlap weakens anatomical knee-to-boot tracking. B04 and B07 make the chains more separated in the individual still, but their changes do not preserve those chains smoothly across neighbors. No detached upper-body part was observed.',
  'Head, hair, shoulders and tunic remain coherent; there is no conspicuous global root or upper-body teleport at the changed poses or closure. Stable upper body is not evidence of correct foot contacts.',
  'At 84 pixels the face/blue-gold/silver identity survives on light, dark and ground. Fine cuff highlights and depth cues collapse, leaving alternating lower-body widths and occasional foot-shape pops more visible than reliable tracked support.',
  'Perspective can place valid feet at different screen-space heights. The drawn ground guide is a diagnostic reference, not a requirement that both soles occupy y=112.'
 ],
 'cyclic_pairs':{'southeast':pairs,'southwest':pairs},
 'smallest_warranted_next_repair':'Repair the 03->04->05 lower-body transition in one diagonal first: retain B04\'s opposite-support intent, redraw its cream thigh and brown boot to match the volumes, cuff language and knee-to-ankle chain of 03/05, and trace both foot roles through all eight cels. Inspect the resulting full loop at 84 pixels before propagating the repair. B07 needs a separate 06->07->00 continuity repair; do not infer that an unrendered A/B hybrid passes.',
 'limits':[
  'Assessment used ordered stills and all adjacent-pair diagnostics; exact 9/160-second holds are known from the manifest, but continuous human real-time playback was not observed.',
  'An 84-pixel nearest-neighbor proxy approximates 128*0.66=84.48 pixels. It does not reproduce unknown engine filtering, subpixel positioning, compositing or camera behavior.',
  'Projected support and swing are visual inferences. There is no actor translation, speed, ground plane, collision, shadow timing or in-engine locomotion evidence to verify planting, sliding, penetration, world contact or runtime loop feel.',
  'Cardinal imagery and appearance establish identity and turn context only; they were not promoted to walk acceptance evidence.',
  'Scores express this bounded visual judgment, not a measured universal scale. Differences of a few tenths are small tradeoffs, not statistical certainty.'
 ],
 'diagnostics_viewed':['southeast-native.png','southeast-nearest2x.png','southeast-proxy84.png','southwest-native.png','southwest-nearest2x.png','southwest-proxy84.png','southeast-all-cyclic-pairs.png','southwest-all-cyclic-pairs.png','context-east.png','context-south.png','context-west.png'],
 'source_or_canonical_edits':False
}
md=f'''**Independent anonymous walk review — frozen {now}**

No clean whole-cycle winner. B improves opposite-support intent at cel 04 and earns a small motion-readability advantage. A keeps more consistent boot/pants rendering and a less disruptive 07→00 join. Neither gives a fully convincing alternating walk in this bounded evidence.

All 63 nominated PNG hashes matched before and after inspection; INPUTS.json also remained unchanged. I read only that manifest, its nominated PNGs and my own diagnostics. No mapping, history, project documents, skills, other grades, source or canonical assets were read or edited.

| Whole-cycle score, 0–10 | A | B |
| --- | ---: | ---: |
| Appearance | 7.0 | 6.7 |
| Identity | 8.5 | 8.4 |
| Motion readability | 4.5 | 5.0 |
| Game usefulness | 5.5 | 5.6 |

The same score judgment applies to both southeast and southwest; the principal strengths and defects are mirrored. These small score gaps express a tradeoff, not measurement precision. Appearance considers rendering and coherent materials through the whole gait. Identity compares the supplied appearance/cardinal context. Motion considers trackable foot roles through every cyclic pair. Game usefulness concerns the 84-pixel proxy under light, dark and ground views. More movement, distinct feet, changed pixels, cel count and export correctness receive no art credit.

The copper hair, readable blue eyes, blue/gold tunic, silver shoulder armor, cream trousers and brown leather keep the actor recognizable. Head, hair, shoulders and torso stay coherent through both loops; I see no conspicuous global root or upper-body teleport. At small scale those identity anchors survive. The primary weaknesses are below the pelvis.

The first dominant extended boot stays visually favored through 00/01/02 and the overlapped 03. A largely continues that dominance at 04. B04 finally supplies a clear opposite lower/extended boot. That is a useful counterphase statement, but its larger rounded boot and broad cream thigh arrive abruptly. At 05→06 the opposite knee rises distinctly; a brief knee lift is not sufficient evidence that both feet have completed persistent support and swing paths. At 07 the first dominant stance returns quickly. Consequently B suggests alternation better, but does not solve the whole gait.

**Local pose preference versus whole-cycle judgment**

- 04: Prefer B's support-role blocking and separation. Its 03→04→05 boot/thigh volume is weaker than A's established material treatment; the isolated pose does not justify a whole-cycle appearance increase.
- 07: B offers clearer two-leg separation in a still. Prefer A for boot/pants consistency and closure. B changes exposed shorts/cuff construction at 06→07 and collapses back into 00's tucked rear-leg construction at 07→00.
- Anatomical tracking: 02→03→04 narrows the legs into overlap, making knee-to-boot assignment uncertain. B's changed cels separate those chains locally but do not carry them smoothly through the neighboring cels. I did not observe an independently detached upper-body part.
- At 84 pixels, fine cuff shading and depth cues diminish; leg-width changes and foot-volume pops compete with the desired support/swing read. Both are usable as recognizable diagonal character movement, with substantial gait qualifications.

**Every cyclic pair inspected**

The following applies to southeast and southwest; the first dominant boot is screen-right in southeast and screen-left in southwest. I avoid claiming anatomical left/right through the ambiguous overlaps.

| Pair | A | B |
| --- | --- | --- |
'''
for p in pairs: md+=f"| {p['pair'].replace('->','→')} | {p['A']} | {p['B']} |\n"
md+='''
Both direction-specific all-pairs sheets were inspected separately, including 07→00. All 32 test cels were viewed on light, dark and ground backgrounds at native 128, nearest-neighbor 2× and 84-pixel proxy sizes. All 31 context PNGs were inspected as identity/turn context only.

**Smallest warranted next repair**

Repair 03→04→05 below the pelvis in one diagonal first. Retain B04's opposite-support intent, but match the cream thigh, boot volume, cuff language and knee-to-ankle chain to 03/05. Trace both feet through all eight cels, then inspect the complete loop at 84 pixels before propagating the repair. B07 still requires its own 06→07→00 continuity repair. An unrendered hybrid of A and B has not been reviewed or scored.

**Evidence limits**

The supplied stage is 128×128 with pivot (64,112), game scale 0.66, eight equal 9/160-second holds and a 0.45-second loop. I inspected still chronology and every adjacent pair; continuous human playback at that speed was not observed. The 84-pixel nearest-neighbor proxy approximates 84.48 pixels and does not reproduce unknown engine filtering or subpixel motion.

Support/swing labels are projected visual inferences. The ground grid and pivot-height line are comparison aids; valid diagonal feet can have different screen heights. No actor translation, velocity, camera, ground collision or timed shadow evidence was supplied, so planted world contact, sliding, penetration and runtime loop feel are unverified. Cardinal walks and idles supplied identity and turn context, not physical-contact certification.

This report and its JSON scores are frozen once. No unchanged rerating was performed. OUTPUTS.sha256 covers the final review outputs other than the manifest itself.
'''
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'report.md').write_text(md)
(OUT/'FROZEN.json').write_text(json.dumps({'frozen_utc':now,'report':'report.md','structured_report':'report.json','input_pngs_verified_before_and_after':63,'input_manifest_unchanged':True,'scores_frozen':True,'no_unchanged_rerating':True,'output_manifest':'OUTPUTS.sha256','self_hash_excluded':'OUTPUTS.sha256'},indent=2)+'\n')
manifest=[]
for p in sorted(OUT.iterdir()):
 if p.is_file() and p.name!='OUTPUTS.sha256':
  manifest.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")
(OUT/'OUTPUTS.sha256').write_text('\n'.join(manifest)+'\n')
print(json.dumps({'frozen_utc':now,'input_pngs':63,'before_after_match':True,'output_count':len(manifest),'report_sha256':hashlib.sha256((OUT/'report.md').read_bytes()).hexdigest(),'json_sha256':hashlib.sha256((OUT/'report.json').read_bytes()).hexdigest(),'output_manifest_sha256':hashlib.sha256((OUT/'OUTPUTS.sha256').read_bytes()).hexdigest()}))
