import subprocess
import sys

from claim import record


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
    assert "date-claims" in result.stdout


def test_changed_proof(sealed, tmp_path, key_file):
    output = tmp_path / "disclosed"
    assert run("disclose", sealed, output, "--key", key_file).returncode == 0
    (output / "proof").write_bytes(b"changed")
    result = run("verify", output)
    assert result.returncode == 1 and result.stdout == ""
    assert "opening does not match" in result.stderr


def test_reuse_key(sealed, tmp_path, key_file):
    second, output = tmp_path / "second", tmp_path / "disclosed"
    assert (
        run(
            "seal", tmp_path / "proof", second, "--key", key_file, "--author", "Alice"
        ).returncode
        == 0
    )
    assert run("disclose", sealed, output, "--key", key_file).returncode == 0
    assert (
        run(
            "disclose", second, tmp_path / "second-disclosure", "--key", key_file
        ).returncode
        == 0
    )
    assert run("verify", output).returncode == 0


def test_backup_key_recovery(sealed, tmp_path, key_file):
    backup = tmp_path / "backup-key"
    backup.write_bytes(key_file.read_bytes())
    key_file.unlink()
    output = tmp_path / "disclosed"
    assert run("disclose", sealed, output, "--key", backup).returncode == 0
    assert run("verify", output).returncode == 0


def test_wrong_key(sealed, tmp_path):
    path = tmp_path / "other-key"
    assert run("keygen", path).returncode == 0
    result = run("disclose", sealed, tmp_path / "output", "--key", path)
    assert result.returncode == 1 and "Traceback" not in result.stderr
    assert not (tmp_path / "output").exists()


def test_disclose(sealed, tmp_path, key_file):
    output = tmp_path / "disclosed"
    result = run("disclose", sealed, output, "--key", key_file)
    assert result.returncode == 0
    assert (output / "proof").read_bytes() == b"proof\r\n\xff"
    claim_id = record.record_id((output / "record.json").read_bytes())
    assert f"Claim ID: {claim_id}" in result.stdout
    assert f"Salt: {(output / 'salt').read_bytes().hex()}" in result.stdout
    assert key_file.read_text() not in result.stdout


def test_verify(sealed, tmp_path, key_file):
    output = tmp_path / "disclosed"
    assert run("disclose", sealed, output, "--key", key_file).returncode == 0
    key_file.unlink()
    result = run("verify", output)
    assert result.returncode == 0
    assert "Opening matches." in result.stdout


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


def test_seal_rejects_coauthors(tmp_path, key_file):
    source = tmp_path / "proof"
    source.write_bytes(b"A proof by Alice and Bob")
    result = run(
        "seal",
        source,
        tmp_path / "sealed",
        "--key",
        key_file,
        "--author",
        "Alice",
        "--author",
        "Bob",
    )
    assert result.returncode == 1
    assert "exactly one" in result.stderr
