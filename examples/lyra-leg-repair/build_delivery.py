"""Build fixed-clock comparison and verify actual editable-tool exchange."""
from pathlib import Path
from fractions import Fraction
import hashlib, importlib.util, json, shutil, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

R=Path(__file__).resolve().parent
D=R/'delivery-v4'
D.mkdir(exist_ok=False)
T=Path('/home/astra/.codex/skills/sprite-construction-editing/assets/toolkit')
sys.path.insert(0,str(T))
from sprite_lab import validate_project, render_frame, canonical_json, export_aseprite, import_aseprite
spec=importlib.util.spec_from_file_location('apng','/home/astra/.codex/skills/sprite-animation-pipeline/scripts/exact_apng.py')
apng=importlib.util.module_from_spec(spec);spec.loader.exec_module(apng)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')

banks={}
for name,folder in [('before','inputs'),('after','candidate-v4')]:
    (D/name).mkdir()
    images=[]
    for i in range(8):
        shutil.copy2(R/folder/f'{i:02}.png',D/name/f'{i:02}.png')
        images.append(Image.open(D/name/f'{i:02}.png').convert('RGBA'))
    banks[name]=images
    holds=[Fraction(9,160)]*8
    data=apng.encode(images,holds,0)
    proof=apng.verify(data,images,holds,0)
    (D/f'{name}.apng.png').write_bytes(data)
    write(D/f'{name}-apng-receipt.json',proof)

# Disjoint protected-upper/editable-lower layers preserve RGBA without
# premultiplied edge recomposition. Articulated source masters stay in candidate-v3/parts.
palette=[[0,0,0,0]];indices={(0,0,0,0):0}
def indexed(a):
    result=[]
    for rgba in a.reshape(-1,4):
        c=tuple(int(v) for v in rgba)
        if c not in indices:indices[c]=len(palette);palette.append(list(c))
        result.append(indices[c])
    return result
project={'schema':'sprite-edit-project/v1','canvas':{'width':128,'height':128,'render_pivot':[64,112],'ground_pivot':[64,112]},'palette':palette,
 'layers':[{'id':'lower','name':'Repaired lower body - editable','locked':False},{'id':'upper','name':'Original upper - protected','locked':True}],
 'cels':{},'frames':[],'animations':[{'id':'walk-SE','frames':[f'f{i}' for i in range(8)],'fps':160,'loop':True,'events':[]}],
 'provenance':{'source':'candidate-v4','clock':'8 exposures of9/160 seconds =450ms; external editor milliseconds are quantized','scope':'Lower-body proportion repair candidate; not animation approval, actual joint recovery, or physical foot-contact validation.'}}
records=[]
for i in range(8):
    before=np.array(banks['before'][i]);after=np.array(banks['after'][i]);mask=np.array(Image.open(R/'candidate-v4/layers'/f'{i:02}-edit-mask.png'))>0
    assert np.array_equal(before[~mask],after[~mask])
    assert np.array_equal(before[:78],after[:78])
    hidden=(after[:,:,3]==0)&np.any(after[:,:,:3]!=0,axis=2)
    # The editor's renderer canonicalizes fully transparent RGB. Preserve the
    # unmodified source PNG, and explicitly bind this invisible-only difference.
    editable=after.copy();editable[editable[:,:,3]==0]=0
    for layer in ['lower','upper']:
        a=editable.copy();a[~mask if layer=='lower' else mask]=0
        project['cels'][f'{layer}{i}']={'layer_id':layer,'pixels':indexed(a)}
    project['frames'].append({'id':f'f{i}','duration_ticks':9,'cels':{k:f'{k}{i}' for k in ['lower','upper']},'landmarks':{}})
    records.append({'frame':i,'before_sha256':sha(D/'before'/f'{i:02}.png'),'after_sha256':sha(D/'after'/f'{i:02}.png'),'changed_pixels':int(np.any(before!=after,axis=2).sum()),'above_y78_exact':True,'outside_edit_mask_exact':True,'editor_only_transparent_rgb_zeroed_xy':[[int(x),int(y)]for y,x in np.argwhere(hidden)]})
validate_project(project)
def canonical_image(im):
    a=np.array(im);a[a[:,:,3]==0]=0;return Image.fromarray(a)
for i,expected in enumerate(banks['after']):assert render_frame(project,f'f{i}').tobytes()==canonical_image(expected).tobytes()
(D/'editable-project.json').write_text(canonical_json(project)+'\n')
exchange=export_aseprite(project,D/'lyra-walk-SE.aseprite','walk-SE')
write(D/'ase-export-receipt.json',exchange)
cmd=['/home/astra/.local/bin/libresprite','-b',str(D/'lyra-walk-SE.aseprite'),'--save-as',str(D/'lyra-walk-SE-tool-saved.aseprite'),'--sheet',str(D/'tool-sheet.png'),'--sheet-type','horizontal','--data',str(D/'tool-frames.json'),'--format','json-array']
result=subprocess.run(cmd,capture_output=True,text=True,check=True)
assert (D/'lyra-walk-SE-tool-saved.aseprite').is_file()
reopened=import_aseprite(D/'lyra-walk-SE-tool-saved.aseprite',D/'lyra-walk-SE.aseprite.sprite-lab.json')
sheet=Image.open(D/'tool-sheet.png').convert('RGBA')
assert sheet.size==(1024,128)
for i,expected in enumerate(banks['after']):
    assert render_frame(reopened,f'f{i}').tobytes()==canonical_image(expected).tobytes()
    assert sheet.crop((128*i,0,128*(i+1),128)).tobytes()==canonical_image(expected).tobytes()
assert canonical_json(reopened)==canonical_json(project)

# Exact450ms loop: nine160Hz ticks for each source exposure; no extra wrap frame.
cache={}
args=['ffmpeg','-hide_banner','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size','768x356','-framerate','160','-i','pipe:0','-an','-c:v','libx264','-threads','8','-preset','fast','-crf','12','-pix_fmt','yuv420p','-movflags','+faststart',str(D/'before-after.mp4')]
proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
for tick in range(576):
    i=(tick//9)%8
    if i not in cache:
        im=Image.new('RGB',(768,356),(28,34,45));dr=ImageDraw.Draw(im)
        for col,name in enumerate(['before','after']):
            dr.text((col*384+24,16),('Before' if col==0 else 'Repaired candidate')+f' / frame{i}',fill='white')
            cel=banks[name][i].resize((256,256),Image.Resampling.NEAREST)
            im.paste(cel,(col*384+64,58),cel)
        dr.text((24,330),'Same128px canvas / 2x nearest / 450ms cycle / eight full loops',fill='#c0c9d8')
        cache[i]=im.tobytes()
    proc.stdin.write(cache[i])
proc.stdin.close();error=proc.stderr.read().decode();assert proc.wait()==0,error
probe=json.loads(subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_frames,duration','-of','json',str(D/'before-after.mp4')],capture_output=True,text=True,check=True).stdout)
assert probe['streams'][0]['nb_frames']=='576' and probe['streams'][0]['duration']=='3.600000'
write(D/'VERIFICATION.json',{'frames':records,'editable_json_render_rgba_exact_after_declared_transparent_rgb_zeroing':True,'actual_libresprite_save_reopen_exact':True,'actual_libresprite_sheet_all_eight_rgba_exact_after_declared_transparent_rgb_zeroing':True,'reimport_project_exact':True,'external_editor_holds_ms':[f['duration'] for f in json.loads((D/'tool-frames.json').read_text())['frames']],'authoritative_hold_seconds':[9,160],'total_seconds':[9,20],'video':probe,'video_sha256':sha(D/'before-after.mp4'),'scope':'Pixel preservation, editable exchange and exposure scheduling only. Art and timed visual acceptance separate.'})
print('Eight cels: preservation, exact APNG, actual LibreSprite save/reopen RGBA and project equality, 3.6s video verified')
