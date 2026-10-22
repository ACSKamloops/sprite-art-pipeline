#!/usr/bin/env python3
"""Read-only exact raster/journal/native-editor artifact replay. Never assigns art approval."""
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from PIL import Image

SKILL=Path(__file__).resolve().parents[1]
FIXTURE=SKILL/'assets/part-jab-study'
sys.path.insert(0,str(SKILL.parent/'sprite-construction-editing/assets/toolkit'))
from sprite_lab import load_project,project_hash,render_frame,import_aseprite,read_aseprite
from sprite_lab.history import History


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    data=json.loads((FIXTURE/'PROVENANCE.json').read_text())
    assert sha(FIXTURE/'layered/initial.project.json')==data['initial_file_sha256']
    assert sha(FIXTURE/'layered/project.json')==data['final_file_sha256']
    initial=load_project((FIXTURE/'layered/initial.project.json').read_text())
    expected=load_project((FIXTURE/'layered/project.json').read_text())
    journal=json.loads((FIXTURE/'layered/underpaint.journal.json').read_text())
    history=History.replay(initial,journal)
    assert project_hash(history.project)==project_hash(expected)
    assert project_hash(history.undo())==project_hash(initial)
    assert project_hash(history.redo())==project_hash(expected)
    for rel,digest in expected['provenance']['source_image_sha256'].items():
        assert sha(FIXTURE/'layered'/rel)==digest
    native=read_aseprite(FIXTURE/'layered/editable.aseprite')
    assert project_hash(import_aseprite(FIXTURE/'layered/editable.aseprite'))==project_hash(expected)
    resaved=read_aseprite(FIXTURE/'native-editor-proof/resaved.aseprite')
    sheet=Image.open(FIXTURE/'native-editor-proof/sheet.png').convert('RGBA')
    manifest=json.loads((FIXTURE/'manifest.json').read_text())
    images=[]
    for i,(frame,entry,a,b) in enumerate(zip(expected['frames'],manifest['frames'],native['frames'],resaved['frames'],strict=True)):
        p=FIXTURE/'expected-frames'/Path(entry['file']).name
        assert sha(p)==entry['sha256']
        image=Image.open(p).convert('RGBA');images.append(image)
        assert render_frame(history.project,frame['id']).tobytes()==image.tobytes()
        assert hashlib.sha256(image.tobytes()).hexdigest()==entry['rgba_sha256']
        assert sheet.crop((i*80,0,(i+1)*80,80)).tobytes()==image.tobytes()
        assert set(a['cels'])==set(b['cels'])
        for layer in a['cels']:
            assert a['cels'][layer].tobytes()==b['cels'][layer].tobytes()
    assert images[0].tobytes()==images[-1].tobytes()
    assert all(im.crop((0,52,80,80)).tobytes()==images[0].crop((0,52,80,80)).tobytes() for im in images)
    assert sum(f['duration_ticks'] for f in expected['frames'])==28
    assert expected['animations'][0]['fps']==48
    print(json.dumps({'frames':len(images),'layers':len(expected['layers']),
          'journal_replay_undo_redo_exact':True,'portable_source_pins_exact':True,
          'ASE_project_exact':True,'retained_external_editor_cels_and_sheet_exact':True,
          'all_rendered_rgba_exact':True,'fixed_lower_body_exact':True,'duration':[7,12],
          'scope':'Offline fixture and retained editor-artifact replay only; no model call, fresh editor launch or art approval.'},indent=2))


if __name__=='__main__':
    main()
