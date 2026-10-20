"""Fetch the creator's public CC0 upload and retain the exact selected source files."""
from pathlib import Path
import urllib.request,zipfile,hashlib,json,io
ROOT=Path(__file__).resolve().parent;out=ROOT/'source/original'
if out.exists():raise ValueError('Source snapshot already exists; refuse overwrite')
u='https://opengameart.org/sites/default/files/rpg_characters_-_nov_2020.zip';data=urllib.request.urlopen(u).read();z=zipfile.ZipFile(io.BytesIO(data));prefix='RPG Characters - Nov 2020/'
files=['Blends/Ranger.blend','Textures/Ranger_Texture.png','Textures/Ranger_Bow_Texture.png','License.txt'];out.mkdir(parents=True)
for name in files:
 p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(prefix+name))
r={'author':'Quaternius','official_page':'https://quaternius.com/packs/rpgcharacters.html','creator_upload_page':'https://opengameart.org/content/lowpoly-rpg-characters','download_url':u,'archive_sha256':hashlib.sha256(data).hexdigest(),'license':'CC0-1.0','source_files_sha256':{name:hashlib.sha256((out/name).read_bytes()).hexdigest()for name in files}};(ROOT/'source/provenance.json').write_text(json.dumps(r,indent=2)+'\n')
