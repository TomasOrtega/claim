from hashlib import sha256
from io import BytesIO
from types import SimpleNamespace

import pytest
from bitcoin import MainParams
from opentimestamps.core.notary import BitcoinBlockHeaderAttestation, PendingAttestation
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


@pytest.fixture
def anchored(pending):
    receipt = timestamp.parse_receipt(b"record", pending)
    receipt.timestamp.attestations.add(BitcoinBlockHeaderAttestation(100))
    context = BytesSerializationContext()
    receipt.serialize(context)
    return context.getbytes()


@pytest.fixture
def node(monkeypatch):
    header = SimpleNamespace(
        hashMerkleRoot=sha256(b"record").digest(), nTime=1234567890
    )
    node = SimpleNamespace(
        getblockhash=lambda _: MainParams.GENESIS_BLOCK.GetHash(),
        getblockheader=lambda _: header,
    )
    monkeypatch.setattr(timestamp, "Proxy", lambda **_: node, raising=False)
    return node


def test_parse_receipt(pending):
    assert timestamp.parse_receipt(b"record", pending).file_hash_op == OpSHA256()


def test_ots_client(pending, tmp_path):
    path = tmp_path / "receipt.ots"
    path.write_bytes(pending)
    timestamp.run_ots("info", path)


def test_ots_client_error(tmp_path):
    with pytest.raises(ValueError, match="timestamp info failed"):
        timestamp.run_ots("info", tmp_path / "missing")


def test_stamp(pending, monkeypatch):
    def provider(command, path):
        assert command == "stamp" and path.read_bytes() == b"record"
        path.with_suffix(".ots").write_bytes(pending)

    monkeypatch.setattr(timestamp, "run_ots", provider)
    assert timestamp.stamp(b"record") == pending


def test_pending(pending):
    assert timestamp.verify(b"record", pending) == {"status": "pending"}


def test_verified_anchor(anchored, node):
    assert timestamp.verify(b"record", anchored) == {
        "status": "verified",
        "unix_time": 1234567890,
        "block_height": 100,
    }


def test_wrong_merkle_root(anchored, node):
    node.getblockheader(b"hash").hashMerkleRoot = bytes(32)
    with pytest.raises(ValueError, match="does not match Bitcoin chain"):
        timestamp.verify(b"record", anchored)


def test_wrong_chain(anchored, node):
    node.getblockhash = lambda _: b"other chain"
    with pytest.raises(ValueError, match="Bitcoin mainnet node required"):
        timestamp.verify(b"record", anchored)


def test_unverified_anchor(anchored, monkeypatch):
    def unavailable(**_):
        raise ValueError("node unavailable")

    monkeypatch.setattr(timestamp, "Proxy", unavailable, raising=False)
    with pytest.raises(ValueError):
        timestamp.verify(b"record", anchored)


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
