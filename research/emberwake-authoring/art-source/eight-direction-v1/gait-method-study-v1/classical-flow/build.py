#!/usr/bin/env python3
"""Bounded classical-flow test. No learned model, no new semantic paint."""
from pathlib import Path
import hashlib, json, shutil
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
SRC = Path('/home/astra/artifacts/emberwake-source-cel-game-preview-v11/bake/rowan/southeast')
N = 128
Y, X = np.mgrid[:N, :N].astype(np.float32)
GRID = np.dstack((X, Y))

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + '\n')

def remap(arr, coords, interp=cv2.INTER_LINEAR):
    return cv2.remap(arr, coords[:, :, 0], coords[:, :, 1], interp,
                     borderMode=cv2.BORDER_CONSTANT, borderValue=0)

def gray(rgba):
    a = rgba[:, :, 3:4].astype(np.float32) / 255
    rgb = rgba[:, :, :3].astype(np.float32) * a + 176 * (1-a)
    return cv2.cvtColor(np.uint8(np.rint(rgb)), cv2.COLOR_RGB2GRAY)

def get_flow(a, b, method):
    # Native sampling so one flow unit equals one sprite pixel.
    ga, gb = gray(a), gray(b)
    if method == 'dis':
        op = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        op.setFinestScale(0)
        op.setVariationalRefinementIterations(10)
        return op.calc(ga, gb, None)
    return cv2.calcOpticalFlowFarneback(ga, gb, None, .5, 4, 13, 5, 7, 1.5, 0)

def invcoords(flow, t):
    coords = GRID.copy()
    for _ in range(6):
        coords = GRID - t * remap(flow, coords)
    return coords

def interpolate(a, b, ab, ba, t, mode):
    ca, cb = invcoords(ab, t), invcoords(ba, 1-t)
    aa, bb = remap(a, ca, cv2.INTER_NEAREST), remap(b, cb, cv2.INTER_NEAREST)
    if mode == 'single':
        return (aa if t <= .5 else bb).copy()
    if mode == 'source':
        # All output paint comes literally from one nearest-sampled donor.
        out = (aa if t <= .5 else bb).copy()
        # Opposite donor fills only transparent holes, not partial-alpha edges.
        alternate = bb if t <= .5 else aa
        holes = (out[:,:,3] == 0) & (alternate[:,:,3] > 0)
        out[holes] = alternate[holes]
        return out
    # Deliberate premultiplied blend: newly mixed RGB/alpha is disclosed.
    af, bf = aa.astype(np.float32) / 255, bb.astype(np.float32) / 255
    alpha = af[:,:,3] * (1-t) + bf[:,:,3] * t
    rgb = af[:,:,:3] * af[:,:,3:4] * (1-t) + bf[:,:,:3] * bf[:,:,3:4] * t
    rgb = np.divide(rgb, alpha[:,:,None], out=np.zeros_like(rgb), where=alpha[:,:,None]>0)
    return np.uint8(np.rint(np.dstack((rgb, alpha)).clip(0,1)*255))

def sheet(lanes, scale, bg, output):
    w, h = 8 * (scale+8), len(lanes)*(scale+25)
    result = Image.new('RGB', (w,h), bg)
    d = ImageDraw.Draw(result)
    for row, (label, frames) in enumerate(lanes):
        for col, frame in enumerate(frames):
            cel = frame.resize((scale,scale), Image.Resampling.NEAREST)
            x, y = col*(scale+8), row*(scale+25)+20
            result.paste(cel,(x,y),cel)
            d.text((x+2,y-17),f'{label} {col}', fill='#ffffff' if sum(bg)<450 else '#151515')
    result.save(output)

def main():
    cv2.setNumThreads(8)
    arrays=[]; inputs=[]
    for i in range(8):
        dst=ROOT/'inputs'/f'{i:02}.png'; shutil.copyfile(SRC/f'{i:02}.png',dst)
        arrays.append(np.array(Image.open(dst).convert('RGBA')))
        inputs.append({'path':str(dst.relative_to(ROOT)), 'sha256':digest(dst)})
    flows=ROOT/'flows'; flows.mkdir(exist_ok=True)
    lanes=[]; timelines={}
    baseline=[Image.fromarray(a) for a in arrays]
    timelines['control']={'frames':[f'inputs/{i:02}.png' for i in range(8)],'hold':[9,160]}
    lanes.append(('control',baseline))
    stats=[]
    for method in ('dis','farneback'):
        pairs=[]
        for i in range(8):
            a,b=arrays[i],arrays[(i+1)%8]
            ab,ba=get_flow(a,b,method),get_flow(b,a,method)
            np.savez_compressed(flows/f'{method}-{i:02}.npz',ab=ab,ba=ba)
            pairs.append((ab,ba))
        for mode in ('source','blend'):
            name=f'{method}-{mode}'; dest=ROOT/'frames'/name;dest.mkdir(parents=True,exist_ok=True)
            paths=[]; midpoints=[]; exact=True
            for i,(ab,ba) in enumerate(pairs):
                for sub in range(4):
                    t=sub/4
                    out=arrays[i].copy() if sub==0 else interpolate(arrays[i],arrays[(i+1)%8],ab,ba,t,mode)
                    path=dest/f'{i*4+sub:02}.png';Image.fromarray(out).save(path)
                    paths.append(str(path.relative_to(ROOT)))
                    if sub==0: exact=exact and np.array_equal(out,arrays[i])
                    if sub==2: midpoints.append(Image.fromarray(out))
            timelines[name]={'frames':paths,'hold':[9,640]}
            stats.append({'lane':name,'original_eight_rgba_exact':exact,'new_color_mixing':mode=='blend'})
            lanes.append((name,midpoints))
    proof=ROOT/'proof';proof.mkdir(exist_ok=True)
    for scale in (84,128,256):
        for label,bg in [('light',(238,236,226)),('dark',(28,32,40)),('game',(38,62,50))]:
            sheet(lanes,scale,bg,proof/f'midpoints-{scale}-{label}.png')
    save_json(ROOT/'TIMELINES.json',{'cycle':[9,20],'lanes':timelines})
    save_json(ROOT/'METHOD.json',{'identity':'Rowan','view':'southeast','inputs':inputs,'versions':{'opencv':cv2.__version__,'numpy':np.__version__},'parameters':{'resolution':128,'gray':'RGBA composite against176 RGB then grayscale','dis':{'preset':'medium','finest_scale':0,'variational_iterations':10},'farneback':{'pyr_scale':.5,'levels':4,'winsize':13,'iterations':5,'poly_n':7,'poly_sigma':1.5,'flags':0},'inverse_iterations':6,'paint_sampling':'nearest','subframes':4},'checks':stats,'qualifications':['Classical optical flow, no learned/generative model or H3.','Original8 are exact at every fourth sample; key pose timing/cycle0.45 remains exact.','Source mode chooses one donor and fills only alpha0 holes; this is not inferred anatomy.','Blend mixes premultiplied nearest samples and introduces new RGB/alpha.','Neither more frames nor these mechanical checks imply motion quality.']})
    print(json.dumps({'lanes':list(timelines),'checks':stats,'proof':str(proof)},indent=2))

if __name__=='__main__': main()
