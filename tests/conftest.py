import pytest

from claim.encryption import new_key
from claim.files import write_private
from claim.registry import accept
from claim.workflow import disclose, seal


@pytest.fixture
def key():
    return new_key()


@pytest.fixture
def key_file(tmp_path, key):
    path = tmp_path / "key"
    write_private(path, key)
    return path


@pytest.fixture
def sealed(tmp_path, key):
    source, directory = tmp_path / "proof", tmp_path / "sealed"
    source.write_bytes(b"proof\r\n\xff")
    seal(source, directory, key, ["Alice"])
    return directory


@pytest.fixture
def accepted(sealed, tmp_path):
    root = tmp_path / "registry"
    return root, accept(root, sealed / "record.json")


@pytest.fixture
def disclosed(sealed, tmp_path, key):
    output = tmp_path / "disclosed"
    disclose(sealed, output, key)
    return output


@pytest.fixture
def published(disclosed, monkeypatch):
    from io import BytesIO

    from test_disclosure import PROOF_URL, RAW_URL

    from claim import disclosure

    class Opener:
        def open(self, url, timeout):
            assert url == RAW_URL and timeout == 30
            return BytesIO((disclosed / "proof").read_bytes())

    monkeypatch.setattr(disclosure, "build_opener", lambda *_: Opener())
    return PROOF_URL, (disclosed / "salt").read_bytes().hex()
