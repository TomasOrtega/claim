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


def test_key_overwrite(tmp_path):
    path = tmp_path / "key"
    path.write_bytes(b"existing")
    result = run("keygen", path)
    assert result.returncode == 1 and "Traceback" not in result.stderr
    assert path.read_bytes() == b"existing"
