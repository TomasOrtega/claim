from io import BytesIO

import pytest
from test_disclosure import PROOF_URL

from claim import submissions

URL = "https://github.com/user-attachments/files/123/record.json"


def disclosure_body(claim_id, url, salt):
    return f"### Claim ID\n\n{claim_id}\n\n### Proof URL\n\n{url}\n\n### Salt\n\n{salt}"


def test_attachment():
    assert submissions.attachment_url(f"### Record\n\n[record.json]({URL})") == URL


@pytest.mark.parametrize(
    "body",
    [
        "",
        "file:///etc/passwd",
        "http://127.0.0.1/record.json",
        URL + "?url=other",
        URL.replace("github.com", "github.com.evil.example"),
        URL + " " + URL,
        URL.replace("/user-attachments/files/", "/example/registry/raw/main/"),
    ],
)
def test_reject_download_targets(body):
    with pytest.raises(ValueError, match="attach exactly one"):
        submissions.attachment_url(body)


def test_download_preserves_record(sealed, tmp_path, monkeypatch):
    data = (sealed / "record.json").read_bytes()
    monkeypatch.setattr(submissions, "urlopen", lambda *a, **kw: BytesIO(data))
    output = tmp_path / "submission"
    output.mkdir()
    submissions.download(URL, output)
    assert (output / "record.json").read_bytes() == data
    assert list(output.iterdir()) == [output / "record.json"]


def test_oversized_download(tmp_path, monkeypatch):
    monkeypatch.setattr(submissions, "MAX_RECORD_BYTES", 4)
    monkeypatch.setattr(submissions, "urlopen", lambda *a, **kw: BytesIO(b"12345"))
    with pytest.raises(ValueError, match="size limit"):
        submissions.download(URL, tmp_path)
    assert not list(tmp_path.iterdir())


def test_disclosure_form():
    claim_id, salt = "b" * 64, "c" * 64
    request = submissions.disclosure_request(disclosure_body(claim_id, PROOF_URL, salt))
    assert request == {"claim_id": claim_id, "proof_url": PROOF_URL, "salt": salt}


@pytest.mark.parametrize(
    "body",
    [
        "",
        URL,
        disclosure_body("b" * 63, PROOF_URL, "c" * 64),
        disclosure_body("b" * 64, PROOF_URL, "c" * 63),
        disclosure_body("b" * 64, PROOF_URL, "c" * 64) + "\n### Salt\n" + "d" * 64,
        disclosure_body("b" * 64, PROOF_URL, "c" * 64) + "\n" + URL,
    ],
)
def test_invalid_disclosure_form(body):
    with pytest.raises(ValueError):
        submissions.disclosure_request(body)
