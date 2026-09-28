import pytest

from claim import files


def test_private_directory(tmp_path):
    path = tmp_path / "private"
    files.create_private_directory(path)
    assert path.stat().st_mode & 0o777 == 0o700


def test_existing_directory(tmp_path):
    with pytest.raises(FileExistsError):
        files.create_private_directory(tmp_path)


def test_private_file(tmp_path):
    files.write_private(tmp_path / "secret", b"private")
    assert (tmp_path / "secret").read_bytes() == b"private"


def test_private_file_permissions(tmp_path):
    files.write_private(tmp_path / "secret", b"private")
    assert (tmp_path / "secret").stat().st_mode & 0o777 == 0o600
