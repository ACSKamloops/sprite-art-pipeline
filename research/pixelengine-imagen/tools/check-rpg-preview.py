#!/usr/bin/env python3
"""Exercise legacy and expanded inspectors using a retained, explicitly aliased fixture.

No generation. The base six-action package remains unchanged. Aliases prove
runtime policy and resource transport only, never action-art coverage.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('rpg_builder', HERE/'build-rpg-preview.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def run(package, output, godot):
    if output.exists():
        raise ValueError('Fresh check output required')
    output.mkdir(parents=True)
    base = json.loads((package/'library.json').read_text())
    if set(base['actions']) != {'idle','walk','punch','cast','hurt','dodge'}:
        raise ValueError('Regression input must be the historical six-action package')
    original = builder.digest(package/'library.json')
    reports = []
    def build(source, target):
        result = builder.build(SimpleNamespace(package=source,output=target,config=None,godot=godot,check=True))
        reports.append(result)
    build(package,output/'legacy')
    fixture = output/'TEMPORARY-ALIASED-FIXTURE'
    shutil.copytree(package,fixture)
    by_id = {c['id']:c for c in base['clips']}
    for action in ['run','guard','stun','dash','jump','land','crouch','knockdown','get_up','death','interact']:
        for view in base['directions']:
            source = 'walk' if action == 'run' else 'idle'
            clip = copy.deepcopy(by_id[base['selected'][source+'_'+view]])
            clip.update(id='TEMPORARY-ALIAS-'+action+'-'+view,action=action,role='fixture-only',
                        review_status='TEMPORARY ALIAS: NO NEW ACTION ART',loop=action in ['run','guard','crouch'])
            base['clips'].append(clip)
            base['selected'][action+'_'+view] = clip['id']
        base['actions'].append(action)
    base['fixture_warning'] = 'TEMPORARY ALIASES ONLY: runtime and resource checks, no new action art.'
    builder.write(fixture/'library.json',base)
    (fixture/'TEMPORARY-ALIASES.txt').write_text(base['fixture_warning']+'\n')
    build(fixture,output/'expanded')
    # Mutations must fail before creating output; don't mask unrelated builder errors.
    rejection_checks = 0
    for name, mutate, expected in [
        ('missing-binding',lambda lib: lib['selected'].pop('run_N'),'Complete declared'),
        ('unknown-action',lambda lib: lib['actions'].append('teleport'),'Unsupported action'),
        ('duplicate-direction',lambda lib: lib['directions'].append('N'),'Eight unique'),
    ]:
        broken = copy.deepcopy(base)
        mutate(broken)
        builder.write(fixture/'library.json',broken)
        try:
            builder.build(SimpleNamespace(package=fixture,output=output/name,config=None,godot=godot,check=False))
        except ValueError as error:
            if expected not in str(error):
                raise
            rejection_checks += 1
        else:
            raise AssertionError('Invalid package accepted: '+name)
    builder.write(fixture/'library.json',base)
    assert builder.digest(package/'library.json') == original
    report = {'builds':reports,'negative_contract_checks':rejection_checks,
              'fixture_scope':base['fixture_warning'],'source_library_unchanged':True}
    builder.write(output/'REGRESSION-RESULT.json',report)
    print(json.dumps(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--godot',default='godot')
    args = parser.parse_args()
    run(args.package.resolve(),args.output.absolute(),args.godot)
