import json

import pytest
from test_dates import COMMIT, DATE, RUN

from claim import dates, record, registry


@pytest.mark.parametrize("claim_id", ["../secret", "", "A" * 64, "a" * 63])
def test_invalid_claim_path(tmp_path, claim_id):
    with pytest.raises(ValueError, match="invalid claim ID"):
        registry.location(tmp_path, claim_id)


def test_accept(sealed, tmp_path):
    root = tmp_path / "registry"
    claim_id = registry.accept(root, sealed / "record.json")
    entry = registry.location(root, claim_id)
    assert record.record_id((entry / "record.json").read_bytes()) == claim_id
    assert {path.name for path in entry.iterdir()} == {"record.json"}


def test_claims_use_hash_prefix_directories(accepted):
    root, claim_id = accepted
    path = root / "claims" / claim_id[:2] / claim_id[2:4] / claim_id
    assert registry.location(root, claim_id) == path
    assert (path / "record.json").is_file()


def test_public_export_uses_hash_prefixes(accepted, tmp_path):
    root, claim_id = accepted
    output = tmp_path / "site"
    registry.export(root, output)
    relative = f"claims/{claim_id[:2]}/{claim_id[2:4]}/{claim_id}/record.json"
    assert (output / relative).is_file()
    assert f"./{relative}" in (output / "index.html").read_text()


def test_duplicate_intake(accepted, sealed):
    root, claim_id = accepted
    before = registry.read_claim(registry.location(root, claim_id))
    with pytest.raises(FileExistsError):
        registry.accept(root, sealed / "record.json")
    assert registry.read_claim(registry.location(root, claim_id)) == before


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
        "disclosure",
    }
    assert not (tmp_path / "public" / "private-key").exists()


def test_export_registry(accepted, tmp_path):
    root, claim_id = accepted
    registry.export(root, tmp_path / "site")
    index = json.loads((tmp_path / "site" / "index.json").read_bytes())
    assert [entry["id"] for entry in index["claims"]] == [claim_id]
    assert index["authors"] == {"alice": 1}
    assert "Alice" in (tmp_path / "site" / "index.html").read_text()
    assert (tmp_path / "site" / ".nojekyll").exists()


def test_export_inside_registry(accepted):
    root, _ = accepted
    with pytest.raises(ValueError, match="outside the registry"):
        registry.export(root, root / "public")


def test_reject_encrypted_submission(sealed, tmp_path):
    with pytest.raises(ValueError):
        registry.accept(tmp_path / "registry", sealed / "opening.fernet")
    assert not (tmp_path / "registry").exists()


def test_export_date(accepted, tmp_path):
    directory = registry.location(*accepted)
    dates.save(directory, registry.read_claim(directory), DATE, COMMIT, RUN)
    output = tmp_path / "public"
    entry = registry.export_claim(directory, output)
    assert entry["date"]["recorded_at"] == DATE
    assert (output / "date.json").read_bytes() == (directory / "date.json").read_bytes()


def test_count_usernames_ignores_case(accepted, tmp_path):
    root, _ = accepted
    original = record.load_record(registry.read_claim(registry.location(*accepted)))
    source = tmp_path / "record.json"
    source.write_bytes(record.dump_record(original | {"authors": ["alice"]}))
    registry.accept(root, source)
    registry.export(root, tmp_path / "site")
    index = json.loads((tmp_path / "site" / "index.json").read_bytes())
    assert index["authors"] == {"alice": 2}
