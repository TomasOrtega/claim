import re
from pathlib import Path

from claim import encryption, files, record
from claim.limits import MAX_OPENING_BYTES


def location(root: Path, claim_id: str) -> Path:
    if re.fullmatch(r"[0-9a-f]{64}", claim_id) is None:
        raise ValueError("invalid claim ID")
    return root / "claims" / claim_id


def read_submission(source: Path) -> tuple[bytes, bytes]:
    data = record.read_record(source / "record.json")
    token = files.read_limited(source / "opening.fernet", MAX_OPENING_BYTES)
    encryption.validate_token(token)
    return data, token
