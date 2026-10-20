from pathlib import Path
import hashlib,json
root=Path('/home/astra/artifacts/emberwake-rear-walk-review-v1');out=root/'review/rear_walk_cold'
before=json.loads((out/'hashes-before.json').read_text());after={};ok=True
for actor,record in before.items():
    folder=root/actor/'input';m=json.loads((folder/'INPUTS.json').read_text());entries=m['context']+[e for v in m['variants'].values() for d in v.values() for e in d]
    mh=hashlib.sha256((folder/'INPUTS.json').read_bytes()).hexdigest();rows=[]
    for e in entries:
        h=hashlib.sha256((folder/e['path']).read_bytes()).hexdigest();rows.append({'path':e['path'],'expected':e['sha256'],'actual':h,'matches':h==e['sha256']})
    after[actor]={'manifest_sha256':mh,'manifest_unchanged':mh==record['manifest_sha256'],'files':rows}
    ok=ok and after[actor]['manifest_unchanged'] and all(r['matches'] for r in rows) and all(r['actual']==b['actual'] for r,b in zip(rows,record['files']))
(out/'hashes-after.json').write_text(json.dumps(after,indent=2)+'\n')
ratings={
 'reviewer':'rear_walk_cold','frozen':True,'rating_scale':10,
 'coverage':{'candidate_cels':96,'cyclic_pairs':96,'pngs_verified_before_after':189,'scales':[128,256,84],'backgrounds':['light','dark','diagnostic_ground']},
 'actors':{
  'rowan':{'A':{'appearance':8.0,'identity':9.0,'motion_readability':4.5,'game_usefulness':5.5},'B':{'appearance':7.0,'identity':9.0,'motion_readability':6.5,'game_usefulness':6.5},'preference':'B','confidence':'moderate'},
  'lyra':{'A':{'appearance':8.5,'identity':9.0,'motion_readability':5.0,'game_usefulness':6.0},'B':{'appearance':8.0,'identity':9.0,'motion_readability':7.0,'game_usefulness':7.0},'preference':'B','confidence':'moderate'},
  'brann':{'A':{'appearance':8.0,'identity':7.5,'motion_readability':5.5,'game_usefulness':6.0},'B':{'appearance':7.0,'identity':9.0,'motion_readability':6.0,'game_usefulness':6.5},'preference':'B narrowly','confidence':'low to moderate'}
 },'input_integrity_pass':ok,'human_normal_speed_smoothness_established':False,'world_contact_certified':False
}
(out/'ratings.json').write_text(json.dumps(ratings,indent=2)+'\n')
assert ok
print('Integrity confirmed:189/189 PNG before/after;3/3 manifests unchanged. Frozen report and ratings saved.')
