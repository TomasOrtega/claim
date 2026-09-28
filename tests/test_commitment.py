import pytest

from claim.commitment import commit, new_salt

ARTIFACT = b"theorem: 1 + 1 = 2\n"
SALT = bytes(range(32))
COMMITMENT = "d8c1f7f6682114f2e776e755c16f7f73d27ae7546c561ff9679a5ea5e35b25cb"


def test_commitment_vector():
    assert commit(ARTIFACT, SALT) == COMMITMENT


@pytest.mark.parametrize("length", [0, 1, 31, 33, 64])
def test_invalid_salt_length(length):
    with pytest.raises(ValueError, match="salt must be exactly 32 bytes"):
        commit(ARTIFACT, bytes(length))


def test_new_salt(monkeypatch):
    monkeypatch.setattr(
        "claim.commitment.secrets.token_bytes", lambda n: bytes(range(n))
    )
    assert new_salt() == SALT
