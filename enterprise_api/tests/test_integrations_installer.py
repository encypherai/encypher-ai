from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def _load_installer_module():
    repo_root = Path(__file__).resolve().parents[2]
    installer_path = repo_root / "scripts" / "integrations_installer.py"
    spec = importlib.util.spec_from_file_location("integrations_installer", installer_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


installer = _load_installer_module()


def test_default_targets_include_all_integrations() -> None:
    args = installer.parse_args([])

    targets = installer.resolve_targets(args)

    assert targets == ["outlook", "office", "google_docs"]


def test_explicit_targets_respected_without_all() -> None:
    args = installer.parse_args(["--outlook", "--office"])

    targets = installer.resolve_targets(args)

    assert targets == ["outlook", "office"]


def test_all_flag_overrides_partial_target_selection() -> None:
    args = installer.parse_args(["--all", "--outlook"])

    targets = installer.resolve_targets(args)

    assert targets == ["outlook", "office", "google_docs"]


def test_build_local_test_plan_contains_expected_commands_for_selected_targets() -> None:
    repo_root = Path("/repo")

    plan = installer.build_local_test_plan(repo_root=repo_root, targets=["outlook", "google_docs"])

    command_steps = [step for step in plan if step.kind == "command"]
    command_strings = [" ".join(step.command) for step in command_steps]

    assert "npm test" in command_strings
    assert "npm pack --dry-run" in command_strings
    assert "uv run pytest enterprise_api/tests/test_email_embedding_survivability.py -q" in command_strings


def test_build_deploy_plan_has_manual_steps_for_each_target() -> None:
    steps = installer.build_deploy_plan(["outlook", "office", "google_docs"])

    joined = "\n".join(step.description for step in steps)
    assert "Outlook" in joined
    assert "Word/Excel/PowerPoint" in joined
    assert "Google Docs" in joined


def test_validate_manifest_files_accepts_valid_xml_and_json(tmp_path: Path) -> None:
    xml_path = tmp_path / "manifest.xml"
    xml_path.write_text("<root><child /></root>", encoding="utf-8")

    json_path = tmp_path / "appsscript.json"
    json_path.write_text('{"name": "ok"}', encoding="utf-8")

    xml_result = installer.validate_xml_file(xml_path)
    json_result = installer.validate_json_file(json_path)

    assert xml_result.ok is True
    assert json_result.ok is True
