"""Schedule real UI continuations to guard newer user selections."""
from pathlib import Path
import subprocess


def test_source_ui_discards_superseded_restore_and_file_load():
    script = r'''
const fs = require('fs'), vm = require('vm'), assert = require('assert/strict');
class Element {
  constructor() { this.children=[]; this.events={}; this.value=''; }
  addEventListener(name, fn) { this.events[name]=fn; }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children=items; }
  setAttribute() {}
  get dataset() { return this._dataset ||= {}; }
}
const elements = new Map();
global.window = {}; global.document = {
  getElementById(id) { if (!elements.has(id)) elements.set(id,new Element()); return elements.get(id); },
  createElement() { return new Element(); }
};
vm.runInThisContext(fs.readFileSync('sprite_workbench/web/source-vfx.js','utf8'));
function deferred() { let resolve; const promise=new Promise(r=>resolve=r); return {promise,resolve}; }
function setup() {
  elements.clear(); const receipt=deferred(); let extraFetches=0, previews=0;
  const old={id:'observed.old',recipe:{label:'old'},provenance:{}};
  const fresh={id:'observed.new',recipe:{label:'new'},provenance:{}};
  const ui=new window.PixelLabSourceUI({action:fn=>fn(),invoke:async()=>({controls:[]}),
    request:async path=> {
      if(path.endsWith('receipt')) return receipt.promise;
      extraFetches++; return {kind:'effect-recipe',subject:null,images:{}};
    }});
  ui.catalog={observed_defaults:[old,fresh],observed_subject_examples:[],presets:[],observed_boundary:'test'};
  ui.recent=[{id:'old-job',result:{observed_id:old.id,control_receipt:'receipt',recipe:'effect'}}];
  ui.$('recent').value='old-job'; ui.showResult=async()=>{previews++;};
  return {ui,old,fresh,receipt,extra:()=>extraFetches,previews:()=>previews};
}
(async()=>{
  // A pending restore must not overwrite a later library choice.
  let s=setup(), pending=s.ui.$('recent').events.change();
  s.ui.$('preset').value='observed:'+s.fresh.id; await s.ui.loadPreset();
  s.receipt.resolve({kind:'source-controls',declared_recipe:s.old.recipe}); await pending;
  assert.equal(s.ui.observedId,s.fresh.id); assert.equal(JSON.parse(s.ui.$('recipe').value).label,'new');
  assert.equal(s.extra(),0); assert.equal(s.previews(),0);
  // A manually edited recipe and its source identity must survive an older restore.
  s=setup(); pending=s.ui.$('recent').events.change();
  s.ui.$('recipe').value='{"label":"manual"}'; s.ui.$('recipe').events.input();
  s.receipt.resolve({kind:'source-controls',declared_recipe:s.old.recipe}); await pending;
  assert.equal(JSON.parse(s.ui.$('recipe').value).label,'manual'); assert.equal(s.ui.observedId,null);
  assert.equal(s.extra(),0); assert.equal(s.previews(),0);
  // File.text() is asynchronous too; a superseded file must not replace the new choice.
  s=setup(); const file=deferred(), target={files:[{size:10,text:()=>file.promise}],value:'old.json'};
  pending=s.ui.$('file').events.change({target});
  s.ui.$('preset').value='observed:'+s.fresh.id; await s.ui.loadPreset();
  file.resolve('{"label":"file"}'); await pending;
  assert.equal(s.ui.observedId,s.fresh.id); assert.equal(JSON.parse(s.ui.$('recipe').value).label,'new');
  // Preserve the positive path: a current restore still commits and displays its result.
  s=setup(); pending=s.ui.$('recent').events.change();
  s.receipt.resolve({kind:'source-controls',declared_recipe:s.old.recipe}); await pending;
  assert.equal(s.ui.observedId,s.old.id); assert.equal(JSON.parse(s.ui.$('recipe').value).label,'old');
  assert.equal(s.extra(),1); assert.equal(s.previews(),1);
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
    result = subprocess.run(['node', '-e', script], cwd=Path(__file__).parents[1],
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
