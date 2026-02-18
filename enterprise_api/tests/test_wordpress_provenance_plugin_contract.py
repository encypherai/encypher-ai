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

    # Canonical unified micro options (TEAM_166+):
    assert "'manifest_mode' => 'micro'" in src
    assert "'ecc' => true" in src
    assert "'embed_c2pa' => true" in src
    assert "'manifest_mode' => 'micro_ecc_c2pa'" not in src

    # Keep sentence-level signing + embedding-plan reconstruction path.
    assert "'segmentation_level' => 'sentence'" in src
    assert "'return_embedding_plan' => true" in src
    assert "resolve_signed_text_with_embedding_plan" in src


def test_mark_post_needs_verification_does_not_overwrite_signed_hash_on_manual_edit() -> None:
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

    fn_marker = "public function mark_post_needs_verification"
    start = src.find(fn_marker)
    assert start != -1
    window = src[start : start + 2200]

    # If a post is already signed and visible content changes, keep the previous
    # signed-content hash so auto_sign_on_update can detect the delta and re-sign.
    assert "_encypher_marked" in window
    assert "$is_marked && $previous_content && $previous_content !== $current_hash" in window
    assert "return;" in window


def test_call_backend_only_sends_authorization_when_auth_required() -> None:
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

    fn_marker = "private function call_backend"
    start = src.find(fn_marker)
    assert start != -1
    window = src[start : start + 1600]

    # Public verify requests must not be forced to send potentially stale/invalid
    # Authorization headers just because a key is present in plugin settings.
    assert "if ($require_auth && $api_key)" in window
    assert "} elseif ($require_auth) {" in window


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


def test_frontend_verify_modal_maps_common_error_categories() -> None:
    repo_root = _repo_root()
    frontend_php = (
        repo_root
        / "integrations"
        / "wordpress-provenance-plugin"
        / "plugin"
        / "encypher-provenance"
        / "includes"
        / "class-encypher-provenance-frontend.php"
    )
    src = frontend_php.read_text(encoding="utf-8")

    assert "function buildVerificationFailureHint" in src
    assert "Invalid API key" in src
    assert "No valid C2PA manifest found for this content." in src
    assert "Failed to verify content. Please try again." in src


def test_frontend_verify_modal_surfaces_edited_action_copy() -> None:
    repo_root = _repo_root()
    frontend_php = (
        repo_root
        / "integrations"
        / "wordpress-provenance-plugin"
        / "plugin"
        / "encypher-provenance"
        / "includes"
        / "class-encypher-provenance-frontend.php"
    )
    src = frontend_php.read_text(encoding="utf-8")

    assert "Latest action:" in src
    assert "Edited (provenance chain updated)" in src


def test_settings_page_surfaces_launch_readiness_checklist_and_health_card() -> None:
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
    js_file = (
        repo_root
        / "integrations"
        / "wordpress-provenance-plugin"
        / "plugin"
        / "encypher-provenance"
        / "assets"
        / "js"
        / "settings-page.js"
    )

    admin_src = admin_php.read_text(encoding="utf-8")
    js_src = js_file.read_text(encoding="utf-8")

    assert "Launch Readiness Checklist" in admin_src
    assert "Connection Health" in admin_src
    assert "Step 1: Configure API base URL" in admin_src
    assert "Step 2: Add API key" in admin_src
    assert "Step 3: Run connection test" in admin_src

    assert "Connected and ready" in js_src
    assert "Auth required" in js_src
    assert "Disconnected" in js_src
    assert "Last check:" in js_src


def test_content_page_surfaces_expanded_provenance_states_and_recovery_ctas() -> None:
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

    assert "Modified since signing" in src
    assert "Verification failed" in src
    assert "Unsigned (needs signing)" in src
    assert "Re-sign by updating this post." in src
    assert "Run Verify to refresh status." in src


def test_settings_page_optional_polish_includes_accessibility_live_regions() -> None:
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

    assert 'id="connection-status" role="status" aria-live="polite"' in src
    assert 'id="test-connection-result" role="status" aria-live="polite"' in src
    assert 'id="encypher-connection-health-state" class="encypher-health-state" role="status" aria-live="polite"' in src


def test_settings_page_optional_polish_includes_explanatory_help_copy() -> None:
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

    assert "What is BYOK?" in src
    assert "What is hard binding?" in src
    assert "No verification link yet. Sign this post first." in src
    assert "Whitelabel is also available as a paid add-on for Free plans" in src
    assert "1,000 sign requests/month included; $0.02/sign request after the monthly cap." in src
    assert "Verification requests remain available with a soft cap of 10,000/month." in src


def test_editor_sidebar_surfaces_encypher_branding_c2pa_compatibility_and_free_plan_cap() -> None:
    repo_root = _repo_root()
    sidebar_js = (
        repo_root
        / "integrations"
        / "wordpress-provenance-plugin"
        / "plugin"
        / "encypher-provenance"
        / "assets"
        / "js"
        / "editor-sidebar.js"
    )
    src = sidebar_js.read_text(encoding="utf-8")

    assert "Encypher powers this provenance workflow with C2PA-compatible signing and verification." in src
    assert "Free plan includes up to 1,000 sign requests/month." in src
    assert "$0.02/sign request after the monthly cap." in src
    assert "Verification stays available with a soft cap of 10,000 requests/month." in src
    assert "Whitelabel and advanced controls are available as add-ons, or included with Enterprise." in src
    assert "Encypher Content Signing (C2PA-compatible)" in src


def test_admin_pages_surface_free_plan_cap_messaging() -> None:
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

    assert "Free plan includes up to 1,000 sign requests/month for publishing workflows." in src
    assert "Need more than 1,000 sign requests/month?" in src


def test_usage_progress_bars_surface_across_plugin_surfaces() -> None:
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
    bulk_php = (
        repo_root
        / "integrations"
        / "wordpress-provenance-plugin"
        / "plugin"
        / "encypher-provenance"
        / "includes"
        / "class-encypher-provenance-bulk.php"
    )
    sidebar_js = (
        repo_root
        / "integrations"
        / "wordpress-provenance-plugin"
        / "plugin"
        / "encypher-provenance"
        / "assets"
        / "js"
        / "editor-sidebar.js"
    )

    admin_src = admin_php.read_text(encoding="utf-8")
    bulk_src = bulk_php.read_text(encoding="utf-8")
    sidebar_src = sidebar_js.read_text(encoding="utf-8")

    assert "encypher-usage-progress" in admin_src
    assert "Monthly API calls this month" in admin_src
    assert "API calls remaining this month" in admin_src
    assert "Usage resets on:" in admin_src
    assert "encypher-usage-progress-compact" in admin_src

    quick_actions_idx = admin_src.find("Quick Actions")
    dashboard_usage_idx = admin_src.find("encypher-dashboard-usage-progress")
    assert quick_actions_idx != -1
    assert dashboard_usage_idx != -1
    assert dashboard_usage_idx > quick_actions_idx

    assert "encypher-bulk-usage-progress" in bulk_src
    assert "Monthly API call usage" in bulk_src

    assert "EncypherProvenanceConfig.usage" in sidebar_src
    assert "Monthly API call usage" in sidebar_src


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
        "/api/v1/sign/advanced",
        "/api/v1/verify/advanced",
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
