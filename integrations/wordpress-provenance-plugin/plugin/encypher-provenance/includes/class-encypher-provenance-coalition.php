<?php
namespace EncypherAssurance;

if (! defined('ABSPATH')) {
    exit;
}

/**
 * Coalition integration class.
 * Handles coalition membership, stats display, and revenue tracking.
 */
class Coalition
{
    /**
     * Register WordPress hooks.
     */
    public function register_hooks(): void
    {
        add_action('wp_dashboard_setup', [$this, 'add_coalition_widget']);
        add_action('admin_menu', [$this, 'add_coalition_page']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_coalition_assets']);
    }

    /**
     * Add coalition widget to WordPress dashboard.
     */
    public function add_coalition_widget(): void
    {
        wp_add_dashboard_widget(
            'encypher_coalition_widget',
            __('Encypher Coalition Stats', 'encypher-provenance'),
            [$this, 'render_coalition_widget']
        );
    }

    /**
     * Add coalition page to admin menu.
     */
    public function add_coalition_page(): void
    {
        add_submenu_page(
            'encypher',
            __('Coalition Dashboard', 'encypher-provenance'),
            __('Coalition', 'encypher-provenance'),
            'manage_options',
            'encypher-coalition',
            [$this, 'render_coalition_page']
        );
    }

    /**
     * Enqueue coalition CSS and JS.
     */
    public function enqueue_coalition_assets($hook): void
    {
        // Only load on dashboard and coalition pages
        if ($hook !== 'index.php' && strpos($hook, 'encypher-coalition') === false) {
            return;
        }

        wp_enqueue_style(
            'encypher-coalition-widget',
            ENCYPHER_ASSURANCE_PLUGIN_URL . 'assets/css/coalition-widget.css',
            [],
            ENCYPHER_ASSURANCE_VERSION
        );
    }

    /**
     * Render coalition widget on dashboard.
     */
    public function render_coalition_widget(): void
    {
        $stats = $this->get_coalition_stats();
        $settings = get_option('encypher_assurance_settings', []);
        $tier = $settings['tier'] ?? 'free';

        include ENCYPHER_ASSURANCE_PLUGIN_DIR . 'admin/partials/coalition-widget.php';
    }

    /**
     * Render full coalition page.
     */
    public function render_coalition_page(): void
    {
        $stats = $this->get_coalition_stats();
        $settings = get_option('encypher_assurance_settings', []);
        $tier = $settings['tier'] ?? 'free';

        include ENCYPHER_ASSURANCE_PLUGIN_DIR . 'admin/partials/coalition-page.php';
    }

    /**
     * Get coalition stats from API.
     *
     * @return array|null Coalition stats or null on error
     */
    public function get_coalition_stats(): ?array
    {
        $settings = get_option('encypher_assurance_settings', []);
        $api_base = $settings['api_base_url'] ?? 'https://api.encypherai.com/api/v1';
        $api_key = $settings['api_key'] ?? '';

        if (empty($api_key)) {
            return null;
        }

        // Check transient cache first (1 hour)
        $cache_key = 'encypher_coalition_stats_' . md5($api_key);
        $cached = get_transient($cache_key);
        if ($cached !== false) {
            return $cached;
        }

        $response = wp_remote_get(
            $api_base . '/coalition/stats',
            [
                'headers' => [
                    'Authorization' => 'Bearer ' . $api_key,
                    'Content-Type' => 'application/json',
                ],
                'timeout' => 15,
            ]
        );

        if (is_wp_error($response)) {
            error_log('Encypher Coalition: API error - ' . $response->get_error_message());
            return null;
        }

        $status_code = wp_remote_retrieve_response_code($response);
        if ($status_code !== 200) {
            error_log('Encypher Coalition: API returned status ' . $status_code);
            return null;
        }

        $body = json_decode(wp_remote_retrieve_body($response), true);
        
        if (!isset($body['success']) || !$body['success']) {
            error_log('Encypher Coalition: API returned unsuccessful response');
            return null;
        }

        $stats = $body['data'] ?? null;

        // Cache for 1 hour
        if ($stats) {
            set_transient($cache_key, $stats, HOUR_IN_SECONDS);
        }

        return $stats;
    }

    /**
     * Get revenue split percentage for current tier.
     *
     * @param string $tier User's tier (free, pro, enterprise)
     * @return array Revenue split info
     */
    public function get_revenue_split(string $tier): array
    {
        $splits = [
            'free' => [
                'member_percent' => 60,
                'encypher_percent' => 40,
                'payout_threshold' => 50,
            ],
            'enterprise' => [
                'member_percent' => 85,
                'encypher_percent' => 15,
                'payout_threshold' => 0, // No minimum
            ],
            'strategic_partner' => [
                'member_percent' => 85,
                'encypher_percent' => 15,
                'payout_threshold' => 0,
            ],
        ];

        return $splits[$tier] ?? $splits['free'];
    }

    /**
     * Calculate Pro upgrade ROI based on current earnings.
     *
     * @param float $current_earnings Current monthly earnings
     * @param string $current_tier Current tier
     * @return array ROI calculation
     */
    public function calculate_pro_upgrade_roi(float $current_earnings, string $current_tier = 'free'): array
    {
        if ($current_tier !== 'free') {
            return [
                'show_upgrade' => false,
                'message' => '',
            ];
        }

        $free_split = $this->get_revenue_split('free');
        $enterprise_split = $this->get_revenue_split('enterprise');

        $free_payout = $current_earnings * ($free_split['member_percent'] / 100);
        $enterprise_payout = $current_earnings * ($enterprise_split['member_percent'] / 100);
        $monthly_gain = $enterprise_payout - $free_payout;

        return [
            'show_upgrade' => true,
            'current_payout' => $free_payout,
            'pro_payout' => $enterprise_payout,
            'monthly_gain' => $monthly_gain,
            'pro_cost' => 0,
            'net_benefit' => $monthly_gain,
            'break_even_earnings' => 0,
            'is_profitable' => true,
        ];
    }
}
