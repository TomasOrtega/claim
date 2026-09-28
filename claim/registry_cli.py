from pathlib import Path

from claim import registry


def add_commands(commands) -> None:
    command = commands.add_parser("accept", help="accept an encrypted claim")
    for argument in ("registry", "source", "receipt"):
        command.add_argument(argument, type=Path)
    command.set_defaults(run=run)
    export = commands.add_parser("export-index", help="export a public registry site")
    export.add_argument("registry", type=Path)
    export.add_argument("output", type=Path)
    export.set_defaults(run=run)


def run(args) -> int:
    if args.command == "accept":
        print(registry.accept(args.registry, args.source, args.receipt))
    else:
        registry.export(args.registry, args.output)
    return 0
