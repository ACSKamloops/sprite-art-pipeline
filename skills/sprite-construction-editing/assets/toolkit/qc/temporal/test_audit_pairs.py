import unittest
import numpy as np
from audit_pairs import metric,motion_contract
class AdversarialChecks(unittest.TestCase):
 def setUp(self):
  self.palette={'ink':'152C37','copper':'B96D43'}
  self.a=np.zeros((192,192,4),dtype=np.uint8);self.a[70:100,70:100]=[185,109,67,255]
  self.pose={'landmarks':{'hand':[90,90]},'grip':[90,90],'hands':{'front':[90,90]}}
 def compare(self,b,pose=None):return metric(self.a,b,self.pose,pose or self.pose,self.palette)
 def test_planar_root_contract_is_preserved_without_reinterpretation(self):
  p={'view':'front','world_root':[0,4.0],'contact_basis':'planar_xy','ground_projection':{'type':'facing_depth_plane','scope':'Per-boot reference'},'world_motion_status':'raster audit pending'}
  self.assertEqual(motion_contract(p),p)
 def test_contract_does_not_invent_world_ground_or_acceptance(self):
  self.assertEqual(motion_contract({'view':'right','landmarks':{}}),{'view':'right'})
 def test_unmodified_is_exact(self):
  m=self.compare(self.a.copy());self.assertEqual(m['visible_changed_pixels'],0);self.assertEqual(m['flags'],[])
 def test_one_pixel_texture_mutation_is_visible(self):
  b=self.a.copy();b[80,80]=[255,0,255,255];m=self.compare(b);self.assertEqual(m['visible_changed_pixels'],1);self.assertIn('off_palette_color',m['flags'])
 def test_moved_pivot_no_recentering(self):
  b=np.roll(self.a,1,axis=1);m=self.compare(b);self.assertEqual(m['visible_changed_pixels'],60);self.assertLess(m['silhouette_iou'],1)
 def test_wrong_grip_contract(self):
  p={**self.pose,'grip':[96,90]};self.assertIn('grip_target_separation',self.compare(self.a,p)['flags'])
 def test_material_loss_requires_review(self):
  b=self.a.copy();b[70:85,70:100]=[21,44,55,255];m=self.compare(b);self.assertIn('material_area_step_review:copper',m['flags']);self.assertEqual(m['alpha_added'],0)
 def test_flip_asymmetry_is_measured(self):
  self.a[90:98,100:120]=[185,109,67,255];m=self.compare(self.a[:,::-1].copy());self.assertGreater(m['visible_changed_pixels'],0)
 def test_joint_teleport_requires_review(self):
  p={**self.pose,'landmarks':{'hand':[105,90]}};self.assertIn('large_landmark_step_review',self.compare(self.a,p)['flags'])
 def test_transparent_rgb_is_not_visible_change(self):
  b=self.a.copy();b[0,0,:3]=[1,2,3];self.assertEqual(self.compare(b)['visible_changed_pixels'],0)
if __name__=='__main__':unittest.main()
