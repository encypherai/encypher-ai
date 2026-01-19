from pathlib import Path

import pytest


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.mark.asyncio
async def test_checked_in_sdk_runtimes_do_not_default_to_localhost() -> None:
    repo_root = _repo_root()

    python_config = repo_root / "sdk" / "python" / "encypher" / "configuration.py"
    ts_runtime = repo_root / "sdk" / "typescript" / "src" / "runtime.ts"
    rust_config = repo_root / "sdk" / "rust" / "src" / "apis" / "configuration.rs"

    assert 'http://localhost"' not in python_config.read_text(encoding="utf-8")
    assert 'http://localhost"' not in ts_runtime.read_text(encoding="utf-8")
    assert 'http://localhost"' not in rust_config.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_checked_in_go_sdk_uses_monorepo_module_path() -> None:
    repo_root = _repo_root()

    go_root = repo_root / "sdk" / "go"
    go_mod = go_root / "go.mod"
    go_test_root = go_root / "test"

    assert "module github.com/encypherai/encypherai-commercial/sdk/go" in go_mod.read_text(encoding="utf-8")

    for go_file in go_root.rglob("*.go"):
        assert "github.com/encypherai/sdk-go" not in go_file.read_text(encoding="utf-8")

    assert go_test_root.exists()
    for test_file in go_test_root.rglob("*.go"):
        text = test_file.read_text(encoding="utf-8")
        assert "github.com/GIT_USER_ID/GIT_REPO_ID" not in text
        assert "package encypher_test" in text
