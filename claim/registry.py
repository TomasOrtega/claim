import re
from hashlib import sha256
from pathlib import Path

from claim import encryption, files, record, timestamp
from claim.limits import MAX_OPENING_BYTES, MAX_TIMESTAMP_BYTES


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


def read_claim(directory: Path) -> bytes:
    data = record.read_record(directory / "record.json")
    if record.record_id(data) != directory.name:
        raise ValueError("record ID mismatch")
    return data


def read_receipts(directory: Path, data: bytes) -> dict[str, bytes]:
    proofs = {}
    for path in sorted((directory / "timestamps").iterdir()):
        proof = files.read_limited(path, MAX_TIMESTAMP_BYTES)
        if path.name != sha256(proof).hexdigest() + ".ots":
            raise ValueError("timestamp receipt ID mismatch")
        timestamp.parse_receipt(data, proof)
        proofs[path.name] = proof
    if not proofs:
        raise ValueError("missing timestamp receipt")
    return proofs


def save_receipt(directory: Path, data: bytes, proof: bytes) -> None:
    timestamp.parse_receipt(data, proof)
    receipts = directory / "timestamps"
    receipts.mkdir(mode=0o700, exist_ok=True)
    files.write_private(receipts / (sha256(proof).hexdigest() + ".ots"), proof)


def add_receipt(root: Path, claim_id: str, proof_path: Path) -> None:
    directory = location(root, claim_id)
    data = read_claim(directory)
    save_receipt(directory, data, files.read_limited(proof_path, MAX_TIMESTAMP_BYTES))


def accept(root: Path, source: Path, receipt: Path) -> str:
    files.require_external(root)
    data, token = read_submission(source)
    proof = files.read_limited(receipt, MAX_TIMESTAMP_BYTES)
    timestamp.parse_receipt(data, proof)
    claim_id = record.record_id(data)
    directory = location(root, claim_id)
    root.mkdir(mode=0o700, exist_ok=True)
    directory.parent.mkdir(mode=0o700, exist_ok=True)
    files.create_private_directory(directory)
    files.write_private(directory / "opening.fernet", token)
    save_receipt(directory, data, proof)
    files.write_private(directory / "record.json", data)
    return claim_id
