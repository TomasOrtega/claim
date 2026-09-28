from pathlib import Path

from claim import commitment, files, storage
from claim.limits import MAX_ARTIFACT_BYTES


def freeze(source: Path, opening: Path, key: bytes) -> str:
    artifact = files.read_limited(source, MAX_ARTIFACT_BYTES)
    salt = commitment.new_salt()
    storage.save_opening(opening, artifact, salt, key)
    return commitment.commit(artifact, salt)
