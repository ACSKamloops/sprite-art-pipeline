from pathlib import Path
import subprocess,json,hashlib,io
from PIL import Image,ImageDraw,ImageSequence
OUT=Path(__file__).resolve().parent
SRC=Path('/home/astra/artifacts/captain-guided-key-art-v1')
report=json.load(open(SRC/'report.json'))
receipt={'schema':'independent-decoded-art-review/v1','reviewer':'captain_key_art_fresh_review','limitation':'Chronological decoded actual MP4 images only; no continuous video ingestion.','inputs':{},'variants':[]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p in SRC.glob('*'):
 if p.is_file():receipt['inputs'][str(p)]=sha(p)
for v in report['variants']:
 p=SRC/v['file']; frames=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(p)]))['frames']
 ts=[float(f['best_effort_timestamp_time'])*1000 for f in frames]
 desired=[k*150*v['slowdown'] for k in range(9)]
 indices=[next(i for i,t in enumerate(ts) if t>=target-.01) for target in desired]
 filt='select='+ '+'.join('eq(n\\,%d)'%i for i in indices)
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vf',filt,'-fps_mode','passthrough','-f','image2pipe','-vcodec','png','-'])
 # PNG stream boundaries via IEND chunks.
 parts=raw.split(b'IEND\xaeB`\x82'); imgs=[Image.open(io.BytesIO(x+b'IEND\xaeB`\x82')).convert('RGB') for x in parts if x]
 crop=(250,65,690,445) if v['zoom']==1 else (280,60,960,730)
 fixed=Image.new('RGB',((crop[2]-crop[0])*3,(crop[3]-crop[1]+25)*3),'#22272d'); full=Image.new('RGB',(512*3,(416+25)*3),'#22272d')
 dr=ImageDraw.Draw(fixed); df=ImageDraw.Draw(full)
 for k,img in enumerate(imgs):
  c=img.crop(crop); x=(k%3)*c.width; y=(k//3)*(c.height+25); fixed.paste(c,(x,y)); dr.text((x+4,y+c.height+3),f'key {k%8} @ {ts[indices[k]]:.0f}ms',fill='white')
  small=img.resize((512,416)); xx=(k%3)*512; yy=(k//3)*441; full.paste(small,(xx,yy)); df.text((xx+4,yy+420),f'key {k%8} @ {ts[indices[k]]:.0f}ms',fill='white')
 stem=p.stem; fixed.save(OUT/(stem+'-fixed.png')); full.save(OUT/(stem+'-stage.png'))
 receipt['variants'].append({'file':str(p),'sha256':sha(p),'zoom':v['zoom'],'slowdown':v['slowdown'],'indices':indices,'decoded_timestamps_ms':[ts[i] for i in indices],'fixed_stage_crop':crop,'images':[stem+'-fixed.png',stem+'-stage.png']})
ref=Path('/home/astra/artifacts/captain-motion-reference-v1/Man_walk_1_4.gif'); im=Image.open(ref); ims=[f.convert('RGB') for f in ImageSequence.Iterator(im)]
sheet=Image.new('RGB',(316*4,(392+25)*2),'white'); dr=ImageDraw.Draw(sheet)
for k in range(8):
 idx=round(k*(len(ims)-1)/7); x=(k%4)*316;y=(k//4)*417;sheet.paste(ims[idx],(x,y));dr.text((x+3,y+395),f'reference frame {idx}',fill='black')
sheet.save(OUT/'human-eight-poses.png'); receipt['inputs'][str(ref)]=sha(ref)
base=Path(__file__).resolve().parents[3]
for rel in ['pilot/space-marine-captain/upright-master-v1/native-256.png','pilot/captain-guided-key-art-v1/artifacts/trial-v2/construction.json','pilot/captain-guided-key-art-v1/artifacts/trial-v2/audition-physical.json']+[f'pilot/captain-guided-key-art-v1/artifacts/trial-v2/frames/{i:03}.png' for i in range(8)]:receipt['inputs'][rel]=sha(base/rel)
receipt['evidence_sha256']={p.name:sha(p) for p in OUT.glob('*.png')};(OUT/'sha-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('Decoded all eight actual exports, all eight first-cycle keys and next-cycle key0; sheets:',len(receipt['evidence_sha256']))
