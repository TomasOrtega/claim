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


def test_disclose(sealed, tmp_path, key_file):
    output = tmp_path / "disclosed"
    result = run("disclose", sealed, output, "--key", key_file)
    assert result.returncode == 0
    assert (output / "proof").read_bytes() == b"proof\r\n\xff"


def test_verify(sealed, tmp_path, key_file):
    output = tmp_path / "disclosed"
    assert run("disclose", sealed, output, "--key", key_file).returncode == 0
    key_file.unlink()
    result = run("verify", output)
    assert result.returncode == 0
    assert "timestamp not checked" in result.stdout


def test_seal(tmp_path, key_file):
    source, directory = tmp_path / "proof", tmp_path / "sealed"
    source.write_bytes(b"proof")
    result = run("seal", source, directory, "--key", key_file, "--author", "Alice")
    assert result.returncode == 0
    assert (directory / "record.json").exists()


def test_keygen(tmp_path):
    path = tmp_path / "key"
    result = run("keygen", path)
    assert result.returncode == 0
    assert len(path.read_bytes()) == 44
    assert "two secure copies" in result.stdout
    assert path.read_text() not in result.stdout + result.stderr


def test_key_overwrite(tmp_path):
    path = tmp_path / "key"
    path.write_bytes(b"existing")
    result = run("keygen", path)
    assert result.returncode == 1 and "Traceback" not in result.stderr
    assert path.read_bytes() == b"existing"
