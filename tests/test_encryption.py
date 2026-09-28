import pytest
from cryptography.fernet import Fernet, InvalidToken

from claim import encryption

ARTIFACT = b"\x00proof\xff\r\n"
SALT = bytes(range(32))


@pytest.fixture
def key():
    return encryption.new_key()


def test_generated_key():
    assert Fernet(encryption.new_key()).encrypt(b"proof")


def test_encrypt_opening(key):
    token = encryption.encrypt_opening(ARTIFACT, SALT, key)
    assert Fernet(key).decrypt(token) == b"claim:opening:v1\0" + SALT + ARTIFACT


@pytest.mark.parametrize("length", [0, 31, 33])
def test_invalid_salt(key, length):
    with pytest.raises(ValueError, match="salt must be exactly 32 bytes"):
        encryption.encrypt_opening(ARTIFACT, bytes(length), key)


def test_decrypt_opening(key):
    token = encryption.encrypt_opening(ARTIFACT, SALT, key)
    assert encryption.decrypt_opening(token, key) == (ARTIFACT, SALT)


def test_wrong_key(key):
    token = encryption.encrypt_opening(ARTIFACT, SALT, key)
    with pytest.raises(InvalidToken):
        encryption.decrypt_opening(token, encryption.new_key())
