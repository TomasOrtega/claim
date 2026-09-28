from pathlib import Path

from claim.encryption import new_key
from claim.files import require_external, write_private


def save_key(path: Path) -> None:
    require_external(path)
    write_private(path, new_key())
