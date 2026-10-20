"""Self-contained actual decoded-pixel negative: all hashes valid, video stale."""
import hashlib,json,shutil,tempfile,unittest
from pathlib import Path
from PIL import Image,ImageDraw
import export_motion
from export_motion import Motion,export_variant,sha
from inspect_export import inspect, fixed_crop

class FixedCropGeometry(unittest.TestCase):
    def test_full_canvas_travel_union_clamps_only_outside_stage(self):
        rows=[{'draw_origin':[-10,20]},{'draw_origin':[50,70]},{'draw_origin':[90,80]}]
        result=fixed_crop([100,100],[32,32],1,rows,'union')
        self.assertEqual(result['stage_rectangle_xyxy'],[0,20,100,100])
        self.assertEqual(result['unclamped_full_canvas_union_xyxy'],[-10,20,122,112])
        self.assertEqual(result['visible_canvas_placements_not_fully_covered'],0)
        self.assertTrue(result['same_rectangle_all_transitions'])
        self.assertFalse(result['uses_alpha_bbox'])

    def test_explicit_omission_disclosed_and_invalid_geometry_rejected(self):
        rows=[{'draw_origin':[20,20]},{'draw_origin':[60,40]}]
        self.assertEqual(fixed_crop([100,100],[32,32],1,rows,[20,20,52,52])['visible_canvas_placements_not_fully_covered'],1)
        for rectangle in [[-1,0,50,50],[0,0,101,100],[20,20,20,40],[0,0,True,40]]:
            with self.assertRaises(ValueError):fixed_crop([100,100],[32,32],1,rows,rectangle)

class SwappedSourceVideo(unittest.TestCase):
    def test_consistently_rebound_wrong_source_is_detected_in_pixels(self):
        with tempfile.TemporaryDirectory(prefix='motion-inspector-negative-') as temporary:
            root=Path(temporary);source=root/'input';export=root/'export';source.mkdir();export.mkdir();(export/'source-frames').mkdir()
            frames=[]
            for i in range(8):
                image=Image.new('RGBA',(32,32),(0,0,0,0));ImageDraw.Draw(image).rectangle((4,5,20,28),fill=(180,30+i*10,50,255))
                path=source/f'{i}.png';image.save(path);frames.append({'index':i,'file':path.name,'sha256':sha(path),'phase_label':f'synthetic{i}','duration_ms':150,'physical_root':[i*2,0]})
                shutil.copyfile(path,export/'source-frames'/f'{i:02d}.png')
            spec={'schema':'motion-audition/v1','name':'Synthetic regression, not art','canvas':[32,32],'stage':[256,256],'origin':[70,80],'cycle_ms':1200,'root_stride':[16,0],'root_policy':'physical','camera':'fixed','frames':frames}
            spec_path=source/'spec.json';spec_path.write_text(json.dumps(spec,indent=2)+'\n')
            variant=export_variant(Motion(spec_path),export,1,1,False,1,17)
            report={'spec_sha256':sha(spec_path),'source_sha256':[x['sha256']for x in frames],'code_sha256':sha(export_motion.__file__),'variants':[variant]}
            (export/'report.json').write_text(json.dumps(report,indent=2)+'\n')
            self.assertTrue(inspect(spec_path,export,root/'positive',{'rgba-1x-normal.mp4'},detail_crop='union',detail_scale=2)['passed'])
            path=source/spec['frames'][0]['file'];image=Image.open(path).convert('RGBA')
            ImageDraw.Draw(image).rectangle((4,5,20,28),fill=(5,210,240,255));image.save(path)
            spec['frames'][0]['sha256']=sha(path);spec_path.write_text(json.dumps(spec,indent=2)+'\n')
            shutil.copyfile(path,export/'source-frames/00.png')
            report['spec_sha256']=sha(spec_path);report['source_sha256']=[x['sha256']for x in spec['frames']]
            (export/'report.json').write_text(json.dumps(report,indent=2)+'\n')
            # Video and its hash stay frozen/valid. Only decoded RGB exposes stale art.
            result=inspect(spec_path,export,root/'negative',{'rgba-1x-normal.mp4'})
            self.assertFalse(result['passed']);self.assertGreater(result['variants'][0]['failed_decoded_frames'],0)
            self.assertGreater(result['variants'][0]['decoded_RGB_max_error'],100)
            self.assertEqual(result['variants'][0]['declared_scene_state_mismatches'],0)
            self.assertTrue(result['variants'][0]['all_actual_timestamps_match_report'])
            print(json.dumps({'scenario':'valid_hashes_stale_video_wrong_source','detected':not result['passed'],'failed_decoded_frames':result['variants'][0]['failed_decoded_frames'],'max_RGB_error':result['variants'][0]['decoded_RGB_max_error'],'timestamp_sequence_matches':True,'root_state_mismatches':result['variants'][0]['declared_scene_state_mismatches']}))

if __name__=='__main__':unittest.main()
