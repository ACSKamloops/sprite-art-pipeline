"""Adversarial capture completeness checks; no network or real credentials."""
import importlib.util
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location('verify_pair', Path(__file__).parents[1] / 'scripts/verify_h3_pixellab_comparison.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


@pytest.fixture
def capture():
    post = {'request': {'method': 'POST'}, 'response': {'content': {'text': '{}'}}}
    pending = {'request': {'method': 'GET'}, 'response': {'content': {'text': '{"status":"processing"}'}}}
    completed = {'request': {'method': 'GET'}, 'response': {'content': {'text': '{"status":"completed"}'}}}
    har = [post, pending, completed]
    records = [{'ordinal': i, 'reported': har[i]} for i in [0, 2]]
    return har, records


def test_pending_poll_may_be_unselected_while_both_proof_records_are_bound(capture):
    har, records = capture
    assert verify.captured_pair(har, records) == (har[0], har[2])


@pytest.mark.parametrize('hidden_record', [0, 2])
def test_hidden_extra_submission_or_completed_response_is_rejected(capture, hidden_record):
    har, records = capture
    har.append(har[hidden_record])
    with pytest.raises(ValueError, match='Full HAR'):
        verify.captured_pair(har, records)


def test_projection_missing_completed_result_is_rejected(capture):
    har, records = capture
    with pytest.raises(ValueError, match='selection omits'):
        verify.captured_pair(har, records[:1])


def test_rea_projection_with_modified_payload_is_rejected(capture):
    har, records = capture
    records[0]['reported'] = {'request': {'method': 'POST'}, 'response': {'content': {'text': 'different'}}}
    with pytest.raises(ValueError, match='mismatch'):
        verify.captured_pair(har, records)
