"""Read-only source inspection and ONE schematic P/07 paint guide; no sprite edit."""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
SRC = Path('/home/astra/projects/emberwake-demo/art-source/eight-direction-v1/lyra-stance-spring-v1')
for folder in ['inputs/current', 'inputs/source', 'components', 'masks', 'guides', 'sheets']:
    (OUT / folder).mkdir(parents=True, exist_ok=True)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rgba(path):
    return np.array(Image.open(path).convert('RGBA'))

def save_mask(mask, path):
    Image.fromarray((mask * 255).astype('uint8')).save(OUT / path)

def spans_mask(rows, visible=None):
    mask = np.zeros((128,128), bool)
    for y, spans in rows.items():
        for x0,x1 in spans:
            mask[int(y),x0:x1+1] = True
    return mask if visible is None else mask & visible

def polygon(points):
    im = Image.new('L',(128,128))
    ImageDraw.Draw(im).polygon(points, fill=255)
    return np.array(im)>0

def shift_mask(mask, dx, dy):
    result = np.zeros_like(mask)
    yy,xx = np.where(mask)
    result[yy+dy,xx+dx] = True
    return result

project = json.loads((SRC / 'component-editor/projects/final.json').read_text())
palette = np.array(project['palette'], np.uint8)
current = {}
components = {}
for i in [0,5,6,7]:
    shutil.copy2(SRC / f'editor-render/{i:02}.png', OUT / f'inputs/current/{i:02}.png')
    current[i] = rgba(SRC / f'editor-render/{i:02}.png')
    frame = next(f for f in project['frames'] if f['id'] == f'{i:02}')
    components[i] = {}
    for layer, cel in frame['cels'].items():
        art = palette[np.array(project['cels'][cel]['pixels'])].reshape(128,128,4)
        components[i][layer] = art
        Image.fromarray(art).save(OUT / f'components/{i:02}-{layer}.png')
        save_mask(art[...,3]>0, f'masks/{i:02}-component-{layer}.png')

# Literal visible near/Q boot contours, inspected against the source pixels.
# The retained distal witness alone misses the upper curved brown shaft.
q06rows = {
    86:[[47,47]],87:[[46,47]],88:[[46,47]],89:[[46,47]],90:[[46,48]],
    91:[[45,48]],92:[[45,49]],93:[[45,50],[59,59]],94:[[44,59]],
    95:[[44,58]],96:[[43,58]],97:[[42,58]],98:[[42,57]],99:[[43,57]],
    100:[[43,56]],101:[[44,57]],102:[[44,57]],103:[[45,58]],
    104:[[45,59]],105:[[45,59]],106:[[46,59]],107:[[46,59]],
    108:[[46,59]],109:[[47,58]],110:[[49,58]]
}
q07rows = {
    84:[[47,53]],85:[[47,53]],86:[[47,53]],87:[[47,53]],88:[[47,54]],
    89:[[46,54]],90:[[45,55]],91:[[44,56]],92:[[44,56]],93:[[44,58]],
    94:[[44,59]],95:[[44,60]],96:[[44,61]],97:[[45,61]],98:[[45,59]],
    99:[[45,59]],100:[[46,58]],101:[[46,58]],102:[[47,58]],
    103:[[48,57]],104:[[49,56]],105:[[50,55]]
}
q = {6:spans_mask(q06rows,current[6][...,3]>0),7:spans_mask(q07rows,current[7][...,3]>0)}
map05 = np.load(SRC / 'retained-source/inputs/repair05/maps/05-left-front.npz')
q[5] = np.zeros((128,128),bool)
for y,x in np.argwhere(map05['owner']):
    sx,sy = map(int,map05['source_xy'][y,x])
    if q[6][sy,sx]:
        assert np.array_equal(current[5][y,x],current[6][sy,sx])
        q[5][y,x] = True

z00 = np.load(SRC / 'retained-source/inputs/boot-witness/lyra-southeast-00-screen-right.npz')
z06 = np.load(SRC / 'retained-source/inputs/boot-witness/lyra-southeast-06-screen-right.npz')
p = {}
for i,z in [(0,z00),(6,z06)]:
    mask = np.zeros((128,128),bool)
    for x,y in z['destination_xy']:
        mask[y,x] = True
    p[i] = mask
p07_projected = shift_mask(p[0],1,-3)
p[7] = np.zeros((128,128),bool)
mismatches=[]
for (x,y), color in zip(z00['destination_xy'],z00['RGBA']):
    xx,yy = int(x)+1,int(y)-3
    if np.array_equal(current[7][yy,xx],color):
        p[7][yy,xx] = True
    else:
        owners=[name for name,art in components[7].items() if art[yy,xx,3]>0]
        mismatches.append({'source00_at':[int(x),int(y)],'destination07_at':[xx,yy],
                           'source_RGBA':color.tolist(),'actual07_RGBA':current[7][yy,xx].tolist(),
                           'actual_component_owners':owners})
assert int(p[7].sum())==342 and len(mismatches)==6
p[5] = np.zeros((128,128),bool)
map05p = np.load(SRC / 'retained-source/inputs/repair05/maps/05-right-rear.npz')
for y,x in np.argwhere(map05p['owner']):
    sx,sy = map(int,map05p['source_xy'][y,x])
    if p[6][sy,sx]:
        p[5][y,x] = True
for i in [5,6,7]:
    save_mask(q[i],f'masks/{i:02}-Q-visible-boot-literal.png')
for i in [0,5,6,7]:
    save_mask(p[i],f'masks/{i:02}-P-retained-paint-witness.png')
save_mask(p07_projected & ~p[7],'masks/07-P-source00-witness-occluded-or-different.png')

# Point labels denote inspected paint features, never foot contact or bones.
observed = {
    '06':{'cuff':[76,87],'heel':[71,100],'forefoot':[79,97]},
    '07':{'cuff':[69,87],'heel':[67,104],'forefoot':[85,101]},
    '00':{'cuff':[68,90],'heel':[66,107],'forefoot':[84,104]},
}
qanchors = {'05':{'cuff':[56,96],'heel':[48,109],'forefoot':[60,109]},
            '06':{'cuff':[54,94],'heel':[46,107],'forefoot':[58,107]},
            '07':{'visible_boot_entry':[50,84],'heel':[47,101],'forefoot':[57,101]}}
target={name:((np.array(observed['06'][name],float)+observed['00'][name])/2).tolist()
        for name in ['cuff','heel','forefoot']}
target['hip_authored_hidden']=[66,82]
target['knee_authored_hidden']=[71,84]

# ONE NEW-DRAWING SCHEMATIC, not a sprite, texture warp, or selected amplitude.
# The envelope only indicates possible paint scope; source07 upper/Q wins.
boot_envelope = polygon([(71,87),(75,88),(76,93),(75,97),(78,98),(82,99),
                         (83,101),(82,103),(78,105),(70,106),(67,105),
                         (65,102),(66,98),(67,94),(68,90)])
calf_envelope = polygon([(68,83),(73,83),(75,85),(74,88),(71,89),(68,87)])
protected = components[7]['body'][...,3]>0
protected |= q[7]
envelope_raw = boot_envelope | calf_envelope
target_scope = envelope_raw & ~protected
blocked = envelope_raw & protected
new_coverage = target_scope & (current[7][...,3]==0)
source_replacement = target_scope & (current[7][...,3]>0)
save_mask(protected,'masks/07-upper-Q-protected.png')
save_mask(boot_envelope & ~protected,'masks/07-guide-P-boot-envelope.png')
save_mask(calf_envelope & ~protected,'masks/07-guide-P-charcoal-envelope.png')
save_mask(target_scope,'masks/07-guide-P-schematic-scope.png')
save_mask(blocked,'masks/07-guide-blocked-by-protected-upper-Q.png')
save_mask(new_coverage,'masks/07-guide-new-silhouette-coverage.png')
save_mask(source_replacement,'masks/07-guide-existing-paint-needing-new-drawing.png')

guide={
 'status':'ONE conditional new-drawing P/07 guide; stop before construction',
 'scope':'Southeast current05/06/07/00 source evidence; no southwest bank, editor write, model call, final paint or quality score',
 'source_root':str(SRC),'canonical_frames':{f'{i:02}':digest(SRC/f'editor-render/{i:02}.png') for i in [0,5,6,7]},
 'identity':{
  'Q05_to_Q06':'Source05 left-front map uses actual06 near/screen-left visible paint. Cuff/heel/forefoot distal translation is exactly (+2,+2) in05 relative to06.',
  'Q07':'Screen-left trailing visible boot is the best painted-path continuation, but its true proximal cuff is hidden and no longitudinal anatomical identity ID is retained.',
  'P06_to_P07_to_P00':'Screen-right bent/raised paint at06 progresses to the advancing screen-right boot at07/00; this projected role remains qualified as anatomical identity.',
  'not_lowest_foot_tracking':True},
 'Q_only_repair':'NO-GO. No Q movement is proposed; 06->07 exchange includes the prominent P knee/calf/boot presentation change.',
 'P00_to_P07_paint_witness':{'translation':[1,-3],'samples':348,'exact_RGBA_samples':342,'mismatches':mismatches,
   'mismatch_breakdown':'Two upper fixed_lower samples have different paint; four left-edge samples are transparent in07. These are boundary/visibility differences, not proof of body occlusion.',
   'limitation':'Retained visible paint witness, not a pure-material mask or complete hidden boot master.'},
 'Q_literal_boot_rows':{'06':q06rows,'07':q07rows},
 'observed_P_surface_anchors':observed,'observed_Q_surface_anchors':qanchors,
 'anchor_semantics':{'cuff':'Inspected material contour sample, not a bone joint; different projections do not prove exact anatomical point homology.',
    'heel':'Visible rear/sole-contour paint sample; not a ground contact assertion.',
    'forefoot':'Visible outer forefoot paint sample; not a projected foot skeleton.',
    'Q07_cuff':'Not visible as a reliable homologous cuff; only a visible boot-entry sample is supplied.'},
 'one_proposal':{'frame':'07','part':'P calf/shaft/foot drawing only','type':'New authored unbending and boot reorientation, not rigid movement or a source-exact warp',
   'controls':target,'derivation':'Cuff/heel/forefoot target points are the arithmetic halfway positions between inspected06 and00 surface samples. They are an exploratory chronology corridor, not a physical interpolation law or approved paint amplitude.',
   'hip_knee_semantics':'Dashed authored guide controls beneath/behind the protected coat. Hip and knee positions are not recovered joints and must not overwrite the actual07 upper.',
   'paint_requirements':'New charcoal calf/knee transition and coherent full shaft/forefoot perspective. Preserve substantial brown boot volume; do not shrink/recolor a detached distal fragment.',
   'original07_upper_and_Q_protected':True,'body_bob_or_timing_change':False,
   'new_coverage_pixels_in_schematic':int(new_coverage.sum()),
   'protected_pixels_crossed_by_raw_schematic_and_excluded':int(blocked.sum()),
   'existing_paint_pixels_in_schematic':int(source_replacement.sum()),
   'hidden_new_coverage':'No hidden anatomy has been supplied. The clipped envelope excludes the protected upper/Q. Its newly covered silhouette pixels require new paint; changed material boundaries within the current P footprint also require new drawing. Additional hidden calf/boot surfaces remain unknown.',
   'source_only_rigid_translation_no_go':'The three observed feature paths require different motions. A wholeboot translation does not produce this guide; a rigid rotation cannot preserve all the changing pairwise feature distances.',
   'acceptance':'Root visual feasibility review only; no final sprite has been constructed or accepted.'},
 'point_distances':{},'scales':[128,256,84],
 'grounds':{'light':'#e7e3d6','dark':'#22252b','game':'#27392f'},
 'timing':{'holds':[[9,160]]*8,'loop':[9,20],'change':False},
 'hip_angles_authored_not_recovered':True,'final_paint_constructed':False,
 'model_calls':0,'editor_or_canonical_writes':0,'new_quality_scores':None}
for pair in [('cuff','heel'),('heel','forefoot'),('cuff','forefoot')]:
    guide['point_distances']['-'.join(pair)]={
      key:float(np.linalg.norm(np.array(points[pair[0]])-np.array(points[pair[1]])))
      for key,points in [*observed.items(),('guide',target)]}
(OUT/'GUIDE.json').write_text(json.dumps(guide,indent=2)+'\n')

colors={'P':(255,113,202,130),'Q':(80,222,255,130),'new':(255,180,60,190)}
def composite(a,bg):
    im=Image.new('RGBA',(128,128),bg);im.alpha_composite(Image.fromarray(a));return im

def tint(im,mask,color):
    layer=np.zeros((128,128,4),np.uint8);layer[mask]=color
    im.alpha_composite(Image.fromarray(layer));return im

def marker(draw,pt,color,kind='cross'):
    x,y=pt
    if kind=='hidden':
        draw.ellipse((x-1.5,y-1.5,x+1.5,y+1.5),outline=color,width=1)
    else:
        draw.line((x-2,y,x+2,y),fill=color,width=1);draw.line((x,y-2,x,y+2),fill=color,width=1)

def dashed(draw,a,b,color):
    a,b=np.array(a,float),np.array(b,float)
    steps=max(1,int(np.linalg.norm(b-a)*3))
    for step in range(steps):
        if step%3!=0:continue
        pt=a+(b-a)*step/steps;end=a+(b-a)*min(step+1,steps)/steps
        draw.line((tuple(pt),tuple(end)),fill=color,width=1)

def annotated(i,bg,owners=False,proposal=False):
    im=composite(current[i],bg)
    if owners:
        if i in q:tint(im,q[i],colors['Q'])
        tint(im,p[i],colors['P'])
    draw=ImageDraw.Draw(im)
    if f'{i:02}' in observed:
        for pt in observed[f'{i:02}'].values():marker(draw,pt,'#ff6fc9')
    if i in [5,6,7]:
        for pt in qanchors[f'{i:02}'].values():marker(draw,pt,'#50deff')
    if proposal:
        tint(im,target_scope,(255,186,80,65))
        tint(im,new_coverage,(255,70,55,205))
        draw=ImageDraw.Draw(im)
        # Actual07 source remains intact under these diagram overlays.
        dashed(draw,target['hip_authored_hidden'],target['knee_authored_hidden'],'#ffd954')
        dashed(draw,target['knee_authored_hidden'],target['cuff'],'#ffd954')
        draw.line([tuple(target[k]) for k in ['cuff','heel','forefoot']],fill='#ffd954',width=1)
        for key,pt in target.items():marker(draw,pt,'#ffff68','hidden' if 'hidden' in key else 'cross')
        for key in ['cuff','heel','forefoot']:
            draw.line((tuple(observed['06'][key]),tuple(observed['00'][key])),fill='#9de8ae',width=1)
    return im.convert('RGB')

sheet_index=[]
for scale in [128,256,84]:
  font=ImageFont.load_default(size=9 if scale==84 else 12 if scale==128 else 14)
  for ground,bg in guide['grounds'].items():
    gap,label,margin=8,24,12;cw,ch=scale+gap,scale+label+gap
    sheet=Image.new('RGB',(margin*2+4*cw,margin*2+3*ch+30),'#444444');draw=ImageDraw.Draw(sheet)
    draw.text((margin,4),'P pink | Q cyan | proposed07 yellow | new coverage red',font=font,fill='white')
    rows=[[(i,f'{i:02} current',False,False) for i in [5,6,7,0]],
          [(i,f'{i:02} owners',True,False) for i in [5,6,7,0]],
          [(6,'06 P/Q points',False,False),(7,'07 P/Q points',False,False),
           (0,'00 P points',False,False),(7,'07 NEW DRAW guide',True,True)]]
    for row,cells in enumerate(rows):
      for col,(i,title,owners,proposal) in enumerate(cells):
        x,y=margin+col*cw,margin+30+row*ch
        draw.text((x,y),title,font=font,fill='white')
        im=annotated(i,bg,owners,proposal) if row else composite(current[i],bg).convert('RGB')
        sheet.paste(im.resize((scale,scale),Image.Resampling.NEAREST),(x,y+label))
    name=f'05-06-07-00-and-one-P07-guide-{scale}-{ground}.png';sheet.save(OUT/'sheets'/name)
    sheet_index.append({'file':'sheets/'+name,'scale':scale,'background':bg,'whole_canvas':True,'nearest':True,
                        'proposal':'Only bottom-right panel: one schematic new-drawing P07 proposal; no edited sprite.'})
    annotated(7,bg,True,True).resize((scale,scale),Image.Resampling.NEAREST).save(OUT/f'guides/P07-one-schematic-{scale}-{ground}.png')
(OUT/'sheet-index.json').write_text(json.dumps(sheet_index,indent=2)+'\n')

# The same ONE guide, enlarged and labelled for Root's diagram inspection.
large = annotated(7,'#e7e3d6',True,True).resize((1024,1024),Image.Resampling.NEAREST)
diagram=Image.new('RGB',(1536,1064),'#e7e3d6');diagram.paste(large,(0,40));draw=ImageDraw.Draw(diagram)
titlefont=ImageFont.load_default(size=20);textfont=ImageFont.load_default(size=17)
draw.text((12,10),'ONE P07 new-drawing corridor / schematic only / original07 art under overlay',font=titlefont,fill='#22252b')
lines=[
 'P pink / Q cyan / proposal yellow',
 'Green: observed06-to00 surface paths',
 'Red: 2 possible new silhouette pixels',
 '',
 'Observed cuff / heel / forefoot:',
 '06: (76,87) / (71,100) / (79,97)',
 '07: (69,87) / (67,104) / (85,101)',
 '00: (68,90) / (66,107) / (84,104)',
 '',
 'One P07 exploratory corridor:',
 'Cuff       (72,88.5)',
 'Heel       (68.5,103.5)',
 'Forefoot   (81.5,100.5)',
 'Hip H      (66,82)  authored / hidden',
 'Knee K     (71,84)  authored / hidden',
 '',
 'Surface midpoints require different',
 'motions: calf + shaft + foot need',
 'coherent new drawing / reorientation.',
 'A rigid wholeboot move is NO-GO.',
 '',
 'Original07 upper and Q protected.',
 '6 raw-envelope pixels blocked.',
 '244 existing pixels in paint envelope.',
 'Hidden anatomy is not recovered.',
 'P/Q anatomical identity is qualified.',
 '',
 'No repaired sprite / new paint / model.',
 'No body bob or timing change.',
 'Root feasibility inspection only.'
]
for row,line in enumerate(lines):draw.text((1035,80+row*28),line,font=textfont,fill='#22252b')
for key,label in [('hip_authored_hidden','H'),('knee_authored_hidden','K'),('cuff','C'),('heel','H*'),('forefoot','F')]:
    x,y=target[key];draw.text((x*8+13,y*8+40-18),label,font=textfont,fill='#765200')
diagram.save(OUT/'guides/P07-control-diagram-8x.png')

copied=[]
for rel in ['component-editor/projects/final.json','retained-source/inputs/05-construction-witness.py',
            'retained-source/inputs/03-04-construction-witness.py',
            'retained-source/inputs/repair05/maps/05-left-front.npz',
            'retained-source/inputs/repair05/maps/05-right-rear.npz',
            'retained-source/literal-owner-prep/LITERAL-ROWS.json',
            'retained-source/waist-completion-v1/maps/06-screen-left-support.npz',
            'retained-source/waist-completion-v1/maps/06-screen-right-raised.npz',
            'retained-source/inputs/boot-witness/lyra-southeast-00-screen-right.npz',
            'retained-source/inputs/boot-witness/lyra-southeast-06-screen-left.npz',
            'retained-source/inputs/boot-witness/lyra-southeast-06-screen-right.npz']:
    dest=OUT/'inputs/source'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SRC/rel,dest)
    copied.append({'canonical':str(SRC/rel),'copy':str(dest.relative_to(OUT)),'sha256':digest(dest)})
(OUT/'COPIED-SOURCE.json').write_text(json.dumps(copied,indent=2)+'\n')
print(json.dumps({'sheets':len(sheet_index),'proposal':'one P07 new-drawing schematic','no_repaired_sprite':True,
                  'P00_to_P07_exact':int(p[7].sum()),'P00_to_P07_occluded_or_different':len(mismatches),
                  'schematic_new_coverage_pixels':int(new_coverage.sum()),'blocked_protected_pixels':int(blocked.sum())},indent=2))
