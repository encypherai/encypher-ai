#!/usr/bin/env python3
"""
Test Coverage Script for EncypherAI Commercial

Runs pytest with coverage on all Python services and generates a report.

Usage:
    python scripts/run_test_coverage.py [--service SERVICE_NAME]
"""
import subprocess
import sys
import argparse
from pathlib import Path
from typing import Dict, Tuple, Optional

# Services with their test directories
SERVICES = [
    ("auth-service", "services/auth-service", "app"),
    ("key-service", "services/key-service", "app"),
    ("billing-service", "services/billing-service", "app"),
    ("analytics-service", "services/analytics-service", "app"),
    ("user-service", "services/user-service", "app"),
    ("notification-service", "services/notification-service", "app"),
    ("encoding-service", "services/encoding-service", "app"),
    ("verification-service", "services/verification-service", "app"),
    ("coalition-service", "services/coalition-service", "app"),
    ("enterprise-api", "enterprise_api", "app"),
]


def run_coverage(service_path: str, source_dir: str) -> Tuple[float, int, int, str]:
    """
    Run pytest with coverage on a service.
    Returns (coverage_percent, tests_passed, tests_failed, output)
    """
    tests_path = Path(service_path) / "tests"
    source_path = Path(service_path) / source_dir
    
    if not tests_path.exists():
        return -1, 0, 0, "No tests directory found"
    
    if not source_path.exists():
        return -1, 0, 0, "No source directory found"
    
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                str(tests_path),
                f"--cov={source_path}",
                "--cov-report=term-missing",
                "--cov-fail-under=0",
                "-v",
                "--tb=short",
                "-q"
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=service_path,
            timeout=300
        )
        
        output = result.stdout + result.stderr
        
        # Parse coverage percentage
        coverage = 0.0
        for line in output.split('\n'):
            if 'TOTAL' in line and '%' in line:
                parts = line.split()
                for part in parts:
                    if '%' in part:
                        try:
                            coverage = float(part.replace('%', ''))
                            break
                        except ValueError:
                            pass
        
        # Parse test results
        passed = 0
        failed = 0
        for line in output.split('\n'):
            if 'passed' in line.lower():
                parts = line.split()
                for i, part in enumerate(parts):
                    if 'passed' in part.lower() and i > 0:
                        try:
                            passed = int(parts[i-1])
                        except ValueError:
                            pass
            if 'failed' in line.lower():
                parts = line.split()
                for i, part in enumerate(parts):
                    if 'failed' in part.lower() and i > 0:
                        try:
                            failed = int(parts[i-1])
                        except ValueError:
                            pass
        
        return coverage, passed, failed, output
    except subprocess.TimeoutExpired:
        return -1, 0, 0, "Test timed out after 300 seconds"
    except Exception as e:
        return -1, 0, 0, str(e)


def main():
    parser = argparse.ArgumentParser(description="Run test coverage for services")
    parser.add_argument("--service", "-s", help="Run coverage for specific service only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Test Coverage Report for EncypherAI Commercial")
    print("=" * 60)
    
    results: Dict[str, Tuple[float, int, int]] = {}
    
    services_to_run = SERVICES
    if args.service:
        services_to_run = [(n, p, s) for n, p, s in SERVICES if args.service.lower() in n.lower()]
        if not services_to_run:
            print(f"Service '{args.service}' not found")
            return 1
    
    for name, path, source in services_to_run:
        if not Path(path).exists():
            print(f"\n{name}: [SKIP] Path not found")
            continue
        
        print(f"\nRunning tests for {name}...", flush=True)
        coverage, passed, failed, output = run_coverage(path, source)
        
        if coverage == -1:
            print(f"  [SKIP] {output}")
            continue
        
        results[name] = (coverage, passed, failed)
        
        status = "[OK]" if failed == 0 else "[FAIL]"
        cov_status = "[LOW]" if coverage < 50 else "[OK]" if coverage >= 80 else "[MED]"
        print(f"  Coverage: {coverage:.1f}% {cov_status}")
        print(f"  Tests: {passed} passed, {failed} failed {status}")
        
        if args.verbose and output:
            print("\n  --- Output ---")
            for line in output.split('\n')[-20:]:
                print(f"  {line}")
    
    # Summary
    print(f"\n{'='*60}")
    print("COVERAGE SUMMARY")
    print(f"{'='*60}")
    
    if not results:
        print("No test results collected")
        return 1
    
    print(f"\n{'Service':<25} {'Coverage':>10} {'Passed':>8} {'Failed':>8}")
    print("-" * 55)
    
    total_passed = 0
    total_failed = 0
    coverages = []
    
    for name, (coverage, passed, failed) in sorted(results.items(), key=lambda x: -x[1][0]):
        status = "[OK]" if failed == 0 else "[FAIL]"
        cov_icon = "!" if coverage < 50 else "~" if coverage < 80 else "+"
        print(f"{name:<25} {coverage:>9.1f}% {passed:>8} {failed:>8} {cov_icon}")
        total_passed += passed
        total_failed += failed
        coverages.append(coverage)
    
    avg_coverage = sum(coverages) / len(coverages) if coverages else 0
    
    print("-" * 55)
    print(f"{'TOTAL':<25} {avg_coverage:>9.1f}% {total_passed:>8} {total_failed:>8}")
    
    print(f"\nCoverage Legend: + >= 80%, ~ 50-79%, ! < 50%")
    
    if total_failed > 0:
        print(f"\n[!] {total_failed} tests failed!")
        return 1
    elif avg_coverage < 50:
        print(f"\n[!] Average coverage ({avg_coverage:.1f}%) is below 50%")
        return 1
    else:
        print(f"\n[OK] All tests passed, average coverage: {avg_coverage:.1f}%")
        return 0


if __name__ == "__main__":
    sys.exit(main())
