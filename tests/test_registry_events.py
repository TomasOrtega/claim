import pytest

from claim import events, registry, workflow


@pytest.mark.parametrize("name", ["proof", "salt", "record.json"])
def test_changed_disclosure(accepted, disclosed, name):
    (disclosed / name).write_bytes(b"changed")
    with pytest.raises(ValueError):
        registry.disclose(*accepted, disclosed)
    assert events.read(registry.location(*accepted)) == []


def test_disclose_claim(accepted, disclosed):
    root, claim_id = accepted
    original = registry.read_claim(registry.location(root, claim_id))
    registry.disclose(root, claim_id, disclosed)
    directory = registry.location(root, claim_id)
    assert events.read(directory) == ["disclosed"]
    assert registry.read_claim(directory) == original
    assert workflow.verify(directory / "disclosure") == workflow.verify(disclosed)
