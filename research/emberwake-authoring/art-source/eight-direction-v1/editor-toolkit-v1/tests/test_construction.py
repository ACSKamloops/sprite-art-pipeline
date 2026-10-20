import tempfile,json,sys,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from sprite_construct import construct
from sprite_lab import render_frame
class ConstructionTests(unittest.TestCase):
    def test_actual_source_placement_layers_shared_cels_partial_alpha(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);Image.new('RGBA',(2,2),(10,30,80,255)).save(p/'body.png');Image.new('RGBA',(1,1),(200,40,90,128)).save(p/'cloth.png')
            frame={'id':'a','duration_ticks':5,'cels':{'body':{'image':'body.png','at':[1,1]},'cloth':{'image':'cloth.png','at':[2,1]}}}
            spec={'schema':'sprite-construction-spec/v1','canvas':{'width':4,'height':4,'render_pivot':[2,2],'ground_pivot':[2,4]},'layers':[{'id':x,'name':x,'locked':False} for x in ['body','cloth']],
                'frames':[frame,{**frame,'id':'b'}],'animations':[{'id':'walk','frames':['a','b'],'fps':60.098811862348406,'loop':True,'events':[]}]}
            (p/'spec.json').write_text(json.dumps(spec));project=construct(p/'spec.json');self.assertEqual(len(project['cels']),2);image=render_frame(project,'a')
            self.assertEqual(image.getpixel((0,0)),(0,0,0,0));self.assertEqual(image.getpixel((1,1)),(10,30,80,255));self.assertEqual(image.getpixel((2,1)),(105,35,85,255));self.assertEqual(project['frames'][0]['cels'],project['frames'][1]['cels'])
            spec['frames'][0]['cels']['body']['at']=[3,3];(p/'spec.json').write_text(json.dumps(spec))
            with self.assertRaisesRegex(ValueError,'clipped'):construct(p/'spec.json')
            spec['frames'][0]['cels']['body']['image']='../escape.png';(p/'spec.json').write_text(json.dumps(spec))
            with self.assertRaisesRegex(ValueError,'portable'):construct(p/'spec.json')
