import re
from hashlib import sha256
from pathlib import Path

from claim import encryption, files, record, timestamp
from claim.limits import MAX_OPENING_BYTES


def location(root: Path, claim_id: str) -> Path:
    if re.fullmatch(r"[0-9a-f]{64}", claim_id) is None:
        raise ValueError("invalid claim ID")
    return root / "claims" / claim_id


def read_submission(source: Path) -> tuple[bytes, bytes]:
    if {p.name for p in source.iterdir()} != {"record.json", "opening.fernet"}:
        raise ValueError("unexpected submission files")
    data = record.read_record(source / "record.json")
    token = files.read_limited(source / "opening.fernet", MAX_OPENING_BYTES)
    encryption.validate_token(token)
    return data, token


def save_receipt(directory: Path, data: bytes, proof: bytes) -> None:
    timestamp.parse_receipt(data, proof)
    receipts = directory / "timestamps"
    receipts.mkdir(mode=0o700, exist_ok=True)
    files.write_private(receipts / (sha256(proof).hexdigest() + ".ots"), proof)
