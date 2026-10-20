from pathlib import Path
import json,hashlib,datetime
S=Path('/home/astra/artifacts/emberwake-brann-se-three-pose-v1')
A=Path('/home/astra/artifacts/emberwake-brann-three-pose-independent-replay-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def save(n,d):(A/n).write_text(json.dumps(d,indent=2)+'\n')
before=load(A/'SOURCE-INVENTORY-BEFORE.json')
after={'source':str(S),'files':[{'path':str(p.relative_to(S)),'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(S.rglob('*'))if p.is_file()],'SHA256SUMS_sha256':sha(S/'SHA256SUMS')}
save('SOURCE-INVENTORY-AFTER.json',after)
assert before['files']==after['files']
assert before['SHA256SUMS_sha256']==after['SHA256SUMS_sha256']
ledger=load(A/'LEDGER-VERIFICATION.json');assert ledger['all_ledger_entries_match']
for entry in ledger['entries']:assert sha(S/entry['path'])==entry['expected_sha256']
checks=load(A/'INDEPENDENT-CHECKS.json');run=load(A/'ACTUAL-RUN.json');sourceonly=load(A/'SOURCE-ONLY-RUN.json')
receipt={
 'status':'PASS independent mechanical replay, with listed qualifications; art not rated',
 'audited_package':str(S),'audit_folder':str(A),'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':'Mechanical ledger, fresh retained replay, all8 PNG/RGBA, journal undo/redo, negative guards, source witnesses, source-map/occlusion claims and dependency inspection. No canonical writes, art review, model calls, GUI/game or media playback.',
 'source_unchanged':{'all_files_identical_before_after':True,'file_count':len(after['files']),'ledger_sha256':after['SHA256SUMS_sha256']},
 'ledger':{'entries':len(ledger['entries']),'all_match':True,'unlisted_files':ledger['unlisted_files'],'qualification':'SHA256SUMS omits its own file and eight preexisting toolkit bytecode cache files. Source-only replay bypassed those caches; none were changed.'},
 'actual_retained_script_run':run,'actual_source_only_script_run':sourceonly,
 'all8_decoded_RGBA_exact':True,'all8_PNG_bytes_exact':True,'all8_editor_renders_exact':True,
 'initial_project_sha256':checks['initial_project_sha256'],'project_sha256':checks['final_project_sha256'],
 'journal':{'transactions':3,'undo_all_exact':True,'redo_all_exact':True,'negative_guards':checks['negative_guard_checks'],'qualification':checks['guard_qualification']},
 'source_witness_claims':{'six_maps_and_source_array_owner_metadata_exact':True,'declared_inverse_maps_and_literal_joins_reproduced_by_retained_script':True,'literal_witness_counts':checks['literal_source_witnesses'],'six_occlusion_counts_and_masks_exact':True,'qualification':checks['occlusion_qualification'],'phase03_projection':'Declared nearest-sampled 5/6 vertical boot projection: 379 source-positive pixels become 319 placed; explicitly not unscaled source-perfect or hidden anatomy.'},
 'preservation':{'changed_phases':[3,4,5],'unchanged_endpoint_PNG_bytes':[0,1,2,6,7],'full_original_upper_on_changed_phases_RGBA_exact':True},
 'clock':'8 x 9/160 seconds = 0.45 second loop; project clock checked, media playback not audited',
 'dependency_inspection':{'runtime':'Python standard library, installed Pillow and NumPy, package-local sprite_lab toolkit and package-local artwork/JSON/NPZ. No replay call to network, subprocess, outside artwork or canonical repo found.','tested_versions':{'Python':checks['python'],'Pillow':checks['Pillow'],'NumPy':checks['NumPy']},'producer_only_external_paths':{'script':'scripts/source_proof.py','paths':['/home/astra/artifacts/emberwake-brann-full-lower-paint-v1/se-near-attachment-v5','/home/astra/artifacts/emberwake-brann-se04-source-part-guide-v1/frames/04.png','/home/astra/artifacts/emberwake-brann-se04-source-part-guide-v1/GUIDE.json'],'executed':False},'other_helpers':'scripts/proofs_media.py requires ffmpeg/ffprobe; producer/draft/freeze helpers write package outputs. None were run. Portable replay claim is verified; whole producer helper suite is not self-contained.'},
 'gaps':['No art acceptance, anatomy/contact claim, inherited quality score or selection.','No GUI/editor interoperability or in-game runtime check.','APNG/MP4 bytes are ledger-verified only; duration/playback was not independently tested.','Python/Pillow/NumPy are installed dependencies rather than a vendored environment.'],
 'evidence':['ACTUAL-RUN.json','REPLAY-STDOUT.txt','REPLAY-STDERR.txt','SOURCE-ONLY-RUN.json','SOURCE-ONLY-STDOUT.txt','SOURCE-ONLY-STDERR.txt','INDEPENDENT-CHECKS.json','LEDGER-VERIFICATION.json','SOURCE-INVENTORY-BEFORE.json','SOURCE-INVENTORY-AFTER.json','audit_checks.py']
}
save('AUDIT-RECEIPT.json',receipt)
report='''Independent Brann mechanical audit: PASS with qualifications. Art was not rated.\n\nThe retained replay exited 0 into a fresh audit output. A second fresh replay bypassed the package\'s preexisting bytecode caches and also exited 0. Both reproduced all eight frozen PNG bytes and decoded RGBA; the recorded editor project renders agree. All three journal transactions undo to the initial project hash and redo to the final hash. Stale journal, stale transaction, out-of-mask paint, and tampered receipt were rejected.\n\nAll 209 ledger entries match. The package has 218 files: SHA256SUMS itself and eight preexisting toolkit bytecode files are unlisted. All 218 source files remained byte-identical across the audit. Replay uses local source assets/toolkit with Python, Pillow and NumPy. The retained source_proof producer helper references outside asset folders; it is not called by replay and was not executed. Media regeneration helpers require ffmpeg/ffprobe and were not executed.\n\nSix source maps, their full source-image witnesses, literal source colors, and six declared alpha-occlusion records/masks checked exactly. Phase03 explicitly uses a nearest-sampled 5/6 vertical projection; it is not an unscaled source-perfect part. Alpha contribution is a compositing claim, not recovered anatomy or perceived visibility. Actual operation masks exclude the fixed upper; there are no intrinsic upper layer locks or candidate_patch cel-hash guards. Project hash preconditions, operation masks, receipt comparison and final upper equality protect this recorded replay.\n\nProject timing is exactly 8 x 9/160 s = 0.45 s. Media playback, editor GUI interoperability, runtime and visual quality were outside scope.\n\nSee AUDIT-RECEIPT.json and INDEPENDENT-CHECKS.json for hashes, commands, actual run/exit evidence and negative guard results.\n'''
(A/'REPORT.md').write_text(report)
# Hash all audit evidence at completion; ledger excludes itself by construction.
(A/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(A)}\n'for p in sorted(A.rglob('*'))if p.is_file()and p.name!='SHA256SUMS'))
print(json.dumps({'status':'PASS','source_files_unchanged':len(after['files']),'ledger_entries':len(ledger['entries']),'report':str(A/'REPORT.md'),'receipt':str(A/'AUDIT-RECEIPT.json'),'source_only_exit':sourceonly['exit_code'],'audit_ledger_sha256':sha(A/'SHA256SUMS')}))
