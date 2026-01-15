from __future__ import annotations

import re
from pathlib import Path


def test_dashboard_page_avoids_time_dependent_ssr_hydration() -> None:
    """Guardrail: Dashboard app router renders client components on the server.

    If we compute time-dependent strings (e.g., greeting) during render, SSR/CSR can
    diverge and trigger hydration errors.
    """

    repo_root = Path(__file__).resolve().parents[2]
    page_path = repo_root / "apps" / "dashboard" / "src" / "app" / "page.tsx"
    text = page_path.read_text(encoding="utf-8")

    # Rendering must not depend on time; client-only effects are allowed.
    assert "const greeting = new Date().getHours()" not in text
    assert "let greeting = new Date().getHours()" not in text
    assert "var greeting = new Date().getHours()" not in text

    # placeholderData must be deterministic (no new Date() inside it)
    match = re.search(r"placeholderData\s*:\s*\{(?P<body>.*?)\}\s*,\s*\n\s*\}\);", text, re.DOTALL)
    if match:
        assert "new Date(" not in match.group("body")
