"""Independent literal-map replay and scope audit; writes only small reports."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parents[1]
P=R/'pose-proof-v1'
def a(p):return np.array(Image.open(p).convert('RGBA'))
def m(p):return np.array(Image.open(p).convert('L'))>0
source=a(R/'inputs/04-approved.png')
candidate=a(P/'04-plant-plus8.png')
body=a(R/'inputs/04-body.png')[...,3]>0
q=m(P/'literal-Q.png')
cloth=m(P/'target-cloth.png')
boot=m(P/'target-boot.png')
maps=np.load(P/'source-field.npz')
layers=[]
witnesses=[]
for role,mask,key in [('cloth',cloth,'source_cloth_xy'),('boot',boot,'source_boot_xy')]:
    layer=np.zeros_like(source)
    for y,x in np.argwhere(mask):
        sx,sy=maps[key][y,x]
        layer[y,x]=source[sy,sx]
        witnesses.append({'role':role,'target':[int(x),int(y)],'source04':[int(sx),int(sy)],
                          'source_RGBA':source[sy,sx].tolist(),'candidate_RGBA':candidate[y,x].tolist()})
    layers.append(layer)
base=source.copy()
base[q]=0
replay=np.array(Image.alpha_composite(Image.alpha_composite(Image.fromarray(base),Image.fromarray(layers[0])),Image.fromarray(layers[1])))
replay[body]=source[body]
assert np.array_equal(replay,candidate)
original_cloth=m(P/'literal-cloth.png')
original_boot=m(P/'literal-boot.png')
joins=[]
for y,x in np.argwhere(original_cloth):
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        bx,by=x+dx,y+dy
        if not original_boot[by,bx]:continue
        tx,ty=x+8,y+8
        btx,bty=bx+8,by+8
        joins.append({'source_cloth':[int(x),int(y)],'source_boot':[int(bx),int(by)],
                      'target_expected_cloth':[int(tx),int(ty)],'target_boot':[int(btx),int(bty)],
                      'cloth_at_boundary_present':bool(cloth[ty,tx]),'boot_present':bool(boot[bty,btx])})
occlusions=[]
for y,x in np.argwhere((source[...,3]>0)&~q&~body&(cloth|boot)):
    occlusions.append({'target':[int(x),int(y)],'previous_other_visible_RGBA':source[y,x].tolist(),
                       'foreground_role':'boot' if boot[y,x] else 'cloth',
                       'foreground_source04':maps['source_boot_xy' if boot[y,x] else 'source_cloth_xy'][y,x].tolist(),
                       'candidate_RGBA':candidate[y,x].tolist()})
unexpected_loss=(source[...,3]>0)&(candidate[...,3]==0)&~q
assert not unexpected_loss.any()
unsupported_joins=[v for v in joins if not v['cloth_at_boundary_present'] or not v['boot_present']]
result={'independent_saved_map_replay_RGBA_exact':True,'source_target_samples':len(witnesses),
        'original_cloth_boot_adjacency_pairs':len(joins),'unsupported_adjacency_pairs':unsupported_joins,
        'upper_owner_RGBA_exact':bool(np.array_equal(candidate[body],source[body])),
        'new_Q_foreground_occlusion_of_existing_other_visible_paint':len(occlusions),
        'old_Q_pixels_now_background':int((q&(candidate[...,3]==0)).sum()),
        'unexpected_old_paint_loss_outside_Q':int(unexpected_loss.sum()),'authored_new_underpaint':0,
        'source_claim':'Literal source-colored projected cloth plus rigid current04 visible boot. No recovered hidden anatomy or contact schedule.'}
(P/'SOURCE-WITNESSES.json').write_text(json.dumps(witnesses,indent=2)+'\n')
(P/'FOREGROUND-OCCLUSION-WITNESSES.json').write_text(json.dumps(occlusions,indent=2)+'\n')
(P/'CUFF-ADJACENCIES.json').write_text(json.dumps(joins,indent=2)+'\n')
(R/'AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
