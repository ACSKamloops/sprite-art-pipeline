"""Source-attached three-value sole contrast experiment, no emission change."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'captain-head-fine-paint-v1/combined-candidate/combined-body-paint.png'
MASK = Path('/home/astra/projects/captain-rig-carry-art-v8/experiments/captain-sole-fill-v1/guarded-fill-mask.png')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE) == 'ceb0108276bb3be3f2d6c31367acb01c57818af2184e1f67e878d9fc97d9c4e8'
assert sha(MASK) == '3eebeb2c2142ee9768ca5f2da02155b720dcd1808df1fd68c4600c3da88fc11d'
before = np.array(Image.open(SOURCE).convert('RGBA'))
mask = np.array(Image.open(MASK).convert('L')) == 255
after = before.copy()
palette = [((30,31,33),(42,45,49)), ((15,16,18),(18,21,25)), ((39,40,42),(74,80,86))]
seen = np.zeros(mask.shape, dtype=bool)
counts = []
for old, new in palette:
    selected = mask & np.all(before[:,:,:3] == old, axis=2)
    after[selected,:3] = new
    seen |= selected
    counts.append({'before':old,'after':new,'texels':int(selected.sum())})
assert np.array_equal(seen, mask), 'Unexpected owned sole palette'
assert np.array_equal(after[~mask], before[~mask])
assert np.array_equal(after[:,:,3], before[:,:,3])
out = HERE / 'candidate'
out.mkdir(exist_ok=False)
Image.fromarray(after).save(out/'combined-head-sole-contrast.png')
(out/'receipt.json').write_text(json.dumps({'state':'BOUNDED_SOLE_PALETTE_CANDIDATE_NOT_ART_APPROVAL',
    'source_sha256':sha(SOURCE),'mask_sha256':sha(MASK),'script_sha256':sha(Path(__file__)),
    'texture_sha256':sha(out/'combined-head-sole-contrast.png'),'palette':counts,
    'outside_owned_RGBA_exact':True,'alpha_exact':True,
    'emission_strength_change':False,'limits':['Authored tread remains inferred','No geometry or motion change','Rendering/review pending']},indent=2)+'\n')
print('PALETTE_CANDIDATE', sum(x['texels'] for x in counts))
