from pathlib import Path

from claim import timestamp
from claim.files import write_private
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
    return 0
