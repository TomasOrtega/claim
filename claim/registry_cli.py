from pathlib import Path

from claim import dates, registry


def add_commands(commands) -> None:
    date = commands.add_parser(
        "date-claims", help="record dates for a pushed registry commit"
    )
    date.add_argument("registry", type=Path)
    for argument in ("commit", "date", "run_url"):
        date.add_argument(argument)
    date.set_defaults(run=run)
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
    disclosure = commands.add_parser(
        "accept-disclosure", help="record a checked disclosure"
    )
    disclosure.add_argument("registry", type=Path)
    disclosure.add_argument("claim_id")
    disclosure.add_argument("source", type=Path)
    disclosure.set_defaults(run=run)
    for name in ("withdraw", "export-bundle"):
        command = commands.add_parser(name)
        command.add_argument("registry", type=Path)
        command.add_argument("claim_id")
        if name == "export-bundle":
            command.add_argument("output", type=Path)
        command.set_defaults(run=run)


def run(args) -> int:
    if args.command == "date-claims":
        print(dates.record_push(args.registry, args.commit, args.date, args.run_url))
    elif args.command == "accept":
        print(registry.accept(args.registry, args.source, args.receipt))
    elif args.command == "add-receipt":
        registry.add_receipt(args.registry, args.claim_id, args.receipt)
    elif args.command == "accept-disclosure":
        registry.disclose(args.registry, args.claim_id, args.source)
    elif args.command == "withdraw":
        registry.withdraw(args.registry, args.claim_id)
    elif args.command == "export-bundle":
        registry.bundle(args.registry, args.claim_id, args.output)
    else:
        registry.export(args.registry, args.output)
    return 0
