from claim import events, registry, workflow


def test_disclose_claim(accepted, disclosed):
    root, claim_id = accepted
    original = registry.read_claim(registry.location(root, claim_id))
    registry.disclose(root, claim_id, disclosed)
    directory = registry.location(root, claim_id)
    assert events.read(directory) == ["disclosed"]
    assert registry.read_claim(directory) == original
    assert workflow.verify(directory / "disclosure") == workflow.verify(disclosed)
