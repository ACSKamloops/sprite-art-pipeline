import copy,json,tempfile,unittest,zipfile,io
from pathlib import Path
from PIL import Image
from sprite_lab import *

def fixture():
    return {'schema':'sprite-edit-project/v1','canvas':{'width':4,'height':3,'render_pivot':[2,1],'ground_pivot':[2,3]},'palette':[[0,0,0,0],[255,0,0,255],[0,0,255,255],[0,255,0,128]],'layers':[{'id':'back','name':'Back','locked':False},{'id':'front','name':'Front','locked':False}],'cels':{'a':{'layer_id':'back','pixels':[0,1,0,0,0,1,1,0,0,0,0,0]},'b':{'layer_id':'front','pixels':[0,0,0,0,0,2,0,0,0,0,0,0]},'c':{'layer_id':'back','pixels':[0,0,0,0,0,1,0,0,0,0,0,0]}},'frames':[{'id':'f0','duration_ticks':3,'cels':{'back':'a','front':'b'},'landmarks':{'hand':[1,1]}},{'id':'f1','duration_ticks':5,'cels':{'back':'c'},'landmarks':{}}],'animations':[{'id':'walk','frames':['f0','f1'],'fps':60.098811862348406,'loop':True,'events':[{'at_tick':3,'name':'footfall'}]}],'provenance':{'source_sha256':'readonlyfixture'}}
def tx(p,*ops):return {'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(p),'reason':'Precise test','operations':list(ops)}
class CoreTests(unittest.TestCase):
    def test_overlap_and_missing_cel(self):
        p=fixture();self.assertEqual(render_frame(p,'f0').getpixel((1,1)),(0,0,255,255));self.assertEqual(render_frame(p,'f1').getpixel((1,1)),(255,0,0,255))
    def test_partial_alpha_exact(self):
        p=fixture();p['cels']['b']['pixels'][5]=3;self.assertEqual(render_frame(p,'f0').getpixel((1,1)),(127,128,0,255));p['palette'][1][3]=128;self.assertEqual(render_frame(p,'f0').getpixel((1,1)),(85,170,0,192))
    def test_local_edit_preserves_everything_else(self):
        p=fixture();result=apply_transaction(p,tx(p,{'op':'paint','cel_id':'b','points':[[2,1,2]]}));q=result['project'];self.assertEqual(result['receipt']['diff']['frames']['f0']['coordinates'],[[2,1]]);self.assertEqual(render_frame(q,'f1').tobytes(),render_frame(p,'f1').tobytes());self.assertEqual(p['canvas'],q['canvas']);self.assertEqual(p['animations'],q['animations']);self.assertEqual(p['frames'],q['frames']);self.assertEqual(p['provenance'],q['provenance']);self.assertEqual(p,fixture())
    def test_invalid_transaction_atomic_after_valid_prefix(self):
        p=fixture();baseline=canonical_json(p)
        invalid=[{'op':'paint','cel_id':'b','points':[[7,1,2]]},{'op':'paint','cel_id':'b','points':[[1,1,True]]},{'op':'erase','cel_id':'b','points':[[1,1]],'extra':1},{'op':'translate','cel_id':'b','dx':20,'dy':0},{'op':'palette','index':0,'rgba':[1,2,3,4]},{'op':'wat'},{'op':'paint','cel_id':[],'points':[]}]
        for op in invalid:
            with self.subTest(op=op):
                with self.assertRaises(EditError):apply_transaction(p,tx(p,{'op':'paint','cel_id':'b','points':[[2,1,2]]},op))
                self.assertEqual(canonical_json(p),baseline)
    def test_stale_and_locked(self):
        p=fixture();t=tx(p,{'op':'erase','cel_id':'b','points':[[1,1]]});t['expected_project_sha256']='0'*64
        with self.assertRaises(EditError):apply_transaction(p,t)
        p['layers'][1]['locked']=True
        for op in [{'op':'erase','cel_id':'b','points':[[1,1]]},{'op':'palette','index':2,'rgba':[4,5,6,255]}]:
            with self.assertRaises(EditError):apply_transaction(p,tx(p,op))
    def test_masked_recolor_and_erase(self):
        p=fixture();r=apply_transaction(p,tx(p,{'op':'replace_color','cel_id':'a','from_index':1,'to_index':2,'mask':[[1,0]]},{'op':'erase','cel_id':'a','points':[[2,1]]}));self.assertEqual(r['receipt']['diff']['cels']['a']['coordinates'],[[1,0],[2,1]]);self.assertEqual(r['project']['cels']['a']['pixels'][5],1)
    def test_translate_preserves_source_and_clipping(self):
        p=fixture();q=apply_transaction(p,tx(p,{'op':'translate','cel_id':'b','dx':1,'dy':1}))['project'];self.assertEqual(q['cels']['b']['pixels'][10],2);self.assertEqual(sum(q['cels']['b']['pixels']),2);self.assertEqual(p,fixture())
        q=apply_transaction(p,tx(p,{'op':'translate','cel_id':'b','dx':9,'dy':0,'allow_clip':True}))['project'];self.assertEqual(sum(q['cels']['b']['pixels']),0)
    def test_layer_translation_shared_cel_once(self):
        p=fixture();p['frames'][1]['cels']['front']='b';q=apply_transaction(p,tx(p,{'op':'translate_layer','layer_id':'front','dx':1,'dy':0}))['project'];self.assertEqual(q['cels']['b']['pixels'][6],2);self.assertEqual(q['cels']['b']['pixels'][7],0)
    def test_candidate_localization_and_stale(self):
        p=fixture();pixels=list(p['cels']['b']['pixels']);pixels[6]=1;op={'op':'candidate_patch','cel_id':'b','mask':[[2,1]],'candidate_pixels':pixels,'expected_cel_sha256':cel_hash(p,'b')};q=apply_transaction(p,tx(p,op));self.assertEqual(q['receipt']['diff']['cels']['b']['coordinates'],[[2,1]]);op['candidate_pixels'][0]=1
        with self.assertRaises(EditError):apply_transaction(p,tx(p,op))
        op['candidate_pixels'][0]=0;op['expected_cel_sha256']='bad'
        with self.assertRaises(EditError):apply_transaction(p,tx(p,op))
    def test_rgba_candidate_new_color_and_outside_rejection(self):
        p=fixture();im=render_cel(p,'b');im.putpixel((2,1),(13,157,241,177));t=candidate_transaction(p,'b',im,[[2,1]]);q=apply_transaction(p,t)['project'];self.assertEqual(render_cel(q,'b').getpixel((2,1)),(13,157,241,177));self.assertEqual(q['palette'][-1],[13,157,241,177]);im.putpixel((0,0),(1,2,3,255))
        with self.assertRaises(EditError):candidate_transaction(p,'b',im,[[2,1]])
    def test_history_undo_redo_replay_cursor(self):
        p=fixture();h=History(p);h.apply(tx(h.project,{'op':'erase','cel_id':'b','points':[[1,1]]}));edited=project_hash(h.project);h.undo();self.assertEqual(project_hash(h.project),project_hash(p));journal=h.journal();replayed=History.replay(p,journal);self.assertEqual(project_hash(replayed.project),project_hash(p));replayed.redo();self.assertEqual(project_hash(replayed.project),edited);replayed.undo();replayed.apply(tx(replayed.project,{'op':'paint','cel_id':'b','points':[[3,2,1]]}));self.assertEqual(len(replayed.records),1)
    def test_tampered_receipt_rejected(self):
        p=fixture();h=History(p);h.apply(tx(p,{'op':'erase','cel_id':'b','points':[[1,1]]}));j=h.journal();j['receipts'][0]['after_sha256']='bad'
        with self.assertRaises(EditError):History.replay(p,j)
    def test_explicit_metadata_edit(self):
        p=fixture();q=apply_transaction(p,tx(p,{'op':'frame_timing','frame_id':'f1','duration_ticks':8},{'op':'pivots','render_pivot':[2,-3],'ground_pivot':[2,9]}))['project'];self.assertEqual(q['cels'],p['cels']);self.assertEqual(q['frames'][1]['duration_ticks'],8)
    def test_export_determinism(self):
        p=fixture()
        with tempfile.TemporaryDirectory()as temp:
            a=Path(temp)/'a';b=Path(temp)/'b';export_project(p,a,1);export_project(p,b,1)
            self.assertEqual({x.name:x.read_bytes()for x in a.iterdir()},{x.name:x.read_bytes()for x in b.iterdir()});atlas=Image.open(a/'atlas.png');self.assertEqual(atlas.crop((0,3,4,6)).tobytes(),render_frame(p,'f1').tobytes());self.assertEqual(json.loads((a/'manifest.json').read_text())['animations'],p['animations'])
    def test_ora_lossless_reopen_and_external_pixel_edit(self):
        p=fixture();p['frames'][1]['cels']['front']='b'
        with tempfile.TemporaryDirectory()as temp:
            path=Path(temp)/'a.ora';other=Path(temp)/'b.ora';export_ora(p,'f0',path);export_ora(p,'f0',other);self.assertEqual(path.read_bytes(),other.read_bytes());self.assertEqual(import_ora(path),p)
            with zipfile.ZipFile(path)as archive:entries={n:archive.read(n)for n in archive.namelist()}
            im=Image.open(io.BytesIO(entries['data/layer-0001.png'])).convert('RGBA');im.putpixel((2,1),(11,22,33,123));entries['data/layer-0001.png']=png_bytes(im)
            with zipfile.ZipFile(other,'w')as archive:
                for n,payload in entries.items():archive.writestr(n,payload)
            q=import_ora(other);self.assertEqual(render_frame(q,'f1').tobytes(),render_frame(p,'f1').tobytes());self.assertEqual(render_cel(q,q['frames'][0]['cels']['front']).getpixel((2,1)),(11,22,33,123));self.assertEqual(q['animations'],p['animations']);self.assertEqual(q['canvas'],p['canvas'])
    def test_canonical_js_numbers_and_unicode(self):
        self.assertEqual(canonical_json({'z':1.0,'tiny':1e-7,'zero':-0.0,'fixed':1e-6,'large':1e21}),'{"fixed":0.000001,"large":1e+21,"tiny":1e-7,"z":1,"zero":0}');self.assertEqual(canonical_json({'\ue000':1,'😀':2}),'{"😀":2,"":1}')
        for v in [float('nan'),float('inf'),9007199254740992]:
            with self.assertRaises(ValueError):canonical_json(v)
if __name__=='__main__':unittest.main()
