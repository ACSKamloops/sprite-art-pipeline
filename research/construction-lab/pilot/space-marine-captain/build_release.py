"""Build a useful local game-art handoff only from fresh approved evidence."""
from pathlib import Path
import argparse, hashlib, json, math, shutil

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser()
    for name in ['candidate','legs','editable','primary','secondary','engine','material','output']:
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('Preserve frozen releases')
    candidate_sha=sha(a.candidate/'manifest.json')
    rejection_file=HERE/'user-rejection-v20.json'
    if rejection_file.exists():
        rejection=json.loads(rejection_file.read_text())
        if rejection['manifest_sha256']==candidate_sha and rejection['decision']=='rejected_by_user_visual_quality':
            raise ValueError('User rejected this exact candidate; historical reviewer scores cannot approve a new release')
    m=json.loads((a.candidate/'manifest.json').read_text())
    primary=json.loads(a.primary.read_text());secondary=json.loads(a.secondary.read_text())
    assert primary['input_fingerprint']==candidate_sha and secondary['manifest_sha256']==candidate_sha
    assert primary['overall_score']>=9 and secondary['weighted_score']>=9
    assert min(c['score']for c in primary['categories'])>=8.5
    assert min(secondary['scores'].values())>=8.5
    assert primary['gate']['passed'] and secondary['visual_threshold_met']
    assert not secondary['observed_critical_visual_failures']
    engine=json.loads(a.engine.read_text());material=json.loads(a.material.read_text())
    assert engine['manifest_sha256']==candidate_sha and engine['passed']
    assert material['actor_manifest_sha256']==candidate_sha and material['passed']
    assert material['leg_manifest_sha256']==sha(a.legs/'manifest.json')==m['leg_source_manifest_sha256']
    exchange=json.loads((a.editable/'receipt.json').read_text())
    assert exchange['candidate_manifest_sha256']==candidate_sha and exchange['all_layer_composites_exact_source']
    a.output.mkdir(parents=True)
    shutil.copytree(a.candidate/'frames',a.output/'sprites/frames')
    shutil.copy2(a.candidate/'manifest.json',a.output/'sprites/manifest.json')
    shutil.copy2(a.candidate/'walk-atlas.png',a.output/'sprites/walk-atlas.png')
    shutil.copy2(a.candidate/'walk-preview.gif',a.output/'captain-walk.gif')
    shutil.copytree(a.editable,a.output/'editable')
    legs=json.loads((a.legs/'manifest.json').read_text())
    support=[]
    # Match the actual GPU material test's episode-fixed integer support;
    # per-pose draw-root rounding can disagree at half-pixel boundaries.
    for frame in legs['frames']:
        targets={}
        for side,design in legs['registered_design']['legs'].items():
            if frame['legs'][side]['contact']:
                episode=math.floor(frame['phase']+design['phase_offset'])
                target=[design['rest_sole'][k]+legs['root_stride'][k]*(.3-design['phase_offset']+episode)for k in [0,1]]
                # Godot nearest integer is ties away from zero, not Python bankers.
                targets[side]=[math.floor(v+.5)if v>=0 else math.ceil(v-.5)for v in target]
        support.append({'frame':frame['key'],'support_world':targets})
    policy={'candidate_manifest_sha256':candidate_sha,'leg_manifest_sha256':sha(a.legs/'manifest.json'),
            'frames':support,'method':'GPU-tested source-attached fixed stance episode target; one shared complete-actor correction',
            'max_tested_correction_px':material['max_visual_physical_root_offset']}
    (a.output/'contact-policy.json').write_text(json.dumps(policy,indent=2)+'\n')
    (a.output/'proofs').mkdir()
    for name,path in [('primary-art.json',a.primary),('secondary-art.json',a.secondary),
                      ('engine.json',a.engine),('material.json',a.material)]:
        shutil.copy2(path,a.output/'proofs'/name)
    for path in [HERE/'release-preview.gd',ROOT/'pilot/captain72-godot/hold_clock.gd']:
        shutil.copy2(path,a.output/('preview.gd'if path.name=='release-preview.gd'else path.name))
    (a.output/'project.godot').write_text('''config_version=5
[application]
config/name="Captain Walk - reviewed game sprite"
run/main_scene="res://main.tscn"
[display]
window/size/viewport_width=960
window/size/viewport_height=760
[importer_defaults]
texture={"compress/mode": 0, "mipmaps/generate": false, "process/fix_alpha_border": false, "process/premult_alpha": false}
[rendering]
renderer/rendering_method="gl_compatibility"
textures/default_filters/use_nearest_mipmap_filter=false
textures/canvas_textures/default_texture_filter=0
''')
    (a.output/'main.tscn').write_text('''[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://preview.gd" id="1"]
[node name="CaptainWalk" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
script = ExtResource("1")
''')
    lines=['[gd_resource type="SpriteFrames" load_steps=73 format=3]','']
    for i,row in enumerate(m['frames']):
        assert sha(a.output/'sprites'/row['file'])==row['sha256']
        lines.append(f'[ext_resource type="Texture2D" path="res://sprites/{row["file"]}" id="{i+1}"]')
    entries=[f'{{"duration": {row["duration_ms"]*.06:.12g}, "texture": ExtResource("{i+1}")}}'
             for i,row in enumerate(m['frames'])]
    lines+=['','[resource]','animations = [{"frames": ['+',\n'.join(entries)+'], "loop": true, "name": &"combat_ready_walk", "speed": 60.0}]']
    (a.output/'captain-walk.tres').write_text('\n'.join(lines)+'\n')
    gate={'schema':'reviewed-captain-walk-release/v1','candidate_manifest_sha256':candidate_sha,
          'contact_policy_sha256':sha(a.output/'contact-policy.json'),
          'sprite_resource_sha256':sha(a.output/'captain-walk.tres'),
          'source_candidate':str(a.candidate.resolve()),'source_legs':str(a.legs.resolve()),
          'primary_score':primary['overall_score'],'secondary_score':secondary['weighted_score'],
          'scope':'One authored three-quarter combat-ready walk. User visual acceptance remains separate.',
          'frames':72,'cycle_ms':m['cycle_ms'],'release_builder_sha256':sha(Path(__file__)),
          'limits':['No other directions/actions inferred','No firearm variant','Conservative flat stance and shared draw correction; not 3D collision anatomy'],
          'frozen_inputs':{str(path.resolve()):sha(path)for path in [a.primary,a.secondary,a.engine,a.material,a.candidate/'manifest.json',a.legs/'manifest.json']}}
    (a.output/'approval.json').write_text(json.dumps(gate,indent=2)+'\n')
    shutil.copy2(HERE/'references/approved-256.png',a.output/'reference.png')
    player=(HERE/'animation-review/index.html').read_text()
    player=player.replace('<h1>Captain — source-bound animation review</h1>','<h1>Captain — reviewed combat-ready walk</h1>')
    player=player.replace('Candidate under review. Technical playback does not approve sprite quality. One combat-ready view; newly authored legs, fixed approved upper-body details. Movement uses the candidate\'s declared stride.',
        f'Independent art reviews: {gate["primary_score"]:.3f}/10 and {gate["secondary_score"]:.3f}/10. One authored view and walk. Native 256px sprites, exact timing, shared stance correction.')
    original="const query=new URLSearchParams(location.search);const candidate=query.get('candidate')||'assembled-v4';if(!/^assembled-v\\d+$/.test(candidate))throw Error('Invalid candidate name');const base='../'+candidate+'/';"
    assert original in player
    player=player.replace(original,"let candidate='reviewed_walk',contactPolicy;const base='sprites/';")
    old="const selectedRoot=f.physical_root;return{side,world:[foot[0]+selectedRoot[0],foot[1]+selectedRoot[1]]}"
    assert old in player
    player=player.replace(old,"return{side,world:contactPolicy.frames[n].support_world[side]}")
    old="manifest=await response.json();if(manifest.status!=='UNAPPROVED_EXPERIMENT')throw Error('Unexpected review state');"
    assert old in player
    new="const approval=await(await fetch('approval.json')).json();const manifestBytes=await response.arrayBuffer();if(await hash(manifestBytes)!==approval.candidate_manifest_sha256)throw Error('Changed approved manifest');manifest=JSON.parse(new TextDecoder().decode(manifestBytes));candidate=approval.source_candidate.split('/').at(-1);const contactBytes=await(await fetch('contact-policy.json')).arrayBuffer();if(await hash(contactBytes)!==approval.contact_policy_sha256)throw Error('Changed contact policy');contactPolicy=JSON.parse(new TextDecoder().decode(contactBytes));if(contactPolicy.candidate_manifest_sha256!==approval.candidate_manifest_sha256||contactPolicy.leg_manifest_sha256!==manifest.leg_source_manifest_sha256)throw Error('Changed contact source');"
    player=player.replace(old,new).replace("'../references/approved-256.png'","'reference.png'")
    (a.output/'index.html').write_text(player)
    receipt={'approval_sha256':sha(a.output/'approval.json'),
             'files':{str(path.relative_to(a.output)):sha(path)for path in sorted(a.output.rglob('*'))if path.is_file()}}
    (a.output/'release-files.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'output':str(a.output),'primary':gate['primary_score'],'secondary':gate['secondary_score'],'files':len(receipt['files'])}))


if __name__=='__main__':main()
