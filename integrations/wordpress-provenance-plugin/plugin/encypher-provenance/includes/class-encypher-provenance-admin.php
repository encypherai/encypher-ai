<?php
namespace EncypherProvenance;

if (! defined('ABSPATH')) {
    exit;
}

/**
 * Handles admin settings and editor integrations.
 */
class Admin
{
    private const ACCOUNT_CACHE_TTL = 900; // 15 minutes
    private function get_icon(string $name, string $class = 'encypher-icon'): string
    {
        $icons = [
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
        add_action('admin_head', [$this, 'output_admin_menu_icon_css']);
        add_action('enqueue_block_editor_assets', [$this, 'enqueue_block_editor_assets']);
        add_action('wp_dashboard_setup', [$this, 'register_dashboard_widget']);
        add_action('wp_ajax_encypher_dismiss_onboarding', [$this, 'ajax_dismiss_onboarding']);
        add_action('wp_ajax_encypher_clear_error_log', [$this, 'ajax_clear_error_log']);
        add_action('wp_ajax_encypher_export_error_log', [$this, 'ajax_export_error_log']);
        // Classic editor meta box disabled - using Gutenberg sidebar instead
        // add_action('admin_enqueue_scripts', [$this, 'enqueue_classic_assets']);
        // add_action('add_meta_boxes', [$this, 'register_classic_meta_box']);
    }

    public function output_admin_menu_icon_css(): void
    {
        echo '<style>';
        echo '#adminmenu #toplevel_page_encypher .wp-menu-image img{width:20px;height:20px;max-width:20px;max-height:20px;padding:7px 0;box-sizing:content-box;filter:brightness(0) invert(.65);}';
        echo '#adminmenu #toplevel_page_encypher:hover .wp-menu-image img{filter:brightness(0) invert(1);}';
        echo '#adminmenu .wp-has-current-submenu#toplevel_page_encypher .wp-menu-image img{filter:brightness(0) invert(1);}';
        echo '</style>';
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
        $icon_svg = ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/images/encypher_check_color.svg';

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
    }

    public function register_settings(): void
    {
        register_setting('encypher_provenance_settings_group', 'encypher_provenance_settings', [
            'type' => 'array',
            'sanitize_callback' => [$this, 'sanitize_settings'],
            'default' => [
                'api_base_url' => 'https://api.encypherai.com/api/v1',
                'api_key' => '',
                'connect_email' => '',
                'connect_session_id' => '',
                'auto_verify' => true,
                'connection_last_status' => 'unknown',
                'connection_last_checked_at' => '',
                'auto_mark_on_publish' => true,
                'auto_mark_on_update' => true,
                'metadata_format' => 'c2pa',
                'add_hard_binding' => true,
                'tier' => 'free',
                'signing_mode' => 'managed',
                'signing_profile_id' => '',
                'organization_id' => '',
                'organization_name' => '',
                'usage' => [
                    'api_calls' => [
                        'used' => 0,
                        'limit' => 1000,
                        'remaining' => 1000,
                        'percentage_used' => 0,
                        'is_unlimited' => false,
                        'reset_date' => '',
                    ],
                ],
                'post_types' => ['post', 'page'],
                'error_webhook_url' => '',
                'error_webhook_threshold' => 3,
            ],
        ]);

        add_settings_section(
            'encypher_provenance_main_section',
            __('Workspace Connection', 'encypher-provenance'),
            function () {
                echo '<p>' . esc_html__('Connect WordPress to your Encypher workspace so the plugin can sign, verify, and report provenance automatically. The recommended path is secure email connect. Existing API keys remain supported for teams that manage credentials manually.', 'encypher-provenance') . '</p>';
            },
            'encypher-provenance-settings'
        );

        add_settings_field(
            'encypher_provenance_magic_link_connect',
            __('Email connect', 'encypher-provenance'),
            [$this, 'render_magic_link_connect_field'],
            'encypher-provenance-settings',
            'encypher_provenance_main_section'
        );

        add_settings_field(
            'encypher_provenance_api_key',
            __('Existing API key (optional)', 'encypher-provenance'),
            [$this, 'render_api_key_field'],
            'encypher-provenance-settings',
            'encypher_provenance_main_section'
        );

        add_settings_field(
            'encypher_provenance_api_base_url',
            __('Encypher API URL', 'encypher-provenance'),
            [$this, 'render_api_base_url_field'],
            'encypher-provenance-settings',
            'encypher_provenance_main_section'
        );

        add_settings_field(
            'encypher_provenance_auto_verify',
            __('Automatically verify content on render', 'encypher-provenance'),
            [$this, 'render_auto_verify_field'],
            'encypher-provenance-settings',
            'encypher_provenance_main_section'
        );

        // Signature Management Section
        add_settings_section(
            'encypher_provenance_signature_section',
            __('Signature Management', 'encypher-provenance'),
            function () {
                echo '<p>' . esc_html__('Manage how your content is signed. Free workspaces use Encypher-managed certificates. Enterprise can bring their own signing profiles.', 'encypher-provenance') . '</p>';
            },
            'encypher-provenance-settings'
        );

        add_settings_field(
            'encypher_provenance_signing_mode',
            __('Signature mode', 'encypher-provenance'),
            [$this, 'render_signing_mode_field'],
            'encypher-provenance-settings',
            'encypher_provenance_signature_section'
        );

        add_settings_field(
            'encypher_provenance_signing_profile_id',
            __('Signing profile ID', 'encypher-provenance'),
            [$this, 'render_signing_profile_id_field'],
            'encypher-provenance-settings',
            'encypher_provenance_signature_section'
        );

        // C2PA Settings Section
        add_settings_section(
            'encypher_provenance_c2pa_section',
            __('C2PA Settings', 'encypher-provenance'),
            function () {
                echo '<p>' . esc_html__('Configure C2PA-compliant text authentication options.', 'encypher-provenance') . '</p>';
            },
            'encypher-provenance-settings'
        );

        add_settings_field(
            'encypher_provenance_auto_mark_on_publish',
            __('Auto-mark on publish', 'encypher-provenance'),
            [$this, 'render_auto_mark_on_publish_field'],
            'encypher-provenance-settings',
            'encypher_provenance_c2pa_section'
        );

        add_settings_field(
            'encypher_provenance_auto_mark_on_update',
            __('Auto-mark on update', 'encypher-provenance'),
            [$this, 'render_auto_mark_on_update_field'],
            'encypher-provenance-settings',
            'encypher_provenance_c2pa_section'
        );

        add_settings_field(
            'encypher_provenance_metadata_format',
            __('Metadata format', 'encypher-provenance'),
            [$this, 'render_metadata_format_field'],
            'encypher-provenance-settings',
            'encypher_provenance_c2pa_section'
        );

        add_settings_field(
            'encypher_provenance_post_types',
            __('Post types to auto-mark', 'encypher-provenance'),
            [$this, 'render_post_types_field'],
            'encypher-provenance-settings',
            'encypher_provenance_c2pa_section'
        );

        // Display Settings Section
        add_settings_section(
            'encypher_provenance_display_section',
            __('Display Settings', 'encypher-provenance'),
            function () {
                echo '<p>' . esc_html__('Configure how C2PA badges appear on your site.', 'encypher-provenance') . '</p>';
            },
            'encypher-provenance-settings'
        );

        add_settings_field(
            'encypher_provenance_show_badge',
            __('Show C2PA badge', 'encypher-provenance'),
            [$this, 'render_show_badge_field'],
            'encypher-provenance-settings',
            'encypher_provenance_display_section'
        );

        add_settings_field(
            'encypher_provenance_badge_position',
            __('Badge position', 'encypher-provenance'),
            [$this, 'render_badge_position_field'],
            'encypher-provenance-settings',
            'encypher_provenance_display_section'
        );

        add_settings_field(
            'encypher_provenance_show_branding',
            __('Whitelabeling (Hide Branding)', 'encypher-provenance'),
            [$this, 'render_show_branding_field'],
            'encypher-provenance-settings',
            'encypher_provenance_display_section'
        );

        // Tier Settings Section
        add_settings_section(
            'encypher_provenance_tier_section',
            __('Tier & Subscription', 'encypher-provenance'),
            function () {
                echo '<p>' . esc_html__('Your current subscription tier and upgrade options.', 'encypher-provenance') . '</p>';
            },
            'encypher-provenance-settings'
        );

        add_settings_field(
            'encypher_provenance_tier',
            __('Current tier', 'encypher-provenance'),
            [$this, 'render_tier_field'],
            'encypher-provenance-settings',
            'encypher_provenance_tier_section'
        );

        // Alerting Section
        add_settings_section(
            'encypher_provenance_alerting_section',
            __('Alerting & Error Reporting', 'encypher-provenance'),
            function () {
                $settings = get_option('encypher_provenance_settings', []);
                $tier = $settings['tier'] ?? 'free';
                if (! in_array($tier, ['enterprise', 'strategic_partner'], true)) {
                    echo '<p>' . wp_kses(
                        sprintf(
                            /* translators: %s: upgrade link */
                            __('Webhook alerting is an Enterprise add-on. <a href="%s" target="_blank" rel="noopener noreferrer">Upgrade to Enterprise</a> to enable outbound failure webhooks.', 'encypher-provenance'),
                            'https://encypherai.com/pricing'
                        ),
                        ['a' => ['href' => [], 'target' => [], 'rel' => []]]
                    ) . '</p>';
                } else {
                    echo '<p>' . esc_html__('Configure outbound webhooks to receive real-time alerts when signing fails repeatedly.', 'encypher-provenance') . '</p>';
                }
            },
            'encypher-provenance-settings'
        );

        add_settings_field(
            'encypher_provenance_error_webhook_url',
            __('Failure webhook URL', 'encypher-provenance'),
            [$this, 'render_error_webhook_url_field'],
            'encypher-provenance-settings',
            'encypher_provenance_alerting_section'
        );

        add_settings_field(
            'encypher_provenance_error_webhook_threshold',
            __('Alert after N consecutive failures', 'encypher-provenance'),
            [$this, 'render_error_webhook_threshold_field'],
            'encypher-provenance-settings',
            'encypher_provenance_alerting_section'
        );

        // Coalition Settings Section
        add_settings_section(
            'encypher_provenance_coalition_section',
            __('Coalition Membership', 'encypher-provenance'),
            function () {
                echo '<p>' . esc_html__('Participate in the Encypher Coalition to earn revenue from AI company licensing deals.', 'encypher-provenance') . '</p>';
            },
            'encypher-provenance-settings'
        );

        add_settings_field(
            'encypher_provenance_coalition_enabled',
            __('Coalition Status', 'encypher-provenance'),
            [$this, 'render_coalition_enabled_field'],
            'encypher-provenance-settings',
            'encypher_provenance_coalition_section'
        );

        add_settings_field(
            'encypher_provenance_coalition_auto_enroll',
            __('Auto-enroll in Encypher Coalition', 'encypher-provenance'),
            [$this, 'render_coalition_auto_enroll_field'],
            'encypher-provenance-settings',
            'encypher_provenance_coalition_section'
        );

        // WordPress/ai Integration Section
        add_settings_section(
            'encypher_provenance_wordpress_ai_section',
            __('WordPress/ai Integration', 'encypher-provenance'),
            function () {
                echo '<p>' . esc_html__('Automatically sign content generated by the WordPress/ai (AI Experiments) plugin with Encypher C2PA provenance.', 'encypher-provenance') . '</p>';
            },
            'encypher-provenance-settings'
        );

        add_settings_field(
            'encypher_provenance_wordpress_ai_enabled',
            __('Enable WordPress/ai Integration', 'encypher-provenance'),
            [$this, 'render_wordpress_ai_enabled_field'],
            'encypher-provenance-settings',
            'encypher_provenance_wordpress_ai_section'
        );

    }

    /**
     * Normalizes an API base URL to always end with /api/v1 (no trailing slash).
     * Accepts both https://api.encypherai.com/ and https://api.encypherai.com/api/v1.
     */
    private static function normalize_api_base_url(string $url): string
    {
        $url = rtrim(trim($url), '/');
        if ('' === $url) {
            return '';
        }
        if (! str_ends_with($url, '/api/v1')) {
            $url .= '/api/v1';
        }
        return $url;
    }

    public function sanitize_settings(array $settings): array
    {
        $sanitized = [];
        $current_settings = get_option('encypher_provenance_settings', []);
        if (! is_array($current_settings)) {
            $current_settings = [];
        }
        $sanitized['api_base_url'] = isset($settings['api_base_url']) ? esc_url_raw(trim($settings['api_base_url'])) : 'https://api.encypherai.com/api/v1';
        $sanitized['api_base_url'] = self::normalize_api_base_url($sanitized['api_base_url']);
        $sanitized['api_key'] = isset($settings['api_key']) ? sanitize_text_field($settings['api_key']) : '';
        $sanitized['connect_email'] = isset($settings['connect_email'])
            ? sanitize_email((string) $settings['connect_email'])
            : (isset($current_settings['connect_email']) ? sanitize_email((string) $current_settings['connect_email']) : '');
        $sanitized['connect_session_id'] = isset($settings['connect_session_id'])
            ? sanitize_text_field((string) $settings['connect_session_id'])
            : (isset($current_settings['connect_session_id']) ? sanitize_text_field((string) $current_settings['connect_session_id']) : '');
        $sanitized['auto_verify'] = isset($settings['auto_verify']) ? (bool) $settings['auto_verify'] : false;
        $valid_connection_states = ['unknown', 'connected', 'auth_required', 'disconnected'];
        $connection_last_status = isset($settings['connection_last_status']) ? sanitize_key((string) $settings['connection_last_status']) : (isset($current_settings['connection_last_status']) ? sanitize_key((string) $current_settings['connection_last_status']) : 'unknown');
        $sanitized['connection_last_status'] = in_array($connection_last_status, $valid_connection_states, true) ? $connection_last_status : 'unknown';
        $sanitized['connection_last_checked_at'] = isset($settings['connection_last_checked_at']) ? sanitize_text_field((string) $settings['connection_last_checked_at']) : (isset($current_settings['connection_last_checked_at']) ? sanitize_text_field((string) $current_settings['connection_last_checked_at']) : '');
        $sanitized['auto_mark_on_publish'] = isset($settings['auto_mark_on_publish']) ? (bool) $settings['auto_mark_on_publish'] : true;
        $sanitized['auto_mark_on_update'] = isset($settings['auto_mark_on_update']) ? (bool) $settings['auto_mark_on_update'] : true;
        $sanitized['metadata_format'] = isset($settings['metadata_format']) && in_array($settings['metadata_format'], ['basic', 'c2pa'], true) ? $settings['metadata_format'] : 'c2pa';
        $sanitized['add_hard_binding'] = true;
        $sanitized['post_types'] = isset($settings['post_types']) && is_array($settings['post_types']) ? array_map('sanitize_text_field', $settings['post_types']) : ['post', 'page'];

        $account = null;
        $previous_tier = isset($current_settings['tier']) ? $current_settings['tier'] : 'free';
        $previous_org_id = isset($current_settings['organization_id']) ? $current_settings['organization_id'] : '';
        $previous_org_name = isset($current_settings['organization_name']) ? $current_settings['organization_name'] : '';
        if (!empty($sanitized['api_key'])) {
            $account = $this->resolve_remote_account($sanitized['api_base_url'], $sanitized['api_key'], $current_settings);
            if (is_wp_error($account)) {
                add_settings_error(
                    'encypher_provenance_settings',
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
            $sanitized['usage'] = $this->normalize_usage_snapshot(
                isset($account['usage']) && is_array($account['usage']) ? $account['usage'] : [],
                $sanitized['tier']
            );
        } elseif (!empty($sanitized['api_key']) && $previous_tier !== 'free') {
            // Keep last-known tier if dashboard lookup failed but we have a previous subscription
            $sanitized['tier'] = $previous_tier;
            $sanitized['organization_id'] = $previous_org_id;
            $sanitized['organization_name'] = $previous_org_name;
            $sanitized['features'] = isset($current_settings['features']) ? $current_settings['features'] : [];
            $sanitized['usage'] = $this->normalize_usage_snapshot(
                isset($current_settings['usage']) && is_array($current_settings['usage']) ? $current_settings['usage'] : [],
                $sanitized['tier']
            );
            add_settings_error(
                'encypher_provenance_settings',
                'tier_last_known',
                __('Using last known subscription details until the dashboard becomes reachable.', 'encypher-provenance'),
                'warning'
            );
        } else {
            $sanitized['tier'] = 'free';
            $sanitized['organization_id'] = '';
            $sanitized['organization_name'] = '';
            $sanitized['usage'] = $this->normalize_usage_snapshot([], 'free');
        }

        $requested_mode = isset($settings['signing_mode']) && in_array($settings['signing_mode'], ['managed', 'byok'], true) ? $settings['signing_mode'] : 'managed';
        if ('free' === $sanitized['tier']) {
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
                        'encypher_provenance_settings',
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

        // Free tier: badge must always be shown with branding; position is user-configurable
        $valid_positions = ['top', 'bottom', 'bottom-right'];
        if ($sanitized['tier'] === 'free') {
            $sanitized['show_badge'] = true;
            $sanitized['badge_position'] = isset($settings['badge_position']) && in_array($settings['badge_position'], $valid_positions, true) ? $settings['badge_position'] : 'bottom';
            $sanitized['coalition_enabled'] = true; // Always enabled for free tier
            $sanitized['show_branding'] = true; // Always show branding for free tier
        } else {
            $sanitized['show_badge'] = isset($settings['show_badge']) ? (bool) $settings['show_badge'] : true;
            $sanitized['badge_position'] = isset($settings['badge_position']) && in_array($settings['badge_position'], $valid_positions, true) ? $settings['badge_position'] : 'bottom';
            $sanitized['coalition_enabled'] = isset($settings['coalition_enabled']) ? (bool) $settings['coalition_enabled'] : true; // Optional for enterprise
            $sanitized['show_branding'] = isset($settings['show_branding']) ? (bool) $settings['show_branding'] : true;
        }

        // Alerting: webhook URL only writable by enterprise; free tier always cleared
        $is_enterprise_tier = in_array($sanitized['tier'], ['enterprise', 'strategic_partner'], true);
        if ($is_enterprise_tier && ! empty($settings['error_webhook_url'])) {
            $sanitized['error_webhook_url'] = esc_url_raw(trim((string) $settings['error_webhook_url']));
        } else {
            $sanitized['error_webhook_url'] = '';
        }
        $sanitized['error_webhook_threshold'] = isset($settings['error_webhook_threshold'])
            ? max(1, min(100, (int) $settings['error_webhook_threshold']))
            : 3;

        // WordPress/ai integration toggle
        $sanitized['wordpress_ai_enabled'] = isset($settings['wordpress_ai_enabled']) ? (bool) $settings['wordpress_ai_enabled'] : false;

        // Coalition auto-enroll toggle
        $sanitized['coalition_auto_enroll'] = isset($settings['coalition_auto_enroll']) ? (bool) $settings['coalition_auto_enroll'] : false;

        return $sanitized;
    }

    private function resolve_remote_account(string $api_base_url, string $api_key, $fallback = [])
    {
        if (! is_array($fallback)) {
            $fallback = [];
        }

        $base = rtrim((string) $api_base_url, '/');
        if ('' === $base || '' === trim($api_key)) {
            return [
                'tier' => 'free',
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
        $tier = $data['tier'] ?? 'free';
        if (! in_array($tier, ['free', 'enterprise', 'strategic_partner'], true)) {
            $tier = 'free';
        }

        $features = isset($data['features']) && is_array($data['features']) ? $data['features'] : [];
        $usage = $this->fetch_remote_usage_quota($base, $api_key, $tier, $fallback);

        $account = [
            'tier' => $tier,
            'organization_id' => isset($data['organization_id']) ? sanitize_text_field((string) $data['organization_id']) : '',
            'organization_name' => isset($data['organization_name']) ? sanitize_text_field((string) $data['organization_name']) : '',
            'features' => $features,
            'usage' => $usage,
        ];

        set_site_transient($cache_key, $account, self::ACCOUNT_CACHE_TTL);

        return $account;
    }

    private function build_account_cache_key(string $api_base_url, string $api_key): string
    {
        return 'encypher_account_' . md5(strtolower($api_base_url) . '|' . substr(hash('sha256', $api_key), 0, 16));
    }

    private function fetch_remote_usage_quota(string $api_base_url, string $api_key, string $tier, array $fallback = []): array
    {
        $fallback_usage = isset($fallback['usage']) && is_array($fallback['usage'])
            ? $fallback['usage']
            : [];
        $normalized_fallback = $this->normalize_usage_snapshot($fallback_usage, $tier);
        $quota_url = rtrim((string) $api_base_url, '/') . '/account/quota';
        $response = wp_remote_get($quota_url, [
            'timeout' => 15,
            'headers' => [
                'Accept' => 'application/json',
                'Authorization' => 'Bearer ' . sanitize_text_field($api_key),
            ],
        ]);

        if (is_wp_error($response)) {
            return $normalized_fallback;
        }

        $status_code = wp_remote_retrieve_response_code($response);
        if ($status_code >= 400) {
            return $normalized_fallback;
        }

        $body = json_decode(wp_remote_retrieve_body($response), true);
        if (! is_array($body)) {
            return $normalized_fallback;
        }

        $data = isset($body['data']) && is_array($body['data']) ? $body['data'] : [];
        $metrics = isset($data['metrics']) && is_array($data['metrics']) ? $data['metrics'] : [];
        $api_calls = isset($metrics['api_calls']) && is_array($metrics['api_calls']) ? $metrics['api_calls'] : [];

        if (empty($api_calls)) {
            return $normalized_fallback;
        }

        return $this->normalize_usage_snapshot([
            'api_calls' => [
                'used' => isset($api_calls['used']) ? (int) $api_calls['used'] : 0,
                'limit' => isset($api_calls['limit']) ? (int) $api_calls['limit'] : ('free' === $tier ? 1000 : -1),
                'remaining' => isset($api_calls['remaining']) ? (int) $api_calls['remaining'] : 0,
                'percentage_used' => isset($api_calls['percentage_used']) ? (float) $api_calls['percentage_used'] : 0,
                'is_unlimited' => isset($api_calls['limit']) ? ((int) $api_calls['limit'] < 0) : ('free' !== $tier),
                'reset_date' => isset($data['reset_date']) ? sanitize_text_field((string) $data['reset_date']) : '',
                'period_end' => isset($data['period_end']) ? sanitize_text_field((string) $data['period_end']) : '',
            ],
        ], $tier);
    }

    private function normalize_usage_snapshot(array $usage, string $tier): array
    {
        $default_limit = 'free' === $tier ? 1000 : -1;
        $api_calls = isset($usage['api_calls']) && is_array($usage['api_calls']) ? $usage['api_calls'] : $usage;

        $used = isset($api_calls['used']) ? max(0, (int) $api_calls['used']) : 0;
        $limit = isset($api_calls['limit']) ? (int) $api_calls['limit'] : $default_limit;
        $is_unlimited = isset($api_calls['is_unlimited']) ? (bool) $api_calls['is_unlimited'] : ($limit < 0);

        if ($is_unlimited) {
            $limit = -1;
            $remaining = -1;
            $percentage_used = 0.0;
        } else {
            if ($limit <= 0) {
                $limit = $default_limit > 0 ? $default_limit : 1000;
            }
            $remaining = isset($api_calls['remaining'])
                ? max(0, (int) $api_calls['remaining'])
                : max(0, $limit - $used);
            $percentage_used = isset($api_calls['percentage_used'])
                ? (float) $api_calls['percentage_used']
                : ($limit > 0 ? round(($used / $limit) * 100, 2) : 0.0);
        }

        if (! $is_unlimited) {
            $percentage_used = min(100.0, max(0.0, $percentage_used));
        }

        return [
            'api_calls' => [
                'used' => $used,
                'limit' => $limit,
                'remaining' => $remaining,
                'percentage_used' => $percentage_used,
                'is_unlimited' => $is_unlimited,
                'reset_date' => isset($api_calls['reset_date']) ? sanitize_text_field((string) $api_calls['reset_date']) : '',
                'period_end' => isset($api_calls['period_end']) ? sanitize_text_field((string) $api_calls['period_end']) : '',
            ],
        ];
    }

    private function get_usage_snapshot($settings, bool $refresh_remote = false): array
    {
        if (! is_array($settings)) {
            $settings = [];
        }

        $tier = isset($settings['tier']) ? (string) $settings['tier'] : 'free';
        $usage = $this->normalize_usage_snapshot(
            isset($settings['usage']) && is_array($settings['usage']) ? $settings['usage'] : [],
            $tier
        );

        if (! $refresh_remote) {
            return $usage;
        }

        $api_key = isset($settings['api_key']) ? trim((string) $settings['api_key']) : '';
        $api_base_url = isset($settings['api_base_url']) ? trim((string) $settings['api_base_url']) : '';
        if ('' === $api_key || '' === $api_base_url) {
            return $usage;
        }

        $quota_usage = $this->fetch_remote_usage_quota($api_base_url, $api_key, $tier, [
            'usage' => $usage,
        ]);
        if (isset($quota_usage['api_calls']) && is_array($quota_usage['api_calls'])) {
            return $quota_usage;
        }

        $account = $this->resolve_remote_account($api_base_url, $api_key, $settings);
        if (is_array($account) && isset($account['usage']) && is_array($account['usage'])) {
            return $this->normalize_usage_snapshot($account['usage'], $tier);
        }

        return $usage;
    }

    private function render_usage_progress_bar(array $usage, string $wrapper_class = 'encypher-usage-progress', string $title = 'Monthly API call usage'): void
    {
        $api_calls = isset($usage['api_calls']) && is_array($usage['api_calls']) ? $usage['api_calls'] : [];
        $used = isset($api_calls['used']) ? max(0, (int) $api_calls['used']) : 0;
        $limit = isset($api_calls['limit']) ? (int) $api_calls['limit'] : 1000;
        $remaining = isset($api_calls['remaining']) ? (int) $api_calls['remaining'] : max(0, $limit - $used);
        $percentage = isset($api_calls['percentage_used']) ? (float) $api_calls['percentage_used'] : 0.0;
        $is_unlimited = ! empty($api_calls['is_unlimited']) || $limit < 0;
        $reset_date = isset($api_calls['reset_date']) ? (string) $api_calls['reset_date'] : '';
        $human_readable_reset_date = $reset_date;

        if ($reset_date) {
            $reset_timestamp = strtotime($reset_date);
            if (false !== $reset_timestamp) {
                $human_readable_reset_date = wp_date(
                    get_option('date_format') . ' ' . get_option('time_format'),
                    $reset_timestamp
                );
            }
        }

        if (! $is_unlimited) {
            $percentage = min(100.0, max(0.0, $percentage));
        }

        $wrapper_classes = trim($wrapper_class . ' encypher-usage-progress');
        ?>
        <div class="<?php echo esc_attr($wrapper_classes); ?>">
            <h3 class="encypher-usage-progress-title"><?php echo esc_html($title); ?></h3>
            <?php if ($is_unlimited): ?>
                <p class="encypher-usage-progress-summary">
                    <strong><?php esc_html_e('Monthly API calls this month:', 'encypher-provenance'); ?></strong>
                    <?php echo esc_html(number_format_i18n($used)); ?>
                    <span class="description"><?php esc_html_e('Unlimited plan', 'encypher-provenance'); ?></span>
                </p>
            <?php else: ?>
                <p class="encypher-usage-progress-summary">
                    <strong><?php esc_html_e('Monthly API calls this month:', 'encypher-provenance'); ?></strong>
                    <?php echo esc_html(number_format_i18n($used)); ?>
                    / <?php echo esc_html(number_format_i18n($limit)); ?>
                    (<?php echo esc_html(number_format_i18n((int) round($percentage))); ?>%)
                </p>
                <div class="encypher-usage-progress-track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="<?php echo esc_attr((int) round($percentage)); ?>">
                    <div class="encypher-usage-progress-fill" style="width: <?php echo esc_attr($percentage); ?>%;"></div>
                </div>
                <p class="encypher-usage-progress-remaining">
                    <strong><?php esc_html_e('API calls remaining this month:', 'encypher-provenance'); ?></strong>
                    <?php echo esc_html(number_format_i18n(max(0, $remaining))); ?>
                </p>
            <?php endif; ?>
            <?php if ($reset_date): ?>
                <p class="description encypher-usage-progress-reset">
                    <?php
                    printf(
                        /* translators: %s: reset date/time in site's locale */
                        esc_html__('Usage resets on: %s', 'encypher-provenance'),
                        esc_html($human_readable_reset_date)
                    );
                    ?>
                </p>
            <?php endif; ?>
        </div>
        <?php
    }

    public function render_settings_page(): void
    {
        if (! current_user_can('manage_options')) {
            return;
        }

        $settings = get_option('encypher_provenance_settings', []);
        $connection_status = isset($settings['connection_last_status']) ? (string) $settings['connection_last_status'] : 'unknown';
        $last_checked_at = isset($settings['connection_last_checked_at']) ? (string) $settings['connection_last_checked_at'] : '';

        ?>
        <div class="wrap encypher-settings-page">
            <h1 class="encypher-page-title">
                <span class="encypher-logo">
                    <img
                        class="encypher-brand-lockup"
                        src="<?php echo esc_url(ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/images/encypher_full_logo_color.svg'); ?>"
                        alt="<?php echo esc_attr__('Encypher', 'encypher-provenance'); ?>"
                    />
                </span>
                <span class="encypher-title-divider" aria-hidden="true">|</span>
                <span><?php esc_html_e('Settings', 'encypher-provenance'); ?></span>
            </h1>

            <?php settings_errors('encypher_provenance_settings'); ?>

            <div class="encypher-settings-grid">
                <div class="encypher-settings-panel encypher-settings-panel-primary">
                    <div class="encypher-launch-checklist">
                        <h2><?php esc_html_e('Launch Readiness Checklist', 'encypher-provenance'); ?></h2>
                        <ol>
                            <li><?php esc_html_e('Step 1: Start secure email connect or paste an existing API key', 'encypher-provenance'); ?></li>
                            <li><?php esc_html_e('Step 2: Confirm WordPress is connected to your workspace', 'encypher-provenance'); ?></li>
                            <li><?php esc_html_e('Step 3: Publish and verify your first signed post', 'encypher-provenance'); ?></li>
                        </ol>
                    </div>

                    <div class="encypher-connection-health-card">
                        <h2><?php esc_html_e('Connection Health', 'encypher-provenance'); ?></h2>
                        <div id="encypher-connection-health-state" class="encypher-health-state" role="status" aria-live="polite">
                            <?php echo esc_html($connection_status === 'connected' ? __('Connected and ready', 'encypher-provenance') : __('Disconnected', 'encypher-provenance')); ?>
                        </div>
                        <p id="connection-status" role="status" aria-live="polite">
                            <?php echo esc_html($connection_status === 'connected' ? __('Connected', 'encypher-provenance') : __('Not connected', 'encypher-provenance')); ?>
                        </p>
                        <p id="test-connection-result" role="status" aria-live="polite">
                            <?php
                            if ($last_checked_at) {
                                printf(
                                    esc_html__('Last check: %s', 'encypher-provenance'),
                                    esc_html($last_checked_at)
                                );
                            } else {
                                esc_html_e('Last check: not yet run', 'encypher-provenance');
                            }
                            ?>
                        </p>
                    </div>
                </div>
            </div>

            <form method="post" action="options.php">
                <?php settings_fields('encypher_provenance_settings_group'); ?>
                <?php do_settings_sections('encypher-provenance-settings'); ?>
                <?php submit_button(__('Save Settings', 'encypher-provenance')); ?>
            </form>
        </div>
        <style>
            .encypher-settings-grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: 16px; margin: 20px 0; }
            .encypher-settings-panel { display: grid; gap: 16px; }
            .encypher-launch-checklist,
            .encypher-connection-health-card { background: #fff; border: 1px solid #dcdcde; border-radius: 8px; padding: 20px; }
            .encypher-launch-checklist h2,
            .encypher-connection-health-card h2 { margin-top: 0; margin-bottom: 12px; }
            .encypher-launch-checklist ol { margin: 0 0 0 18px; }
            .encypher-launch-checklist li { margin-bottom: 8px; }
            .encypher-health-state { font-weight: 600; color: #1b3a5f; margin-bottom: 8px; }
            #connection-status,
            #test-connection-result { margin: 0 0 6px; }
        </style>
        <?php
    }

    /**
     * Render the main Dashboard page.
     */
    public function render_dashboard_page(): void
    {
        if (! current_user_can('manage_options')) {
            return;
        }

        $settings = get_option('encypher_provenance_settings', []);

        $tier = isset($settings['tier']) ? $settings['tier'] : 'free';
        $org_name = isset($settings['organization_name']) ? $settings['organization_name'] : '';
        $api_key = isset($settings['api_key']) ? $settings['api_key'] : '';
        $usage = $this->get_usage_snapshot($settings, true);
        $is_connected = !empty($api_key);
        $stats = $this->gather_analytics_stats();
        $show_onboarding = get_option('encypher_show_onboarding', true) && !$is_connected;

        ?>
        <div class="wrap encypher-dashboard">
            <div class="encypher-header">
                <h1>
                    <span class="encypher-logo">
                        <img
                            class="encypher-brand-lockup"
                            src="<?php echo esc_url(ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/images/encypher_full_logo_color.svg'); ?>"
                            alt="<?php echo esc_attr__('Encypher', 'encypher-provenance'); ?>"
                        />
                    </span>
                    <span class="encypher-title-divider" aria-hidden="true">|</span>
                    <?php esc_html_e('Dashboard', 'encypher-provenance'); ?>
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
                    <a href="<?php echo esc_url(admin_url('admin.php?page=encypher-bulk-mark')); ?>" class="encypher-action-card">
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

            <div class="encypher-section">
                <h2><?php esc_html_e('API usage', 'encypher-provenance'); ?></h2>
                <?php $this->render_usage_progress_bar($usage, 'encypher-dashboard-usage-progress encypher-usage-progress-compact'); ?>
            </div>

            <div class="encypher-section">
                <h2><?php esc_html_e('Support', 'encypher-provenance'); ?></h2>
                <div class="encypher-support-card">
                    <p><strong><?php esc_html_e('Need help? Contact support', 'encypher-provenance'); ?></strong></p>
                    <p>
                        <a href="mailto:wp-support@encypherai.com">wp-support@encypherai.com</a>
                    </p>
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
            .encypher-brand-lockup { width: 120px; height: auto; display: block; }
            .encypher-org-badge { background: #1B3A5F; color: #fff; padding: 4px 12px; border-radius: 4px; font-size: 13px; }
            .encypher-icon { width: 24px; height: 24px; stroke: currentColor; }
            .encypher-icon-lg { width: 32px; height: 32px; color: #2271b1; }
            .encypher-icon-stat { width: 28px; height: 28px; color: #1B3A5F; }
            .encypher-icon-action { width: 24px; height: 24px; color: #2271b1; }
            .encypher-stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }
            .encypher-stat-card { background: #fff; border: 1px solid #dcdcde; border-radius: 8px; padding: 20px; text-align: center; }
            .encypher-stat-card .stat-icon { display: flex; justify-content: center; margin-bottom: 12px; }
            .encypher-stat-card .stat-value { font-size: 32px; font-weight: 700; color: #1B3A5F; }
            .encypher-stat-card .stat-label { color: #646970; font-size: 13px; margin-top: 4px; }
            .encypher-tier-card.tier-free { border-color: #2271b1; background: linear-gradient(135deg, #f0f6fc 0%, #fff 100%); }
            .encypher-tier-card.tier-free .stat-icon .encypher-icon { color: #2271b1; }
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
            .encypher-usage-progress { background: #fff; border: 1px solid #dcdcde; border-radius: 8px; padding: 16px; }
            .encypher-usage-progress-title { margin: 0 0 8px; font-size: 14px; color: #1b2f50; }
            .encypher-usage-progress-summary { margin: 0 0 10px; }
            .encypher-usage-progress-track { width: 100%; height: 10px; border-radius: 999px; background: #e8edf2; overflow: hidden; }
            .encypher-usage-progress-fill { height: 100%; background: linear-gradient(90deg, #1b2f50 0%, #2a87c4 100%); }
            .encypher-usage-progress-remaining { margin: 10px 0 0; font-size: 13px; color: #334155; }
            .encypher-usage-progress-reset { margin-top: 8px; }
            .encypher-usage-progress-compact { padding: 10px 14px; }
            .encypher-usage-progress-compact .encypher-usage-progress-title { margin-bottom: 6px; }
            .encypher-usage-progress-compact .encypher-usage-progress-summary { margin-bottom: 6px; font-size: 12px; }
            .encypher-usage-progress-compact .encypher-usage-progress-track { height: 7px; margin-top: 6px; }
            .encypher-usage-progress-compact .encypher-usage-progress-remaining { margin-top: 6px; font-size: 12px; }
            .encypher-usage-progress-compact .encypher-usage-progress-reset { margin-top: 6px; font-size: 11px; }
            .encypher-support-card { background:#fff; border:1px solid #dcdcde; border-radius:8px; padding:16px; }
            .encypher-support-card p { margin: 0 0 8px; }
            .encypher-support-card p:last-child { margin-bottom: 0; }
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
     * AJAX handler: clear the site-wide error log.
     */
    public function ajax_clear_error_log(): void
    {
        check_ajax_referer('encypher_clear_error_log');
        if (! current_user_can('manage_options')) {
            wp_send_json_error('Unauthorized', 403);
        }
        ErrorLog::clear();
        wp_send_json_success();
    }

    /**
     * AJAX handler: export the error log as CSV (enterprise only).
     */
    public function ajax_export_error_log(): void
    {
        check_ajax_referer('encypher_export_error_log');
        if (! current_user_can('manage_options')) {
            wp_die('Unauthorized', 403);
        }

        $settings = get_option('encypher_provenance_settings', []);
        $tier = isset($settings['tier']) ? $settings['tier'] : 'free';
        if (! in_array($tier, ['enterprise', 'strategic_partner'], true)) {
            wp_die(__('CSV export requires an Enterprise plan.', 'encypher-provenance'), 403);
        }

        $log = ErrorLog::get_raw_log();
        $filename = 'encypher-error-log-' . gmdate('Y-m-d') . '.csv';

        header('Content-Type: text/csv; charset=utf-8');
        header('Content-Disposition: attachment; filename="' . $filename . '"');
        header('Pragma: no-cache');
        header('Expires: 0');

        $out = fopen('php://output', 'w');
        fputcsv($out, ['timestamp', 'post_id', 'post_title', 'context', 'error_code', 'error_message', 'consecutive_failures']);
        foreach ($log as $entry) {
            fputcsv($out, [
                $entry['timestamp'] ?? '',
                $entry['post_id'] ?? '',
                $entry['post_title'] ?? '',
                $entry['context'] ?? '',
                $entry['error_code'] ?? '',
                $entry['error_message'] ?? '',
                $entry['consecutive_failures'] ?? '',
            ]);
        }
        fclose($out);
        exit;
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
            'free' => [
                'next_tier' => 'Enterprise',
                'price' => 'Custom',
                'features' => [
                    __('Bring Your Own Keys (BYOK)', 'encypher-provenance'),
                    __('Word-level segmentation', 'encypher-provenance'),
                    __('Dual binding & fingerprinting', 'encypher-provenance'),
                    __('Archive backfill included', 'encypher-provenance'),
                    __('SSO/SCIM integration', 'encypher-provenance'),
                    __('Dedicated support & SLA', 'encypher-provenance'),
                ],
                'cta_url' => 'https://encypherai.com/enterprise',
            ],
        ];

        $upgrade = $upgrades[$current_tier] ?? $upgrades['free'];
        ?>
        <div class="encypher-section encypher-upsell">
            <h2><?php esc_html_e('Unlock More Features', 'encypher-provenance'); ?></h2>
            <div class="upsell-card">
                <div class="upsell-header">
                    <span class="upsell-badge"><?php echo esc_html($upgrade['next_tier']); ?></span>
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
            .encypher-upsell .upsell-badge { background: #2271b1; color: #fff; padding: 6px 16px; border-radius: 4px; font-weight: 600; }
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

        $settings = get_option('encypher_provenance_settings', []);
        $tier = isset($settings['tier']) ? $settings['tier'] : 'free';

        $usage = $this->get_usage_snapshot($settings, true);

        global $wpdb;

        $paged = isset($_GET['paged']) ? max(1, (int) $_GET['paged']) : 1;
        $per_page = 50;
        $configured_post_types = isset($settings['post_types']) && is_array($settings['post_types'])
            ? $settings['post_types']
            : ['post', 'page'];

        // Get posts with their signing status
        $posts = get_posts([
            'post_type' => $configured_post_types,
            'post_status' => 'publish',
            'posts_per_page' => $per_page,
            'paged' => $paged,
            'orderby' => 'date',
            'order' => 'DESC',
        ]);

        $total_posts = (int) (new \WP_Query([
            'post_type' => $configured_post_types,
            'post_status' => 'publish',
            'posts_per_page' => -1,
            'fields' => 'ids',
        ]))->found_posts;
        $total_pages = (int) ceil($total_posts / $per_page);

        ?>
        <div class="wrap encypher-content-page">
            <h1 class="encypher-page-title">
                <span class="encypher-logo">
                    <img
                        class="encypher-brand-lockup"
                        src="<?php echo esc_url(ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/images/encypher_full_logo_color.svg'); ?>"
                        alt="<?php echo esc_attr__('Encypher', 'encypher-provenance'); ?>"
                    />
                </span>
                <span class="encypher-title-divider" aria-hidden="true">|</span>
                <span><?php esc_html_e('Content', 'encypher-provenance'); ?></span>
            </h1>
            <p class="description"><?php esc_html_e('View and manage the signing status of your content.', 'encypher-provenance'); ?></p>
            <?php if ('free' === $tier): ?>
                <div class="notice notice-info inline">
                    <p>
                        <?php esc_html_e('Free plan includes up to 1,000 sign requests/month for publishing workflows.', 'encypher-provenance'); ?>
                        <?php esc_html_e('$0.02/sign request applies after the monthly cap.', 'encypher-provenance'); ?>
                        <?php esc_html_e('Verification requests remain available with a soft cap of 10,000/month.', 'encypher-provenance'); ?>
                        <?php esc_html_e('Need more than 1,000 sign requests/month?', 'encypher-provenance'); ?>
                        <a href="https://dashboard.encypherai.com/billing" target="_blank" rel="noopener noreferrer"><?php esc_html_e('View billing options', 'encypher-provenance'); ?></a>
                    </p>
                </div>
            <?php endif; ?>

            <?php $this->render_usage_progress_bar($usage, 'encypher-content-usage-progress'); ?>

            <div class="tablenav top">
                <div class="alignleft actions">
                    <a href="<?php echo esc_url(admin_url('admin.php?page=encypher-bulk-mark')); ?>" class="button button-primary">
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
                            $last_signed = get_post_meta($post->ID, '_encypher_provenance_last_signed', true);
                            $status = get_post_meta($post->ID, '_encypher_provenance_status', true);
                            $document_id = get_post_meta($post->ID, '_encypher_provenance_document_id', true);
                            $verification_url = get_post_meta($post->ID, '_encypher_provenance_verification_url', true);

                            $status_label = __('Signed', 'encypher-provenance');
                            $status_class = 'status-signed';
                            $status_guidance = __('Provenance embedded. Run Verify to confirm integrity.', 'encypher-provenance');

                            if (! $is_marked) {
                                $status_label = __('Unsigned (needs signing)', 'encypher-provenance');
                                $status_class = 'status-unsigned';
                                $status_guidance = __('Use Bulk Sign or publish/update this post to sign it.', 'encypher-provenance');
                            } elseif ('c2pa_verified' === $status) {
                                $status_label = __('Signed', 'encypher-provenance');
                                $status_class = 'status-signed';
                                $status_guidance = __('Verified provenance is available.', 'encypher-provenance');
                            } elseif ('modified' === $status) {
                                $status_label = __('Modified since signing', 'encypher-provenance');
                                $status_class = 'status-modified';
                                $status_guidance = __('Re-sign by updating this post.', 'encypher-provenance');
                            } elseif ('verification_failed' === $status) {
                                $status_label = __('Verification failed', 'encypher-provenance');
                                $status_class = 'status-verify-failed';
                                $status_guidance = __('Run Verify to refresh status.', 'encypher-provenance');
                            }
                        ?>
                            <tr>
                                <td class="column-title">
                                    <strong><a href="<?php echo esc_url(get_edit_post_link($post->ID)); ?>"><?php echo esc_html(get_the_title($post)); ?></a></strong>
                                </td>
                                <td class="column-type"><?php echo esc_html(get_post_type_object($post->post_type)->labels->singular_name); ?></td>
                                <td class="column-status">
                                    <span class="encypher-status-badge <?php echo esc_attr($status_class); ?>"><?php echo esc_html($status_label); ?></span>
                                    <p class="encypher-status-guidance"><?php echo esc_html($status_guidance); ?></p>
                                </td>
                                <td class="column-signed">
                                    <?php echo $last_signed ? esc_html($last_signed) : '—'; ?>
                                </td>
                                <td class="column-actions">
                                    <?php if ($verification_url): ?>
                                        <a href="<?php echo esc_url($verification_url); ?>" target="_blank" rel="noopener noreferrer" class="button button-small">
                                            <?php esc_html_e('Verify', 'encypher-provenance'); ?>
                                        </a>
                                    <?php else: ?>
                                        <span class="encypher-no-verify-link"><?php esc_html_e('No verification link yet. Sign this post first.', 'encypher-provenance'); ?></span>
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

            <?php if ($total_pages > 1): ?>
                <div class="tablenav bottom">
                    <div class="tablenav-pages">
                        <span class="displaying-num">
                            <?php echo esc_html(sprintf(
                                /* translators: %d: total number of posts */
                                _n('%d item', '%d items', $total_posts, 'encypher-provenance'),
                                $total_posts
                            )); ?>
                        </span>
                        <span class="pagination-links">
                            <?php if ($paged > 1): ?>
                                <a class="prev-page button" href="<?php echo esc_url(add_query_arg('paged', $paged - 1)); ?>">&laquo;</a>
                            <?php endif; ?>
                            <span class="paging-input">
                                <?php echo esc_html($paged); ?> / <?php echo esc_html($total_pages); ?>
                            </span>
                            <?php if ($paged < $total_pages): ?>
                                <a class="next-page button" href="<?php echo esc_url(add_query_arg('paged', $paged + 1)); ?>">&raquo;</a>
                            <?php endif; ?>
                        </span>
                    </div>
                </div>
            <?php endif; ?>

        </div>
        <style>
            .encypher-content-page .encypher-page-title { display:flex; align-items:center; gap:10px; margin:0 0 12px; }
            .encypher-content-page .encypher-logo { display:inline-flex; align-items:center; }
            .encypher-content-page .encypher-brand-lockup { width:120px; height:auto; display:block; }
            .encypher-content-page .encypher-title-divider { color:#8c8f94; font-weight:400; }
            .encypher-content-page .encypher-status-badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
            .encypher-content-page .status-signed { background: #d1e7dd; color: #0a3622; }
            .encypher-content-page .status-unsigned { background: #f8d7da; color: #58151c; }
            .encypher-content-page .status-modified { background: #fff3cd; color: #664d03; }
            .encypher-content-page .status-verify-failed { background: #f8d7da; color: #842029; }
            .encypher-content-page .encypher-status-guidance { margin: 6px 0 0; font-size: 12px; color: #50575e; }
            .encypher-content-page .encypher-no-verify-link { display: inline-block; margin-right: 8px; font-size: 12px; color: #646970; }
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

        $settings = get_option('encypher_provenance_settings', []);
        $tier = isset($settings['tier']) ? $settings['tier'] : 'free';
        $org_id = isset($settings['organization_id']) ? $settings['organization_id'] : '';
        $org_name = isset($settings['organization_name']) ? $settings['organization_name'] : '';
        $api_key = isset($settings['api_key']) ? $settings['api_key'] : '';
        $usage = $this->get_usage_snapshot($settings, true);
        $is_connected = !empty($api_key);

        $tier_info = [
            'free' => ['name' => 'Free', 'price' => 'Free', 'color' => '#2271b1'],
            'enterprise' => ['name' => 'Enterprise', 'price' => 'Custom', 'color' => '#dba617'],
            'strategic_partner' => ['name' => 'Strategic Partner', 'price' => 'Custom', 'color' => '#dba617'],
        ];
        $current_tier_info = $tier_info[$tier] ?? $tier_info['free'];

        ?>
        <div class="wrap encypher-account-page">
            <h1 class="encypher-page-title">
                <span class="encypher-logo">
                    <img
                        class="encypher-brand-lockup"
                        src="<?php echo esc_url(ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/images/encypher_full_logo_color.svg'); ?>"
                        alt="<?php echo esc_attr__('Encypher', 'encypher-provenance'); ?>"
                    />
                </span>
                <span class="encypher-title-divider" aria-hidden="true">|</span>
                <span><?php esc_html_e('Account', 'encypher-provenance'); ?></span>
            </h1>

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
                    <?php if ('free' === $tier): ?>
                        <p class="description"><?php esc_html_e('Need more than 1,000 sign requests/month? $0.02/sign request overage and Enterprise plans are available from billing.', 'encypher-provenance'); ?></p>
                    <?php endif; ?>
                    <?php $this->render_usage_progress_bar($usage, 'encypher-account-usage-progress'); ?>
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
        ];

        if (!in_array($hook_suffix, $encypher_pages, true)) {
            return;
        }

        wp_enqueue_style(
            'encypher-provenance-settings',
            ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/css/settings-page.css',
            [],
            ENCYPHER_PROVENANCE_VERSION
        );

        wp_enqueue_script(
            'encypher-provenance-settings',
            ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/js/settings-page.js',
            ['jquery'],
            ENCYPHER_PROVENANCE_VERSION,
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

        $options = get_option('encypher_provenance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'free';
        wp_localize_script(
            'encypher-provenance-settings',
            'EncypherSettingsData',
            [
                'tier' => $tier,
                'connectEmail' => isset($options['connect_email']) ? (string) $options['connect_email'] : '',
                'connectSessionId' => isset($options['connect_session_id']) ? (string) $options['connect_session_id'] : '',
                'signingMode' => isset($options['signing_mode']) ? $options['signing_mode'] : 'managed',
                'byokEnabled' => isset($options['signing_mode']) && 'byok' === $options['signing_mode'],
                'dashboardUrls' => [
                    'billing' => 'https://dashboard.encypherai.com/billing',
                    'apiKey' => 'https://dashboard.encypherai.com/register',
                    'byok' => 'https://dashboard.encypherai.com/signing-profiles',
                ],
                'strings' => [
                    'byokDisabled' => __('BYOK is only available on the Enterprise tier.', 'encypher-provenance'),
                    'tierDowngraded' => __('Your workspace tier no longer supports custom signing profiles. We reset BYOK to Encypher-managed certificates.', 'encypher-provenance'),
                    'connectStarted' => __('Check your email for the secure approval link. This page will keep watching for completion.', 'encypher-provenance'),
                    'connectCompleted' => __('WordPress connected successfully. Your API key has been provisioned automatically.', 'encypher-provenance'),
                ],
            ]
        );
    }

    public function render_api_base_url_field(): void
    {
        $options = get_option('encypher_provenance_settings', []);
        $value = isset($options['api_base_url']) && '' !== $options['api_base_url'] ? esc_url($options['api_base_url']) : 'https://api.encypherai.com';
        ?>
        <input type="url" id="api_base_url" class="regular-text" name="encypher_provenance_settings[api_base_url]" value="<?php echo esc_attr($value); ?>" placeholder="https://api.encypherai.com/api/v1" required />
        <p class="description">
            <?php esc_html_e('Most publishers can leave this on the default hosted Encypher API. Change it only if your organization runs a self-hosted endpoint.', 'encypher-provenance'); ?>
        </p>
        <div id="connection-status" role="status" aria-live="polite"></div>
        <button type="button" id="test-connection-btn" class="button"><?php esc_html_e('Test Connection', 'encypher-provenance'); ?></button>
        <div id="test-connection-result" role="status" aria-live="polite"></div>
        <?php
    }

    public function render_api_key_field(): void
    {
        $options = get_option('encypher_provenance_settings', []);
        $value = isset($options['api_key']) ? $options['api_key'] : '';
        ?>
        <input type="password" id="api_key" class="regular-text" name="encypher_provenance_settings[api_key]" value="<?php echo esc_attr($value); ?>" autocomplete="off" />
        <p class="description">
            <?php esc_html_e('Optional if you use email connect. Paste an existing Encypher API key only when your team manages credentials outside the guided setup flow.', 'encypher-provenance'); ?>
            <br>
            <a class="button button-secondary" href="https://dashboard.encypherai.com/register" target="_blank" rel="noopener noreferrer">
                <?php esc_html_e('Open Dashboard', 'encypher-provenance'); ?>
            </a>
            <a class="button button-link" style="margin-left:8px;" href="https://dashboard.encypherai.com/billing" target="_blank" rel="noopener noreferrer">
                <?php esc_html_e('Manage Workspace & Billing', 'encypher-provenance'); ?>
            </a>
        </p>
        <?php
    }

    public function render_magic_link_connect_field(): void
    {
        $options = get_option('encypher_provenance_settings', []);
        $email = isset($options['connect_email']) ? (string) $options['connect_email'] : '';
        $session_id = isset($options['connect_session_id']) ? (string) $options['connect_session_id'] : '';
        ?>
        <div class="encypher-magic-link-connect">
            <input type="email" id="encypher-connect-email" class="regular-text" value="<?php echo esc_attr($email); ?>" placeholder="you@example.com" autocomplete="email" />
            <button type="button" id="encypher-connect-start-btn" class="button button-secondary"><?php esc_html_e('Email me a secure connect link', 'encypher-provenance'); ?></button>
            <button type="button" id="encypher-connect-poll-btn" class="button" <?php echo '' === $session_id ? 'disabled' : ''; ?>><?php esc_html_e('Check connect status', 'encypher-provenance'); ?></button>
            <input type="hidden" name="encypher_provenance_settings[connect_email]" value="<?php echo esc_attr($email); ?>" />
            <input type="hidden" name="encypher_provenance_settings[connect_session_id]" value="<?php echo esc_attr($session_id); ?>" />
            <p class="description"><?php esc_html_e('Recommended for first-time setup. Enter your work email, approve the site from the secure link we send you, and the plugin will provision its API key automatically.', 'encypher-provenance'); ?></p>
            <div id="encypher-connect-status" role="status" aria-live="polite"></div>
        </div>
        <?php
    }

    public function render_auto_verify_field(): void
    {
        $options = get_option('encypher_provenance_settings', []);
        $checked = ! empty($options['auto_verify']);
        ?>
        <label>
            <input type="checkbox" name="encypher_provenance_settings[auto_verify]" value="1" <?php checked($checked); ?> />
            <?php esc_html_e('Verify signed content when rendering posts/pages.', 'encypher-provenance'); ?>
        </label>
        <?php
    }

    public function render_signing_mode_field(): void
    {
        $options = get_option('encypher_provenance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'free';
        $value = isset($options['signing_mode']) ? $options['signing_mode'] : 'managed';

        if ('free' === $tier) {
            ?>
            <p class="description">
                <?php esc_html_e('Free workspaces use Encypher-managed certificates. Upgrade to Enterprise for Bring Your Own Key support.', 'encypher-provenance'); ?>
            </p>
            <input type="hidden" name="encypher_provenance_settings[signing_mode]" value="managed" />
            <?php
            return;
        }
        ?>
        <select id="encypher-signing-mode" name="encypher_provenance_settings[signing_mode]">
            <option value="managed" <?php selected('managed', $value); ?>>
                <?php esc_html_e('Managed certificate (recommended)', 'encypher-provenance'); ?>
            </option>
            <option value="byok" <?php selected('byok', $value); ?>>
                <?php esc_html_e('Bring Your Own Key (BYOK)', 'encypher-provenance'); ?>
            </option>
        </select>
        <p class="description">
            <?php esc_html_e('BYOK lets you sign posts with your own Ed25519 key pair or HSM-backed keys (Enterprise) registered in the Encypher dashboard.', 'encypher-provenance'); ?>
            <br><strong><?php esc_html_e('What is BYOK?', 'encypher-provenance'); ?></strong>
            <?php esc_html_e('Bring Your Own Key means signatures are created using your organization-managed keys instead of Encypher-managed certificates.', 'encypher-provenance'); ?>
        </p>
        <?php
    }

    public function render_signing_profile_id_field(): void
    {
        $options = get_option('encypher_provenance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'free';
        $mode = isset($options['signing_mode']) ? $options['signing_mode'] : 'managed';
        $value = isset($options['signing_profile_id']) ? $options['signing_profile_id'] : '';

        if ('free' === $tier) {
            ?>
            <p class="description">
                <?php esc_html_e('Upgrade to Enterprise to configure custom signing profiles from your Encypher dashboard.', 'encypher-provenance'); ?>
            </p>
            <input type="hidden" name="encypher_provenance_settings[signing_profile_id]" value="" />
            <?php
            return;
        }

        $readonly = ('byok' !== $mode);
        ?>
        <input
            id="encypher-signing-profile-id"
            type="text"
            class="regular-text"
            name="encypher_provenance_settings[signing_profile_id]"
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
        $asset_path = ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/js/editor-sidebar.js';
        wp_enqueue_script(
            'encypher-provenance-editor-sidebar',
            $asset_path,
            ['wp-plugins', 'wp-edit-post', 'wp-editor', 'wp-components', 'wp-element', 'wp-data', 'wp-api-fetch'],
            ENCYPHER_PROVENANCE_VERSION,
            true
        );

        $settings = get_option('encypher_provenance_settings', []);
        $tier = isset($settings['tier']) ? $settings['tier'] : 'free';
        $usage = $this->get_usage_snapshot($settings, true);
        wp_localize_script(
            'encypher-provenance-editor-sidebar',
            'EncypherProvenanceConfig',
            [
                'restUrl' => esc_url_raw(rest_url('encypher-provenance/v1/')),
                'nonce' => wp_create_nonce('wp_rest'),
                'autoVerify' => ! empty($settings['auto_verify']),
                'tier' => $tier,
                'usage' => $usage,
                'signingMode' => isset($settings['signing_mode']) ? $settings['signing_mode'] : 'managed',
                'byokEnabled' => isset($settings['signing_mode']) && 'byok' === $settings['signing_mode'],
                'upgradeUrl' => 'https://dashboard.encypherai.com/billing',
                'manageAccountUrl' => 'https://dashboard.encypherai.com/settings',
                'wordpress_ai_enabled' => !empty($settings['wordpress_ai_enabled']) ? true : false,
                'settings_url' => admin_url('admin.php?page=encypher-settings'),
            ]
        );

        wp_enqueue_style(
            'encypher-provenance-editor-css',
            ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/css/editor.css',
            [],
            ENCYPHER_PROVENANCE_VERSION
        );

        // WordPress/ai provenance panel
        wp_enqueue_script(
            'encypher-wordpress-ai-provenance',
            ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/js/wordpress-ai-provenance.js',
            ['wp-plugins', 'wp-edit-post', 'wp-element', 'wp-components', 'wp-data', 'wp-api-fetch'],
            ENCYPHER_PROVENANCE_VERSION,
            true
        );
        wp_enqueue_style(
            'encypher-wordpress-ai-provenance',
            ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/css/wordpress-ai-provenance.css',
            [],
            ENCYPHER_PROVENANCE_VERSION
        );
    }

    public function enqueue_classic_assets(string $hook_suffix): void
    {
        if (! in_array($hook_suffix, ['post.php', 'post-new.php'], true)) {
            return;
        }

        wp_enqueue_script(
            'encypher-provenance-classic',
            ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/js/classic-meta-box.js',
            ['jquery'],
            ENCYPHER_PROVENANCE_VERSION,
            true
        );

        wp_localize_script(
            'encypher-provenance-classic',
            'EncypherProvenanceClassic',
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
        wp_nonce_field('encypher_provenance_meta_box', 'encypher_provenance_meta_box_nonce');
        $status = get_post_meta($post->ID, '_encypher_provenance_status', true);
        $document_id = get_post_meta($post->ID, '_encypher_provenance_document_id', true);
        $verification_url = get_post_meta($post->ID, '_encypher_provenance_verification_url', true);
        $total_sentences = (int) get_post_meta($post->ID, '_encypher_provenance_total_sentences', true);
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
        $settings = get_option('encypher_provenance_settings', []);
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
        $settings = get_option('encypher_provenance_settings', []);
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
        $options = get_option('encypher_provenance_settings', []);
        $checked = isset($options['auto_mark_on_publish']) ? (bool) $options['auto_mark_on_publish'] : true;
        ?>
        <label>
            <input type="checkbox" name="encypher_provenance_settings[auto_mark_on_publish]" value="1" <?php checked($checked); ?> />
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
        $options = get_option('encypher_provenance_settings', []);
        $checked = isset($options['auto_mark_on_update']) ? (bool) $options['auto_mark_on_update'] : true;
        ?>
        <label>
            <input type="checkbox" name="encypher_provenance_settings[auto_mark_on_update]" value="1" <?php checked($checked); ?> />
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
        $options = get_option('encypher_provenance_settings', []);
        $value = isset($options['metadata_format']) ? $options['metadata_format'] : 'c2pa';
        ?>
        <select name="encypher_provenance_settings[metadata_format]">
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
     * Render post types field.
     */
    public function render_post_types_field(): void
    {
        $options = get_option('encypher_provenance_settings', []);
        $selected_types = isset($options['post_types']) ? (array) $options['post_types'] : ['post', 'page'];
        $post_types = get_post_types(['public' => true], 'objects');
        ?>
        <fieldset>
            <?php foreach ($post_types as $post_type): ?>
                <label style="display:block; margin-bottom:5px;">
                    <input type="checkbox"
                           name="encypher_provenance_settings[post_types][]"
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
        $options = get_option('encypher_provenance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'free';
        $usage = $this->get_usage_snapshot($options, true);

        $tier_names = [
            'free' => __('Free', 'encypher-provenance'),
            'enterprise' => __('Enterprise', 'encypher-provenance'),
            'strategic_partner' => __('Strategic Partner', 'encypher-provenance'),
        ];

        $tier_features = [
            'free' => [
                __('Auto-sign on publish & update', 'encypher-provenance'),
                __('Sentence-level C2PA signing (micro + ECC + embedded C2PA)', 'encypher-provenance'),
                __('Attribution indexing', 'encypher-provenance'),
                __('1,000 sign requests/month included', 'encypher-provenance'),
                __('Archive backfill available at $0.01/document', 'encypher-provenance'),
                __('Encypher-managed certificates', 'encypher-provenance'),
            ],
            'enterprise' => [
                __('All Free features', 'encypher-provenance'),
                __('Bring Your Own Key (BYOK)', 'encypher-provenance'),
                __('Word-level segmentation', 'encypher-provenance'),
                __('Dual binding & fingerprinting', 'encypher-provenance'),
                __('Archive backfill included', 'encypher-provenance'),
                __('SSO/SCIM integration', 'encypher-provenance'),
                __('Dedicated support & SLA', 'encypher-provenance'),
            ],
            'strategic_partner' => [
                __('All Enterprise features', 'encypher-provenance'),
                __('Custom integration support', 'encypher-provenance'),
            ],
        ];
        ?>
        <div class="encypher-tier-display">
            <p style="font-size:18px; font-weight:bold; color:#1B2F50;">
                <?php echo esc_html(isset($tier_names[$tier]) ? $tier_names[$tier] : $tier_names['free']); ?>
            </p>

            <div style="background:#f0f6fc; padding:15px; border-left:4px solid #2A87C4; margin:10px 0;">
                <strong><?php esc_html_e('Features:', 'encypher-provenance'); ?></strong>
                <ul style="margin:10px 0;">
                    <?php foreach ((isset($tier_features[$tier]) ? $tier_features[$tier] : $tier_features['free']) as $feature): ?>
                        <li><?php echo esc_html($feature); ?></li>
                    <?php endforeach; ?>
                </ul>
            </div>

            <?php if ('free' === $tier): ?>
                <p class="description" style="margin-top: 8px; color: #555d66;">
                    <?php esc_html_e('1,000 sign requests/month included; $0.02/sign request after the monthly cap.', 'encypher-provenance'); ?>
                    <?php esc_html_e('Verification requests remain available with a soft cap of 10,000/month.', 'encypher-provenance'); ?>
                </p>
                <p>
                    <a href="https://encypherai.com/enterprise" class="button button-primary" target="_blank">
                        <?php esc_html_e('Upgrade to Enterprise', 'encypher-provenance'); ?>
                    </a>
                </p>
            <?php endif; ?>

            <?php $this->render_usage_progress_bar($usage, 'encypher-settings-usage-progress'); ?>

            <input type="hidden" name="encypher_provenance_settings[tier]" value="<?php echo esc_attr($tier); ?>" />
        </div>
        <?php
    }

    public function render_show_badge_field(): void
    {
        $options = get_option('encypher_provenance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'free';
        $checked = isset($options['show_badge']) ? (bool) $options['show_badge'] : true; // Default ON

        if ('free' === $tier) {
            ?>
            <label>
                <input type="checkbox" name="encypher_provenance_settings[show_badge]" value="1" checked disabled />
                <?php esc_html_e('Display C2PA badge on marked posts', 'encypher-provenance'); ?>
            </label>
            <input type="hidden" name="encypher_provenance_settings[show_badge]" value="1" />
            <p class="description">
                <?php esc_html_e('Shows a badge indicating the post is C2PA protected. Helps readers verify authenticity.', 'encypher-provenance'); ?>
            </p>
            <p class="description" style="color: #666; font-style: italic;">
                <?php esc_html_e('Free tier requires the C2PA badge to be displayed.', 'encypher-provenance'); ?>
                <a href="https://encypherai.com/enterprise" target="_blank"><?php esc_html_e('Upgrade to Enterprise', 'encypher-provenance'); ?></a>
                <?php esc_html_e('to customize badge visibility.', 'encypher-provenance'); ?>
            </p>
            <?php
        } else {
            ?>
            <label>
                <input type="checkbox" name="encypher_provenance_settings[show_badge]" value="1" <?php checked($checked); ?> />
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
        $options = get_option('encypher_provenance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'free';
        $value = isset($options['badge_position']) ? $options['badge_position'] : 'bottom';
        ?>
        <select name="encypher_provenance_settings[badge_position]">
            <option value="bottom" <?php selected($value, 'bottom'); ?>><?php esc_html_e('Bottom of post (above comments)', 'encypher-provenance'); ?></option>
            <option value="top" <?php selected($value, 'top'); ?>><?php esc_html_e('Top of post', 'encypher-provenance'); ?></option>
            <option value="bottom-right" <?php selected($value, 'bottom-right'); ?>><?php esc_html_e('Bottom-right corner (floating)', 'encypher-provenance'); ?></option>
        </select>
        <p class="description"><?php esc_html_e('Choose where the C2PA badge appears on posts.', 'encypher-provenance'); ?></p>
        <?php
    }

    /**
     * Render show branding field.
     */
    public function render_show_branding_field(): void
    {
        $options = get_option('encypher_provenance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'free';
        $checked = isset($options['show_branding']) ? (bool) $options['show_branding'] : true; // Default ON

        if ('free' === $tier) {
            ?>
            <label>
                <input type="checkbox" name="encypher_provenance_settings[show_branding]" value="1" checked disabled />
                <?php esc_html_e('Display Encypher branding', 'encypher-provenance'); ?>
            </label>
            <input type="hidden" name="encypher_provenance_settings[show_branding]" value="1" />
            <p class="description">
                <?php esc_html_e('Free tier includes "Powered by Encypher" branding on verification badges.', 'encypher-provenance'); ?>
                <a href="https://encypherai.com/enterprise" target="_blank"><?php esc_html_e('Upgrade to Enterprise to remove branding.', 'encypher-provenance'); ?></a>
                <br><?php esc_html_e('Whitelabel is also available as a paid add-on for Free plans. Contact Encypher support or sales for current pricing.', 'encypher-provenance'); ?>
            </p>
            <?php
        } else {
            ?>
            <label>
                <input type="checkbox" name="encypher_provenance_settings[show_branding]" value="1" <?php checked($checked); ?> />
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
        $options = get_option('encypher_provenance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'free';
        $enabled = isset($options['coalition_enabled']) ? (bool) $options['coalition_enabled'] : true;

        // Free tier: always enabled, cannot be disabled
        if ('free' === $tier) {
            ?>
            <div style="background:#e7f5fe; padding:15px; border-left:4px solid #2271b1; margin:10px 0;">
                <p style="margin:0 0 10px 0;">
                    <strong style="color:#2271b1;"><span class="dashicons dashicons-yes-alt" style="vertical-align: middle;"></span> <?php esc_html_e('Active Coalition Member', 'encypher-provenance'); ?></strong>
                </p>
                <p style="margin:0; font-size:13px;">
                    <?php esc_html_e('Coalition membership is required for free tier users. Your content is pooled with other members for bulk licensing to AI companies.', 'encypher-provenance'); ?>
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
            <input type="hidden" name="encypher_provenance_settings[coalition_enabled]" value="1" />
            <?php
        } else {
            // Enterprise: optional but recommended
            ?>
            <label>
                <input type="checkbox" name="encypher_provenance_settings[coalition_enabled]" value="1" <?php checked($enabled, true); ?> />
                <?php esc_html_e('Participate in Encypher Coalition', 'encypher-provenance'); ?>
            </label>
            <div style="background:#f0f6fc; padding:15px; border-left:4px solid #2271b1; margin:10px 0;">
                <p style="margin:0; font-size:13px;">
                    <?php esc_html_e('Coalition membership allows you to earn revenue from AI company licensing deals. Your content is pooled with other members for bulk licensing.', 'encypher-provenance'); ?>
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

    /**
     * Render coalition auto-enroll field.
     */
    public function render_coalition_auto_enroll_field(): void
    {
        $options  = get_option('encypher_provenance_settings', []);
        $enrolled = (bool) get_option('encypher_coalition_enrolled', false);
        $checked  = isset($options['coalition_auto_enroll']) ? (bool) $options['coalition_auto_enroll'] : false;
        $enrolled_at = get_option('encypher_coalition_enrolled_at', '');
        ?>
        <label>
            <input type="checkbox" name="encypher_provenance_settings[coalition_auto_enroll]" value="1" <?php checked($checked, true); ?> />
            <?php esc_html_e('Automatically enroll this site in the Encypher Coalition', 'encypher-provenance'); ?>
        </label>
        <?php if ($enrolled): ?>
        <div style="margin-top:8px; padding:8px 12px; background:#edfaef; border-left:4px solid #00a32a;">
            <span class="dashicons dashicons-yes-alt" style="color:#00a32a; vertical-align:middle;"></span>
            <strong style="color:#00a32a;"><?php esc_html_e('Enrolled', 'encypher-provenance'); ?></strong>
            <?php if ($enrolled_at): ?>
                &mdash; <?php echo esc_html(sprintf(
                    /* translators: %s: enrollment date */
                    __('since %s', 'encypher-provenance'),
                    date_i18n(get_option('date_format'), strtotime($enrolled_at))
                )); ?>
            <?php endif; ?>
        </div>
        <?php else: ?>
        <p class="description"><?php esc_html_e('Enable to automatically enroll this site in the Encypher Coalition when settings are saved. Coalition members pool content for AI company licensing deals.', 'encypher-provenance'); ?></p>
        <?php endif; ?>
        <?php
    }

    /**
     * Render WordPress/ai integration enabled field.
     */
    public function render_wordpress_ai_enabled_field(): void
    {
        $options = get_option('encypher_provenance_settings', []);
        $enabled = isset($options['wordpress_ai_enabled']) ? (bool) $options['wordpress_ai_enabled'] : false;
        $wpai_active = class_exists('WP_AI\\Plugin') || class_exists('WordPressAI\\Plugin') || class_exists('WP_AI_Experiments\\Plugin')
            || function_exists('wp_register_ability') || function_exists('wp_do_ability');
        ?>
        <label>
            <input type="checkbox" name="encypher_provenance_settings[wordpress_ai_enabled]" value="1" <?php checked($enabled, true); ?> />
            <?php esc_html_e('Sign AI-generated content with Encypher C2PA provenance', 'encypher-provenance'); ?>
        </label>
        <?php if (!$wpai_active): ?>
        <p class="description" style="color:#856404;">
            <span class="dashicons dashicons-warning" style="vertical-align:middle;"></span>
            <?php esc_html_e('The WordPress/ai plugin does not appear to be active. This setting will have no effect until WordPress/ai is installed and activated.', 'encypher-provenance'); ?>
        </p>
        <?php else: ?>
        <p class="description">
            <?php esc_html_e('When enabled, content generated by WordPress/ai experiments (titles, excerpts, summaries, alt text, etc.) will be automatically signed via the Encypher API before being returned to the editor.', 'encypher-provenance'); ?>
        </p>
        <?php endif; ?>
        <?php
    }

    /**
     * Render failure webhook URL field.
     */
    public function render_error_webhook_url_field(): void
    {
        $options = get_option('encypher_provenance_settings', []);
        $tier    = isset($options['tier']) ? $options['tier'] : 'free';
        $value   = isset($options['error_webhook_url']) ? esc_url($options['error_webhook_url']) : '';
        $is_enterprise = in_array($tier, ['enterprise', 'strategic_partner'], true);
        ?>
        <input type="url"
            id="error_webhook_url"
            class="regular-text"
            name="encypher_provenance_settings[error_webhook_url]"
            value="<?php echo esc_attr($value); ?>"
            placeholder="https://hooks.example.com/encypher-alerts"
            <?php echo $is_enterprise ? '' : 'disabled'; ?> />
        <?php if (! $is_enterprise): ?>
            <p class="description">
                <?php echo wp_kses(
                    sprintf(
                        /* translators: %s: pricing link */
                        __('<a href="%s" target="_blank" rel="noopener noreferrer">Upgrade to Enterprise</a> to enable failure webhooks.', 'encypher-provenance'),
                        'https://encypherai.com/pricing'
                    ),
                    ['a' => ['href' => [], 'target' => [], 'rel' => []]]
                ); ?>
            </p>
        <?php else: ?>
            <p class="description"><?php esc_html_e('Receives a POST request with JSON payload when signing fails repeatedly. Leave blank to disable.', 'encypher-provenance'); ?></p>
        <?php endif; ?>
        <?php
    }

    /**
     * Render failure webhook threshold field.
     */
    public function render_error_webhook_threshold_field(): void
    {
        $options   = get_option('encypher_provenance_settings', []);
        $tier      = isset($options['tier']) ? $options['tier'] : 'free';
        $threshold = isset($options['error_webhook_threshold']) ? (int) $options['error_webhook_threshold'] : 3;
        $is_enterprise = in_array($tier, ['enterprise', 'strategic_partner'], true);
        ?>
        <input type="number"
            id="error_webhook_threshold"
            name="encypher_provenance_settings[error_webhook_threshold]"
            value="<?php echo esc_attr($threshold); ?>"
            min="1" max="100" step="1"
            style="width:80px;"
            <?php echo $is_enterprise ? '' : 'disabled'; ?> />
        <p class="description"><?php esc_html_e('Fire the webhook after this many consecutive failures for the same post. Default: 3.', 'encypher-provenance'); ?></p>
        <?php
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
                <a href="<?php echo esc_url(admin_url('admin.php?page=encypher-analytics')); ?>" class="button button-small">
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
        $settings = get_option('encypher_provenance_settings', []);
        $tier = isset($settings['tier']) ? $settings['tier'] : 'free';
        $advanced_analytics = !empty($settings['features']['advanced_analytics']) || in_array($tier, ['enterprise', 'strategic_partner'], true);
        ?>
        <div class="wrap encypher-analytics-page">
            <h1 class="encypher-page-title">
                <span class="encypher-logo">
                    <img
                        class="encypher-brand-lockup"
                        src="<?php echo esc_url(ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/images/encypher_full_logo_color.svg'); ?>"
                        alt="<?php echo esc_attr__('Encypher', 'encypher-provenance'); ?>"
                    />
                </span>
                <span class="encypher-title-divider" aria-hidden="true">|</span>
                <span><?php esc_html_e('Analytics', 'encypher-provenance'); ?></span>
            </h1>
            <p class="description">
                <?php esc_html_e('Track how much of your WordPress library is protected with Encypher provenance markers.', 'encypher-provenance'); ?>
            </p>

            <div class="encypher-analytics-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-top:20px;">
                <div class="analytics-card">
                    <span class="analytics-card-icon dashicons dashicons-media-document" aria-hidden="true"></span>
                    <strong class="analytics-card-value"><?php echo esc_html($stats['total_posts']); ?></strong>
                    <span class="analytics-card-label"><?php esc_html_e('Published posts', 'encypher-provenance'); ?></span>
                </div>
                <div class="analytics-card">
                    <span class="analytics-card-icon dashicons dashicons-yes-alt" aria-hidden="true"></span>
                    <strong class="analytics-card-value"><?php echo esc_html($stats['signed_posts']); ?></strong>
                    <span class="analytics-card-label"><?php esc_html_e('Signed posts', 'encypher-provenance'); ?></span>
                </div>
                <div class="analytics-card">
                    <span class="analytics-card-icon dashicons dashicons-chart-pie" aria-hidden="true"></span>
                    <strong class="analytics-card-value"><?php echo esc_html($stats['coverage']); ?>%</strong>
                    <span class="analytics-card-label"><?php esc_html_e('Coverage', 'encypher-provenance'); ?></span>
                </div>
                <div class="analytics-card">
                    <span class="analytics-card-icon dashicons dashicons-editor-ol" aria-hidden="true"></span>
                    <strong class="analytics-card-value"><?php echo esc_html($stats['sentence_posts']); ?></strong>
                    <span class="analytics-card-label"><?php esc_html_e('Sentence-level posts', 'encypher-provenance'); ?></span>
                </div>

                <?php
                $verify_hits_total = (int) get_option('encypher_verify_hits', 0);
                $verify_hits_daily = get_option('encypher_verify_hits_daily', []);
                $verify_hits_daily = is_array($verify_hits_daily) ? $verify_hits_daily : [];
                $cutoff_30d = gmdate('Y-m-d', strtotime('-30 days'));
                $verify_hits_30d = 0;
                foreach ($verify_hits_daily as $date => $count) {
                    if ($date >= $cutoff_30d) {
                        $verify_hits_30d += (int) $count;
                    }
                }
                ?>
                <div class="analytics-card">
                    <span class="analytics-card-icon dashicons dashicons-shield" aria-hidden="true"></span>
                    <strong class="analytics-card-value"><?php echo esc_html(number_format_i18n($verify_hits_30d)); ?></strong>
                    <span class="analytics-card-label"><?php esc_html_e('Verification Hits (30d)', 'encypher-provenance'); ?></span>
                    <small style="display:block; color:#50575e; margin-top:4px; font-size:11px;">
                        <?php echo esc_html(sprintf(
                            /* translators: %s: total lifetime count */
                            __('%s lifetime', 'encypher-provenance'),
                            number_format_i18n($verify_hits_total)
                        )); ?>
                    </small>
                </div>

                <div class="analytics-card">
                    <span class="analytics-card-icon dashicons dashicons-warning" aria-hidden="true"></span>
                    <strong class="analytics-card-value"><?php echo esc_html($stats['tampered_posts']); ?></strong>
                    <span class="analytics-card-label"><?php esc_html_e('Tampering alerts', 'encypher-provenance'); ?></span>
                </div>
            </div>

            <div class="encypher-analytics-section" style="margin-top:32px;">
            <h2 style="margin-top:0;"><?php esc_html_e('Recent activity', 'encypher-provenance'); ?></h2>
            <table class="widefat striped encypher-activity-table">
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
                                <td>
                                    <?php
                                    $status_text = (string) $recent['status'];
                                    if ('c2pa_protected' === $status_text) {
                                        $status_text = 'encypher_signed';
                                    }
                                    $status_slug = sanitize_html_class(strtolower($status_text));
                                    ?>
                                    <span class="encypher-status-pill encypher-status-pill--<?php echo esc_attr($status_slug); ?>">
                                        <?php echo esc_html($status_text); ?>
                                    </span>
                                </td>
                                <td><?php echo esc_html($recent['sentences']); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </tbody>
            </table>
            <p class="encypher-status-legend">
                <?php esc_html_e('Status guide:', 'encypher-provenance'); ?>
                <code>encypher_signed</code>,
                <code>modified</code>,
                <code>tampered</code>,
                <code>verification_failed</code>.
            </p>
            </div>

            <p style="margin-top:24px;">
                <?php esc_html_e('Workspace tier:', 'encypher-provenance'); ?>
                <strong><?php echo esc_html(ucfirst($stats['tier'])); ?></strong>
            </p>

            <?php
            // ── Error Log ──────────────────────────────────────────────────────
            $error_log_entries = ErrorLog::get_log_for_tier($tier);
            $full_log_count    = count(ErrorLog::get_raw_log());
            $is_enterprise_tier = in_array($tier, ['enterprise', 'strategic_partner'], true);
            $clear_nonce = wp_create_nonce('encypher_clear_error_log');
            ?>
            <div id="error-log" class="encypher-analytics-section" style="margin-top:40px;">
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                    <h2 style="margin:0;"><?php esc_html_e('Error Log', 'encypher-provenance'); ?></h2>
                    <div style="display:flex;gap:8px;align-items:center;">
                        <?php if ($is_enterprise_tier && ! empty($error_log_entries)): ?>
                            <a href="<?php echo esc_url(admin_url('admin-ajax.php?action=encypher_export_error_log&_wpnonce=' . wp_create_nonce('encypher_export_error_log'))); ?>"
                               class="button button-small">
                                <?php esc_html_e('Export CSV', 'encypher-provenance'); ?>
                            </a>
                        <?php endif; ?>
                        <?php if (! empty($error_log_entries)): ?>
                            <button type="button"
                                class="button button-small"
                                onclick="if(confirm('<?php echo esc_js(__('Clear all error log entries?', 'encypher-provenance')); ?>')) { jQuery.post(ajaxurl, {action:'encypher_clear_error_log', _wpnonce:'<?php echo esc_js($clear_nonce); ?>'}, function(){ location.reload(); }); }">
                                <?php esc_html_e('Clear log', 'encypher-provenance'); ?>
                            </button>
                        <?php endif; ?>
                    </div>
                </div>
                <p class="description" style="margin-top:6px;">
                    <?php
                    if ($is_enterprise_tier) {
                        echo esc_html(sprintf(
                            /* translators: %d: total entries */
                            __('Showing all %d entries (last 50 stored).', 'encypher-provenance'),
                            $full_log_count
                        ));
                    } else {
                        echo esc_html(sprintf(
                            /* translators: 1: shown count, 2: total count */
                            __('Showing %1$d of %2$d entries. Upgrade to Enterprise to see the full log and export CSV.', 'encypher-provenance'),
                            count($error_log_entries),
                            $full_log_count
                        ));
                    }
                    ?>
                </p>

                <?php if (empty($error_log_entries)): ?>
                    <p style="color:#50575e;"><?php esc_html_e('No signing or verification errors recorded.', 'encypher-provenance'); ?></p>
                <?php else: ?>
                    <table class="widefat striped" style="margin-top:12px;">
                        <thead>
                            <tr>
                                <th style="width:160px;"><?php esc_html_e('Time', 'encypher-provenance'); ?></th>
                                <th><?php esc_html_e('Post', 'encypher-provenance'); ?></th>
                                <th style="width:120px;"><?php esc_html_e('Context', 'encypher-provenance'); ?></th>
                                <th style="width:140px;"><?php esc_html_e('Error code', 'encypher-provenance'); ?></th>
                                <th><?php esc_html_e('Message', 'encypher-provenance'); ?></th>
                                <th style="width:60px;"><?php esc_html_e('Streak', 'encypher-provenance'); ?></th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($error_log_entries as $entry): ?>
                                <?php
                                $ts = isset($entry['timestamp'])
                                    ? wp_date(get_option('date_format') . ' H:i:s', strtotime($entry['timestamp']))
                                    : '—';
                                $post_id    = (int) ($entry['post_id'] ?? 0);
                                $post_title = $entry['post_title'] ?? '';
                                $streak     = (int) ($entry['consecutive_failures'] ?? 0);
                                ?>
                                <tr>
                                    <td style="font-size:12px;color:#50575e;"><?php echo esc_html($ts); ?></td>
                                    <td>
                                        <?php if ($post_id > 0 && $post_title): ?>
                                            <a href="<?php echo esc_url(get_edit_post_link($post_id)); ?>">
                                                <?php echo esc_html($post_title); ?>
                                            </a>
                                            <span style="color:#646970;font-size:11px;"> #<?php echo esc_html($post_id); ?></span>
                                        <?php elseif ($post_id > 0): ?>
                                            <span style="color:#646970;">#<?php echo esc_html($post_id); ?></span>
                                        <?php else: ?>
                                            <span style="color:#646970;">—</span>
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <code style="font-size:11px;"><?php echo esc_html($entry['context'] ?? ''); ?></code>
                                    </td>
                                    <td>
                                        <code style="font-size:11px;"><?php echo esc_html($entry['error_code'] ?? ''); ?></code>
                                    </td>
                                    <td style="font-size:12px;"><?php echo esc_html($entry['error_message'] ?? ''); ?></td>
                                    <td style="text-align:center;">
                                        <?php if ($streak >= 3): ?>
                                            <span style="color:#d63638;font-weight:600;"><?php echo esc_html($streak); ?></span>
                                        <?php elseif ($streak > 1): ?>
                                            <span style="color:#dba617;"><?php echo esc_html($streak); ?></span>
                                        <?php else: ?>
                                            <?php echo esc_html($streak ?: '1'); ?>
                                        <?php endif; ?>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                    <?php if (! $is_enterprise_tier && $full_log_count > ErrorLog::DISPLAY_FREE): ?>
                        <p style="margin-top:8px;font-size:12px;color:#646970;">
                            <?php echo wp_kses(
                                sprintf(
                                    /* translators: %s: pricing link */
                                    __('<a href="%s" target="_blank" rel="noopener noreferrer">Upgrade to Enterprise</a> to see all %d entries and export as CSV.', 'encypher-provenance'),
                                    'https://encypherai.com/pricing',
                                    $full_log_count
                                ),
                                ['a' => ['href' => [], 'target' => [], 'rel' => []]]
                            ); ?>
                        </p>
                    <?php endif; ?>
                <?php endif; ?>
            </div>
        </div>
        <style>
            .encypher-analytics-page .encypher-page-title {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 4px;
            }
            .encypher-analytics-page .encypher-logo {
                display: inline-flex;
                align-items: center;
            }
            .encypher-analytics-page .encypher-brand-lockup {
                width: 120px;
                height: auto;
                display: block;
            }
            .encypher-analytics-page .encypher-title-divider {
                color: #8c8f94;
                font-weight: 400;
            }
            .encypher-analytics-page .analytics-card {
                background: #fff;
                border: 1px solid #dcdcde;
                border-radius: 10px;
                padding: 16px;
                text-align: center;
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
            }
            .encypher-analytics-page .analytics-card-icon {
                width: 30px;
                height: 30px;
                line-height: 30px;
                border-radius: 999px;
                background: #e6f0ff;
                color: #0a4b78;
                font-size: 16px;
                margin: 0 auto 8px;
                display: block;
            }
            .encypher-analytics-page .analytics-card-value {
                display: block;
                font-size: 28px;
                color: #1d2327;
                line-height: 1.1;
            }
            .encypher-analytics-page .analytics-card-label {
                color: #50575e;
                font-size: 12px;
                letter-spacing: 0.01em;
            }
            .encypher-analytics-page .encypher-analytics-section {
                background: #fff;
                border: 1px solid #dcdcde;
                border-radius: 10px;
                padding: 16px;
            }
            .encypher-analytics-page .encypher-activity-table td,
            .encypher-analytics-page .encypher-activity-table th {
                vertical-align: middle;
            }
            .encypher-analytics-page .encypher-status-pill {
                display: inline-block;
                border-radius: 999px;
                padding: 2px 10px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.02em;
                background: #e8f5e9;
                color: #1e5e2f;
            }
            .encypher-analytics-page .encypher-status-pill--verification_failed,
            .encypher-analytics-page .encypher-status-pill--tampered {
                background: #fbeaea;
                color: #b42318;
            }
            .encypher-analytics-page .encypher-status-pill--modified,
            .encypher-analytics-page .encypher-status-pill--not_signed {
                background: #fff4d6;
                color: #8a4b00;
            }
            .encypher-analytics-page .encypher-status-legend {
                margin: 12px 0 0;
                font-size: 12px;
                color: #50575e;
            }
            .encypher-analytics-page .encypher-status-legend code {
                font-size: 11px;
            }
            @media (max-width: 782px) {
                .encypher-analytics-page .encypher-page-title {
                    font-size: 22px;
                }
                .encypher-analytics-page .encypher-analytics-grid {
                    grid-template-columns: 1fr !important;
                }
                .encypher-analytics-page .analytics-card {
                    padding: 14px;
                }
                .encypher-analytics-page .encypher-analytics-section {
                    padding: 12px;
                }
                .encypher-analytics-page .encypher-activity-table th,
                .encypher-analytics-page .encypher-activity-table td {
                    font-size: 12px;
                }
            }
        </style>
        <?php
    }

    private function gather_analytics_stats(bool $with_recent = false): array
    {
        global $wpdb;

        $settings = get_option('encypher_provenance_settings', []);
        $post_types = isset($settings['post_types']) && is_array($settings['post_types'])
            ? array_values(array_filter(array_map('sanitize_text_field', $settings['post_types'])))
            : ['post', 'page'];
        if (empty($post_types)) {
            $post_types = ['post', 'page'];
        }

        $placeholders = implode(',', array_fill(0, count($post_types), '%s'));

        $total_posts = (int) $wpdb->get_var(
            $wpdb->prepare(
                "SELECT COUNT(ID) FROM {$wpdb->posts} WHERE post_status = 'publish' AND post_type IN ($placeholders)",
                ...$post_types
            )
        );

        $signed_posts = (int) $wpdb->get_var(
            $wpdb->prepare(
                "SELECT COUNT(DISTINCT pm.post_id)
                 FROM {$wpdb->postmeta} pm
                 INNER JOIN {$wpdb->posts} p ON p.ID = pm.post_id
                 WHERE pm.meta_key = %s
                   AND pm.meta_value = %s
                   AND p.post_status = 'publish'
                   AND p.post_type IN ($placeholders)",
                '_encypher_marked',
                '1',
                ...$post_types
            )
        );

        $sentence_posts = (int) $wpdb->get_var(
            $wpdb->prepare(
                "SELECT COUNT(DISTINCT pm.post_id)
                 FROM {$wpdb->postmeta} pm
                 INNER JOIN {$wpdb->posts} p ON p.ID = pm.post_id
                 WHERE pm.meta_key = '_encypher_provenance_total_sentences'
                   AND CAST(pm.meta_value AS UNSIGNED) > 0
                   AND p.post_status = 'publish'
                   AND p.post_type IN ($placeholders)",
                ...$post_types
            )
        );

        $tampered_posts = (int) $wpdb->get_var(
            $wpdb->prepare(
                "SELECT COUNT(DISTINCT pm.post_id)
                 FROM {$wpdb->postmeta} pm
                 INNER JOIN {$wpdb->posts} p ON p.ID = pm.post_id
                 WHERE pm.meta_key = %s
                   AND pm.meta_value = %s
                   AND p.post_status = 'publish'
                   AND p.post_type IN ($placeholders)",
                '_encypher_provenance_status',
                'tampered',
                ...$post_types
            )
        );

        $coverage = $total_posts > 0 ? round(($signed_posts / $total_posts) * 100) : 0;
        if ($coverage > 100) {
            $coverage = 100;
        }

        $recent_posts = [];
        if ($with_recent) {
            $recent_rows = $wpdb->get_results(
                "SELECT post_id, meta_value FROM {$wpdb->postmeta}
                 WHERE meta_key = '_encypher_provenance_last_signed'
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
                    'status' => get_post_meta($post->ID, '_encypher_provenance_status', true) ?: __('Unknown', 'encypher-provenance'),
                    'sentences' => (int) get_post_meta($post->ID, '_encypher_provenance_total_sentences', true),
                ];
            }
        }

        $settings = get_option('encypher_provenance_settings', []);
        $tier = isset($settings['tier']) ? $settings['tier'] : 'free';

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
