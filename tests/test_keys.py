import pytest
from cryptography.fernet import Fernet

from claim import keys


def test_save_key(tmp_path):
    path = tmp_path / "key"
    keys.save_key(path)
    assert Fernet(path.read_bytes()).encrypt(b"proof")


def test_load_key(tmp_path, key):
    path = tmp_path / "key"
    path.write_bytes(key)
    assert keys.load_key(path) == key


@pytest.mark.parametrize("data", [b"", b"bad key", b"a" * 45])
def test_invalid_key_file(tmp_path, data):
    path = tmp_path / "key"
    path.write_bytes(data)
    with pytest.raises(ValueError):
        keys.load_key(path)
