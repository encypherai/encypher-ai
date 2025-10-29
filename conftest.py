"""
Ensure each workspace package is importable when running pytest from the repo root.
"""
from __future__ import annotations

import sys
from pathlib import Path
import types
from importlib.machinery import ModuleSpec

ROOT = Path(__file__).resolve().parent
ENTERPRISE_APP_PATH = ROOT / "enterprise_api" / "app"
DASHBOARD_APP_PATH = ROOT / "dashboard_app" / "backend" / "app"


def _ensure_workspace_paths() -> None:
    workspace_roots = [
        ROOT,
        ROOT / "audit_log_cli",
        ROOT / "policy_validator_cli",
        ROOT / "dashboard_app" / "backend",
        ROOT / "shared_commercial_libs",
        ROOT / "enterprise_api",
        ROOT / "encypher-ai",
    ]

    for path in workspace_roots:
        if path.exists():
            sys.path.insert(0, str(path))


def _set_app_module(*paths: Path) -> None:
    for key in list(sys.modules.keys()):
        if key.startswith("app."):
            sys.modules.pop(key, None)
    search_locations = [str(path) for path in paths if path.exists()]
    app_module = types.ModuleType("app")
    app_module.__package__ = "app"
    app_module.__path__ = search_locations  # type: ignore[attr-defined]
    app_module.__spec__ = ModuleSpec("app", loader=None, is_package=True)
    app_module.__spec__.submodule_search_locations = search_locations  # type: ignore[attr-defined]
    sys.modules["app"] = app_module


_ensure_workspace_paths()
_set_app_module(ENTERPRISE_APP_PATH, DASHBOARD_APP_PATH)


def pytest_collectstart(collector) -> None:
    path = getattr(collector, "path", None)
    if path is None:
        return
    path_str = str(path)
    if "dashboard_app" in path_str:
        _set_app_module(DASHBOARD_APP_PATH)
    elif "enterprise_api" in path_str:
        _set_app_module(ENTERPRISE_APP_PATH)


def _ensure_tests_namespace() -> None:
    candidate_paths = [
        ROOT / "enterprise_api" / "tests",
        ROOT / "policy_validator_cli" / "tests",
        ROOT / "audit_log_cli" / "tests",
        ROOT / "dashboard_app" / "backend" / "tests",
        ROOT / "encypher-ai" / "tests",
    ]

    tests_module = sys.modules.get("tests")
    if tests_module is None:
        tests_module = types.ModuleType("tests")
        tests_module.__path__ = []  # type: ignore[attr-defined]
        sys.modules["tests"] = tests_module

    combined_paths = list(getattr(tests_module, "__path__", []))  # type: ignore[arg-type]

    for path in candidate_paths:
        if path.exists():
            path_str = str(path)
            if path_str not in combined_paths:
                combined_paths.append(path_str)

    tests_module.__path__ = combined_paths  # type: ignore[attr-defined]


_ensure_tests_namespace()
