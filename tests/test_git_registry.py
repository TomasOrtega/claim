import subprocess


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
