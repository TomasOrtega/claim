from io import BytesIO
from pathlib import Path, PurePosixPath
from zipfile import BadZipFile, ZipFile

from claim.files import write_private

MAX_EXPANDED = 128 * 1024 * 1024


def unpack(data: bytes, directory: Path) -> None:
    try:
        with ZipFile(BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) > 20000 or sum(e.file_size for e in entries) > MAX_EXPANDED:
                raise ValueError("archive exceeds size limit")
            for entry in entries:
                parts = PurePosixPath(entry.filename)
                if parts.is_absolute() or ".." in parts.parts or ":" in entry.filename:
                    raise ValueError("unsafe archive path")
                if (
                    parts.as_posix() != entry.filename.rstrip("/")
                    or "\\" in entry.filename
                ):
                    raise ValueError("unsafe archive path")
                path = directory / entry.filename
                path.parent.mkdir(parents=True, exist_ok=True)
                if not entry.is_dir():
                    write_private(path, archive.read(entry))
    except BadZipFile as exc:
        raise ValueError("invalid ZIP archive") from exc
