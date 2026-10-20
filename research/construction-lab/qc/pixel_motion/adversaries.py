#!/usr/bin/env python3
"""Run reproducible real-art adversaries without changing source project/files."""
import copy,json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
from check import check,diagnostic,material_check,sha,layer_image,data
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent

def fork(p):
    return {**p,'canvas':copy.deepcopy(p['canvas']),'layers':copy.deepcopy(p['layers']),'palette':copy.deepcopy(p['palette']),'cels':dict(p['cels']),'frames':copy.deepcopy(p['frames'])}
def replace_image(p,fid,lid,image):
    frame=next(f for f in p['frames']if f['id']==fid);oldid=frame['cels'][lid];mapping={tuple(c):i for i,c in enumerate(p['palette'])};indices=[]
    for c in data(image):
        if c[3]==0:c=(0,0,0,0)
        if c not in mapping:mapping[c]=len(p['palette']);p['palette'].append(list(c))
        indices.append(mapping[c])
    p['cels'][oldid]={'layer_id':lid,'pixels':indices}
def zoom(before,after,path):
    a=Image.new('RGB',(before.width*2,before.height),(35,35,35));a.paste(before,(0,0),before);a.paste(after,(before.width,0),after);draw=ImageDraw.Draw(a);draw.line((0,140,a.width,140),fill=(80,200,80));draw.text((3,3),'Before',fill='white');draw.text((before.width+3,3),'After',fill='white');a.resize((a.width*3,a.height*3),Image.Resampling.NEAREST).save(path)
def main():
    project_path=ROOT/'study/layered-cutout/project.json';p=json.loads(project_path.read_text());ann=json.loads((HERE/'study-annotations.json').read_text());out=HERE/'evidence';out.mkdir(exist_ok=True);results=[]
    base,images=check(p,ann,ROOT);base['inputs']={'project_file_sha256':sha(project_path),'annotation_sha256':sha(HERE/'study-annotations.json'),'checker_sha256':sha(HERE/'check.py'),'adversary_driver_sha256':sha(__file__)};diagnostic(images,base,out/'current')
    cases=[]
    q=fork(p);fid='walk_06';lid='rear_foot';before=ROOT/'study/layered-cutout/rendered-before-rear-foot'/f'{fid}-{lid}.png';replace_image(q,fid,lid,Image.open(before).convert('RGBA'));cases.append(('retained_rear_sole_elevated_1px',q,ann,'STANCE_GROUND_CONTACT',{'retained_original_png':str(before.relative_to(ROOT)),'sha256':sha(before),'expected_measured_sole_row':138},fid))
    a=copy.deepcopy(ann);a['actions'][0]['root_speed_px_s']=64;cases.append(('world_speed_mismatch_64px_s',p,a,'STANCE_BOUNDARY_WORLD_SLIDING',{'root_speed_changed_from':48,'to':64},'walk_03'))
    q=fork(p);q['canvas']['ground_pivot'][1]+=1;cases.append(('moved_ground_anchor',q,ann,'ANCHOR_OR_CANVAS_CHANGED',{'ground_pivot_y_delta':1},'walk_00'))
    q=fork(p);frame=q['frames'][0]
    for lid in ann['layer_order']:
        image=layer_image(q,frame,lid);shift=Image.new('RGBA',image.size);shift.paste(image,(70,0));replace_image(q,'walk_00',lid,shift)
    cases.append(('clipped_sprite',q,ann,'ALPHA_CANVAS_EDGE',{'translated_all_parts_x':70,'crop_is_intentional_negative':True},'walk_00'))
    q=fork(p);q['frames'][0]['cels']=dict(q['frames'][3]['cels']);cases.append(('wrong_pose',q,ann,'REFERENCE_POSE_COMPOSITE',{'walk_00_bindings_replaced_with':'walk_03'},'walk_00'))
    q=fork(p);q['layers'].reverse();cases.append(('wrong_layer_order',q,ann,'LAYER_ORDER_CHANGED',{'layer_order':'reversed'},'walk_03'))
    q=fork(p);q['palette'][1]=[255,0,255,255];cases.append(('unexpected_palette_edit',q,ann,'PALETTE_REFERENCE_CHANGED',{'palette_index':1,'rgba':[255,0,255,255]},'walk_00'))
    for name,q,a,required,mutation,fid in cases:
        report,rendered=check(q,a,ROOT);codes=sorted(set(i['code']for i in report['issues']));assert required in codes,(name,codes)
        folder=out/name;folder.mkdir(exist_ok=True);diagnostic(rendered,report,folder);zoom(images[fid],rendered[fid],folder/'before-after-3x.png');images[fid].save(folder/'before.png');rendered[fid].save(folder/'after.png')
        entry={'case':name,'required_failure':required,'observed_issue_codes':codes,'source_project_file_sha256':sha(project_path),'mutation':mutation,'report':str((folder/'report.json').relative_to(ROOT)),'before_sha256':sha(folder/'before.png'),'after_sha256':sha(folder/'after.png')};(folder/'mutation.json').write_text(json.dumps(entry,indent=2)+'\n');results.append(entry)
    material=material_check(ROOT/'study/ai-local-edit/source.png',ROOT/'study/ai-local-edit/localized-preview.png',json.loads((HERE/'material-annotations.json').read_text()));assert len(material['violations'])==3;(out/'actual-ai-material-leak.json').write_text(json.dumps(material,indent=2)+'\n');zoom(Image.open(ROOT/'study/ai-local-edit/source.png').convert('RGBA'),Image.open(ROOT/'study/ai-local-edit/localized-preview.png').convert('RGBA'),out/'actual-ai-material-before-after-3x.png')
    a=Image.open(ROOT/'study/ai-local-edit/source.png').convert('RGBA');b=Image.open(ROOT/'study/ai-local-edit/localized-preview.png').convert('RGBA');crop=(54,94,82,122);detail=Image.new('RGB',(56,28),(35,35,35));detail.paste(a.crop(crop),(0,0),a.crop(crop));detail.paste(b.crop(crop),(28,0),b.crop(crop));detail.resize((448,224),Image.Resampling.NEAREST).save(out/'actual-ai-material-knee-8x.png')
    summary={'schema':'sprite-pixel-motion-adversary-summary/v1','source_project_file_sha256':sha(project_path),'qc_source_sha256':{path.name:sha(path)for path in [HERE/'check.py',HERE/'adversaries.py',HERE/'build_annotations.py',HERE/'study-annotations.json',HERE/'material-annotations.json']},'baseline_issue_codes':sorted(set(i['code']for i in base['issues'])),'cases':results,'actual_ai_material_violations':3,'art_quality_approved':False,'scope':'Real-art negative fixtures plus retained historical defective foot and observed rejected AI patch; no mutation of original evidence.'};(out/'adversary-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({'baseline_codes':summary['baseline_issue_codes'],'adversaries':len(results),'actual_material_failures':3}))
if __name__=='__main__':main()
