"""Actual LibreSprite open/save, reopen/render and sidecar reimport."""
import argparse,json,shutil,subprocess
from pathlib import Path
from PIL import Image
from common import ROOT,rgba,sha,write,verify_inputs
from sprite_lab import import_aseprite,read_aseprite,project_hash,load_json,canonical_json
from sprite_lab.core import render_frames

def main(binary):
    verify_inputs();tool=Path(binary or shutil.which('libresprite')or'')
    assert tool.is_file(),'LibreSprite binary required'
    final=load_json((ROOT/'projects/final.json').read_text())
    sidecar=ROOT/'exchange/rowan-ne-final.aseprite.sprite-lab.json'
    commands=[]
    for src,stem in [('rowan-ne-final.aseprite','tool-saved'),('tool-saved.aseprite','tool-reopened')]:
        dest=ROOT/f'exchange/{stem}.aseprite';assert not dest.exists()
        cmd=[str(tool),'-b','--list-layers',str(ROOT/'exchange'/src),'--save-as',str(dest),'--sheet',str(ROOT/f'exchange/{stem}-sheet.png'),'--sheet-type','horizontal','--data',str(ROOT/f'exchange/{stem}.json'),'--format','json-array']
        result=subprocess.run(cmd,text=True,capture_output=True)
        (ROOT/f'exchange/{stem}.log').write_text(result.stdout+result.stderr)
        assert result.returncode==0 and dest.is_file()and(ROOT/f'exchange/{stem}-sheet.png').is_file()
        commands.append({'argv':cmd,'returncode':result.returncode,'log':f'exchange/{stem}.log'})
    rows=[];imports=[]
    for stem in ['tool-saved','tool-reopened']:
        saved=ROOT/f'exchange/{stem}.aseprite';parsed=read_aseprite(saved)
        assert len(parsed['layers'])==1 and len(parsed['frames'])==8
        sheet=Image.open(ROOT/f'exchange/{stem}-sheet.png').convert('RGBA');assert sheet.size==(1024,128)
        imported=import_aseprite(saved,sidecar=sidecar);assert project_hash(imported)==project_hash(final)
        (ROOT/f'exchange/{stem}-reimported-project.json').write_text(canonical_json(imported)+'\n')
        canonical=ROOT/f'exchange/{stem}-canonical-png';canonical.mkdir()
        for i,image in enumerate(render_frames(imported,[f'{i:02}'for i in range(8)])):
            expected=ROOT/f'inputs/expected-final/{i:02}.png';actual=sheet.crop((i*128,0,(i+1)*128,128))
            assert parsed['frames'][i]['cels'][0].tobytes()==rgba(expected).tobytes()
            assert actual.tobytes()==rgba(expected).tobytes()==image.tobytes()
            actual.save(canonical/f'{i:02}.png');assert (canonical/f'{i:02}.png').read_bytes()==expected.read_bytes()
            rows.append({'pass':stem,'phase':i,'saved_cel_RGBA_exact':True,'actual_tool_render_RGBA_exact':True,'reimported_project_RGBA_exact':True,'canonical_reencoded_PNG_bytes_exact':True,'source_PNG_sha256':sha(expected),'quantized_ms':parsed['frames'][i]['milliseconds']})
        imports.append({'pass':stem,'ASE_sha256':sha(saved),'project_sha256':project_hash(imported)})
    assert sum(f['milliseconds']for f in parsed['frames'])==450
    r={'status':'PASS actual LibreSprite save/reopen/render/reimport, all8 final cels exact','commands':commands,'tool_path':str(tool),'tool_resolved_path':str(tool.resolve()),'tool_binary_sha256':sha(tool.resolve()),'whole_project_reimport_exact':True,'native_round_trips':imports,'all8_twice':rows,'one_flat_layer':True,'upstream_source_parts_separate':True,'rational_clock_sidecar':'exchange/RATIONAL-CLOCK.json','native_duration_total_ms':450,'native_ms_quantization':'56/57ms holds preserve .45 total; original9/160 sidecar authoritative','PNG_encoding_note':'Raw tool sheets retain the tool PNG encoding. Each cropped RGBA render is separately encoded with the same canonical PNG writer and matches frozen final PNG bytes; native sheet encoding is not claimed identical to individual source PNGs.','new_art_changes':0,'model_calls':0,'canonical_writes':0,'normal_speed_acceptance':False}
    write(ROOT/'verification/NATIVE-RECEIPT.json',r)
    print(json.dumps({k:v for k,v in r.items()if k not in ['commands','all8_twice']}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--libresprite');a=ap.parse_args();main(a.libresprite)
