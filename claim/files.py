import os
from pathlib import Path


def require_external(path: Path) -> None:
    if path.resolve().is_relative_to(Path(__file__).resolve().parents[1]):
        raise ValueError("private files must be outside the source checkout")


def create_private_directory(path: Path) -> None:
    path.mkdir(mode=0o700)


def write_private(path: Path, data: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)


def read_limited(path: Path, limit: int) -> bytes:
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("file exceeds size limit")
    return data
