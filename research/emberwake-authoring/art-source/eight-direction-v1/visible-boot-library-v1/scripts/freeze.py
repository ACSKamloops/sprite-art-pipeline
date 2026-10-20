from pathlib import Path
import json,hashlib,shutil,collections
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
shutil.copy2(ROOT/'replayed/REPLAY-RECEIPT.json',ROOT/'SOURCE-REPLAY-RECEIPT.json')
donors=json.loads((ROOT/'DONORS.json').read_text());sources=json.loads((ROOT/'INPUTS.json').read_text());editor=json.loads((ROOT/'EDITOR-RECEIPT.json').read_text())
for s in sources:assert sha(ROOT/s['copy'])==s['sha256']and sha(s['source'])==s['sha256']
counts=dict(collections.Counter(d['status']for d in donors))
save(ROOT/'STATUS-SUMMARY.json',{'source_cels':15,'visible_cutouts':30,'status_counts':counts,'complete_hidden_anatomical_parts':0,'donors_locked_as_masters':0,'partial_or_drawing_concern':[{'id':d['id'],'status':d['status'],'visible_extent':d['visible_extent'],'drawing_concern':d['drawing_concern'],'notes':d['notes']}for d in donors if d['status']!='visible_cutout_candidate'],'selection_status':'No donor selected by this inventory. Even candidate means visible surface only.'})
save(ROOT/'MANIFEST.json',{'scope':'Visible-boot source inventory only; no generation or animation expansion','source_cels':sources,'views':['rowan southeast','rowan northeast','lyra southeast','lyra northeast','brann northeast'],'phases':[0,2,6],'canvas':[128,128],'source_pixel_origin':[0,0],'transform':'identity; original stage, no fitting/normalization/translation/scale/rotation','persistent_limb_identity':'unproven; labels describe screen position only','complete_hidden_boot_anatomy':False,'model_calls':0,'canonical_project_sha256':editor['canonical_project_sha256'],'project':'project.json','initial_project':'initial-project.json','actual_guarded_journal':'journal.json','animations':[],'status_counts':counts,'donors':[{'id':d['id'],'status':d['status'],'cutout':d['cutout'],'sha256':sha(ROOT/d['cutout']),'mask':d['mask'],'mask_sha256':sha(ROOT/d['mask']),'witness':d['witness'],'witness_sha256':sha(ROOT/d['witness'])}for d in donors],'source_replay_receipt':'SOURCE-REPLAY-RECEIPT.json','art_selection':'none; visible-source exactness is not a complete boot or gait approval'})
toolkit=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}for p in sorted((ROOT/'toolkit/sprite_lab').rglob('*.py'))]
save(ROOT/'TOOLKIT-DEPENDENCIES.json',{'copied_from':'/home/astra/artifacts/emberwake-brann-full-lower-paint-v1/toolkit/sprite_lab','files':toolkit})
files=sorted(p for p in ROOT.rglob('*')if p.is_file()and p.name!='SHA256SUMS'and'__pycache__'not in p.parts)
(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(ROOT)}\n'for p in files))
print('Frozen15 sources and30 visible donors. MANIFEST SHA256 '+sha(ROOT/'MANIFEST.json'))
print('Canonical project SHA256 '+editor['canonical_project_sha256']);print('Status counts '+json.dumps(counts))
