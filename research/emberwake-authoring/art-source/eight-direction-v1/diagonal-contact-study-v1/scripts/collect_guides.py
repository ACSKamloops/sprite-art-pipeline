"""Read-only intake. Run once; retained source files are immutable inputs."""
from pathlib import Path
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[1]
B = Path('/home/astra/projects/emberwake-demo/art-source/eight-direction-v1')
L = Path('/home/astra/artifacts/emberwake-lyra-stance-spring-v1')
N = Path('/home/astra/artifacts/emberwake-brann-ne06-recovery-v1/portable-donor07-v1')
items = {
    'lyra-04-map.npz': L / 'inputs/repair03-04/maps/04-left-leg.npz',
    'lyra-05-map.npz': L / 'inputs/repair05/maps/05-left-front.npz',
    'lyra-06-source.png': L / 'inputs/current/06.png',
    'lyra-curve-and-owners.json': L / 'waist-completion-v1/REBUILD-RECEIPT.json',
    'rowan-04-construction.json': B / 'rowan-boot04-hybrid-v1/CONSTRUCTION.json',
    'rowan-04-source00.png': B / 'rowan-boot04-hybrid-v1/inputs/authority/00.png',
    'rowan-04-front-owner.png': B / 'rowan-boot04-hybrid-v1/masks/00-boot1.png',
    'rowan-05-map.npz': B / 'rowan-05-path-v1/preview-v1/maps/05-projection.npz',
    'rowan-05-control.png': B / 'rowan-05-path-v1/inputs/control/05.png',
    'rowan-05-raw-map.npz': B / 'rowan-five-bridge-v1/maps/05-raw-source.npz',
    'rowan-05-raw.png': B / 'rowan-five-bridge-v1/generation/raw.png',
    'brann-se-04-map.npz': B / 'brann-full-lower-v1/se/maps/04.npz',
    'brann-se-05-map.npz': B / 'brann-full-lower-v1/se/maps/05.npz',
    'brann-se-04-recipe.json': B / 'brann-full-lower-v1/se/maps/04.json',
    'brann-se-05-recipe.json': B / 'brann-full-lower-v1/se/maps/05.json',
    'brann-se-source04.png': B / 'brann-full-lower-v1/registered/se/corrected-04.png',
    'brann-se-07-map.npz': B / 'brann-07-transition-v1/maps/07-newP-source00.npz',
    'brann-se-07-recipe.json': B / 'brann-07-transition-v1/RECIPE.json',
    'brann-se-07-source00.png': B / 'brann-07-transition-v1/inputs/control/00.png',
    'brann-ne-05-map.npz': B / 'brann-ne05-06-recovery-v1/maps/05.npz',
    'brann-ne-05-recipe.json': B / 'brann-ne05-06-recovery-v1/RECIPE.json',
    'brann-ne-06-map.npz': N / 'maps/source-map.npz',
    'brann-ne-06-recipe.json': N / 'recipe.json',
    'brann-ne-source07.png': B / 'brann-ne05-06-recovery-v1/inputs/control/07.png',
    'brann-ne-Q-owner.png': B / 'brann-ne05-06-recovery-v1/masks/Q-source07-complete-owner.png',
}
ledger = []
for name, source in items.items():
    if not source.is_file():
        print('MISSING', name, source)
        continue
    dest = R / 'inputs/guides' / name
    dest.parent.mkdir(exist_ok=True)
    assert not dest.exists()
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    shutil.copyfile(source, dest)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    assert hashlib.sha256(dest.read_bytes()).hexdigest() == before
    ledger.append({'original': str(source), 'retained': str(dest.relative_to(R)), 'sha256': before})
(R / 'GUIDE-INPUTS.json').write_text(json.dumps(ledger, indent=2) + '\n')
print('retained guides', len(ledger))
