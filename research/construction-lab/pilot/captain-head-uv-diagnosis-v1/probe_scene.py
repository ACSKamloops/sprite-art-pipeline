import bpy,json,sys,hashlib
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]);s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=6;s.render.resolution_x=384;s.render.resolution_y=384;s.render.resolution_percentage=100;r=[]
for o in s.objects:
 if o.type=='MESH':
  r.append({'object':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'materials':[m.name if m else None for m in o.data.materials],'groups':[g.name for g in o.vertex_groups],'images':[{'material':m.name,'image':n.image.name,'size':list(n.image.size),'filter':n.interpolation} for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]})
(out/'mesh-inventory.json').write_text(json.dumps(r,indent=2)+'\n')
for f in [1,33,103]:
 s.frame_set(f);bpy.context.view_layer.update();s.render.filepath=str(out/f'source-{f:03}.png');bpy.ops.render.render(write_still=True)
