from pathlib import Path
from fractions import Fraction
import json,hashlib,datetime
ROOT=Path('/home/astra/artifacts/emberwake-source-legs-review-v2/input');OUT=Path('/home/astra/artifacts/emberwake-source-legs-review-v2/review');CONTROL=Path('/home/astra/artifacts/emberwake-complete-boots-review-v1/review')
for n in ['report.md','report.json','SHA256SUMS']:
 assert not (OUT/n).exists(),f'Refusing to rewrite frozen {n}'
m=json.loads((ROOT/'INPUTS.json').read_text());old=json.loads((CONTROL/'report.json').read_text());oldhash=json.loads((CONTROL/'input-hashes-before.json').read_text())
anchor=old['ratings']['B'];assert anchor=={'appearance':7.8,'identity':8.5,'motion_readability':6.8,'game_usefulness':7.2}
oldmap={e['path']:e['actual_sha256'] for e in oldhash['images']}
anchor_checks=[]
for direction in ['southeast','southwest']:
 for i in range(8):
  p=f'A/{direction}/{i:02}.png';current=hashlib.sha256((ROOT/p).read_bytes()).hexdigest();prior=oldmap[f'B/{direction}/{i:02}.png'];anchor_checks.append({'current_path':p,'prior_variant':'B','sha256':current,'matches_own_frozen_control':current==prior})
assert len(anchor_checks)==16 and all(e['matches_own_frozen_control'] for e in anchor_checks)
entries=[e for v in m['variants'].values() for seq in v.values() for e in seq]+m['context'];after=[]
for e in entries:
 got=hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest();after.append({'path':e['path'],'expected_sha256':e['sha256'],'actual_sha256':got,'verified':got==e['sha256']})
before=json.loads((OUT/'input-hashes-before.json').read_text());assert len(after)==79 and all(e['verified'] for e in after);assert {e['path']:e['actual_sha256'] for e in before['images']}=={e['path']:e['actual_sha256'] for e in after}
(OUT/'input-hashes-after.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'images':after},indent=2)+'\n')
ratings={'A':dict(anchor),'B':{'appearance':8.0,'identity':8.5,'motion_readability':7.0,'game_usefulness':7.4},'C':{'appearance':8.0,'identity':8.5,'motion_readability':6.5,'game_usefulness':7.0}}
B_cels={
 '00':'Unchanged low alpha / tucked beta contact-like pose. Clear boots and familiar costume volumes.',
 '01':'Unchanged near-contact arrangement; small leg-silhouette travel still risks a perceptual plateau with 00.',
 '02':'Unchanged separated boots, with a straighter/narrower low alpha toe. Roles remain readable.',
 '03':'New fuller rounded proximal trousers replace the narrow columns. Both boots stay visible; knee-to-cuff continuity is improved.',
 '04':'Unchanged beta-low / alpha-raised opposite pose. Its newly low knee/boot remains broader than adjacent poses.',
 '05':'Unchanged two-boot separation after exchange. Beta-low boot narrows/turns from 04.',
 '06':'Unchanged clear raised alpha knee and low beta boot; a stylized but connected lifted leg.',
 '07':'New fuller bent trousers and cuff attachment read more like 06/00 volumes. The two boots remain legible; the recovery is still quick.'}
C_cels={
 '00':'B00 contact-like pose: alpha low, beta tucked.',
 '01':'Exact continuation of C00; combined visible hold is 112.5ms.',
 '02':'B03 passing/neutral pose: both boots visible and closer to the body, with repaired rounded trousers.',
 '03':'Exact continuation of C02; combined visible hold is 112.5ms.',
 '04':'B04 opposite contact-like pose: beta low, alpha tucked.',
 '05':'Exact continuation of C04; combined visible hold is 112.5ms.',
 '06':'B03 passing/neutral pose reused for the return half; same shapes as C02.',
 '07':'Exact continuation of C06; combined visible hold is 112.5ms.'}
B_pairs={
 '00->01':('minor','Unchanged small leg travel/plateau risk; a near-hold, not an exact duplicate.'),
 '01->02':('minor','Unchanged toe/shaft straightening is noticeable but roles remain coherent.'),
 '02->03':('minor','The convergence now retains fuller trouser volume and two readable boots. Better than the anchored A03 narrow columns.'),
 '03->04':('minor-to-moderate','Clear alpha-to-beta low-role exchange. Fuller 03 trousers reduce the clothing pulse, but the beta-low boot/knee in 04 still changes breadth conspicuously.'),
 '04->05':('minor','Unchanged broad-to-narrow/turned beta-low boot; the local whole-boot volume issue is not repaired by 03/07 clothing edits.'),
 '05->06':('acceptable','Unchanged readable lift with attached knee/cuff/boot. No demonstrated role interchange.'),
 '06->07':('minor-to-moderate','Bent trouser/cuff volume is materially more consistent than A07. Return is still fast; the whole-boot orientation change is still noticeable.'),
 '07->00':('minor','Better fuller trouser continuity than A07->00. No gross pose reset; silhouette travel into 00/01 remains limited.')}
C_pairs={
 '00->01':('intentional hold','Exact duplicate, forming 112.5ms of the first contact-like pose. A held drawing is not by itself a defect.'),
 '01->02':('minor-to-moderate','Contact-like to passing/neutral changes both boot configurations in one jump. Two roles are readable, but no recovery arc is drawn between them.'),
 '02->03':('intentional hold','Exact duplicate, forming 112.5ms of neutral/passing. This neutral pose occupies one quarter of the loop here.'),
 '03->04':('minor-to-moderate','Passing to opposite contact-like pose clearly alternates the low role. The B03->B04 breadth change remains exposed.'),
 '04->05':('intentional hold','Exact duplicate, forming 112.5ms of the opposite contact-like pose.'),
 '05->06':('moderate','Exact reverse of the C03->C04 image change. Reusing the same neutral geometry makes the return more like a reversible march/rock than a distinct recovery.'),
 '06->07':('intentional hold','Exact duplicate, forming the second 112.5ms neutral/passing hold; neutral totals 225ms, half the loop.'),
 '07->00':('minor-to-moderate','Exact reverse of the C01->C02 image change. It closes coherently but supplies no distinct second-half arc; no whole-character/yaw reset is apparent.')}
seqs=[]
for v in ['B','C']:
 for direction in ['southeast','southwest']:
  alpha_side='screen right' if direction=='southeast' else 'screen left';beta_side='screen left' if direction=='southeast' else 'screen right';notes=B_cels if v=='B' else C_cels;pnotes=B_pairs if v=='B' else C_pairs
  seqs.append({'variant':v,'direction':direction,'ratings':ratings[v],
   'projected_roles':{'alpha':f'The low/forward boot on {alpha_side} in 00. Persistent projected role, not an anatomical side.',
    'beta':f'The opposite, tucked/higher boot on {beta_side} in 00.',
    'tracking':('00-02 alpha low/beta tucked; 03 both visible during convergence; 04-06 beta low/alpha raised; 07-00 alpha returns low/beta tucked.' if v=='B' else '00-01 alpha low/beta tucked; 02-03 both converge; 04-05 beta low/alpha tucked; 06-07 the same neutral geometry returns before alpha-low 00.'),
    'finding':'No definite foot interchange demonstrated. C has weaker directional recovery information, not a proven anatomical swap. Equal sole Y and fixed anatomical screen sides were not required.'},
   'cels':[{'cel':f'{i:02}','inspected':True,'observation':notes[f'{i:02}']} for i in range(8)],
   'cyclic_pairs':[{'pair':f'{i:02}->{(i+1)%8:02}','inspected':True,'severity':pnotes[f'{i:02}->{(i+1)%8:02}'][0],'observation':pnotes[f'{i:02}->{(i+1)%8:02}'][1]} for i in range(8)]})
report={
 'status':'frozen single declared follow-up; not a new cold review',
 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':{'input_root':str(ROOT),'output_root':str(OUT),'input_manifest_sha256':hashlib.sha256((ROOT/'INPUTS.json').read_bytes()).hexdigest(),
  'images_verified':79,'B_C_walk_cels_inspected':32,'B_C_cyclic_pairs_inspected':32,'scales':['native128','nearest2x256','nearest84proxy'],'backgrounds':['light#e8e7db','dark#181e27','ground#576546'],
  'context_use':'Nominated cardinal/appearance context is identity/turn only, already inspected in this reviewer\'s own frozen control; matching context hashes were reverified here.',
  'outside_material_read':'Only nominated input and this reviewer\'s own frozen control report/hash record. No parent mappings, producer docs, skills or other agents\' work.',
  'input_mutation':False,'canonical_repo_access':False,'target_number_supplied':False},
 'anchor':{'current_variant':'A','prior_own_variant':'B','prior_frozen_report':str(CONTROL/'report.json'),'prior_report_sha256':hashlib.sha256((CONTROL/'report.json').read_bytes()).hexdigest(),
  'prior_ratings_retained_exactly':True,'rerated':False,'ratings':anchor,'byte_identity_checks':anchor_checks},
 'verification':{'before_verified':79,'after_verified':79,'mismatches':0,'before_equals_after':True,'art_credit_for_exactness_frame_count_uniqueness_or_fewer_drawings':False},
 'rating_scale':'Absolute subjective 0-10 for this compact RPG use: 0 unusable, 5 recognizable but visibly rough, 10 exceptional finished art. Decimal changes are small judgments, not measured precision.',
 'ratings':ratings,
 'preference':'B overall: modest actual clothing/attachment improvement over the unchanged A anchor, with more informative recovery than C. C is a viable deliberate compact march but not the preferred organic walk.',
 'B_vs_A':{'actual_change':'Only 03 and 07 differ in both directions. New 03 restores rounded proximal trouser volume; new 07 replaces pinched light shapes with fuller bent trousers/cuff attachment.',
  'perceived_repair':'03 now fits the neighboring trouser material/volume better, and 06->07->00 has less clothing-volume restoration/popping. Both boots remain separate. This earns a modest improvement, not a whole-cycle reclassification.',
  'unchanged_limits':'00->01 plateau, 04->05 whole-boot breadth/angle change, shallow arms and rigid torso remain. 06->07 still turns rapidly; a clothing-only repair cannot establish smoother cadence or contact.'},
 'C_vs_B':{'verified_pose_slots':['B00','B00','B03','B03','B04','B04','B03','B03'],
  'logical_sequence':['contact-like B00','passing/neutral B03','opposite contact-like B04','passing/neutral B03'],
  'each_logical_hold_seconds':float(Fraction(9,80)),'loop_seconds':float(Fraction(9,20)),
  'benefits':'Distinct alpha-low and beta-low poses alternate at even 225ms spacing. Four equal visible holds are deliberate and easier to parse as a four-beat pattern. Restrained amplitude avoids some B05/06 extremes.',
  'costs':'The same nearly neutral passing geometry occupies half the cycle. Each return retraces a preceding image change; separate second-half recovery and most body bob disappear. The result suggests a more mechanical march/rock. This is a pose-order/hold judgment, not a penalty for three drawings.',
  'hold_finding':'Four exact adjacent duplicate pairs are intentional 112.5ms holds. Their duration and what poses receive them matter; repeated pixels are not automatically defects.'},
 'appearance_identity':'B and C share the strong face, spiky hair, blue/gold tunic, silver shoulders, brown boots and repaired clothing. C reuses B drawings, so it earns no appearance increase solely from simplification. Dark backgrounds soften the darkest boot outlines, but highlights preserve the figures and role separation at84px.',
 'sequences':seqs,
 'smallest_meaningful_next_repair':{
  'B':'If continuing, reconcile the newly low whole-boot/cuff breadth in04 with03 and05. The proximal clothing repairs are useful; do not keep repainting them to chase a score. Check actual playback before adjusting the shared00->01 contact dwell.',
  'C':'A bounded next ordering test would use repaired B07 for C06/07 instead of reusing B03, retaining four112.5ms holds and.45s duration. Its purpose is a distinct return path, not an extra-drawing bonus. This has not been generated or rated.'},
 'perception_limits':['Static cels, ordered strips and all eight cyclic pairs were inspected for B/C SE/SW; no continuous human playback was observed.',
  'Still chronology cannot certify exact perceived cadence at the supplied holds or physical world contact, planting, friction or game translation.',
  'The84px nearest proxy approximates0.66 canvas scale. Engine filtering, camera and terrain may alter readability.',
  'This declared follow-up retains the prior A judgment. It is neither a newly cold independent score nor evidence that unchanged art improved.'],
 'artifacts':{'full_cel_sheets':9,'cyclic_pair_sheets':4,'A_B_changed_cel_comparisons':2,'hash_ledger':'SHA256SUMS','pixel_facts':'diagnostic-pixel-facts.json; raw RGBA facts only'}}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['# Source-legs and cadence follow-up — frozen','',
'B is preferred overall. Its new 03/07 clothing volumes are a modest visible repair over the frozen A control. C supplies a clear, deliberate four-beat alternating step, but loses the distinct recovery and much of the body response, giving it a more mechanical march quality.','',
'This is one declared follow-up using my own frozen control, not a new cold review. Current A is byte-identical to my previous B in all16 walk images. Its existing scores and judgment are retained unchanged; A was not rerated.','',
'| Variant | Appearance | Identity | Motion readability | Game usefulness |','|---|---:|---:|---:|---:|']
for v in ['A','B','C']:
 r=ratings[v];label='A — retained anchor' if v=='A' else v;lines.append(f"| {label} | {r['appearance']:.1f} | {r['identity']:.1f} | {r['motion_readability']:.1f} | {r['game_usefulness']:.1f} |")
lines+=['','Absolute subjective0–10 ratings for this compact RPG use:0 unusable,5 recognizable but visibly rough,10 exceptional finished art. SE/SW received the same B/C scores after separate inspection. Small decimal differences are judgments. Source exactness, added frames, uniqueness and fewer drawings earn no art credit. No target number was supplied.','',
'## B compared with retained A','',
'03 replaces narrow straight trouser columns with fuller rounded volumes that fit the surrounding cels better.07 improves the bent trouser/cuff attachment and reduces the pinched light shapes visible in the control. Both whole boots remain legible. The clearest actual repair is clothing continuity through06→07→00, with a smaller improvement through02→03→04.','',
'These are local improvements.00→01 still has little leg-silhouette travel.04→05 still changes the newly low boot from broad to narrower/turned.06→07 still returns quickly, and arms/torso remain restrained. The new clothing does not establish contact or a smooth exact-time cadence.','',
'## C compared with B','',
'C verifies as B00,B00,B03,B03,B04,B04,B03,B03. Its four visible holds are each112.5ms, totaling.45s. Distinct alpha-low and beta-low contact-like poses alternate225ms apart. This gives an understandable, even four-beat pattern; held drawings are a valid choice.','',
'The cost is in the selected order and duration: the same near-neutral passing geometry occupies225ms, half the loop. C05→06 exactly reverses C03→04, and C07→00 exactly reverses C01→02. A separate recovery arc and much of B’s bob disappear. This suggests a more mechanical march/rock while remaining legible as alternating steps. C is not penalized merely for using three drawings, and B gets no credit merely for having eight.','',
'C uses the same repaired art, so its appearance and identity scores remain comparable to B. There is no appearance bonus for suppressing poses. Warm boot highlights preserve visibility on dark backgrounds, although the darkest edges soften. Both remain usable at84px.','',
'## Persistent projected roles','',
'Alpha is low/forward in00: SE screen right, SW screen left. Beta begins higher/tucked on the opposite side. These are persistent projected roles, not anatomical left/right. In B, alpha is low00–02, both converge visibly in03, beta becomes low in04–06, and alpha returns low through07→00. In C, alpha is low00/01, both converge02/03, beta is low04/05, and the same neutral geometry returns06/07. No definite foot interchange is demonstrated. C has weaker directional recovery information; that is not proof of a swap. Equal sole Y and fixed anatomical screen sides were not required.','',
'## Every cel','',
'Each cel was inspected separately for SE/SW at native128, nearest2× and84px proxy, on light/dark/ground backgrounds.','',
'| Slot | B | C |','|---|---|---|']
for i in range(8):
 k=f'{i:02}';lines.append(f'| {k} | {B_cels[k]} | {C_cels[k]} |')
lines+=['','## Every cyclic adjacent pair','','These notes apply to the separately inspected SE/SW sequences with projected screen sides reversed. report.json records each sequence explicitly.','','| Pair | B | C |','|---|---|---|']
for i in range(8):
 p=f'{i:02}->{(i+1)%8:02}';lines.append(f'| {p.replace("->","→")} | {B_pairs[p][0]}: {B_pairs[p][1]} | {C_pairs[p][0]}: {C_pairs[p][1]} |')
lines+=['','## Smallest meaningful next step','',report['smallest_meaningful_next_repair']['B'],'',report['smallest_meaningful_next_repair']['C'],'',
'## Verification and limits','',
'All79 nominated image hashes match before and after; the checks agree. All32 B/C cels and32 cyclic pairs were inspected, including07→00. Nine full-cel sheets, four lower-body cyclic-pair sheets and two A/B changed-cel comparison sheets are included. Only nominated input and my own frozen report/hash record were read; no producer docs, parent mappings, skills or other agents’ work. Inputs and canonical repo were not changed.','',
'This is static chronology and pair perception. No continuous human playback was observed, and the report does not certify exact-time cadence or physical world contact, planting, friction or translation. The84px nearest proxy approximates the stated0.66 canvas scale; actual engine sampling may differ.','',
'Artifacts: `report.json`, `input-hashes-before.json`, `input-hashes-after.json`, `diagnostic-pixel-facts.json`, `sheet-*.png`, `pairs-*.png`, `compare-A-B-*.png`, and the frozen output ledger `SHA256SUMS`.','']
(OUT/'report.md').write_text('\n'.join(lines))
ledger=[]
for p in sorted(OUT.rglob('*')):
 if p.is_file() and p.name!='SHA256SUMS':ledger.append(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(OUT)}')
(OUT/'SHA256SUMS').write_text('\n'.join(ledger)+'\n')
for p in OUT.rglob('*'):
 if p.is_file():p.chmod(0o444)
print(json.dumps({'status':'frozen declared follow-up','anchor_retained':anchor,'ratings':ratings,'verified_before':79,'verified_after':79,'anchor_images_byte_verified':16,'ledger_entries':len(ledger),'report_sha256':hashlib.sha256((OUT/'report.md').read_bytes()).hexdigest(),'json_sha256':hashlib.sha256((OUT/'report.json').read_bytes()).hexdigest(),'ledger_sha256':hashlib.sha256((OUT/'SHA256SUMS').read_bytes()).hexdigest()},indent=2))
