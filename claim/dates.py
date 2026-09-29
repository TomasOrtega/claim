import json
import re
import subprocess
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


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, timeout=30, check=False
    )
    if result.returncode:
        raise ValueError("could not read pushed commit")
    return result.stdout


def record_push(
    root: Path, commit: str, recorded_at: str, run_url: str, before: str | None = None
) -> int:
    if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise ValueError("invalid pushed commit")
    if before is not None and re.fullmatch(r"[0-9a-f]{40}", before) is None:
        raise ValueError("invalid previous commit")
    if before == "0" * 40:
        before = git(root, "hash-object", "-t", "tree", "/dev/null").decode().strip()
    revisions = [before, commit] if before else [commit]
    paths = git(
        root,
        "diff-tree",
        "--root",
        "--diff-merges=first-parent",
        "--no-commit-id",
        "--no-renames",
        "--diff-filter=A",
        "-r",
        "--name-only",
        "-z",
        *revisions,
        "--",
        "claims",
    )
    count = 0
    for path in paths.decode().split("\0"):
        if not path.endswith("/record.json"):
            continue
        if (
            re.fullmatch(
                r"claims/([0-9a-f]{2})/([0-9a-f]{2})/\1\2[0-9a-f]{60}/record.json", path
            )
            is None
        ):
            raise ValueError("invalid claim path")
        directory = (root / path).parent
        data = git(root, "show", f"{commit}:{path}")
        if (
            record.record_id(data) != directory.name
            or record.read_record(directory / "record.json") != data
        ):
            raise ValueError("pushed record does not match registry")
        count += save(directory, data, recorded_at, commit, run_url)
    return count
