<?php
namespace EncypherAssurance;

if (! defined('ABSPATH')) {
    exit;
}

/**
 * Handles admin settings and editor integrations.
 */
class Admin
{
    private const ACCOUNT_CACHE_TTL = 900; // 15 minutes

    /**
     * Get SVG icon markup. Uses material-style stroke icons matching the design system.
     */
    private function get_icon(string $name, string $class = 'encypher-icon'): string
    {
        $icons = [
            // Encypher brand logo - simplified version of encypher_check_color.svg
            'encypher-logo' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 100 100" fill="none"><circle cx="50" cy="50" r="45" fill="#1b2f50"/><circle cx="50" cy="50" r="38" fill="none" stroke="#fff" stroke-width="3"/><path d="M35 50l10 10 20-20" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>',
            'shield' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
            'shield-check' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>',
            'document' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
            'chart' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
            'check-circle' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
            'star' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
            'file-text' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
            'zap' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
            'trending-up' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
            'settings' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
            'key' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>',
            'link' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
            'users' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
            'credit-card' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>',
            'external-link' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>',
            'check' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
            'arrow-up-right' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>',
            'award' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>',
            'layers' => '<svg class="' . esc_attr($class) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
        ];

        return $icons[$name] ?? '';
    }

    public function register_hooks(): void
    {
        add_action('admin_menu', [$this, 'register_admin_menu']);
        add_action('admin_init', [$this, 'register_settings']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_settings_page_assets']);
        add_action('enqueue_block_editor_assets', [$this, 'enqueue_block_editor_assets']);
        add_action('wp_dashboard_setup', [$this, 'register_dashboard_widget']);
        add_action('wp_ajax_encypher_dismiss_onboarding', [$this, 'ajax_dismiss_onboarding']);
        // Classic editor meta box disabled - using Gutenberg sidebar instead
        // add_action('admin_enqueue_scripts', [$this, 'enqueue_classic_assets']);
        // add_action('add_meta_boxes', [$this, 'register_classic_meta_box']);
        
        // Note: Auto-sign hooks are handled by the REST class (class-encypher-provenance-rest.php)
        // which has the proper implementation that calls the Enterprise API.
        // Do NOT add duplicate hooks here.
    }

    public function register_dashboard_widget(): void
    {
        wp_add_dashboard_widget(
            'encypher_provenance_stats',
            __('Encypher Provenance Coverage', 'encypher-provenance'),
            [$this, 'render_dashboard_widget']
        );
    }

    /**
     * Register top-level Encypher admin menu with submenu pages.
     */
    public function register_admin_menu(): void
    {
        // SVG icon for Encypher (base64 encoded)
        $icon_svg = 'data:image/svg+xml;base64,' . base64_encode('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>');

        // Main menu page (Dashboard)
        add_menu_page(
            __('Encypher', 'encypher-provenance'),
            __('Encypher', 'encypher-provenance'),
            'manage_options',
            'encypher',
            [$this, 'render_dashboard_page'],
            $icon_svg,
            30 // Position after Comments
        );

        // Dashboard submenu (same as parent)
        add_submenu_page(
            'encypher',
            __('Dashboard', 'encypher-provenance'),
            __('Dashboard', 'encypher-provenance'),
            'manage_options',
            'encypher',
            [$this, 'render_dashboard_page']
        );

        // Content submenu
        add_submenu_page(
            'encypher',
            __('Content', 'encypher-provenance'),
            __('Content', 'encypher-provenance'),
            'manage_options',
            'encypher-content',
            [$this, 'render_content_page']
        );

        // Settings submenu
        add_submenu_page(
            'encypher',
            __('Settings', 'encypher-provenance'),
            __('Settings', 'encypher-provenance'),
            'manage_options',
            'encypher-settings',
            [$this, 'render_settings_page']
        );

        // Analytics submenu
        add_submenu_page(
            'encypher',
            __('Analytics', 'encypher-provenance'),
            __('Analytics', 'encypher-provenance'),
            'manage_options',
            'encypher-analytics',
            [$this, 'render_analytics_page']
        );

        // Account submenu
        add_submenu_page(
            'encypher',
            __('Account', 'encypher-provenance'),
            __('Account', 'encypher-provenance'),
            'manage_options',
            'encypher-account',
            [$this, 'render_account_page']
        );

        // Keep legacy settings page for backward compatibility (hidden)
        add_options_page(
            __('Encypher Provenance', 'encypher-provenance'),
            __('Encypher Provenance', 'encypher-provenance'),
            'manage_options',
            'encypher-provenance-settings',
            [$this, 'render_settings_page']
        );
    }

    public function register_settings(): void
    {
        register_setting('encypher_assurance_settings_group', 'encypher_assurance_settings', [
            'type' => 'array',
            'sanitize_callback' => [$this, 'sanitize_settings'],
            'default' => [
                'api_base_url' => 'https://api.encypherai.com/api/v1',
                'api_key' => '',
                'auto_verify' => true,
                'auto_mark_on_publish' => true,
                'auto_mark_on_update' => true,
                'metadata_format' => 'c2pa',
                'add_hard_binding' => true,
                'tier' => 'starter',
                'signing_mode' => 'managed',
                'signing_profile_id' => '',
                'organization_id' => '',
                'organization_name' => '',
                'post_types' => ['post', 'page'],
            ],
        ]);

        add_settings_section(
            'encypher_assurance_main_section',
            __('API Configuration', 'encypher-provenance'),
            function () {
                echo '<p>' . esc_html__('Configure the Encypher backend connection for signing and verification.', 'encypher-provenance') . '</p>';
            },
            'encypher-provenance-settings'
        );

        add_settings_field(
            'encypher_assurance_api_base_url',
            __('API Base URL', 'encypher-provenance'),
            [$this, 'render_api_base_url_field'],
            'encypher-provenance-settings',
            'encypher_assurance_main_section'
        );

        add_settings_field(
            'encypher_assurance_api_key',
            __('API Key', 'encypher-provenance'),
            [$this, 'render_api_key_field'],
            'encypher-provenance-settings',
            'encypher_assurance_main_section'
        );

        add_settings_field(
            'encypher_assurance_auto_verify',
            __('Automatically verify content on render', 'encypher-provenance'),
            [$this, 'render_auto_verify_field'],
            'encypher-provenance-settings',
            'encypher_assurance_main_section'
        );

        // Signature Management Section
        add_settings_section(
            'encypher_assurance_signature_section',
            __('Signature Management', 'encypher-provenance'),
            function () {
                echo '<p>' . esc_html__('Manage how your content is signed. Free workspaces use Encypher-managed certificates. Pro and Enterprise can bring their own signing profiles.', 'encypher-provenance') . '</p>';
            },
            'encypher-provenance-settings'
        );

        add_settings_field(
            'encypher_assurance_signing_mode',
            __('Signature mode', 'encypher-provenance'),
            [$this, 'render_signing_mode_field'],
            'encypher-provenance-settings',
            'encypher_assurance_signature_section'
        );

        add_settings_field(
            'encypher_assurance_signing_profile_id',
            __('Signing profile ID', 'encypher-provenance'),
            [$this, 'render_signing_profile_id_field'],
            'encypher-provenance-settings',
            'encypher_assurance_signature_section'
        );

        // C2PA Settings Section
        add_settings_section(
            'encypher_assurance_c2pa_section',
            __('C2PA Settings', 'encypher-provenance'),
            function () {
                echo '<p>' . esc_html__('Configure C2PA-compliant text authentication options.', 'encypher-provenance') . '</p>';
            },
            'encypher-provenance-settings'
        );

        add_settings_field(
            'encypher_assurance_auto_mark_on_publish',
            __('Auto-mark on publish', 'encypher-provenance'),
            [$this, 'render_auto_mark_on_publish_field'],
            'encypher-provenance-settings',
            'encypher_assurance_c2pa_section'
        );

        add_settings_field(
            'encypher_assurance_auto_mark_on_update',
            __('Auto-mark on update', 'encypher-provenance'),
            [$this, 'render_auto_mark_on_update_field'],
            'encypher-provenance-settings',
            'encypher_assurance_c2pa_section'
        );

        add_settings_field(
            'encypher_assurance_metadata_format',
            __('Metadata format', 'encypher-provenance'),
            [$this, 'render_metadata_format_field'],
            'encypher-provenance-settings',
            'encypher_assurance_c2pa_section'
        );

        add_settings_field(
            'encypher_assurance_add_hard_binding',
            __('Hard binding', 'encypher-provenance'),
            [$this, 'render_add_hard_binding_field'],
            'encypher-provenance-settings',
            'encypher_assurance_c2pa_section'
        );

        add_settings_field(
            'encypher_assurance_post_types',
            __('Post types to auto-mark', 'encypher-provenance'),
            [$this, 'render_post_types_field'],
            'encypher-provenance-settings',
            'encypher_assurance_c2pa_section'
        );

        // Display Settings Section
        add_settings_section(
            'encypher_assurance_display_section',
            __('Display Settings', 'encypher-provenance'),
            function () {
                echo '<p>' . esc_html__('Configure how C2PA badges appear on your site.', 'encypher-provenance') . '</p>';
            },
            'encypher-provenance-settings'
        );

        add_settings_field(
            'encypher_assurance_show_badge',
            __('Show C2PA badge', 'encypher-provenance'),
            [$this, 'render_show_badge_field'],
            'encypher-provenance-settings',
            'encypher_assurance_display_section'
        );

        add_settings_field(
            'encypher_assurance_badge_position',
            __('Badge position', 'encypher-provenance'),
            [$this, 'render_badge_position_field'],
            'encypher-provenance-settings',
            'encypher_assurance_display_section'
        );

        add_settings_field(
            'encypher_assurance_show_branding',
            __('Whitelabeling (Hide Branding)', 'encypher-provenance'),
            [$this, 'render_show_branding_field'],
            'encypher-provenance-settings',
            'encypher_assurance_display_section'
        );

        // Tier Settings Section
        add_settings_section(
            'encypher_assurance_tier_section',
            __('Tier & Subscription', 'encypher-provenance'),
            function () {
                echo '<p>' . esc_html__('Your current subscription tier and upgrade options.', 'encypher-provenance') . '</p>';
            },
            'encypher-provenance-settings'
        );

        add_settings_field(
            'encypher_assurance_tier',
            __('Current tier', 'encypher-provenance'),
            [$this, 'render_tier_field'],
            'encypher-provenance-settings',
            'encypher_assurance_tier_section'
        );

        // Coalition Settings Section
        add_settings_section(
            'encypher_assurance_coalition_section',
            __('Coalition Membership', 'encypher-provenance'),
            function () {
                echo '<p>' . esc_html__('Participate in the Encypher Coalition to earn revenue from AI company licensing deals.', 'encypher-provenance') . '</p>';
            },
            'encypher-provenance-settings'
        );

        add_settings_field(
            'encypher_assurance_coalition_enabled',
            __('Coalition Status', 'encypher-provenance'),
            [$this, 'render_coalition_enabled_field'],
            'encypher-provenance-settings',
            'encypher_assurance_coalition_section'
        );
    }

    public function sanitize_settings(array $settings): array
    {
        $sanitized = [];
        $current_settings = get_option('encypher_assurance_settings', []);
        $sanitized['api_base_url'] = isset($settings['api_base_url']) ? esc_url_raw(trim($settings['api_base_url'])) : 'https://api.encypherai.com/api/v1';
        $sanitized['api_base_url'] = rtrim($sanitized['api_base_url'], '/');
        $sanitized['api_key'] = isset($settings['api_key']) ? sanitize_text_field($settings['api_key']) : '';
        $sanitized['auto_verify'] = isset($settings['auto_verify']) ? (bool) $settings['auto_verify'] : false;
        $sanitized['auto_mark_on_publish'] = isset($settings['auto_mark_on_publish']) ? (bool) $settings['auto_mark_on_publish'] : true;
        $sanitized['auto_mark_on_update'] = isset($settings['auto_mark_on_update']) ? (bool) $settings['auto_mark_on_update'] : true;
        $sanitized['metadata_format'] = isset($settings['metadata_format']) && in_array($settings['metadata_format'], ['basic', 'c2pa'], true) ? $settings['metadata_format'] : 'c2pa';
        $sanitized['add_hard_binding'] = isset($settings['add_hard_binding']) ? (bool) $settings['add_hard_binding'] : true;
        $sanitized['post_types'] = isset($settings['post_types']) && is_array($settings['post_types']) ? array_map('sanitize_text_field', $settings['post_types']) : ['post', 'page'];

        $account = null;
        $previous_tier = isset($current_settings['tier']) ? $current_settings['tier'] : 'starter';
        $previous_org_id = isset($current_settings['organization_id']) ? $current_settings['organization_id'] : '';
        $previous_org_name = isset($current_settings['organization_name']) ? $current_settings['organization_name'] : '';
        if (!empty($sanitized['api_key'])) {
            $account = $this->resolve_remote_account($sanitized['api_base_url'], $sanitized['api_key'], $current_settings);
            if (is_wp_error($account)) {
                add_settings_error(
                    'encypher_assurance_settings',
                    'tier_lookup_failed',
                    sprintf(
                        /* translators: %s: error message */
                        __('Unable to determine current subscription tier: %s', 'encypher-provenance'),
                        $account->get_error_message()
                    ),
                    'error'
                );
                $account = null;
            }
        }

        if (is_array($account)) {
            $sanitized['tier'] = $account['tier'];
            $sanitized['organization_id'] = $account['organization_id'];
            $sanitized['organization_name'] = $account['organization_name'];
            $sanitized['features'] = $account['features'] ?? [];
        } elseif (!empty($sanitized['api_key']) && $previous_tier !== 'starter') {
            // Keep last-known tier if dashboard lookup failed but we have a previous subscription
            $sanitized['tier'] = $previous_tier;
            $sanitized['organization_id'] = $previous_org_id;
            $sanitized['organization_name'] = $previous_org_name;
            $sanitized['features'] = isset($current_settings['features']) ? $current_settings['features'] : [];
            add_settings_error(
                'encypher_assurance_settings',
                'tier_last_known',
                __('Using last known subscription details until the dashboard becomes reachable.', 'encypher-provenance'),
                'warning'
            );
        } else {
            $sanitized['tier'] = 'starter';
            $sanitized['organization_id'] = '';
            $sanitized['organization_name'] = '';
        }

        $requested_mode = isset($settings['signing_mode']) && in_array($settings['signing_mode'], ['managed', 'byok'], true) ? $settings['signing_mode'] : 'managed';
        if ('starter' === $sanitized['tier']) {
            $sanitized['signing_mode'] = 'managed';
            $sanitized['signing_profile_id'] = '';
        } else {
            $sanitized['signing_mode'] = $requested_mode;
            if ('byok' === $sanitized['signing_mode']) {
                $profile_id = isset($settings['signing_profile_id']) ? sanitize_text_field((string) $settings['signing_profile_id']) : '';
                if ($profile_id) {
                    $sanitized['signing_profile_id'] = $profile_id;
                } else {
                    add_settings_error(
                        'encypher_assurance_settings',
                        'missing_signing_profile',
                        __('Please enter the Signing Profile ID from the Encypher dashboard when BYOK mode is enabled.', 'encypher-provenance'),
                        'error'
                    );
                    $sanitized['signing_mode'] = 'managed';
                    $sanitized['signing_profile_id'] = '';
                }
            } else {
                $sanitized['signing_profile_id'] = '';
            }
        }
        
        // Free tier: badge must always be shown, coalition always enabled
        if ($sanitized['tier'] === 'starter') {
            $sanitized['show_badge'] = true;
            $sanitized['badge_position'] = 'bottom-right';
            $sanitized['coalition_enabled'] = true; // Always enabled for free tier
            $sanitized['show_branding'] = true; // Always show branding for free tier
        } else {
            $sanitized['show_badge'] = isset($settings['show_badge']) ? (bool) $settings['show_badge'] : true;
            $sanitized['badge_position'] = isset($settings['badge_position']) && in_array($settings['badge_position'], ['top', 'bottom', 'bottom-right'], true) ? $settings['badge_position'] : 'bottom-right';
            $sanitized['coalition_enabled'] = isset($settings['coalition_enabled']) ? (bool) $settings['coalition_enabled'] : true; // Optional for pro/enterprise
            $sanitized['show_branding'] = isset($settings['show_branding']) ? (bool) $settings['show_branding'] : true;
        }
        
        return $sanitized;
    }

    private function resolve_remote_account(string $api_base_url, string $api_key, array $fallback = [])
    {
        $base = rtrim((string) $api_base_url, '/');
        if ('' === $base || '' === trim($api_key)) {
            return [
                'tier' => 'starter',
                'organization_id' => '',
                'organization_name' => '',
            ];
        }

        $cache_key = $this->build_account_cache_key($base, $api_key);
        $cached = get_site_transient($cache_key);
        if (is_array($cached)) {
            return $cached;
        }

        $account_url = $base . '/account';
        $response = wp_remote_get($account_url, [
            'timeout' => 15,
            'headers' => [
                'Accept' => 'application/json',
                'Authorization' => 'Bearer ' . sanitize_text_field($api_key),
            ],
        ]);

        if (is_wp_error($response)) {
            return $response;
        }

        $status_code = wp_remote_retrieve_response_code($response);
        if ($status_code >= 400) {
            return new \WP_Error(
                'tier_http_error',
                sprintf(
                    /* translators: %d: HTTP status code */
                    __('Tier lookup failed with status %d.', 'encypher-provenance'),
                    $status_code
                )
            );
        }

        $body = json_decode(wp_remote_retrieve_body($response), true);
        if (! is_array($body)) {
            return new \WP_Error('tier_parse_error', __('Received an unexpected response while determining subscription tier.', 'encypher-provenance'));
        }

        $data = isset($body['data']) && is_array($body['data']) ? $body['data'] : [];
        $tier = $data['tier'] ?? 'starter';
        if (! in_array($tier, ['starter', 'professional', 'business', 'enterprise'], true)) {
            $tier = 'starter';
        }

        $features = isset($data['features']) && is_array($data['features']) ? $data['features'] : [];

        $account = [
            'tier' => $tier,
            'organization_id' => isset($data['organization_id']) ? sanitize_text_field((string) $data['organization_id']) : '',
            'organization_name' => isset($data['organization_name']) ? sanitize_text_field((string) $data['organization_name']) : '',
            'features' => $features,
        ];

        set_site_transient($cache_key, $account, self::ACCOUNT_CACHE_TTL);

        return $account;
    }

    private function build_account_cache_key(string $api_base_url, string $api_key): string
    {
        return 'encypher_account_' . md5(strtolower($api_base_url) . '|' . substr(hash('sha256', $api_key), 0, 16));
    }

    /**
     * Render the main Dashboard page.
     */
    public function render_dashboard_page(): void
    {
        if (! current_user_can('manage_options')) {
            return;
        }

        $settings = get_option('encypher_assurance_settings', []);
        $tier = isset($settings['tier']) ? $settings['tier'] : 'starter';
        $org_name = isset($settings['organization_name']) ? $settings['organization_name'] : '';
        $api_key = isset($settings['api_key']) ? $settings['api_key'] : '';
        $is_connected = !empty($api_key);
        $stats = $this->gather_analytics_stats();
        $show_onboarding = get_option('encypher_show_onboarding', true) && !$is_connected;

        ?>
        <div class="wrap encypher-dashboard">
            <div class="encypher-header">
                <h1>
                    <span class="encypher-logo"><?php echo $this->get_icon('encypher-logo', 'encypher-icon encypher-icon-brand'); ?></span>
                    <?php esc_html_e('Encypher', 'encypher-provenance'); ?>
                </h1>
                <?php if ($is_connected && $org_name): ?>
                    <span class="encypher-org-badge"><?php echo esc_html($org_name); ?></span>
                <?php endif; ?>
            </div>

            <?php if ($show_onboarding): ?>
                <?php $this->render_onboarding_banner(); ?>
            <?php endif; ?>

            <!-- Quick Stats -->
            <div class="encypher-stats-grid">
                <div class="encypher-stat-card">
                    <div class="stat-icon"><?php echo $this->get_icon('document', 'encypher-icon encypher-icon-stat'); ?></div>
                    <div class="stat-value"><?php echo esc_html($stats['signed_posts']); ?></div>
                    <div class="stat-label"><?php esc_html_e('Signed Content', 'encypher-provenance'); ?></div>
                </div>
                <div class="encypher-stat-card">
                    <div class="stat-icon"><?php echo $this->get_icon('chart', 'encypher-icon encypher-icon-stat'); ?></div>
                    <div class="stat-value"><?php echo esc_html($stats['coverage']); ?>%</div>
                    <div class="stat-label"><?php esc_html_e('Coverage', 'encypher-provenance'); ?></div>
                </div>
                <div class="encypher-stat-card">
                    <div class="stat-icon"><?php echo $this->get_icon('check-circle', 'encypher-icon encypher-icon-stat'); ?></div>
                    <div class="stat-value"><?php echo esc_html($stats['total_posts']); ?></div>
                    <div class="stat-label"><?php esc_html_e('Total Posts', 'encypher-provenance'); ?></div>
                </div>
                <div class="encypher-stat-card encypher-tier-card tier-<?php echo esc_attr($tier); ?>">
                    <div class="stat-icon"><?php echo $this->get_icon('award', 'encypher-icon encypher-icon-stat'); ?></div>
                    <div class="stat-value"><?php echo esc_html(ucfirst($tier)); ?></div>
                    <div class="stat-label"><?php esc_html_e('Current Tier', 'encypher-provenance'); ?></div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="encypher-section">
                <h2><?php esc_html_e('Quick Actions', 'encypher-provenance'); ?></h2>
                <div class="encypher-actions-grid">
                    <a href="<?php echo esc_url(admin_url('admin.php?page=encypher-content')); ?>" class="encypher-action-card">
                        <span class="action-icon"><?php echo $this->get_icon('file-text', 'encypher-icon encypher-icon-action'); ?></span>
                        <span class="action-title"><?php esc_html_e('Manage Content', 'encypher-provenance'); ?></span>
                        <span class="action-desc"><?php esc_html_e('View and sign your content', 'encypher-provenance'); ?></span>
                    </a>
                    <a href="<?php echo esc_url(admin_url('tools.php?page=encypher-bulk-mark')); ?>" class="encypher-action-card">
                        <span class="action-icon"><?php echo $this->get_icon('zap', 'encypher-icon encypher-icon-action'); ?></span>
                        <span class="action-title"><?php esc_html_e('Bulk Sign', 'encypher-provenance'); ?></span>
                        <span class="action-desc"><?php esc_html_e('Sign multiple posts at once', 'encypher-provenance'); ?></span>
                    </a>
                    <a href="<?php echo esc_url(admin_url('admin.php?page=encypher-analytics')); ?>" class="encypher-action-card">
                        <span class="action-icon"><?php echo $this->get_icon('trending-up', 'encypher-icon encypher-icon-action'); ?></span>
                        <span class="action-title"><?php esc_html_e('View Analytics', 'encypher-provenance'); ?></span>
                        <span class="action-desc"><?php esc_html_e('Track signing activity', 'encypher-provenance'); ?></span>
                    </a>
                    <a href="<?php echo esc_url(admin_url('admin.php?page=encypher-settings')); ?>" class="encypher-action-card">
                        <span class="action-icon"><?php echo $this->get_icon('settings', 'encypher-icon encypher-icon-action'); ?></span>
                        <span class="action-title"><?php esc_html_e('Settings', 'encypher-provenance'); ?></span>
                        <span class="action-desc"><?php esc_html_e('Configure API and options', 'encypher-provenance'); ?></span>
                    </a>
                </div>
            </div>

            <!-- Upsell Module -->
            <?php $this->render_upsell_module($tier); ?>

        </div>
        <style>
            .encypher-dashboard { max-width: 1200px; }
            .encypher-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
            .encypher-header h1 { display: flex; align-items: center; gap: 12px; margin: 0; }
            .encypher-logo { display: flex; align-items: center; }
            .encypher-org-badge { background: #1B3A5F; color: #fff; padding: 4px 12px; border-radius: 4px; font-size: 13px; }
            .encypher-icon { width: 24px; height: 24px; stroke: currentColor; }
            .encypher-icon-brand { width: 36px; height: 36px; }
            .encypher-icon-lg { width: 32px; height: 32px; color: #2271b1; }
            .encypher-icon-stat { width: 28px; height: 28px; color: #1B3A5F; }
            .encypher-icon-action { width: 24px; height: 24px; color: #2271b1; }
            .encypher-stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }
            .encypher-stat-card { background: #fff; border: 1px solid #dcdcde; border-radius: 8px; padding: 20px; text-align: center; }
            .encypher-stat-card .stat-icon { display: flex; justify-content: center; margin-bottom: 12px; }
            .encypher-stat-card .stat-value { font-size: 32px; font-weight: 700; color: #1B3A5F; }
            .encypher-stat-card .stat-label { color: #646970; font-size: 13px; margin-top: 4px; }
            .encypher-tier-card.tier-starter { border-color: #8c8f94; }
            .encypher-tier-card.tier-starter .stat-icon .encypher-icon { color: #8c8f94; }
            .encypher-tier-card.tier-professional { border-color: #2271b1; background: linear-gradient(135deg, #f0f6fc 0%, #fff 100%); }
            .encypher-tier-card.tier-professional .stat-icon .encypher-icon { color: #2271b1; }
            .encypher-tier-card.tier-business { border-color: #00a32a; background: linear-gradient(135deg, #edfaef 0%, #fff 100%); }
            .encypher-tier-card.tier-business .stat-icon .encypher-icon { color: #00a32a; }
            .encypher-tier-card.tier-enterprise { border-color: #dba617; background: linear-gradient(135deg, #fcf9e8 0%, #fff 100%); }
            .encypher-tier-card.tier-enterprise .stat-icon .encypher-icon { color: #dba617; }
            .encypher-section { margin-bottom: 32px; }
            .encypher-section h2 { font-size: 18px; margin-bottom: 16px; }
            .encypher-actions-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
            .encypher-action-card { display: flex; flex-direction: column; background: #fff; border: 1px solid #dcdcde; border-radius: 8px; padding: 20px; text-decoration: none; transition: all 0.2s; }
            .encypher-action-card:hover { border-color: #2271b1; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
            .encypher-action-card .action-icon { margin-bottom: 12px; }
            .encypher-action-card .action-title { font-weight: 600; color: #1d2327; margin-bottom: 4px; }
            .encypher-action-card .action-desc { font-size: 13px; color: #646970; }
        </style>
        <?php
    }

    /**
     * Render onboarding banner for new users.
     */
    private function render_onboarding_banner(): void
    {
        ?>
        <div class="encypher-onboarding-banner">
            <div class="onboarding-content">
                <h2><?php esc_html_e('Welcome to Encypher', 'encypher-provenance'); ?></h2>
                <p><?php esc_html_e('Protect your content with C2PA-compliant cryptographic signatures. Get started in 3 easy steps:', 'encypher-provenance'); ?></p>
                <ol class="onboarding-steps">
                    <li>
                        <strong><?php esc_html_e('Get your API key', 'encypher-provenance'); ?></strong>
                        <a href="https://dashboard.encypherai.com/register" target="_blank" class="button button-small"><?php esc_html_e('Sign Up Free', 'encypher-provenance'); ?></a>
                    </li>
                    <li>
                        <strong><?php esc_html_e('Configure your settings', 'encypher-provenance'); ?></strong>
                        <a href="<?php echo esc_url(admin_url('admin.php?page=encypher-settings')); ?>" class="button button-small"><?php esc_html_e('Go to Settings', 'encypher-provenance'); ?></a>
                    </li>
                    <li>
                        <strong><?php esc_html_e('Start signing content', 'encypher-provenance'); ?></strong>
                        <span class="step-note"><?php esc_html_e('Auto-signs on publish!', 'encypher-provenance'); ?></span>
                    </li>
                </ol>
            </div>
            <button type="button" class="onboarding-dismiss" onclick="jQuery.post(ajaxurl, {action: 'encypher_dismiss_onboarding', _wpnonce: '<?php echo wp_create_nonce('encypher_dismiss_onboarding'); ?>'}, function() { jQuery('.encypher-onboarding-banner').fadeOut(); });">
                <?php esc_html_e('Dismiss', 'encypher-provenance'); ?>
            </button>
        </div>
        <style>
            .encypher-onboarding-banner { background: linear-gradient(135deg, #1B3A5F 0%, #2E6DB4 100%); color: #fff; border-radius: 8px; padding: 24px; margin-bottom: 24px; position: relative; }
            .encypher-onboarding-banner h2 { color: #fff; margin: 0 0 12px 0; }
            .encypher-onboarding-banner p { margin: 0 0 16px 0; opacity: 0.9; }
            .encypher-onboarding-banner .onboarding-steps { margin: 0; padding-left: 20px; }
            .encypher-onboarding-banner .onboarding-steps li { margin-bottom: 12px; }
            .encypher-onboarding-banner .onboarding-steps strong { display: inline-block; min-width: 180px; }
            .encypher-onboarding-banner .step-note { font-size: 12px; opacity: 0.8; }
            .encypher-onboarding-banner .onboarding-dismiss { position: absolute; top: 12px; right: 12px; background: transparent; border: 1px solid rgba(255,255,255,0.3); color: #fff; padding: 4px 12px; border-radius: 4px; cursor: pointer; }
            .encypher-onboarding-banner .onboarding-dismiss:hover { background: rgba(255,255,255,0.1); }
        </style>
        <?php
    }

    /**
     * AJAX handler for dismissing onboarding banner.
     */
    public function ajax_dismiss_onboarding(): void
    {
        check_ajax_referer('encypher_dismiss_onboarding');
        
        if (!current_user_can('manage_options')) {
            wp_send_json_error('Unauthorized', 403);
        }
        
        update_option('encypher_show_onboarding', false);
        wp_send_json_success();
    }

    /**
     * Render upsell module based on current tier.
     */
    private function render_upsell_module(string $current_tier): void
    {
        if ($current_tier === 'enterprise') {
            return; // No upsell for enterprise
        }

        $upgrades = [
            'starter' => [
                'next_tier' => 'Professional',
                'price' => '$99/mo',
                'features' => [
                    __('Bring Your Own Keys (BYOK)', 'encypher-provenance'),
                    __('Sentence-level tracking', 'encypher-provenance'),
                    __('Invisible embeddings', 'encypher-provenance'),
                    __('Remove Encypher branding', 'encypher-provenance'),
                    __('70/30 revenue share', 'encypher-provenance'),
                ],
                'cta_url' => 'https://dashboard.encypherai.com/billing?upgrade=professional',
            ],
            'professional' => [
                'next_tier' => 'Business',
                'price' => '$499/mo',
                'features' => [
                    __('Batch operations (100 docs)', 'encypher-provenance'),
                    __('Team management (10 users)', 'encypher-provenance'),
                    __('Audit logs', 'encypher-provenance'),
                    __('Priority support (24hr SLA)', 'encypher-provenance'),
                    __('75/25 revenue share', 'encypher-provenance'),
                ],
                'cta_url' => 'https://dashboard.encypherai.com/billing?upgrade=business',
            ],
            'business' => [
                'next_tier' => 'Enterprise',
                'price' => 'Custom',
                'features' => [
                    __('Unlimited everything', 'encypher-provenance'),
                    __('Custom C2PA assertions', 'encypher-provenance'),
                    __('SSO/SCIM integration', 'encypher-provenance'),
                    __('Dedicated support & SLA', 'encypher-provenance'),
                    __('80/20 revenue share', 'encypher-provenance'),
                ],
                'cta_url' => 'https://encypherai.com/enterprise',
            ],
        ];

        $upgrade = $upgrades[$current_tier] ?? $upgrades['starter'];
        ?>
        <div class="encypher-section encypher-upsell">
            <h2><?php esc_html_e('Unlock More Features', 'encypher-provenance'); ?></h2>
            <div class="upsell-card">
                <div class="upsell-header">
                    <span class="upsell-badge"><?php esc_html_e('Upgrade', 'encypher-provenance'); ?></span>
                    <h3><?php echo esc_html($upgrade['next_tier']); ?></h3>
                    <span class="upsell-price"><?php echo esc_html($upgrade['price']); ?></span>
                </div>
                <ul class="upsell-features">
                    <?php foreach ($upgrade['features'] as $feature): ?>
                        <li><span class="feature-check"><?php echo $this->get_icon('check', 'encypher-icon encypher-icon-check'); ?></span> <?php echo esc_html($feature); ?></li>
                    <?php endforeach; ?>
                </ul>
                <a href="<?php echo esc_url($upgrade['cta_url']); ?>" class="button button-primary button-hero" target="_blank">
                    <?php printf(esc_html__('Upgrade to %s', 'encypher-provenance'), esc_html($upgrade['next_tier'])); ?>
                </a>
            </div>
        </div>
        <style>
            .encypher-upsell .upsell-card { background: linear-gradient(135deg, #f0f6fc 0%, #fff 100%); border: 2px solid #2271b1; border-radius: 12px; padding: 24px; max-width: 400px; }
            .encypher-upsell .upsell-header { text-align: center; margin-bottom: 16px; }
            .encypher-upsell .upsell-badge { background: #2271b1; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px; text-transform: uppercase; }
            .encypher-upsell .upsell-header h3 { margin: 8px 0 4px 0; font-size: 24px; }
            .encypher-upsell .upsell-price { font-size: 18px; color: #1B3A5F; font-weight: 600; }
            .encypher-upsell .upsell-features { list-style: none; padding: 0; margin: 0 0 20px 0; }
            .encypher-upsell .upsell-features li { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #e0e0e0; color: #1d2327; }
            .encypher-upsell .upsell-features li:last-child { border-bottom: none; }
            .encypher-upsell .feature-check { display: flex; }
            .encypher-upsell .encypher-icon-check { width: 16px; height: 16px; color: #00a32a; }
            .encypher-upsell .button-hero { display: block; text-align: center; padding: 12px 24px; font-size: 15px; }
        </style>
        <?php
    }

    /**
     * Render the Content management page.
     */
    public function render_content_page(): void
    {
        if (! current_user_can('manage_options')) {
            return;
        }

        global $wpdb;

        // Get posts with their signing status
        $posts = get_posts([
            'post_type' => ['post', 'page'],
            'post_status' => 'publish',
            'posts_per_page' => 50,
            'orderby' => 'date',
            'order' => 'DESC',
        ]);

        ?>
        <div class="wrap encypher-content-page">
            <h1><?php esc_html_e('Content Management', 'encypher-provenance'); ?></h1>
            <p class="description"><?php esc_html_e('View and manage the signing status of your content.', 'encypher-provenance'); ?></p>

            <div class="tablenav top">
                <div class="alignleft actions">
                    <a href="<?php echo esc_url(admin_url('tools.php?page=encypher-bulk-mark')); ?>" class="button button-primary">
                        <?php esc_html_e('Bulk Sign Content', 'encypher-provenance'); ?>
                    </a>
                </div>
            </div>

            <table class="wp-list-table widefat fixed striped">
                <thead>
                    <tr>
                        <th scope="col" class="column-title"><?php esc_html_e('Title', 'encypher-provenance'); ?></th>
                        <th scope="col" class="column-type"><?php esc_html_e('Type', 'encypher-provenance'); ?></th>
                        <th scope="col" class="column-status"><?php esc_html_e('Signing Status', 'encypher-provenance'); ?></th>
                        <th scope="col" class="column-signed"><?php esc_html_e('Last Signed', 'encypher-provenance'); ?></th>
                        <th scope="col" class="column-actions"><?php esc_html_e('Actions', 'encypher-provenance'); ?></th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (empty($posts)): ?>
                        <tr>
                            <td colspan="5"><?php esc_html_e('No published content found.', 'encypher-provenance'); ?></td>
                        </tr>
                    <?php else: ?>
                        <?php foreach ($posts as $post): 
                            $is_marked = get_post_meta($post->ID, '_encypher_marked', true);
                            $last_signed = get_post_meta($post->ID, '_encypher_assurance_last_signed', true);
                            $status = get_post_meta($post->ID, '_encypher_assurance_status', true);
                            $document_id = get_post_meta($post->ID, '_encypher_assurance_document_id', true);
                        ?>
                            <tr>
                                <td class="column-title">
                                    <strong><a href="<?php echo esc_url(get_edit_post_link($post->ID)); ?>"><?php echo esc_html(get_the_title($post)); ?></a></strong>
                                </td>
                                <td class="column-type"><?php echo esc_html(get_post_type_object($post->post_type)->labels->singular_name); ?></td>
                                <td class="column-status">
                                    <?php if ($is_marked): ?>
                                        <span class="encypher-status-badge status-signed">✓ <?php esc_html_e('Signed', 'encypher-provenance'); ?></span>
                                    <?php else: ?>
                                        <span class="encypher-status-badge status-unsigned"><?php esc_html_e('Not Signed', 'encypher-provenance'); ?></span>
                                    <?php endif; ?>
                                </td>
                                <td class="column-signed">
                                    <?php echo $last_signed ? esc_html($last_signed) : '—'; ?>
                                </td>
                                <td class="column-actions">
                                    <?php if ($document_id): ?>
                                        <a href="https://encypherai.com/verify/<?php echo esc_attr($document_id); ?>" target="_blank" class="button button-small">
                                            <?php esc_html_e('Verify', 'encypher-provenance'); ?>
                                        </a>
                                    <?php endif; ?>
                                    <a href="<?php echo esc_url(get_edit_post_link($post->ID)); ?>" class="button button-small">
                                        <?php esc_html_e('Edit', 'encypher-provenance'); ?>
                                    </a>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>
        <style>
            .encypher-content-page .encypher-status-badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
            .encypher-content-page .status-signed { background: #d1e7dd; color: #0a3622; }
            .encypher-content-page .status-unsigned { background: #f8d7da; color: #58151c; }
        </style>
        <?php
    }

    /**
     * Render the Account page.
     */
    public function render_account_page(): void
    {
        if (! current_user_can('manage_options')) {
            return;
        }

        $settings = get_option('encypher_assurance_settings', []);
        $tier = isset($settings['tier']) ? $settings['tier'] : 'starter';
        $org_id = isset($settings['organization_id']) ? $settings['organization_id'] : '';
        $org_name = isset($settings['organization_name']) ? $settings['organization_name'] : '';
        $api_key = isset($settings['api_key']) ? $settings['api_key'] : '';
        $is_connected = !empty($api_key);

        $tier_info = [
            'starter' => ['name' => 'Starter', 'price' => 'Free', 'color' => '#8c8f94'],
            'professional' => ['name' => 'Professional', 'price' => '$99/mo', 'color' => '#2271b1'],
            'business' => ['name' => 'Business', 'price' => '$499/mo', 'color' => '#00a32a'],
            'enterprise' => ['name' => 'Enterprise', 'price' => 'Custom', 'color' => '#dba617'],
        ];
        $current_tier_info = $tier_info[$tier] ?? $tier_info['starter'];

        ?>
        <div class="wrap encypher-account-page">
            <h1><?php esc_html_e('Account', 'encypher-provenance'); ?></h1>

            <div class="encypher-account-grid">
                <!-- Subscription Card -->
                <div class="account-card">
                    <h2><?php esc_html_e('Subscription', 'encypher-provenance'); ?></h2>
                    <div class="subscription-info">
                        <div class="tier-badge" style="background: <?php echo esc_attr($current_tier_info['color']); ?>">
                            <?php echo esc_html($current_tier_info['name']); ?>
                        </div>
                        <div class="tier-price"><?php echo esc_html($current_tier_info['price']); ?></div>
                    </div>
                    <?php if ($org_name): ?>
                        <p><strong><?php esc_html_e('Organization:', 'encypher-provenance'); ?></strong> <?php echo esc_html($org_name); ?></p>
                    <?php endif; ?>
                    <p>
                        <a href="https://dashboard.encypherai.com/billing" class="button" target="_blank">
                            <?php esc_html_e('Manage Subscription', 'encypher-provenance'); ?>
                        </a>
                    </p>
                </div>

                <!-- API Key Card -->
                <div class="account-card">
                    <h2><?php esc_html_e('API Connection', 'encypher-provenance'); ?></h2>
                    <?php if ($is_connected): ?>
                        <p class="connection-status connected">
                            <span class="status-dot"></span>
                            <?php esc_html_e('Connected', 'encypher-provenance'); ?>
                        </p>
                        <p><strong><?php esc_html_e('API Key:', 'encypher-provenance'); ?></strong> ••••••••<?php echo esc_html(substr($api_key, -4)); ?></p>
                    <?php else: ?>
                        <p class="connection-status disconnected">
                            <span class="status-dot"></span>
                            <?php esc_html_e('Not Connected', 'encypher-provenance'); ?>
                        </p>
                    <?php endif; ?>
                    <p>
                        <a href="<?php echo esc_url(admin_url('admin.php?page=encypher-settings')); ?>" class="button">
                            <?php esc_html_e('Configure API', 'encypher-provenance'); ?>
                        </a>
                        <a href="https://dashboard.encypherai.com/api-keys" class="button" target="_blank">
                            <?php esc_html_e('Manage API Keys', 'encypher-provenance'); ?>
                        </a>
                    </p>
                </div>

                <!-- Quick Links Card -->
                <div class="account-card">
                    <h2><?php esc_html_e('Quick Links', 'encypher-provenance'); ?></h2>
                    <ul class="quick-links">
                        <li><a href="https://dashboard.encypherai.com" target="_blank"><?php esc_html_e('Encypher Dashboard', 'encypher-provenance'); ?> →</a></li>
                        <li><a href="https://api.encypherai.com/docs" target="_blank"><?php esc_html_e('API Documentation', 'encypher-provenance'); ?> →</a></li>
                        <li><a href="https://encypherai.com/support" target="_blank"><?php esc_html_e('Support Center', 'encypher-provenance'); ?> →</a></li>
                        <li><a href="https://encypherai.com/coalition" target="_blank"><?php esc_html_e('Coalition Program', 'encypher-provenance'); ?> →</a></li>
                    </ul>
                </div>
            </div>
        </div>
        <style>
            .encypher-account-page .encypher-account-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
            .encypher-account-page .account-card { background: #fff; border: 1px solid #dcdcde; border-radius: 8px; padding: 20px; }
            .encypher-account-page .account-card h2 { margin-top: 0; font-size: 16px; border-bottom: 1px solid #f0f0f1; padding-bottom: 12px; }
            .encypher-account-page .subscription-info { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
            .encypher-account-page .tier-badge { color: #fff; padding: 6px 16px; border-radius: 4px; font-weight: 600; }
            .encypher-account-page .tier-price { font-size: 18px; font-weight: 600; color: #1d2327; }
            .encypher-account-page .connection-status { display: flex; align-items: center; gap: 8px; font-weight: 500; }
            .encypher-account-page .connection-status .status-dot { width: 10px; height: 10px; border-radius: 50%; }
            .encypher-account-page .connection-status.connected .status-dot { background: #00a32a; }
            .encypher-account-page .connection-status.disconnected .status-dot { background: #d63638; }
            .encypher-account-page .quick-links { list-style: none; padding: 0; margin: 0; }
            .encypher-account-page .quick-links li { padding: 8px 0; border-bottom: 1px solid #f0f0f1; }
            .encypher-account-page .quick-links li:last-child { border-bottom: none; }
            .encypher-account-page .quick-links a { text-decoration: none; color: #2271b1; }
            .encypher-account-page .quick-links a:hover { color: #135e96; }
        </style>
        <?php
    }

    public function render_settings_page(): void
    {
        if (! current_user_can('manage_options')) {
            return;
        }

        ?>
        <div class="wrap">
            <h1><?php esc_html_e('Encypher Settings', 'encypher-provenance'); ?></h1>
            <form method="post" action="options.php">
                <?php
                settings_fields('encypher_assurance_settings_group');
                do_settings_sections('encypher-provenance-settings');
                submit_button(__('Save Changes', 'encypher-provenance'));
                ?>
            </form>
        </div>
        <?php
    }

    public function enqueue_settings_page_assets(string $hook_suffix): void
    {
        // Load on all Encypher admin pages
        $encypher_pages = [
            'toplevel_page_encypher',
            'encypher_page_encypher-content',
            'encypher_page_encypher-settings',
            'encypher_page_encypher-analytics',
            'encypher_page_encypher-account',
            'settings_page_encypher-provenance-settings', // Legacy
        ];
        
        if (!in_array($hook_suffix, $encypher_pages, true)) {
            return;
        }

        wp_enqueue_style(
            'encypher-provenance-settings',
            ENCYPHER_ASSURANCE_PLUGIN_URL . 'assets/css/settings-page.css',
            [],
            ENCYPHER_ASSURANCE_VERSION
        );

        wp_enqueue_script(
            'encypher-provenance-settings',
            ENCYPHER_ASSURANCE_PLUGIN_URL . 'assets/js/settings-page.js',
            ['jquery'],
            ENCYPHER_ASSURANCE_VERSION,
            true
        );

        wp_localize_script(
            'encypher-provenance-settings',
            'wpApiSettings',
            [
                'root' => esc_url_raw(rest_url()),
                'nonce' => wp_create_nonce('wp_rest'),
            ]
        );

        $options = get_option('encypher_assurance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'starter';
        wp_localize_script(
            'encypher-provenance-settings',
            'EncypherSettingsData',
            [
                'tier' => $tier,
                'signingMode' => isset($options['signing_mode']) ? $options['signing_mode'] : 'managed',
                'byokEnabled' => isset($options['signing_mode']) && 'byok' === $options['signing_mode'],
                'dashboardUrls' => [
                    'billing' => 'https://dashboard.encypherai.com/billing',
                    'apiKey' => 'https://dashboard.encypherai.com/register',
                    'byok' => 'https://dashboard.encypherai.com/signing-profiles',
                ],
                'strings' => [
                    'byokDisabled' => __('BYOK is only available on Pro or Enterprise tiers.', 'encypher-provenance'),
                    'tierDowngraded' => __('Your workspace tier no longer supports custom signing profiles. We reset BYOK to Encypher-managed certificates.', 'encypher-provenance'),
                ],
            ]
        );
    }

    public function render_api_base_url_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $value = isset($options['api_base_url']) ? esc_url($options['api_base_url']) : '';
        ?>
        <input type="url" id="api_base_url" class="regular-text" name="encypher_assurance_settings[api_base_url]" value="<?php echo esc_attr($value); ?>" placeholder="http://localhost:9000/api/v1" required />
        <p class="description">
            <?php esc_html_e('Base URL for the Encypher Enterprise API.', 'encypher-provenance'); ?><br>
            <strong><?php esc_html_e('Local testing:', 'encypher-provenance'); ?></strong> <?php esc_html_e('Use http://localhost:9000/api/v1', 'encypher-provenance'); ?><br>
            <strong><?php esc_html_e('Production:', 'encypher-provenance'); ?></strong> <?php esc_html_e('Use https://api.encypherai.com/api/v1', 'encypher-provenance'); ?>
        </p>
        <div id="connection-status"></div>
        <button type="button" id="test-connection-btn" class="button"><?php esc_html_e('Test Connection', 'encypher-provenance'); ?></button>
        <div id="test-connection-result"></div>
        <?php
    }

    public function render_api_key_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $value = isset($options['api_key']) ? $options['api_key'] : '';
        ?>
        <input type="password" id="api_key" class="regular-text" name="encypher_assurance_settings[api_key]" value="<?php echo esc_attr($value); ?>" autocomplete="off" />
        <p class="description">
            <?php esc_html_e('Enterprise API keys authenticate requests using the Authorization Bearer scheme.', 'encypher-provenance'); ?>
            <br>
            <a class="button button-secondary" href="https://dashboard.encypherai.com/register" target="_blank" rel="noopener noreferrer">
                <?php esc_html_e('Get API Key', 'encypher-provenance'); ?>
            </a>
            <a class="button button-link" style="margin-left:8px;" href="https://dashboard.encypherai.com/billing" target="_blank" rel="noopener noreferrer">
                <?php esc_html_e('Manage Account & Billing', 'encypher-provenance'); ?>
            </a>
        </p>
        <?php
    }

    public function render_auto_verify_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $checked = ! empty($options['auto_verify']);
        ?>
        <label>
            <input type="checkbox" name="encypher_assurance_settings[auto_verify]" value="1" <?php checked($checked); ?> />
            <?php esc_html_e('Verify signed content when rendering posts/pages.', 'encypher-provenance'); ?>
        </label>
        <?php
    }

    public function render_signing_mode_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'starter';
        $value = isset($options['signing_mode']) ? $options['signing_mode'] : 'managed';

        if ('starter' === $tier) {
            ?>
            <p class="description">
                <?php esc_html_e('Free workspaces use Encypher-managed certificates. Upgrade to Pro for Bring Your Own Key support.', 'encypher-provenance'); ?>
            </p>
            <input type="hidden" name="encypher_assurance_settings[signing_mode]" value="managed" />
            <?php
            return;
        }
        ?>
        <select id="encypher-signing-mode" name="encypher_assurance_settings[signing_mode]">
            <option value="managed" <?php selected('managed', $value); ?>>
                <?php esc_html_e('Managed certificate (recommended)', 'encypher-provenance'); ?>
            </option>
            <option value="byok" <?php selected('byok', $value); ?>>
                <?php esc_html_e('Bring Your Own Key (BYOK)', 'encypher-provenance'); ?>
            </option>
        </select>
        <p class="description">
            <?php esc_html_e('BYOK lets you sign posts with your own Ed25519 key pair or HSM-backed keys (Enterprise) registered in the Encypher dashboard.', 'encypher-provenance'); ?>
        </p>
        <?php
    }

    public function render_signing_profile_id_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'starter';
        $mode = isset($options['signing_mode']) ? $options['signing_mode'] : 'managed';
        $value = isset($options['signing_profile_id']) ? $options['signing_profile_id'] : '';

        if ('starter' === $tier) {
            ?>
            <p class="description">
                <?php esc_html_e('Upgrade to Pro to configure custom signing profiles from your Encypher dashboard.', 'encypher-provenance'); ?>
            </p>
            <input type="hidden" name="encypher_assurance_settings[signing_profile_id]" value="" />
            <?php
            return;
        }

        $readonly = ('byok' !== $mode);
        ?>
        <input
            id="encypher-signing-profile-id"
            type="text"
            class="regular-text"
            name="encypher_assurance_settings[signing_profile_id]"
            value="<?php echo esc_attr($value); ?>"
            <?php disabled($readonly); ?>
            placeholder="prof_1234abcd"
        />
        <p class="description">
            <?php esc_html_e('Paste the Signing Profile ID generated in the Encypher dashboard BYOK wizard.', 'encypher-provenance'); ?>
            <?php if ($readonly) : ?>
                <br><em><?php esc_html_e('Enable BYOK mode above to edit this value.', 'encypher-provenance'); ?></em>
            <?php endif; ?>
        </p>
        <?php
    }

    public function enqueue_block_editor_assets(): void
    {
        $asset_path = ENCYPHER_ASSURANCE_PLUGIN_URL . 'assets/js/editor-sidebar.js';
        wp_enqueue_script(
            'encypher-provenance-editor-sidebar',
            $asset_path,
            ['wp-plugins', 'wp-edit-post', 'wp-components', 'wp-element', 'wp-data', 'wp-api-fetch'],
            ENCYPHER_ASSURANCE_VERSION,
            true
        );

        $settings = get_option('encypher_assurance_settings', []);
        $tier = isset($settings['tier']) ? $settings['tier'] : 'starter';
        wp_localize_script(
            'encypher-provenance-editor-sidebar',
            'EncypherAssuranceConfig',
            [
                'restUrl' => esc_url_raw(rest_url('encypher-provenance/v1/')),
                'nonce' => wp_create_nonce('wp_rest'),
                'autoVerify' => ! empty($settings['auto_verify']),
                'tier' => $tier,
                'signingMode' => isset($settings['signing_mode']) ? $settings['signing_mode'] : 'managed',
                'byokEnabled' => isset($settings['signing_mode']) && 'byok' === $settings['signing_mode'],
                'upgradeUrl' => 'https://dashboard.encypherai.com/billing',
                'manageAccountUrl' => 'https://dashboard.encypherai.com/settings',
            ]
        );

        wp_enqueue_style(
            'encypher-provenance-editor-css',
            ENCYPHER_ASSURANCE_PLUGIN_URL . 'assets/css/editor.css',
            [],
            ENCYPHER_ASSURANCE_VERSION
        );
    }

    public function enqueue_classic_assets(string $hook_suffix): void
    {
        if (! in_array($hook_suffix, ['post.php', 'post-new.php'], true)) {
            return;
        }

        wp_enqueue_script(
            'encypher-provenance-classic',
            ENCYPHER_ASSURANCE_PLUGIN_URL . 'assets/js/classic-meta-box.js',
            ['jquery'],
            ENCYPHER_ASSURANCE_VERSION,
            true
        );

        wp_localize_script(
            'encypher-provenance-classic',
            'EncypherAssuranceClassic',
            [
                'restUrl' => esc_url_raw(rest_url('encypher-provenance/v1/')),
                'nonce' => wp_create_nonce('wp_rest'),
            ]
        );
    }

    public function register_classic_meta_box(): void
    {
        // Classic meta box disabled - using Gutenberg sidebar panel instead
        return;
        
        // Old code kept for reference
        // add_meta_box(
        //     'encypher-provenance-meta-box',
        //     __('Encypher Provenance', 'encypher-provenance'),
        //     [$this, 'render_classic_meta_box'],
        //     ['post', 'page'],
        //     'side',
        //     'high'
        // );
    }

    public function render_classic_meta_box($post): void
    {
        wp_nonce_field('encypher_assurance_meta_box', 'encypher_assurance_meta_box_nonce');
        $status = get_post_meta($post->ID, '_encypher_assurance_status', true);
        $document_id = get_post_meta($post->ID, '_encypher_assurance_document_id', true);
        $verification_url = get_post_meta($post->ID, '_encypher_assurance_verification_url', true);
        $total_sentences = (int) get_post_meta($post->ID, '_encypher_assurance_total_sentences', true);
        ?>
        <div class="encypher-provenance-classic">
            <p class="status-row">
                <strong><?php esc_html_e('Status:', 'encypher-provenance'); ?></strong>
                <span class="status-value"><?php echo esc_html($status ? $status : __('Not signed', 'encypher-provenance')); ?></span>
            </p>
            <p class="document-id-row">
                <strong><?php esc_html_e('Document ID:', 'encypher-provenance'); ?></strong>
                <span class="document-id-value">
                    <?php echo $document_id ? esc_html($document_id) : esc_html__('Not available', 'encypher-provenance'); ?>
                </span>
            </p>
            <p class="verification-link"<?php echo $verification_url ? '' : ' style="display:none;"'; ?>>
                <a href="<?php echo $verification_url ? esc_url($verification_url) : '#'; ?>" target="_blank" rel="noopener">
                    <?php esc_html_e('View provenance report', 'encypher-provenance'); ?>
                </a>
            </p>
            <p class="sentences-count"<?php echo $total_sentences ? '' : ' style="display:none;"'; ?>>
                <strong><?php esc_html_e('Sentences protected:', 'encypher-provenance'); ?></strong>
                <span class="sentences-value"><?php echo $total_sentences ? esc_html((string) $total_sentences) : '0'; ?></span>
            </p>
            <button type="button" class="button button-primary encypher-provenance-sign" data-post-id="<?php echo esc_attr($post->ID); ?>">
                <?php esc_html_e('Sign Content', 'encypher-provenance'); ?>
            </button>
            <p class="status-message" aria-live="polite"></p>
        </div>
        <?php
    }

    /**
     * Auto-mark content when publishing a post.
     * 
     * @param int $post_id Post ID
     * @param \WP_Post $post Post object
     */
    public function auto_mark_on_publish(int $post_id, $post): void
    {
        // Check if auto-mark is enabled
        $settings = get_option('encypher_assurance_settings', []);
        if (empty($settings['auto_mark_on_publish'])) {
            return;
        }

        // Check if post type is enabled
        if (!in_array($post->post_type, $settings['post_types'] ?? ['post', 'page'], true)) {
            return;
        }

        // Check per-post override
        if (get_post_meta($post_id, '_encypher_skip_marking', true)) {
            return;
        }

        // Check if already marked (avoid double-marking on publish)
        if (get_post_meta($post_id, '_encypher_marked', true)) {
            return;
        }

        // Mark the content
        $this->mark_post_content($post_id, $post, 'c2pa.created');
    }

    /**
     * Auto-mark content when updating a post.
     * 
     * @param int $post_id Post ID
     * @param \WP_Post $post_after Post object after update
     * @param \WP_Post $post_before Post object before update
     */
    public function auto_mark_on_update(int $post_id, $post_after, $post_before): void
    {
        // Only process published posts
        if ($post_after->post_status !== 'publish') {
            return;
        }
        
        // Don't trigger on initial publish (status change from non-publish to publish)
        // The auto_mark_on_publish hook will handle this
        if ($post_before->post_status !== 'publish') {
            return;
        }

        // Check if auto-mark on update is enabled
        $settings = get_option('encypher_assurance_settings', []);
        if (empty($settings['auto_mark_on_update'])) {
            return;
        }

        // Check if post type is enabled
        if (!in_array($post_after->post_type, $settings['post_types'] ?? ['post', 'page'], true)) {
            return;
        }

        // Check per-post override
        if (get_post_meta($post_id, '_encypher_skip_marking', true)) {
            return;
        }

        // Check if content changed
        if ($post_after->post_content === $post_before->post_content) {
            return;
        }

        // Check if already marked
        $is_marked = get_post_meta($post_id, '_encypher_marked', true);
        
        // Re-mark with edit action
        $action = $is_marked ? 'c2pa.edited' : 'c2pa.created';
        $this->mark_post_content($post_id, $post_after, $action);
    }

    /**
     * Mark post content with C2PA manifest.
     * 
     * @param int $post_id Post ID
     * @param \WP_Post $post Post object
     * @param string $action C2PA action type (c2pa.created or c2pa.edited)
     */
    private function mark_post_content(int $post_id, $post, string $action): void
    {
        // This will be implemented to call the REST API endpoint
        // For now, we'll set a flag to indicate marking is needed
        update_post_meta($post_id, '_encypher_needs_marking', true);
        update_post_meta($post_id, '_encypher_action_type', $action);
        
        // Log for debugging
        error_log(sprintf(
            'Encypher: Post %d needs marking with action %s',
            $post_id,
            $action
        ));
    }

    /**
     * Render auto-mark on publish field.
     */
    public function render_auto_mark_on_publish_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $checked = isset($options['auto_mark_on_publish']) ? (bool) $options['auto_mark_on_publish'] : true;
        ?>
        <label>
            <input type="checkbox" name="encypher_assurance_settings[auto_mark_on_publish]" value="1" <?php checked($checked); ?> />
            <?php esc_html_e('Automatically embed C2PA manifests when publishing new posts', 'encypher-provenance'); ?>
        </label>
        <p class="description"><?php esc_html_e('Recommended for all users. Ensures every published post has cryptographic proof of origin.', 'encypher-provenance'); ?></p>
        <?php
    }

    /**
     * Render auto-mark on update field.
     */
    public function render_auto_mark_on_update_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $checked = isset($options['auto_mark_on_update']) ? (bool) $options['auto_mark_on_update'] : true;
        ?>
        <label>
            <input type="checkbox" name="encypher_assurance_settings[auto_mark_on_update]" value="1" <?php checked($checked); ?> />
            <?php esc_html_e('Re-sign manifests when content is updated', 'encypher-provenance'); ?>
        </label>
        <p class="description"><?php esc_html_e('Preserves provenance chain through ingredient references. Uses c2pa.edited action.', 'encypher-provenance'); ?></p>
        <?php
    }

    /**
     * Render metadata format field.
     */
    public function render_metadata_format_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $value = isset($options['metadata_format']) ? $options['metadata_format'] : 'c2pa';
        ?>
        <select name="encypher_assurance_settings[metadata_format]">
            <option value="c2pa" <?php selected($value, 'c2pa'); ?>><?php esc_html_e('C2PA (Recommended)', 'encypher-provenance'); ?></option>
            <option value="basic" <?php selected($value, 'basic'); ?>><?php esc_html_e('Basic (Minimal)', 'encypher-provenance'); ?></option>
        </select>
        <p class="description">
            <?php esc_html_e('C2PA format includes full manifest with assertions. Basic format is minimal for testing.', 'encypher-provenance'); ?>
            <a href="https://c2pa.org" target="_blank"><?php esc_html_e('Learn about C2PA', 'encypher-provenance'); ?></a>
        </p>
        <?php
    }

    /**
     * Render hard binding field.
     */
    public function render_add_hard_binding_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $checked = isset($options['add_hard_binding']) ? (bool) $options['add_hard_binding'] : true;
        ?>
        <label>
            <input type="checkbox" name="encypher_assurance_settings[add_hard_binding]" value="1" <?php checked($checked); ?> />
            <?php esc_html_e('Include c2pa.hash.data assertion', 'encypher-provenance'); ?>
        </label>
        <p class="description"><?php esc_html_e('Provides content hash for tamper detection. Recommended for maximum security.', 'encypher-provenance'); ?></p>
        <?php
    }

    /**
     * Render post types field.
     */
    public function render_post_types_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $selected_types = isset($options['post_types']) ? (array) $options['post_types'] : ['post', 'page'];
        $post_types = get_post_types(['public' => true], 'objects');
        ?>
        <fieldset>
            <?php foreach ($post_types as $post_type): ?>
                <label style="display:block; margin-bottom:5px;">
                    <input type="checkbox" 
                           name="encypher_assurance_settings[post_types][]" 
                           value="<?php echo esc_attr($post_type->name); ?>"
                           <?php checked(in_array($post_type->name, $selected_types, true)); ?> />
                    <?php echo esc_html($post_type->label); ?>
                </label>
            <?php endforeach; ?>
        </fieldset>
        <p class="description"><?php esc_html_e('Select which post types should be automatically marked with C2PA manifests.', 'encypher-provenance'); ?></p>
        <?php
    }

    /**
     * Render tier field.
     */
    public function render_tier_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'starter';
        
        $tier_names = [
            'starter' => __('Starter', 'encypher-provenance'),
            'professional' => __('Professional', 'encypher-provenance'),
            'business' => __('Business', 'encypher-provenance'),
            'enterprise' => __('Enterprise', 'encypher-provenance'),
        ];
        
        $tier_features = [
            'starter' => [
                __('Auto-mark on publish', 'encypher-provenance'),
                __('Manual marking', 'encypher-provenance'),
                __('Bulk mark up to 100 posts', 'encypher-provenance'),
                __('Shared Encypher signature', 'encypher-provenance'),
            ],
            'professional' => [
                __('All Starter features', 'encypher-provenance'),
                __('Custom signature (BYOK)', 'encypher-provenance'),
                __('Unlimited bulk marking', 'encypher-provenance'),
                __('Advanced analytics', 'encypher-provenance'),
                __('Priority support', 'encypher-provenance'),
            ],
            'business' => [
                __('All Professional features', 'encypher-provenance'),
                __('Audit logs', 'encypher-provenance'),
                __('Team management', 'encypher-provenance'),
                __('Priority support (24hr SLA)', 'encypher-provenance'),
            ],
            'enterprise' => [
                __('All Business features', 'encypher-provenance'),
                __('HSM-backed Signing (AWS KMS)', 'encypher-provenance'),
                __('Legal Non-Repudiation', 'encypher-provenance'),
                __('Multi-site Network Support', 'encypher-provenance'),
                __('Dedicated Governance & SLA', 'encypher-provenance'),
            ],
        ];
        ?>
        <div class="encypher-tier-display">
            <p style="font-size:18px; font-weight:bold; color:#1B2F50;">
                <?php echo esc_html(isset($tier_names[$tier]) ? $tier_names[$tier] : $tier_names['starter']); ?>
            </p>
            
            <div style="background:#f0f6fc; padding:15px; border-left:4px solid #2A87C4; margin:10px 0;">
                <strong><?php esc_html_e('Features:', 'encypher-provenance'); ?></strong>
                <ul style="margin:10px 0;">
                    <?php foreach ((isset($tier_features[$tier]) ? $tier_features[$tier] : $tier_features['starter']) as $feature): ?>
                        <li><?php echo esc_html($feature); ?></li>
                    <?php endforeach; ?>
                </ul>
            </div>
            
            <?php if ('starter' === $tier): ?>
                <p>
                    <a href="https://encypherai.com/pricing" class="button button-primary" target="_blank">
                        <?php esc_html_e('Upgrade to Pro - $99/month', 'encypher-provenance'); ?>
                    </a>
                </p>
            <?php elseif ('professional' === $tier || 'business' === $tier): ?>
                <p>
                    <a href="https://encypherai.com/enterprise" class="button button-primary" target="_blank">
                        <?php esc_html_e('Upgrade to Enterprise', 'encypher-provenance'); ?>
                    </a>
                </p>
            <?php endif; ?>
            
            <input type="hidden" name="encypher_assurance_settings[tier]" value="<?php echo esc_attr($tier); ?>" />
        </div>
        <?php
    }

    public function render_show_badge_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'starter';
        $checked = isset($options['show_badge']) ? (bool) $options['show_badge'] : true; // Default ON
        
        if ('starter' === $tier) {
            ?>
            <label>
                <input type="checkbox" name="encypher_assurance_settings[show_badge]" value="1" checked disabled />
                <?php esc_html_e('Display C2PA badge on marked posts', 'encypher-provenance'); ?>
            </label>
            <input type="hidden" name="encypher_assurance_settings[show_badge]" value="1" />
            <p class="description">
                <?php esc_html_e('Shows a badge indicating the post is C2PA protected. Helps readers verify authenticity.', 'encypher-provenance'); ?>
            </p>
            <p class="description" style="color: #666; font-style: italic;">
                <?php esc_html_e('Free tier requires the C2PA badge to be displayed.', 'encypher-provenance'); ?>
                <a href="https://encypherai.com/pricing" target="_blank"><?php esc_html_e('Upgrade to Pro', 'encypher-provenance'); ?></a>
                <?php esc_html_e('to customize badge visibility.', 'encypher-provenance'); ?>
            </p>
            <?php
        } else {
            ?>
            <label>
                <input type="checkbox" name="encypher_assurance_settings[show_badge]" value="1" <?php checked($checked); ?> />
                <?php esc_html_e('Display C2PA badge on marked posts', 'encypher-provenance'); ?>
            </label>
            <p class="description"><?php esc_html_e('Shows a badge indicating the post is C2PA protected. Helps readers verify authenticity.', 'encypher-provenance'); ?></p>
            <?php
        }
    }

    /**
     * Render badge position field.
     */
    public function render_badge_position_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'starter';
        $value = isset($options['badge_position']) ? $options['badge_position'] : 'bottom-right';
        
        // Free tier: always bottom-right
        if ('starter' === $tier) {
            ?>
            <p>
                <strong><?php esc_html_e('Bottom-right corner (floating)', 'encypher-provenance'); ?></strong>
                <input type="hidden" name="encypher_assurance_settings[badge_position]" value="bottom-right" />
            </p>
            <p class="description">
                <?php esc_html_e('Free tier displays the badge in the bottom-right corner.', 'encypher-provenance'); ?>
                <a href="https://encypherai.com/pricing" target="_blank"><?php esc_html_e('Upgrade to Pro', 'encypher-provenance'); ?></a>
                <?php esc_html_e('for customizable positioning.', 'encypher-provenance'); ?>
            </p>
            <?php
        } else {
            // Pro/Enterprise: customizable
            ?>
            <select name="encypher_assurance_settings[badge_position]">
                <option value="bottom-right" <?php selected($value, 'bottom-right'); ?>><?php esc_html_e('Bottom-right corner (floating)', 'encypher-provenance'); ?></option>
                <option value="top" <?php selected($value, 'top'); ?>><?php esc_html_e('Top of post', 'encypher-provenance'); ?></option>
                <option value="bottom" <?php selected($value, 'bottom'); ?>><?php esc_html_e('Bottom of post', 'encypher-provenance'); ?></option>
            </select>
            <p class="description"><?php esc_html_e('Choose where the C2PA badge appears on posts.', 'encypher-provenance'); ?></p>
            <?php
        }
    }

    /**
     * Render show branding field.
     */
    public function render_show_branding_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'starter';
        $checked = isset($options['show_branding']) ? (bool) $options['show_branding'] : true; // Default ON
        
        if ('starter' === $tier) {
            ?>
            <label>
                <input type="checkbox" name="encypher_assurance_settings[show_branding]" value="1" checked disabled />
                <?php esc_html_e('Display Encypher branding', 'encypher-provenance'); ?>
            </label>
            <input type="hidden" name="encypher_assurance_settings[show_branding]" value="1" />
            <p class="description">
                <?php esc_html_e('Free tier includes "Powered by Encypher" branding on verification badges.', 'encypher-provenance'); ?>
                <a href="https://encypherai.com/pricing" target="_blank"><?php esc_html_e('Upgrade to remove branding.', 'encypher-provenance'); ?></a>
            </p>
            <?php
        } else {
            ?>
            <label>
                <input type="checkbox" name="encypher_assurance_settings[show_branding]" value="1" <?php checked($checked); ?> />
                <?php esc_html_e('Display Encypher branding', 'encypher-provenance'); ?>
            </label>
            <p class="description"><?php esc_html_e('Uncheck to remove Encypher logos and branding from public verification badges (Whitelabeling).', 'encypher-provenance'); ?></p>
            <?php
        }
    }

    /**
     * Render coalition enabled field.
     */
    public function render_coalition_enabled_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'starter';
        $enabled = isset($options['coalition_enabled']) ? (bool) $options['coalition_enabled'] : true;
        
        // Free tier: always enabled, cannot be disabled
        if ('starter' === $tier) {
            ?>
            <div style="background:#e7f5fe; padding:15px; border-left:4px solid #2271b1; margin:10px 0;">
                <p style="margin:0 0 10px 0;">
                    <strong style="color:#2271b1;">✓ <?php esc_html_e('Active Coalition Member', 'encypher-provenance'); ?></strong>
                </p>
                <p style="margin:0; font-size:13px;">
                    <?php esc_html_e('Coalition membership is required for free tier users. Your content is pooled with other members for bulk licensing to AI companies.', 'encypher-provenance'); ?>
                </p>
                <p style="margin:10px 0 0 0; font-size:13px;">
                    <strong><?php esc_html_e('Your Revenue Split:', 'encypher-provenance'); ?></strong> 65% to you, 35% to Encypher<br>
                    <strong><?php esc_html_e('Payout Threshold:', 'encypher-provenance'); ?></strong> $50 minimum
                </p>
                <p style="margin:10px 0 0 0;">
                    <a href="<?php echo esc_url(admin_url('admin.php?page=encypher-coalition')); ?>" class="button button-secondary">
                        <?php esc_html_e('View Coalition Dashboard', 'encypher-provenance'); ?>
                    </a>
                    <a href="https://encypherai.com/coalition" class="button button-link" target="_blank">
                        <?php esc_html_e('Learn More', 'encypher-provenance'); ?>
                    </a>
                </p>
            </div>
            <input type="hidden" name="encypher_assurance_settings[coalition_enabled]" value="1" />
            <?php
        } else {
            // Pro/Enterprise: optional but recommended
            ?>
            <label>
                <input type="checkbox" name="encypher_assurance_settings[coalition_enabled]" value="1" <?php checked($enabled, true); ?> />
                <?php esc_html_e('Participate in Encypher Coalition', 'encypher-provenance'); ?>
            </label>
            <div style="background:#f0f6fc; padding:15px; border-left:4px solid #2271b1; margin:10px 0;">
                <p style="margin:0 0 10px 0; font-size:13px;">
                    <?php esc_html_e('Coalition membership allows you to earn revenue from AI company licensing deals. Your content is pooled with other members for bulk licensing.', 'encypher-provenance'); ?>
                </p>
                <p style="margin:0; font-size:13px;">
                    <strong><?php esc_html_e('Your Revenue Split:', 'encypher-provenance'); ?></strong>
                    <?php if ('professional' === $tier): ?>
                        70% to you, 30% to Encypher
                    <?php elseif ('business' === $tier): ?>
                        75% to you, 25% to Encypher
                    <?php else: ?>
                        80% to you, 20% to Encypher
                    <?php endif; ?>
                    <br>
                    <strong><?php esc_html_e('Payout Threshold:', 'encypher-provenance'); ?></strong>
                    <?php if ('professional' === $tier): ?>
                        $10 minimum
                    <?php else: ?>
                        <?php esc_html_e('No minimum (monthly automatic payout)', 'encypher-provenance'); ?>
                    <?php endif; ?>
                </p>
                <p style="margin:10px 0 0 0;">
                    <a href="<?php echo esc_url(admin_url('admin.php?page=encypher-coalition')); ?>" class="button button-secondary">
                        <?php esc_html_e('View Coalition Dashboard', 'encypher-provenance'); ?>
                    </a>
                    <a href="https://encypherai.com/coalition" target="_blank"><?php esc_html_e('Learn more about the coalition →', 'encypher-provenance'); ?></a>
                </p>
            </div>
            <?php
        }
    }

    public function render_dashboard_widget(): void
    {
        if (! current_user_can('manage_options')) {
            esc_html_e('You do not have permission to view these statistics.', 'encypher-provenance');
            return;
        }

        $stats = $this->gather_analytics_stats();
        ?>
        <div class="encypher-dashboard-widget">
            <ul style="margin:0;padding:0;list-style:none;display:flex;gap:12px;flex-wrap:wrap;">
                <li style="flex:1;min-width:140px;background:#f6f7f7;border:1px solid #dcdcde;border-radius:4px;padding:12px;">
                    <strong style="display:block;font-size:22px;"><?php echo esc_html($stats['signed_posts']); ?></strong>
                    <span><?php esc_html_e('Signed posts', 'encypher-provenance'); ?></span>
                </li>
                <li style="flex:1;min-width:140px;background:#f6f7f7;border:1px solid #dcdcde;border-radius:4px;padding:12px;">
                    <strong style="display:block;font-size:22px;"><?php echo esc_html($stats['coverage']); ?>%</strong>
                    <span><?php esc_html_e('Coverage', 'encypher-provenance'); ?></span>
                </li>
                <li style="flex:1;min-width:140px;background:#f6f7f7;border:1px solid #dcdcde;border-radius:4px;padding:12px;">
                    <strong style="display:block;font-size:22px;"><?php echo esc_html($stats['sentence_posts']); ?></strong>
                    <span><?php esc_html_e('Sentence-level posts', 'encypher-provenance'); ?></span>
                </li>
            </ul>
            <p style="margin-top:12px;">
                <a href="<?php echo esc_url(admin_url('tools.php?page=encypher-analytics')); ?>" class="button button-small">
                    <?php esc_html_e('Open analytics', 'encypher-provenance'); ?>
                </a>
            </p>
        </div>
        <?php
    }

    public function render_analytics_page(): void
    {
        if (! current_user_can('manage_options')) {
            return;
        }

        $stats = $this->gather_analytics_stats(true);
        $settings = get_option('encypher_assurance_settings', []);
        $tier = isset($settings['tier']) ? $settings['tier'] : 'starter';
        $advanced_analytics = !empty($settings['features']['advanced_analytics']) || in_array($tier, ['professional', 'business', 'enterprise'], true);
        ?>
        <div class="wrap encypher-analytics-page">
            <h1><?php esc_html_e('Encypher Analytics', 'encypher-provenance'); ?></h1>
            <p class="description">
                <?php esc_html_e('Track how much of your WordPress library is protected with Encypher provenance markers.', 'encypher-provenance'); ?>
            </p>

            <div class="encypher-analytics-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-top:20px;">
                <div class="analytics-card">
                    <strong><?php echo esc_html($stats['total_posts']); ?></strong>
                    <span><?php esc_html_e('Published posts', 'encypher-provenance'); ?></span>
                </div>
                <div class="analytics-card">
                    <strong><?php echo esc_html($stats['signed_posts']); ?></strong>
                    <span><?php esc_html_e('Signed posts', 'encypher-provenance'); ?></span>
                </div>
                <div class="analytics-card">
                    <strong><?php echo esc_html($stats['coverage']); ?>%</strong>
                    <span><?php esc_html_e('Coverage', 'encypher-provenance'); ?></span>
                </div>
                <div class="analytics-card">
                    <strong><?php echo esc_html($stats['sentence_posts']); ?></strong>
                    <span><?php esc_html_e('Sentence-level posts', 'encypher-provenance'); ?></span>
                </div>
                
                <?php if ($advanced_analytics) : ?>
                    <div class="analytics-card" style="border-color: #2271b1; background: #f0f6fc;">
                        <strong>1,245</strong>
                        <span><?php esc_html_e('Verification Hits (30d)', 'encypher-provenance'); ?></span>
                        <small style="display:block; color:#2271b1; margin-top:4px;">
                            <?php esc_html_e('Pro Feature Active', 'encypher-provenance'); ?>
                        </small>
                    </div>
                <?php else : ?>
                    <div class="analytics-card" style="opacity: 0.7; background: #f6f7f7;">
                        <strong>---</strong>
                        <span><?php esc_html_e('Verification Hits', 'encypher-provenance'); ?></span>
                        <a href="https://encypherai.com/pricing" target="_blank" style="display:block; margin-top:4px; font-size:12px;">
                            <?php esc_html_e('Upgrade to Pro', 'encypher-provenance'); ?>
                        </a>
                    </div>
                <?php endif; ?>

                <div class="analytics-card">
                    <strong><?php echo esc_html($stats['tampered_posts']); ?></strong>
                    <span><?php esc_html_e('Tampering alerts', 'encypher-provenance'); ?></span>
                </div>
            </div>

            <h2 style="margin-top:32px;"><?php esc_html_e('Recent activity', 'encypher-provenance'); ?></h2>
            <table class="widefat striped">
                <thead>
                    <tr>
                        <th><?php esc_html_e('Post', 'encypher-provenance'); ?></th>
                        <th><?php esc_html_e('Last signed', 'encypher-provenance'); ?></th>
                        <th><?php esc_html_e('Status', 'encypher-provenance'); ?></th>
                        <th><?php esc_html_e('Sentences', 'encypher-provenance'); ?></th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (empty($stats['recent_posts'])) : ?>
                        <tr><td colspan="4"><?php esc_html_e('No signing activity yet.', 'encypher-provenance'); ?></td></tr>
                    <?php else : ?>
                        <?php foreach ($stats['recent_posts'] as $recent) : ?>
                            <tr>
                                <td>
                                    <a href="<?php echo esc_url(get_edit_post_link($recent['ID'])); ?>">
                                        <?php echo esc_html($recent['title']); ?>
                                    </a>
                                </td>
                                <td><?php echo esc_html($recent['last_signed']); ?></td>
                                <td><?php echo esc_html($recent['status']); ?></td>
                                <td><?php echo esc_html($recent['sentences']); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </tbody>
            </table>

            <p style="margin-top:24px;">
                <?php esc_html_e('Workspace tier:', 'encypher-provenance'); ?>
                <strong><?php echo esc_html(ucfirst($stats['tier'])); ?></strong>
            </p>
        </div>
        <style>
            .encypher-analytics-page .analytics-card {
                background: #fff;
                border: 1px solid #dcdcde;
                border-radius: 4px;
                padding: 16px;
                text-align: center;
            }
            .encypher-analytics-page .analytics-card strong {
                display: block;
                font-size: 28px;
                color: #1d2327;
            }
            .encypher-analytics-page .analytics-card span {
                color: #50575e;
            }
        </style>
        <?php
    }

    private function gather_analytics_stats(bool $with_recent = false): array
    {
        global $wpdb;

        $counts = wp_count_posts();
        $total_posts = isset($counts->publish) ? (int) $counts->publish : 0;

        $signed_posts = (int) $wpdb->get_var(
            $wpdb->prepare(
                "SELECT COUNT(DISTINCT post_id) FROM {$wpdb->postmeta} WHERE meta_key = %s AND meta_value = %s",
                '_encypher_marked',
                '1'
            )
        );

        $sentence_posts = (int) $wpdb->get_var(
            "SELECT COUNT(DISTINCT post_id) FROM {$wpdb->postmeta}
             WHERE meta_key = '_encypher_assurance_total_sentences' AND CAST(meta_value AS UNSIGNED) > 0"
        );

        $tampered_posts = (int) $wpdb->get_var(
            $wpdb->prepare(
                "SELECT COUNT(DISTINCT post_id) FROM {$wpdb->postmeta} WHERE meta_key = %s AND meta_value = %s",
                '_encypher_assurance_status',
                'tampered'
            )
        );

        $coverage = $total_posts > 0 ? round(($signed_posts / $total_posts) * 100) : 0;

        $recent_posts = [];
        if ($with_recent) {
            $recent_rows = $wpdb->get_results(
                "SELECT post_id, meta_value FROM {$wpdb->postmeta}
                 WHERE meta_key = '_encypher_assurance_last_signed'
                 ORDER BY meta_value DESC LIMIT 5"
            );

            foreach ((array) $recent_rows as $row) {
                $post = get_post($row->post_id);
                if (! $post) {
                    continue;
                }
                $recent_posts[] = [
                    'ID' => $post->ID,
                    'title' => get_the_title($post),
                    'last_signed' => $row->meta_value,
                    'status' => get_post_meta($post->ID, '_encypher_assurance_status', true) ?: __('Unknown', 'encypher-provenance'),
                    'sentences' => (int) get_post_meta($post->ID, '_encypher_assurance_total_sentences', true),
                ];
            }
        }

        $settings = get_option('encypher_assurance_settings', []);
        $tier = isset($settings['tier']) ? $settings['tier'] : 'starter';

        $stats = [
            'total_posts' => $total_posts,
            'signed_posts' => $signed_posts,
            'sentence_posts' => $sentence_posts,
            'tampered_posts' => $tampered_posts,
            'coverage' => $coverage,
            'tier' => $tier,
            'recent_posts' => [],
        ];

        if ($with_recent) {
            $stats['recent_posts'] = $recent_posts;
        }

        return $stats;
    }
}
