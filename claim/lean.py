import json
import os
import re
from pathlib import Path

from claim.files import read_limited
from claim.process import capture

TOOLCHAIN = "leanprover/lean4:v4.34.0"


def validate_project(directory: Path) -> None:
    if read_limited(directory / "lean-toolchain", 128).decode().strip() != TOOLCHAIN:
        raise ValueError(f"Lean checks require {TOOLCHAIN}")
    manifest = json.loads(read_limited(directory / "lake-manifest.json", 1024 * 1024))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("packages"), list):
        raise ValueError("invalid Lake manifest")  # noqa: TRY004
    for package in manifest["packages"]:
        if not isinstance(package, dict) or package.get("type") != "path":
            raise ValueError("vendor dependencies as local path packages")
        if not isinstance(package.get("dir"), str):
            raise ValueError("invalid dependency directory")  # noqa: TRY004
        dependency = directory / package["dir"]
        if not dependency.resolve().is_relative_to(directory.resolve()):
            raise ValueError("dependency must be inside the archive")
    if any(
        ".lake/build" in p.relative_to(directory).as_posix() or ".olean" in p.suffixes
        for p in directory.rglob("*")
    ):
        raise ValueError("archive must contain sources without build outputs")


def validate_name(name: str) -> None:
    if (
        re.fullmatch(r"[A-Za-z_][A-Za-z_0-9']*(\.[A-Za-z_][A-Za-z_0-9']*)*", name)
        is None
    ):
        raise ValueError("use an ASCII dotted Lean name")


def build(directory: Path, module: str, prefix: list[str]) -> None:
    validate_project(directory)
    validate_name(module)
    capture(
        [*prefix, "lake", "--wfail", "--no-cache", "build", f"+{module}"], cwd=directory
    )


def check_build(directory: Path, module: str, theorem: str, prefix: list[str]) -> str:
    validate_name(module)
    validate_name(theorem)
    roots = sorted(
        {
            p
            for p in directory.rglob("lean")
            if p.parts[-4:] == (".lake", "build", "lib", "lean")
        }
    )
    environment = {k: v for k, v in os.environ.items() if not k.startswith("LEAN_")}
    command = [
        *prefix,
        "lean",
        "--run",
        str(Path(__file__).with_name("Check.lean")),
        module,
        theorem,
    ]
    return (
        capture(command + [str(p) for p in roots], env=environment, limit=65536)
        .decode()
        .strip()
    )
