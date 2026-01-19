from __future__ import annotations

import json
from pathlib import Path

import pytest


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_sdk_python_metadata_has_mit_license_and_urls() -> None:
    repo_root = _repo_root()

    pyproject = repo_root / "sdk" / "python" / "pyproject.toml"
    text = _read_text(pyproject)

    assert 'name = "encypher"' in text
    assert "license" in text
    assert "MIT" in text

    assert 'Documentation = "https://api.encypherai.com/docs"' in text
    assert 'Repository = "https://github.com/encypherai/encypherai-commercial"' in text


@pytest.mark.asyncio
async def test_sdk_typescript_metadata_is_publish_ready() -> None:
    repo_root = _repo_root()

    package_json = repo_root / "sdk" / "typescript" / "package.json"
    data = json.loads(_read_text(package_json))

    assert data["name"] == "@encypher/sdk"
    assert data.get("license") == "MIT"
    assert data.get("author") == "Encypher"

    publish_config = data.get("publishConfig")
    assert isinstance(publish_config, dict)
    assert publish_config.get("access") == "public"

    files = data.get("files")
    assert isinstance(files, list)
    assert "dist" in files

    npmignore = repo_root / "sdk" / "typescript" / ".npmignore"
    if npmignore.exists():
        assert "README.md" not in _read_text(npmignore)


@pytest.mark.asyncio
async def test_sdk_rust_metadata_has_mit_license_and_readme() -> None:
    repo_root = _repo_root()

    cargo_toml = repo_root / "sdk" / "rust" / "Cargo.toml"
    text = _read_text(cargo_toml)

    assert 'license = "MIT"' in text
    assert 'readme = "README.md"' in text


@pytest.mark.asyncio
async def test_sdk_packaging_and_publish_workflows_exist() -> None:
    repo_root = _repo_root()

    workflows_dir = repo_root / ".github" / "workflows"

    packaging = workflows_dir / "sdk-packaging.yml"
    publish_python = workflows_dir / "sdk-publish-python.yml"
    publish_typescript = workflows_dir / "sdk-publish-typescript.yml"
    publish_rust = workflows_dir / "sdk-publish-rust.yml"

    assert packaging.exists()
    assert publish_python.exists()
    assert publish_typescript.exists()
    assert publish_rust.exists()

    packaging_text = _read_text(packaging)
    assert "uv build" in packaging_text
    assert "npm pack" in packaging_text
    assert "cargo package" in packaging_text

    assert "sdk/python/v" in _read_text(publish_python)
    assert "sdk/typescript/v" in _read_text(publish_typescript)
    assert "sdk/rust/v" in _read_text(publish_rust)
