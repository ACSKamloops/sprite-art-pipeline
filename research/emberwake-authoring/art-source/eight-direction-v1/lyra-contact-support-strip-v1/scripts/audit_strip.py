"""Replay the three saved source maps and document declared depth overlaps."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
P=R/'strip-final'
def a(p):return np.array(Image.open(p).convert('RGBA'))
def over(back,front):return np.array(Image.alpha_composite(Image.fromarray(back),Image.fromarray(front)))
master=a(R/'inputs/master04.png')
records=[]
for phase in [4,5,6]:
    current=a(R/f'inputs/{phase:02}-current.png')
    body_layer=a(R/f'inputs/{phase:02}-body.png');body=body_layer[...,3]>0
    old=np.array(Image.open(P/f'{phase:02}-old-Q-visible-owner.png').convert('L'))>0
    maps=np.load(P/f'{phase:02}-source-maps.npz')
    layers=[]
    witnesses=[]
    for role,key,ownerkey in [('cloth','cloth_source04_xy','target_cloth'),('boot','boot_source04_xy','target_boot')]:
        layer=np.zeros_like(master)
        for y,x in np.argwhere(maps[ownerkey]):
            sx,sy=maps[key][y,x];layer[y,x]=master[sy,sx]
            witnesses.append({'role':role,'target':[int(x),int(y)],'master04':[int(sx),int(sy)],'source_RGBA':master[sy,sx].tolist()})
        assert np.array_equal(layer,a(P/f'{phase:02}-{("cloth-layer" if role=="cloth" else "complete-boot-layer")}.png'))
        layers.append(layer)
    base=current.copy();base[old]=0
    replay=over(over(base,layers[0]),layers[1]);replay[body]=current[body]
    lower=over(layers[0],layers[1]);target=maps['target_cloth']|maps['target_boot'];overlap=target&body
    normal=over(lower,body_layer);replay[overlap]=normal[overlap]
    path=P/f'{phase:02}-{("rejected-boot-only-diagnostic" if phase==6 else "support-feasibility")}.png'
    assert np.array_equal(replay,a(path))
    occlusions=[]
    for y,x in np.argwhere(target&~old&~body&(current[...,3]>0)):
        occlusions.append({'target':[int(x),int(y)],'retained_base_other_lower_RGBA':current[y,x].tolist(),
                           'foreground_Q_part':'boot'if maps['target_boot'][y,x]else'cloth','composed_RGBA':replay[y,x].tolist()})
    (P/f'{phase:02}-OTHER-LOWER-OCCLUSIONS.json').write_text(json.dumps(occlusions,indent=2)+'\n')
    (P/f'{phase:02}-SOURCE-SAMPLES.json').write_text(json.dumps(witnesses,indent=2)+'\n')
    field=json.loads((P/f'{phase:02}-FIELD.json').read_text())
    if phase==6:assert field['nonpositive_count']==41 and not maps['target_cloth'].any()
    else:assert field['nonpositive_count']==0
    records.append({'phase':phase,'saved_map_replay_RGBA_exact':True,'full_rigid_boot_samples':int(maps['target_boot'].sum()),
                    'all_source_samples':len(witnesses),'new_Q_over_other_existing_lower_pixels':len(occlusions),
                    'new_lower_upper_source_over_intersections':int(overlap.sum()),'body_layer_input_unmodified':True,
                    'upper_displayed_RGBA_exact_outside_new_overlap':bool(np.array_equal(replay[body&~overlap],current[body&~overlap])),
                    'diagnostic_only':phase==6})
assert (P/'04-support-feasibility.png').read_bytes()==(R/'inputs/frozen04-plus8.png').read_bytes()
(R/'AUDIT.json').write_text(json.dumps({'phases':records,'frozen04_candidate_PNG_bytes_exact':True,'06_inverted_cloth_not_rasterized':True,'new_paint':0},indent=2)+'\n')
print(json.dumps(records))
