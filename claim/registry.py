import json
import re
from collections import Counter
from pathlib import Path

from claim import dates, disclosure, events, files, record, site


def location(root: Path, claim_id: str) -> Path:
    if re.fullmatch(r"[0-9a-f]{64}", claim_id) is None:
        raise ValueError("invalid claim ID")
    return root / "claims" / claim_id[:2] / claim_id[2:4] / claim_id


def preserve_git_bytes(root: Path) -> None:
    path = root / ".gitattributes"
    if not path.exists():
        files.write_private(path, b"* -text\n")
    elif files.read_limited(path, 1024) != b"* -text\n":
        raise ValueError("registry .gitattributes must contain only '* -text'")


def read_claim(directory: Path) -> bytes:
    data = record.read_record(directory / "record.json")
    if record.record_id(data) != directory.name:
        raise ValueError("record ID mismatch")
    return data


def disclose(root: Path, claim_id: str, proof_url: str, salt: str) -> None:
    directory = location(root, claim_id)
    original = read_claim(directory)
    history = events.read(directory)
    if "disclosed" in history:
        raise ValueError("claim already disclosed")
    value = disclosure.check(original, proof_url, salt)
    files.write_private(
        directory / "disclosure.json", json.dumps(value).encode() + b"\n"
    )
    events.append(directory, "disclosed")


def withdraw(root: Path, claim_id: str) -> None:
    directory = location(root, claim_id)
    read_claim(directory)
    events.append(directory, "withdrawn")


def export_claim(directory: Path, output: Path) -> dict:
    data = read_claim(directory)
    date = dates.read(directory, data)
    history = events.read(directory)
    opening = disclosure.read(directory, data) if "disclosed" in history else None
    entry = record.load_record(data) | {
        "id": directory.name,
        "status": events.status(history),
        "events": history,
        "date": date,
        "disclosure": opening,
    }
    output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    files.create_private_directory(output)
    files.write_private(output / "record.json", data)
    if date is not None:
        files.write_private(output / "date.json", json.dumps(date).encode() + b"\n")
    for event in history:
        events.append(output, event)
    if opening is not None:
        files.write_private(
            output / "disclosure.json", json.dumps(opening).encode() + b"\n"
        )
    return entry


def bundle(root: Path, claim_id: str, output: Path) -> None:
    directory = location(root, claim_id)
    if "disclosed" not in events.read(directory):
        raise ValueError("claim has not been disclosed")
    data = read_claim(directory)
    opening = disclosure.read(directory, data)
    proof = disclosure.download(opening, data)
    export_claim(directory, output)
    files.write_private(output / "proof", proof)
    files.write_private(output / "salt", bytes.fromhex(opening["salt"]))
    preserve_git_bytes(output)


def export(root: Path, output: Path) -> None:
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("public output must be outside the registry")
    files.create_private_directory(output)
    preserve_git_bytes(output)
    entries = [
        export_claim(path, location(output, path.name))
        for path in sorted((root / "claims").glob("*/*/*"))
    ]
    counts = Counter(entry["authors"][0].lower() for entry in entries)
    index = {"claims": entries, "authors": dict(sorted(counts.items()))}
    files.write_private(output / "index.html", site.render(index).encode("utf-8"))
    files.write_private(output / ".nojekyll", b"")
    files.write_private(
        output / "index.json",
        json.dumps(index, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
    )


def accept(root: Path, source: Path) -> str:
    data = record.read_record(source)
    claim_id = record.record_id(data)
    directory = location(root, claim_id)
    root.mkdir(mode=0o700, exist_ok=True)
    preserve_git_bytes(root)
    directory.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    files.create_private_directory(directory)
    files.write_private(directory / "record.json", data)
    return claim_id
