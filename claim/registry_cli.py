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
    receipt = commands.add_parser("add-receipt", help="append timestamp evidence")
    receipt.add_argument("registry", type=Path)
    receipt.add_argument("claim_id")
    receipt.add_argument("receipt", type=Path)
    receipt.set_defaults(run=run)


def run(args) -> int:
    if args.command == "accept":
        print(registry.accept(args.registry, args.source, args.receipt))
    elif args.command == "add-receipt":
        registry.add_receipt(args.registry, args.claim_id, args.receipt)
    else:
        registry.export(args.registry, args.output)
    return 0
