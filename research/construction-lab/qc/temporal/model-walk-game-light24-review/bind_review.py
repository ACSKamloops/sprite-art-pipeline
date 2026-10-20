"""Bind a personally viewed review to immutable source/capture inputs; checks do not score art."""
import hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
BASE=Path('/home/astra/projects/sprite-construction-lab-art-expansion/pilot/model-sprite-quality-v1')
PACK=BASE/'candidate-walk-bow160-game-light-v11'
MAIN=Path('/home/astra/projects/sprite-construction-lab')
COPY=MAIN/'pilot/model-sprite-quality-v1'/PACK.name
CAP=Path('/home/astra/artifacts/model-walk-game-light-final24-timed/capture.json')
EXPECTED='03fa079e0495dd83f81ad6a00d1778f57e4b7effa885c4d5d54498ebd7c226c8'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p,expected=None):
 h=sha(p)
 if expected:assert h==expected,(str(p),h,expected)
 return {'path':str(p),'sha256':h}
m=json.loads((PACK/'manifest.json').read_text());cap=json.loads(CAP.read_text())
assert sha(PACK/'manifest.json')==EXPECTED==sha(COPY/'manifest.json')==cap['manifest_sha256']
frames=[]
for view,records in m['views'].items():
 for rec in records:
  assert sha(PACK/rec['png'])==rec['sha256']==sha(COPY/rec['png'])
  frames.append({'view':view,'sample':rec['sample'],'png':rec['png'],'sha256':rec['sha256']})
assert len(frames)==48
sources=[bind(BASE/p,h) for p,h in m['source_sha256'].items()]
renderer=bind(BASE/'source/renderers/render_walk_game_light-v11.py',m['render_script_sha256'])
assert sha(BASE/'render_walk_game_light.py')==renderer['sha256']
reopen=json.loads((PACK/'reopen-validation.json').read_text())
assert reopen['passed'] and len(reopen['checks'])==8 and all(c['exact_decoded_component_differences']==0 for c in reopen['checks'])
scene=bind(PACK/'ranger-walk-render.blend',reopen['scene_sha256'])
relative={};matrix_ledger_residual=0
for view,t in m['view_transforms'].items():
 camera=np.array(t['camera_world_matrix'])
 relative[view]={}
 for lamp,matrix in t['lights_world_matrices'].items():
  actual=np.linalg.inv(camera)@np.array(matrix)
  declared=np.array(t['lights_camera_space_matrices'][lamp])
  matrix_ledger_residual=max(matrix_ledger_residual,float(np.max(np.abs(actual-declared))))
  relative[view][lamp]=actual
max_direction_residual=max(float(np.max(np.abs(relative[v][l]-relative['front'][l]))) for v in relative for l in relative[v])
assert max_direction_residual<1e-5
html=bind(MAIN/'pilot/model-walk-audition/index.html',cap['player_sha256'])
static=json.loads((ROOT/'pairs/static-inputs.json').read_text());timed=json.loads((ROOT/'timed/capture-binding.json').read_text())
assert static['manifest_sha256']==timed['manifest_sha256']==EXPECTED
assert timed['chronological_screenshots']==sum(len(x['entries']) for x in cap['modes'])==43
assert timed['paused_screenshots']==len(cap['paused'])==12
assert all(x['stopped']['loop']>=3 and x['stopped']['seconds']>=3.75 for x in cap['modes'])
observations=[
 {'kind':'strength','description':'Four genuine views retain the same hood, costume volume, limb anatomy and bow hand. No observed direction-dependent limb role swap, grip detach or loop reset.'},
 {'kind':'strength','description':'Bent passing knees, alternating reach and modest torso bob form a credible authored walking performance. The free arm counters the stride while the constrained arm carries its actual bow.'},
 {'kind':'lighting_repair','description':'Right-facing calf and forearm contrast now approaches the left-facing treatment. Hood/cloth/leather stay recognizable across all four views, without the previous conspicuous bright-side/dark-side split. Different exposed surfaces and asymmetric gear still have legitimate different tones; equal whole-sprite brightness is not required.'},
 {'kind':'limitation','description':'Thin olive bow remains faint against the dark audition background, especially from behind. Narrow feet and sparse face details limit small-scale readability; test intended game backgrounds before production.'},
 {'kind':'projected_observation','description':'In the inspected key images the lower bow limb stays above the lowest foot region. This is a screen-image observation, not a world contact, terrain clearance or collision measurement.'},
 {'kind':'untested','description':'Fixed-origin playback does not prove planted-foot slip, movement speed calibration, anatomical sole/toe contact, terrain behavior or transitions. No free-unarmed walk, other actions, original CopperScout brief, complete game library or user art-direction acceptance.'}
]
r={
 'schema':'sprite.independent_visual_review.v2','decision':'accepted_bow_walk_foundation_only','reviewer':'independent temporal reviewer',
 'input_fingerprint':EXPECTED,'clip_ids':['bow_walk_'+v for v in m['views']], 'observations':observations,
 'scope':{'accepted':'Four-direction modern RPG prerendered bow-carry walk foundation only.','lighting_revision_reviewed':True,'production_art_approved':False,'pixel_painted_art_approved':False,'original_CopperScout_design_approved':False,'full_animation_library_approved':False,'user_art_direction_approval':False},
 'visual_coverage':{'all48_static_poses':True,'all44_adjacent_and4_loop_pairs':True,'static_scales':[1,2],'static_pair_sheets_personally_viewed':32,'automatic_visual_inheritance':False,'chronological_screenshots_personally_viewed':43,'chronological_screenshots_by_scale':{str(x['scale']):len(x['entries']) for x in cap['modes']},'timed_direction_cells':172,'paused_screenshots_personally_viewed':12,'paused_direction_cells':48,'timed_strips_personally_viewed':21,'clock_duration_seconds':[x['stopped']['seconds'] for x in cap['modes']],'clock_cycles_completed_each_mode':3,'continuous_video_ingested':False,'timestamp_claim':'Screenshot before/after states are clock ranges and may cross a pose boundary.'},
 'clock':{'source_fps':24,'source_frames':[0,30],'cycle_seconds':1.25,'unique_keys_per_view':12,'duplicated_endpoint_excluded':True,'gif_centisecond_quantization':'GIF holds approximate individual 1.25/12-second keys; full cycle is 1250ms.'},
 'lighting_evidence':{'camera_relative_light_direction_residual_max':max_direction_residual,'declared_matrix_ledger_residual_max':matrix_ledger_residual,'scope':'Independent numeric check of recorded camera/light matrices. All lamps rotate with each orbit view; this establishes a fixed-screen baked studio convention, not dynamic world illumination.'},
 'source_bindings':{'manifest':bind(PACK/'manifest.json',EXPECTED),'main_manifest':bind(COPY/'manifest.json',EXPECTED),'source_files':sources,'render_script':renderer,'renderer_freeze':bind(BASE/'source/renderers/renderer-v11-freeze.json'),'packed_scene':scene,'landmarks':bind(PACK/'landmarks.json'),'producer_reopen_report':bind(PACK/'reopen-validation.json'),'producer_byte_report':bind(PACK/'byte-validation.json'),'capture':bind(CAP),'browser_html':html,'browser_config':bind(MAIN/'pilot/model-walk-audition/config.json'),'static_receipt':bind(ROOT/'pairs/static-inputs.json'),'timed_receipt':bind(ROOT/'timed/capture-binding.json'),'frames':frames},
 'historical_review_preserved':{'v10_manifest':'ff86ff56b7aaa0c603b3582e569853823dfd1c601ef645fa5d48d1ff5d67aae7','v10_receipt':bind(ROOT.parent/'model-walk-bow24-review/final-review.json'),'old_V2_visual_rejection_remains_valid':True},
 'authorship_boundary':'Credible performance comes from the licensed Quaternius authored 3D model/Walk. Camera, face shader detailing, contrast and bow presentation are declared adaptations; this is not proof that rejected AI sheets or painted cutouts became good animation.',
 'unpromoted_fine_edit_demo_in_review':False
}
(ROOT/'final-review.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'decision':r['decision'],'manifest':EXPECTED,'frames':len(frames),'viewed_chronological':43,'matrix_residual':max_direction_residual,'review_sha256':sha(ROOT/'final-review.json')}))
