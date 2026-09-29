from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from claim import archives, lean, lean_container
from claim.files import read_limited, write_private
from claim.limits import MAX_ARTIFACT_BYTES


def check(
    source: Path, module: str, theorem: str, *, image=None, trusted_local=False
) -> dict:
    if bool(image) == trusted_local:
        raise ValueError("choose an image or an explicit trusted local check")
    lean.validate_name(module)
    lean.validate_name(theorem)
    data = read_limited(source, MAX_ARTIFACT_BYTES)
    with TemporaryDirectory() as temporary:
        directory = Path(temporary)
        project = directory / "project"
        project.mkdir()
        archives.unpack(data, project)
        lean.validate_project(project)
        if trusted_local:
            prefix = ["elan", "run", lean.TOOLCHAIN]
            lean.build(project, module, prefix)
            statement = lean.check_build(project, module, theorem, prefix)
        else:
            archive = directory / "source.zip"
            write_private(archive, data)
            archive.chmod(0o444)
            built = lean_container.run(archive, image, "build", module, theorem)
            archive = directory / "built.zip"
            write_private(archive, built)
            archive.chmod(0o444)
            statement = (
                lean_container.run(archive, image, "check", module, theorem)
                .decode()
                .strip()
            )
    return {
        "artifact_sha256": sha256(data).hexdigest(),
        "toolchain": lean.TOOLCHAIN,
        "module": module,
        "theorem": theorem,
        "statement": statement,
        "mode": "author-reported" if trusted_local else "isolated",
        "image": image,
    }
