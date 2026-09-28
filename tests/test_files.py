from pathlib import Path

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


@pytest.mark.parametrize("size", [5, 64])
def test_oversized_file(tmp_path, size):
    (tmp_path / "source").write_bytes(bytes(size))
    with pytest.raises(ValueError, match="file exceeds size limit"):
        files.read_limited(tmp_path / "source", 4)


def test_negative_read_limit(tmp_path):
    with pytest.raises(ValueError, match="limit must be nonnegative"):
        files.read_limited(tmp_path / "missing", -1)


def test_checkout_destination():
    with pytest.raises(ValueError, match="outside the source checkout"):
        files.require_external(Path(__file__).parent / "private")


def test_checkout_symlink(tmp_path):
    link = tmp_path / "link"
    link.symlink_to(Path(__file__).parent, target_is_directory=True)
    with pytest.raises(ValueError, match="outside the source checkout"):
        files.require_external(link / "private")
