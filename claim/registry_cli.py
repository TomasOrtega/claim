from pathlib import Path

from claim import registry


def add_commands(commands) -> None:
    command = commands.add_parser("accept", help="accept an encrypted claim")
    for argument in ("registry", "source", "receipt"):
        command.add_argument(argument, type=Path)
    command.set_defaults(run=run)


def run(args) -> int:
    print(registry.accept(args.registry, args.source, args.receipt))
    return 0
