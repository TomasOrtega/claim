import pytest

from claim import record, registry


@pytest.mark.parametrize("claim_id", ["../secret", "", "A" * 64, "a" * 63])
def test_invalid_claim_path(tmp_path, claim_id):
    with pytest.raises(ValueError, match="invalid claim ID"):
        registry.location(tmp_path, claim_id)


def test_accept(sealed, receipt, tmp_path):
    root = tmp_path / "registry"
    claim_id = registry.accept(root, sealed, receipt)
    entry = registry.location(root, claim_id)
    assert record.record_id((entry / "record.json").read_bytes()) == claim_id
    assert (entry / "opening.fernet").read_bytes() == (
        sealed / "opening.fernet"
    ).read_bytes()


def test_duplicate_intake(accepted, sealed, receipt):
    root, claim_id = accepted
    before = (registry.location(root, claim_id) / "opening.fernet").read_bytes()
    with pytest.raises(FileExistsError):
        registry.accept(root, sealed, receipt)
    assert (registry.location(root, claim_id) / "opening.fernet").read_bytes() == before


def test_invalid_intake_receipt(sealed, receipt, tmp_path):
    receipt.write_bytes(b"invalid")
    root = tmp_path / "registry"
    with pytest.raises(ValueError):
        registry.accept(root, sealed, receipt)
    assert not root.exists()


def test_changed_registered_record(accepted):
    root, claim_id = accepted
    directory = registry.location(root, claim_id)
    path = directory / "record.json"
    path.write_bytes(b" " + path.read_bytes())
    with pytest.raises(ValueError, match="record ID mismatch"):
        registry.read_claim(directory)


def test_submission(sealed):
    data, token = registry.read_submission(sealed)
    assert data == (sealed / "record.json").read_bytes()
    assert token == (sealed / "opening.fernet").read_bytes()


def test_submission_with_key(sealed, key):
    (sealed / "key").write_bytes(key)
    with pytest.raises(ValueError, match="unexpected submission files"):
        registry.read_submission(sealed)


def test_save_receipt(sealed, receipt, tmp_path):
    data = (sealed / "record.json").read_bytes()
    registry.save_receipt(tmp_path, data, receipt.read_bytes())
    paths = list((tmp_path / "timestamps").glob("*.ots"))
    assert len(paths) == 1 and paths[0].read_bytes() == receipt.read_bytes()
