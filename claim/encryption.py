from cryptography.fernet import Fernet

_PREFIX = b"claim:opening:v1\0"


def new_key() -> bytes:
    return Fernet.generate_key()


def encrypt_opening(artifact: bytes, salt: bytes, key: bytes) -> bytes:
    if len(salt) != 32:
        raise ValueError("salt must be exactly 32 bytes")
    return Fernet(key).encrypt(_PREFIX + salt + artifact)
