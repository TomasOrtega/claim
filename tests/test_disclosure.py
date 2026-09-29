from io import BytesIO
from urllib.request import Request

import pytest

from claim import disclosure

PROOF_URL = "https://github.com/alice/proofs/blob/" + "a" * 40 + "/first/proof.pdf"
RAW_URL = PROOF_URL.replace("github.com", "raw.githubusercontent.com").replace(
    "/blob/", "/"
)


def test_pinned_proof_url():
    assert disclosure.raw_url(PROOF_URL) == RAW_URL
    assert disclosure.raw_url(PROOF_URL.replace("proof.pdf", "my%20proof.pdf")) == (
        RAW_URL.replace("proof.pdf", "my%20proof.pdf")
    )


@pytest.mark.parametrize(
    "url",
    [
        PROOF_URL.replace("a" * 40, "main"),
        PROOF_URL.replace("a" * 40, "a" * 7),
        PROOF_URL + "?raw=1",
        PROOF_URL + "#L1",
        PROOF_URL.replace("github.com", "github.com.evil.example"),
        PROOF_URL.replace("https:", "http:"),
        PROOF_URL.replace("/first/", "/../"),
        PROOF_URL.replace("/first/", "/%2e%2e/"),
        PROOF_URL.replace("proof.pdf", "%2f..%2fmain%2fproof"),
        PROOF_URL.replace("proof.pdf", "%5cproof"),
        PROOF_URL.replace("proof.pdf", "%00proof"),
        "file:///etc/passwd",
    ],
)
def test_reject_unpinned_or_unsafe_url(url):
    with pytest.raises(ValueError, match="proof URL"):
        disclosure.raw_url(url)


def test_download_is_bounded(monkeypatch):
    class Opener:
        def open(self, url, timeout):
            assert url == RAW_URL and timeout == 30
            return BytesIO(b"12345")

    monkeypatch.setattr(disclosure, "build_opener", lambda *_: Opener())
    monkeypatch.setattr(disclosure, "MAX_ARTIFACT_BYTES", 4)
    with pytest.raises(ValueError, match="size limit"):
        disclosure.fetch(PROOF_URL)


def test_proof_redirects_are_rejected():
    handler = disclosure.NoRedirect()
    request = Request(RAW_URL)
    with pytest.raises(ValueError, match="must not redirect"):
        handler.http_error_302(
            request, BytesIO(b""), 302, "Found", {"location": "http://127.0.0.1/"}
        )
