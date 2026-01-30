from __future__ import annotations

import subprocess
from pathlib import Path


def test_stop_dev_sh_help() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "stop-dev.sh"

    result = subprocess.run(
        ["bash", str(script), "--help"],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(repo_root),
    )

    assert result.returncode == 0
    assert "Usage: ./stop-dev.sh" in result.stdout
