import subprocess

from claim import registry, storage


def test_git_restore(accepted, tmp_path, key):
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
    assert storage.load_opening(entry / "opening.fernet", key)[0] == b"proof\r\n\xff"


def git(path, *args):
    subprocess.run(
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
