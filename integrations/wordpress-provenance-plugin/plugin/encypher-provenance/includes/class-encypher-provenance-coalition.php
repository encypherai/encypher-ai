<?php
namespace EncypherProvenance;

if (! defined('ABSPATH')) {
    exit;
}

/**
 * Coalition integration class.
 * Handles coalition membership and stats display.
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
            ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/css/coalition-widget.css',
            [],
            ENCYPHER_PROVENANCE_VERSION
        );
    }

    /**
     * Render coalition widget on dashboard.
     */
    public function render_coalition_widget(): void
    {
        $stats = $this->get_coalition_stats();
        $settings = get_option('encypher_provenance_settings', []);
        $tier = $settings['tier'] ?? 'free';

        include ENCYPHER_PROVENANCE_PLUGIN_DIR . 'admin/partials/coalition-widget.php';
    }

    /**
     * Render full coalition page.
     */
    public function render_coalition_page(): void
    {
        $stats = $this->get_coalition_stats();
        $settings = get_option('encypher_provenance_settings', []);
        $tier = $settings['tier'] ?? 'free';

        include ENCYPHER_PROVENANCE_PLUGIN_DIR . 'admin/partials/coalition-page.php';
    }

    /**
     * Get coalition stats from API.
     *
     * @return array|null Coalition stats or null on error
     */
    public function get_coalition_stats(): ?array
    {
        $settings = get_option('encypher_provenance_settings', []);
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

}
