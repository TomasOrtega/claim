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


@pytest.mark.parametrize("symlink", [False, True])
def test_no_overwrite(tmp_path, symlink):
    target = tmp_path / "original"
    target.write_bytes(b"original")
    path = tmp_path / "link" if symlink else target
    if symlink:
        path.symlink_to(target)
    with pytest.raises(FileExistsError):
        files.write_private(path, b"replacement")
    assert target.read_bytes() == b"original"


def test_bounded_read(tmp_path):
    (tmp_path / "source").write_bytes(b"abcd")
    assert files.read_limited(tmp_path / "source", 4) == b"abcd"
