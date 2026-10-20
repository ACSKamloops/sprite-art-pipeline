#!/usr/bin/env python3
"""Make a local review player bound to an exact candidate bake, no model calls."""
from pathlib import Path
import argparse,json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
HTML='''<!doctype html><meta charset="utf-8"><title>Emberwake direction review</title>
<style>body{background:#1c232e;color:#e8eef8;font:16px system-ui;margin:24px}header{display:flex;gap:18px;align-items:center;flex-wrap:wrap}button,select{font:inherit;padding:8px;background:#344052;color:white;border:1px solid #637389;border-radius:4px}#grid{display:grid;grid-template-columns:repeat(3,minmax(250px,1fr));gap:16px;margin-top:20px}.card{background:#2e394b;padding:12px;border-radius:8px}.stage{display:flex;align-items:end;min-height:260px;gap:14px}canvas{image-rendering:pixelated;background:repeating-conic-gradient(#344052 0% 25%,#3b495a 0% 50%)50%/16px 16px}.small{image-rendering:pixelated}small{color:#afc3d9}h2{font-size:18px;margin:0 0 8px}#note{max-width:1000px}</style>
<h1>Eight-direction art review</h1><p id="note">Native paint at 2× beside the actual 0.66× game scale. Each one-shot includes neutral entry and recovery. Step through every cel as well as watching normal speed. This player is an art candidate, not engine verification.</p>
<header><label>Action <select id="action"><option>walk</option><option>attack</option><option>cast</option><option>hurt</option><option>dodge</option><option>idle</option></select></label><label>Speed <select id="speed"><option value="1">1× normal</option><option value="0.5">0.5×</option><option value="0.25">0.25×</option></select></label><button id="pause">Pause</button><button id="step">Next cel</button><label>Background <select id="bg"><option value="checker">Checker</option><option value="#eee8dc">Light</option><option value="#151820">Dark</option><option value="#617b56">Ground</option></select></label></header><div id="grid"></div><p><small id="bind"></small></p>
<script>
let cards=[],paused=false,time=0,last=0;const action=document.querySelector('#action'),speed=document.querySelector('#speed');
function timeline(card){const clip=card.manifest.animations[card.view+'_'+action.value],idle=card.manifest.animations[card.view+'_idle'];return clip.loop?clip:{frames:[idle.frames[0],...clip.frames,idle.frames[0]],holds:[.25,...clip.holds,.3],loop:true};}
function paint(c){const clip=timeline(c),duration=clip.holds.reduce((a,b)=>a+b,0);let t=time%duration,k=0;while(k<clip.holds.length-1&&t>=clip.holds[k])t-=clip.holds[k++];const i=clip.frames[k],cols=c.manifest.columns;for(const canvas of c.canvases){const ctx=canvas.getContext('2d');ctx.clearRect(0,0,128,128);ctx.drawImage(c.image,i%cols*128,Math.floor(i/cols)*128,128,128,0,0,128,128);}c.label.textContent='Cel '+k+'/'+(clip.frames.length-1)+' · atlas '+i+' · '+clip.holds[k].toFixed(5)+' s';}
function tick(ts){if(!paused)time+=(ts-last)/1000*Number(speed.value);last=ts;cards.forEach(paint);requestAnimationFrame(tick);}
document.querySelector('#pause').onclick=e=>{paused=!paused;e.target.textContent=paused?'Play':'Pause';};
document.querySelector('#step').onclick=()=>{paused=true;document.querySelector('#pause').textContent='Play';if(!cards.length)return;const c=timeline(cards[0]),dur=c.holds.reduce((a,b)=>a+b,0);let phase=time%dur,sum=0;for(let h of c.holds){sum+=h;if(sum>phase+.00001){time+=sum-phase+.000001;break;}}cards.forEach(paint);};
action.onchange=()=>{time=0;};document.querySelector('#bg').onchange=e=>document.querySelectorAll('canvas').forEach(c=>{c.style.background=e.target.value==='checker'?'':e.target.value;});
(async()=>{const receipt=await(await fetch('REVIEW-INPUTS.json')).json();document.querySelector('#bind').textContent='Exact bake: '+receipt.bake_sha256;for(const actor of ['rowan','lyra','brann']){const manifest=await(await fetch(actor+'/animations.json')).json();const image=new Image();image.src=actor+'/atlas.png';await image.decode();for(const view of ['southeast','northeast','southwest','northwest']){const card=document.createElement('div');card.className='card';card.innerHTML='<h2>'+actor+' · '+view+'</h2><div class="stage"><canvas width="128" height="128" style="width:256px;height:256px"></canvas><canvas class="small" width="128" height="128" style="width:84.48px;height:84.48px"></canvas></div><small></small>';document.querySelector('#grid').appendChild(card);cards.push({manifest,image,view,canvases:[...card.querySelectorAll('canvas')],label:card.querySelector('small')});}}requestAnimationFrame(tick);})();
</script>'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--bake',required=True,type=Path);p.add_argument('--out',required=True,type=Path);args=p.parse_args()
 assert not args.out.exists();args.out.mkdir(parents=True)
 inputs={'bake_sha256':sha(args.bake/'REPLAY.json'),'actors':{}}
 for a in ['rowan','lyra','brann']:
  d=args.out/a;d.mkdir();inputs['actors'][a]={}
  for f in ['atlas.png','animations.json']:
   shutil.copyfile(args.bake/a/f,d/f);inputs['actors'][a][f]=sha(d/f)
 (args.out/'REVIEW-INPUTS.json').write_text(json.dumps(inputs,indent=2)+'\n');(args.out/'index.html').write_text(HTML)
 print(args.out/'index.html')
if __name__=='__main__':main()
