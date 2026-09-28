import pytest

from claim import encryption, storage


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
