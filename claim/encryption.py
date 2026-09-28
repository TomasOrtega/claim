from cryptography.fernet import Fernet


def new_key() -> bytes:
    return Fernet.generate_key()
