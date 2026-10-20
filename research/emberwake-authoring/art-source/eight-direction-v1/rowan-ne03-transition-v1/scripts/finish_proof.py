from pathlib import Path
import argparse, json
import numpy as np
from PIL import Image,ImageDraw

P=Path(__file__).resolve().parents[1]

def main(out):
    assert out.is_absolute()and not out.exists();out.mkdir(parents=True)
    a=np.array(Image.open(P/'inputs/current/03.png').convert('RGBA'))
    raw=np.array(Image.open(P/'candidate-proof/03.png').convert('RGBA'))
    final=np.array(Image.open(P/'final/03.png').convert('RGBA'))
    s=json.loads((P/'spec/RECIPE.json').read_text())
    crop=(58,100,79,114);sc=24;w,h=21*sc,14*sc
    proof=Image.new('RGB',(w*2,h+30),(224,221,211));d=ImageDraw.Draw(proof)
    for i,(title,ar)in enumerate([('rotated sole before4pixel cleanup',raw),('final sole; angle/source fixed',final)]):
        im=Image.fromarray(ar).crop(crop).resize((w,h),Image.Resampling.NEAREST);bg=Image.new('RGBA',(w,h),(224,221,211,255));bg=Image.alpha_composite(bg,im);proof.paste(bg.convert('RGB'),(i*w,30));d.text((i*w+3,7),title,fill='black')
        for op in s['sole_cleanup']['operations']:
            x,y=op['target'];X=i*w+(x-crop[0])*sc;Y=30+(y-crop[1])*sc;d.rectangle([X,Y,X+23,Y+23],outline=(30,120,255))
    proof.save(out/'sole-four-pixel-before-after24x.png')
    owner=np.zeros_like(a)
    for part,c in [('cloth',[245,210,80,255]),('boot',[220,90,40,255])]:
        for y,x0,x1 in s[part]['literal_inclusive_rows']:owner[y,x0:x1+1]=c
    up=np.array(Image.open(P/'final/masks/protected-upper.png'))>0;owner[up]=[40,110,240,255]
    other=(a[:,:,3]>0)&(owner[:,:,3]==0);owner[other]=[130,130,130,255]
    proof=Image.new('RGB',(256*3,282),(224,221,211));d=ImageDraw.Draw(proof)
    for i,(title,ar)in enumerate([('current03',a),('literal source owners',owner),('ONE final03',final)]):
        im=Image.fromarray(ar).resize((256,256),Image.Resampling.NEAREST);bg=Image.new('RGBA',(256,256),(224,221,211,255));bg=Image.alpha_composite(bg,im);proof.paste(bg.convert('RGB'),(i*256,26));d.text((i*256+4,5),title,fill='black')
    proof.save(out/'owner-control-final-2x.png')
    cxy=np.load(P/'final/maps/cloth.npz')['source_xy'];bxy=np.load(P/'final/maps/boot.npz')['source_xy']
    coverage=[]
    for y,x in zip(*np.where((a[:,:,3]==0)&(final[:,:,3]>0))):
        part='boot'if bxy[y,x,0]>=0 else'cloth';sx,sy=map(int,(bxy if part=='boot'else cxy)[y,x]);assert sx>=0
        coverage.append({'target':[int(x),int(y)],'part':part,'source_phase':3,'source':[sx,sy],'source_RGBA':a[sy,sx].tolist(),'composed_RGBA':final[y,x].tolist()})
    anchors=[]
    for role,(x,y)in [('upper cuff material',(69,94)),('shaft highlight',(69,97)),('ankle crease material',(69,101)),('heel lower shade',(68,110)),('forefoot edge shade',(78,106))]:
        hits=[[int(xx),int(yy)]for yy,xx in zip(*np.where((bxy[:,:,0]==x)&(bxy[:,:,1]==y)))]
        assert hits
        anchors.append({'role':role,'source03':[x,y],'source_RGBA':a[y,x].tolist(),'actual_target_coords':hits,'scope':'Literal same-source material feature only; not a ground-contact assertion.'})
    (out/'COVERAGE-AND-ANCHORS.json').write_text(json.dumps({'newly_covered_vs_original03':coverage,'source_reused_material_pixels':len(coverage),'new_authored_RGB_pixels':0,'literal_joint_underlap':s['joint_underlap'],'actual_boot_feature_tracks':anchors,'sole_cleanup':s['sole_cleanup']},indent=2)+'\n')
    print('Supplementary proofs and source witnesses',len(coverage),'new mapped pixels')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();main(a.output)
