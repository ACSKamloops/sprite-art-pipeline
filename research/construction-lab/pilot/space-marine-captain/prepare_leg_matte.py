"""Candidate alpha cleanup, not anatomical or animation approval.

The source master is unchanged. Retain RGB exactly for alpha>=128; remove
lower-alpha pixels and invisible RGB. The contour still needs visual review.
"""
import hashlib, json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'generated/hidden-legs-raw.png'


def main():
    source_bytes=SOURCE.read_bytes()
    binding=json.loads((ROOT/'generated/provenance.json').read_text())
    expected=binding['generated_masters']['hidden-legs-raw.png']['sha256']
    digest=hashlib.sha256(source_bytes).hexdigest()
    if digest!=expected:raise ValueError('Generated master changed; review/rebind required')
    im=Image.open(SOURCE).convert('RGBA')
    original=list(im.get_flattened_data())
    cleaned=[(r,g,b,255)if a>=128 else(0,0,0,0)for r,g,b,a in original]
    im.putdata(cleaned)
    for before,after in zip(original,cleaned):
        if before[3]>=128:assert before[:3]==after[:3] and after[3]==255
        else:assert after==(0,0,0,0)
    path=ROOT/'generated/hidden-leg-matte-candidate.png';im.save(path)
    boxes={}
    for name,box in [('right',(0,0,768,1024)),('left',(768,0,1536,1024))]:
        part=im.crop(box);bbox=part.getbbox();part=part.crop(bbox)
        part.save(ROOT/'generated'/f'concept-{name}-leg.png')
        boxes[name]={'source_half_box':box,'local_alpha_bbox':bbox,'dimensions':part.size}
    assert SOURCE.read_bytes()==source_bytes
    receipt={'source_sha256':digest,'threshold':128,'visible_retained_rgb_exact':True,
             'fully_opaque_or_transparent':True,'master_unchanged':True,
             'transparent_rgb_zeroed':True,'part_crops':boxes,
             'output_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
             'decision':'Provisional matte only; perspective/proportion/contour and rig fitting unapproved.',
             'reason':'Approved native sprite uses hard alpha. Generated master contains tinyalpha exterior RGB and globalpartialalpha. Normalize an explicit candidate; preserve master.'}
    (ROOT/'generated/matte-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__=='__main__':main()
