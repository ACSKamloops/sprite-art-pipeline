from fractions import Fraction
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
import pytest

from sprite_workbench.core import Store, ValidationError, load_sequence
from sprite_workbench.effects import render_effect

FIX = Path(__file__).parent/'fixtures/effects'


@pytest.mark.parametrize('case',json.loads((FIX/'reference-cases.json').read_text())['cases'],ids=lambda c:c['family'])
def test_F09_all17_source_family_adapter_sequences(tmp_path,case):
    store=Store(tmp_path)
    subject=store.put_raster(np.array(case['subject'],np.uint8)) if case['subject'] is not None else None
    result=render_effect(store,case['recipe'],subject=subject)
    for stream,ident in result['streams'].items():
        doc,frames=load_sequence(Store(tmp_path),ident)
        assert [hashlib.sha256(a.tobytes()).hexdigest() for a in frames]==case['expected'][stream]
        assert all(Fraction(*f['duration']) == 1/Fraction(str(case['recipe']['fps'])) for f in doc['frames'])
        assert doc['visual_approval']=='unreviewed'
    assert result['status']=='candidate_needs_visual_review'


@pytest.mark.parametrize('case',json.loads((FIX/'server-cases.json').read_text())['cases'],ids=lambda c:c['name'])
def test_F09_retained_actual_MCP_pixels_separate_from_clocks(tmp_path,case):
    store=Store(tmp_path)
    result=render_effect(store,case['recipe'])
    doc,frames=load_sequence(store,result['sequence'])
    sheet=np.array(Image.open(FIX/case['sheet']).convert('RGBA'))
    manifest=json.loads((FIX/case['manifest']).read_text())
    assert len(frames)==len(manifest['frames'])
    for a,record in zip(frames,manifest['frames']):
        r=record['frame']; expected=sheet[r['y']:r['y']+r['h'],r['x']:r['x']+r['w']]
        assert np.array_equal(a,expected)
    assert doc['loop']==case['recipe']['loop']
    # Local rational clock is explicit; source sidecar rounds each duration.
    assert Fraction(*doc['frames'][0]['duration'])==Fraction(1,case['recipe']['fps'])
    assert manifest['frames'][0]['duration']==int(1000/case['recipe']['fps']+.5)


def test_effect_rejects_resource_and_unknown_family_before_publication(tmp_path):
    store=Store(tmp_path)
    with pytest.raises(ValidationError,match='Local VFX'):
        render_effect(store,{'canvas':{'w':1024,'h':1024},'layers':[]})
    with pytest.raises(ValidationError):
        render_effect(store,{'canvas':{'w':32,'h':32},'frames':1,'layers':[{'id':'x','type':'private-neural-magic'}]})
    assert store.get_head('effect') is None
