#!/usr/bin/env python3
"""Make a bounded one-pixel breath from a real neutral; fixed lower body.

Authored source-pixel deformation, not new ImageGen paint or physical rig.
One inverse source map includes transparency to erase the former upper edge.
"""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--chest',type=int,default=69);p.add_argument('--hip',type=int,default=84);args=p.parse_args()
 assert not args.out.exists();args.out.mkdir(parents=True)
 im=np.array(Image.open(args.source).convert('RGBA'));assert im.shape==(128,128,4)
 yy,xx=np.indices((128,128));rows=np.array([0,14,args.chest,args.hip,127]);targets=rows+np.array([0,-1,-1,0,0]);sy=np.floor(np.interp(np.arange(128),targets,rows)+.5).astype(int)[:,None].repeat(128,axis=1)
 xy=np.stack((xx,sy),axis=-1).astype(np.int16);result=im[sy,xx]
 assert np.array_equal(result[args.hip:],im[args.hip:])
 Image.fromarray(result).save(args.out/'23.png');np.savez_compressed(args.out/'source-map.npz',source_xy=xy)
 np.testing.assert_array_equal(im[xy[:,:,1],xy[:,:,0]],result)
 rec={'schema':'emberwake-one-pixel-breath/v1','source':str(args.source.resolve()),'source_sha256':sha(args.source),'source_points_y':rows.tolist(),'target_points_y':targets.tolist(),'native_stage':[128,128],'output_sha256':sha(args.out/'23.png'),'source_map_sha256':sha(args.out/'source-map.npz'),'fixed_lower_body_from_row':args.hip,'lower_rgba_equal':True,'source_replay_equal':True,'changed_rgba_pixels':int(np.any(im!=result,axis=2).sum()),'scope':'One pixel upward head/chest excursion; no identity repaint, new pose count, art rating or hidden surface claim. Preserve existing two .58s idle holds.'}
 (args.out/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n');print(args.out/'23.png')
if __name__=='__main__':main()
