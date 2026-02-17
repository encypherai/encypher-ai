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


def test_plugin_uses_supported_sign_and_verify_endpoints() -> None:
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

    assert "'/enterprise/embeddings/encode-with-embeddings'" not in src
    assert "'/sign'" in src
    # /sign/advanced is deprecated (returns 410), plugin should use /sign with options
    # assert "'/sign/advanced'" in src  # Deprecated
    assert "'/verify'" in src
    # /verify/advanced causes strict hard-binding behavior for mutated visible text;
    # plugin verification should use the public /verify endpoint.
    assert "'/verify/advanced'" not in src


def test_plugin_requests_embedding_plan_and_has_plan_application_path() -> None:
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

    assert "'return_embedding_plan' => true" in src
    assert "resolve_signed_text_with_embedding_plan" in src


def test_verify_text_extraction_preserves_inline_boundaries_without_forced_spaces() -> None:
    repo_root = _repo_root()
    parser_php = (
        repo_root
        / "integrations"
        / "wordpress-provenance-plugin"
        / "plugin"
        / "encypher-provenance"
        / "includes"
        / "class-encypher-provenance-html-parser.php"
    )
    src = parser_php.read_text(encoding="utf-8")

    assert "function extract_text_for_verify" in src
    # Guard against reintroducing unconditional inter-fragment spaces.
    assert "return implode(' ', $parts);" not in src
    # Gap handling should be explicit and aware of block-vs-inline boundaries.
    assert "gap_requires_space" in src


def test_verify_response_prefers_signing_identity_and_full_manifest_payload() -> None:
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

    assert "resolve_signing_identity" in src
    assert "build_manifest_payload_for_display" in src
    assert "$normalized['signer_name'] = $normalized['signing_identity'] ?: $this->resolve_signer_display($verdict);" in src


def test_wordpress_plugin_docs_do_not_reference_legacy_embeddings_endpoints() -> None:
    repo_root = _repo_root()
    docs = [
        repo_root / "integrations" / "wordpress-provenance-plugin" / "README.md",
        repo_root / "integrations" / "wordpress-provenance-plugin" / "INTEGRATION_SUMMARY.md",
        repo_root / "integrations" / "wordpress-provenance-plugin" / "IMPLEMENTATION_COMPLETE.md",
        repo_root / "integrations" / "wordpress-provenance-plugin" / "LOCAL_TESTING_GUIDE.md",
        repo_root / "integrations" / "wordpress-provenance-plugin" / "TIER_AUDIT.md",
        repo_root / "integrations" / "wordpress-provenance-plugin" / "plugin" / "encypher-provenance" / "README.md",
    ]

    forbidden = [
        "/api/v1/enterprise/embeddings/encode-with-embeddings",
        "/enterprise/embeddings/encode-with-embeddings",
    ]

    for path in docs:
        src = path.read_text(encoding="utf-8")
        for legacy in forbidden:
            assert legacy not in src


def test_tools_router_does_not_generate_ephemeral_demo_keys() -> None:
    repo_root = _repo_root()
    tools_py = repo_root / "enterprise_api" / "app" / "routers" / "tools.py"
    src = tools_py.read_text(encoding="utf-8")

    assert "get_demo_private_key" in src
    assert "Generated ephemeral demo keys" not in src


def test_plugin_accepts_current_canonical_tier_ids() -> None:
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

    # Canonical tier ids are: free, enterprise, strategic_partner.
    # Legacy names are normalized server-side before reaching plugin settings.
    assert "free" in src
    assert "enterprise" in src
    assert "strategic_partner" in src


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


def test_plugin_has_no_legacy_settings_menu_artifacts() -> None:
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
    admin_src = admin_php.read_text(encoding="utf-8")
    assert "add_options_page" not in admin_src


def test_plugin_bulk_mark_is_not_registered_under_wp_tools_menu() -> None:
    repo_root = _repo_root()
    bulk_php = (
        repo_root
        / "integrations"
        / "wordpress-provenance-plugin"
        / "plugin"
        / "encypher-provenance"
        / "includes"
        / "class-encypher-provenance-bulk.php"
    )
    bulk_src = bulk_php.read_text(encoding="utf-8")

    assert "'tools.php'" not in bulk_src


def test_plugin_bulk_mark_links_do_not_point_to_wp_tools_menu() -> None:
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
    admin_src = admin_php.read_text(encoding="utf-8")

    assert "tools.php?page=encypher-bulk-mark" not in admin_src


def test_plugin_coalition_page_is_under_encypher_menu() -> None:
    repo_root = _repo_root()
    coalition_php = (
        repo_root
        / "integrations"
        / "wordpress-provenance-plugin"
        / "plugin"
        / "encypher-provenance"
        / "includes"
        / "class-encypher-provenance-coalition.php"
    )
    coalition_src = coalition_php.read_text(encoding="utf-8")

    assert "add_submenu_page" in coalition_src
    assert "'encypher'" in coalition_src


def test_plugin_sign_endpoint_does_not_block_resigning_marked_posts() -> None:
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

    assert "already_signed" not in src


def test_plugin_auto_sign_does_not_delete_marked_meta_as_a_bypass() -> None:
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

    assert "delete_post_meta($post_id, '_encypher_marked')" not in src


def test_plugin_does_not_log_request_uri_on_every_request() -> None:
    repo_root = _repo_root()
    plugin_php = (
        repo_root / "integrations" / "wordpress-provenance-plugin" / "plugin" / "encypher-provenance" / "includes" / "class-encypher-provenance.php"
    )
    src = plugin_php.read_text(encoding="utf-8")

    assert "Encypher: REQUEST_URI=" not in src


def test_plugin_provenance_handler_uses_global_wp_query() -> None:
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

    assert "new \\WP_Query" in src or "use WP_Query;" in src


def test_plugin_ui_does_not_use_emoji_status_glyphs() -> None:
    repo_root = _repo_root()
    plugin_root = repo_root / "integrations" / "wordpress-provenance-plugin" / "plugin" / "encypher-provenance"

    targets = [
        plugin_root / "includes" / "class-encypher-provenance-admin.php",
        plugin_root / "includes" / "class-encypher-provenance-frontend.php",
        plugin_root / "assets" / "js" / "editor-sidebar.js",
        plugin_root / "assets" / "js" / "settings-page.js",
        plugin_root / "admin" / "partials" / "coalition-page.php",
        plugin_root / "admin" / "partials" / "coalition-widget.php",
        plugin_root / "templates" / "provenance-report.php",
    ]

    forbidden = ["✅", "❌", "✓", "✗"]
    for path in targets:
        src = path.read_text(encoding="utf-8")
        for glyph in forbidden:
            assert glyph not in src
