#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

TARGETS_ALL = ["outlook", "office", "google_docs"]


@dataclass(frozen=True)
class ValidationResult:
    path: Path
    ok: bool
    message: str


@dataclass(frozen=True)
class PlanStep:
    kind: str  # "validation" | "command" | "manual"
    description: str
    command: tuple[str, ...] = ()
    cwd: Path | None = None


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="integrations-installer",
        description=(
            "Portable installer helper for Encypher integrations. "
            "Supports local preflight testing and deploy-plan generation."
        ),
    )
    parser.add_argument("--all", action="store_true", help="Target all integrations (default if none selected)")
    parser.add_argument("--outlook", action="store_true", help="Target Outlook add-in")
    parser.add_argument("--office", action="store_true", help="Target Office add-ins (Word/Excel/PowerPoint)")
    parser.add_argument("--google-docs", dest="google_docs", action="store_true", help="Target Google Docs add-on")
    parser.add_argument(
        "--mode",
        choices=["local-test", "deploy-plan"],
        default="local-test",
        help="Operation mode (default: local-test)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute local-test commands. Without this, print plan only.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root path (auto-detected by default)",
    )
    parser.add_argument(
        "--report-file",
        type=Path,
        default=None,
        help="Optional markdown report output file",
    )
    return parser.parse_args(argv)


def resolve_targets(args: argparse.Namespace) -> list[str]:
    explicit = []
    if args.outlook:
        explicit.append("outlook")
    if args.office:
        explicit.append("office")
    if args.google_docs:
        explicit.append("google_docs")

    if args.all or not explicit:
        return TARGETS_ALL.copy()
    return explicit


def validate_xml_file(path: Path) -> ValidationResult:
    try:
        ET.parse(path)
        return ValidationResult(path=path, ok=True, message="XML parse OK")
    except Exception as exc:  # pragma: no cover - defensive
        return ValidationResult(path=path, ok=False, message=f"XML parse failed: {exc}")


def validate_json_file(path: Path) -> ValidationResult:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return ValidationResult(path=path, ok=True, message="JSON parse OK")
    except Exception as exc:  # pragma: no cover - defensive
        return ValidationResult(path=path, ok=False, message=f"JSON parse failed: {exc}")


def build_local_test_plan(repo_root: Path, targets: Sequence[str]) -> list[PlanStep]:
    plan: list[PlanStep] = []

    if "outlook" in targets:
        outlook_dir = repo_root / "integrations" / "outlook-email-addin"
        plan.extend(
            [
                PlanStep("validation", "Validate Outlook manifest XML"),
                PlanStep("command", "Outlook add-in unit tests", command=("npm", "test"), cwd=outlook_dir),
                PlanStep("command", "Outlook package dry-run", command=("npm", "pack", "--dry-run"), cwd=outlook_dir),
                PlanStep(
                    "command",
                    "Email survivability integration tests",
                    command=("uv", "run", "pytest", "enterprise_api/tests/test_email_embedding_survivability.py", "-q"),
                    cwd=repo_root,
                ),
            ]
        )

    if "office" in targets:
        office_dir = repo_root / "integrations" / "microsoft-office-addin"
        plan.extend(
            [
                PlanStep("validation", "Validate Microsoft Office manifest XML"),
                PlanStep("command", "Microsoft Office add-in unit tests", command=("npm", "test"), cwd=office_dir),
                PlanStep("command", "Microsoft Office package dry-run", command=("npm", "pack", "--dry-run"), cwd=office_dir),
            ]
        )

    if "google_docs" in targets:
        gdocs_dir = repo_root / "integrations" / "google-docs-addon"
        plan.extend(
            [
                PlanStep("validation", "Validate Google Docs appsscript JSON"),
                PlanStep("command", "Google Docs add-on unit tests", command=("npm", "test"), cwd=gdocs_dir),
                PlanStep("command", "Google Docs package dry-run", command=("npm", "pack", "--dry-run"), cwd=gdocs_dir),
            ]
        )

    return plan


def build_deploy_plan(targets: Sequence[str]) -> list[PlanStep]:
    steps: list[PlanStep] = []

    if "outlook" in targets:
        steps.append(
            PlanStep(
                "manual",
                "Outlook: Upload manifest in Outlook web/desktop for custom add-in testing, then stage M365 Admin Center rollout.",
            )
        )
    if "office" in targets:
        steps.append(
            PlanStep(
                "manual",
                "Word/Excel/PowerPoint: Upload Office manifest for sideload testing in each host, then stage tenant deployment.",
            )
        )
    if "google_docs" in targets:
        steps.append(
            PlanStep(
                "manual",
                "Google Docs: Push via clasp, run Test deployments, then proceed to Workspace domain rollout/Marketplace submission.",
            )
        )

    return steps


def _validation_targets(repo_root: Path, targets: Sequence[str]) -> list[Path]:
    manifests: list[Path] = []
    if "outlook" in targets:
        manifests.append(repo_root / "integrations" / "outlook-email-addin" / "manifest.xml")
    if "office" in targets:
        manifests.append(repo_root / "integrations" / "microsoft-office-addin" / "manifest.xml")
    return manifests


def run_local_test_plan(repo_root: Path, targets: Sequence[str], execute: bool) -> tuple[list[str], bool]:
    lines: list[str] = []
    ok = True

    xml_paths = _validation_targets(repo_root, targets)
    for xml_path in xml_paths:
        result = validate_xml_file(xml_path)
        lines.append(f"- [{'x' if result.ok else ' '}] {result.path}: {result.message}")
        ok = ok and result.ok

    if "google_docs" in targets:
        json_path = repo_root / "integrations" / "google-docs-addon" / "appsscript.json"
        result = validate_json_file(json_path)
        lines.append(f"- [{'x' if result.ok else ' '}] {result.path}: {result.message}")
        ok = ok and result.ok

    for step in build_local_test_plan(repo_root, targets):
        if step.kind != "command":
            continue
        command_render = " ".join(step.command)
        if not execute:
            lines.append(f"- [ ] {step.description}: {command_render} (cwd={step.cwd})")
            continue

        proc = subprocess.run(step.command, cwd=step.cwd, check=False)
        passed = proc.returncode == 0
        ok = ok and passed
        lines.append(f"- [{'x' if passed else ' '}] {step.description}: {command_render} (exit={proc.returncode})")

    return lines, ok


def _report_header(targets: Sequence[str], mode: str) -> list[str]:
    return [
        "# Integrations Installer Report",
        "",
        f"Mode: `{mode}`",
        f"Targets: `{', '.join(targets)}`",
        "",
    ]


def _print_plan(title: str, steps: Iterable[PlanStep]) -> None:
    print(title)
    for step in steps:
        if step.command:
            print(f"- {step.description}: {' '.join(step.command)} (cwd={step.cwd})")
        else:
            print(f"- {step.description}")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    targets = resolve_targets(args)

    report_lines = _report_header(targets, args.mode)

    if args.mode == "deploy-plan":
        steps = build_deploy_plan(targets)
        _print_plan("Deploy plan:", steps)
        report_lines.extend([f"- [ ] {step.description}" for step in steps])
        success = True
    else:
        steps = build_local_test_plan(repo_root, targets)
        _print_plan("Local-test plan:", steps)
        lines, success = run_local_test_plan(repo_root=repo_root, targets=targets, execute=args.execute)
        report_lines.extend(lines)

    if args.report_file:
        args.report_file.parent.mkdir(parents=True, exist_ok=True)
        args.report_file.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
        print(f"Wrote report: {args.report_file}")

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
