import subprocess

from claim import registry


def test_git_restore(accepted, tmp_path):
    root, claim_id = accepted
    git(root, "init")
    git(root, "add", ".")
    git(
        root,
        "commit",
        "-m",
        "test: snapshot registry",
        "-m",
        "Assisted-by: Codex:GPT-6",
    )
    restored = tmp_path / "restored"
    git(root, "clone", "--no-local", "--config", "core.autocrlf=true", root, restored)
    entry = registry.location(restored, claim_id)
    assert registry.read_claim(entry) == registry.read_claim(
        registry.location(root, claim_id)
    )
    assert not (entry / "opening.fernet").exists()


def git(path, *args):
    return subprocess.run(
        [
            "git",
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "user.name=Claim test",
            "-c",
            "user.email=claim@example.invalid",
            "-C",
            str(path),
            *map(str, args),
        ],
        check=True,
        capture_output=True,
    )


def test_public_attributes(accepted, tmp_path):
    output = tmp_path / "site"
    registry.export(accepted[0], output)
    assert (output / ".gitattributes").read_bytes() == b"* -text\n"
