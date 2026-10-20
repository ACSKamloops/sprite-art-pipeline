from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args()
assert a.output.is_absolute() and not a.output.exists(),'Absolute fresh output required'
recipe=json.loads((ROOT/'RECIPE.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for i in range(8):
 assert sha(ROOT/recipe['sources'][str(i)])==recipe['hashes'][str(i)]
 assert sha(ROOT/'frames'/f'{i:02}.png')==recipe['hashes'][str(i)]
a.output.mkdir(parents=True)
for i in range(8):
 out=a.output/f'{i:02}.png';shutil.copyfile(ROOT/recipe['sources'][str(i)],out)
 assert sha(out)==recipe['hashes'][str(i)]
(a.output/'REPLAY-RECEIPT.json').write_text(json.dumps({'frames':8,'source_and_output_PNG_bytes_exact':True,'recipe_sha256':sha(ROOT/'RECIPE.json'),'qualification':'Source composition only; no inherited art score or runtime acceptance'},indent=2)+'\n')
print('8/8 source composition PNGs exact')
