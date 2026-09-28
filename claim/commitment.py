from hashlib import sha256


def commit(artifact: bytes, salt: bytes) -> str:
    return sha256(b"claim:commit:v1\0" + salt + sha256(artifact).digest()).hexdigest()
