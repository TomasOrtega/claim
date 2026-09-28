import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from bitcoin import MainParams
from bitcoin.rpc import Proxy
from opentimestamps.core.notary import BitcoinBlockHeaderAttestation, VerificationError
from opentimestamps.core.op import OpSHA256
from opentimestamps.core.serialize import (
    BytesDeserializationContext,
    DeserializationError,
)
from opentimestamps.core.timestamp import DetachedTimestampFile

from claim.files import read_limited
from claim.limits import MAX_TIMESTAMP_BYTES


def run_ots(command: str, path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from otsclient.ots import main; main()",
            "--no-cache",
            "--no-bitcoin",
            command,
            str(path),
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if result.returncode:
        raise ValueError(f"timestamp {command} failed: {result.stderr.strip()}")


def stamp(data: bytes) -> bytes:
    with TemporaryDirectory(prefix="claim-ots-") as directory:
        path = Path(directory) / "record"
        path.write_bytes(data)
        run_ots("stamp", path)
        proof = read_limited(path.with_suffix(".ots"), MAX_TIMESTAMP_BYTES)
        parse_receipt(data, proof)
        return proof


def parse_receipt(data: bytes, proof: bytes) -> DetachedTimestampFile:
    if len(proof) > MAX_TIMESTAMP_BYTES:
        raise ValueError("timestamp exceeds size limit")
    try:
        receipt = DetachedTimestampFile.deserialize(BytesDeserializationContext(proof))
    except DeserializationError as exc:
        raise ValueError("invalid timestamp receipt") from exc
    if (
        receipt.file_hash_op != OpSHA256()
        or receipt.file_digest != sha256(data).digest()
    ):
        raise ValueError("timestamp does not match record")
    return receipt


def verify(data: bytes, proof: bytes) -> dict:
    receipt = parse_receipt(data, proof)
    anchors = [
        (msg, a)
        for msg, a in receipt.timestamp.all_attestations()
        if isinstance(a, BitcoinBlockHeaderAttestation)
    ]
    if not anchors:
        return {"status": "pending"}
    node = Proxy(timeout=10)
    if node.getblockhash(0) != MainParams.GENESIS_BLOCK.GetHash():
        raise ValueError("Bitcoin mainnet node required")
    for message, attestation in sorted(anchors, key=lambda item: item[1].height):
        try:
            header = node.getblockheader(node.getblockhash(attestation.height))
            time = attestation.verify_against_blockheader(message, header)
        except (VerificationError, IndexError):
            continue
        return {
            "status": "verified",
            "unix_time": time,
            "block_height": attestation.height,
        }
    raise ValueError("timestamp does not match Bitcoin chain")
