import json
import re
from collections import Counter
from hashlib import sha256
from pathlib import Path

from bitcoin.rpc import JSONRPCError

from claim import encryption, files, record, site, timestamp
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


def timestamp_status(data: bytes, proofs) -> dict:
    results = []
    for proof in proofs:
        try:
            results.append(timestamp.verify(data, proof))
        except (OSError, ValueError, JSONRPCError):
            results.append({"status": "failed"})
    verified = [r for r in results if r["status"] == "verified"]
    if verified:
        return min(verified, key=lambda r: r["unix_time"])
    return {"status": "pending" if {"status": "pending"} in results else "failed"}


def export_claim(directory: Path, output: Path) -> dict:
    data = read_claim(directory)
    proofs = read_receipts(directory, data)
    entry = record.load_record(data) | {
        "id": directory.name,
        "status": "sealed",
        "timestamp": timestamp_status(data, proofs.values()),
        "receipts": list(proofs),
    }
    files.create_private_directory(output)
    files.write_private(output / "record.json", data)
    for name, proof in proofs.items():
        files.write_private(output / name, proof)
    return entry


def export(root: Path, output: Path) -> None:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("public output must be outside the registry")
    files.create_private_directory(output)
    entries = [
        export_claim(path, output / path.name)
        for path in sorted((root / "claims").iterdir())
    ]
    counts = Counter(name for entry in entries for name in entry["authors"])
    index = {"claims": entries, "authors": dict(sorted(counts.items()))}
    files.write_private(output / "index.html", site.render(index).encode("utf-8"))
    files.write_private(output / ".nojekyll", b"")
    files.write_private(
        output / "index.json",
        json.dumps(index, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
    )


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
