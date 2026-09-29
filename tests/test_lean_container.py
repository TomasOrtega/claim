import pytest

from claim import lean_container


def test_container_isolation(tmp_path, monkeypatch):
    commands = []
    monkeypatch.setattr(
        lean_container, "capture", lambda cmd, **kw: commands.append(cmd) or b"checked"
    )
    monkeypatch.setattr(
        lean_container.subprocess, "run", lambda cmd, **kw: commands.append(cmd)
    )
    assert (
        lean_container.run(
            tmp_path / "proof.zip", "sha256:" + "a" * 64, "check", "Proof", "result"
        )
        == b"checked"
    )
    assert {
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--pull=never",
        "--user=65534:65534",
    } <= set(commands[0])
    assert commands[1][:3] == ["docker", "rm", "--force"]


def test_container_requires_image_id(tmp_path):
    with pytest.raises(ValueError, match="image ID"):
        lean_container.run(tmp_path, "latest", "check", "Proof", "result")


def test_container_failure_cleanup(tmp_path, monkeypatch):
    def fail(*args, **kwargs):
        raise TimeoutError("timed out")

    removed = []
    monkeypatch.setattr(lean_container, "capture", fail)
    monkeypatch.setattr(
        lean_container.subprocess, "run", lambda cmd, **kw: removed.append(cmd)
    )
    with pytest.raises(TimeoutError):
        lean_container.run(tmp_path, "sha256:" + "a" * 64, "build", "Proof", "result")
    assert removed[0][:3] == ["docker", "rm", "--force"]
