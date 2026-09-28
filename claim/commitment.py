import secrets
from hashlib import sha256


def commit(artifact: bytes, salt: bytes) -> str:
    if len(salt) != 32:
        raise ValueError("salt must be exactly 32 bytes")
    return sha256(b"claim:commit:v1\0" + salt + sha256(artifact).digest()).hexdigest()


def new_salt() -> bytes:
    return secrets.token_bytes(32)


def verify_opening(artifact: bytes, salt: bytes, commitment: str) -> bool:
    return commit(artifact, salt) == commitment
