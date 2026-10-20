"""Actual local-browser clock, source raster and timed presentation receipts."""
from pathlib import Path
import argparse, base64, hashlib, io, json, subprocess
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
CLI='/home/astra/.codex/skills/playwright/scripts/playwright_cli.sh'


def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',required=True)
    p.add_argument('--url');p.add_argument('--player-file',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('Preserve prior browser receipts')
    a.output.mkdir(parents=True)
    url=a.url or 'http://127.0.0.1:8144/pilot/space-marine-captain/animation-review/?candidate='+a.candidate
    js='''async (page) => {
      await page.goto(__CANDIDATE_URL__);
      await page.waitForFunction(()=>window.CaptainReview?.ready);
      const tests=await page.evaluate(()=>{
        const api=window.CaptainReview,m=api.manifest,checks=[],rasters=[];
        let start=0;
        for(let n=0;n<m.frames.length;n++){
          const f=m.frames[n],next=n+1<m.frames.length?m.frames[n+1].physical_root:m.root_stride;
          for(const fraction of[0,.2,.5,.8]){
            api.seekMs(start+fraction*f.duration_ms);const s=api.state();
            const expected=f.physical_root.map((v,i)=>v+(next[i]-v)*fraction);
            checks.push({frame:n,fraction,selected:s.frame,root:s.physical_root,
              pass:s.frame===n&&s.physical_root.every((v,i)=>Math.abs(v-expected[i])<1e-8)});
          }
          api.seek(n);rasters.push({frame:n,png:document.getElementById('native').toDataURL('image/png')});
          api.seekMs(start+f.duration_ms-.001);checks.push({frame:n,near_end:true,pass:api.state().frame===n});
          start+=f.duration_ms;
        }
        api.seekMs(m.cycle_ms);const wrap=api.state();
        checks.push({wrap:true,pass:wrap.frame===0&&wrap.physical_root.every((v,i)=>Math.abs(v-m.root_stride[i])<1e-8)});
        return{checks,rasters};
      });
      const timed=[];
      for(const scale of[1,2]){
        await page.evaluate(scale=>{
          const el=document.getElementById('scale');el.value=String(scale);el.dispatchEvent(new Event('change'));
          const api=window.CaptainReview;api.seekMs(0);api.play();
        },scale);
        for(let i=0;i<12;i++){
          await page.waitForTimeout(230);
          timed.push(await page.evaluate(()=>({state:window.CaptainReview.state(),
            native:document.getElementById('native').toDataURL('image/png'),
            stage:document.getElementById('stage').toDataURL('image/png')})));
        }
        await page.evaluate(()=>window.CaptainReview.pause());
      }
      return{...tests,timed};
    }'''.replace('__CANDIDATE_URL__',json.dumps(url))
    result=subprocess.run([CLI,'-s=captain-review','run-code',js],cwd=ROOT,capture_output=True,text=True)
    (a.output/'cli-capture.txt').write_text(result.stdout+result.stderr)
    assert result.returncode==0 and '### Error' not in result.stdout,result.stdout[:1000]
    captured=json.loads(result.stdout.split('### Result\n',1)[1].split('\n###',1)[0])
    assert all(row['pass']for row in captured['checks'])
    source=ROOT/'pilot/space-marine-captain'/a.candidate
    manifest_path=source/'manifest.json';m=json.loads(manifest_path.read_text())
    def png(data,path):
        blob=base64.b64decode(data.split(',',1)[1]);path.write_bytes(blob)
        return Image.open(io.BytesIO(blob)).convert('RGBA'),hashlib.sha256(blob).hexdigest()
    raster_rows=[]
    for row in captured['rasters']:
        f=m['frames'][row['frame']];expected_path=source/f['file']
        assert hashlib.sha256(expected_path.read_bytes()).hexdigest()==f['sha256']
        image,digest=png(row['png'],a.output/f"pose-{row['frame']:02}.png")
        assert image.tobytes()==Image.open(expected_path).convert('RGBA').tobytes()
        raster_rows.append({'frame':row['frame'],'actual_browser_png_sha256':digest,'RGBA_exact_source':True})
    timed_rows=[];images=[]
    for i,row in enumerate(captured['timed']):
        state=row['state'];f=m['frames'][state['frame']]
        image,digest=png(row['native'],a.output/f'timed-native-{i:02}.png')
        assert image.tobytes()==Image.open(source/f['file']).convert('RGBA').tobytes()
        _,stage_hash=png(row['stage'],a.output/f'timed-stage-{i:02}.png')
        timed_rows.append({**state,'actual_native_sha256':digest,'actual_stage_sha256':stage_hash,'RGBA_exact_source':True});images.append(image)
    for offset in range(0,len(images),6):
        sheet=Image.new('RGBA',(6*256,280),(38,43,49,255));draw=ImageDraw.Draw(sheet)
        for x,image in enumerate(images[offset:offset+6]):
            sheet.alpha_composite(image,(x*256,24));r=timed_rows[offset+x]
            draw.text((x*256+6,5),f"pose{r['frame']} {r['clock_ms']:.0f}ms {r['scale']}x",fill='white')
        sheet.save(a.output/f'chronology-{offset//6}.png')
    receipt={'candidate_manifest_sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
             'player_sha256':hashlib.sha256((a.player_file or source.parent/'animation-review/index.html').read_bytes()).hexdigest(),
             'clock_root_checks':captured['checks'],'source_rasters':raster_rows,'timed':timed_rows,
             'scope':'Actual Chromium canvas readback, all72pose renders and timed native/2x presentation; not continuous video ingestion or art approval'}
    (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'candidate':a.candidate,'checks':len(captured['checks']),'source_exact_poses':len(raster_rows),'timed_samples':len(timed_rows),'output':str(a.output)}))


if __name__=='__main__':main()
