from pathlib import Path
import copy,hashlib,json,sys,math
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'toolkit'))
from sprite_lab import History,project_hash,render_frame,render_cel,validate_project
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p))>0
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def png(p,a):Image.fromarray(a.astype('uint8')).save(p)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for n in ['frames','layers','maps','masks']:(ROOT/n).mkdir(exist_ok=True)
yy,xx=np.mgrid[:128,:128]
donor=arr(ROOT/'inputs/whole-arm-donor.png');donor[donor[:,:,3]==0]=0
source_owner=mask(ROOT/'inputs/near-source-owner.png')&(yy>=67)
motion=json.loads((ROOT/'inputs/v4/MOTION.json').read_text())
palette=json.loads((ROOT/'inputs/v4/project.json').read_text())['palette']
lookup={tuple(c):i for i,c in enumerate(palette)}
def indexed(a):return [lookup[tuple(map(int,c))]for c in a.reshape(-1,4)]
initial=json.loads((ROOT/'inputs/v4/project.json').read_text())
initial['layers'].insert(1,{'id':'sleeve','name':'Literal rounded near sleeve attachment behind complete cuff/glove','locked':False})
for i in range(8):
    initial['cels'][f'sleeve{i}']={'layer_id':'sleeve','pixels':[0]*16384}
    initial['frames'][i]['cels']['sleeve']=f'sleeve{i}'
initial['provenance']={'scope':'Near-arm attachment trial only, from frozen v4','model_calls':0,'status':'unselected bounded experiment'}
validate_project(initial)
for i in range(8):assert render_frame(initial,f'f{i}').tobytes()==Image.open(ROOT/'inputs/v4/frames'/f'{i:02}.png').convert('RGBA').tobytes()
target=copy.deepcopy(initial);records=[];witnesses=[]
PIVOT=np.array([39.,82.]);ANGLES={5:3.,6:5.,7:3.}
for i in range(8):
    old={layer:arr(ROOT/'inputs/v4/layers'/f'{i:02}-{layer}.png')for layer in ['body','far','near','fixed']}
    parts={**{k:v.copy()for k,v in old.items()},'sleeve':np.zeros((128,128,4),dtype='uint8')}
    fixed=mask(ROOT/'inputs/v4/masks'/f'{i:02}-fixed-head-pauldron.png')
    ownership=np.zeros((128,128),bool);coords=np.full((128,128,2),-1,dtype='int16');sleeve_xy=coords.copy();removed=np.zeros((128,128),bool);literal=[]
    if i in ANGLES:
        dx,dy=motion[i]['near_translation'];bob=motion[i]['body_bob_from_control'];angle=ANGLES[i];rad=math.radians(angle);cs,sn=math.cos(rad),math.sin(rad)
        # One complete rigid cuff/glove part, rotated about its palm center.
        # Translation of that anchor is exactly v4's original hand path.
        tx=xx-PIVOT[0]-dx;ty=yy-PIVOT[1]-dy-bob
        sx=np.floor(cs*tx+sn*ty+PIVOT[0]+.5).astype('int16');sy=np.floor(-sn*tx+cs*ty+PIVOT[1]+.5).astype('int16')
        valid=(sx>=0)&(sx<128)&(sy>=0)&(sy<128);ownership[valid]=source_owner[sy[valid],sx[valid]]
        near=np.zeros_like(donor);near[ownership]=donor[sy[ownership],sx[ownership]];coords[ownership]=np.stack([sx,sy],axis=-1)[ownership]
        occluded=ownership&fixed&(near[:,:,3]>0);near[fixed]=0;parts['near']=near
        # Only the earlier authored exterior socket paint is re-owned.
        # Original body material, torso-edge completion, far arm and all
        # actual source lower paint stay in their existing layers.
        bodymap=np.load(ROOT/'inputs/v4/maps'/f'{i:02}-body.npz')
        removed=(bodymap['source_role']==1)&(xx<48)&(yy<=71+bob)&(yy>=61+bob)&~fixed
        parts['body'][removed]=0
        # Rounded dark sleeve centerline from the underside of the fixed
        # pauldron to the rotated cuff root. This is authored missing paint,
        # sampled only from actual same-view dark sleeve material.
        anchor=np.array([43.,63.+bob])
        cuff_source=np.array([41.,67.]);v=cuff_source-PIVOT
        endpoint=PIVOT+np.array([cs*v[0]-sn*v[1],sn*v[0]+cs*v[1]])+np.array([dx,dy+bob])
        axis=endpoint-anchor;length=float(np.linalg.norm(axis));unit=axis/length;perp=np.array([-unit[1],unit[0]])
        rx=xx-anchor[0];ry=yy-anchor[1];t=np.clip((rx*axis[0]+ry*axis[1])/(length*length),0,1)
        cx=anchor[0]+t*axis[0];cy=anchor[1]+t*axis[1];dist=np.sqrt((xx-cx)**2+(yy-cy)**2)
        radius=4.2-.4*t
        sleeve=(dist<=radius)&~fixed&(parts['body'][:,:,3]==0)&(yy>=61+bob)&(yy<=72+bob)&(xx<51)
        # Final inspected single-pixel interior join at the inside edge.
        # Retain the exterior elbow opening; do not change the rigid part.
        if i in [5,7]:
            jx,jy=47,67 if i==5 else 66
            assert not fixed[jy,jx] and parts['body'][jy,jx,3]==0
            sleeve[jy,jx]=True
        cross=(xx-cx)*perp[0]+(yy-cy)*perp[1]
        for y,x in np.argwhere(sleeve):
            if dist[y,x]>radius[y,x]-1.:sx0,sy0=44,66
            else:sx0=int(np.clip(np.floor(40+cross[y,x]+.5),36,44));sy0=int(np.clip(np.floor(64+2*t[y,x]+.5),64,66))
            color=donor[sy0,sx0];assert color[3]>=200 and max(map(int,color[:3]))<=105
            parts['sleeve'][y,x]=color;sleeve_xy[y,x]=[sx0,sy0]
            literal.append({'destination':[int(x),int(y)],'source':[sx0,sy0],'rgba':color.tolist(),'material':'same-view dark sleeve, rounded authored bridge'})
        Image.fromarray((occluded*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}-rigid-part-fixed-pauldron-occlusion.png')
        record={'phase':i,'rotation_degrees_image_clockwise':angle,'source_palm_anchor':PIVOT.tolist(),'target_palm_anchor':(PIVOT+[dx,dy+bob]).tolist(),'anchor_translation_from_v4':[dx,dy],'unchanged_body_bob':bob,'rigid_part_source_cutoff_y':67,'rigid_transform':'whole cuff/glove inverse nearest; one angle/anchor/translation, no distal warp','sleeve_anchor':anchor.tolist(),'sleeve_cuff_endpoint':endpoint.tolist(),'sleeve_radius_top_bottom':[4.2,3.8],'previous_three_row_span_after_dy':3+dy,'literal_sleeve_pixels':len(literal),'removed_old_authored_socket_pixels':int(removed.sum()),'fixed_pauldron_occlusion_pixels':int(occluded.sum()),'source_glove_alpha_area':int((source_owner&(yy>=76)&(donor[:,:,3]>=200)).sum()),'rendered_glove_alpha_area':int((ownership&(sy>=76)&(near[:,:,3]>=200)).sum())}
    else:record={'phase':i,'unchanged_v4_RGBA':True}
    Image.fromarray((ownership*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}-complete-rigid-owner.png')
    Image.fromarray((removed*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}-old-authored-socket-removal.png')
    np.savez_compressed(ROOT/'maps'/f'{i:02}-rigid-near.npz',source_xy=coords,owner=ownership)
    np.savez_compressed(ROOT/'maps'/f'{i:02}-sleeve.npz',source_xy=sleeve_xy,owner=parts['sleeve'][:,:,3]>0)
    for layer,a in parts.items():
        png(ROOT/'layers'/f'{i:02}-{layer}.png',a)
        if layer in ['body','near','sleeve']:target['cels'][f'{layer}{i}']['pixels']=indexed(a)
    witnesses.append({'phase':i,'literal_sleeve_underpaint_before_complete_rigid_near_part':literal})
    records.append(record)
validate_project(target)
history=History(initial)
for i in range(8):
    operations=[]
    for layer in ['body','sleeve','near']:
        before=np.array(render_cel(initial,f'{layer}{i}'));after=arr(ROOT/'layers'/f'{i:02}-{layer}.png');points=[]
        for y,x in np.argwhere(np.any(before!=after,axis=2)):points.append([int(x),int(y),lookup[tuple(map(int,after[y,x]))]])
        if points:operations.append({'op':'paint','cel_id':f'{layer}{i}','points':points,'mask':[[x,y]for x,y,_ in points]})
    if operations:history.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(history.project),'reason':'Re-own only prior authored near socket; establish literal rounded dark sleeve before compositing the complete rigid cuff/glove about the unchanged v4 palm path; fixed pauldron stays in front','operations':operations})
assert project_hash(history.project)==project_hash(target)
for i in range(8):
    image=render_frame(target,f'f{i}');image.save(ROOT/'frames'/f'{i:02}.png');a=np.array(image);old=arr(ROOT/'inputs/v4/frames'/f'{i:02}.png');fixed=mask(ROOT/'inputs/v4/masks'/f'{i:02}-fixed-head-pauldron.png')
    assert np.array_equal(a[fixed],old[fixed]);assert np.array_equal(a[92:],old[92:])
    if i not in ANGLES:assert np.array_equal(a,old)
    lower=arr(ROOT/'inputs/lower-owners'/f'{i:02}.png')[:,:,3]>0;changed=lower&np.any(a!=old,axis=2)
    records[i]['lower_source_owner_overlap_changes']=[[int(x),int(y)]for y,x in np.argwhere(changed)]
    records[i]['final_png_sha256']=sha(ROOT/'frames'/f'{i:02}.png')
    changed=np.any(a!=old,axis=2);Image.fromarray((changed*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}-actual-final-change.png')
    records[i]['actual_RGBA_changed_pixels']=int(changed.sum())
save(ROOT/'initial-project.json',initial);save(ROOT/'project.json',target);save(ROOT/'journal.json',history.journal());save(ROOT/'ATTACHMENT.json',records);save(ROOT/'LITERAL-SLEEVE.json',witnesses)
final=project_hash(history.project);replayed=History.replay(initial,history.journal())
assert project_hash(replayed.project)==final
for i in range(8):assert render_frame(replayed.project,f'f{i}').tobytes()==Image.open(ROOT/'frames'/f'{i:02}.png').convert('RGBA').tobytes()
for _ in range(len(history.records)):history.undo()
assert project_hash(history.project)==project_hash(initial)
for _ in range(len(history.records)):history.redo()
assert project_hash(history.project)==final
save(ROOT/'REPLAY-RECEIPT.json',{'project_sha256':final,'actual_editor_transactions':len(history.records),'eight_rendered_frames_exact':True,'undo_redo_and_replay_exact':True,'unchanged_phases':[0,1,2,3,4],'far_body_source_and_fixed_ownership_preserved':True,'rows_92_to_127_exact_v4':True,'model_calls':0,'status':'unselected near attachment trial; no art score or acceptance'})
print('One near-arm attachment trial:05–07 only; all8 rendered, exact toolkit replay/undo/redo.')
