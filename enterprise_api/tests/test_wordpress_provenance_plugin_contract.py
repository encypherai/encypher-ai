"""Contract tests for the WordPress provenance plugin.

These tests are intentionally lightweight and validate that the plugin:
- Uses documented Enterprise API endpoints
- Correctly handles canonical tier IDs
- Avoids obvious security footguns in public routes

The WordPress plugin does not currently ship with a PHPUnit harness in-repo,
so we enforce these invariants with repo-level pytest.
"""

from __future__ import annotations

from pathlib import Path


def _repo_root() -> Path:
    # .../enterprise_api/tests/<file>.py -> repo root is 2 levels up
    return Path(__file__).resolve().parents[2]


def test_plugin_uses_account_endpoint_for_tier_lookup() -> None:
    repo_root = _repo_root()
    admin_php = (
        repo_root
        / "integrations"
        / "wordpress-provenance-plugin"
        / "plugin"
        / "encypher-provenance"
        / "includes"
        / "class-encypher-provenance-admin.php"
    )
    rest_php = (
        repo_root
        / "integrations"
        / "wordpress-provenance-plugin"
        / "plugin"
        / "encypher-provenance"
        / "includes"
        / "class-encypher-provenance-rest.php"
    )

    admin_src = admin_php.read_text(encoding="utf-8")
    rest_src = rest_php.read_text(encoding="utf-8")

    assert "$base . '/account'" in admin_src
    assert "$base . '/stats'" not in admin_src

    assert "$base . '/account'" in rest_src
    assert "$base . '/stats'" not in rest_src


def test_plugin_accepts_canonical_tier_ids() -> None:
    repo_root = _repo_root()
    admin_php = (
        repo_root
        / "integrations"
        / "wordpress-provenance-plugin"
        / "plugin"
        / "encypher-provenance"
        / "includes"
        / "class-encypher-provenance-admin.php"
    )
    src = admin_php.read_text(encoding="utf-8")

    # Canonical tier ids are: starter, professional, business, enterprise
    assert "starter" in src
    assert "professional" in src
    assert "business" in src
    assert "enterprise" in src


def test_public_verify_requires_published_post() -> None:
    repo_root = _repo_root()
    rest_php = (
        repo_root
        / "integrations"
        / "wordpress-provenance-plugin"
        / "plugin"
        / "encypher-provenance"
        / "includes"
        / "class-encypher-provenance-rest.php"
    )
    src = rest_php.read_text(encoding="utf-8")

    # Verify endpoint is public; it must not allow verifying drafts/private posts.
    fn_marker = "public function handle_verify_request"
    start = src.find(fn_marker)
    assert start != -1
    window = src[start : start + 2500]
    assert "post_status" in window
    assert "'publish'" in window


def test_auto_mark_on_publish_setting_key_used() -> None:
    repo_root = _repo_root()
    rest_php = (
        repo_root
        / "integrations"
        / "wordpress-provenance-plugin"
        / "plugin"
        / "encypher-provenance"
        / "includes"
        / "class-encypher-provenance-rest.php"
    )
    src = rest_php.read_text(encoding="utf-8")

    assert "['auto_mark_on_publish']" in src
    assert "['auto_sign_on_publish']" not in src
