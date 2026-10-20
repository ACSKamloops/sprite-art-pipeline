"""Mount shipped PCK read-only and byte-compare four specific extracted members.
Never launches the packaged app or reads its project/auth settings.
"""
import hashlib,json,os,subprocess,tempfile
from pathlib import Path
R=Path('/home/astra/projects/pixellab-local-test-20261011')
OUT=Path(__file__).resolve().parents[2]/'docs/recovery-round3-20261014'
PCK=R/'evidence/pixelorama_pixellab.pck'
assert hashlib.sha256(PCK.read_bytes()).hexdigest()=='ebf9812ea474bddb84faa22183a1ec0178983cdc285674a4d0177c606e8a4a3f'
paths=['src/Classes/FloodFillObject.gdc','src/Autoload/DrawingAlgos.gdc','src/Shaders/ColorSelect.gdshader','src/Shaders/ColorReplace.gdshader']
script='''extends SceneTree
func _init():
    assert(ProjectSettings.load_resource_pack(__PACK__))
    for relative in __FILES__:
        var packed=FileAccess.get_file_as_bytes("res://"+relative)
        var extracted=FileAccess.get_file_as_bytes(__EXTRACTED__+"/"+relative)
        assert(packed.size()>0 and packed==extracted)
        print("MEMBER "+JSON.stringify({"relative":relative,"bytes":packed.size(),"sha256":packed.hex_encode().sha256_text()}))
    print("MEMBERS_PASS")
    quit(0)
'''.replace('__PACK__',json.dumps(str(PCK))).replace('__FILES__',json.dumps(paths)).replace('__EXTRACTED__',json.dumps(str(R/'pixelorama-extracted')))
# Godot summary's sha hashes hex text; authoritative binary hash is computed below.
with tempfile.TemporaryDirectory(prefix='pck-member-oracle-',dir=OUT)as tmp:
 t=Path(tmp);(t/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Read-only PCK member proof"\n');(t/'member_oracle.gd').write_text(script)
 env={k:v for k,v in os.environ.items()if k in ['PATH','HOME','LANG']};env['XDG_DATA_HOME']=str(t/'userdata')
 p=subprocess.run(['/home/astra/.local/bin/godot','--headless','--quit-after','3','--path',tmp,'--script','res://member_oracle.gd'],env=env,text=True,capture_output=True,timeout=30)
 if p.returncode or 'MEMBERS_PASS'not in p.stdout:print(p.stdout,p.stderr);raise SystemExit(1)
 members=[]
 for line in p.stdout.splitlines():
  if line.startswith('MEMBER '):
   j=json.loads(line[7:]);raw=(R/'pixelorama-extracted'/j['relative']).read_bytes();members.append(dict(path=j['relative'],bytes=j['bytes'],binary_sha256=hashlib.sha256(raw).hexdigest(),pck_equals_extracted_bytes=True))
 result=dict(classification='original-pck-member-byte-membership-not-decompilation-equivalence',pck=str(PCK),pck_sha256=hashlib.sha256(PCK.read_bytes()).hexdigest(),members=members,engine=p.stdout.splitlines()[0],stderr=p.stderr,boundary='Only mounts pack and reads four allowlisted files. No packaged app scene,autoload/project settings or credential code launched/read.')
 (OUT/'PCK-MEMBER-PROOF.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
