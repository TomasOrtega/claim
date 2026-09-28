from base64 import urlsafe_b64decode, urlsafe_b64encode

import pytest
from cryptography.fernet import Fernet, InvalidToken

from claim import encryption

ARTIFACT = b"\x00proof\xff\r\n"
SALT = bytes(range(32))


def test_generated_key():
    assert Fernet(encryption.new_key()).encrypt(b"proof")


def test_encrypted_framing(key):
    encryption.validate_token(encryption.encrypt_opening(ARTIFACT, SALT, key))
    with pytest.raises(ValueError):
        encryption.validate_token(key)


@pytest.mark.parametrize("data", [b"", b"plaintext proof", b"a" * 164, b"!" * 164])
def test_bad_encrypted_framing(data):
    with pytest.raises(ValueError):
        encryption.validate_token(data)


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


def test_tampered_ciphertext(key):
    token = encryption.encrypt_opening(ARTIFACT, SALT, key)
    raw = bytearray(urlsafe_b64decode(token))
    raw[30] ^= 1
    with pytest.raises(InvalidToken):
        encryption.decrypt_opening(urlsafe_b64encode(raw), key)


@pytest.mark.parametrize(
    "payload", [b"", b"claim:opening:v2\0" + SALT, b"claim:opening:v1\0" + SALT[:-1]]
)
def test_invalid_payload(key, payload):
    with pytest.raises(ValueError, match="invalid opening format"):
        encryption.decrypt_opening(Fernet(key).encrypt(payload), key)


def test_reused_key(key):
    for artifact in (b"", ARTIFACT, bytes(range(256))):
        token = encryption.encrypt_opening(artifact, SALT, key)
        assert encryption.decrypt_opening(token, key) == (artifact, SALT)


def test_fresh_encryption_randomness(key):
    assert encryption.encrypt_opening(
        ARTIFACT, SALT, key
    ) != encryption.encrypt_opening(ARTIFACT, SALT, key)


def test_oversized_artifact(key, monkeypatch):
    monkeypatch.setattr(encryption, "MAX_ARTIFACT_BYTES", 3, raising=False)
    with pytest.raises(ValueError, match="artifact exceeds size limit"):
        encryption.encrypt_opening(b"four", SALT, key)


def test_oversized_token(key, monkeypatch):
    monkeypatch.setattr(encryption, "MAX_OPENING_BYTES", 3, raising=False)
    with pytest.raises(ValueError, match="opening exceeds size limit"):
        encryption.decrypt_opening(b"four", key)


def test_oversized_payload(key, monkeypatch):
    token = Fernet(key).encrypt(b"claim:opening:v1\0" + SALT + b"four")
    monkeypatch.setattr(encryption, "MAX_ARTIFACT_BYTES", 3)
    with pytest.raises(ValueError, match="artifact exceeds size limit"):
        encryption.decrypt_opening(token, key)


def test_size_boundary(key, monkeypatch):
    monkeypatch.setattr(encryption, "MAX_ARTIFACT_BYTES", len(ARTIFACT))
    token = encryption.encrypt_opening(ARTIFACT, SALT, key)
    monkeypatch.setattr(encryption, "MAX_OPENING_BYTES", len(token))
    assert encryption.decrypt_opening(token, key) == (ARTIFACT, SALT)
