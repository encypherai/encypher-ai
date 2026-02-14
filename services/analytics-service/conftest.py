"""Root conftest for analytics-service tests.

Ensures the analytics-service app package is importable regardless of
how pytest is invoked (from repo root or service directory).
"""

import sys
import os

# Ensure this service's directory is first on sys.path so that
# `import app` resolves to the analytics-service app, not another service.
_service_dir = os.path.dirname(os.path.abspath(__file__))
if _service_dir not in sys.path:
    sys.path.insert(0, _service_dir)
