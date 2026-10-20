"""One authored support-pose feasibility proof; no animation bank or game edit.

Literal current04 visible owners, rigid boot translation, and a bounded cloth
field with explicit hip/boot boundary pins. Failed fields remain diagnostics.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[1]
BOOT_DELTA = np.array([8., 8.])
# Literal inclusive row guides traced against current approved04 paint.
# They include dark cloth contours, not only the earlier conservative gray core.
Q_ROWS = {84: [(54,54)], 85: [(50,64)], 86: [(49,64)], 87: [(49,63)],
          88: [(49,64)], 89: [(49,63)], 90: [(49,63)], 91: [(49,63)],
          92: [(49,63)], 93: [(48,63)], 94: [(49,64)], 95: [(49,63)],
          96: [(49,63)], 97: [(49,63)], 98: [(48,63)], 99: [(48,62)],
          100: [(47,62)], 101: [(46,62)], 102: [(46,61)], 103: [(47,61)],
          104: [(47,60)], 105: [(48,61)], 106: [(48,61)], 107: [(49,62)],
          108: [(49,63)], 109: [(49,63)], 110: [(50,63)], 111: [(50,63)],
          112: [(50,63)], 113: [(51,62)], 114: [(53,62)]}
CLOTH_ROWS = {84: [(54,54)], 85: [(50,64)], 86: [(49,64)], 87: [(49,63)],
              88: [(49,49),(51,64)], 89: [(51,63)], 90: [(51,63)], 91: [(51,63)],
              92: [(52,63)], 93: [(52,63)], 94: [(53,64)], 95: [(54,63)],
              96: [(55,62)], 97: [(55,62)], 98: [(57,60)]}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def arr(p):
    return np.array(Image.open(p).convert('RGBA'))

def rows_mask(rows):
    m = np.zeros((128,128), bool)
    for y, spans in rows.items():
        for lo, hi in spans:
            m[y, lo:hi+1] = True
    return m

def over(back, front):
    return np.array(Image.alpha_composite(Image.fromarray(back), Image.fromarray(front)))

def neighbors(x,y):
    return [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]

def proof(out, source, candidate, cloth, boot, body, target_cloth, target_boot):
    for size in [128,84,256]:
        for ground, name, ink in [('#e7e3d6','light','black'),('#22252b','dark','white')]:
            board = Image.new('RGB',(size*2,size+28),ground)
            draw = ImageDraw.Draw(board)
            for j,(label,a) in enumerate([('current04',source),('+8,+8 plant hypothesis',candidate)]):
                im = Image.fromarray(a).resize((size,size),Image.Resampling.NEAREST)
                board.paste(im,(j*size,28),im)
                draw.text((j*size+3,4),label,fill=ink)
            board.save(out/f'whole-character-{size}-{name}.png')
    box = (40,78,84,126)
    board = Image.new('RGB',(44*8*2,48*8+26),'#e7e3d6')
    draw = ImageDraw.Draw(board)
    for j,(a,label,cm,bm) in enumerate([(source,'literal source owners',cloth,boot),(candidate,'posed source owners',target_cloth,target_boot)]):
        view = Image.fromarray(a).convert('RGBA')
        tint = np.array(view)
        tint[cm,:3] = (20,170,210)
        tint[bm,:3] = (210,60,180)
        tint[body,:3] = (230,185,50)
        view = Image.fromarray(tint).crop(box).resize((44*8,48*8),Image.Resampling.NEAREST)
        board.paste(view,(j*44*8,26),view)
        draw.text((j*44*8+3,4),label,fill='black')
    board.save(out/'owners-source-target-8x.png')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert not args.output.exists(),'Fresh output required'
    args.output.mkdir(parents=True)
    for e in json.loads((R/'INPUTS.json').read_text()):
        assert sha(R/e['retained'])==e['sha256']
    source=arr(R/'inputs/04-approved.png')
    body=arr(R/'inputs/04-body.png')[...,3]>0
    q=rows_mask(Q_ROWS)&(source[...,3]>0)&~body
    cloth=rows_mask(CLOTH_ROWS)&q
    boot=q&~cloth
    assert not np.any((cloth|boot)&body)
    assert np.array_equal(q,cloth|boot)
    # Body-adjacent/top cloth is pinned. Every real cloth/boot interface is a
    # rigid boot pin. No per-color segmentation or hidden coverage is added.
    hip=np.zeros((128,128),bool)
    cuff=np.zeros((128,128),bool)
    for y,x in np.argwhere(cloth):
        hip[y,x]=y<=85 or any(body[yy,xx] for xx,yy in neighbors(x,y))
        cuff[y,x]=any(boot[yy,xx] for xx,yy in neighbors(x,y))
    conflict=hip&cuff
    weight=np.zeros((128,128),float)
    weight[cuff]=1
    for iteration in range(5000):
        previous=weight.copy()
        for y,x in np.argwhere(cloth&~hip&~cuff):
            vals=[previous[yy,xx] for xx,yy in neighbors(x,y) if cloth[yy,xx]]
            if vals:weight[y,x]=sum(vals)/len(vals)
        weight[hip]=0
        weight[cuff]=1
        if np.max(abs(weight-previous))<1e-12:break
    # Shared texel-corner weights preserve the literal boot/cloth boundary.
    corner_cache={}
    corner_conflicts=[]
    def corner(x2,y2):
        key=(x2,y2)
        if key in corner_cache:return corner_cache[key]
        x,y=x2/2,y2/2
        incident=[(int(math.floor(x)),int(math.floor(y))),
                  (int(math.floor(x))+1,int(math.floor(y))),
                  (int(math.floor(x)),int(math.floor(y))+1),
                  (int(math.floor(x))+1,int(math.floor(y))+1)]
        has_boot=any(boot[yy,xx] for xx,yy in incident)
        has_hip=any(body[yy,xx] or hip[yy,xx] for xx,yy in incident)
        values=[weight[yy,xx] for xx,yy in incident if cloth[yy,xx]]
        if has_boot and has_hip:corner_conflicts.append([x,y])
        w=1. if has_boot else (0. if has_hip else float(np.mean(values)))
        result=(np.array([x,y]),np.array([x,y])+BOOT_DELTA*w,w)
        corner_cache[key]=result
        return result
    placed=np.zeros_like(source)
    xy=np.full((128,128,2),-1,np.int16)
    target_owner=np.zeros((128,128),bool)
    determinants=[]
    overlap=[]
    for y,x in np.argwhere(cloth):
        cs=[corner(2*x-1,2*y-1),corner(2*x+1,2*y-1),corner(2*x+1,2*y+1),corner(2*x-1,2*y+1)]
        for tri in [(0,1,2),(0,2,3)]:
            source_tri=np.array([cs[k][0] for k in tri])
            target_tri=np.array([cs[k][1] for k in tri])
            det=float(np.linalg.det(np.column_stack((target_tri[1]-target_tri[0],target_tri[2]-target_tri[0]))))
            determinants.append(det)
            if abs(det)<1e-12:continue
            inv=np.linalg.inv(np.vstack((target_tri.T,np.ones(3))))
            for yy in range(max(0,int(math.ceil(target_tri[:,1].min()))),min(127,int(math.floor(target_tri[:,1].max())))+1):
                for xx in range(max(0,int(math.ceil(target_tri[:,0].min()))),min(127,int(math.floor(target_tri[:,0].max())))+1):
                    bary=inv@np.array([xx,yy,1.])
                    if bary.min() < -1e-9:continue
                    if target_owner[yy,xx] and xy[yy,xx].tolist()!=[x,y]:
                        overlap.append({'target':[xx,yy],'first_source':xy[yy,xx].tolist(),'second_source':[int(x),int(y)]})
                    placed[yy,xx]=source[y,x]
                    xy[yy,xx]=[x,y]
                    target_owner[yy,xx]=True
    boot_layer=np.zeros_like(source)
    boot_xy=np.full((128,128,2),-1,np.int16)
    boot_target=np.zeros((128,128),bool)
    for y,x in np.argwhere(boot):
        tx,ty=int(x+8),int(y+8)
        assert 0<=tx<128 and 0<=ty<128,'Complete boot clipped'
        boot_layer[ty,tx]=source[y,x]
        boot_xy[ty,tx]=[x,y]
        boot_target[ty,tx]=True
    assert np.array_equal(boot_layer[boot_target],source[boot])
    base=source.copy()
    base[q]=0
    candidate=over(over(base,placed),boot_layer)
    candidate[body]=source[body]
    # This proof exposes any disocclusion; it never fills a hole to pass.
    Image.fromarray(candidate).save(args.output/'04-plant-plus8.png')
    for name,mask in [('literal-Q',q),('literal-cloth',cloth),('literal-boot',boot),('hip-pins',hip),('cuff-pins',cuff),('target-cloth',target_owner),('target-boot',boot_target)]:
        Image.fromarray(mask.astype('uint8')*255).save(args.output/f'{name}.png')
    np.savez_compressed(args.output/'source-field.npz',weight=weight,source_cloth_xy=xy,source_boot_xy=boot_xy)
    journal={'Q_rows':Q_ROWS,'cloth_rows':CLOTH_ROWS,'boot_owner':'Literal Q minus literal cloth, no color classifier.',
             'ambiguous_dark_edge_assignment':'Rows86-87x49 and88x49 stay with cloth contour; first warm leather begins88x50. This is an authored visible-part interpretation, not recovered anatomy.',
             'boot_translation':[8,8],'cloth_field':'Discrete harmonic weights on literal cloth; hip=0, actual boot-adjacent cuff=1; shared texel corners are pinned at true part boundaries.',
             'new_underpaint':0,'source_part_authority':'Current approved04 visible surface; no hidden boot or limb master claim.'}
    (args.output/'LITERAL-RIG.json').write_text(json.dumps(journal,indent=2)+'\n')
    yb,xb=np.where(boot_target)
    data={'status':'One pose feasibility proof; pending root anatomy/owner inspection, never a contact pass',
          'source_04_SHA256':sha(R/'inputs/04-approved.png'),'candidate_SHA256':sha(args.output/'04-plant-plus8.png'),
          'Q_owner_pixels':int(q.sum()),'cloth_source_pixels':int(cloth.sum()),'boot_visible_source_pixels':int(boot.sum()),
          'complete_boot_layer_RGBA_exact_at_translation':True,'target_boot_bbox_inclusive':[int(xb.min()),int(yb.min()),int(xb.max()),int(yb.max())],
          'right_and_bottom_boot_margin_pixels':[127-int(xb.max()),127-int(yb.max())],
          'upper_owner_RGBA_exact':bool(np.array_equal(candidate[body],source[body])),
          'cloth_triangle_min_determinant':min(determinants),'nonpositive_triangles':sum(d<=0 for d in determinants),
          'hip_cuff_pin_conflicts':np.argwhere(conflict)[:,::-1].tolist(),'corner_pin_conflicts':corner_conflicts,
          'target_different_donor_overlaps':overlap,'boot_over_body_pixels':int((boot_target&body).sum()),
          'cloth_over_body_pixels_before_foreground_restore':int((target_owner&body).sum()),
          'no_target_boot_clipping':True,'new_paint_or_hidden_fill':0,'waveform_or_support_schedule_committed':False,
          'support_math':{'required_native_SE_component_per_quarter_cycle':158*.1125/.66/math.sqrt(2),
                          'required_native_SE_component_per_half_cycle':158*.225/.66/math.sqrt(2),
                          'plus8_minus8_with_existing04_06_sole_path_component':20,
                          'quarter_cycle_root_world':158*.1125,'quarter_cycle_plus8_minus8_backward_world':20*.66*math.sqrt(2),
                          '24_exposures_hold':.45/24,'24_exposures_within_hold_drift_world':158*.45/24,
                          '32_exposures_hold':.45/32,'32_exposures_within_hold_drift_world':158*.45/32}}
    data['construction_self_rejected']=bool(data['nonpositive_triangles'] or len(overlap) or len(corner_conflicts) or conflict.any())
    (args.output/'RECEIPT.json').write_text(json.dumps(data,indent=2)+'\n')
    proof(args.output,source,candidate,cloth,boot,body,target_owner,boot_target)
    print(json.dumps({k:data[k] for k in ['construction_self_rejected','cloth_triangle_min_determinant','nonpositive_triangles','boot_visible_source_pixels','target_boot_bbox_inclusive','right_and_bottom_boot_margin_pixels','upper_owner_RGBA_exact','new_paint_or_hidden_fill']}))

if __name__=='__main__':main()
