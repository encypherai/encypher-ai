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
    assert "response_embeddings" in src
    assert "$clean_content = $this->strip_c2pa_embeddings($post->post_content);" in src


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
    js_file = repo_root / "integrations" / "wordpress-provenance-plugin" / "plugin" / "encypher-provenance" / "assets" / "js" / "settings-page.js"

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
    assert "const $status = $('#connection-status');" in js_src
    assert 'status-text-success">Connected</span>' in js_src
    assert 'status-text-error">Not connected</span>' in js_src


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


def test_settings_sanitization_guards_against_non_array_options_payloads() -> None:
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

    assert "if (! is_array($current_settings))" in src
    assert "if (! is_array($fallback))" in src


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
    assert "What is hard binding?" not in src
    assert "No verification link yet. Sign this post first." in src
    assert "Whitelabel is also available as a paid add-on for Free plans" in src
    assert "1,000 sign requests/month included; $0.02/sign request after the monthly cap." in src
    assert "Verification requests remain available with a soft cap of 10,000/month." in src


def test_editor_sidebar_surfaces_encypher_branding_c2pa_compatibility_and_free_plan_cap() -> None:
    repo_root = _repo_root()
    sidebar_js = repo_root / "integrations" / "wordpress-provenance-plugin" / "plugin" / "encypher-provenance" / "assets" / "js" / "editor-sidebar.js"
    src = sidebar_js.read_text(encoding="utf-8")

    assert "Encypher powers this provenance workflow with C2PA-compatible signing and verification." in src
    assert "Free plan includes up to 1,000 sign requests/month." in src
    assert "$0.02/sign request after the monthly cap." in src
    assert "Verification stays available with a soft cap of 10,000 requests/month." in src
    assert "Whitelabel and advanced controls are available as add-ons, or included with Enterprise." in src
    assert "Encypher Content Signing (C2PA-compatible)" in src
    assert "View C2PA Manifest" in src
    assert "Upgrade to view the underlying C2PA manifest." not in src
    assert "renderUpgradeCallout" not in src


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
    sidebar_js = repo_root / "integrations" / "wordpress-provenance-plugin" / "plugin" / "encypher-provenance" / "assets" / "js" / "editor-sidebar.js"

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

    assert "const [usage, setUsage] = useState(" in sidebar_src
    assert "setUsage(response.usage.api_calls);" in sidebar_src
    assert "EncypherProvenanceConfig.usage" in sidebar_src
    assert "Monthly API call usage" in sidebar_src


def test_status_endpoint_returns_usage_snapshot_for_sidebar_refresh() -> None:
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

    assert "public function handle_status_request" in src
    assert "'usage' =>" in src
    assert "resolve_usage_snapshot" in src
    assert "fetch_remote_usage_quota" in src
    assert "'/account/quota'" in src
    assert "increment_usage_snapshot" not in src


def test_coalition_routes_use_dashboard_endpoint_and_valid_settings_slug() -> None:
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
    coalition_page = (
        repo_root / "integrations" / "wordpress-provenance-plugin" / "plugin" / "encypher-provenance" / "admin" / "partials" / "coalition-page.php"
    )
    coalition_widget = (
        repo_root / "integrations" / "wordpress-provenance-plugin" / "plugin" / "encypher-provenance" / "admin" / "partials" / "coalition-widget.php"
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

    coalition_src = coalition_php.read_text(encoding="utf-8")
    page_src = coalition_page.read_text(encoding="utf-8")
    widget_src = coalition_widget.read_text(encoding="utf-8")
    bulk_src = bulk_php.read_text(encoding="utf-8")

    assert "/coalition/dashboard" in coalition_src
    assert "/coalition/stats" not in coalition_src
    assert "build_empty_stats_payload" in coalition_src
    assert "$status_code >= 500" in coalition_src

    assert "page=encypher-settings" in page_src
    assert "page=encypher-settings" in widget_src
    assert "page=encypher-provenance" not in page_src
    assert "page=encypher-provenance" not in widget_src
    assert "$has_coalition_traction" in page_src
    assert "$has_coalition_traction" in widget_src
    assert "Coalition is in early rollout" in page_src
    assert "Coalition is in early rollout" in widget_src
    assert "encypher-page-title" in page_src
    assert "encypher_full_logo_color.svg" in page_src

    assert "encypher-page-title" in bulk_src
    assert "encypher_full_logo_color.svg" in bulk_src


def test_analytics_page_uses_icon_cards_and_section_scaffolding() -> None:
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

    assert "analytics-card-icon" in src
    assert "analytics-card-label" in src
    assert "encypher-analytics-section" in src
    assert "encypher-activity-table" in src
    assert "encypher-status-pill" in src
    assert "encypher-page-title" in src
    assert "encypher-title-divider" in src
    assert "c2pa_protected" in src
    assert "encypher_signed" in src
    assert "encypher_full_logo_color.svg" in src


def test_settings_no_longer_exposes_hard_binding_toggle_and_forces_it_enabled() -> None:
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

    assert "encypher_provenance_add_hard_binding" not in src
    assert "render_add_hard_binding_field" not in src
    assert "$sanitized['add_hard_binding'] = true;" in src


def test_dashboard_includes_support_contact_cta() -> None:
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

    assert "wp-support@encypherai.com" in src
    assert "Need help? Contact support" in src


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


def test_auto_sign_respects_configured_post_types_setting() -> None:
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

    # Both auto_sign_on_publish and auto_sign_on_update must check configured post_types
    # rather than hardcoding 'post' only.
    publish_marker = "public function auto_sign_on_publish"
    update_marker = "public function auto_sign_on_update"

    publish_start = src.find(publish_marker)
    update_start = src.find(update_marker)
    assert publish_start != -1
    assert update_start != -1

    publish_window = src[publish_start : publish_start + 1200]
    update_window = src[update_start : update_start + 1800]

    # Must read post_types from settings, not hardcode 'post'
    assert "$settings['post_types']" in publish_window
    assert "in_array($post->post_type, $configured_post_types" in publish_window
    assert "'post' !== $post->post_type" not in publish_window

    assert "$settings['post_types']" in update_window
    assert "in_array($post->post_type, $configured_post_types" in update_window
    assert "'post' !== $post->post_type" not in update_window


def test_content_page_has_pagination_and_respects_configured_post_types() -> None:
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

    fn_marker = "public function render_content_page"
    start = src.find(fn_marker)
    assert start != -1
    # Find the next public function to bound the search window
    next_fn = src.find("\n    public function ", start + len(fn_marker))
    window = src[start:next_fn] if next_fn != -1 else src[start:]

    # Must use a variable for per_page (not hardcoded inline) and support pagination
    assert "$per_page" in window
    assert "'paged' =>" in window
    assert "total_pages" in window
    assert "tablenav bottom" in window
    assert "pagination-links" in window

    # Must use configured post_types, not hardcoded ['post', 'page']
    assert "$configured_post_types" in window
    assert "$settings['post_types']" in window


def test_all_debug_logging_gated_behind_wp_debug() -> None:
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

    # All operational error_log calls must be routed through debug_log()
    # which is gated behind WP_DEBUG. No bare error_log('Encypher: ...') in production paths.
    assert "private function debug_log" in src
    assert "defined('WP_DEBUG') && WP_DEBUG" in src

    # Count bare error_log calls (excluding the one inside debug_log itself)
    debug_log_fn_start = src.find("private function debug_log")
    debug_log_fn_end = src.find("\n    }", debug_log_fn_start) + 6
    src_without_debug_fn = src[:debug_log_fn_start] + src[debug_log_fn_end:]

    import re

    bare_calls = re.findall(r"\berror_log\s*\(", src_without_debug_fn)
    assert len(bare_calls) == 0, f"Found {len(bare_calls)} bare error_log() call(s) outside debug_log(): {bare_calls}"


def test_content_page_signed_status_guidance_distinguishes_verified_vs_embedded() -> None:
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

    # Signed-but-not-yet-verified posts should show a prompt to verify, not claim verification is available
    assert "Provenance embedded. Run Verify to confirm integrity." in src
    # Explicitly verified posts show the stronger claim
    assert "Verified provenance is available." in src
    # The verified state must be gated on c2pa_verified status
    assert "'c2pa_verified' === $status" in src


def test_error_log_class_exists_with_required_interface() -> None:
    repo_root = _repo_root()
    error_log_php = (
        repo_root
        / "integrations"
        / "wordpress-provenance-plugin"
        / "plugin"
        / "encypher-provenance"
        / "includes"
        / "class-encypher-provenance-error-log.php"
    )
    src = error_log_php.read_text(encoding="utf-8")

    # Core public API
    assert "class ErrorLog" in src
    assert "public static function record_failure" in src
    assert "public static function record_success" in src
    assert "public static function get_log_for_tier" in src
    assert "public static function get_raw_log" in src
    assert "public static function clear" in src
    assert "public static function maybe_fire_webhook" in src
    assert "public static function get_consecutive_failures" in src

    # Ring buffer constants
    assert "const OPTION_KEY" in src
    assert "const MAX_ENTRIES" in src
    assert "const DISPLAY_FREE" in src

    # Per-post meta keys
    assert "_encypher_last_sign_error" in src
    assert "_encypher_consecutive_failures" in src or "CONSECUTIVE_META" in src

    # Webhook fires only when URL is configured
    assert "error_webhook_url" in src
    assert "wp_remote_post" in src

    # Tier gating: enterprise sees full log, free sees DISPLAY_FREE entries
    assert "enterprise" in src
    assert "strategic_partner" in src
    assert "array_slice" in src


def test_error_log_class_is_required_in_plugin_bootstrap() -> None:
    repo_root = _repo_root()
    bootstrap_php = (
        repo_root / "integrations" / "wordpress-provenance-plugin" / "plugin" / "encypher-provenance" / "includes" / "class-encypher-provenance.php"
    )
    src = bootstrap_php.read_text(encoding="utf-8")
    assert "class-encypher-provenance-error-log.php" in src


def test_perform_signing_records_failure_and_success_in_error_log() -> None:
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

    fn_marker = "private function perform_signing"
    start = src.find(fn_marker)
    assert start != -1
    next_fn = src.find("\n    ", start + len(fn_marker) + 200)
    window = src[start : start + 3000]

    # Must record failure with error code + message
    assert "ErrorLog::record_failure(" in window
    assert "ErrorLog::record_success(" in window
    # Must fire webhook on failure
    assert "ErrorLog::maybe_fire_webhook(" in window
    # Consecutive failure count must be passed to webhook payload
    assert "ErrorLog::get_consecutive_failures(" in window


def test_admin_notice_shown_on_post_edit_screen_for_failed_auto_sign() -> None:
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

    # Notice renderer must exist and be registered
    assert "public function render_sign_error_notice" in src
    assert "add_action('admin_notices', [$this, 'render_sign_error_notice'])" in src

    fn_marker = "public function render_sign_error_notice"
    start = src.find(fn_marker)
    assert start != -1
    window = src[start : start + 2500]

    # Must check we're on a post edit screen
    assert "get_current_screen" in window
    # Must read per-post error meta
    assert "_encypher_last_sign_error" in window
    # Must show consecutive failure count
    assert "consecutive" in window
    # Must link to error log and settings
    assert "encypher-analytics#error-log" in window
    assert "encypher-settings" in window
    # Must be dismissible via AJAX
    assert "encypher_dismiss_sign_error" in window
    assert "ajax_dismiss_sign_error" in src


def test_webhook_setting_is_enterprise_only_and_sanitized() -> None:
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

    # Setting section must exist
    assert "Alerting & Error Reporting" in src
    assert "Failure webhook URL" in src
    assert "Alert after N consecutive failures" in src

    # Field renderers must exist
    assert "public function render_error_webhook_url_field" in src
    assert "public function render_error_webhook_threshold_field" in src

    # Sanitize: free tier always clears webhook URL
    sanitize_marker = "public function sanitize_settings"
    start = src.find(sanitize_marker)
    assert start != -1
    next_fn = src.find("\n    private function ", start)
    window = src[start:next_fn] if next_fn != -1 else src[start : start + 5000]
    assert "error_webhook_url" in window
    assert "error_webhook_threshold" in window
    assert "is_enterprise_tier" in window
    assert "esc_url_raw" in window


def test_analytics_page_has_error_log_section_with_tier_gating() -> None:
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

    fn_marker = "public function render_analytics_page"
    start = src.find(fn_marker)
    assert start != -1
    next_fn = src.find("\n    private function ", start)
    window = src[start:next_fn] if next_fn != -1 else src[start : start + 10000]

    # Error log section must be present
    assert 'id="error-log"' in window
    assert "Error Log" in window

    # Must use ErrorLog class
    assert "ErrorLog::get_log_for_tier(" in window
    assert "ErrorLog::get_raw_log(" in window
    assert "ErrorLog::DISPLAY_FREE" in window

    # Tier gating: enterprise sees full log + export, free sees truncated
    assert "Export CSV" in window
    assert "encypher_export_error_log" in window
    assert "Upgrade to Enterprise" in window

    # Clear log button must be present
    assert "encypher_clear_error_log" in window

    # Table columns
    assert "Error code" in window
    assert "Streak" in window
    assert "consecutive_failures" in window


def test_admin_ajax_handlers_registered_for_error_log() -> None:
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

    # Both handlers must be registered
    assert "wp_ajax_encypher_clear_error_log" in src
    assert "wp_ajax_encypher_export_error_log" in src

    # Both handler methods must exist
    assert "public function ajax_clear_error_log" in src
    assert "public function ajax_export_error_log" in src

    # Export must be enterprise-gated
    export_marker = "public function ajax_export_error_log"
    start = src.find(export_marker)
    assert start != -1
    window = src[start : start + 1200]
    assert "enterprise" in window
    assert "strategic_partner" in window
    assert "text/csv" in window
    assert "fputcsv" in window


def test_manual_sign_records_success_in_error_log() -> None:
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

    fn_marker = "public function handle_sign_request"
    start = src.find(fn_marker)
    assert start != -1
    next_fn = src.find("\n    public function ", start + len(fn_marker) + 100)
    window = src[start:next_fn] if next_fn != -1 else src[start : start + 5000]

    # Manual sign success path must clear the error streak
    assert "ErrorLog::record_success(" in window
    # Must NOT record failure (manual sign surfaces errors inline to the JS caller)
    # but success must always clear the streak
    assert "ErrorLog::record_success($post_id)" in window


def test_verify_hits_counter_incremented_on_every_verify_call() -> None:
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

    # increment_verify_hits must exist as a private method
    assert "private function increment_verify_hits" in src

    fn_marker = "private function increment_verify_hits"
    start = src.find(fn_marker)
    assert start != -1
    window = src[start : start + 1000]

    # Must use wp_options for persistence
    assert "encypher_verify_hits" in window
    assert "encypher_verify_hits_daily" in window
    # Must prune daily buckets older than 30 days
    assert "30 days" in window or "-30 days" in window
    # Must be called from handle_verify_request
    verify_fn = src.find("public function handle_verify_request")
    assert verify_fn != -1
    next_fn = src.find("\n    public function ", verify_fn + 100)
    verify_window = src[verify_fn:next_fn] if next_fn != -1 else src[verify_fn : verify_fn + 3000]
    assert "increment_verify_hits" in verify_window


def test_analytics_page_shows_real_verify_hits_from_wp_options() -> None:
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

    fn_marker = "public function render_analytics_page"
    start = src.find(fn_marker)
    assert start != -1
    next_fn = src.find("\n    private function ", start)
    window = src[start:next_fn] if next_fn != -1 else src[start : start + 12000]

    # Must read real data from wp_options
    assert "encypher_verify_hits" in window
    assert "encypher_verify_hits_daily" in window
    # Must show 30d count
    assert "verify_hits_30d" in window
    # Must show lifetime total
    assert "verify_hits_total" in window
    # Must NOT contain hardcoded fake number
    assert "1,245" not in window
    # Card must be present for all tiers (no enterprise gate)
    assert "Verification Hits (30d)" in window


def test_enterprise_api_does_not_register_public_verify_route() -> None:
    repo_root = _repo_root()
    verification_py = repo_root / "enterprise_api" / "app" / "routers" / "verification.py"
    src = verification_py.read_text(encoding="utf-8")

    # POST /api/v1/verify is routed by Traefik to the verification-service.
    # The enterprise API must NOT register this route — doing so would shadow
    # the Traefik routing and break public verification for all WordPress sites.
    assert 'router.post("/verify"' not in src
    assert "router.post('/verify')" not in src
    assert "verify_deprecated" not in src
    assert "verify_public" not in src
    # /verify/advanced is the enterprise-API-specific authenticated endpoint
    assert '"/verify/advanced"' in src or "'/verify/advanced'" in src


def test_webhook_test_endpoint_uses_module_level_httpx_import() -> None:
    repo_root = _repo_root()
    webhooks_py = repo_root / "enterprise_api" / "app" / "routers" / "webhooks.py"
    src = webhooks_py.read_text(encoding="utf-8")

    # httpx must be imported at module level (not inside function body)
    lines = src.splitlines()
    import_line = next((i for i, l in enumerate(lines) if l.strip() == "import httpx"), None)
    assert import_line is not None, "httpx must be imported at module level"
    # Must be in the top-level imports (before any function/class definition)
    first_def = next((i for i, l in enumerate(lines) if l.startswith("@router") or l.startswith("async def") or l.startswith("def ")), len(lines))
    assert import_line < first_def, "httpx import must appear before any route definitions"


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
