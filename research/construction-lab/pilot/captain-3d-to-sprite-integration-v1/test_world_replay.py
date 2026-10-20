import importlib.util, json, shutil, tempfile, unittest
from pathlib import Path
import numpy as np

P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('world_replay',P/'world_replay.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
INPUT=Path('/home/astra/projects/captain-3d-rig-lab/render/body-semantic-v1/render-contract.json')
JOINTS=Path('/home/astra/projects/captain-3d-rig-lab/rig/body-v1/retarget-joints.json')

class WorldReplayChecks(unittest.TestCase):
    def setUp(self): self.r=m.Replay(INPUT,JOINTS)

    def test_exact_cycle_root_not_reset(self):
        for mode,rate in [('synchronized',60),('continuous',120)]:
            i,root,screen,fraction,cycle=self.r.state(65*(rate//60),mode)
            self.assertEqual((i,fraction,cycle),(0,0,1))
            np.testing.assert_allclose(root,self.r.stride,atol=1e-12)
            np.testing.assert_allclose(screen,self.r.vector(self.r.stride),atol=1e-12)

    def test_continuous_root_moves_within_held_cel(self):
        a=self.r.state(0,'continuous');b=self.r.state(1,'continuous')
        self.assertEqual(a[0],b[0]);self.assertGreater(np.linalg.norm(a[2]-b[2]),0)
        np.testing.assert_allclose(b[1],self.r.roots[1]*.5,atol=1e-12)

    def test_rotation_axes_round_trip_and_y_sign(self):
        right=self.r.camera[:3,0];up=self.r.camera[:3,1]
        np.testing.assert_allclose(self.r.vector(right),[self.r.scale,0],atol=2e-5)
        np.testing.assert_allclose(self.r.vector(up),[0,-self.r.scale],atol=2e-5)

    def test_matches_independent_blender_witness(self):
        witness=json.loads((P/'projection-witness.json').read_text())
        for item in witness:
            np.testing.assert_allclose(self.r.ground(item['world']),item['pixel'],atol=3e-5)

    def test_changed_camera_timing_or_root_is_rejected(self):
        # New contracts live alongside source images; no copied pixels or edits.
        mutations=[lambda d:d['camera_fixed_matrix'][0].__setitem__(0,2),lambda d:d['frames'][1].__setitem__('duration_seconds',.017),lambda d:d['frames'][1]['visual_root_compensation'].__setitem__(2,1)]
        for change in mutations:
            d=json.loads(INPUT.read_text());change(d)
            # Keep tests read-only on worker repo. Copy source pixels exactly.
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'contract.json'
                for f in d['frames']:
                    shutil.copy2(INPUT.parent/f['file'],Path(tmp)/f['file'])
                path.write_text(json.dumps(d))
                # Prove the corresponding contract guard, not an unrelated path error.
                expected='proper orthonormal' if change is mutations[0] else ('altered timing' if change is mutations[1] else 'horizontal-only')
                with self.assertRaisesRegex(ValueError,expected):m.Replay(path,JOINTS)

    def test_actual_integrated_native_cameras(self):
        root=Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/full-captain-source-hinge-v4')
        joints=Path('/home/astra/projects/captain-3d-rig-lab/rig/contact-source-hinge-v1/retarget-joints-actual.json')
        witness=json.loads((P/'projection-integrated-witness.json').read_text())
        for item in witness['witnesses']:
            size=item['resolution']; r=m.Replay(root/f'native{size}/integration-contract.json',joints)
            self.assertEqual(r.images[0].size,(size,size))
            for point in item['points']:
                np.testing.assert_allclose(r.ground(point['world']),point['actual_blender_pixel'],atol=.001,rtol=0)

    def test_integrated_wrong_controller_or_source_clock_rejected(self):
        source=Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/full-captain-source-hinge-v4/native256/integration-contract.json')
        joints=Path('/home/astra/projects/captain-3d-rig-lab/rig/contact-source-hinge-v1/retarget-joints-actual.json')
        changes=[(lambda d:d.__setitem__('root_controller_baked',False),'baked horizontal-only'),(lambda d:d['timeline'].__setitem__('sample_step',3),'source clock'),(lambda d:d['frames'][3].__setitem__('hold_seconds',.017),'altered timing')]
        for change,reason in changes:
            d=json.loads(source.read_text());change(d)
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'contract.json'
                for frame in d['frames']:shutil.copy2(source.parent/frame['file'],Path(tmp)/frame['file'])
                path.write_text(json.dumps(d))
                with self.assertRaisesRegex(ValueError,reason):m.Replay(path,joints)

    def test_native384_actual_three_loop_2x_bounds(self):
        source=Path('/home/astra/projects/captain-3d-reference-paint-lab/artifacts/full-captain-source-hinge-v4/native384/integration-contract.json')
        joints=Path('/home/astra/projects/captain-3d-rig-lab/rig/contact-source-hinge-v1/retarget-joints-actual.json')
        r=m.Replay(source,joints)
        # The old fixed1024 canvas clipped150 actual120Hz packets here.
        # Use full rendered images, not an estimated actor box or fitted camera.
        for tick in range(390):
            image,row=r.render(tick,'continuous',2,False)
            self.assertEqual(image.size,r.stage)
            self.assertFalse(row['clipped'],f'Full source sprite clipped at tick{tick}')

if __name__=='__main__':unittest.main()
