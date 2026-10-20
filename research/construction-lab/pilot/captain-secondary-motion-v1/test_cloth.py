import copy,json,sys,unittest
from pathlib import Path
import numpy as np
from PIL import Image
from cloth import render,sample_parent
P=Path(__file__).resolve().parent;R=P.parent
class ClothContract(unittest.TestCase):
 def setUp(self):
  self.packet=json.loads((R/'captain-depth-projected-art-v1/source/authored-poses-final.json').read_text());self.cfg=json.loads((R/'captain-upright-rig-v1/design.json').read_text());self.source=Image.open(R/'captain-depth-projected-art-v1/artifacts/trial-v3-volume/upper-parts/complete/cape.png').convert('RGBA')
 def test_stationary_parent_keeps_entire_source_RGBA(self):
  p=copy.deepcopy(self.packet);chest=self.cfg['chest_hinge'];pelvis=self.cfg['pelvis_rest'];p['neutral_bind']['upper_pixels'].update(chest=chest,pelvis=pelvis)
  p['dimensions']['stride_world']=[0,0,0]
  for f in p['frames']:f['upper_pixels'].update(chest=chest,pelvis=pelvis);f['physical_root_pixels']=[0,0];f['chest_counterrotation_degrees']=0
  for i in [0,18,36,54,71]:self.assertEqual(render(self.source,p,i,self.cfg)[0].tobytes(),self.source.tobytes())
 def test_world_wrap_is_translated_not_a_snap(self):
  stride=np.array(self.packet['camera']['matrix_2x3'])@np.array(self.packet['dimensions']['stride_world'])
  for phase in [-.1,0,.24,.99]:
   a,ra=sample_parent(self.packet,phase,self.cfg,'chest');b,rb=sample_parent(self.packet,phase+1,self.cfg,'chest');np.testing.assert_allclose(b-a,stride,atol=1e-12);self.assertAlmostEqual(ra,rb)
 def test_dynamic_lag_uses_only_source_material(self):
  palette=set(map(tuple,np.array(self.source).reshape(-1,4)));changes=[]
  for i in range(72):
   image,rec=render(self.source,self.packet,i,self.cfg);self.assertTrue(set(map(tuple,np.array(image).reshape(-1,4)))<=palette|{(0,0,0,0)});changes.append(rec['max_world_hem_offset'])
  self.assertGreater(min(changes),0);self.assertLess(max(changes),8)
if __name__=='__main__':unittest.main()
