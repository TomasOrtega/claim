import re
import subprocess
from contextlib import suppress
from pathlib import Path
from uuid import uuid4

from claim.archives import MAX_EXPANDED
from claim.process import capture


def run(archive: Path, image: str, mode: str, module: str, theorem: str) -> bytes:
    if re.fullmatch(r"sha256:[0-9a-f]{64}", image) is None:
        raise ValueError("use a local Docker image ID (sha256:...)")
    name = "claim-lean-" + uuid4().hex
    runner = Path(__file__).resolve().parent
    command = [
        "docker",
        "run",
        "--rm",
        "--pull=never",
        "--name",
        name,
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--user=65534:65534",
        "--pids-limit=128",
        "--memory=4g",
        "--memory-swap=4g",
        "--cpus=2",
        "--tmpfs=/tmp:rw,exec,nosuid,size=1g,mode=1777",
        "--env=HOME=/tmp",
        "--env=PYTHONPATH=/runner",
        "--env=PYTHONDONTWRITEBYTECODE=1",
        "--env=PATH=/opt/lean/bin:/usr/local/bin:/usr/bin:/bin",
        "--mount",
        f"type=bind,src={archive},dst=/input/proof.zip,readonly",
        "--mount",
        f"type=bind,src={runner},dst=/runner/claim,readonly",
        "--entrypoint=python3",
        image,
        "-m",
        "claim.lean_worker",
        mode,
        module,
        theorem,
    ]
    try:
        return capture(command, limit=MAX_EXPANDED, timeout=330)
    finally:
        with suppress(OSError, subprocess.TimeoutExpired):
            subprocess.run(
                ["docker", "rm", "--force", name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
                check=False,
            )
