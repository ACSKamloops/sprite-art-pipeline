#!/usr/bin/env python3
"""Retain an actual built-in ImageGen result and bind its request inputs."""
from pathlib import Path
import argparse, hashlib, json, shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'art-source/eight-direction-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--actor',choices=['rowan','lyra'],required=True)
    parser.add_argument('--view',choices=['southeast','northeast'],required=True)
    parser.add_argument('--original',type=Path,required=True)
    args=parser.parse_args()
    request=BASE/'requests'/f'{args.actor}-{args.view}-request.json'
    data=json.loads(request.read_text())
    assert sha(ROOT/data['prompt'])==data['prompt_sha256']
    for item in data['inputs']:
        assert sha(ROOT/item['project_path'])==item['sha256']
    raw=BASE/'raw'/f'{args.actor}-{args.view}-initial.png'
    if raw.exists():raise SystemExit('Raw return already retained; choose a distinct candidate')
    shutil.copyfile(args.original,raw)
    with Image.open(raw) as im:
        size,mode=im.size,im.mode
    data.update({'raw':str(raw.relative_to(ROOT)),'raw_sha256':sha(raw),
        'raw_size':list(size),'raw_mode':mode,'generated_original':str(args.original),
        'quality_status':'Candidate paint; independent pose/view/motion review required.'})
    request.write_text(json.dumps(data,indent=2)+'\n')
    print(args.actor,args.view,size,sha(raw))
if __name__=='__main__':main()
