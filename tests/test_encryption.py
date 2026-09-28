import pytest
from cryptography.fernet import Fernet

from claim import encryption

ARTIFACT = b"\x00proof\xff\r\n"
SALT = bytes(range(32))


@pytest.fixture
def key():
    return encryption.new_key()


def test_generated_key():
    assert Fernet(encryption.new_key()).encrypt(b"proof")
