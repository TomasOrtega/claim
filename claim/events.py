from pathlib import Path

from claim.files import read_limited, write_private

_EVENTS = {
    "disclosed": b'{"event":"disclosed"}\n',
    "withdrawn": b'{"event":"withdrawn"}\n',
}


def status(history: list[str]) -> str:
    if "withdrawn" in history:
        return "withdrawn"
    return "disclosed" if "disclosed" in history else "sealed"


def read(directory: Path) -> list[str]:
    path = directory / "events"
    if not path.exists():
        return []
    history = []
    for i, entry in enumerate(sorted(path.iterdir()), 1):
        data = read_limited(entry, 64)
        if entry.name != f"{i:04d}.json" or data not in _EVENTS.values():
            raise ValueError("invalid claim event")
        event = next(name for name, value in _EVENTS.items() if value == data)
        if event in history:
            raise ValueError("duplicate claim event")
        history.append(event)
    return history


def append(directory: Path, event: str) -> None:
    history = read(directory)
    if event not in _EVENTS or event in history:
        raise ValueError("invalid or duplicate claim event")
    path = directory / "events"
    path.mkdir(mode=0o700, exist_ok=True)
    write_private(path / f"{len(history) + 1:04d}.json", _EVENTS[event])
