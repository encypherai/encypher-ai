import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


def _load_generate_sdk_module():
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "sdk" / "generate_sdk.py"
    spec = importlib.util.spec_from_file_location("sdk_generate_sdk", module_path)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.asyncio
async def test_patch_typescript_metadata_sets_monorepo_repository(tmp_path: Path) -> None:
    mod = _load_generate_sdk_module()

    package_json = tmp_path / "package.json"
    package_json.write_text(
        json.dumps(
            {
                "name": "@encypher/sdk",
                "version": "0.0.0",
                "repository": {"type": "git", "url": "https://github.com/encypherai/sdk-typescript.git"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    mod._patch_typescript_metadata(tmp_path)

    data = json.loads(package_json.read_text(encoding="utf-8"))
    assert data["repository"]["type"] == "git"
    assert data["repository"]["url"] == mod.MONOREPO_GIT_URL
    assert data["repository"]["directory"] == "sdk/typescript"

    runtime_ts = tmp_path / "src" / "runtime.ts"
    runtime_ts.parent.mkdir(parents=True, exist_ok=True)
    runtime_ts.write_text(
        'export const BASE_PATH = "http://localhost".replace(/\\/+$/, "");\n',
        encoding="utf-8",
    )
    mod._patch_typescript_metadata(tmp_path)
    assert "https://api.encypherai.com" in runtime_ts.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_patch_go_metadata_sets_monorepo_module_path(tmp_path: Path) -> None:
    mod = _load_generate_sdk_module()

    go_mod = tmp_path / "go.mod"
    go_mod.write_text("module github.com/encypherai/sdk-go\n\ngo 1.23\n", encoding="utf-8")

    readme = tmp_path / "README.md"
    readme.write_text("import \"github.com/encypherai/sdk-go\"\n", encoding="utf-8")

    main_go = tmp_path / "cmd" / "encypher" / "main.go"
    main_go.parent.mkdir(parents=True, exist_ok=True)
    main_go.write_text(
        'package main\n\nimport encypher "github.com/encypherai/sdk-go"\n',
        encoding="utf-8",
    )

    test_go = tmp_path / "test" / "api_account_test.go"
    test_go.parent.mkdir(parents=True, exist_ok=True)
    test_go.write_text(
        'package encypher\n\nimport openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID/encypher"\n',
        encoding="utf-8",
    )

    mod._patch_go_metadata(tmp_path)

    assert f"module {mod.GO_MODULE_PATH}" in go_mod.read_text(encoding="utf-8")
    assert "go 1.21" in go_mod.read_text(encoding="utf-8")
    assert mod.GO_MODULE_PATH in readme.read_text(encoding="utf-8")
    assert mod.GO_MODULE_PATH in main_go.read_text(encoding="utf-8")

    patched_test = test_go.read_text(encoding="utf-8")
    assert "github.com/GIT_USER_ID/GIT_REPO_ID" not in patched_test
    assert mod.GO_MODULE_PATH in patched_test
    assert "package encypher_test" in patched_test


@pytest.mark.asyncio
async def test_patch_python_metadata_normalizes_dependencies_and_urls(tmp_path: Path) -> None:
    mod = _load_generate_sdk_module()

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name = "encypher"
authors = [
  {name = "OpenAPI Generator Community",email = "team@openapitools.org"},
]
dependencies = [
  "urllib3 (>=2.1.0,<3.0.0)",
]

[project.urls]
Repository = "https://github.com/encypherai/sdk-python"
""",
        encoding="utf-8",
    )

    mod._patch_python_metadata(tmp_path)

    text = pyproject.read_text(encoding="utf-8")
    assert "\"urllib3>=2.1.0,<3.0.0\"" in text
    assert "{name = \"Encypher\"" in text
    assert "email = \"sdk@encypherai.com\"" in text
    assert "Homepage = \"https://encypherai.com\"" in text
    assert f"Documentation = \"{mod.PRODUCTION_BASE_URL}/docs\"" in text
    assert f"Repository = \"{mod.MONOREPO_URL}\"" in text
    assert f"Changelog = \"{mod.MONOREPO_URL}/releases\"" in text

    config_py = tmp_path / "encypher" / "configuration.py"
    config_py.parent.mkdir(parents=True, exist_ok=True)
    config_py.write_text(
        """class Configuration:
    def __init__(self, host=None):
        self._base_path = \"http://localhost\" if host is None else host

    def get_host_settings(self):
        return [
            {
                'url': \"\",
                'description': \"No description provided\",
            }
        ]
""",
        encoding="utf-8",
    )
    mod._patch_python_metadata(tmp_path)
    patched = config_py.read_text(encoding="utf-8")
    assert "https://api.encypherai.com" in patched
    assert "http://localhost:8007" in patched


@pytest.mark.asyncio
async def test_patch_rust_metadata_sets_monorepo_repository(tmp_path: Path) -> None:
    mod = _load_generate_sdk_module()

    cargo = tmp_path / "Cargo.toml"
    cargo.write_text(
        """[package]
name = \"encypher\"
license = \"Unlicense\"
""",
        encoding="utf-8",
    )

    mod._patch_rust_metadata(tmp_path)

    patched = cargo.read_text(encoding="utf-8")
    assert f"repository = \"{mod.MONOREPO_URL}\"" in patched
    assert "homepage = \"https://encypherai.com\"" in patched
    assert f"documentation = \"{mod.PRODUCTION_BASE_URL}/docs\"" in patched
    assert "license = \"MIT\"" in patched
    assert "authors = [\"Encypher <sdk@encypherai.com>\"]" in patched

    rust_cfg = tmp_path / "src" / "apis" / "configuration.rs"
    rust_cfg.parent.mkdir(parents=True, exist_ok=True)
    rust_cfg.write_text(
        'base_path: "http://localhost".to_owned(),\n',
        encoding="utf-8",
    )
    mod._patch_rust_metadata(tmp_path)
    assert "https://api.encypherai.com" in rust_cfg.read_text(encoding="utf-8")


def test_check_openapi_generator_uses_noninteractive_npx(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load_generate_sdk_module()

    called: dict[str, list[str]] = {}

    def fake_run_cmd(cmd: list, capture: bool = True, stream_output: bool = False) -> subprocess.CompletedProcess:
        called["cmd"] = cmd
        return subprocess.CompletedProcess(cmd, 0, "7.0.0\n", "")

    monkeypatch.setattr(mod, "run_cmd", fake_run_cmd)
    monkeypatch.setattr(mod, "log_info", lambda _msg: None)
    monkeypatch.setattr(mod, "log_success", lambda _msg: None)
    monkeypatch.setattr(mod, "log_error", lambda _msg: None)

    version = mod.check_openapi_generator()
    assert version is not None
    assert any(flag in called["cmd"] for flag in ("--yes", "-y"))
