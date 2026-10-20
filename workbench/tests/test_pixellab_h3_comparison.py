"""Offline protocol/evidence checks; fake credentials, supplied marker PNGs only."""
import base64
import importlib.util
import io
import json
from pathlib import Path
from unittest.mock import patch

from PIL import Image
import pytest

SPEC = importlib.util.spec_from_file_location('comparison', Path(__file__).parents[1]/'scripts/pixellab_h3_comparison.py')
pilot = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(pilot)


def png(colour):
    data = io.BytesIO(); Image.new('RGBA',(256,256),colour).save(data,format='PNG');return data.getvalue()


@pytest.fixture
def native(tmp_path):
    root = tmp_path/'native';root.mkdir();source=png((10,20,30,127));(root/'source.png').write_bytes(source)
    body={'model':'MiniMax-H3','content':[{'type':'text','text':'  Exact motion.\n'},
      {'type':'image_url','image_url':{'url':'data:image/png;base64,'+base64.b64encode(source).decode()},'role':'first_frame'}],
      'resolution':'768P','duration':4,'ratio':'adaptive'}
    pilot.write_json(root/'request.json',body);pilot.write_json(root/'case.json',{'input_hashes':{n:pilot.digest((root/n).read_bytes()) for n in ['source.png','request.json']}})
    return root


@pytest.fixture
def run(native,tmp_path):
    root=tmp_path/'run';pilot.prepare(root,native);return root


def test_matched_bytes_literal_prompt_contract_and_not_old_subject(run,native):
    payload=pilot.read_json(run/'request.json');pair=pilot.read_json(run/'pair.json')
    assert payload['description']=='  Exact motion.\n'
    assert payload['first_frame']=={'type':'base64','base64':pilot.read_json(native/'request.json')['content'][1]['image_url']['url'],'format':'png'}
    assert set(payload)=={'description','first_frame','frame_count','seed','no_background','enhance_prompt'}
    assert payload['frame_count']==16 and payload['seed']==123 and payload['no_background'] is True and payload['enhance_prompt'] is False
    assert pair['same_subject_as_old_pixellab_capture'] is False and pair['image_bytes_match'] and pair['literal_prompt_match']
    assert pair['checkpoint_or_private_conversion_parity'] is False


def test_native_input_tamper_rejected_before_preparation(native,tmp_path):
    (native/'source.png').write_bytes(b'tampered')
    with pytest.raises(ValueError,match='changed'):pilot.prepare(tmp_path/'unused',native)
    assert not (tmp_path/'unused').exists()


def test_comparison_tamper_rejects_before_credential_or_call(run):
    (run/'request.json').write_text('{}')
    with patch.object(pilot,'credential') as cred,patch.object(pilot,'_capture') as call:
        with pytest.raises(ValueError,match='changed'):pilot.submit(run)
        cred.assert_not_called();call.assert_not_called()


def test_paid_ambiguous_post_is_once_with_persistent_marker(run):
    def observe(*args):
        assert (run/'.submission.lock').exists()
        assert pilot.read_json(run/'state.json')['submission_attempts']==1
        return {'http_status':None,'transport':'failed-or-ambiguous'},None
    with patch.object(pilot,'credential',return_value='FAKE-SECRET'),patch.object(pilot,'_capture',side_effect=observe) as call:
        assert pilot.submit(run)['status']=='submission-ambiguous'
        with pytest.raises(ValueError,match='already attempted'):pilot.submit(run)
        assert call.call_count==1


def test_exclusive_cross_process_claim_blocks_call(run):
    (run/'.submission.lock').touch()
    with patch.object(pilot,'credential',return_value='FAKE'),patch.object(pilot,'_capture') as call:
        with pytest.raises(FileExistsError):pilot.submit(run)
        call.assert_not_called()


def test_accepted_job_poll_resumes_get_and_only_final_is_extractable(run):
    meta={'http_status':200,'transport':'response'}
    with patch.object(pilot,'credential',return_value='FAKE'),patch.object(pilot,'_capture',return_value=(meta,{'background_job_id':'job_123'})) as call:
        assert pilot.submit(run)['status']=='accepted'
        call.return_value=(meta,{'status':'running','last_response':{'images':['preview']}})
        assert pilot.poll(run)['status']=='running'
        assert call.call_args.args[1:3]==('GET','/v2/background-jobs/job_123')
        assert not (run/'completed-response.json').exists()
        with pytest.raises(FileNotFoundError):pilot.extract(run)


def test_nonfinal_file_is_never_extracted(run):
    pilot.write_json(run/'completed-response.json',{'status':'running','last_response':{'images':[]}})
    with pytest.raises(ValueError,match='final completed'):pilot.extract(run)
    assert not (run/'extracted').exists()


def test_all_final_pngs_retained_order_duplicate_reference_and_metrics(run):
    source=(run/'source.png').read_bytes();second=png((5,6,7,255));third=png((8,9,10,0))
    frames=[source,second,second,third]  # Deliberate duplicate must not be deduplicated.
    pilot.write_json(run/'completed-response.json',{'status':'completed','last_response':{'images':[{'base64':base64.b64encode(x).decode()} for x in frames]}})
    with patch.object(pilot,'credential') as cred,patch.object(pilot,'_capture') as call:
        result=pilot.extract(run);cred.assert_not_called();call.assert_not_called()
    assert result['actual']==4 and result['expected']==17 and result['reference0_byte_identity'] and result['reference0_decoded_identity']
    out=run/'extracted';manifest=pilot.read_json(out/'manifest.json')
    assert [r['index'] for r in manifest['frames']]==[0,1,2,3] and manifest['native_fps'] is None
    assert [(out/f'frame-{i:03d}.png').read_bytes() for i in range(4)]==frames
    assert manifest['frames'][0]['alpha']['partial']==256*256
    assert manifest['frames'][3]['alpha']['zero']==256*256
    assert (out/'generated-atlas.png').exists() and (out/'generated-contact-checker.png').exists()
    html=(out/'index.html').read_text();assert '2000/files.length' in html and 'not native FPS' in html
    assert manifest['pixellab_checkpoint_or_conversion_parity'] is False


def test_returned_reference_mismatch_is_recorded_not_rewritten(run):
    other=png((100,101,102,255));pilot.write_json(run/'completed-response.json',{'status':'completed','last_response':{'images':[{'base64':base64.b64encode(other).decode()}]}})
    result=pilot.extract(run)
    assert not result['reference0_byte_identity'] and not result['reference0_decoded_identity']
    assert (run/'extracted/frame-000.png').read_bytes()==other


class Response(io.BytesIO):
    code=200;headers={'Content-Type':'application/json','Set-Cookie':'should-never-persist'}


def test_producer_har_omits_credentials_headers_and_retains_actual_body_hash(run):
    raw=b'{"background_job_id":"job123","echo":"FAKE-SECRET"}'
    seen=[]
    def opened(req,timeout):seen.append(req);return Response(raw)
    opener=type('Opener',(),{'open':staticmethod(opened)})()
    payload=pilot.read_json(run/'request.json')
    with patch.object(pilot.request,'build_opener',return_value=opener):
        meta,body=pilot._capture(run,'POST','/v2/animate-pixminimax','FAKE-SECRET',payload)
    assert meta['http_status']==200 and body['echo']=='[REDACTED]'
    assert seen[0].get_header('Authorization')=='Bearer FAKE-SECRET'
    text=(run/'network.har').read_text();assert 'FAKE-SECRET' not in text and 'Set-Cookie' not in text and 'Bearer ' not in text
    entry=pilot.read_json(run/'network.har')['log']['entries'][0]
    assert entry['_response_body_sha256_before_scrub']==pilot.digest(raw)
    assert entry['_request_body_sha256']==pilot.digest(seen[0].data)
    assert entry['request']['postData']['text']==seen[0].data.decode()
    assert json.loads(entry['request']['postData']['text'])==payload
    assert set(entry['timings'].values())=={-1} and entry['time']>=0
    assert entry['request']['cookies']==entry['response']['cookies']==[]


def test_api_rejects_nonwhitelisted_paths_methods_without_network(run):
    with patch.object(pilot.request,'build_opener') as opener:
        for method,path in [('POST','/v2/balance'),('GET','https://other.example/key'),('GET','/v2/background-jobs/../escape')]:
            with pytest.raises(ValueError,match='Unexpected'):pilot._capture(run,method,path,'FAKE')
        opener.assert_not_called()


def test_api_no_redirect_handler_refuses_redirect():
    assert pilot.NoRedirect().redirect_request(None,None,302,'',{},'https://other.example') is None


def test_timeout_still_records_actual_attempt_without_secret_or_retry(run):
    opener=type('Opener',(),{'open':staticmethod(lambda *a,**k: (_ for _ in ()).throw(TimeoutError('do-not-copy-error-FAKE')))})()
    with patch.object(pilot.request,'build_opener',return_value=opener):
        meta,body=pilot._capture(run,'POST','/v2/animate-pixminimax','FAKE',pilot.read_json(run/'request.json'))
    assert meta['transport']=='failed-or-ambiguous' and meta['http_status'] is None
    har=pilot.read_json(run/'network.har');entry=har['log']['entries'][0]
    assert entry['_transport_error_type']=='TimeoutError' and entry['_response_body_sha256_scope']=='retained-prefix-only'
    assert 'FAKE' not in (run/'network.har').read_text()


def test_escaped_fake_token_scrubbed_in_json_keys_and_values_before_har_or_receipt(run):
    fake = 'FAKE_TOKEN'
    escaped = ''.join('\\u%04x' % ord(c) for c in fake)
    raw = ('{ "'+escaped+'": ["'+escaped+'", {"message":"prefix '+escaped+' suffix"}] }').encode()
    opener=type('Opener',(),{'open':staticmethod(lambda *a,**k:Response(raw))})()
    with patch.object(pilot.request,'build_opener',return_value=opener):
        _,body=pilot._capture(run,'POST','/v2/animate-pixminimax',fake,{})
    assert body == {'[REDACTED]': ['[REDACTED]', {'message':'prefix [REDACTED] suffix'}]}
    # This is exactly the object submit/poll may next persist as their receipt body.
    assert fake not in json.dumps(body)
    entry=pilot.read_json(run/'network.har')['log']['entries'][0]
    content=entry['response']['content']
    assert content['text_redacted'] is True
    assert json.loads(content['text']) == body
    assert content['text'] == json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False)
    assert escaped not in content['text'] and fake not in content['text']
    assert entry['_response_body_sha256_before_scrub'] == pilot.digest(raw)
    assert entry['_response_body_sha256_scope'] == 'complete-body'


def test_unredacted_response_preserves_exact_original_json_text(run):
    raw = b'{  "background_job_id" : "123", "array": [1, true], "escaped": "\\u263a" }\n'
    opener=type('Opener',(),{'open':staticmethod(lambda *a,**k:Response(raw))})()
    with patch.object(pilot.request,'build_opener',return_value=opener):
        _,body=pilot._capture(run,'POST','/v2/animate-pixminimax','FAKE_TOKEN',{})
    content=pilot.read_json(run/'network.har')['log']['entries'][0]['response']['content']
    assert body == json.loads(raw)
    assert content['text'] == raw.decode() and content['text_redacted'] is False


def test_non_json_literal_fake_secret_is_scrubbed():
    raw=b'upstream error FAKE_TOKEN'
    parsed,text,redacted=pilot.sanitize_response(raw,'FAKE_TOKEN')
    assert parsed['non_json_body'] is True and text == 'upstream error [REDACTED]' and redacted
