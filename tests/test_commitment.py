from hashlib import sha256

import pytest

from claim.commitment import commit, commit_digest, new_salt, verify_opening

ARTIFACT = b"theorem: 1 + 1 = 2\n"
SALT = bytes(range(32))
COMMITMENT = "d8c1f7f6682114f2e776e755c16f7f73d27ae7546c561ff9679a5ea5e35b25cb"


def test_commitment_vector():
    assert commit(ARTIFACT, SALT) == COMMITMENT


def test_commitment_from_digest():
    assert commit_digest(sha256(ARTIFACT).digest(), SALT) == COMMITMENT


@pytest.mark.parametrize("length", [0, 1, 31, 33, 64])
def test_invalid_salt_length(length):
    with pytest.raises(ValueError, match="salt must be exactly 32 bytes"):
        commit(ARTIFACT, bytes(length))


def test_new_salt(monkeypatch):
    monkeypatch.setattr(
        "claim.commitment.secrets.token_bytes", lambda n: bytes(range(n))
    )
    assert new_salt() == SALT


def test_verify_opening():
    assert verify_opening(ARTIFACT, SALT, COMMITMENT)


@pytest.mark.parametrize("offset", range(len(ARTIFACT)))
def test_reject_altered_artifact(offset):
    altered = bytearray(ARTIFACT)
    altered[offset] ^= 1
    assert not verify_opening(bytes(altered), SALT, COMMITMENT)


@pytest.mark.parametrize("offset", range(len(SALT)))
def test_reject_altered_salt(offset):
    altered = bytearray(SALT)
    altered[offset] ^= 1
    assert not verify_opening(ARTIFACT, bytes(altered), COMMITMENT)


def test_distinct_salts():
    assert commit(ARTIFACT, SALT) != commit(ARTIFACT, bytes(32))


def test_binary_vector():
    expected = "29e7f7bde6b5c74faa69652bfab7ddeeea00a5b15e74d2f35ae790edb4ddd206"
    assert commit(bytes(range(256)), SALT) == expected


def test_empty_vector():
    expected = "3032a9ffc8b79fcab4ad38b074cf833c8441ebb04be52bf6823ab43946f0477a"
    assert commit(b"", SALT) == expected


@pytest.mark.parametrize("ending", [b"", b"\r\n"])
def test_line_endings(ending):
    assert not verify_opening(ARTIFACT[:-1] + ending, SALT, COMMITMENT)


@pytest.mark.parametrize("value", ["", "0" * 64, COMMITMENT.upper(), "é" * 64])
def test_wrong_commitment(value):
    assert not verify_opening(ARTIFACT, SALT, value)


@pytest.mark.parametrize("length", [0, 31, 33])
def test_invalid_opening_salt_length(length):
    with pytest.raises(ValueError, match="salt must be exactly 32 bytes"):
        verify_opening(ARTIFACT, bytes(length), COMMITMENT)
