from fractions import Fraction
import numpy as np
import pytest
from sprite_workbench.core import Store,ValidationError,save_sequence,load_sequence
from sprite_workbench.composition import compose_sequences,source_over


def test_F09_composition_merged_rational_clock_and_alpha(tmp_path):
    store=Store(tmp_path)
    blue=np.full((2,2,4),[0,0,255,255],np.uint8)
    red=np.full((2,2,4),[255,0,0,128],np.uint8)
    body=save_sequence(store,[blue,blue.copy()],[Fraction(1,10),Fraction(1,5)],pivots=[(1,2)]*2)
    front=save_sequence(store,[red],[Fraction(1,6)])
    result=compose_sequences(store,body,front=front)
    doc,frames=load_sequence(Store(tmp_path),result['sequence'])
    assert [Fraction(*f['duration']) for f in doc['frames']]==[Fraction(1,10),Fraction(1,15),Fraction(2,15)]
    assert frames[0][0,0].tolist()==[128,0,127,255]
    assert np.array_equal(frames[-1],blue)
    assert doc['frames'][2]['pivot']==[1,2]
    assert doc['metadata']['mapping'][2]['front_frame'] is None
    with pytest.raises(ValidationError,match='common period'):
        compose_sequences(store,body,front=front,loop=True)


def test_hidden_rgb_and_integer_alpha_independent_controls():
    back=np.array([[[31,17,23,0],[0,0,255,128]]],np.uint8)
    front=np.array([[[199,27,69,0],[255,0,0,128]]],np.uint8)
    out=source_over(back,front)
    assert out[0,0].tolist()==[31,17,23,0]
    assert out[0,1].tolist()==[170,0,85,192]
    assert back[0,1].tolist()==[0,0,255,128]
