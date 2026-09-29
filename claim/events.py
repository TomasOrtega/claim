from pathlib import Path

from claim.files import read_limited

_EVENTS = {
    "disclosed": b'{"event":"disclosed"}\n',
    "withdrawn": b'{"event":"withdrawn"}\n',
}


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
