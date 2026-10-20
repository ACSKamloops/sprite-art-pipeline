"""Independent Pillow source-alpha reference against actual engine readback."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def compare(actual,expected):
    delta=np.abs(np.asarray(actual,dtype=np.int16)-np.asarray(expected,dtype=np.int16))
    return {'max_channel_error':int(delta.max()),'channels_over_one_lsb':int((delta>1).sum())}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--pack',type=Path,required=True);args=parser.parse_args()
    report=json.loads((args.output/'report.json').read_text());pack=json.loads((args.pack/'pack.json').read_text())
    if sha(args.pack/'pack.json')!=report['pack_sha256']:raise ValueError('Changed pack')
    rows=[];negative=None
    for item in report['gpu_observations']:
        source=pack['images'][item['cel']];p=args.pack/source['file']
        if sha(p)!=source['sha256']:raise ValueError('Changed source sprite')
        foreground=Image.open(p).convert('RGBA');background=Image.new('RGBA',foreground.size,tuple(item['background'])+(255,));expected=Image.alpha_composite(background,foreground)
        actual=Image.open(args.output/item['file']).convert('RGBA');result=compare(actual,expected);rows.append(dict(item,result=result))
        if negative is None:
            shifted=background.copy();shifted.paste(actual,(1,0));negative=compare(shifted,expected)
    if any(x['result']['channels_over_one_lsb']for x in rows):raise AssertionError('Actual GPU source-alpha compositing mismatch')
    assert negative['channels_over_one_lsb']>0
    proof={'state':'PASS_ACTUAL_GPU_COMPOSITING_NOT_ART_APPROVAL','actual_native_readbacks':len(rows),'pack_sha256':sha(args.pack/'pack.json'),'max_channel_error':max(x['result']['max_channel_error']for x in rows),'negative_actual_image_shift_one_px':negative,'checks':rows,'limits':['Two opaque backgrounds, one view, all65 actual native poses','Soft-alpha blend tolerance1LSB perchannel','GPU screenshots and engine frame events are not continuous video ingestion','No full plant/material identity or sprite craft acceptance']}
    (args.output/'independent-gpu-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='checks'}))
if __name__=='__main__':main()
