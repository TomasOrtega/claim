import json
import re
from datetime import UTC, datetime
from pathlib import Path

from claim import files, record


def validate(value: dict, data: bytes) -> None:
    if not isinstance(value, dict) or value.keys() != {
        "record_sha256",
        "recorded_at",
        "commit",
        "run_url",
    }:
        raise ValueError("invalid claim date")
    if not all(isinstance(v, str) for v in value.values()):
        raise ValueError("invalid claim date fields")
    if value["record_sha256"] != record.record_id(data):
        raise ValueError("date does not match record")
    datetime.strptime(value["recorded_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    if re.fullmatch(r"[0-9a-f]{40}", value["commit"]) is None:
        raise ValueError("invalid dated commit")
    if (
        re.fullmatch(
            r"https://github\.com/[\w.-]+/[\w.-]+/actions/runs/[0-9]+", value["run_url"]
        )
        is None
    ):
        raise ValueError("invalid CI run URL")


def read(directory: Path, data: bytes) -> dict | None:
    path = directory / "date.json"
    if not path.exists():
        return None
    value = json.loads(files.read_limited(path, 4096))
    validate(value, data)
    return value


def save(
    directory: Path, data: bytes, recorded_at: str, commit: str, run_url: str
) -> bool:
    value = {
        "record_sha256": record.record_id(data),
        "recorded_at": recorded_at,
        "commit": commit,
        "run_url": run_url,
    }
    validate(value, data)
    if read(directory, data) is not None:
        return False
    files.write_private(directory / "date.json", json.dumps(value).encode() + b"\n")
    return True
