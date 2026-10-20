"""Read-only local immutable-artifact correspondence and package inventory check."""
from pathlib import Path
import json
from fractions import Fraction
import urllib.request
import zipfile
import hashlib
import os
import sys
from urllib.parse import urlsplit

# CLI: python postflight.py [URL] [OUTPUT]; same env/defaults as browser replay.
base = (sys.argv[1] if len(sys.argv)>1 else os.environ.get('MOTION_QA_URL', 'http://127.0.0.1:8890')).rstrip('/')
folder = Path(sys.argv[2] if len(sys.argv)>2 else os.environ.get('MOTION_QA_OUTPUT', str(Path(__file__).resolve().parent))).resolve()
parsed = urlsplit(base)
if parsed.scheme != 'http' or parsed.hostname != '127.0.0.1' or parsed.path or parsed.query or parsed.fragment or parsed.username or parsed.password:
    raise RuntimeError('QA target must be a local127.0.0.1 HTTP origin')
if any((parent/'.git').exists() for parent in (folder, *folder.parents)):
    raise RuntimeError('QA output must be outside every Git checkout')
if (folder/'postflight-result.json').exists():
    raise RuntimeError('Existing postflight evidence is preserved; choose a fresh output folder')
report = json.loads((folder/'RESULT.json').read_text())
if report.get('target') != base:
    raise RuntimeError('Browser report target does not match postflight target')
def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def document(ident):
    require(len(ident) == 64 and all(c in '0123456789abcdef' for c in ident), 'Invalid artifact ID')
    return json.loads(urllib.request.urlopen(base+'/api/artifact/'+ident).read())
source = document(report['checks'][0]['native']['extraction'])
sequence = document(report['checks'][1]['state']['candidate'])
request = next(r['params'] for r in report['invocations'] if r['method'] == 'local.motion.sample')
require(len(sequence['frames']) == len(request['indices']) == 16, 'Sample count changed')
for frame, index, hold in zip(sequence['frames'], request['indices'], request['holds']):
    require(frame['raster'] == source['frames'][index]['raster'], 'Source index/raster changed')
    require(Fraction(*frame['duration']) == Fraction(*hold), 'Authored hold changed')
require(sequence['loop'] is False and sequence['play_count'] == 1, 'One-shot policy changed')
with zipfile.ZipFile(folder/'studio-package.zip') as archive:
    package = json.loads(archive.read('PACKAGE.json'))
    for row in package['files']:
        raw = archive.read(row['file'])
        require(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], 'ZIP file inventory mismatch')
result = {'status':'passed','selected_raster_correspondence':16,'authored_holds_exact':16,
          'source_indices':request['indices'],'zip_inventory_verified':len(package['files']),
          'scope':'local immutable JSON and ZIP readback; no provider operations'}
(folder/'postflight-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
