import pytest

from claim import cli


def test_lean_cli_requires_execution_choice():
    with pytest.raises(SystemExit) as error:
        cli.main(["check-lean", "proof.zip", "Proof", "result"])
    assert error.value.code == 2
