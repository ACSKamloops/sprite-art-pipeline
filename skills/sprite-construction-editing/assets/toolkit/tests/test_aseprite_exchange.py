"""Actual LibreSprite open/save/reopen/render, not just our own decoder."""
import copy,json,shutil,subprocess,tempfile,unittest,struct,zlib
from pathlib import Path
from PIL import Image
from sprite_lab import *
from sprite_lab.aseprite import _chunk
from test_core import fixture

TOOL=shutil.which('libresprite') or '/home/astra/.local/bin/libresprite'
class AseExchangeTests(unittest.TestCase):
    def test_sixty_hz_cycle_keeps_duration_in_ase_and_tool(self):
        p=fixture();p['frames']=p['frames'][:1];p['frames'][0]['duration_ticks']=1
        p['animations'][0].update(frames=[p['frames'][0]['id']]*72,fps=60,events=[])
        with tempfile.TemporaryDirectory()as td:
            td=Path(td);path=td/'cycle.aseprite';meta=export_aseprite(p,path)
            delays=[row['milliseconds']for row in meta['timing']]
            self.assertEqual(sum(delays),1200);self.assertEqual(set(delays),{16,17})
            self.assertTrue(all(abs(row['cumulative_boundary_error_ms'])<=.5 for row in meta['timing']))
            self.assertEqual(sum(f['milliseconds']for f in read_aseprite(path)['frames']),1200)
            self.assertEqual(import_aseprite(path),p)
            if Path(TOOL).is_file():
                data=td/'tool.json';saved=td/'tool-saved.aseprite'
                run=subprocess.run([TOOL,'-b',str(path),'--save-as',str(saved),'--data',str(data),'--format','json-array'],capture_output=True,text=True,timeout=30)
                self.assertEqual(run.returncode,0,run.stderr)
                self.assertEqual([r['duration']for r in json.loads(data.read_text())['frames']],delays)
                self.assertEqual(import_aseprite(saved,str(path)+'.sprite-lab.json'),p)
    def test_deterministic_sidecar_timing_and_edit_isolation(self):
        p=fixture()
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/'a.aseprite';b=Path(td)/'b.aseprite';m=export_aseprite(p,a);export_aseprite(p,b)
            self.assertEqual(a.read_bytes(),b.read_bytes());self.assertEqual(import_aseprite(a),p)
            self.assertEqual([r['milliseconds']for r in m['timing']],[50,83]);self.assertEqual(import_aseprite(a)['animations'],p['animations'])
            changed=copy.deepcopy(p);changed['palette'].append([13,157,241,177]);changed['cels']['b']['pixels'][6]=4;export_aseprite(changed,b)
            q=import_aseprite(b,str(a)+'.sprite-lab.json');self.assertEqual(render_frame(q,'f1').tobytes(),render_frame(p,'f1').tobytes());self.assertEqual(render_cel(q,q['frames'][0]['cels']['front']).getpixel((2,1)),(13,157,241,177));self.assertEqual(q['canvas'],p['canvas']);self.assertEqual(q['animations'],p['animations'])
            changed['frames'][0]['duration_ticks']=9;export_aseprite(changed,b)
            with self.assertRaises(EditError):import_aseprite(b,str(a)+'.sprite-lab.json')
    def test_linked_cropped_cel_uses_original_image_not_full_canvas(self):
        layer=_chunk(0x2004,struct.pack('<6HB3xH',3,0,0,4,3,0,255,1)+b'L')
        first=_chunk(0x2005,struct.pack('<HhhBHh5xHH',0,1,0,255,2,0,1,1)+zlib.compress(bytes([7,8,9,255])))
        second=_chunk(0x2005,struct.pack('<HhhBHh5xH',0,2,1,255,1,0,0))
        fs=[]
        for chunks in [[layer,first],[second]]:
            data=b''.join(chunks);fs.append(struct.pack('<IHHH2xI',16+len(data),0xf1fa,len(chunks),100,len(chunks))+data)
        data=b''.join(fs);head=bytearray(128);struct.pack_into('<IHHHHHIH',head,0,128+len(data),0xa5e0,2,4,3,32,1,100)
        with tempfile.TemporaryDirectory()as td:
            path=Path(td)/'linked.aseprite';path.write_bytes(head+data);read=read_aseprite(path);self.assertEqual(read['frames'][1]['cels'][0].getpixel((2,1)),(7,8,9,255));self.assertEqual(read['frames'][1]['cels'][0].getpixel((1,0)),(0,0,0,0))
    @unittest.skipUnless(Path(TOOL).is_file(),'LibreSprite unavailable; external-tool proof requires installed executable')
    def test_actual_libresprite_layered_open_save_reopen_render(self):
        p=fixture()
        with tempfile.TemporaryDirectory()as td:
            td=Path(td);source=td/'source.aseprite';saved=td/'saved.aseprite';export_aseprite(p,source)
            for input_path,name,save in [(source,'first',saved),(saved,'reopened',None)]:
                sheet=td/(name+'.png');data=td/(name+'.json');command=[TOOL,'-b','--list-layers',str(input_path)]
                if save:command+=['--save-as',str(save)]
                command+=['--sheet',str(sheet),'--sheet-type','horizontal','--data',str(data),'--format','json-array']
                result=subprocess.run(command,capture_output=True,text=True,timeout=30);self.assertEqual(result.returncode,0,result.stderr);self.assertTrue(sheet.is_file(),result.stdout+result.stderr)
                meta=json.loads(data.read_text());self.assertEqual([l['name']for l in meta['meta']['layers']],['Back','Front']);self.assertEqual([f['duration']for f in meta['frames']],[50,83]);image=Image.open(sheet).convert('RGBA')
                for i,frame in enumerate(p['frames']):self.assertEqual(image.crop((i*4,0,(i+1)*4,3)).tobytes(),render_frame(p,frame['id']).tobytes())
            self.assertEqual(import_aseprite(saved,str(source)+'.sprite-lab.json'),p)
