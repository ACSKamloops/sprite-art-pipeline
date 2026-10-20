import copy,json,tempfile,unittest
from pathlib import Path
from PIL import Image
from qc.pixel_motion.check import check,composite,material_check,sole

def fixture():
    p={'schema':'sprite-edit-project/v1','canvas':{'width':5,'height':5,'render_pivot':[2,2],'ground_pivot':[2,4]},'palette':[[0,0,0,0],[10,80,180,255]],'layers':[{'id':'foot','name':'Foot','locked':False}],'cels':{},'frames':[],'animations':[{'id':'walk','frames':['a','b'],'fps':60,'loop':False,'events':[]}]}
    for name,x in [('a',2),('b',1)]:
        pixels=[0]*25;pixels[3*5+x]=1;p['cels'][name]={'layer_id':'foot','pixels':pixels};p['frames'].append({'id':name,'duration_ticks':1,'cels':{'foot':name},'landmarks':{'ankle':[x,3]}})
    ann={'schema':'sprite-pixel-motion-annotations/v1','canvas':copy.deepcopy(p['canvas']),'layer_order':['foot'],'alpha_threshold':128,'edge_margin':1,'frames':{f['id']:{'landmarks':f['landmarks'],'duration_ticks':1,'layers':{}}for f in p['frames']},'actions':[{'id':'walk','root_speed_px_s':60,'world_motion':'stepped','contacts':[{'layer':'foot','stance_frames':['a','b'],'ground_row':3,'max_ground_error_px':0,'max_boundary_slip_px':0,'max_hold_slip_px':.5}]}]}
    return p,ann
class QcTests(unittest.TestCase):
    def codes(self,p,a):return {x['code']for x in check(p,a,'.',reference=False)[0]['issues']}
    def test_stepped_world_rule_satisfied_without_art_approval(self):
        p,a=fixture();r,_=check(p,a,'.',reference=False);self.assertEqual(r['issues'],[]);self.assertFalse(r['art_quality_approved'])
    def test_hold_sliding_and_fractional_rate_measurement(self):
        p,a=fixture();a['actions'][0]['world_motion']='continuous';p['animations'][0]['fps']=59.94;r,_=check(p,a,'.',reference=False);self.assertIn('HELD_FRAME_WORLD_SLIDING',{i['code']for i in r['issues']});s=next(s for s in r['actions'][0]['fractional_tick_samples']if s['tick']==.5);self.assertAlmostEqual(s['root_world_x'],60*.5/59.94);self.assertEqual(r['actions'][0]['fps'],59.94)
    def test_loop_wrap_is_checked_when_same_stance_continues(self):
        p,a=fixture();p['animations'][0]['loop']=True;r,_=check(p,a,'.',reference=False);wrap=[x for x in r['issues']if x['code']=='STANCE_BOUNDARY_WORLD_SLIDING'];self.assertTrue(any(i['loop_wrap']for i in wrap));self.assertTrue(any(s['tick']==2 for s in r['actions'][0]['fractional_tick_samples']))
    def test_pixel_sole_elevation_and_anchor_independent(self):
        p,a=fixture();p['cels']['a']['pixels'][17]=0;p['cels']['a']['pixels'][12]=1;self.assertIn('STANCE_GROUND_CONTACT',self.codes(p,a));p,a=fixture();p['canvas']['ground_pivot'][1]=3;self.assertIn('ANCHOR_OR_CANVAS_CHANGED',self.codes(p,a))
    def test_missing_clipped_foot_is_unknown_not_crash_or_pass(self):
        p,a=fixture();p['cels']['a']['pixels']=[0]*25;r,_=check(p,a,'.',reference=False);self.assertIn('FOOT_ALPHA_MISSING',{x['code']for x in r['issues']});self.assertTrue(any(s.get('measurement')for s in r['actions'][0]['fractional_tick_samples']))
    def test_annotated_sole_roi_disambiguates_same_layer(self):
        p,a=fixture();p['cels']['a']['pixels'][19]=1;self.assertEqual(sole(composite(p,p['frames'][0])[0])['center_x'],3);self.assertEqual(sole(composite(p,p['frames'][0])[0],roi=[1,2,3,4])['center_x'],2)
    def test_malformed_clocks_reject(self):
        for value in [0,float('nan'),float('inf'),True]:
            p,a=fixture();p['animations'][0]['fps']=value
            with self.assertRaises(ValueError):check(p,a,'.',reference=False)
    def test_independent_partial_alpha_and_layer_order(self):
        p,a=fixture();p['palette']=[[0,0,0,0],[255,0,0,255],[0,255,0,128]];p['layers'].append({'id':'top'});p['cels']['top']={'layer_id':'top','pixels':[2 if i==17 else 0 for i in range(25)]};p['frames'][0]['cels']['top']='top';im,_=composite(p,p['frames'][0]);self.assertEqual(im.getpixel((2,3)),(127,128,0,255))
    def test_material_annotation_local_only(self):
        with tempfile.TemporaryDirectory()as td:
            a=Path(td)/'a.png';b=Path(td)/'b.png';Image.new('RGBA',(2,2),(1,50,200,255)).save(a);Image.new('RGBA',(2,2),(240,20,80,255)).save(b);r=material_check(a,b,{'samples':[{'xy':[1,1],'criterion':'blue_exceeds_red','label':'reviewed cloth'}]});self.assertEqual(len(r['violations']),1);self.assertFalse(r['art_quality_approved'])
if __name__=='__main__':unittest.main()
