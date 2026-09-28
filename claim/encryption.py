from cryptography.fernet import Fernet

_PREFIX = b"claim:opening:v1\0"


def new_key() -> bytes:
    return Fernet.generate_key()


def encrypt_opening(artifact: bytes, salt: bytes, key: bytes) -> bytes:
    if len(salt) != 32:
        raise ValueError("salt must be exactly 32 bytes")
    return Fernet(key).encrypt(_PREFIX + salt + artifact)


def decrypt_opening(token: bytes, key: bytes) -> tuple[bytes, bytes]:
    payload = Fernet(key).decrypt(token)
    offset = len(_PREFIX) + 32
    if not payload.startswith(_PREFIX) or len(payload) < offset:
        raise ValueError("invalid opening format")
    return payload[offset:], payload[len(_PREFIX) : offset]
