import pytest

from claim import commitment, storage, workflow


def test_freeze(tmp_path, key):
    source, opening = tmp_path / "proof", tmp_path / "opening"
    source.write_bytes(b"proof\r\n\xff")
    digest = workflow.freeze(source, opening, key)
    assert commitment.verify_opening(*storage.load_opening(opening, key), digest)


def test_corrupt_saved_opening(tmp_path, key, monkeypatch):
    source = tmp_path / "proof"
    source.write_bytes(b"original")
    monkeypatch.setattr(storage, "load_opening", lambda *_: (b"corrupt", bytes(32)))
    with pytest.raises(ValueError, match="stored opening does not match"):
        workflow.freeze(source, tmp_path / "opening", key)
