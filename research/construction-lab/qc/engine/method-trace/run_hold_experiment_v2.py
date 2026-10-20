#!/usr/bin/env python3
"""Controlled one-byte frame-control experiment on a private derived ROM.
Original ROM remains byte-for-byte unchanged. Compare identical checkpoint/input.
"""
import argparse,ctypes as C,hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
SOURCE=Path('/home/astra/artifacts/rea-som-animation-2026-10-07/runtime')
sys.path.insert(0,str(SOURCE));import harness
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--variant',choices=['baseline','hold-field-1'],required=True);p.add_argument('--output',required=True);p.add_argument('--core',type=Path,required=True);args=p.parse_args()
    original=Path('/home/astra/artifacts/rea-som-test-2026-10-07/roms/Secret of Mana (USA).sfc');digest=sha(original)
    target=original;patch=None
    private=Path('/home/astra/artifacts/som-method-learning-private');private.mkdir(exist_ok=True,parents=True)
    if args.variant!='baseline':
        blob=bytearray(original.read_bytes());off=0x116a9a
        if blob[off]!=0x1c:raise ValueError('Unexpected normal Sword frame-control byte')
        blob[off]=0x19;target=private/'hold-field-1-v2-derived.sfc';target.write_bytes(blob)
        patch={'offset':off,'native_address':'D1:6A9A','before':0x1c,'after':0x19,'scope':'Frame control low-bit field; pose byteAB and all other ROM bytes unchanged'}
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    core=args.core.resolve();state=SOURCE/'cpu_staged3/weapon_owned.state'
    harness.CORE=str(core);em=harness.Emulator(str(target),out);em.load(state);em.cpu_trace=True;em.core.som_runtime_trace_enable(1)
    assert em.core.som_runtime_stage_weapon(9);em.run(180);assert not em.core.som_runtime_stage_active();em.run(8,['right']);em.run(20)
    rows=[]
    for i in range(60):
        keys=['b'] if i<2 else [];em.run(1,keys);raw=em.capture('hold_test');ram=C.string_at(em.ram,131072);b=ram[0xe000:0xe200];u=lambda n:int.from_bytes(b[n:n+2],'little')
        rows.append({'relative_tick':i,'source_tick':em.frame,'keys':keys,'raw':raw.name,'selected_generic':u(0x26)//2,'script_start':u(0x18),'script_pointer':u(0x16),'hold_counter':b[0x12],'frame_control':b[0x89],'mode':b[0x11], 'wram_sha256':sha(raw/'wram.bin'),'oam_sha256':sha(raw/'oam.bin')})
    em.trace.close();em.core.som_runtime_trace_enable(0);em.core.retro_unload_game();em.core.retro_deinit()
    assert sha(original)==digest
    report={'schema':'native-frame-control-experiment/v1','variant':args.variant,'original_rom_sha256':digest,'executed_rom_sha256':sha(target),'core_sha256':sha(core),'checkpoint_sha256':sha(state),'runner_sha256':sha(__file__),'fps':em.av.timing.fps,'patch':patch,'rows':rows,
        'original_unchanged':True,'trace_dropped':0,'trace_dropped_evidence':'Shared harness asserts dropped==0 after every retro_run before resetting trace ring; all268 monitored frames completed','setup':'Same checkpoint/native equip9/180ticks/8right/20neutral then2Bpress58release; no pose/HP/charge RAM writes',
        'limits':['One normal right Sword branch tested; does not prove all scripts or all frame-control values','Instrumented emulator provides selected watchpoints, not every executed instruction']}
    (out/'experiment.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'variant':args.variant,'ticks':len(rows),'output':str(out),'original_unchanged':True}))
if __name__=='__main__':main()
