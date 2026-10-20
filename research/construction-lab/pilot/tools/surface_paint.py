#!/usr/bin/env python3
"""Reversible source-attached rigid-part paint; never auto-redraw animation frames."""
import argparse, copy, hashlib, json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from edit_rig_source import atomic_write
PARTS = {'torso','head','shoulder_armor','equipment'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def finite(v):return type(v) in (int,float) and math.isfinite(v)
def validate(design,patch):
    if patch.get('schema') != 'rig-surface-paint/v1' or not isinstance(patch.get('reason'),str) or not patch['reason'].strip():raise ValueError('A supported patch and reason are required')
    strokes=patch.get('strokes')
    if not isinstance(strokes,list) or not 1<=len(strokes)<=1024:raise ValueError('Invalid stroke count')
    for row in strokes:
        if set(row)!={'view','layer','at','color','size'}:raise ValueError('Unexpected stroke field')
        view=design.get('support_matrix',{}).get(row['view'],{})
        if not view or view.get('supported') is False:raise ValueError('Unsupported authored view')
        if row['layer'] not in PARTS:raise ValueError('This adapter paints rigid parts only')
        if not isinstance(row['at'],list) or len(row['at'])!=2 or not all(finite(v) and -96<=v<=96 for v in row['at']):raise ValueError('Invalid local part coordinates')
        if row['color'] not in design['palette']:raise ValueError('Unknown material color')
        if type(row['size']) is not int or not 1<=row['size']<=4:raise ValueError('Unsupported brush size')
def apply(raw,patch):
    if patch.get('expected_source_sha256')!=sha(raw):raise ValueError('Stale source; explicitly rebase the paint')
    source=json.loads(raw);validate(source,patch);out=copy.deepcopy(source)
    painted=out.setdefault('paint_layers',{})
    for row in patch['strokes']:
        painted.setdefault(row['view'],{}).setdefault(row['layer'],[]).append({k:row[k] for k in ['at','color','size']})
    encoded=(json.dumps(out,indent=2,allow_nan=False)+'\n').encode()
    receipt={'schema':'rig-surface-paint-receipt/v1','before_sha256':sha(raw),'after_sha256':sha(encoded),'before_utf8':raw.decode(),'patch':patch,'status':'Candidate: re-render affected actions/views, verify transformed masks/occlusion and review adjacent frames'}
    return encoded,receipt
def undo(raw,receipt):
    if receipt.get('schema')!='rig-surface-paint-receipt/v1' or sha(raw)!=receipt.get('after_sha256'):raise ValueError('Cannot undo over newer art')
    original=receipt['before_utf8'].encode()
    if sha(original)!=receipt['before_sha256'] or apply(original,receipt['patch'])[0]!=raw:raise ValueError('Corrupt receipt')
    return original
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['apply','undo']);p.add_argument('source',type=Path);p.add_argument('patch_or_receipt',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--receipt',type=Path);a=p.parse_args()
    if a.mode=='apply':
        if not a.receipt or a.receipt.resolve() in [a.source.resolve(),a.output.resolve()]:raise ValueError('A distinct receipt path is required')
        new,receipt=apply(a.source.read_bytes(),json.loads(a.patch_or_receipt.read_text()));atomic_write(a.receipt,(json.dumps(receipt,indent=2)+'\n').encode())
    else:new=undo(a.source.read_bytes(),json.loads(a.patch_or_receipt.read_text()))
    atomic_write(a.output,new);print(json.dumps({'output':str(a.output),'source_sha256':sha(new)}))
if __name__=='__main__':main()
