#!/usr/bin/env python3
"""A bounded authored recovery edit, preserving wince and rigid lower boots.

This edits one actual recovery drawing; it is not atlas registration/fitting.
Source coordinates and literal .10s exposure stay recorded for paired review.
"""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--lift',required=True,type=int,choices=[2,4]);args=p.parse_args()
 assert not args.out.exists();args.out.mkdir(parents=True)
 source=np.array(Image.open(args.source).convert('RGBA'));assert source.shape==(128,128,4)
 rows=np.array([0,14,70,90,94,127]);targets=rows+np.array([0,-args.lift,-args.lift,-args.lift//2,0,0]);assert np.all(np.diff(targets)>0)
 yy,xx=np.indices((128,128));sy=np.floor(np.interp(np.arange(128),targets,rows)+.5).astype(int)[:,None].repeat(128,axis=1);xy=np.stack((xx,sy),axis=-1).astype(np.int16);result=source[sy,xx]
 assert np.array_equal(result[94:],source[94:])
 np.testing.assert_array_equal(source[xy[:,:,1],xy[:,:,0]],result)
 Image.fromarray(result).save(args.out/'25.png');np.savez_compressed(args.out/'source-map.npz',source_xy=xy)
 rec={'schema':'emberwake-hurt-recovery-source-edit/v1','source':str(args.source.resolve()),'source_sha256':sha(args.source),'source_points_y':rows.tolist(),'target_points_y':targets.tolist(),'intent':'Relax an existing compact wince toward neutral with bounded upper-body rise; preserve source expression and lower boots. No arms-out replacement or per-pose atlas fitting.','head_chest_rise_px':args.lift,'rigid_boot_rows':[94,128],'boot_rgba_equal':True,'source_replay_equal':True,'hold_unchanged':[1,10],'output_sha256':sha(args.out/'25.png'),'source_map_sha256':sha(args.out/'source-map.npz'),'changed_rgba_pixels':int(np.any(result!=source,axis=2).sum()),'art_status':'Unreviewed actual changed drawing; no score.'}
 (args.out/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n');print(args.out/'25.png')
if __name__=='__main__':main()
