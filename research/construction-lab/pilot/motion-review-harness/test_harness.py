import copy, hashlib, json, tempfile, unittest
from pathlib import Path
from PIL import Image
from export_motion import Motion, round_away, schedule

class Contracts(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        image=Image.new('RGBA',(8,8),(200,40,30,255));image.save(self.root/'pose.png')
        self.spec={'schema':'motion-audition/v1','canvas':[8,8],'stage':[64,64],'origin':[16,16],'cycle_ms':30,'root_stride':[12,4],'root_policy':'physical','camera':'fixed','frames':[{'index':i,'file':'pose.png','sha256':hashlib.sha256((self.root/'pose.png').read_bytes()).hexdigest(),'phase_label':str(i),'duration_ms':d,'physical_root':[i*6,i*2]}for i,d in enumerate([13,17])]}
    def tearDown(self):self.temp.cleanup()
    def motion(self,s=None):
        p=self.root/'spec.json';p.write_text(json.dumps(s or self.spec));return Motion(p)
    def test_clock(self):
        m=self.motion();self.assertEqual(m.state(12.999)['frame'],0);self.assertEqual(m.state(13)['frame'],1);self.assertEqual(m.state(30)['frame'],0);self.assertEqual(m.state(30)['physical_root'],[12,4]);self.assertEqual(m.state(21.5)['physical_root'],[9,3])
    def test_exact_boundaries_in_schedule(self):
        self.assertEqual(schedule(self.motion(),2,2,17),sorted({0,17,26,34,51,60,68,85,86,102,119,120}))
    def test_same_actor_support(self):
        s=copy.deepcopy(self.spec);s['root_policy']='shared_episode_target';s['frames'][0]['supports']={'right':{'world_target':[20,20],'material_sole':[7,9]}};m=self.motion(s);self.assertEqual(m.state(5)['draw_root'],[13,11]);self.assertEqual(m.state(35)['draw_root'],[25,15]);self.assertEqual(m.state(15)['draw_root'],m.state(15)['physical_root'])
    def test_numeric_caption_matches_decode_oracle(self):
        self.spec["stage"]=[768,640]
        m=self.motion()
        self.assertEqual(m.render(0)[0].tobytes(),m.render(0.0)[0].tobytes())
    def test_ties_away(self):self.assertEqual((round_away(-.5),round_away(.5)),(-1,1))
    def test_negatives(self):
        for key,value in [('duration_ms',0),('duration_ms',13.5),('duration_ms',True),('index',1),('sha256','0'*64),('file','../escape.png'),('phase_label','')]:
            s=copy.deepcopy(self.spec);s['frames'][0][key]=value
            with self.subTest(key=key,value=value),self.assertRaises((ValueError,FileNotFoundError)):self.motion(s)
        s=copy.deepcopy(self.spec);s['cycle_ms']=31
        with self.assertRaises(ValueError):self.motion(s)
        s=copy.deepcopy(self.spec);s['root_policy']='fit_each_foot'
        with self.assertRaises(ValueError):self.motion(s)

if __name__=='__main__':unittest.main()
