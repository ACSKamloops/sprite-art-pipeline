from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rgba(path):return np.array(Image.open(path).convert('RGBA'))
def mask(path):return np.array(Image.open(path).convert('L'))>0
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def verify_inputs():
    files=json.loads((ROOT/'INPUTS.json').read_text())['files']
    for f in files:assert sha(ROOT/f['path'])==f['sha256'],f['path']
    return len(files)
