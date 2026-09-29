from pathlib import Path

from claim import commitment, files, record, storage
from claim.limits import MAX_ARTIFACT_BYTES, MAX_RECORD_BYTES


def freeze(source: Path, opening: Path, key: bytes) -> str:
    artifact = files.read_limited(source, MAX_ARTIFACT_BYTES)
    salt = commitment.new_salt()
    storage.save_opening(opening, artifact, salt, key)
    digest = commitment.commit(artifact, salt)
    if not commitment.verify_opening(*storage.load_opening(opening, key), digest):
        raise ValueError("stored opening does not match commitment")
    return digest


def seal(source: Path, directory: Path, key: bytes, authors: list[str]) -> str:
    files.require_external(directory)
    files.create_private_directory(directory)
    digest = freeze(source, directory / "opening.fernet", key)
    data = record.dump_record(record.build_record(digest, authors))
    files.write_private(directory / "record.json", data)
    return digest


def check_opening(data: bytes, artifact: bytes, salt: bytes) -> str:
    public = record.load_record(data)
    if not commitment.verify_opening(artifact, salt, public["commitment"]):
        raise ValueError("opening does not match record")
    return public["commitment"]


def disclose(directory: Path, output: Path, key: bytes) -> None:
    data = files.read_limited(directory / "record.json", MAX_RECORD_BYTES)
    artifact, salt = storage.load_opening(directory / "opening.fernet", key)
    check_opening(data, artifact, salt)
    files.create_private_directory(output)
    for name, content in {"proof": artifact, "salt": salt, "record.json": data}.items():
        files.write_private(output / name, content)


def read_disclosure(directory: Path) -> dict[str, bytes]:
    limits = {"record.json": MAX_RECORD_BYTES, "proof": MAX_ARTIFACT_BYTES, "salt": 32}
    return {
        name: files.read_limited(directory / name, limit)
        for name, limit in limits.items()
    }


def verify(directory: Path) -> str:
    data = read_disclosure(directory)
    return check_opening(data["record.json"], data["proof"], data["salt"])
