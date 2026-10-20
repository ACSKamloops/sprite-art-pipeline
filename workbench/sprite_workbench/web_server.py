"""Loopback-only HTTP control of real local workbench services."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
from pathlib import Path
import secrets
import threading
from urllib.parse import urlsplit, unquote

from .core import Store, ValidationError, UnsupportedCapability, canonical_json, digest, validate_id
from .capabilities import CapabilityRegistry
from .construction_services import bind_construction
from .jobs import JobManager
from .library import Library
from .pipeline import register_pipeline_job
from .readiness import analysis_catalog, readiness, register_verification, submit_verification

MAX_REQUEST = 4 * 1024 * 1024
MAX_UPLOAD = 32 * 1024 * 1024


class ControlServer(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, store, *, base_dir, port=8874, workers=2, enable_motion_provider=False):
        if type(port) is not int or not 0 <= port <= 65535:
            raise ValidationError('HTTP port must be 0..65535')
        if type(workers) is not int or not 1 <= workers <= 8:
            raise ValidationError('Web worker count must be 1..8')
        self.store = store
        self.base = Path(base_dir).resolve()
        self.base.mkdir(parents=True, exist_ok=True)
        self.token = secrets.token_urlsafe(32)
        self.motion_provider_enabled = enable_motion_provider is True
        from .readiness import source_fingerprint
        self.boot_fingerprint = source_fingerprint()
        self.slots = threading.BoundedSemaphore(12)
        self.manager = JobManager(store, workers=workers)
        try:
            self.registry = CapabilityRegistry()
            self.registry.bind_source_validation()
            self.registry.bind_library(Library(store))
            self.registry.bind_jobs(self.manager)
            bind_construction(self.registry, store, base_dir=self.base)
            from .source_vfx import bind_source_vfx
            from .source_workflow import register_source_job
            bind_source_vfx(self.registry, store)
            from .model_handoff import bind_models
            bind_models(self.registry, store, base_dir=self.base)
            from .selection_services import bind_selection
            from .studio_services import bind_studio
            bind_selection(self.registry, store, base_dir=self.base)
            bind_studio(self.registry, store, base_dir=self.base)
            from .motion_services import bind_motion
            bind_motion(self.registry, store, base_dir=self.base, live_provider_enabled=self.motion_provider_enabled)
            from .parity_services import bind_parity
            bind_parity(self.registry, store, base_dir=self.base)
            register_source_job(self.manager, before_run=self.require_current_source)
            register_pipeline_job(self.manager, base_dir=self.base, path_validator=self.validate_paths,
                                  before_run=self.require_current_source)
            register_verification(self.manager, base_dir=self.base, runtime_fingerprint=self.boot_fingerprint)
            super().__init__(('127.0.0.1', port), ControlHandler)
        except Exception:
            self.manager.close()
            raise

    @property
    def url(self):
        return f'http://127.0.0.1:{self.server_port}'

    def require_current_source(self):
        from .readiness import source_fingerprint
        if source_fingerprint() != self.boot_fingerprint:
            raise ValidationError('Restart the local controller after source changes before running plans')

    def validate_paths(self, value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {'path', 'directory', 'sidecar'} and isinstance(child, str):
                    candidate = Path(child)
                    candidate = candidate if candidate.is_absolute() else self.base / candidate
                    if not candidate.resolve().is_relative_to(self.base):
                        raise ValidationError('Web file paths must remain inside the configured project folder; upload external inputs')
                self.validate_paths(child)
        elif isinstance(value, list):
            for child in value:
                self.validate_paths(child)

    def server_close(self):
        try:
            super().server_close()
        finally:
            self.manager.close()


class ControlHandler(BaseHTTPRequestHandler):
    server_version = 'SpriteWorkbench/0.8'

    def log_message(self, *_args):
        pass  # Request bodies, local paths and session tokens are not access logs.

    def _send(self, status, body, content_type='application/json; charset=utf-8'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; "
                         "img-src 'self' blob: data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, value, status=200):
        self._send(status, canonical_json(value))

    def _origin(self, mutate=False):
        port = self.server.server_port
        hosts = {f'127.0.0.1:{port}', f'localhost:{port}'}
        if self.headers.get('Host', '') not in hosts:
            raise PermissionError('Invalid loopback Host header')
        origin = self.headers.get('Origin')
        if origin and origin not in {'http://' + h for h in hosts}:
            raise PermissionError('Cross-origin control requests are rejected')
        if mutate and not hmac.compare_digest(self.headers.get('X-Workbench-Token', ''), self.server.token):
            raise PermissionError('Missing or invalid local session token; reload this page')

    def _body(self, limit=MAX_REQUEST):
        if self.headers.get('Transfer-Encoding'):
            raise ValidationError('Chunked request bodies are unsupported')
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError as exc:
            raise ValidationError('Invalid body length') from exc
        if not 0 <= length <= limit:
            raise ValidationError('Request body exceeds the local size limit')
        self.connection.settimeout(15)
        raw = self.rfile.read(length)
        if len(raw) != length:
            raise ValidationError('Truncated request body')
        return raw

    def _request(self):
        if self.headers.get_content_type() != 'application/json':
            raise ValidationError('Control requests require application/json')
        value = json.loads(self._body() or b'{}')
        canonical_json(value)
        if not isinstance(value, dict):
            raise ValidationError('Request must be a JSON object')
        return value

    def _paths(self, value):
        """The web UI operates inside its explicitly configured project folder."""
        self.server.validate_paths(value)

    def _upload(self):
        raw = self._body(MAX_UPLOAD)
        if not raw:
            raise ValidationError('Choose a nonempty PNG, APNG or project JSON file')
        if raw.startswith(b'\x89PNG\r\n\x1a\n'):
            from .acquisition import import_image
            folder = self.server.base / 'uploads'
            if folder.is_symlink() or not folder.resolve().is_relative_to(self.server.base):
                raise ValidationError('Upload directory must stay inside the local project')
            folder.mkdir(exist_ok=True)
            path = folder / (digest(raw) + '.png')
            try:
                with path.open('xb') as stream:
                    stream.write(raw)
            except FileExistsError:
                if path.is_symlink() or path.read_bytes() != raw:
                    raise ValidationError('Existing upload path does not match its immutable bytes')
            return import_image(self.server.store, path)
        if len(raw) > 16 * 1024 * 1024:
            raise ValidationError('Project JSON upload exceeds 16MiB')
        from .construction import parse_project, save_project, create_history
        result = save_project(self.server.store, parse_project(raw))
        return {**result, **create_history(self.server.store, result['project'])}

    def _readiness(self):
        result = readiness(self.server.store, self.server.manager)
        restart = result['source_fingerprint'] != self.server.boot_fingerprint
        if restart:
            result.update(status='blocked', setup_ready=False, comparison_ready=False)
            result['blockers'].insert(0, {'id': 'restart-required', 'title': 'Restart the local controller',
                'reason': 'Source files changed after this server started; restart before verifying this version.'})
        result['restart_required'] = restart
        return result

    def _save_plan(self, request):
        from .pipeline import SUPPORTED
        if set(request) != {'plan'} or not isinstance(request['plan'], dict):
            raise ValidationError('Save one declared plan object')
        plan = request['plan']
        if set(plan) - {'version', 'name', 'steps'} or type(plan.get('version')) is not int or plan['version'] != 1:
            raise ValidationError('Plans require version 1, optional name and steps')
        steps = plan.get('steps')
        if not isinstance(steps, list) or not 1 <= len(steps) <= 128:
            raise ValidationError('A plan needs 1..128 steps')
        names = set()
        import re
        for step in steps:
            if (not isinstance(step, dict) or not isinstance(step.get('id'), str)
                    or not re.fullmatch('[A-Za-z][A-Za-z0-9_-]{0,63}', step['id'])
                    or step['id'] in names or step.get('action') not in SUPPORTED):
                raise ValidationError('Plan steps need unique names and implemented local actions')
            names.add(step['id'])
            if step['action'] in {'publish', 'promote'}:
                raise ValidationError('Queued web plans produce candidates; publish separately after review')
        self._paths(plan)
        return {'plan': self.server.store.put_json({'kind': 'pipeline-plan', 'version': 1, 'plan': plan})}

    def _get(self):
        self._origin()
        path = unquote(urlsplit(self.path).path)
        store = self.server.store
        if path in ('/', '/index.html', '/app.js', '/source-vfx.js', '/model-lab.js', '/studio.js', '/motion-lab.js', '/parity-lab.js', '/parity-lab.css', '/style.css'):
            asset = 'index.html' if path in ('/', '/index.html') else path[1:]
            mime = {'index.html': 'text/html; charset=utf-8', 'app.js': 'text/javascript; charset=utf-8',
                    'source-vfx.js': 'text/javascript; charset=utf-8',
                    'model-lab.js': 'text/javascript; charset=utf-8',
                    'studio.js': 'text/javascript; charset=utf-8',
                    'motion-lab.js': 'text/javascript; charset=utf-8',
                    'parity-lab.js': 'text/javascript; charset=utf-8',
                    'parity-lab.css': 'text/css; charset=utf-8',
                    'style.css': 'text/css; charset=utf-8'}[asset]
            self._send(200, (Path(__file__).resolve().parent / 'web' / asset).read_bytes(), mime)
        elif path == '/api/bootstrap':
            self._json({'csrf_token': self.server.token, 'workspace': {'path': str(self.server.base),
                        'store': str(store.path), 'analysis': 'Flows & grammar: complete retained evidence catalog'},
                        'readiness': self._readiness(),
                        'capabilities': self.server.registry.list()})
        elif path == '/favicon.ico':
            self._send(204, b'', 'image/x-icon')
        elif path == '/api/catalog':
            self._json(analysis_catalog())
        elif path == '/api/pixellab/source':
            self.server.require_current_source()
            from .source_workflow import source_catalog
            self._json(source_catalog())
        elif path == '/api/readiness':
            self._json(self._readiness())
        elif path == '/api/jobs':
            with store.connect() as db:
                ids = [row[0] for row in db.execute('SELECT id FROM local_jobs ORDER BY created DESC,id DESC LIMIT 100')]
            self._json([self.server.manager.get(ident) for ident in ids])
        elif path.startswith('/api/motion/media/') and path.endswith('.mp4'):
            from .motion_frames import MAX_MEDIA_BYTES
            ident = validate_id(path.removeprefix('/api/motion/media/')[:-4])
            doc = store.get_json(ident)
            if doc.get('kind') != 'motion-extraction' or doc.get('version') != 1:
                raise ValidationError('Media playback needs an admitted motion extraction')
            raw = store.get_bytes(doc['media'], max_bytes=MAX_MEDIA_BYTES)
            mime = 'video/mp4' if raw[4:8] == b'ftyp' else 'video/webm'
            self._send(200, raw, mime)
        elif path.startswith('/api/studio/download/') and path.endswith('.zip'):
            from .studio import download
            ident = validate_id(path.removeprefix('/api/studio/download/')[:-4])
            self._send(200, download(store, ident), 'application/zip')
        elif path.startswith('/api/project/'):
            from .construction import load_project, project_hash
            ident = validate_id(path.removeprefix('/api/project/'))
            document = load_project(store, ident)
            self._json({'project': ident, 'project_hash': project_hash(document), 'document': document})
        elif path.startswith('/api/artifact/'):
            self._json(store.get_json(validate_id(path.removeprefix('/api/artifact/'))))
        elif path.startswith('/api/raster/') and path.endswith('.png'):
            from .export import png_bytes
            ident = validate_id(path.removeprefix('/api/raster/')[:-4])
            self._send(200, png_bytes(store.get_raster(ident)), 'image/png')
        else:
            self._json({'status': 'not_found', 'error': {'reason': 'Unknown local endpoint'}}, 404)

    def _post(self):
        self._origin(mutate=True)
        path = urlsplit(self.path).path
        if path == '/api/motion/upload':
            from .motion_frames import MAX_MEDIA_BYTES
            raw = self._body(MAX_MEDIA_BYTES)
            if not raw:
                raise ValidationError('Choose a nonempty local video')
            # Byte admission is separate from an explicit bounded decoder call.
            self._json({'media':self.server.store.put_bytes(raw),'bytes':len(raw),'decoded':False})
            return
        if path == '/api/upload':
            self._json(self._upload())
            return
        request = self._request()
        if path == '/api/invoke':
            if set(request) - {'method', 'params'} or not isinstance(request.get('method'), str):
                raise ValidationError('Invocation needs method and params only')
            if not request['method'].startswith('local.'):
                raise UnsupportedCapability(request['method'], 'Vendor execution is unavailable; no remote forwarding')
            if request['method'].startswith(('local.pixellab.', 'local.models.', 'local.studio.', 'local.selection.', 'local.motion.', 'local.parity.')):
                self.server.require_current_source()
            params = request.get('params', {})
            if not isinstance(params, dict):
                raise ValidationError('Method parameters must be a JSON object')
            self._paths(params)
            result = self.server.registry.invoke(request['method'], params)
            self._json({'status': 'completed', 'result': result})
        elif path == '/api/verify':
            if request:
                raise ValidationError('Setup verification takes no fields')
            if self._readiness()['restart_required']:
                raise ValidationError('Restart the local controller after source changes before verifying setup')
            self._json({'status': 'completed', 'result': submit_verification(self.server.store, self.server.manager)})
        elif path == '/api/plan':
            self._json(self._save_plan(request))
        elif path == '/api/compare':
            gate = readiness(self.server.store, self.server.manager)
            self._json({'status': 'blocked', 'error': {'reason': 'Comparison prerequisites remain unresolved',
                                                     'blockers': gate['blockers']}}, 409)
        else:
            self._json({'status': 'not_found', 'error': {'reason': 'Unknown local endpoint'}}, 404)

    def _dispatch(self, action):
        if not self.server.slots.acquire(blocking=False):
            self._json({'status': 'busy', 'error': {'reason': 'Local request capacity reached'}}, 503)
            return
        try:
            action()
        except PermissionError as exc:
            self._json({'status': 'forbidden', 'error': {'reason': str(exc)}}, 403)
        except TimeoutError:
            self._json({'status': 'timeout', 'error': {'reason': 'Local operation timed out; inspect job status'}}, 408)
        except (ValidationError, OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError) as exc:
            error = exc.to_dict() if isinstance(exc, ValidationError) else {
                'status': 'validation_error', 'reason': 'Invalid local control input', 'exception_type': type(exc).__name__}
            self._json({'status': error['status'], 'error': error}, 400)
        finally:
            self.server.slots.release()

    def do_GET(self):
        self._dispatch(self._get)

    def do_POST(self):
        self._dispatch(self._post)


def serve_web(store, *, base_dir, port=8874, workers=2, enable_motion_provider=False):
    with ControlServer(store, base_dir=base_dir, port=port, workers=workers, enable_motion_provider=enable_motion_provider) as server:
        print(json.dumps({'event': 'ready', 'url': server.url, 'workspace': str(server.base),
                          'provider_forwarding': server.motion_provider_enabled}), flush=True)
        try:
            server.serve_forever(poll_interval=0.25)
        except KeyboardInterrupt:
            pass
    return 0
