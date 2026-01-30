from __future__ import annotations

import subprocess
from pathlib import Path


def test_setup_dev_sh_help() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "setup-dev.sh"

    result = subprocess.run(
        ["bash", str(script), "--help"],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(repo_root),
    )

    assert result.returncode == 0
    assert "Usage: ./setup-dev.sh" in result.stdout
    assert "--skip-python" in result.stdout
    assert "--skip-node" in result.stdout
