import json

import pytest

from claim import record, registry


@pytest.mark.parametrize("claim_id", ["../secret", "", "A" * 64, "a" * 63])
def test_invalid_claim_path(tmp_path, claim_id):
    with pytest.raises(ValueError, match="invalid claim ID"):
        registry.location(tmp_path, claim_id)


def test_accept(sealed, tmp_path):
    root = tmp_path / "registry"
    claim_id = registry.accept(root, sealed)
    entry = registry.location(root, claim_id)
    assert record.record_id((entry / "record.json").read_bytes()) == claim_id
    assert (entry / "opening.fernet").read_bytes() == (
        sealed / "opening.fernet"
    ).read_bytes()


def test_duplicate_intake(accepted, sealed):
    root, claim_id = accepted
    before = (registry.location(root, claim_id) / "opening.fernet").read_bytes()
    with pytest.raises(FileExistsError):
        registry.accept(root, sealed)
    assert (registry.location(root, claim_id) / "opening.fernet").read_bytes() == before


def test_changed_registered_record(accepted):
    root, claim_id = accepted
    directory = registry.location(root, claim_id)
    path = directory / "record.json"
    path.write_bytes(b" " + path.read_bytes())
    with pytest.raises(ValueError, match="record ID mismatch"):
        registry.read_claim(directory)


def test_public_export(accepted, tmp_path):
    output = tmp_path / "public"
    entry = registry.export_claim(registry.location(*accepted), output)
    assert entry["authors"] == ["Alice"] and entry["date"] is None
    assert {p.name for p in output.iterdir()} == {"record.json"}
    assert not (output / "opening.fernet").exists()


def test_export_allowlist(accepted, tmp_path, key):
    directory = registry.location(*accepted)
    (directory / "private-key").write_bytes(key)
    entry = registry.export_claim(directory, tmp_path / "public")
    assert set(entry) == {
        "version",
        "commitment",
        "authors",
        "id",
        "status",
        "date",
        "events",
    }
    assert not (tmp_path / "public" / "private-key").exists()


def test_export_registry(accepted, tmp_path):
    root, claim_id = accepted
    registry.export(root, tmp_path / "site")
    index = json.loads((tmp_path / "site" / "index.json").read_bytes())
    assert [entry["id"] for entry in index["claims"]] == [claim_id]
    assert index["authors"] == {"Alice": 1}
    assert "Alice" in (tmp_path / "site" / "index.html").read_text()
    assert (tmp_path / "site" / ".nojekyll").exists()


def test_export_inside_registry(accepted):
    root, _ = accepted
    with pytest.raises(ValueError, match="outside the registry"):
        registry.export(root, root / "public")


def test_submission(sealed):
    data, token = registry.read_submission(sealed)
    assert data == (sealed / "record.json").read_bytes()
    assert token == (sealed / "opening.fernet").read_bytes()


def test_submission_with_key(sealed, key):
    (sealed / "key").write_bytes(key)
    with pytest.raises(ValueError, match="unexpected submission files"):
        registry.read_submission(sealed)
