import json
import re
from hashlib import sha256
from pathlib import Path

from claim.files import read_limited
from claim.limits import MAX_RECORD_BYTES


def validate_record(record: dict) -> None:
    if not isinstance(record, dict) or record.keys() != {
        "version",
        "commitment",
        "authors",
    }:
        raise ValueError("invalid record fields")
    if type(record["version"]) is not int or record["version"] != 1:
        raise ValueError("unsupported record version")
    digest = record["commitment"]
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise ValueError("invalid commitment")
    authors = record["authors"]
    if not isinstance(authors, list) or len(authors) != 1:
        raise ValueError("record must have exactly one GitHub author")
    if any(not isinstance(name, str) or not name.strip() for name in authors):
        raise ValueError("invalid author name")


def build_record(commitment: str, authors: list[str]) -> dict:
    record = {"version": 1, "commitment": commitment, "authors": authors}
    validate_record(record)
    return record | {"authors": authors.copy()}


def dump_record(record: dict) -> bytes:
    validate_record(record)
    text = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    data = (text + "\n").encode("utf-8")
    if len(data) > MAX_RECORD_BYTES:
        raise ValueError("record exceeds size limit")
    return data


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    record = dict(pairs)
    if len(record) != len(pairs):
        raise ValueError("duplicate JSON key")
    return record


def load_record(data: bytes) -> dict:
    if len(data) > MAX_RECORD_BYTES:
        raise ValueError("record exceeds size limit")
    record = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object)
    validate_record(record)
    return record


def read_record(path: Path) -> bytes:
    data = read_limited(path, MAX_RECORD_BYTES)
    load_record(data)
    return data


def record_id(data: bytes) -> str:
    load_record(data)
    return sha256(data).hexdigest()
