import pytest

from claim import record, registry, timestamp


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


def test_registry_receipts(accepted, receipt):
    directory = registry.location(*accepted)
    data = registry.read_claim(directory)
    proofs = registry.read_receipts(directory, data)
    assert list(proofs.values()) == [receipt.read_bytes()]


def test_receipt_append_is_exclusive(accepted, receipt):
    root, claim_id = accepted
    with pytest.raises(FileExistsError):
        registry.add_receipt(root, claim_id, receipt)
    assert (
        len(
            registry.read_receipts(
                registry.location(root, claim_id),
                (registry.location(root, claim_id) / "record.json").read_bytes(),
            )
        )
        == 1
    )


def test_altered_receipt_name(accepted):
    directory = registry.location(*accepted)
    path = next((directory / "timestamps").iterdir())
    path.rename(path.with_name("changed.ots"))
    with pytest.raises(ValueError, match="timestamp receipt ID mismatch"):
        registry.read_receipts(directory, registry.read_claim(directory))


def test_pending_registry_status(sealed, receipt):
    data = (sealed / "record.json").read_bytes()
    assert registry.timestamp_status(data, [receipt.read_bytes()]) == {
        "status": "pending"
    }


def test_failed_registry_status(monkeypatch):
    def fail(*_):
        raise OSError("private operator path")

    monkeypatch.setattr(timestamp, "verify", fail)
    assert registry.timestamp_status(b"record", [b"proof"]) == {"status": "failed"}


def test_earliest_timestamp(monkeypatch):
    monkeypatch.setattr(
        timestamp, "verify", lambda _, proof: {"status": "verified", "unix_time": proof}
    )
    assert registry.timestamp_status(b"record", [20, 10]) == {
        "status": "verified",
        "unix_time": 10,
    }


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
