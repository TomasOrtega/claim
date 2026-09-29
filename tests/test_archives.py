from io import BytesIO
from zipfile import ZipFile

from claim.archives import unpack


def test_unpack_archive(tmp_path):
    stream = BytesIO()
    with ZipFile(stream, "w") as archive:
        archive.writestr("Proof.lean", "theorem result : True := True.intro")
    unpack(stream.getvalue(), tmp_path)
    assert (tmp_path / "Proof.lean").read_text().startswith("theorem")
