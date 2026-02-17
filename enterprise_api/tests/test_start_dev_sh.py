from __future__ import annotations

import subprocess
from pathlib import Path


def test_start_dev_sh_help() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "start-dev.sh"

    result = subprocess.run(
        ["bash", str(script), "--help"],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(repo_root),
    )

    assert result.returncode == 0
    assert "Usage: ./start-dev.sh" in result.stdout
    assert "--skip-docker" in result.stdout
    assert "--skip-frontend" in result.stdout
    assert "--clean-start" in result.stdout


def test_start_dev_sh_rebuild_has_legacy_builder_fallback() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "start-dev.sh"

    contents = script.read_text(encoding="utf-8")

    assert "DOCKER_BUILDKIT=0" in contents
    assert "COMPOSE_DOCKER_CLI_BUILD=0" in contents
