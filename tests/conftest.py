import pytest

from claim.encryption import new_key
from claim.workflow import seal


@pytest.fixture
def key():
    return new_key()


@pytest.fixture
def sealed(tmp_path, key):
    source, directory = tmp_path / "proof", tmp_path / "sealed"
    source.write_bytes(b"proof\r\n\xff")
    seal(source, directory, key, ["Alice"])
    return directory
