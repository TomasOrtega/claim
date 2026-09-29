import os
import shutil

import pytest

from claim.lean import TOOLCHAIN, build, check_build

pytestmark = pytest.mark.skipif(
    not os.getenv("CLAIM_TEST_LEAN"), reason="opt-in Lean integration"
)


@pytest.fixture
def built_project(lean_project):
    (lean_project / "lakefile.toml").write_text(
        'name = "Proof"\n[[lean_lib]]\nname = "Proof"\n'
    )
    (lean_project / "Proof.lean").write_text(
        "theorem result : 1 + 1 = 2 := rfl\naxiom falsehood : False\ntheorem bad : False := falsehood\nset_option warn.sorry false in\ntheorem incomplete : False := by sorry\n"
    )
    build(lean_project, "Proof", [shutil.which("elan"), "run", TOOLCHAIN])
    return lean_project


def test_real_lean(built_project):
    statement = check_build(
        built_project, "Proof", "result", ["elan", "run", TOOLCHAIN]
    )
    assert "Eq" in statement and "2" in statement


@pytest.mark.parametrize("theorem", ["bad", "falsehood", "missing", "incomplete"])
def test_real_lean_rejects(built_project, theorem):
    with pytest.raises(ValueError, match="failed"):
        check_build(built_project, "Proof", theorem, ["elan", "run", TOOLCHAIN])


def test_invalid_lean_proof(lean_project):
    (lean_project / "lakefile.toml").write_text(
        'name = "Proof"\n[[lean_lib]]\nname = "Proof"\n'
    )
    (lean_project / "Proof.lean").write_text("theorem wrong : 1 = 2 := rfl\n")
    with pytest.raises(ValueError, match="failed"):
        build(lean_project, "Proof", ["elan", "run", TOOLCHAIN])
