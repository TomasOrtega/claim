import json
import re
from pathlib import Path

from claim.files import read_limited

TOOLCHAIN = "leanprover/lean4:v4.34.0"


def validate_project(directory: Path) -> None:
    if read_limited(directory / "lean-toolchain", 128).decode().strip() != TOOLCHAIN:
        raise ValueError(f"Lean checks require {TOOLCHAIN}")
    manifest = json.loads(read_limited(directory / "lake-manifest.json", 1024 * 1024))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("packages"), list):
        raise ValueError("invalid Lake manifest")  # noqa: TRY004


def validate_name(name: str) -> None:
    if (
        re.fullmatch(r"[A-Za-z_][A-Za-z_0-9']*(\.[A-Za-z_][A-Za-z_0-9']*)*", name)
        is None
    ):
        raise ValueError("use an ASCII dotted Lean name")
