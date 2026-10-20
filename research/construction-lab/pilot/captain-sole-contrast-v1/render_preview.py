"""Matched native256 palette preview from the frozen combined fine-edit scene."""
import hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'captain-fine-edit-assembly-v1/preview/captain-combined-head-sole04.blend'
sys.path.insert(0,str(HERE.parent/'captain-head-fine-paint-v1'))
from render_candidates import mesh_fingerprint,evaluated_pose_fingerprint
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)=='0a9b4f0926eec5b3ad0a56a2cf0304695392bfb4dcdf282c6733b086e972831d'
TEXTURE=HERE/'candidate/combined-head-sole-contrast.png'
recipe=json.loads((HERE/'candidate/receipt.json').read_text());assert sha(TEXTURE)==recipe['texture_sha256']
OUT=HERE/'preview';OUT.mkdir(exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene
def normals_flags():
    h=hashlib.sha256()
    for o in sorted(s.objects,key=lambda o:o.name):
        if o.type=='MESH':
            h.update(o.name.encode());h.update(np.array([x.vector[:] for x in o.data.corner_normals],dtype='<f4').tobytes())
            h.update(bytes(x.use_edge_sharp for x in o.data.edges));h.update(bytes(x.use_smooth for x in o.data.polygons))
    return h.hexdigest()
before=(mesh_fingerprint(),evaluated_pose_fingerprint(),normals_flags())
s.render.threads_mode='FIXED';s.render.threads=6;s.cycles.device='CPU'
records=[]
def render(kind):
    for size,frames in [(256,(33,103)),(384,(33,))]:
        s.render.resolution_x=s.render.resolution_y=size;s.render.resolution_percentage=100
        for f in frames:
            s.frame_set(f);p=OUT/f'{kind}-{size}-source{f:03}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
            records.append({'kind':kind,'native':size,'source':f,'file':p.name,'sha256':sha(p)})
render('control')
im=bpy.data.images.load(str(TEXTURE),check_existing=False);im.name='CaptainSoleCompactContrast_v1';im.colorspace_settings.name='sRGB';im.pack();bindings=[]
for m in bpy.data.materials:
    if not m.use_nodes:continue
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE'and n.image and n.image.name=='CaptainCombinedHeadSolePaint_v1':
            bindings.append((m.name,n.name,n.interpolation));n.image=im
assert len(bindings)==3
assert before==(mesh_fingerprint(),evaluated_pose_fingerprint(),normals_flags())
render('contrast');s.frame_set(33);packed=OUT/'captain-head-sole-contrast.blend';bpy.ops.wm.save_as_mainfile(filepath=str(packed))
bpy.ops.wm.open_mainfile(filepath=str(packed));bpy.context.scene.render.filepath=str(OUT/'contrast-384-source033-reopened.png');bpy.ops.render.render(write_still=True)
assert sha(SOURCE)=='0a9b4f0926eec5b3ad0a56a2cf0304695392bfb4dcdf282c6733b086e972831d'
(OUT/'receipt.json').write_text(json.dumps({'state':'BOUNDED_PALETTE_PREVIEW_NOT_ART_APPROVAL','source_sha256':sha(SOURCE),'texture_sha256':sha(TEXTURE),'script_sha256':sha(Path(__file__)),'packed_sha256':sha(packed),'protected_mesh_UV_weights_shapes_521poses_normals_flags_exact':before,'bindings':bindings,'sole_emission_strength':.4,'sole_mask_unchanged':True,'renders':records,'limits':['No new geometry/motion','No full65 animation','Palette change can alter indirect lighting','Reopen pixels checked separately']},indent=2)+'\n')
print('CONTRAST_PREVIEW_READY',flush=True)
