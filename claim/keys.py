from pathlib import Path

from cryptography.fernet import Fernet

from claim.encryption import new_key
from claim.files import read_limited, require_external, write_private


def save_key(path: Path) -> None:
    require_external(path)
    write_private(path, new_key())


def load_key(path: Path) -> bytes:
    key = read_limited(path, 44)
    Fernet(key)
    return key
