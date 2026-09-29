import json

import pytest

from claim import disclosure, events, registry, workflow


def test_changed_disclosure(accepted, disclosed, published):
    (disclosed / "proof").write_bytes(b"changed")
    with pytest.raises(ValueError):
        registry.disclose(*accepted, *published)
    assert events.read(registry.location(*accepted)) == []
    assert not (registry.location(*accepted) / "disclosure.json").exists()


def test_withdraw_claim(accepted):
    directory = registry.location(*accepted)
    original = registry.read_claim(directory)
    registry.withdraw(*accepted)
    assert events.read(directory) == ["withdrawn"]
    assert registry.read_claim(directory) == original


def test_export_withdrawal(accepted, tmp_path):
    registry.withdraw(*accepted)
    output = tmp_path / "public"
    entry = registry.export_claim(registry.location(*accepted), output)
    assert entry["status"] == "withdrawn" and entry["events"] == ["withdrawn"]
    assert events.read(output) == ["withdrawn"]


def test_export_disclosure(accepted, published, tmp_path, monkeypatch):
    registry.disclose(*accepted, *published)

    def offline(*args):
        raise AssertionError("site export must not download proofs")

    monkeypatch.setattr(disclosure, "fetch", offline)
    output = tmp_path / "public"
    entry = registry.export_claim(registry.location(*accepted), output)
    assert not (output / "proof").exists()
    assert entry["disclosure"]["proof_url"] == published[0]
    assert json.loads((output / "disclosure.json").read_bytes()) == entry["disclosure"]
    assert entry["events"] == ["disclosed"]


def test_withdrawn_disclosure(accepted, published, tmp_path):
    registry.withdraw(*accepted)
    registry.disclose(*accepted, *published)
    registry.export(accepted[0], tmp_path / "site")
    index = json.loads((tmp_path / "site" / "index.json").read_bytes())
    assert index["authors"] == {"alice": 1}
    assert index["claims"][0]["status"] == "withdrawn"
    assert index["claims"][0]["events"] == ["withdrawn", "disclosed"]


def test_corrupt_disclosed_storage(accepted, published, tmp_path):
    registry.disclose(*accepted, *published)
    directory = registry.location(*accepted)
    path = directory / "disclosure.json"
    value = json.loads(path.read_bytes()) | {"proof_sha256": "0" * 64}
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="disclosure does not match"):
        registry.export_claim(directory, tmp_path / "public")
    assert not (tmp_path / "public").exists()


def test_verification_bundle(accepted, disclosed, published, tmp_path):
    registry.disclose(*accepted, *published)
    registry.bundle(*accepted, tmp_path / "bundle")
    assert workflow.verify(tmp_path / "bundle") == workflow.verify(disclosed)
    assert not (tmp_path / "bundle" / "opening.fernet").exists()


def test_disclose_claim(accepted, published):
    root, claim_id = accepted
    original = registry.read_claim(registry.location(root, claim_id))
    registry.disclose(root, claim_id, *published)
    directory = registry.location(root, claim_id)
    assert events.read(directory) == ["disclosed"]
    assert registry.read_claim(directory) == original
    assert {p.name for p in directory.iterdir()} == {
        "record.json",
        "events",
        "disclosure.json",
    }
    assert disclosure.read(directory, original)["proof_url"] == published[0]


def test_changed_proof_blocks_bundle(accepted, disclosed, published, tmp_path):
    registry.disclose(*accepted, *published)
    (disclosed / "proof").write_bytes(b"changed")
    with pytest.raises(ValueError, match="downloaded proof does not match"):
        registry.bundle(*accepted, tmp_path / "bundle")
    assert not (tmp_path / "bundle").exists()


def test_duplicate_disclosure(accepted, published):
    registry.disclose(*accepted, *published)
    path = registry.location(*accepted) / "disclosure.json"
    original = path.read_bytes()
    with pytest.raises(ValueError, match="already disclosed"):
        registry.disclose(*accepted, *published)
    assert path.read_bytes() == original
