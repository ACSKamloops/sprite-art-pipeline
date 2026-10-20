from pathlib import Path
from PIL import Image
import hashlib,json,datetime
ROOT=Path('/home/astra/artifacts/emberwake-brann-07-followup-review-v1');INP=ROOT/'input';OUT=ROOT/'review';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
before=json.loads((OUT/'input-hashes-before.json').read_text());m=json.loads((INP/'INPUTS.json').read_text());es=[e for v in m['variants'].values() for seq in v.values() for e in seq]+m['context'];rs=[]
for e in es:
 h=hashlib.sha256((INP/e['path']).read_bytes()).hexdigest();assert h==e['sha256'];assert h==next(x['sha256'] for x in before['images'] if x['path']==e['path']);rs.append({'path':e['path'],'sha256':h})
assert len(rs)==63;mh=hashlib.sha256((INP/'INPUTS.json').read_bytes()).hexdigest();assert mh==before['manifest_sha256']
with (OUT/'input-hashes-after.json').open('x') as f:json.dump({'utc':now,'count':63,'all_match':True,'all_unchanged':True,'manifest_sha256':mh,'images':rs},f,indent=2);f.write('\n')
assert Image.open(INP/'B/southeast/03.png').getpixel((68,98))[3]==243
assert Image.open(INP/'B/southwest/03.png').getpixel((60,98))[3]==243
A={'appearance':7.5,'identity':8.5,'motion_readability':7.0,'game_usefulness':7.0};B={'appearance':7.5,'identity':8.5,'motion_readability':7.5,'game_usefulness':7.5}
common={
'00->01':'Unchanged coherent small tuck/lift; P stays lower/forward and Q bends behind.',
'01->02':'Unchanged P retraction/narrowing, Q tucked; compact foreshortening remains.',
'04->05':'Unchanged Q retracts under the body, P visible behind; some brown boot masses merge at84.',
'05->06':'Unchanged broad Q lower-boot volume into exit; P tucked on other projected track.'}
local={'A':{'02->03':'Carried earlier improvement: rounded Q boot/upper and reduced sole turn, but small tucked02 to larger03 remains brisk. Partial-alpha seam is still present.','03->04':'Carried coherent Q-forward support exchange with overlapping boots; partial-alpha seam still admits light ground locally.','06->07':'Carried primary weakness: P goes from tucked/hidden to a long outward shin and steeply pitched/sole-presenting boot. Static kick/pop risk remains.','07->00':'P stays forward/Q rear, but P rolls/flattens sharply. Less severe than06->07, yet visible.'},'B':{'02->03':'Same retained rounded Q recovery drawing, with two marked seam pixels now opaque. Brisk mass/position change remains.','03->04':'Same coherent support/boot-volume transition with local seam cleanup; no new shape or joint cost found.','06->07':'Improved: P returns through a shorter projected shin with a more natural rounded boot upper/toe and less sole-facing pitch. Knee/cuff/boot remain joined. Still a substantial one-hold reveal from06, not proven continuous contact.','07->00':'Improved: less boot roll/flattening and a more natural bridge into00. P remains forward and Q rear; stride remains readable without an obvious static closure seam.'}}
pairs={v:{d:{f'{i:02}->{(i+1)%8:02}':common.get(f'{i:02}->{(i+1)%8:02}',local[v].get(f'{i:02}->{(i+1)%8:02}')) for i in range(8)} for d in ['southeast','southwest']} for v in ['A','B']}
report={
'actor':'brann','review':'Changed07 plus03 seam follow-up, one frozen scoped judgment','frozen_utc':now,
'anchor':{'A_equals_prior03_followup_B':True,'verified_hash_matches':16,'source':'Own prior03-followup B SHA256 values from earlier manifest output already in this conversation. No previous files/reports reopened. Scores carried unchanged as instructed.','A_scores_carried_without_rerating':A,'changed_cels_each_view':['03','07'],'other12_view_cels_equal':True,'evidence':'anchor-and-change-scope.json'},
'sources':'Only new nominated63 PNGs, INPUTS.json and clock, plus own anchor hashes/scores already in conversation. No producer docs/maps/history/source, project source, other reports or skills.',
'coverage':{'walk_cels':32,'cyclic_pairs':32,'all8_pairs_per_sequence':True,'includes07to00':True,'contexts_identity_only':31,'scales':['native128','nearest2x256','nearest84 proxy at0.66','extra bilinear84 ground row'],'grounds':['light','dark','diagnostic green grid'],'diagnostic_sheets':25,'local_checks':'06/07/00 nearest3x;07 volume/joint light/dark/alpha nearest5x;03 exact changed-pixel samples.'},
'hashes':{'before63_match':True,'after63_match':True,'all63_unchanged':True,'INPUTS_json_unchanged':True},
'limits':['Static cels, chronology and cyclic pairs only; no observed normal-speed continuous human playback is claimed.','Manifest9/160s=56.25ms per cel,0.45s per loop. No engine, world translation, root speed, collision or physical foot-lock/contact test occurred.','Diagnostic grounds are contrast backgrounds, not contact planes. Normal depth overlap and differing sole Y are accepted.','Moderate confidence in local drawing/chronology improvement; actual-speed smoothness, weight and world contacts remain unverified.','Context establishes identity/facing only, not required gait mechanics.'],
'scores':{'A':A,'B':B},'score_delta_B_minus_A':{'appearance':0.0,'identity':0.0,'motion_readability':0.5,'game_usefulness':0.5},
'direction_scores':{'A':{d:A for d in ['southeast','southwest']},'B':{d:B for d in ['southeast','southwest']}},
'preference':{'variant':'B','strength':'clear local repair, modest overall increment','confidence':'moderate from static chronology','reason':'Less06->07 shin/sole-pitch jump and more natural07->00 boot bridge, with joined chunky leg/boot volume and readable stride at84.03 seam cleanup is coherent. This does not establish normal-speed planted contacts or eliminate other limitations.','baseline_not_rerated':True,'no_fidelity_pixel_count_exactness_bonus':True},
'foot_key':{'P':'Leg lower/forward at00:screen-right in SE,screen-left in SW, followed through cuff and cyclic return, never relabeled only by side.','Q':'Other leg initially bent behind, lower/forward at04-06 and bending back around07-00.','occlusion':'Normal crossing/overlap and different sole heights are accepted. No anatomical flip is inferred.'},
'local_findings':{'06_to07':'New P shin is less extended and boot exposes less sole; the boot emerges on a more plausible bridge from its tucked06 state. The reveal is still fast over one hold, so the prior weakness is reduced rather than certified absent in playback.','volume_and_join':'Knee/pants, cuff, boot shaft, heel and rounded toe remain substantial and connected. Shorter projection does not visibly collapse the leg into a thin tube or detach the boot. No clear new old-shape remnant or internal background split found.','closure':'P07 now resembles a sensible lead-in to P00 pitch/volume, and Q stays the rear/bent leg. Less flattening than A; no obvious new static07->00 seam.','tradeoff':'07 is a less extreme pose. Stride distinction remains adequate at84 in the inspected contexts; lower extremity is not automatically better, the coherent entry/exit is what earns the gain.','03_cleanup':'Exactly two pixels per view changed from partial alpha198/169 to255 with matching brown shading. Local light-ground seam specks are removed. The third near-opaque alpha243 sample at SE68,98/SW60,98 is unchanged and does not present a material open joint.'},
'03_cleanup_evidence':'03-seam-cleanup.json',
'cyclic_pair_observations':pairs,
'remaining_faults_or_limits':[
 {'id':'R02_03','severity':'low to medium','finding':'Brisk small-tucked02 to substantial Q03 recovery remains; the retained rounded upper/toe is better than the earliest drawing but the mass/position transition is still noticeable.'},
 {'id':'R06_07','severity':'reduced, residual timing uncertainty','finding':'P still emerges from a deeply tucked pose within one hold. Shin/sole snap is materially reduced; actual-speed perception and physical contact are not verified.'},
 {'id':'R_WEIGHT','severity':'low to medium','finding':'Hip/shoulder weight response remains modest; guarded fists-up style is legitimate.'},
 {'id':'R_CONTRAST','severity':'low/background dependent','finding':'Dark hair/pants/rear-boot separation remains weaker on dark ground; bright armor and face preserve identity. Some brown boot overlap softens far-leg detail at84.'}
],
'minimum_next_action':'No new07 or03 cleanup is compelled by the static checks. Preserve the improved projection and joins. Actual observed playback at supplied timing and separately world translation would be needed to decide whether remaining brisk02->03/06->07 transitions need more art. No additional trial/rerating is performed.',
'pixel_scope':'03 exactly2 changed pixels per view.07 lower-only bboxSE(62,86,91,117),SW(38,86,67,117). Six other cels per view are identical. Scope verification is not artistic credit.',
'freeze_policy':'One final frozen scoped judgment; no unchanged-baseline rerating or target chasing.'}
md=f'''# Brann changed-07 and 03-seam follow-up

Frozen once at {now}. **Prefer B.** It reduces the 06→07 shin/sole-pitch kick and bridges more naturally into 00, retaining connected chunky leg/boot volume and a readable stride at 84 pixels. The 03 seam cleanup also holds.

| /10 | A: carried frozen baseline | B |
|---|---:|---:|
| Appearance | 7.5 | 7.5 |
| Identity | 8.5 | 8.5 |
| Motion readability | 7.0 | 7.5 |
| Game usefulness | 7.0 | 7.5 |

A was **not rerated**. All 16 A hashes match the prior 03-follow-up B values already recorded in this conversation. B changes only lower 07 and exactly two 03 pixels per view; the other 12 view/cels are identical. The modest gains concern coherent entry/exit and readable volume, not fidelity, pixel count or exactness.

## Evidence and qualification

Only the new 63 PNGs/INPUTS.json and clock were read; own anchor hashes/scores were already in the conversation. No prior files/reports, producer docs/maps/history/source, project source, other reports or skills were read. All 63 hashes match before/after; images and INPUTS.json remain unchanged.

Coverage: all 32 cels and 32 cyclic pairs including 07→00, both facings at native 128, nearest 2× and nearest 84 proxy of 0.66 scale, on light/dark/diagnostic green grounds. Extra bilinear 84, 06/07/00 details and 07 light/dark/alpha checks are included in 25 bounded diagnostic PNGs. Context is identity/facing only.

**Static-cel/chronology perception only; no observed normal-speed continuous human playback.** Manifest timing is 9/160 s per cel (56.25 ms), 0.45 s per loop. No engine, world translation, root speed, foot-lock or physical-contact test occurred. Contrast grounds are not contact planes; normal overlap and unequal sole Y are allowed. Confidence is moderate locally; actual-speed smoothness, weight and world contacts remain unverified.

## Shin, cuff, boot and closure

P is the leg lower/forward at 00 (screen-right in SE, screen-left in SW), followed through its cuff and cyclic return. Q starts behind, becomes lower/forward at 04–06, and bends back around 07–00. Labels do not follow screen side alone.

A07 sends P from its tucked 06 position into a long outward shin and steeply pitched/sole-presenting boot. B07 uses a shorter projected shin and a rounded upper/toe with less exposed sole. Knee/pants, cuff, shaft, heel and toe remain substantial and connected; the leg does not become a thin tube or floating boot. No clear new old-shape remnant or internal background split appeared in the detailed checks.

P07 now leads into P00's boot pitch/volume more naturally, with less roll/flattening. Q remains the rear/bent leg; no obvious new static closure seam or identity inversion appears. 07 is less extreme, but stride distinction remains adequate at 84. The gain comes from the coherent 06→07→00 bridge, not from suppressing motion by itself. P still emerges over one hold, so actual-speed smoothness remains an open test.

**03 join:** SE (67,96)/(68,97), SW (61,96)/(60,97) now have alpha 255 versus 198/169, with matching brown shading. The two light-ground seam specks are removed. The third nearly opaque sample, SE (68,98)/SW (60,98), remains alpha 243 and does not present a material open joint. See `03-seam-cleanup.json`.

## Every cyclic pair, both facings

| Pair | Finding |
|---|---|
| 00→01 | Unchanged coherent small tuck/lift. |
| 01→02 | Unchanged P retraction/narrowing while Q stays tucked. |
| 02→03 | Retained rounded Q recovery; marked seam pixels cleaned. Brisk mass/position change remains. |
| 03→04 | Same coherent support/volume transition with the local seam cleaned. |
| 04→05 | Unchanged Q retraction/P rear visibility; brown masses partly merge. |
| 05→06 | Unchanged retained broad Q lower-boot volume. |
| 06→07 | B reduces shin extension/sole snap; connected boot still emerges substantially in one hold. |
| 07→00 | B reduces roll/flattening and preserves P-forward/Q-rear closure. |

## Remaining limits and minimum action

The brisk 02→03 recovery remains. The 06→07 reveal is reduced, not proven seamless in playback. Hip/shoulder weight response remains modest, although guarded fists-up motion is a legitimate style. Dark hair/pants/rear-boot contrast is weaker on dark ground, and overlapping brown boots soften some far-leg detail at 84.

No new 07 or 03 cleanup is compelled by these static checks. Preserve the improved projection and joins. Actual observed playback at the supplied timing, and separately world translation, would determine whether the remaining brisk transitions need further drawing work. No additional trial or rerating is performed here.
'''
for name,content in [('report.md',md),('report.json',json.dumps(report,indent=2)+'\n')]:
 with (OUT/name).open('x') as f:f.write(content)
files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='SHA256SUMS')
with (OUT/'SHA256SUMS').open('x') as f:
 for p in files:f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
for name in ['report.md','report.json','SHA256SUMS']:(OUT/name).chmod(0o444)
print('All63 inputs unchanged. Frozen once; ledger entries:',len(files))
for name in ['report.md','report.json','SHA256SUMS']:print(name,hashlib.sha256((OUT/name).read_bytes()).hexdigest())
