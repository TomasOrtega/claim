import json
from pathlib import Path

from claim import lean_workflow


def add_commands(commands):
    command = commands.add_parser("check-lean", help="check a pinned Lean project ZIP")
    command.add_argument("source", type=Path)
    command.add_argument("module")
    command.add_argument("theorem")
    mode = command.add_mutually_exclusive_group(required=True)
    mode.add_argument("--image", help="trusted local Docker image ID")
    mode.add_argument(
        "--trusted-local",
        action="store_true",
        help="execute your own project's build on this computer",
    )
    command.set_defaults(run=run)


def run(args):
    print(
        json.dumps(
            lean_workflow.check(
                args.source,
                args.module,
                args.theorem,
                image=args.image,
                trusted_local=args.trusted_local,
            )
        )
    )
    return 0
