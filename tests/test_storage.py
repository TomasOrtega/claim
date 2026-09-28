import pytest

from claim import encryption, files, storage


@pytest.fixture
def saved(tmp_path, key):
    path = tmp_path / "opening"
    storage.save_opening(path, b"proof", bytes(32), key)
    return path


def test_save_opening(tmp_path, key):
    path = tmp_path / "opening"
    storage.save_opening(path, b"proof", bytes(32), key)
    assert encryption.decrypt_opening(path.read_bytes(), key) == (b"proof", bytes(32))


def test_load_opening(saved, key):
    assert storage.load_opening(saved, key) == (b"proof", bytes(32))


def test_no_opening_overwrite(saved, key):
    with pytest.raises(FileExistsError):
        storage.save_opening(saved, b"replacement", bytes(32), key)
    assert storage.load_opening(saved, key) == (b"proof", bytes(32))


def test_oversized_opening_file(saved, key, monkeypatch):
    monkeypatch.setattr(storage, "MAX_OPENING_BYTES", saved.stat().st_size - 1)
    with pytest.raises(ValueError, match="file exceeds size limit"):
        storage.load_opening(saved, key)


def test_source_edits(tmp_path, key):
    source, frozen = tmp_path / "proof", tmp_path / "opening"
    source.write_bytes(b"original\r\n\x00\xff")
    storage.save_opening(frozen, files.read_limited(source, 100), bytes(32), key)
    source.write_bytes(b"revised\n")
    assert storage.load_opening(frozen, key) == (b"original\r\n\x00\xff", bytes(32))


def test_backup_recovery(saved, tmp_path, key):
    backup = tmp_path / "backup"
    files.create_private_directory(backup)
    files.write_private(backup / "key", key)
    files.write_private(backup / "opening", saved.read_bytes())
    saved.unlink()
    recovered_key = files.read_limited(backup / "key", 44)
    assert storage.load_opening(backup / "opening", recovered_key) == (
        b"proof",
        bytes(32),
    )
