from claim import commitment, storage, workflow


def test_freeze(tmp_path, key):
    source, opening = tmp_path / "proof", tmp_path / "opening"
    source.write_bytes(b"proof\r\n\xff")
    digest = workflow.freeze(source, opening, key)
    assert commitment.verify_opening(*storage.load_opening(opening, key), digest)
