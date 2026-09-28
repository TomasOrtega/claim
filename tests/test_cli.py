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


def test_keygen(tmp_path):
    path = tmp_path / "key"
    result = run("keygen", path)
    assert result.returncode == 0
    assert len(path.read_bytes()) == 44
    assert path.read_text() not in result.stdout + result.stderr
