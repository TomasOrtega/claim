import argparse
from pathlib import Path

from claim.keys import save_key


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="claim")
    commands = parser.add_subparsers(dest="command", required=True)
    keygen = commands.add_parser("keygen", help="generate an encryption key")
    keygen.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        save_key(args.path)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"claim: {exc}\n")
    return 0
