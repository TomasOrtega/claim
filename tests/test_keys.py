from cryptography.fernet import Fernet

from claim import keys


def test_save_key(tmp_path):
    path = tmp_path / "key"
    keys.save_key(path)
    assert Fernet(path.read_bytes()).encrypt(b"proof")
