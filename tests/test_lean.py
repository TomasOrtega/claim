import json

import pytest

from claim.lean import TOOLCHAIN, validate_name, validate_project


@pytest.fixture
def lean_project(tmp_path):
    (tmp_path / "lean-toolchain").write_text(TOOLCHAIN + "\n")
    (tmp_path / "lake-manifest.json").write_text(json.dumps({"packages": []}))
    return tmp_path


def test_pinned_lean_project(lean_project):
    validate_project(lean_project)
    (lean_project / "lean-toolchain").write_text("stable")
    with pytest.raises(ValueError, match="require"):
        validate_project(lean_project)


@pytest.mark.parametrize("name", ["--help", "../Proof", "", "Foo;echo", "Foo..Bar"])
def test_invalid_lean_name(name):
    with pytest.raises(ValueError, match="Lean name"):
        validate_name(name)
