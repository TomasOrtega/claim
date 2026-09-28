from io import BytesIO

import pytest
from opentimestamps.core.notary import PendingAttestation
from opentimestamps.core.op import OpSHA256
from opentimestamps.core.serialize import BytesSerializationContext
from opentimestamps.core.timestamp import DetachedTimestampFile


@pytest.fixture
def pending():
    receipt = DetachedTimestampFile.from_fd(OpSHA256(), BytesIO(b"record"))
    receipt.timestamp.attestations.add(
        PendingAttestation("https://a.pool.opentimestamps.org")
    )
    context = BytesSerializationContext()
    receipt.serialize(context)
    return context.getbytes()
