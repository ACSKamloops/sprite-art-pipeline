"""Compare two public OpenAPI files without fetching or invoking their APIs."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def summary(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    result = {'json_type': type(value).__name__, 'canonical_value_sha256': digest(raw)}
    if isinstance(value, str):
        result.update(characters=len(value))
        if len(value) <= 300:
            result['value'] = value
    elif not isinstance(value, (dict, list)):
        result['value'] = value
    return result


def leaves(a, b, pointer=''):
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(a.keys() | b.keys()):
            p = pointer + '/' + key.replace('~', '~0').replace('/', '~1')
            if key not in a:
                yield {'pointer': p, 'change': 'added', 'new': summary(b[key])}
            elif key not in b:
                yield {'pointer': p, 'change': 'removed', 'old': summary(a[key])}
            else:
                yield from leaves(a[key], b[key], p)
    elif type(a) is not type(b) or a != b:
        yield {'pointer': pointer, 'change': 'changed', 'old': summary(a), 'new': summary(b)}


def compare(old_path, new_path):
    old_raw, new_raw = old_path.read_bytes(), new_path.read_bytes()
    a, b = json.loads(old_raw), json.loads(new_raw)
    verbs = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'}
    ops = lambda doc: {m.upper() + ' ' + p: v for p, item in doc['paths'].items()
                       for m, v in item.items() if m in verbs}
    x, y = ops(a), ops(b)
    sa, sb = a['components']['schemas'], b['components']['schemas']
    changed = sorted(k for k in x.keys() & y.keys() if x[k] != y[k])
    descriptions = []
    for name in changed:
        old, new = x[name].get('description', ''), y[name].get('description', '')
        descriptions.append({'operation': name,
            'removed_description_lines': [s[2:] for s in difflib.ndiff(old.splitlines(), new.splitlines()) if s.startswith('- ')],
            'added_description_lines': [s[2:] for s in difflib.ndiff(old.splitlines(), new.splitlines()) if s.startswith('+ ')]})
    return {'scope': 'Exact recursive JSON leaf diff of two pinned public OpenAPI documents; no runtime or handler/model recovery.',
        'previous_sha256': digest(old_raw), 'current_sha256': digest(new_raw),
        'previous_operations': len(x), 'current_operations': len(y),
        'added': sorted(y.keys() - x.keys()), 'removed': sorted(x.keys() - y.keys()), 'changed': changed,
        'previous_schema_count': len(sa), 'current_schema_count': len(sb),
        'schemas_added': sorted(sb.keys() - sa.keys()), 'schemas_removed': sorted(sa.keys() - sb.keys()),
        'schemas_changed': sorted(k for k in sa.keys() & sb.keys() if sa[k] != sb[k]),
        'whole_documents_json_equal': a == b, 'leaf_changes': list(leaves(a, b)),
        'operation_description_changes': descriptions,
        'current_semantic_additions': [
            {'id': 'normal-map', 'status': 'declared_private_method_unprovided',
             'summary': 'Async sprite/strip normal-map generation, same-size PNG, OpenGL/DirectX convention. Per-frame8..512px and<=32frames are prose; schema frames has minimum1 and no maximum.'},
            {'id': 'smart-target-palette', 'status': 'declared_private_method_unprovided',
             'summary': 'TargetPalette.smart boolean defaultsfalse. Beta single-image semantic object/material recoloring; explicit colors required by prose. AnimateWithTextV2Request explicitly refuses smart.'},
            {'id': 'pro-output-grid-size-buckets', 'status': 'declared_output_contract_not_runtime_verified',
             'summary': 'Generate-image-v2 and generate-with-style-v2 now document finer output-count buckets; historical42/85 thresholds are not current universal defaults.'},
            {'id': 'template-animation-batch-billing', 'status': 'declared_accounting_not_runtime_verified',
             'summary': 'Template animation cost description now bills batches above about100px; current prose includes3batchesat128,5at180,up tooneperclipframeat256. Not an observed debit or scheduler algorithm.'},
        ]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous', type=Path, required=True)
    parser.add_argument('--current', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = compare(args.previous, args.current)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in ['previous_operations', 'current_operations', 'added', 'changed', 'schemas_added', 'schemas_changed']}))
