import pytest

from claim.encryption import new_key


@pytest.fixture
def key():
    return new_key()
