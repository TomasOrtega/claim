from opentimestamps.core.serialize import BytesDeserializationContext
from opentimestamps.core.timestamp import DetachedTimestampFile

from claim.limits import MAX_TIMESTAMP_BYTES


def parse_receipt(data: bytes, proof: bytes) -> DetachedTimestampFile:
    if len(proof) > MAX_TIMESTAMP_BYTES:
        raise ValueError("timestamp exceeds size limit")
    return DetachedTimestampFile.deserialize(BytesDeserializationContext(proof))
