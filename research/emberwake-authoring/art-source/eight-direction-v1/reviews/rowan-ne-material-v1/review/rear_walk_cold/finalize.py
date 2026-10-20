from pathlib import Path
import hashlib,json
root=Path('/home/astra/artifacts/emberwake-rowan-ne-material-review-v1');src=root/'input';out=root/'review/rear_walk_cold'
before=json.loads((out/'hashes-before.json').read_text());after={'manifest_sha256':hashlib.sha256((src/'INPUTS.json').read_bytes()).hexdigest(),'files':[]}
for e in before['files']:
 h=hashlib.sha256((src/e['path']).read_bytes()).hexdigest();after['files'].append({'path':e['path'],'sha256':h,'unchanged':h==e['sha256']})
after['all_unchanged']=after['manifest_sha256']==before['manifest_sha256'] and all(e['unchanged'] for e in after['files']);assert after['all_unchanged']
(out/'hashes-after.json').write_text(json.dumps(after,indent=2)+'\n')
r={'reviewer':'rear_walk_cold','frozen':True,'actor':'rowan','scope':'hem and cream trouser material cleanup only','A':{'appearance':7.0,'identity':9.0,'motion_readability':6.5,'game_usefulness':6.5,'is_exact_prior_anchor':True},'B':{'appearance':7.25,'identity':9.0,'motion_readability':6.5,'game_usefulness':6.5},'preference':'B narrowly','directions':{'northeast':'B narrowly','northwest':'B narrowly'},'new_visible_knee_cuff_holes':False,'new_visible_boot_clipping':False,'visible_material_loss':False,'coverage':{'candidate_cels':32,'cyclic_pairs':32,'scales':[128,256,84],'backgrounds':['light','dark','diagnostic_ground']},'normal_speed_human_observation_established':False,'world_contact_certified':False,'png_hashes_verified_before_after':63,'manifest_unchanged':True}
(out/'ratings.json').write_text(json.dumps(r,indent=2)+'\n');print('Frozen review saved. All63PNG and manifest unchanged before/after.')
