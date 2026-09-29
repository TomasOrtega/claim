from io import BytesIO
from zipfile import ZipFile

from claim.lean_worker import objects


def test_only_lean_objects(tmp_path):
    (tmp_path / "Proof.olean").write_bytes(b"object")
    (tmp_path / "private.txt").write_bytes(b"secret")
    with ZipFile(BytesIO(objects(tmp_path))) as archive:
        assert archive.namelist() == ["Proof.olean"]
        assert archive.read("Proof.olean") == b"object"
