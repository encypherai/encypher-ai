#!/usr/bin/env python
"""Script to build and publish the package to PyPI using UV."""

import glob
import os
import shutil
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
    for path in ("dist", "build"):
        if os.path.isdir(path):
            shutil.rmtree(path)
    for egg_info in glob.glob("*.egg-info"):
        if os.path.isdir(egg_info):
            shutil.rmtree(egg_info)

    # Build the package using UV
    run_command("uv pip build .")

    # Check if we should upload to PyPI
    if len(sys.argv) > 1 and sys.argv[1] == "--publish":
        # Upload to PyPI using UV
        dist_files = glob.glob(os.path.join("dist", "*"))
        if not dist_files:
            raise RuntimeError("No dist artifacts found to publish")
        run_command("uv pip publish " + " ".join(dist_files))
    else:
        print("Package built successfully. Run with --publish to upload to PyPI.")


if __name__ == "__main__":
    main()
