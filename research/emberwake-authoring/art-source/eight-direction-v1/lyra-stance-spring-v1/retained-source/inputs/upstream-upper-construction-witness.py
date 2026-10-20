"""Four bounded coherent-upper trials. No model call, no lower-body warp."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from PIL import Image,ImageDraw
from pilot_rowan_se import polygon
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'trial-v1'
BOB=[0,1,1,0,0,1,1,0]
SWING=[0,-1,-2,-1,0,1,2,1]
ARMS={
 ('rowan','southeast'):[[(37,66),(51,66),(53,70),(51,75),(49,80),(47,83),(44,85),(36,85),(32,82),(31,78),(32,73),(34,70)],[(78,66),(87,66),(91,70),(94,74),(94,79),(90,82),(84,83),(81,80),(80,76),(78,72)]],
 ('rowan','northeast'):[[(41,63),(52,63),(54,68),(53,74),(52,78),(47,81),(42,81),(39,78),(39,70)],[(77,64),(86,64),(91,69),(94,75),(92,79),(88,81),(83,81),(79,77),(77,71)]],
 ('lyra','southeast'):[[(41,69),(52,69),(55,73),(54,79),(53,84),(42,84),(39,81),(39,76)],[(78,65),(86,65),(90,70),(93,75),(91,80),(88,83),(80,83),(77,78),(77,71)]],
 ('lyra','northeast'):[[],[(78,65),(87,65),(90,70),(93,75),(93,81),(89,86),(82,86),(79,83),(78,76)]]}
KNEES_SE={0:[[(49,86),(63,86),(64,94),(54,97),(48,92)],[(63,79),(80,79),(82,97),(64,97)]],
 2:[[(49,81),(64,81),(64,92),(49,93)],[(63,81),(79,81),(83,99),(64,99)]],
 4:[[(49,81),(64,81),(76,101),(63,103),(51,92)],[(65,81),(79,81),(75,97),(62,96)]],
 6:[[(45,79),(64,79),(64,94),(45,94)],[(71,74),(86,74),(90,83),(87,92),(70,91)]]}
KNEES_NE={0:[[(48,80),(78,80),(80,96),(48,98)]],2:[[(48,79),(79,79),(80,95),(48,95)]],
 4:[[(48,80),(79,80),(80,99),(48,100)]],6:[[(47,77),(85,77),(86,96),(47,98)]]}

def masked(a,m):b=a.copy();b[~m]=0;return b
def savej(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def build(actor,view):
    inp=ROOT/'inputs'/actor/view;out=OUT/actor/view
    for d in ['frames','masks','maps','proof']: (out/d).mkdir(parents=True,exist_ok=True)
    a=[np.array(Image.open(inp/f'{i:02}.png').convert('RGBA'))for i in range(8)]
    lm=np.array(Image.open(inp/'upstream-masks/02-lower.png'))>0
    upper=~lm
    if (actor,view)==('rowan','southeast'):
        for y,xs in [(82,[49,50]),(83,[48,49,50]),(84,[47,48,49,50]),(85,[47,48,49,50])]:
            for x in xs:upper[y,x]=False
    arms=[polygon(x)&upper if x else np.zeros((128,128),bool) for x in ARMS[actor,view]]
    torso=upper&~arms[0]&~arms[1]
    # Same visible textured hip paint, used as a short underlay behind complete
    # original lower poses. It fills old arm/waist coverage gaps explicitly.
    if actor=='rowan'and view=='southeast':
        hip=polygon([(50,82),(77,82),(79,85),(76,86),(65,86),(60,88),(50,87)])&lm
        pocket=polygon([(49,81),(60,81),(63,84),(61,88),(58,91),(53,90),(50,87)])
        pocket &= (a[2][...,0]>130)&(a[2][...,1]>90)&(a[2][...,0]>a[2][...,1]+8)&(a[2][...,1]>a[2][...,2]+8)&(a[2][...,3]>200)
    elif actor=='rowan':
        hip=polygon([(50,80),(78,80),(79,84),(74,87),(62,86),(51,85)])&lm
        # Prevent a lifted key2 leather boot becoming a ghost in the hip underlay.
        hip &= (a[2][...,0]>125)&(a[2][...,1]>85)&(a[2][...,2]>55)
        pocket=np.zeros((128,128),bool)
    else:
        y=84 if view=='southeast'else 82
        hip=polygon([(48,y),(78,y),(80,y+3),(76,y+5),(64,y+4),(52,y+5)])&lm
        # Actual charcoal trouser texture only; no coat trim or brown boots.
        rgb=a[2][...,:3].astype(int)
        hip &= (abs(rgb[...,0]-rgb[...,1])<20)&(rgb[...,1]>=rgb[...,2]-8)&(rgb[...,0]<120)
        pocket=np.zeros((128,128),bool)
    for name,m in [('upper-owner',upper),('torso-owner',torso),('left-arm-owner',arms[0]),('right-arm-owner',arms[1]),('hip-underlay',hip),('pocket-underlay',pocket)]:
        Image.fromarray((m*255).astype('uint8')).save(out/'masks'/f'{name}.png')
    receipts=[];frames=[]
    for i in range(8):
        if i%2==0:own=np.array(Image.open(inp/'upstream-masks'/f'{i:02}-lower.png'))>0
        else:
            z=np.load(inp/f'{i:02}-map.npz');own=z['allowed']|z['old_lower']
        own=own.copy()
        old_arm_extension=np.zeros((128,128),bool)
        if actor=='rowan'and view=='northeast':
            # The prior far-arm rectangle stopped before its final glove row.
            # Own the complete glove silhouette and its transparent edge halo.
            old_arm_extension[80:82,29:49]=True
            own &= ~old_arm_extension
        # Explicit removal of the OLD crossing arm in the Lyra side-presented
        # keys. The old rectangular side-glove guards did not own this hand.
        if actor=='lyra'and view=='southeast'and i in(5,6):
            old=polygon([(52,73),(70,73),(72,77),(72,82),(68,84),(54,84)])
            own &= ~old
        if actor=='lyra'and view=='southeast'and i in(0,1,7):
            # Old short coat hem is not leg paint. The common source2 coat is
            # four rows longer; complete boots reassert foreground below.
            own[79:84,48:81]=False
        src=np.full((128,128),-1,np.int16);xy=np.full((128,128,2),-1,np.int16)
        layerid=np.full((128,128),-1,np.int16);canvas=np.zeros((128,128,4),np.uint8)
        def over(part,source,dx=0,dy=0,layer=0):
            ys,xs=np.where(part[...,3]>0)
            for y,x in zip(ys,xs):
                xx,yy=int(x)+dx,int(y)+dy
                if 0<=xx<128 and 0<=yy<128:
                    canvas[yy,xx]=part[y,x];src[yy,xx]=source;xy[yy,xx]=[x,y];layerid[yy,xx]=layer
        over(masked(a[2],torso),2,0,BOB[i],0)
        over(masked(a[2],hip),2,layer=1)
        if i in(0,1,7):over(masked(a[2],pocket),2,layer=2)
        over(masked(a[i],own),i,layer=3)
        over(masked(a[2],arms[0]),2,SWING[i],BOB[i],4)
        over(masked(a[2],arms[1]),2,-SWING[i],BOB[i],5)
        socket=[]
        for k,dx in [(0,SWING[i]),(1,-SWING[i])]:
            if not dx or not arms[k].any():continue
            top=int(np.argwhere(arms[k])[:,0].min())
            for y in range(top-1,top+2):
                for x in range(30,96):
                    xx,yy=x+dx,y+BOB[i]
                    if upper[y,x]and a[2][y,x,3]and 0<=xx<128 and canvas[yy,xx,3]==0:
                        canvas[yy,xx]=a[2][y,x];src[yy,xx]=2;xy[yy,xx]=[x,y];layerid[yy,xx]=6;socket.append([xx,yy,x,y])
        # Complete original knees remain foreground instead of being cut by the
        # new common coat/arms. This is explicit, reviewable layer ordering.
        key=i if i%2==0 else {1:0,3:2,5:6,7:0}[i]
        knee=np.zeros((128,128),bool)
        for poly in (KNEES_SE if view=='southeast'else KNEES_NE)[key]:knee|=polygon(poly)
        knee &= own
        over(masked(a[i],knee),i,layer=7)
        if i%2==0:
            boot=np.zeros((128,128),bool)
            for k in(0,1):boot|=np.array(Image.open(inp/'upstream-masks'/f'{i:02}-boot{k}.png'))>0
        else:
            z=np.load(inp/f'{i:02}-map.npz');boot=z['rigid_boot']>0
        over(masked(a[i],boot),i,layer=8)
        material=[]
        # The cream bracket is cloth, not brown boot leather. Close only the
        # missing curved pocket strips with visible shaded thigh02 pixels.
        if actor=='rowan'and view=='southeast'and i in(1,7):
            rows=([(88,54,62,84,52),(89,55,63,85,52),(90,56,62,86,53),(91,57,61,87,54)]if i==1 else
                  [(88,54,60,84,53),(89,54,61,85,52),(90,54,61,86,52),(91,55,61,87,52),(92,56,60,87,53)])
            for y,x0,x1,sy,sx in rows:
                for x in range(x0,x1+1):
                    xx=sx+x-x0
                    assert a[2][sy,xx,3]>0
                    canvas[y,x]=a[2][sy,xx];src[y,x]=2;xy[y,x]=[xx,sy];layerid[y,x]=9
                    material.append({'target':[x,y],'source':[xx,sy],'source_phase':2,'material':'shaded cream trouser cloth'})
        # Every output colour has a retained source witness. No unexplained new
        # anatomy or fabricated colours enter this trial.
        yy,xx=np.where(canvas[...,3]>0)
        assert all(np.array_equal(canvas[y,x],a[int(src[y,x])][xy[y,x,1],xy[y,x,0]])for y,x in zip(yy,xx))
        # The earlier geometric 'rigid_boot' map includes the tan cloth bracket.
        # Correct that material ownership only at the named local cloth repair;
        # do not claim those original broad geometry masks were pure leather.
        frozen_boot=boot.copy();material_boot_correction=[]
        for r in material:
            x,y=r['target']
            if boot[y,x]:boot[y,x]=False;material_boot_correction.append([x,y])
        exactpaint=boot&(a[i][...,3]>0)
        assert np.array_equal(canvas[exactpaint],a[i][exactpaint]),(actor,view,i,'visible boot changed')
        # Preserve all lower source pixels not occluded by the common upper or
        # explicitly named source-material seam patch; no leg geometry map.
        Image.fromarray(canvas).save(out/'frames'/f'{i:02}.png')
        for n,m in [('lower-owner',own),('foreground-knee',knee),('complete-boot',boot),('upstream-geometric-boot',frozen_boot),('old-arm-ownership-extension',old_arm_extension)]:Image.fromarray((m*255).astype('uint8')).save(out/'masks'/f'{i:02}-{n}.png')
        np.savez_compressed(out/'maps'/f'{i:02}-source.npz',source_id=src,source_xy=xy,layer_id=layerid)
        frames.append(Image.fromarray(canvas))
        receipts.append({'phase':i,'upper_source_phase':2,'lower_source_phase':i,'bob':BOB[i],'left_arm_dx':SWING[i]if arms[0].any()else 0,'right_arm_dx':-SWING[i],
                         'socket_fill':socket,'material_seam_patch':material,'visible_hip_underlay_pixels':int((layerid==1).sum()),'visible_pocket_underlay_pixels':int((layerid==2).sum()),
                         'boot_mask_pixels':int(boot.sum()),'boot_visible_RGBA_exact':True,'boot_transparent_underpaint_pixels':int((boot&(a[i][...,3]==0)&(canvas[...,3]>0)).sum()),'lower_geometric_warp':False,'upstream_geometric_boot_cloth_correction':material_boot_correction})
    for name,size in [('native',128),('game',84),('2x',256)]:
        sheet=Image.new('RGB',(8*size,2*(size+22)),'#e5e2d5');d=ImageDraw.Draw(sheet)
        for row,ims in enumerate([[Image.fromarray(x)for x in a],frames]):
            for i,im in enumerate(ims):
                im=im.resize((size,size),Image.Resampling.NEAREST);sheet.paste(im,(i*size,row*(size+22)+22),im)
                d.text((i*size+3,row*(size+22)+3),f'{"prior"if row==0 else"steady"} {i:02}',fill='black')
        sheet.save(out/'proof'/f'before-after-{name}.png')
    exposures=[]
    for i in range(8):
        im=Image.new('RGB',(424,152),'#e5e2d5');d=ImageDraw.Draw(im)
        for c,(sourceims,size)in enumerate([(a,128),(frames,128),(a,84),(frames,84)]):
            x=sum([128,128,84,84][:c]);z=Image.fromarray(sourceims[i])if c%2==0 else sourceims[i]
            z=z.resize((size,size),Image.Resampling.NEAREST);im.paste(z,(x,22),z);d.text((x+2,4),f'{"prior"if c%2==0 else"steady"} {size} {i:02}',fill='black')
        exposures.append(im)
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','424x152','-framerate','160','-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','14','-pix_fmt','yuv420p',str(out/'before-after.mp4')],stdin=subprocess.PIPE)
    for _ in range(8):
        for im in exposures:
            for __ in range(9):proc.stdin.write(im.tobytes())
    proc.stdin.close();assert proc.wait()==0
    exposures[0].save(out/'before-after.gif',save_all=True,append_images=exposures[1:],duration=[60,50,60,60,50,60,50,60],loop=0,disposal=2)
    savej(out/'receipt.json',{'actor':actor,'view':view,'upper_source_phase':2,'holds':[[9,160]]*8,'cycle':[9,20],
        'frames':receipts,'far_arm_note':'Lyra NE far arm is not visibly separated from cape; no invented far-arm movement'if(actor,view)==('lyra','northeast')else None,
        'score':None,'status':'source-art experiment pending independent review'})
    print(actor,view,'written')
def main():
    for actor,view in [('rowan','southeast'),('rowan','northeast'),('lyra','southeast'),('lyra','northeast')]:build(actor,view)
if __name__=='__main__':main()
