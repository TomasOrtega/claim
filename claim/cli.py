import argparse
from pathlib import Path

from cryptography.fernet import InvalidToken

from claim import timestamp_cli, workflow
from claim.keys import load_key, save_key


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="claim")
    commands = parser.add_subparsers(dest="command", required=True)
    keygen = commands.add_parser("keygen", help="generate an encryption key")
    keygen.add_argument("path", type=Path)
    seal = commands.add_parser("seal", help="save an encrypted claim")
    seal.add_argument("source", type=Path)
    seal.add_argument("directory", type=Path)
    seal.add_argument("--key", type=Path, required=True)
    seal.add_argument("--author", action="append", required=True)
    disclose = commands.add_parser("disclose", help="export a proof and salt")
    disclose.add_argument("directory", type=Path)
    disclose.add_argument("output", type=Path)
    disclose.add_argument("--key", type=Path, required=True)
    verify = commands.add_parser("verify", help="verify a disclosed opening")
    verify.add_argument("directory", type=Path)
    timestamp_cli.add_commands(commands)
    args = parser.parse_args(argv)
    try:
        if args.command == "keygen":
            save_key(args.path)
            print("Key saved. Keep two secure copies in separate places.")
        elif args.command == "seal":
            print(
                workflow.seal(
                    args.source, args.directory, load_key(args.key), args.author
                )
            )
        elif args.command == "disclose":
            workflow.disclose(args.directory, args.output, load_key(args.key))
        elif args.command == "verify":
            workflow.verify(args.directory)
            print("Opening matches; timestamp not checked.")
    except InvalidToken:
        parser.exit(1, "claim: invalid key or encrypted opening\n")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"claim: {exc}\n")
    return 0
