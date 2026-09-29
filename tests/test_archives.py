from io import BytesIO
from zipfile import ZipFile, ZipInfo

import pytest

from claim.archives import unpack


def test_archive_expanded_limit(tmp_path, monkeypatch):
    monkeypatch.setattr("claim.archives.MAX_EXPANDED", 4)
    stream = BytesIO()
    with ZipFile(stream, "w") as archive:
        archive.writestr("proof", b"12345")
    with pytest.raises(ValueError, match="size limit"):
        unpack(stream.getvalue(), tmp_path)


@pytest.mark.parametrize(
    "name", ["../escape", "/escape", "a/../../escape", "a:b", "a//b", "a\\b"]
)
def test_unsafe_archive(tmp_path, name):
    stream = BytesIO()
    with ZipFile(stream, "w") as archive:
        archive.writestr(name, b"bad")
    with pytest.raises(ValueError, match="unsafe archive path"):
        unpack(stream.getvalue(), tmp_path)


def test_unpack_archive(tmp_path):
    stream = BytesIO()
    with ZipFile(stream, "w") as archive:
        archive.writestr("Proof.lean", "theorem result : True := True.intro")
    unpack(stream.getvalue(), tmp_path)
    assert (tmp_path / "Proof.lean").read_text().startswith("theorem")


def test_archive_symlink(tmp_path):
    stream, link = BytesIO(), ZipInfo("link")
    link.external_attr = 0o120777 << 16
    with ZipFile(stream, "w") as archive:
        archive.writestr(link, "../secret")
    with pytest.raises(ValueError, match="unsupported archive entry"):
        unpack(stream.getvalue(), tmp_path)
