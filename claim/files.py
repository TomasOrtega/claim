from pathlib import Path


def create_private_directory(path: Path) -> None:
    path.mkdir(mode=0o700)
