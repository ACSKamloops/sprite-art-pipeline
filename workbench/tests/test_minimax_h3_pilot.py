"""Offline checks for paid-submit safety and explicit native video boundaries."""
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

from PIL import Image
import pytest

SPEC = importlib.util.spec_from_file_location("minimax_h3_pilot", Path(__file__).parents[1] / "scripts/minimax_h3_pilot.py")
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


@pytest.fixture
def prepared(tmp_path):
    source = tmp_path / "hero.png"
    Image.new("RGBA", (256, 256), (30, 70, 150, 255)).save(source)
    prompt = tmp_path / "motion.txt"
    prompt.write_text("Walk in place.\n")
    research = tmp_path / "research"
    captured = research / "runtime/probes/minimax-walk/request.json"
    captured.parent.mkdir(parents=True)
    captured.write_text(json.dumps({"body": {"first_frame": {"base64": "not-used"}, "description": "old subject", "frame_count": 8, "seed": 123, "no_background": True, "enhance_prompt": False}}))
    run = tmp_path / "run"
    pilot.prepare(run, source, prompt, research)
    return run


def test_native_contract_does_not_forward_unsupported_pixel_controls(prepared):
    request = pilot.read_json(prepared / "request.json")
    assert set(request) == {"model", "content", "resolution", "duration", "ratio"}
    assert request["content"][0]["text"] == "Walk in place.\n"
    assert request["content"][1]["role"] == "first_frame"
    assert len(request["content"]) == 2
    assert pilot.read_json(prepared / "case.json")["same_subject_as_pixellab_capture"] is False


def test_tampered_input_rejected_before_any_paid_call(prepared):
    (prepared / "source.png").write_bytes(b"changed")
    with patch.object(pilot, "api_call") as call:
        with pytest.raises(ValueError, match="changed"):
            pilot.submit(prepared)
        call.assert_not_called()


def test_ambiguous_submit_cannot_be_retried(prepared):
    with patch.object(pilot, "credentials", return_value=("FAKE", {"kind": "test"})), patch.object(pilot, "api_call", return_value=({"http_status": None}, None)) as call:
        assert pilot.submit(prepared)["status"] == "submission-ambiguous"
        with pytest.raises(ValueError, match="already attempted"):
            pilot.submit(prepared)
        assert call.call_count == 1


def test_exclusive_claim_prevents_cross_process_duplicate(prepared):
    (prepared / ".submission.lock").touch()
    with patch.object(pilot, "credentials", return_value=("FAKE", {"kind": "test"})), patch.object(pilot, "api_call") as call:
        with pytest.raises(FileExistsError):
            pilot.submit(prepared)
        call.assert_not_called()


def test_successful_job_resumes_polling_without_another_post(prepared):
    with patch.object(pilot, "credentials", return_value=("FAKE", {"kind": "test"})), patch.object(pilot, "api_call", return_value=({"http_status": 200}, {"task_id": "123456"})) as call:
        assert pilot.submit(prepared)["status"] == "accepted"
        call.return_value = ({"http_status": 200}, {"task": {"id": "123456", "status": "succeeded", "content": {"url": "https://cdn.example/video.mp4"}}})
        assert pilot.poll(prepared)["status"] == "succeeded"
        assert call.call_args.args[:2] == ("GET", "/v2/query/video_generation/123456")
        assert (prepared / "completed-response.json").exists()


def test_secret_scrub_preserves_nonsecret_response_structure():
    value = {"error": {"message": "token SECRET rejected"}, "array": ["SECRET", 1]}
    assert "SECRET" not in json.dumps(pilot.scrub(value, "SECRET"))
    assert pilot.scrub(value, "SECRET")["array"][1] == 1


def test_secret_scrub_handles_decoded_unicode_escaped_keys_and_values():
    value = json.loads('{"\\u0053ECRET":{"nested":"\\u0053ECRET"},"safe":1}')
    sanitized = pilot.scrub(value, 'SECRET')
    assert 'SECRET' not in json.dumps(sanitized)
    assert sanitized['safe'] == 1


def test_api_rejects_arbitrary_destination_before_credentials_used():
    with pytest.raises(ValueError, match="Unexpected API path"):
        pilot.api_call("POST", "https://other.example/collect", "FAKE", {})


def test_download_never_sends_api_authorization(prepared):
    import io
    pilot.write_json(prepared / "completed-response.json", {"task": {"status": "succeeded", "content": {"url": "https://cdn.example/video.mp4?signature=not-a-real-secret"}}})
    opener = type("Opener", (), {})()
    seen = []
    def open_request(req, timeout):
        seen.append(req)
        return io.BytesIO(b"native-video-test-bytes")
    opener.open = open_request
    with patch.object(pilot.request, "build_opener", return_value=opener), patch.object(pilot, "credentials") as cred:
        pilot.download(prepared)
        cred.assert_not_called()
    assert not seen[0].has_header("Authorization")
    assert (prepared / "native-video.mp4").read_bytes() == b"native-video-test-bytes"


def test_download_rejects_non_https_result(prepared):
    pilot.write_json(prepared / "completed-response.json", {"status": "succeeded", "content": {"url": "http://cdn.example/video.mp4"}})
    with patch.object(pilot.request, "build_opener") as opener:
        with pytest.raises(ValueError, match="HTTPS"):
            pilot.download(prepared)
        opener.assert_not_called()


def test_local_video_samples_respect_variable_presentation_holds():
    from fractions import Fraction as F
    spec = importlib.util.spec_from_file_location("review_h3_video", Path(__file__).parents[1] / "scripts/review_h3_video.py")
    review = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(review)
    # Long first hold means four sample times intentionally select that frame.
    selected = review.select_frames([F(0), F(1, 2), F(3, 4)], F(1), 8)
    assert [i for _, i in selected] == [0, 0, 0, 0, 1, 1, 2, 2]
    assert selected[-1][0] == F(7, 8)
    with pytest.raises(ValueError):
        review.select_frames([F(0), F(0)], F(1), 8)
