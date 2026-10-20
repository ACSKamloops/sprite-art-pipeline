from pathlib import Path
import sys,json,hashlib,copy
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'toolkit'))
from sprite_lab import History,project_hash,render_frame,render_cel,validate_project
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def png(a,p):Image.fromarray(a.astype('uint8'),'RGBA').save(p)
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def poly(points):
    im=Image.new('L',(128,128));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def shifted_mask(m,dx,dy):
    out=np.zeros_like(m);ys,xs=np.where(m)
    for y,x in zip(ys,xs):
        if 0<=x+dx<128 and 0<=y+dy<128:out[y+dy,x+dx]=True
    return out
for d in ['frames','masks','maps','layers']:(ROOT/d).mkdir(exist_ok=True)
yy,xx=np.mgrid[:128,:128]
donor=arr(ROOT/'inputs'/'whole-arm-donor.png');donor[donor[:,:,3]==0]=0
legacy={s:np.array(Image.open(ROOT/'inputs'/f'legacy-{s}-owner.png'))>0 for s in ['near','far']}
source_masks={'near':legacy['near']&(yy>=64),'far':legacy['far']&(yy>=62)}
for side,m in source_masks.items():Image.fromarray((m*255).astype('uint8')).save(ROOT/'masks'/f'{side}-complete-source-owner.png')
closed=json.loads((ROOT/'inputs'/'closed-slit-source-witnesses.json').read_text())
old_dx=[1,1,0,-1,-1,-1,0,1];bob=[0,1,1,0,0,1,1,0]
# One bounded swing experiment: +-3px horizontal and +-2px vertical. The phase
# evolves smoothly, with no head/chest yaw and no change to the original legs.
travel_x=[0,2,3,2,0,-2,-3,-2];travel_y=[0,1,2,1,0,-1,-2,-1]
config={'near':{'anchor_y':64,'plateau_y':67},'far':{'anchor_y':61,'plateau_y':64}}
# Inspected literal proximal-join corrections, distinct from the ordinary
# open elbow contour. These eight destinations close internal one-pixel
# channels only; the exterior elbow space below them remains untouched.
join_underpaint={
    3:[(79,74,78,74,'dark inner sleeve outline'),(79,75,77,75,'dark inner sleeve outline')],
    7:[(80,y,78,y,'shaded proximal sleeve')for y in range(68,72)]+[(46,78,51,78,'dark tunic edge'),(46,79,51,79,'dark tunic edge')]
}

def map_arm(side,dx,dy,body_bob):
    anchor=config[side]['anchor_y'];plateau=config[side]['plateau_y'];h=plateau-anchor
    ty=yy-body_bob;slope=1+dy/h
    assert slope>0
    sy=np.where(ty<anchor,ty,np.where(ty<plateau+dy,(ty+dy*anchor/h)/slope,ty-dy))
    t=np.clip((sy-anchor)/h,0,1);sx=xx-dx*t
    sx=np.floor(sx+.5).astype('int16');sy=np.floor(sy+.5).astype('int16')
    good=(sx>=0)&(sx<128)&(sy>=0)&(sy<128);own=np.zeros((128,128),bool);own[good]=source_masks[side][sy[good],sx[good]]
    a=np.zeros((128,128,4),dtype='uint8');a[own]=donor[sy[own],sx[own]]
    xy=np.stack([sx,sy],axis=-1);xy[~own]=-1
    return a,own,xy

controls=[];initial_layers=[];target_layers=[];records=[];underpaint_log=[]
for i in range(8):
    control=arr(ROOT/'inputs'/'control'/f'{i:02}.png');controls.append(control)
    # Head, chest above the arm roots, and both actual pauldrons keep the exact
    # control pixels and geometry. Forearms render behind these fixed owners.
    fixed=(yy<=61+bob[i])|shifted_mask(poly([(38,48),(52,48),(57,53),(57,59),(54,63),(49,66),(41,65),(36,61),(35,55)]),0,bob[i])|shifted_mask(poly([(77,50),(85,49),(90,53),(90,59),(87,63),(81,64),(77,61)]),0,bob[i])
    fixed&=control[:,:,3]>0
    foreground=np.zeros_like(control);foreground[fixed]=control[fixed]
    body=control.copy();body[fixed]=0;initialbody=body.copy()
    oldvisible=np.zeros((128,128),bool);oldfull=np.zeros_like(oldvisible)
    for side,mult in [('near',1),('far',-1)]:
        odx=old_dx[i]*mult
        for sy,sx in np.argwhere(source_masks[side]):
            tx,ty=int(sx)+odx,int(sy)+bob[i]
            if not(0<=tx<128 and 0<=ty<128):continue
            oldfull[ty,tx]=True
            if donor[sy,sx,3]>0 and not fixed[ty,tx] and np.array_equal(control[ty,tx],donor[sy,sx]):oldvisible[ty,tx]=True
    # Removal is confined to the old visible source arm in its own layer role.
    # Valid body behind transparent arm contour is never deleted.
    body[oldvisible]=0
    underpaint=[];body_source_xy=np.stack([xx,yy],axis=-1).astype('int16');body_owner=np.zeros((128,128),dtype='int16');body_owner[oldvisible]=-1;body_source_xy[oldvisible]=-1
    dx,dy=travel_x[i],travel_y[i]
    nearedge=np.where(yy-bob[i]<74,48,np.where(yy-bob[i]<80,47,46))
    faredge=np.where(yy-bob[i]<72,79,80)
    torso_hidden=((xx>=nearedge)&(xx<=55)&(yy>=64+bob[i])&(yy<=84+bob[i]))|((xx<=faredge)&(xx>=75)&(yy>=62+bob[i])&(yy<=80+bob[i]))
    # The inner upper-arm connection stays anchored to the torso edge while
    # its outer side follows the cuff. Moving the entire inner edge outward
    # would open another thin channel despite the retained closed-slit pixels.
    near_socket=poly([(35,64+bob[i]),(50,64+bob[i]),(max(49,49+dx),68+dy+bob[i]),(32+dx,68+dy+bob[i])])
    far_socket=poly([(78,62+bob[i]),(90,62+bob[i]),(92-dx,66-dy+bob[i]),(min(79,80-dx),66-dy+bob[i])])
    fill=(torso_hidden|near_socket|far_socket)&(body[:,:,3]==0)&~fixed
    # Explicit literal existing same-cel material underpaint. Search only
    # bounded dark torso/sleeve edge donor columns; never brighten with gold.
    for y,x in np.argwhere(fill):
        side='near'if x<64 else'far';columns=[51,52,53,50,54,55]if side=='near'else[78,77,76,79]
        chosen=None
        for sy in [int(y),int(y)-1,int(y)+1]:
            if not 0<=sy<128:continue
            for sx in columns:
                c=control[sy,sx]
                if c[3]>=200 and max(map(int,c[:3]))<=105:chosen=(sx,sy);break
            if chosen:break
        if not chosen:continue
        sx,sy=chosen;body[y,x]=control[sy,sx];body_owner[y,x]=1;body_source_xy[y,x]=[sx,sy]
        underpaint.append({'destination':[int(x),int(y)],'source':[sx,sy],'rgba':control[sy,sx].tolist(),'material':'existing dark torso/sleeve-edge underpaint'})
    # Keep every one of the closed-slit control witnesses in the body layer;
    # a later arm may occlude them, but transparency cannot reopen the channel.
    for witness in closed[i]['literal_source_witnesses']:
        x,y=witness['destination']
        if not fixed[y,x]:body[y,x]=control[y,x];body_owner[y,x]=0;body_source_xy[y,x]=[x,y]
    literal_joins=[]
    for x,y,sx,sy,material in join_underpaint.get(i,[]):
        assert not fixed[y,x]
        c=control[sy,sx];assert c[3]>=200 and max(map(int,c[:3]))<=105
        body[y,x]=c;body_owner[y,x]=1;body_source_xy[y,x]=[sx,sy]
        literal_joins.append({'destination':[x,y],'source':[sx,sy],'rgba':c.tolist(),'material':material,'reason':'inspected internal proximal channel; exterior elbow negative space retained'})
    near,nowner,nxy=map_arm('near',dx,dy,bob[i]);far,fowner,fxy=map_arm('far',-dx,-dy,bob[i])
    plateau_checks=[]
    for side,a,own,mp,sdx,sdy in [('near',near,nowner,nxy,dx,dy),('far',far,fowner,fxy,-dx,-dy)]:
        # Fixed shoulder owners occlude only the proximal overlap, with the
        # complete mapped cuff/glove retained before that explicit occlusion.
        occluded=own&fixed&(a[:,:,3]>0)
        source_plateau=source_masks[side]&(yy>=config[side]['plateau_y'])&(donor[:,:,3]>0)
        visible_count=0;occ_count=0
        for sy,sx in np.argwhere(source_plateau):
            tx,ty=int(sx)+sdx,int(sy)+sdy+bob[i]
            assert 0<=tx<128 and 0<=ty<128
            assert np.array_equal(a[ty,tx],donor[sy,sx])
            if fixed[ty,tx]:occ_count+=1
            else:visible_count+=1
        plateau_checks.append({'side':side,'complete_rigid_plateau_source_pixels':int(source_plateau.sum()),'visible_pixels':visible_count,'explicit_pauldron_occlusion_pixels':occ_count,'exact_integer_translation':True})
        a[fixed]=0
        Image.fromarray((own*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}-{side}-transparent-owner.png')
        Image.fromarray((occluded*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}-{side}-pauldron-occlusion.png')
        np.savez_compressed(ROOT/'maps'/f'{i:02}-{side}.npz',source_xy=mp,owner=own)
    Image.fromarray((oldvisible*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}-old-visible-arm.png')
    Image.fromarray((oldfull*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}-old-transparent-arm-owner.png')
    Image.fromarray((fixed*255).astype('uint8')).save(ROOT/'masks'/f'{i:02}-fixed-head-pauldron.png')
    np.savez_compressed(ROOT/'maps'/f'{i:02}-body.npz',source_xy=body_source_xy,source_role=body_owner)
    lower=arr(ROOT/'inputs'/f'lower-owner-{i:02}.png')[:,:,3]>0
    lower&=(control[:,:,3]>0)&~oldvisible&~fixed
    assert np.array_equal(body[lower],control[lower])
    initial_layers.append({'body':initialbody,'far':np.zeros_like(body),'near':np.zeros_like(body),'fixed':foreground})
    target_layers.append({'body':body,'far':far,'near':near,'fixed':foreground})
    for layer,value in target_layers[-1].items():png(value,ROOT/'layers'/f'{i:02}-{layer}.png')
    underpaint_log.append({'phase':i,'literal_body_underpaint_before_arms':underpaint,'literal_inspected_join_underpaint_before_arms':literal_joins,'closed_control_witnesses_retained':len(closed[i]['literal_source_witnesses'])})
    records.append({'phase':i,'body_bob_from_control':bob[i],'near_translation':[dx,dy],'far_translation':[-dx,-dy],'proximal_map':config,'old_arm_removed_pixels':int(oldvisible.sum()),'same_material_underpaint_pixels':len(underpaint),'rigid_plateaus':plateau_checks,'lower_body_layer_exact':True,'control_sha256':sha(ROOT/'inputs'/'control'/f'{i:02}.png')})

# Complete modern RGBA palette comes only from frozen source images. The
# initial project renders the closed-slit control exactly before any edit.
palette=[[0,0,0,0]];lookup={(0,0,0,0):0}
for a in controls+[donor]:
    for c in a.reshape(-1,4):
        t=tuple(map(int,c))
        if t not in lookup:lookup[t]=len(palette);palette.append(list(t))
def indexed(a):return [lookup[tuple(map(int,c))]for c in a.reshape(-1,4)]
def make_project(layers):
    cels={};frames=[]
    for i,items in enumerate(layers):
        for layer,a in items.items():cels[f'{layer}{i}']={'layer_id':layer,'pixels':indexed(a)}
        frames.append({'id':f'f{i}','duration_ticks':9,'cels':{k:f'{k}{i}'for k in items},'landmarks':{}})
    return {'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,'layers':[{'id':'body','name':'Control body plus explicit source-material underpaint','locked':False},{'id':'far','name':'Complete far forearm/cuff/glove with rigid distal plateau','locked':False},{'id':'near','name':'Complete near forearm/cuff/glove with rigid distal plateau','locked':False},{'id':'fixed','name':'Exact control head/chest-top/pauldrons foreground ownership','locked':True}],'cels':cels,'frames':frames,'animations':[{'id':'walk','frames':[f'f{i}'for i in range(8)],'fps':160,'loop':True,'events':[]}],'provenance':{'model_calls':0,'scope':'One SE modest counter-swing experiment from closed-slit control; no rear port','status':'unselected experiment','hand_travel':'horizontal+-3px, vertical+-2px, smooth opposite phase','legs_timing_contacts':'original source poses preserved'}}
initial=make_project(initial_layers);target=make_project(target_layers);validate_project(initial);validate_project(target)
for i in range(8):
    assert render_frame(initial,f'f{i}').tobytes()==Image.fromarray(controls[i]).tobytes()
    rendered=render_frame(target,f'f{i}');png(np.array(rendered),ROOT/'frames'/f'{i:02}.png')
    final=np.array(rendered);control=controls[i]
    fixed=np.array(Image.open(ROOT/'masks'/f'{i:02}-fixed-head-pauldron.png'))>0
    assert np.array_equal(final[fixed],control[fixed])
    lower=arr(ROOT/'inputs'/f'lower-owner-{i:02}.png')[:,:,3]>0
    lower&=control[:,:,3]>0
    changed=lower&np.any(final!=control,axis=2)
    records[i]['original_lower_pixels_occluded_by_arms']=[[int(x),int(y)]for y,x in np.argwhere(changed)]
    # Every actual boot/contact pixel is exact; any changed hip-edge overlap
    # is recorded rather than silently called source preservation.
    assert not changed[92:].any()
    records[i]['boot_contact_RGBA_exact']=True
    records[i]['output_sha256']=sha(ROOT/'frames'/f'{i:02}.png')
save(ROOT/'initial-project.json',initial);h=History(initial)
for i in range(8):
    ops=[]
    for layer in ['body','far','near']:
        before=initial_layers[i][layer];after=target_layers[i][layer];points=[]
        for y,x in np.argwhere(np.any(before!=after,axis=2)):points.append([int(x),int(y),lookup[tuple(map(int,after[y,x]))]])
        if points:ops.append({'op':'paint','cel_id':f'{layer}{i}','points':points,'mask':[[x,y]for x,y,_ in points]})
    h.apply({'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(h.project),'reason':'First remove only old source-arm paint and establish literal same-material body underpaint; then composite mapped complete forearms with rigid cuff/glove plateaus behind exact fixed pauldrons','operations':ops})
assert project_hash(h.project)==project_hash(target)
save(ROOT/'project.json',h.project);save(ROOT/'journal.json',h.journal());save(ROOT/'MOTION.json',records);save(ROOT/'UNDERPAINT.json',underpaint_log)
replayed=History.replay(initial,h.journal()).project
for i in range(8):assert render_frame(replayed,f'f{i}').tobytes()==Image.open(ROOT/'frames'/f'{i:02}.png').convert('RGBA').tobytes()
finalhash=project_hash(h.project)
for _ in range(len(h.records)):h.undo()
assert project_hash(h.project)==project_hash(initial)
for _ in range(len(h.records)):h.redo()
assert project_hash(h.project)==finalhash
save(ROOT/'REPLAY-RECEIPT.json',{'frames':8,'journal_undo_redo_exact':True,'rendered_RGBA_exact':True,'project_sha256':finalhash,'boot_contact_RGBA_exact':True,'model_calls':0,'status':'unselected SE-only experiment; no art score or acceptance'})
print('Eight SE frames with explicit body underpaint, complete arm maps and exact toolkit undo/redo/replay.')
