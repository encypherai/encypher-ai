#!/usr/bin/env python3
"""
DEPRECATED: Use the canonical setup script instead:

    cd services/billing-service
    uv run python scripts/setup_stripe.py [--dry-run]

This wrapper exists for backward compatibility only.
"""

import subprocess
import sys
from pathlib import Path

billing_service_dir = Path(__file__).parent.parent / "services" / "billing-service"
script = billing_service_dir / "scripts" / "setup_stripe.py"

if not script.exists():
    print(f"Error: {script} not found")
    sys.exit(1)

sys.exit(subprocess.call(["uv", "run", "python", str(script), *sys.argv[1:]], cwd=str(billing_service_dir)))
