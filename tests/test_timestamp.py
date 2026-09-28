from io import BytesIO

import pytest
from opentimestamps.core.notary import PendingAttestation
from opentimestamps.core.op import OpSHA256
from opentimestamps.core.serialize import BytesSerializationContext
from opentimestamps.core.timestamp import DetachedTimestampFile

from claim import timestamp


@pytest.fixture
def pending():
    receipt = DetachedTimestampFile.from_fd(OpSHA256(), BytesIO(b"record"))
    receipt.timestamp.attestations.add(
        PendingAttestation("https://a.pool.opentimestamps.org")
    )
    context = BytesSerializationContext()
    receipt.serialize(context)
    return context.getbytes()


def test_parse_receipt(pending):
    assert timestamp.parse_receipt(b"record", pending).file_hash_op == OpSHA256()


def test_changed_record(pending):
    with pytest.raises(ValueError, match="timestamp does not match record"):
        timestamp.parse_receipt(b"changed", pending)


@pytest.mark.parametrize("proof", [b"", b"invalid"])
def test_invalid_receipt(proof):
    with pytest.raises(ValueError, match="invalid timestamp receipt"):
        timestamp.parse_receipt(b"record", proof)


def test_receipt_bounds(pending, monkeypatch):
    with pytest.raises(ValueError):
        timestamp.parse_receipt(b"record", pending + b"trailing")
    monkeypatch.setattr(timestamp, "MAX_TIMESTAMP_BYTES", len(pending) - 1)
    with pytest.raises(ValueError, match="timestamp exceeds size limit"):
        timestamp.parse_receipt(b"record", pending)
