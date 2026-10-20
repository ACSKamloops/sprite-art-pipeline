"""Independent small controls plus fresh-run reproducibility, not art approval."""
import unittest,tempfile,json,hashlib
from pathlib import Path
from PIL import Image
import compare
class RotationTests(unittest.TestCase):
 def test_scale2x_known_neighbour_rule(self):
  e=(10,20,30,255);r=(200,0,0,255);b=(0,0,200,255)
  im=Image.new('RGBA',(3,3),e);im.putpixel((1,0),r);im.putpixel((0,1),r);im.putpixel((2,1),b);im.putpixel((1,2),b)
  result=compare.scale2x(im)
  self.assertEqual([result.getpixel(p)for p in [(2,2),(3,2),(2,3),(3,3)]],[r,e,e,b])
  self.assertLessEqual(set(compare.pixels(result)),set(compare.pixels(im)))
 def test_positive90_fixed_pivot(self):
  im=Image.new('RGBA',(4,4));im.putpixel((3,1),(1,2,3,255))
  result=compare.rotate(im,90,(2,2));self.assertEqual(result.getpixel((1,0)),(1,2,3,255));self.assertEqual(sum(p[3]>0 for p in compare.pixels(result)),1)
 def test_fresh_runs_and_refuse_overwrite(self):
  with tempfile.TemporaryDirectory()as td:
   a=Path(td)/'a';b=Path(td)/'b';compare.run(a);compare.run(b)
   for p in a.iterdir():self.assertEqual(p.read_bytes(),(b/p.name).read_bytes(),p.name)
   digest=hashlib.sha256((a/'diagnostics.json').read_bytes()).hexdigest()
   with self.assertRaises(ValueError):compare.run(a)
   self.assertEqual(digest,hashlib.sha256((a/'diagnostics.json').read_bytes()).hexdigest())
 def test_actual_part_zero_identity(self):
  im=Image.open(compare.ROOT/'source/right_shin.png').convert('RGBA')
  for method in ['nearest','scale2x8-approximation']:self.assertEqual(compare.render(im,method,0).tobytes(),im.tobytes())
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(RotationTests);result=unittest.TextTestRunner(verbosity=2).run(suite)
 report={'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'source_sha256':hashlib.sha256((compare.ROOT/'source/right_shin.png').read_bytes()).hexdigest(),'implementation_sha256':hashlib.sha256((compare.ROOT/'compare.py').read_bytes()).hexdigest(),'scope':'Known local Scale2x equations, fixedpivot/angle control, wholefreshoutput byte repeatability, atomic existing-output rejection and actualzeroidentity.'}
 (compare.ROOT/'test-report.json').write_text(json.dumps(report,indent=2)+'\n')
 if not result.wasSuccessful():raise SystemExit(2)
