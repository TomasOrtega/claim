from hashlib import sha256
from zipfile import ZipFile

from claim import lean_workflow


def test_lean_archive_snapshot(lean_project, monkeypatch):
    archive = lean_project.parent / (lean_project.name + ".zip")
    with ZipFile(archive, "w") as output:
        for path in lean_project.iterdir():
            output.write(path, path.name)
    original = archive.read_bytes()
    monkeypatch.setattr(
        lean_workflow.lean, "build", lambda *a: archive.write_bytes(b"edited")
    )
    monkeypatch.setattr(lean_workflow.lean, "check_build", lambda *a: "True")
    result = lean_workflow.check(archive, "Proof", "result", trusted_local=True)
    assert result["artifact_sha256"] == sha256(original).hexdigest()
    assert result["mode"] == "author-reported"
