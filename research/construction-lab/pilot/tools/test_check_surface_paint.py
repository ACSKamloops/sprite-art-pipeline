import math
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from check_surface_paint import check, expected, inside, local_point


class SurfaceCoordinates(unittest.TestCase):
    def test_inverse_mirrored_rotated_surface(self):
        frame={'origin':[10.5,20.5],'angle':math.pi/2,'uv_scale':[-1,1]}
        self.assertEqual(local_point([10,18],frame),(2.0,-1.2246467991473532e-16))

    def test_masks_and_material_are_independent(self):
        frame={'mask':{'include':[[[0,0],[4,0],[4,4],[0,4]]],
                       'exclude':[[[1,1],[2,1],[2,2],[1,2]]]}}
        strokes=[{'at':[0,0],'size':4,'color':'gold'}]; palette={'gold':'F8D795'}
        self.assertEqual(expected((.5,.5),frame,strokes,palette),(248,215,149,255))
        self.assertIsNone(expected((1.5,1.5),frame,strokes,palette))
        self.assertIsNone(expected((4.5,.5),frame,strokes,palette))
        self.assertFalse(inside((2,3),[[0,0],[4,0],[0,4]]))

    def test_last_stroke_wins_but_half_open_edge_does_not_bleed(self):
        frame={'mask':{'include':[[[0,0],[5,0],[5,5],[0,5]]],'exclude':[]}}
        strokes=[{'at':[0,0],'size':4,'color':'a'},{'at':[1,1],'size':1,'color':'b'}]
        self.assertEqual(expected((1.5,1.5),frame,strokes,{'a':'FFFFFF','b':'000000'}),(0,0,0,255))
        self.assertEqual(expected((2,1.5),frame,strokes,{'a':'FFFFFF','b':'000000'}),(255,255,255,255))


class ProofRejection(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.source=self.root/'source';self.source.mkdir()
        design={'palette':{'gold':'F8D795'},'paint_layers':{v:{'torso':[{'at':[0,0],'size':1,'color':'gold'}]} for v in ['right','left','front','back']}}
        (self.source/'design.json').write_text(json.dumps(design))
        (self.source/'clips.json').write_text(json.dumps({'clips':{'idle':{'loop':True}}}))
        for name in ['rig.gd','rig_side.gd']:(self.source/name).write_text('fixture source')
        bindings={name:hashlib.sha256((self.source/name).read_bytes()).hexdigest()for name in ['rig.gd','rig_side.gd','design.json','clips.json']}
        rows=[]
        for view in ['right','left','front','back']:
            prefix='idle-'+view;before=Image.new('RGBA',(192,192));before.putpixel((10,10),(10,10,10,255));after=before.copy();after.putpixel((10,10),(248,215,149,255))
            for suffix,image in [('before',before),('after',after),('surface-before',before),('surface-after',after)]:image.save(self.root/(prefix+'-'+suffix+'.png'))
            rows.append({'prefix':prefix,'clip':'idle','view':view,'phase':0,'before_sha256':hashlib.sha256(before.tobytes()).hexdigest(),'after_sha256':hashlib.sha256(after.tobytes()).hexdigest(),
                         'surface_changed_coordinates':[[10,10]],'visible_changed_coordinates':[[10,10]],
                         'surface_frame':{'origin':[10,10],'angle':0,'uv_scale':[1,1],'mask':{'include':[[[0,0],[2,0],[2,2],[0,2]]],'exclude':[]}}})
        self.report={'passed':True,'source_bindings':bindings,'samples':rows};self.path=self.root/'report.json'
    def run_check(self):
        self.path.write_text(json.dumps(self.report));return check(self.path,self.source/'design.json',1)
    def test_complete_fixture_then_omitted_direction_fails(self):
        self.assertTrue(self.run_check()['passed']);self.report['samples'].pop();self.assertFalse(self.run_check()['passed'])
    def test_duplicate_phase_fails(self):
        self.report['samples'].append(self.report['samples'][0]);self.assertFalse(self.run_check()['passed'])
    def test_wrong_color_or_forged_ledger_fails(self):
        p=self.root/'idle-right-surface-after.png';image=Image.open(p);image.putpixel((10,10),(255,0,0,255));image.save(p)
        self.assertFalse(self.run_check()['passed'])
    def test_changed_source_binding_rejected(self):
        (self.source/'rig_side.gd').write_text('new source')
        with self.assertRaisesRegex(ValueError,'Source differs'):self.run_check()


if __name__=='__main__':unittest.main()
