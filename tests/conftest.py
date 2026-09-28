from io import BytesIO

import pytest
from opentimestamps.core.notary import PendingAttestation
from opentimestamps.core.op import OpSHA256
from opentimestamps.core.serialize import BytesSerializationContext
from opentimestamps.core.timestamp import DetachedTimestampFile

from claim.encryption import new_key
from claim.files import write_private
from claim.registry import accept
from claim.workflow import seal


@pytest.fixture
def key():
    return new_key()


@pytest.fixture
def key_file(tmp_path, key):
    path = tmp_path / "key"
    write_private(path, key)
    return path


@pytest.fixture
def sealed(tmp_path, key):
    source, directory = tmp_path / "proof", tmp_path / "sealed"
    source.write_bytes(b"proof\r\n\xff")
    seal(source, directory, key, ["Alice"])
    return directory


@pytest.fixture
def receipt(sealed, tmp_path):
    stamp = DetachedTimestampFile.from_fd(
        OpSHA256(), BytesIO((sealed / "record.json").read_bytes())
    )
    stamp.timestamp.attestations.add(
        PendingAttestation("https://a.pool.opentimestamps.org")
    )
    context = BytesSerializationContext()
    stamp.serialize(context)
    path = tmp_path / "record.ots"
    path.write_bytes(context.getbytes())
    return path


@pytest.fixture
def accepted(sealed, receipt, tmp_path):
    root = tmp_path / "registry"
    return root, accept(root, sealed, receipt)
