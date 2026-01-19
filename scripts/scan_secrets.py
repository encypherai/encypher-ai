#!/usr/bin/env python3
"""
Secret Scanner for Encypher Commercial

Scans the codebase for potential secrets and generates a report.
Uses detect-secrets under the hood.

Usage:
    python scripts/scan_secrets.py
"""

import json
import subprocess
import sys
from typing import Any, Dict, List

# Files/patterns that are known to contain test/example secrets (not real)
KNOWN_SAFE_PATTERNS = [
    "test",
    "example",
    "mock",
    "fixture",
    "sample",
    ".md",  # Documentation
    "PRDs/",  # Product docs
    ".pem",  # Test certificates
]

# Secret types that are commonly false positives
FALSE_POSITIVE_TYPES = [
    "Base64 High Entropy String",  # Often just encoded data
    "Hex High Entropy String",  # Often just hashes
]


def run_detect_secrets() -> Dict[str, Any]:
    """Run detect-secrets and return results."""
    try:
        result = subprocess.run(
            [
                "detect-secrets",
                "scan",
                "--exclude-files",
                r"\.git|node_modules|\.next|dist|build|\.env\.|package-lock\.json|uv\.lock|\.secrets\.baseline",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error running detect-secrets: {e}")
        return {"results": {}}


def is_likely_false_positive(filename: str, secret_types: List[str]) -> bool:
    """Check if a finding is likely a false positive."""
    # Check filename patterns
    for pattern in KNOWN_SAFE_PATTERNS:
        if pattern.lower() in filename.lower():
            return True

    # Check secret types
    for stype in secret_types:
        if stype in FALSE_POSITIVE_TYPES:
            return True

    return False


def categorize_findings(results: Dict[str, List]) -> Dict[str, List]:
    """Categorize findings into real concerns vs likely false positives."""
    real_concerns = []
    false_positives = []

    for filename, secrets in results.items():
        for secret in secrets:
            finding = {
                "file": filename,
                "line": secret.get("line_number"),
                "type": secret.get("type"),
                "hashed_secret": secret.get("hashed_secret", "")[:16] + "...",
            }

            if is_likely_false_positive(filename, [secret.get("type", "")]):
                false_positives.append(finding)
            else:
                real_concerns.append(finding)

    return {"real_concerns": real_concerns, "false_positives": false_positives}


def main():
    print("=" * 60)
    print("Secret Scanner for Encypher Commercial")
    print("=" * 60)

    print("\nScanning codebase for potential secrets...")
    scan_results = run_detect_secrets()

    if not scan_results.get("results"):
        print("\n[OK] No potential secrets found!")
        return 0

    categorized = categorize_findings(scan_results["results"])

    # Report real concerns
    real_concerns = categorized["real_concerns"]
    false_positives = categorized["false_positives"]

    print(f"\n{'=' * 60}")
    print("SCAN RESULTS")
    print(f"{'=' * 60}")
    print(f"Total findings: {len(real_concerns) + len(false_positives)}")
    print(f"Likely false positives: {len(false_positives)}")
    print(f"Potential real secrets: {len(real_concerns)}")

    if real_concerns:
        print(f"\n{'=' * 60}")
        print("POTENTIAL REAL SECRETS (Review Required)")
        print(f"{'=' * 60}")
        for finding in real_concerns[:20]:  # Limit output
            print(f"\n  File: {finding['file']}")
            print(f"  Line: {finding['line']}")
            print(f"  Type: {finding['type']}")

        if len(real_concerns) > 20:
            print(f"\n  ... and {len(real_concerns) - 20} more")

        print("\n[!] Review these files for potential secrets!")
        return 1
    else:
        print("\n[OK] No real secrets detected (only test/example data)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
