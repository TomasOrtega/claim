from pathlib import Path

from claim.encryption import decrypt_opening, encrypt_opening
from claim.files import read_limited, write_private
from claim.limits import MAX_OPENING_BYTES


def save_opening(path: Path, artifact: bytes, salt: bytes, key: bytes) -> None:
    write_private(path, encrypt_opening(artifact, salt, key))


def load_opening(path: Path, key: bytes) -> tuple[bytes, bytes]:
    return decrypt_opening(read_limited(path, MAX_OPENING_BYTES), key)
