import json

import pytest

from claim import events, registry, workflow


@pytest.mark.parametrize("name", ["proof", "salt", "record.json"])
def test_changed_disclosure(accepted, disclosed, name):
    (disclosed / name).write_bytes(b"changed")
    with pytest.raises(ValueError):
        registry.disclose(*accepted, disclosed)
    assert events.read(registry.location(*accepted)) == []


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


def test_export_disclosure(accepted, disclosed, tmp_path):
    registry.disclose(*accepted, disclosed)
    output = tmp_path / "public"
    entry = registry.export_claim(registry.location(*accepted), output)
    assert workflow.verify(output) == workflow.verify(disclosed)
    assert entry["events"] == ["disclosed"]


def test_withdrawn_disclosure(accepted, disclosed, tmp_path):
    registry.withdraw(*accepted)
    registry.disclose(*accepted, disclosed)
    registry.export(accepted[0], tmp_path / "site")
    index = json.loads((tmp_path / "site" / "index.json").read_bytes())
    assert index["authors"] == {"Alice": 1}
    assert index["claims"][0]["status"] == "withdrawn"
    assert index["claims"][0]["events"] == ["withdrawn", "disclosed"]


def test_disclose_claim(accepted, disclosed):
    root, claim_id = accepted
    original = registry.read_claim(registry.location(root, claim_id))
    registry.disclose(root, claim_id, disclosed)
    directory = registry.location(root, claim_id)
    assert events.read(directory) == ["disclosed"]
    assert registry.read_claim(directory) == original
    assert workflow.verify(directory / "disclosure") == workflow.verify(disclosed)
