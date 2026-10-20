import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import surface_paint as paint
class Paint(unittest.TestCase):
 def setUp(self):
  self.raw=(Path(__file__).resolve().parents[1]/'rigged-character/design.json').read_bytes()
  self.patch={'schema':'rig-surface-paint/v1','expected_source_sha256':paint.sha(self.raw),'reason':'Reusable coat stitch candidate','strokes':[{'view':'right','layer':'torso','at':[0,-6],'color':'teal_light','size':1}]}
 def test_exact_undo_and_unchanged_other_source(self):
  new,r=paint.apply(self.raw,self.patch);self.assertEqual(paint.undo(new,r),self.raw)
  d=json.loads(new);d.pop('paint_layers');self.assertEqual(d,json.loads(self.raw))
 def test_rejects_wrong_shapes_views_palette_and_fabric(self):
  for key,value in [('at',[float('nan'),0]),('size',True),('view','front'),('layer','front_arm'),('color','unknown')]:
   p=copy.deepcopy(self.patch);p['strokes'][0][key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):paint.apply(self.raw,p)
 def test_stale_replay_and_tampered_undo(self):
  new,r=paint.apply(self.raw,self.patch)
  with self.assertRaises(ValueError):paint.apply(new,self.patch)
  with self.assertRaises(ValueError):paint.undo(new+b' ',r)
  r['patch']['strokes'][0]['at']=[3,4]
  with self.assertRaises(ValueError):paint.undo(new,r)
if __name__=='__main__':unittest.main()
