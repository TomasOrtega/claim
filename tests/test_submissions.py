from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from claim import submissions

URL = "https://github.com/user-attachments/files/123/record.json"


def zip_files(contents):
    stream = BytesIO()
    with ZipFile(stream, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in contents.items():
            archive.writestr(name, data)
    return stream.getvalue()


def test_attachment():
    assert (
        submissions.attachment_url(f"### Record\n\n[record.json]({URL})", ".json")
        == URL
    )


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
        submissions.attachment_url(body, ".json")


def test_download_preserves_record(sealed, tmp_path, monkeypatch):
    data = (sealed / "record.json").read_bytes()
    monkeypatch.setattr(submissions, "urlopen", lambda *a, **kw: BytesIO(data))
    output = tmp_path / "submission"
    output.mkdir()
    submissions.download("submit", URL, output)
    assert (output / "record.json").read_bytes() == data
    assert list(output.iterdir()) == [output / "record.json"]


def test_oversized_download(tmp_path, monkeypatch):
    monkeypatch.setattr(submissions, "MAX_RECORD_BYTES", 4)
    monkeypatch.setattr(submissions, "urlopen", lambda *a, **kw: BytesIO(b"12345"))
    with pytest.raises(ValueError, match="size limit"):
        submissions.download("submit", URL, tmp_path)
    assert not list(tmp_path.iterdir())


def test_disclosure_zip(disclosed):
    contents = {p.name: p.read_bytes() for p in disclosed.iterdir()}
    assert submissions.disclosure_files(zip_files(contents)) == contents


@pytest.mark.parametrize(
    "extra", ["key", "opening.fernet", "../secret", "nested/proof"]
)
def test_disclosure_rejects_extra_files(disclosed, extra):
    contents = {p.name: p.read_bytes() for p in disclosed.iterdir()} | {extra: b"extra"}
    with pytest.raises(ValueError, match="ZIP must contain only"):
        submissions.disclosure_files(zip_files(contents))


@pytest.mark.parametrize("name", ["proof", "salt", "record.json"])
def test_disclosure_rejects_changed_opening(disclosed, name):
    contents = {p.name: p.read_bytes() for p in disclosed.iterdir()} | {
        name: b"changed"
    }
    with pytest.raises(ValueError):
        submissions.disclosure_files(zip_files(contents))


def test_disclosure_rejects_zip_bomb(disclosed, monkeypatch):
    monkeypatch.setattr(submissions, "MAX_ARTIFACT_BYTES", 16)
    contents = {p.name: p.read_bytes() for p in disclosed.iterdir()} | {
        "proof": bytes(100000)
    }
    with pytest.raises(ValueError, match="size limit"):
        submissions.disclosure_files(zip_files(contents))


def test_invalid_zip():
    with pytest.raises(ValueError, match="invalid disclosure ZIP"):
        submissions.disclosure_files(b"not a ZIP")
