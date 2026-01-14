from __future__ import annotations

from pathlib import Path


def test_linux_start_dev_script_exists_and_has_expected_commands() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "start-dev.sh"

    assert script_path.exists(), "Expected repo root to contain start-dev.sh"

    text = script_path.read_text(encoding="utf-8")

    # Basic contract: script starts Docker Compose full stack and both frontends.
    assert "docker-compose.full-stack.yml" in text
    assert "apps/marketing-site" in text
    assert "apps/dashboard" in text
    assert "npm" in text
