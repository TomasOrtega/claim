from pathlib import Path


def add_commands(commands) -> None:
    for name in ("stamp", "upgrade", "verify-time"):
        command = commands.add_parser(name)
        command.add_argument("record", type=Path)
        if name != "stamp":
            command.add_argument("proof", type=Path)
        if name != "verify-time":
            command.add_argument("output", type=Path)
