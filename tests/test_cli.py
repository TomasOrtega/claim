import subprocess
import sys


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "claim", *map(str, args)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_help():
    result = run("--help")
    assert result.returncode == 0
    assert "usage:" in result.stdout
