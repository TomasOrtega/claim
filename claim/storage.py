from pathlib import Path

from claim.encryption import encrypt_opening
from claim.files import write_private


def save_opening(path: Path, artifact: bytes, salt: bytes, key: bytes) -> None:
    write_private(path, encrypt_opening(artifact, salt, key))
