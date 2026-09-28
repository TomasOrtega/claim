from cryptography.fernet import Fernet

from claim import encryption


def test_generated_key():
    assert Fernet(encryption.new_key()).encrypt(b"proof")
