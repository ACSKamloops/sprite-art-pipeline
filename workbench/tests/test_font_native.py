from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import numpy as np
import pytest
from sprite_workbench.assets import rasterize_font
from sprite_workbench.core import Store,ValidationError,UnsupportedCapability
from sprite_workbench.pipeline import execute_plan
from sprite_workbench import font_native

FONT=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
RETAINED=Path('/home/astra/projects/pixellab-local-test-20261011')


def native_font():
    if not FONT.is_file():pytest.skip('Optional named DejaVu font fixture missing')
    if not shutil.which('cc') or not shutil.which('pkg-config'):pytest.skip('Optional native build tools missing')
    if subprocess.run(['pkg-config','--exists','freetype2'],check=False).returncode:pytest.skip('Optional FreeType development files missing')
    return FONT


def test_default_pillow_unchanged_and_explicit_native_real_metrics():
    path=native_font();old,oldinfo=rasterize_font(path,'Ag ')
    explicit,info=rasterize_font(path,'Ag ',mode='pillow')
    assert oldinfo==info and oldinfo['method']=='pillow-explicit-font-v1'
    for key in old:np.testing.assert_array_equal(old[key]['array'],explicit[key]['array'])
    native,receipt=rasterize_font(path.read_bytes(),'Ag ',mode='freetype-no-hinting')
    assert receipt['load_flags']==32774 and receipt['freetype_version']
    assert receipt['glyph_count']==3 and receipt['pixel_count']>0
    assert native['g']['bearing'][1]<0 and native[' ']['advance']>0
    assert not native[' ']['array'].any()
    assert receipt['font_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['A']['array'].shape[2]==4


def test_native_unavailable_is_structured_and_never_changes_default(monkeypatch):
    if not FONT.is_file():pytest.skip('Optional named DejaVu fixture missing')
    monkeypatch.setattr(font_native.shutil,'which',lambda _:None)
    with pytest.raises(UnsupportedCapability) as exc:rasterize_font(FONT,'A',mode='freetype-no-hinting')
    assert exc.value.to_dict()['status']=='unsupported'
    assert rasterize_font(FONT,'A')[1]['method']=='pillow-explicit-font-v1'


@pytest.mark.parametrize('kwargs',[
    {'characters':['AA']},{'characters':['\ud800']},{'characters':[]},{'characters':['A']*4097},
    {'size':0},{'size':513},{'mode':'mystery'},{'color':None},{'color':[1,2,3,256]},
    {'timeout':float('nan')},{'timeout':0},{'timeout':True}])
def test_native_bad_admission_before_process(kwargs):
    args={'characters':'A','mode':'freetype-no-hinting',**kwargs}
    with pytest.raises(ValidationError):rasterize_font(b'not a font',**args)


def test_bad_font_size_budget_and_timeout(monkeypatch):
    native_font()
    with pytest.raises(ValidationError,match='Unsupported local font'):rasterize_font(b'not font','A',mode='freetype-no-hinting')
    with pytest.raises(ValidationError,match='32MiB'):rasterize_font(b'x'*(32*1024*1024+1),'A',mode='freetype-no-hinting')
    def timed_out(*args,**kwargs):raise subprocess.TimeoutExpired(args[0],kwargs['timeout'])
    monkeypatch.setattr(font_native.subprocess,'run',timed_out)
    with pytest.raises(ValidationError,match='wall-clock'):rasterize_font(FONT,'A',mode='freetype-no-hinting')


def test_native_pixel_protocol_budget_and_pipeline_snapshot(tmp_path,monkeypatch):
    path=native_font();(tmp_path/'source.ttf').write_bytes(path.read_bytes())
    store=Store(tmp_path/'store')
    result=execute_plan(store,{'version':1,'steps':[{'id':'font','action':'font','path':'source.ttf','characters':'Ag ',
                      'size':16,'mode':'freetype-no-hinting','timeout':10}]},base_dir=tmp_path)
    assert result['status']=='completed'
    doc=store.get_json(result['results']['font']['atlas'])
    assert store.get_bytes(doc['font_source']['bytes'])==path.read_bytes()
    assert doc['font_source']['rasterization']['load_flags']==32774


def test_all_81_retained_glyphs_uniform_nohinting():
    native_font();font=RETAINED/'runtime/probes/feature-font-grid/font.ttf'
    metrics=RETAINED/'analysis-root/retained-font/FONT-ATLAS-MEASUREMENTS.json'
    atlas=RETAINED/'runtime/probes/feature-font-grid/image-00.png'
    if not all(p.is_file() for p in (font,metrics,atlas)):pytest.skip('Optional external81glyph vendor oracle absent')
    assert hashlib.sha256(font.read_bytes()).hexdigest()=='defe50b862e2b8f0de4fcf66931687c9a6d1f85c23daeac94aa7a94edb0a6e91'
    expected=json.loads(metrics.read_text());from PIL import Image
    a=np.array(Image.open(atlas).convert('RGBA'))
    chars=''.join(g['character'] for g in expected['glyphs']);got,receipt=rasterize_font(font.read_bytes(),chars,size=16,mode='freetype-no-hinting')
    def shape(mask):
        y,x=np.where(mask);return sorted(zip((x-x.min()).tolist(),(y-y.min()).tolist())) if len(x) else []
    assert len(got)==81
    for g in expected['glyphs']:
        actual=got[g['character']];s=shape(actual['array'][:,:,3]>0);cells=g['atlas_shape_matches']
        assert not s if not cells else any(s==shape(a[c['row']*16:(c['row']+1)*16,c['col']*16:(c['col']+1)*16,3]>0) for c in cells),g['character']
        assert actual['advance']*64==g['advance_width_units']
        assert set(np.unique(actual['array'][:,:,3]))<={0,255}
    assert receipt['load_flags']==32774


def test_native_actual_pixel_budget_enforced():
    path=native_font()
    with pytest.raises(ValidationError,match='pixel/dimension budget'):
        rasterize_font(path,''.join(chr(i) for i in range(32,512)),size=512,mode='freetype-no-hinting')
