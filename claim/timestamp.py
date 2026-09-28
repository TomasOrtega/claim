from hashlib import sha256

from opentimestamps.core.op import OpSHA256
from opentimestamps.core.serialize import (
    BytesDeserializationContext,
    DeserializationError,
)
from opentimestamps.core.timestamp import DetachedTimestampFile

from claim.limits import MAX_TIMESTAMP_BYTES


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
