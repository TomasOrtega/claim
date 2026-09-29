import os
from pathlib import Path
from zipfile import ZipFile

import pytest

from claim.lean_workflow import check


@pytest.mark.skipif(
    not os.getenv("CLAIM_TEST_LEAN_IMAGE"), reason="opt-in Docker integration"
)
def test_real_lean_container(tmp_path):
    archive = tmp_path / "proof.zip"
    with ZipFile(archive, "w") as output:
        for path in Path("examples/lean").iterdir():
            output.write(path, path.name)
    result = check(
        archive, "Proof", "result", image=os.environ["CLAIM_TEST_LEAN_IMAGE"]
    )
    assert result["mode"] == "isolated" and "Eq" in result["statement"]
