import pytest

from claim import registry


@pytest.mark.parametrize("claim_id", ["../secret", "", "A" * 64, "a" * 63])
def test_invalid_claim_path(tmp_path, claim_id):
    with pytest.raises(ValueError, match="invalid claim ID"):
        registry.location(tmp_path, claim_id)


def test_submission(sealed):
    data, token = registry.read_submission(sealed)
    assert data == (sealed / "record.json").read_bytes()
    assert token == (sealed / "opening.fernet").read_bytes()
