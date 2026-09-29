import os
import signal
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from subprocess import DEVNULL, PIPE, Popen


def capture(command, *, cwd=None, env=None, limit=128 * 1024 * 1024, timeout=300):
    with Popen(
        command, cwd=cwd, env=env, stdout=PIPE, stderr=DEVNULL, start_new_session=True
    ) as process:
        reader = ThreadPoolExecutor(max_workers=1)
        try:
            data = reader.submit(process.stdout.read, limit + 1).result(timeout)
            if len(data) > limit:
                raise ValueError("command output exceeds size limit")
            if process.wait(timeout=10):
                raise ValueError("Lean command failed")
            return data
        finally:
            with suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
            reader.shutdown(wait=False)
