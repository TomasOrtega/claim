import json
import re
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from urllib.parse import quote, unquote
from urllib.request import HTTPRedirectHandler, build_opener

from claim import commitment, files, record
from claim.limits import MAX_ARTIFACT_BYTES, MAX_RECORD_BYTES


def raw_url(url: str) -> str:
    match = re.fullmatch(
        r"https://github\.com/([A-Za-z0-9-]+)/([A-Za-z0-9_.-]+)/blob/"
        r"([0-9a-f]{40})/([^\s?#]+)",
        url,
    )
    if match is None or len(url) > 4096:
        raise ValueError("proof URL must be a GitHub file link pinned to a full commit")
    owner, repo, commit, path = match.groups()
    parts = [unquote(part) for part in path.split("/")]
    if repo in {".", ".."} or any(
        part in {"", ".", ".."} or re.search(r"[/\\\x00-\x1f\x7f]", part)
        for part in parts
    ):
        raise ValueError("invalid proof URL path")
    path = "/".join(quote(part, safe="") for part in parts)
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{commit}/{path}"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError("proof URL must not redirect")


def fetch(url: str) -> bytes:
    with build_opener(NoRedirect()).open(raw_url(url), timeout=30) as response:
        proof = response.read(MAX_ARTIFACT_BYTES + 1)
    if len(proof) > MAX_ARTIFACT_BYTES:
        raise ValueError("proof exceeds size limit")
    return proof


def salt_bytes(value: str) -> bytes:
    if re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError("salt must be 64 lowercase hexadecimal characters")
    return bytes.fromhex(value)


def validate(value: dict, data: bytes) -> None:
    if (
        not isinstance(value, dict)
        or value.keys() != {"proof_url", "salt", "proof_sha256", "verified_at"}
        or not all(isinstance(v, str) for v in value.values())
    ):
        raise ValueError("invalid disclosure fields")
    raw_url(value["proof_url"])
    salt = salt_bytes(value["salt"])
    if re.fullmatch(r"[0-9a-f]{64}", value["proof_sha256"]) is None:
        raise ValueError("invalid proof hash")
    digest = commitment.commit_digest(bytes.fromhex(value["proof_sha256"]), salt)
    if digest != record.load_record(data)["commitment"]:
        raise ValueError("disclosure does not match record")
    datetime.strptime(value["verified_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def check(data: bytes, url: str, salt: str) -> dict:
    opening_salt = salt_bytes(salt)
    proof = fetch(url)
    if not commitment.verify_opening(
        proof, opening_salt, record.load_record(data)["commitment"]
    ):
        raise ValueError("opening does not match record")
    return {
        "proof_url": url,
        "salt": salt,
        "proof_sha256": sha256(proof).hexdigest(),
        "verified_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def read(directory: Path, data: bytes) -> dict:
    value = json.loads(
        files.read_limited(directory / "disclosure.json", MAX_RECORD_BYTES)
    )
    validate(value, data)
    return value


def download(value: dict, data: bytes) -> bytes:
    validate(value, data)
    proof = fetch(value["proof_url"])
    if sha256(proof).hexdigest() != value["proof_sha256"]:
        raise ValueError("downloaded proof does not match disclosure")
    return proof
