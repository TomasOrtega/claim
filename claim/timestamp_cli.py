import json
from pathlib import Path

from claim import timestamp
from claim.files import read_limited, write_private
from claim.limits import MAX_TIMESTAMP_BYTES
from claim.record import read_record


def add_commands(commands) -> None:
    for name in ("stamp", "upgrade", "verify-time"):
        command = commands.add_parser(name)
        command.add_argument("record", type=Path)
        if name != "stamp":
            command.add_argument("proof", type=Path)
        if name != "verify-time":
            command.add_argument("output", type=Path)


def run(args) -> int:
    data = read_record(args.record)
    if args.command == "stamp":
        write_private(args.output, timestamp.stamp(data))
    elif args.command == "upgrade":
        proof = read_limited(args.proof, MAX_TIMESTAMP_BYTES)
        write_private(args.output, timestamp.upgrade(data, proof))
    else:
        result = timestamp.verify(data, read_limited(args.proof, MAX_TIMESTAMP_BYTES))
        print(json.dumps(result))
        return 0 if result["status"] == "verified" else 1
    return 0
