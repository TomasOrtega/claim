import sys
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from claim import archives, lean
from claim.files import read_limited


def objects(directory: Path) -> bytes:
    stream, remaining = BytesIO(), archives.MAX_EXPANDED
    with ZipFile(stream, "w") as archive:
        for path in sorted(directory.rglob("*.olean*")):
            if path.is_symlink() or not path.is_file():
                raise ValueError("invalid Lean object")
            data = read_limited(path, remaining)
            remaining -= len(data)
            archive.writestr(path.relative_to(directory).as_posix(), data)
    return stream.getvalue()


def main(args):
    mode, module, theorem = args
    with TemporaryDirectory() as temporary:
        directory = Path(temporary)
        archives.unpack(
            read_limited(Path("/input/proof.zip"), archives.MAX_EXPANDED), directory
        )
        if mode == "build":
            lean.build(directory, module, [])
            sys.stdout.buffer.write(objects(directory))
        elif mode == "check":
            print(lean.check_build(directory, module, theorem, []))
        else:
            raise ValueError("invalid Lean worker mode")


if __name__ == "__main__":
    main(sys.argv[1:])
