import pytest

from claim.lean import validate_name, validate_project


def test_lean_rejects_build_cache(lean_project):
    (lean_project / "Proof.olean").touch()
    with pytest.raises(ValueError, match="without build outputs"):
        validate_project(lean_project)


def test_pinned_lean_project(lean_project):
    validate_project(lean_project)
    (lean_project / "lean-toolchain").write_text("stable")
    with pytest.raises(ValueError, match="require"):
        validate_project(lean_project)


@pytest.mark.parametrize("name", ["--help", "../Proof", "", "Foo;echo", "Foo..Bar"])
def test_invalid_lean_name(name):
    with pytest.raises(ValueError, match="Lean name"):
        validate_name(name)
