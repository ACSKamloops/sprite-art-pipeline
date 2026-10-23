#!/usr/bin/env python3
"""Reconstruct a connected leg patch from saved paint with explicit registration."""
import argparse, hashlib, importlib.util, json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

HERE=Path(__file__).resolve().parent
POLYGON=[(29,50),(38,50),(39,54),(43,58),(44,67),(29,67),(29,54),(27,53)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--base',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 out=args.output.absolute();assert not out.exists() and not out.is_symlink()
 base=args.base.resolve();source=base/'entry-protected-support/actions/get_up';manifest=json.loads((source/'manifest.json').read_text())
 frames=[]
 for f in manifest['frames']:
  assert sha(source/f['file'])==f['sha256'];frames.append(Image.open(source/f['file']).convert('RGBA'))
 rawpath=HERE/'generation-03/raw.png';ret=json.loads((HERE/'generation-03/return.json').read_text());assert sha(rawpath)==ret['raw_sha256']
 request=json.loads((HERE/'generation-03/request.json').read_text())
 assert sha(HERE/'generation-03/prompt.txt')==request['prompt_sha256']
 for f in request['ordered_inputs']:assert sha(HERE/'generation-03'/f['file'])==f['sha256']
 raw=Image.open(rawpath).convert('RGBA');a=np.array(raw.resize((80,80),Image.Resampling.NEAREST));a[:,:,3]=np.where(a[:,:,3]>=200,255,0);a[a[:,:,3]==0]=0
 registered=Image.new('RGBA',(80,80));registered.paste(Image.fromarray(a),(0,-10))
 mask=Image.new('L',(80,80));ImageDraw.Draw(mask).polygon(POLYGON,fill=255);owner=np.array(mask)>0
 original=np.array(frames[3]);patch=np.array(registered);repaired=original.copy();repaired[owner]=patch[owner]
 assert np.array_equal(repaired[~owner],original[~owner])
 frames[3]=Image.fromarray(repaired)
 spec=importlib.util.spec_from_file_location('bank_leg',args.repo/'research/pixelengine-imagen/tools/build-rpg-bank.py');bank=importlib.util.module_from_spec(spec);spec.loader.exec_module(bank)
 out.mkdir(parents=True)
 provenance={'operation':'Saved ImageGen connected folded-leg paint, explicit shared patch translation and owned pixel replacement',
  'raw_sha256':sha(rawpath),'raw_dimensions':list(raw.size),'whole_raw_to_native':[80,80],'nearest_center':True,'alpha_threshold':200,
  'patch_translation':[0,-10],'registration_reason':'Provider shifted entire return down; align generated knee/boot patch to frozen target before masking. Not automatic bbox fitting or source-animation recentering.',
  'allowed_polygon':POLYGON,'source_manifest_sha256':sha(source/'manifest.json'),'source_frame03_sha256':sha(source/'frames/0003.png'),
  'source_support05':'guarded source-restored lower-leg variant; human playback not accepted','human_feedback':'Leg vanishes in one frame; repair03 without changing time or other poses'}
 bank.export_action(out,'get_up','SE',frames,{'loop':False,'holds':[f['hold'] for f in manifest['frames']],'events':[]},provenance,list(range(10)))
 from sprite_lab import History,candidate_transaction,canonical_json,project_hash,render_frame
 initial=json.loads((source/'project.json').read_text());f=initial['frames'][3];cel=f['cels']['body']
 coords=[[int(x),int(y)] for y,x in zip(*np.nonzero(owner))]
 tx=candidate_transaction(initial,cel,frames[3],coords);tx['reason']='Restore connected folded second leg in frame03 after user playback rejection; protected surrounding pose'
 hist=History(initial);hist.apply(tx);final=hist.project;journal=hist.journal();assert render_frame(final,f['id']).tobytes()==frames[3].tobytes()
 assert project_hash(History.replay(initial,journal).project)==project_hash(final)
 hist.undo();assert project_hash(hist.project)==project_hash(initial)
 (out/'editor').mkdir();(out/'editor/initial.json').write_text(canonical_json(initial)+'\n');(out/'editor/final.json').write_text(canonical_json(final)+'\n');write(out/'editor/journal.json',journal)
 mask.save(out/'allowed-mask.png');registered.save(out/'registered-paint.png');frames[3].save(out/'repaired03.png')
 changed=(repaired!=original).any(axis=-1)
 write(out/'VERIFIED.json',{'changed_frame':3,'changed_RGBA_pixels':int(changed.sum()),'allowed_pixels':int(owner.sum()),'outside_mask_exact':True,
  'other_nine_frames_and_holds_exact':True,'undo_replay_exact':True,'raw_sha256':sha(rawpath),'repaired_frame_sha256':sha(out/'repaired03.png'),
  'provenance':provenance,'scope':'Literal construction/export/editor verification, not art acceptance'})
 sheet=Image.new('RGB',(960,350),(221,217,204));draw=ImageDraw.Draw(sheet)
 for k,(im,label) in enumerate([(frames[2],'preceding02'),(Image.fromarray(original),'old03'),(frames[3],'repaired03'),(frames[4],'following04')]):
  up=im.resize((240,240),Image.Resampling.NEAREST);sheet.paste(up,(k*240,25),up);sheet.paste(im,(k*240+80,265),im);draw.text((k*240+4,5),label,fill='black')
 sheet.save(out/'leg-comparison.png');print(json.dumps({'output':str(out),'changed_pixels':int(changed.sum()),'outside_mask_exact':True}))
if __name__=='__main__':main()
