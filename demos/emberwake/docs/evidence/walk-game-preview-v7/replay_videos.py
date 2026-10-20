"""Replay the actual six native-capture encodes into a fresh folder."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert not a.out.exists();a.out.mkdir(parents=True)
 captures=json.loads((a.native/'RECEIPT.json').read_text());expected={x['clip']:x for x in json.loads((ROOT/'media/MEDIA-RECEIPT.json').read_text())}
 # Verify original complete capture ledger before feeding source media.
 count=0
 for line in (a.native/'SHA256SUMS').read_text().splitlines():
  h,rel=line.split(None,1);f=(a.native/rel.strip()).resolve();assert f.is_relative_to(a.native.resolve()) and sha(f)==h;count+=1
 def encode(clip):
  key=clip['actor']+'-'+clip['view'];assert Path(key).name==key
  out=a.out/(key+'.mp4');cmd=['ffmpeg','-hide_banner','-loglevel','error','-framerate','320','-i',str(a.native/key/'%04d.png'),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
  r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=avg_frame_rate,nb_read_frames,duration','-of','json',str(out)],text=True))['streams'][0]
  assert probe['avg_frame_rate']=='320/1' and int(probe['nb_read_frames'])==288 and float(probe['duration'])==.9
  assert sha(out)==expected[key]['mp4_sha256'],'Encoded bytes differ; record toolchain drift rather than overwriting expected hashes.'
  return {'clip':key,'command':cmd,'PNG_to_MP4_bytes_exact':True,'sha256':sha(out),'probe':probe}
 with ThreadPoolExecutor(max_workers=3)as pool:rows=list(pool.map(encode,captures['clips']))
 receipt={'passed':True,'capture_ledger_entries':count,'clips':rows,'ffmpeg_version':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0],'scope':'Actual media reproduction only, no motion/contact score'}
 (a.out/'REPLAY-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(f'PASS {len(rows)} actual native MP4 byte replays; {count} original capture hashes')
if __name__=='__main__':main()
