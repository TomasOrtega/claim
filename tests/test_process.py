import sys

import pytest

from claim.process import capture


def test_capture_limit():
    with pytest.raises(ValueError, match="size limit"):
        capture([sys.executable, "-c", "print('x' * 100)"], limit=10)


def test_capture_failed():
    with pytest.raises(ValueError, match="failed"):
        capture([sys.executable, "-c", "raise SystemExit(1)"])
