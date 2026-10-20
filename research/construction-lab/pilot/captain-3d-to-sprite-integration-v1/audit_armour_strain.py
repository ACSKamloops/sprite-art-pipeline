"""Read-only deformation audit of fixed source edges and bone ownership.

Run with Blender --background --python this.py -- --input frozen.blend --output NEW.
This diagnoses source-owner seams. It does not score art or discover anatomy.
"""
import argparse, hashlib, json, sys
from pathlib import Path
import bpy, numpy as np

p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
if a.output.exists():raise FileExistsError('Preserve prior audits')
a.output.mkdir(parents=True)
bpy.ops.wm.open_mainfile(filepath=str(a.input));scene=bpy.context.scene
arm=next(o for o in scene.objects if o.type=='ARMATURE');meshes=[o for o in scene.objects if o.type=='MESH' and any(m.type=='ARMATURE'for m in o.modifiers)]
dependency=bpy.context.evaluated_depsgraph_get();report={'state':'UNAPPROVED_OWNERSHIP_STRAIN_DIAGNOSTIC','input_sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'masks':'Fixed rest-world leg region Z[-.85,-.25], absX>.105. Semantic owner is frozen vertex group, not recovered plate anatomy.','meshes':{},'limits':['Mixed-owner edges can legitimately bridge flexible black joints; strain alone does not prove damaged visible armour','Single-owner rigid edge preservation does not prove good source ownership or silhouette','Fixed original rest edges below0.1mm excluded from ratios; no pose-dependent selection','No scene/material/source edits or contact approval']}
for obj in meshes:
    rest=np.array([obj.matrix_world@v.co for v in obj.data.vertices]);edges=np.array([e.vertices[:]for e in obj.data.edges],dtype=np.int32)
    owners=[];rigid=[]
    for v in obj.data.vertices:
        weights=[g for g in v.groups if g.weight>1e-7]
        best=max(weights,key=lambda g:g.weight);owners.append(obj.vertex_groups[best.group].name);rigid.append(len(weights)==1 and best.weight>.99999)
    owners=np.array(owners);rigid=np.array(rigid);base=np.linalg.norm(rest[edges[:,1]]-rest[edges[:,0]],axis=1)
    midpoint=(rest[edges[:,0]]+rest[edges[:,1]])*.5
    leg=(midpoint[:,2]>=-.85)&(midpoint[:,2]<=-.25)&(np.abs(midpoint[:,0])>.105)&(base>.0001)
    same=leg&rigid[edges[:,0]]&rigid[edges[:,1]]&(owners[edges[:,0]]==owners[edges[:,1]])
    crossed=leg&rigid[edges[:,0]]&rigid[edges[:,1]]&(owners[edges[:,0]]!=owners[edges[:,1]])
    seam=leg&~same;frames=[];worst=[]
    for frame in range(1,131,2):
        scene.frame_set(frame);bpy.context.view_layer.update();evaluated=obj.evaluated_get(dependency)
        if len(evaluated.data.vertices)!=len(rest):raise ValueError('Topology changed under modifier')
        xyz=np.array([evaluated.matrix_world@v.co for v in evaluated.data.vertices]);length=np.linalg.norm(xyz[edges[:,1]]-xyz[edges[:,0]],axis=1)
        ratio=np.divide(length,base,out=np.ones_like(base),where=base>.0001)
        row={'source_frame':frame,'output_cel':(frame-1)//2}
        for name,mask in [('same_rigid_owner',same),('cross_rigid_owner',crossed),('all_owner_seams',seam)]:
            values=ratio[mask];row[name]={'count':int(mask.sum()),'p01':float(np.percentile(values,1)),'p50':float(np.percentile(values,50)),'p95':float(np.percentile(values,95)),'maximum':float(values.max()),'minimum':float(values.min())}
        frames.append(row)
        ids=np.flatnonzero(crossed);ranking=ids[np.argsort(ratio[ids])[-3:][::-1]]
        for edgeid in ranking:
            u,v=edges[edgeid];worst.append({'cel':(frame-1)//2,'edge':int(edgeid),'vertices':[int(u),int(v)],'owners':[str(owners[u]),str(owners[v])],'rest_world_midpoint':midpoint[edgeid].tolist(),'rest_length_m':float(base[edgeid]),'posed_length_m':float(length[edgeid]),'ratio':float(ratio[edgeid])})
    report['meshes'][obj.name]={'edge_masks_counts':{'leg':int(leg.sum()),'same_rigid_owner':int(same.sum()),'cross_rigid_owner':int(crossed.sum()),'seam':int(seam.sum())},'frames':frames,'largest_cross_owner_stretches':sorted(worst,key=lambda r:r['ratio'],reverse=True)[:24]}
    if max(abs(r['same_rigid_owner']['maximum']-1)for r in frames)>1e-3: raise AssertionError('Purported same-bone rigid edges deform unexpectedly')
(a.output/'strain-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'output':str(a.output),'meshes':{n:{'mask_counts':v['edge_masks_counts'],'largest_stretch':v['largest_cross_owner_stretches'][0]}for n,v in report['meshes'].items()}}))
