#!/usr/bin/env python
"""Script to build and publish the package to PyPI using UV."""
import subprocess
import sys


def run_command(command: str) -> subprocess.CompletedProcess:
    """Run a shell command and print output."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=True)
    return result


def main() -> None:
    """Build and publish the package using UV."""
    # Clean previous builds
    run_command("rm -rf dist/ build/ *.egg-info")

    # Build the package using UV
    run_command("uv pip build .")

    # Check if we should upload to PyPI
    if len(sys.argv) > 1 and sys.argv[1] == "--publish":
        # Upload to PyPI using UV
        run_command("uv pip publish dist/*")
    else:
        print("Package built successfully. Run with --publish to upload to PyPI.")


if __name__ == "__main__":
    main()
