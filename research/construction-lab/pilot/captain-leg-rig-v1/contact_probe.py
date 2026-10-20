"""Actual boot PNG readback in moving fixed-camera512 canvas, two fullcycles."""
from pathlib import Path
from PIL import Image,ImageDraw
import math,json,hashlib,argparse
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def translated(im,root):
 return im.transform((512,288),Image.Transform.AFFINE,(1,0,-128-root[0],0,1,-root[1]),Image.Resampling.NEAREST,fillcolor=(0,0,0,0))
def sole(im):
 box=im.getchannel('A').getbbox();y=box[3]-1;p=im.load();return[min(x for x in range(box[0],box[2])if p[x,y][3]),y]
def probe(pack,out):
 if out.exists():raise ValueError('Refuse priorproof')
 out.mkdir(parents=True);m=json.loads((pack/'manifest.json').read_text());stride=m['root_stride'];duration=m['duration_ticks'];frames=m['frames'];design=m['registered_design']['legs'];records=[];episodes={};material_episodes={};previews={mode:[]for mode in ['physical','global-contact-lock']};max_offset=0
 for mode in previews:
  for tick in range(int(duration*2)):
   for frac in [0,.2,.4,.6,.8]:
    p=(tick+frac)/duration;cycle=math.floor(p);phase=p-cycle;index=max(i for i,f in enumerate(frames)if f['phase']<=phase+1e-12);f=frames[index];physics=[v*p for v in stride];active=[l for l,d in design.items()if(p+d['phase_offset'])%1<.6-1e-12];targets={}
    for leg in active:
     d=design[leg];episode=math.floor(p+d['phase_offset']);targets[leg]=[round(d['rest_sole'][j]+stride[j]*(.3-d['phase_offset']+episode))for j in range(2)]
    drawroot=physics[:]
    if mode=='global-contact-lock'and active:
     chosen=active[0];cached=f['legs'][chosen]['actual_sole'];drawroot=[targets[chosen][j]-cached[j]for j in range(2)]
    max_offset=max(max_offset,math.hypot(*[drawroot[j]-physics[j]for j in range(2)]))
    boots={l:Image.open(pack/'boot-isolates'/f'{l}-{index:02}.png').convert('RGBA')for l in ['right','left']};points={l:sole(translated(im,drawroot))for l,im in boots.items()}
    for l in active:
     ep=f'{mode}/{l}/{math.floor(p+design[l]["phase_offset"])}';episodes.setdefault(ep,[]).append(points[l]);material_episodes.setdefault(ep,set()).add(hashlib.sha256(translated(boots[l],drawroot).tobytes()).hexdigest())
    records.append({'mode':mode,'tick':tick+frac,'pose_key':index,'physical_root':physics,'draw_root':drawroot,'active':active,'actual_world_soles':points,'requested_support':targets})
    if frac==0:
     image=translated(Image.open(pack/f['png']).convert('RGBA'),drawroot);bg=Image.new('RGBA',image.size,(31,34,41,255));bg.alpha_composite(image);ImageDraw.Draw(bg).text((8,8),f'{mode} tick{tick:03} physicalroot{physics[0]:.2f},{physics[1]:.2f}',fill='white');previews[mode].append(bg.convert('RGB'))
 metrics=[]
 for episode,points in episodes.items():
  spans=[max(p[j]for p in points)-min(p[j]for p in points)for j in range(2)];metrics.append({'episode':episode,'samples':len(points),'peak_to_peak_xy':spans,'gate_0_5':max(spans)<=.5,'distinct_whole_boot_RGBA':len(material_episodes[episode]),'whole_boot_material_stable':len(material_episodes[episode])==1})
 for mode,images in previews.items():images[0].save(out/f'{mode}.gif',save_all=True,append_images=images[1:],duration=[round((i+1)*1000/60/10)*10-round(i*1000/60/10)*10 for i in range(len(images))],loop=0,disposal=2)
 r={'schema':'captain-boot-world-readback/v1','manifest_sha256':sha(pack/'manifest.json'),'renderer':'Pillow nearest affine actualPNG raster, NOT GodotGPU','physical_scope':'twofullcycles, fivefractional samplespertick144ticks, native512fixedcamera, noautofit','gate':'Each stanceepisode actualsolexmin/lowestrow peaktopeak≤0.5px, unmodified','metrics':metrics,'physical_pass':all(x['gate_0_5']for x in metrics if x['episode'].startswith('physical/')),'global_contact_lock_pass':all(x['gate_0_5']for x in metrics if x['episode'].startswith('global-contact-lock/')),'global_whole_boot_material_pass':all(x['whole_boot_material_stable']for x in metrics if x['episode'].startswith('global-contact-lock/')),'max_visual_physical_root_offset':max_offset,'rows':records,'policy':'OneglobalXY drawtranslation uses designatedactivefoot cachedactualsole and declaredfixedworld supporttarget. SAMEtranslation applied to BOTHboots and wholeleg PNG; physicalrootcontinues. Bothfeet checked in doublecontact. No independentlymovingboots. Visual root held within eachcachedpose, sourceframechanges remain visible.','limits':['Whole boot equality covers actual isolated native boot RGBA in fixed world canvas, including every colored pixel; calf occlusion in final actor is separate','Pillow CPU readback, not engineGPU proof','Ground points are declared lowestopaqueboot witnesses, not fullphysicalheel/toe collision surface','No bodyart/anatomy/wholegame quality approval','5fractional samples/tick finite, not everyreal-time instant','Episode points change legitimately after swing; consecutiveepisodesnotmerged']}
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('physicalpass',r['physical_pass'],'globallockpass',r['global_contact_lock_pass'],'maxoffset',max_offset)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--pack',type=Path,default=ROOT/'candidate-v8');p.add_argument('--output',type=Path,default=ROOT/'contact-proof-v8');a=p.parse_args();probe(a.pack,a.output)
