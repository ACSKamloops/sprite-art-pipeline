"""Independent palette import edge cases; canvas-boundary input, no provider."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import numpy as np
import pytest

from sprite_workbench import parity_palette as palette
from sprite_workbench.core import ValidationError

ASSET=Path(os.environ.get('PIXELLAB_PALETTE_ORIGINAL',
    '/home/astra/artifacts/pixellab-recovery-web-20261014/assets/2713c302f049-create-9c5cec3372075418.js'))


def original(rgba):
    if not ASSET.exists() or not shutil.which('node'):
        pytest.skip('Direct retained-source differential requires original bundle and Node')
    request={'width':rgba.shape[1],'height':rgba.shape[0],'rgba':rgba.reshape(-1).tolist()}
    result=subprocess.run(['node',str(Path(__file__).with_name('parity_palette_oracle.cjs')),str(ASSET)],
        input=json.dumps(request),capture_output=True,text=True,timeout=10)
    assert result.returncode==0,result.stderr
    return json.loads(result.stdout)


def matches_source(rgba):
    expected=original(rgba);actual=palette.import_palette_image(rgba)
    assert {k:actual[k]for k in ('colors','warning','error')}==expected
    assert actual['accepted']is(expected['error']is None)
    return actual


def bins(reverse=False,repeat=0):
    # >256 RGB values in two5-bit bins. Every bin's representative has a
    # first-seen frequency tie, unless repeat explicitly breaks the tie.
    dark=[[r,g,b,255]for r in range(8)for g in range(8)for b in range(8)][:257]
    if reverse:dark.reverse()
    return np.array(dark+[[7,7,7,1]]*repeat+[[248,248,248,255]],np.uint8)[None,...]


def test_two_bin_equal_frequency_ties_keep_first_rgb_not_lexicographic_minimum():
    forward=matches_source(bins());reverse=matches_source(bins(reverse=True))
    assert forward['colors']==['#000000','#f8f8f8']
    assert reverse['colors']==['#040000','#f8f8f8']
    assert forward['adapter']['branch']=='original-32-representatives'


def test_frequency_winner_uses_occurrences_not_alpha_weight():
    a=bins(repeat=3);b=a.copy();b[...,3]=255
    low_alpha=matches_source(a);opaque=matches_source(b)
    assert low_alpha['colors']==opaque['colors']==['#070707','#f8f8f8']
    assert low_alpha['warning']==opaque['warning']


def test_exact_256_with_many_hidden_extras_does_not_cross_threshold():
    visible=[[i,0,0,1 if i%2 else 255]for i in range(256)]
    hidden=[[i,1,1,0]for i in range(256)]
    a=np.array(visible+hidden,np.uint8)[None,...]
    result=matches_source(a)
    assert result['adapter']['unique_visible_rgb']==256
    assert result['adapter']['branch']=='original-first-seen'
    assert result['colors']==['#%02x0000'%i for i in range(256)]
    assert result['warning']is None


def test_257_same_bin_rejection_is_not_promoted_or_warned_as_success():
    dark=bins()[...,:257,:]
    result=matches_source(dark)
    assert result['adapter']['unique_visible_rgb']==257
    assert result['accepted']is False and result['colors']==[] and result['palette_rgba']==[]
    assert result['warning']is None
    assert result['error']=='The image has 1 colour; a palette needs at least 2.'


def test_first_seen_order_is_not_frequency_sorted_and_duplicates_ignore_alpha_magnitude():
    a=np.array([[[11,22,33,0],[240,7,2,1],[1,2,3,127],*[ [1,2,3,255]for _ in range(20)],
        [240,7,2,255],[11,22,33,1]]],np.uint8)
    result=matches_source(a)
    assert result['colors']==['#f00702','#010203','#0b1621']
    assert result['palette_rgba']==[[240,7,2,255],[1,2,3,255],[11,22,33,255]]


def test_noncontiguous_readonly_array_is_row_major_without_input_mutation():
    storage=np.array([[[10,20,30,255],[40,50,60,127],[70,80,90,1]],
                      [[110,120,130,255],[140,150,160,1],[170,180,190,0]]],np.uint8)
    view=storage[:,::-1];view.setflags(write=False);before=storage.copy()
    result=matches_source(view)
    assert result['colors']==['#46505a','#28323c','#0a141e','#8c96a0','#6e7882']
    assert result['adapter']['source_rgba_sha256']==hashlib.sha256(view.tobytes(order='C')).hexdigest()
    assert np.array_equal(storage,before)


def test_caller_mutation_during_child_execution_cannot_rewrite_source_receipt(monkeypatch):
    a=np.array([[[255,0,0,255],[0,255,0,255]]],np.uint8)
    submitted=a.copy();real=palette.subprocess.run
    def change_caller_after_original_source_returns(*args,**kwargs):
        result=real(*args,**kwargs)
        a[:]=[0,0,255,255]
        return result
    monkeypatch.setattr(palette.subprocess,'run',change_caller_after_original_source_returns)
    result=palette.import_palette_image(a)
    assert result['colors']==['#ff0000','#00ff00']
    assert result['adapter']['unique_visible_rgb']==2
    assert result['adapter']['source_rgba_sha256']==hashlib.sha256(submitted.tobytes()).hexdigest()


def test_maximum_local_pixel_budget_accepts_two_colors_without_reduction():
    a=np.zeros((512,512,4),np.uint8);a[...,3]=255;a[:,1::2,:3]=[12,34,56]
    result=palette.import_palette_image(a)
    assert result['colors']==['#000000','#0c2238'] and result['warning']is None


def test_over_budget_refuses_before_node(monkeypatch):
    monkeypatch.setattr(palette.subprocess,'run',lambda *a,**k:pytest.fail('Over-budget input reached child'))
    with pytest.raises(ValidationError,match='local budget'):
        palette.import_palette_image(np.zeros((513,512,4),np.uint8))


def test_timeout_and_missing_node_have_no_fallback(monkeypatch):
    a=np.array([[[0,0,0,255],[255,255,255,255]]],np.uint8)
    def timeout(*args,**kwargs):raise subprocess.TimeoutExpired(args[0],10)
    monkeypatch.setattr(palette.subprocess,'run',timeout)
    with pytest.raises(ValidationError,match='execution budget'):palette.import_palette_image(a)
    monkeypatch.setattr(palette.shutil,'which',lambda _:None)
    with pytest.raises(ValidationError,match='no fallback'):palette.import_palette_image(a)
