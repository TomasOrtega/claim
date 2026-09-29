import json
import re
from collections import Counter
from pathlib import Path

from claim import dates, encryption, events, files, record, site, workflow
from claim.limits import MAX_OPENING_BYTES


def location(root: Path, claim_id: str) -> Path:
    if re.fullmatch(r"[0-9a-f]{64}", claim_id) is None:
        raise ValueError("invalid claim ID")
    return root / "claims" / claim_id


def preserve_git_bytes(root: Path) -> None:
    path = root / ".gitattributes"
    if not path.exists():
        files.write_private(path, b"* -text\n")
    elif files.read_limited(path, 1024) != b"* -text\n":
        raise ValueError("registry .gitattributes must contain only '* -text'")


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


def disclose(root: Path, claim_id: str, source: Path) -> None:
    directory = location(root, claim_id)
    original = read_claim(directory)
    snapshot = workflow.read_disclosure(source)
    if snapshot["record.json"] != original:
        raise ValueError("disclosure record does not match registered record")
    workflow.check_opening(original, snapshot["proof"], snapshot["salt"])
    history = events.read(directory)
    if "disclosed" in history:
        raise ValueError("claim already disclosed")
    output = directory / "disclosure"
    files.create_private_directory(output)
    for name, data in snapshot.items():
        files.write_private(output / name, data)
    events.append(directory, "disclosed")


def withdraw(root: Path, claim_id: str) -> None:
    directory = location(root, claim_id)
    read_claim(directory)
    events.append(directory, "withdrawn")


def export_claim(directory: Path, output: Path) -> dict:
    data = read_claim(directory)
    date = dates.read(directory, data)
    history = events.read(directory)
    disclosure = (
        workflow.read_disclosure(directory / "disclosure")
        if "disclosed" in history
        else {}
    )
    if disclosure:
        if disclosure["record.json"] != data:
            raise ValueError("disclosure record does not match registered record")
        workflow.check_opening(data, disclosure["proof"], disclosure["salt"])
    entry = record.load_record(data) | {
        "id": directory.name,
        "status": events.status(history),
        "events": history,
        "date": date,
    }
    files.create_private_directory(output)
    files.write_private(output / "record.json", data)
    if date is not None:
        files.write_private(output / "date.json", json.dumps(date).encode() + b"\n")
    for event in history:
        events.append(output, event)
    for name in ("proof", "salt") if disclosure else ():
        files.write_private(output / name, disclosure[name])
    return entry


def bundle(root: Path, claim_id: str, output: Path) -> None:
    directory = location(root, claim_id)
    if "disclosed" not in events.read(directory):
        raise ValueError("claim has not been disclosed")
    export_claim(directory, output)
    preserve_git_bytes(output)


def export(root: Path, output: Path) -> None:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("public output must be outside the registry")
    files.create_private_directory(output)
    preserve_git_bytes(output)
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


def accept(root: Path, source: Path) -> str:
    files.require_external(root)
    data, token = read_submission(source)
    claim_id = record.record_id(data)
    directory = location(root, claim_id)
    root.mkdir(mode=0o700, exist_ok=True)
    preserve_git_bytes(root)
    directory.parent.mkdir(mode=0o700, exist_ok=True)
    files.create_private_directory(directory)
    files.write_private(directory / "opening.fernet", token)
    files.write_private(directory / "record.json", data)
    return claim_id
