"""Integration contract checks for the isolated source-method UI fragment."""
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess

import pytest

WEB = Path(__file__).resolve().parents[1] / 'sprite_workbench' / 'web'


class Fragment(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = []
        self.scripts = []
        self.buttons = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'script':
            self.scripts.append(attrs)
        if tag == 'button':
            self.buttons.append(attrs)


def test_fragment_has_unique_namespaced_controls_and_all_js_literal_targets():
    fragment = Fragment((WEB / 'parity-lab.fragment.html').read_text())
    assert len(fragment.ids) == len(set(fragment.ids))
    assert all(ident.startswith('parity-') or ident == 'view-parity' for ident in fragment.ids)
    source = (WEB / 'parity-lab.js').read_text()
    literal_targets = set(re.findall(r"this\.\$\('([^']+)'\)", source))
    assert {'parity-' + target for target in literal_targets} <= set(fragment.ids)
    assert all(button.get('type') == 'button' for button in fragment.buttons)
    assert not fragment.scripts  # Host app owns script loading; no hidden runtime.


def test_only_source_local_invocations_and_upload_transport_are_exposed():
    source = (WEB / 'parity-lab.js').read_text()
    services = set(re.findall(r"this\.api\.invoke\('([^']+)'", source))
    assert services == {'local.parity.catalog', 'local.parity.palette', 'local.parity.pixels',
                        'local.parity.footprints', 'local.parity.paint'}
    assert 'fetch(' not in source
    assert not re.search(r'https?://|/provider/|local\.motion\.(submit|poll|download)', source)
    text = (WEB / 'parity-lab.fragment.html').read_text()
    for boundary in ['low-alpha', 'private', 'Linked cels', 'RGBA', 'hosted']:
        assert boundary in text


def test_css_does_not_define_unscoped_shared_rules():
    source = (WEB / 'parity-lab.css').read_text()
    # Every actual selector starts with the panel class, including mobile rules.
    selectors = re.findall(r'(?:^|[{}])\s*([^{}]+)\{', source)
    for group in selectors:
        if group.startswith('@media'):
            continue
        assert all(selector.strip().startswith('.parity-lab') for selector in group.split(','))


def test_javascript_parses_with_existing_node():
    node = shutil.which('node')
    if not node:
        pytest.skip('Node unavailable')
    result = subprocess.run([node, '--check', str(WEB / 'parity-lab.js')], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_actual_ui_preserves_inline_paint_receipt_and_distinct_footprint_id():
    node = shutil.which('node')
    if not node:
        pytest.skip('Node unavailable')
    # Exercise the actual class method. A real paint returns an inline guarded
    # transaction receipt, while palette/pixel receipts are artifact IDs.
    script = r"""
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const context={window:{}};vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),context);
const ui=Object.create(context.window.ParityLabUI.prototype),fields={};
ui.$=id=>fields[id]||(fields[id]={removeAttribute(){},replaceChildren(){}});
const result={receipt:{schema:'sprite-edit-receipt/v1',transaction:{operations:[]}},footprint:'a'.repeat(64),history:'b'.repeat(64),project:'c'.repeat(64)};
ui.show(result,'Paint');
assert(fields['receipt-id'].textContent.includes('Inline edit receipt'));
assert(fields['receipt-id'].textContent.includes('Footprint: '+result.footprint));
assert.deepStrictEqual(JSON.parse(fields['result-json'].textContent),result);
ui.show({receipt:'d'.repeat(64)},'Pixel method');
assert.strictEqual(fields['receipt-id'].textContent,'Receipt: '+'d'.repeat(64));
assert.throws(()=>ui.show({receipt:'malformed'},'Bad receipt'),/SHA256/);
"""
    result = subprocess.run([node, '-e', script, str(WEB / 'parity-lab.js')],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
