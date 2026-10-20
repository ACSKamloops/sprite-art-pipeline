"""Render fixed source seam identities at their stretched poses, in own outputs."""
import bpy, hashlib, json
from pathlib import Path
import numpy as np
from mathutils import Vector

ROOT=Path('/home/astra/projects/captain-3d-rig-lab')
OUT=Path('/home/astra/artifacts/captain-armour-strain-witness-v1')
if OUT.exists():raise FileExistsError('Preserve previous witnesses')
OUT.mkdir(parents=True)
source=ROOT/'render/body-semantic-v1/diagnostic-render.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=4
arm=next(o for o in scene.objects if o.type=='ARMATURE');body=next(o for o in scene.objects if o.type=='MESH' and any(m.type=='ARMATURE'for m in o.modifiers))
rest=np.array([body.matrix_world@v.co for v in body.data.vertices]);edges=np.array([e.vertices[:]for e in body.data.edges]);base=np.linalg.norm(rest[edges[:,1]]-rest[edges[:,0]],axis=1)
ownership=[];rigid=[]
for vertex in body.data.vertices:
    gs=[g for g in vertex.groups if g.weight>1e-7];ownership.append(max(gs,key=lambda g:g.weight).group);rigid.append(len(gs)==1)
ownership=np.array(ownership);rigid=np.array(rigid);mid=(rest[edges[:,0]]+rest[edges[:,1]])*.5
mask=(mid[:,2]>=-.85)&(mid[:,2]<=-.25)&(np.abs(mid[:,0])>.105)&(base>.0001)&rigid[edges[:,0]]&rigid[edges[:,1]]&(ownership[edges[:,0]]!=ownership[edges[:,1]])
edge_lookup={tuple(sorted((int(u),int(v)))):i for i,(u,v) in enumerate(edges)}
neutral=bpy.data.materials.new('Diagnostic neutral');neutral.diffuse_color=(.28,.32,.36,1);neutral.use_nodes=True;neutral.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.28,.32,.36,1)
bad=bpy.data.materials.new('Actual greater than4x source edge stretch');bad.use_nodes=True;n=bad.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(1,.03,.015,1);n.inputs['Emission Color'].default_value=(1,.01,0,1);n.inputs['Emission Strength'].default_value=.4
body.data.materials.append(neutral);neutral_id=len(body.data.materials)-1;body.data.materials.append(bad);bad_id=len(body.data.materials)-1
groups=json.loads((ROOT/'rig/body-v1/retarget-joints.json').read_text());root0=Vector(groups[0]['root']);records=[]
for cel in [2,18,27,50]:
    frame=1+2*cel;scene.frame_set(frame);delta=Vector(groups[frame-1]['root'])-root0;arm.location=(-delta.x,-delta.y,0);bpy.context.view_layer.update()
    for poly in body.data.polygons:poly.material_index=0
    scene.render.filepath=str(OUT/f'cel-{cel:02d}-source.png');bpy.ops.render.render(write_still=True)
    ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());points=np.array([ev.matrix_world@v.co for v in ev.data.vertices]);length=np.linalg.norm(points[edges[:,1]]-points[edges[:,0]],axis=1)
    ratios=np.divide(length,base,out=np.ones_like(base),where=base>.0001);bad_edges=set(np.flatnonzero(mask&(ratios>4)).tolist());marked=0
    for poly in body.data.polygons:
        v=list(poly.vertices);ids=[edge_lookup[tuple(sorted((v[i],v[(i+1)%len(v)])))]for i in range(len(v))]
        highlight=any(i in bad_edges for i in ids);poly.material_index=bad_id if highlight else neutral_id;marked+=int(highlight)
    scene.render.filepath=str(OUT/f'cel-{cel:02d}-strain.png');bpy.ops.render.render(write_still=True)
    records.append({'cel':cel,'bad_cross_owner_edges':len(bad_edges),'incident_highlighted_polygons':marked})
(OUT/'receipt.json').write_text(json.dumps({'state':'DEFORMATION_DIAGNOSTIC_NOT_ART','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'definition':'Red polygons incident to fixed source leg cross-rigid-owner edge with posed/rest length>4. Same geometry andcamera. Diagnostic materials replace art only in separate strain render.','frames':records,'limits':['Singlepolygon includes nearbyflexiblejoint material; colour does not prove all redfaces are armour','Reference source textures preserved in separate paired render','No anatomy/contact/art score claim']},indent=2)+'\n')
print(records)
