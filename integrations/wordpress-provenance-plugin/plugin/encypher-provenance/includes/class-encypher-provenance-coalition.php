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
    private function debug_log(string $message): void
    {
        if (defined('WP_DEBUG') && WP_DEBUG) {
            error_log('Encypher: ' . $message);
        }
    }

    /**
     * Register WordPress hooks.
     */
    public function register_hooks(): void
    {
        add_action('wp_dashboard_setup', [$this, 'add_coalition_widget']);
        add_action('admin_menu', [$this, 'add_coalition_page']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_coalition_assets']);
        add_action('update_option_encypher_provenance_settings', [$this, 'maybe_enroll_on_settings_save'], 10, 2);
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
        $cache_key = 'encypher_coalition_stats_' . md5(strtolower((string) $api_base) . '|' . (string) $api_key);
        $cached = get_transient($cache_key);
        if ($cached !== false) {
            return $cached;
        }

        $response = wp_remote_get(
            $api_base . '/coalition/dashboard',
            [
                'headers' => [
                    'Authorization' => 'Bearer ' . $api_key,
                    'Content-Type' => 'application/json',
                ],
                'timeout' => 15,
            ]
        );

        if (is_wp_error($response)) {
            $this->debug_log('Coalition API error - ' . $response->get_error_message());
            return null;
        }

        $status_code = wp_remote_retrieve_response_code($response);
        if ($status_code >= 500) {
            $this->debug_log('Coalition API returned status ' . $status_code);
            return null;
        }

        if ($status_code !== 200) {
            $this->debug_log('Coalition API returned non-fatal status ' . $status_code . '; using empty stats fallback');
            return $this->build_empty_stats_payload();
        }

        $body = json_decode(wp_remote_retrieve_body($response), true);
        if (!is_array($body)) {
            $this->debug_log('Coalition API returned invalid JSON payload');
            return $this->build_empty_stats_payload();
        }

        $raw_stats = isset($body['data']) && is_array($body['data']) ? $body['data'] : $body;
        $stats = $this->normalize_stats_payload($raw_stats);
        if (!is_array($stats)) {
            return $this->build_empty_stats_payload();
        }

        // Cache for 1 hour
        if ($stats) {
            set_transient($cache_key, $stats, HOUR_IN_SECONDS);
        }

        return $stats;
    }

    /**
     * Normalize coalition payloads from API into the legacy widget/page shape.
     *
     * @param array $payload Raw API payload.
     * @return array|null
     */
    private function normalize_stats_payload(array $payload): ?array
    {
        if (isset($payload['content_stats']) && isset($payload['coalition_stats'])) {
            return $payload;
        }

        if (!isset($payload['current_period']) || !is_array($payload['current_period'])) {
            return null;
        }

        $current_period = $payload['current_period'];

        return [
            'content_stats' => [
                'total_documents' => isset($current_period['documents_count']) ? (int) $current_period['documents_count'] : 0,
                'total_word_count' => isset($current_period['sentences_count']) ? (int) $current_period['sentences_count'] : 0,
                'verification_count' => 0,
                'last_signed' => null,
            ],
            'coalition_stats' => [
                'total_members' => 0,
                'total_content_pool' => isset($current_period['documents_count']) ? (int) $current_period['documents_count'] : 0,
                'active_agreements' => isset($payload['recent_earnings']) && is_array($payload['recent_earnings']) ? count($payload['recent_earnings']) : 0,
            ],
        ];
    }

    /**
     * Provide a predictable zero-state payload so dashboard surfaces can render
     * even when coalition data is unavailable for the current account.
     */
    private function build_empty_stats_payload(): array
    {
        return [
            'content_stats' => [
                'total_documents' => 0,
                'total_word_count' => 0,
                'verification_count' => 0,
                'last_signed' => null,
            ],
            'coalition_stats' => [
                'total_members' => 0,
                'total_content_pool' => 0,
                'active_agreements' => 0,
            ],
        ];
    }

    /**
     * Enroll this WordPress site in the Encypher Coalition.
     * Called when the user enables the coalition enrollment toggle.
     *
     * @return array{success: bool, message: string}
     */
    public function enroll_site(): array
    {
        $settings = get_option('encypher_provenance_settings', []);
        $api_base = rtrim($settings['api_base_url'] ?? 'https://api.encypherai.com/api/v1', '/');
        $api_key  = $settings['api_key'] ?? '';

        if (empty($api_key)) {
            return ['success' => false, 'message' => __('API key required for Coalition enrollment.', 'encypher-provenance')];
        }

        $site_url = get_home_url();
        $site_name = get_bloginfo('name');

        $body = [
            'site_url'  => $site_url,
            'site_name' => $site_name,
            'source'    => 'wordpress-plugin',
        ];

        $response = wp_remote_post(
            $api_base . '/coalition/enroll',
            [
                'headers' => [
                    'Authorization' => 'Bearer ' . $api_key,
                    'Content-Type'  => 'application/json',
                ],
                'body'    => wp_json_encode($body),
                'timeout' => 20,
            ]
        );

        if (is_wp_error($response)) {
            $this->debug_log('Coalition enrollment error: ' . $response->get_error_message());
            return ['success' => false, 'message' => $response->get_error_message()];
        }

        $status = wp_remote_retrieve_response_code($response);
        if ($status < 200 || $status >= 300) {
            $body_str = wp_remote_retrieve_body($response);
            $decoded  = json_decode($body_str, true);
            $msg      = isset($decoded['message']) ? $decoded['message'] : sprintf(__('Enrollment failed (HTTP %d).', 'encypher-provenance'), $status);
            return ['success' => false, 'message' => $msg];
        }

        update_option('encypher_coalition_enrolled', true);
        update_option('encypher_coalition_enrolled_at', gmdate('c'));

        return ['success' => true, 'message' => __('Successfully enrolled in the Encypher Coalition.', 'encypher-provenance')];
    }

    /**
     * Trigger Coalition enrollment when the admin saves settings with the toggle enabled.
     *
     * @param mixed $old_value Previous option value.
     * @param mixed $new_value New option value.
     */
    public function maybe_enroll_on_settings_save($old_value, $new_value): void
    {
        $old_enrolled = !empty($old_value['coalition_auto_enroll']);
        $new_enrolled = !empty($new_value['coalition_auto_enroll']);

        // Only trigger on rising edge (user just enabled it)
        if (!$old_enrolled && $new_enrolled) {
            $result = $this->enroll_site();
            if ($result['success']) {
                add_settings_error(
                    'encypher_provenance_settings',
                    'coalition_enrolled',
                    __('Encypher Coalition enrollment successful! Your site is now a coalition member.', 'encypher-provenance'),
                    'success'
                );
            } else {
                add_settings_error(
                    'encypher_provenance_settings',
                    'coalition_enroll_failed',
                    sprintf(__('Coalition enrollment failed: %s', 'encypher-provenance'), $result['message']),
                    'error'
                );
            }
        }
    }

}
