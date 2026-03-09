<?php
namespace EncypherProvenance;

use WP_Query;

if (! defined('ABSPATH')) {
    exit;
}

/**
 * Handles bulk marking operations for WordPress archives.
 *
 * Provides admin interface and AJAX endpoints for marking
 * existing posts in batches with progress tracking.
 */
class Bulk
{
    /**
     * Register hooks for bulk marking functionality.
     */
    public function register_hooks(): void
    {
        add_action('admin_menu', [$this, 'register_bulk_page']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_bulk_assets']);
        add_action('wp_ajax_encypher_bulk_mark_batch', [$this, 'handle_bulk_mark_batch']);
        add_action('wp_ajax_encypher_get_bulk_status', [$this, 'handle_get_bulk_status']);
    }

    /**
     * Register bulk marking admin page.
     */
    public function register_bulk_page(): void
    {
        add_submenu_page(
            'encypher',
            __('Bulk Sign', 'encypher-provenance'),
            __('Bulk Sign', 'encypher-provenance'),
            'manage_options',
            'encypher-bulk-mark',
            [$this, 'render_bulk_page']
        );
    }

    /**
     * Enqueue assets for bulk marking page.
     */
    public function enqueue_bulk_assets(string $hook_suffix): void
    {
        if ('encypher_page_encypher-bulk-mark' !== $hook_suffix) {
            return;
        }

        $settings = get_option('encypher_provenance_settings', []);
        $tier = isset($settings['tier']) ? (string) $settings['tier'] : 'free';
        $pricing = $this->get_archive_pricing($tier);
        $bulk_script_path = ENCYPHER_PROVENANCE_PLUGIN_DIR . 'assets/js/bulk-mark.js';
        $bulk_style_path = ENCYPHER_PROVENANCE_PLUGIN_DIR . 'assets/css/bulk-mark.css';
        $bulk_script_version = file_exists($bulk_script_path) ? (string) filemtime($bulk_script_path) : ENCYPHER_PROVENANCE_VERSION;
        $bulk_style_version = file_exists($bulk_style_path) ? (string) filemtime($bulk_style_path) : ENCYPHER_PROVENANCE_VERSION;

        wp_enqueue_script(
            'encypher-bulk-mark',
            ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/js/bulk-mark.js',
            ['jquery'],
            $bulk_script_version,
            true
        );

        wp_localize_script(
            'encypher-bulk-mark',
            'EncypherBulkMark',
            [
                'ajaxUrl' => admin_url('admin-ajax.php'),
                'nonce' => wp_create_nonce('encypher_bulk_mark'),
                'restUrl' => esc_url_raw(rest_url('encypher-provenance/v1/')),
                'restNonce' => wp_create_nonce('wp_rest'),
                'tier' => $tier,
                'pricing' => $pricing,
                'billingUrlBase' => 'https://dashboard.encypherai.com/billing',
            ]
        );

        wp_enqueue_style(
            'encypher-bulk-mark-css',
            ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/css/bulk-mark.css',
            [],
            $bulk_style_version
        );
    }

    /**
     * Render bulk marking admin page.
     */
    public function render_bulk_page(): void
    {
        if (! current_user_can('manage_options')) {
            return;
        }

        $settings = get_option('encypher_provenance_settings', []);
        $tier = $settings['tier'] ?? 'free';
        $usage = $this->normalize_usage_snapshot(
            isset($settings['usage']) && is_array($settings['usage']) ? $settings['usage'] : [],
            $tier
        );
        $pricing = $this->get_archive_pricing($tier);
        $api_calls = isset($usage['api_calls']) && is_array($usage['api_calls']) ? $usage['api_calls'] : [];
        $remaining = isset($api_calls['remaining']) ? (int) $api_calls['remaining'] : 0;
        $post_types = get_post_types(['public' => true], 'objects');

        ?>
        <div class="wrap encypher-bulk-mark-page">
            <h1 class="encypher-page-title">
                <span class="encypher-logo">
                    <img
                        class="encypher-brand-lockup"
                        src="<?php echo esc_url(ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/images/encypher_full_logo_color.svg'); ?>"
                        alt="<?php echo esc_attr__('Encypher', 'encypher-provenance'); ?>"
                    />
                </span>
                <span class="encypher-title-divider" aria-hidden="true">|</span>
                <span><?php esc_html_e('Bulk Sign', 'encypher-provenance'); ?></span>
            </h1>

            <div class="encypher-bulk-intro">
                <p><?php esc_html_e('Protect your existing archive in one run. Estimate the size of your backlog, review the one-time archive price, then bulk sign everything that should carry provenance.', 'encypher-provenance'); ?></p>
            </div>

            <?php $this->render_usage_progress_bar($usage); ?>

            <?php if ('free' === $tier): ?>
            <div class="notice notice-info">
                <p>
                    <strong><?php esc_html_e('Free plan:', 'encypher-provenance'); ?></strong>
                    <?php esc_html_e('Publishing workflows include 1,000 sign requests/month.', 'encypher-provenance'); ?>
                    <?php esc_html_e('Archive backfill is available as a one-time add-on at $0.01/document.', 'encypher-provenance'); ?>
                </p>
            </div>
            <?php else: ?>
            <div class="notice notice-success">
                <p>
                    <strong><?php esc_html_e('Enterprise plan:', 'encypher-provenance'); ?></strong>
                    <?php esc_html_e('Archive backfill is included with your plan. Estimate the scope below and start bulk signing when ready.', 'encypher-provenance'); ?>
                </p>
            </div>
            <?php endif; ?>

            <div class="encypher-bulk-form">
                <h2><?php esc_html_e('Select Archive Content to Protect', 'encypher-provenance'); ?></h2>

                <table class="form-table">
                    <tr>
                        <th scope="row"><?php esc_html_e('Post Types', 'encypher-provenance'); ?></th>
                        <td>
                            <?php foreach ($post_types as $post_type): ?>
                                <?php
                                $count = wp_count_posts($post_type->name);
                                $total = isset($count->publish) ? $count->publish : 0;
                                ?>
                                <label>
                                    <input type="checkbox"
                                           name="post_types[]"
                                           value="<?php echo esc_attr($post_type->name); ?>"
                                           data-count="<?php echo esc_attr($total); ?>"
                                           <?php checked(in_array($post_type->name, ['post', 'page'], true)); ?>>
                                    <?php echo esc_html($post_type->label); ?>
                                    <span class="description">(<?php echo esc_html($total); ?> <?php esc_html_e('found', 'encypher-provenance'); ?>)</span>
                                </label><br>
                            <?php endforeach; ?>
                        </td>
                    </tr>

                    <tr>
                        <th scope="row"><?php esc_html_e('Date Range', 'encypher-provenance'); ?></th>
                        <td>
                            <select name="date_range" id="encypher-date-range">
                                <option value="all"><?php esc_html_e('All Time', 'encypher-provenance'); ?></option>
                                <option value="last_month"><?php esc_html_e('Last Month', 'encypher-provenance'); ?></option>
                                <option value="last_3_months"><?php esc_html_e('Last 3 Months', 'encypher-provenance'); ?></option>
                                <option value="last_6_months"><?php esc_html_e('Last 6 Months', 'encypher-provenance'); ?></option>
                                <option value="last_year"><?php esc_html_e('Last Year', 'encypher-provenance'); ?></option>
                                <option value="custom"><?php esc_html_e('Custom Range', 'encypher-provenance'); ?></option>
                            </select>

                            <div id="encypher-custom-date-range" style="display:none; margin-top:10px;">
                                <label>
                                    <?php esc_html_e('From:', 'encypher-provenance'); ?>
                                    <input type="date" name="date_from" id="encypher-date-from">
                                </label>
                                <label style="margin-left:10px;">
                                    <?php esc_html_e('To:', 'encypher-provenance'); ?>
                                    <input type="date" name="date_to" id="encypher-date-to">
                                </label>
                            </div>
                        </td>
                    </tr>

                    <tr>
                        <th scope="row"><?php esc_html_e('Status Filter', 'encypher-provenance'); ?></th>
                        <td>
                            <label>
                                <input type="radio" name="status_filter" value="unmarked" checked>
                                <?php esc_html_e('Unmarked Only', 'encypher-provenance'); ?>
                                <span class="description"><?php esc_html_e('(Recommended)', 'encypher-provenance'); ?></span>
                            </label><br>
                            <label>
                                <input type="radio" name="status_filter" value="all">
                                <?php esc_html_e('All Posts', 'encypher-provenance'); ?>
                                <span class="description"><?php esc_html_e('(Re-mark already marked posts)', 'encypher-provenance'); ?></span>
                            </label>
                        </td>
                    </tr>

                    <tr>
                        <th scope="row"><?php esc_html_e('Batch Size', 'encypher-provenance'); ?></th>
                        <td>
                            <input type="number" name="batch_size" id="encypher-batch-size" value="10" min="1" max="50">
                            <p class="description"><?php esc_html_e('Number of posts to process per batch (1-50). Lower values are safer for slow servers.', 'encypher-provenance'); ?></p>
                        </td>
                    </tr>
                </table>

                <div class="encypher-bulk-summary">
                    <h3><?php esc_html_e('Summary', 'encypher-provenance'); ?></h3>
                    <p>
                        <strong><?php esc_html_e('Total posts to mark:', 'encypher-provenance'); ?></strong>
                        <span id="encypher-total-count">0</span>
                    </p>
                    <p>
                        <strong><?php esc_html_e('Estimated archive backfill total:', 'encypher-provenance'); ?></strong>
                        <span id="encypher-archive-estimate"><?php echo esc_html('$0.00'); ?></span>
                    </p>
                    <?php if ('free' === $tier): ?>
                    <p class="encypher-tier-limit encypher-free-plan-note">
                        <strong><?php esc_html_e('Free publishing quota remaining this month:', 'encypher-provenance'); ?></strong>
                        <span id="encypher-free-remaining"><?php echo esc_html(number_format_i18n(max(0, $remaining))); ?></span>
                        <?php esc_html_e('sign requests', 'encypher-provenance'); ?>
                    </p>
                    <p class="description"><?php esc_html_e('Archive backfill is billed separately as a one-time operation. Your monthly publishing quota continues to apply to new content.', 'encypher-provenance'); ?></p>
                    <p class="encypher-archive-actions">
                        <a
                            href="<?php echo esc_url($this->build_archive_billing_url(0)); ?>"
                            id="encypher-buy-archive-backfill"
                            class="button button-secondary button-large"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            <?php esc_html_e('Buy Archive Backfill', 'encypher-provenance'); ?>
                        </a>
                        <span class="description"><?php esc_html_e('Opens billing with this archive estimate pre-filled.', 'encypher-provenance'); ?></span>
                    </p>
                    <?php else: ?>
                    <p class="encypher-plan-included">
                        <strong><?php esc_html_e('Archive backfill:', 'encypher-provenance'); ?></strong>
                        <?php esc_html_e('Included with your plan.', 'encypher-provenance'); ?>
                    </p>
                    <?php endif; ?>
                </div>

                <p class="submit">
                    <button type="button" id="encypher-start-bulk-mark" class="button button-primary button-large">
                        <?php esc_html_e('Start Bulk Marking', 'encypher-provenance'); ?>
                    </button>
                </p>
            </div>

            <div class="encypher-bulk-progress" style="display:none;">
                <h2><?php esc_html_e('Bulk Marking Progress', 'encypher-provenance'); ?></h2>

                <div class="encypher-progress-bar">
                    <div class="encypher-progress-fill" style="width:0%"></div>
                </div>

                <p class="encypher-progress-text">
                    <span id="encypher-progress-percentage">0%</span>
                    (<span id="encypher-progress-current">0</span> / <span id="encypher-progress-total">0</span>)
                </p>

                <p class="encypher-progress-status">
                    <strong><?php esc_html_e('Status:', 'encypher-provenance'); ?></strong>
                    <span id="encypher-progress-status-text"><?php esc_html_e('Initializing...', 'encypher-provenance'); ?></span>
                </p>

                <p class="encypher-progress-current-post">
                    <strong><?php esc_html_e('Current:', 'encypher-provenance'); ?></strong>
                    <span id="encypher-current-post-title">-</span>
                    <span class="description">(ID: <span id="encypher-current-post-id">-</span>)</span>
                </p>

                <div class="encypher-progress-stats">
                    <p>
                        <strong><?php esc_html_e('Successful:', 'encypher-provenance'); ?></strong>
                        <span id="encypher-success-count">0</span>
                    </p>
                    <p>
                        <strong><?php esc_html_e('Failed:', 'encypher-provenance'); ?></strong>
                        <span id="encypher-error-count">0</span>
                        <a href="#" id="encypher-view-errors" style="display:none;"><?php esc_html_e('View Errors', 'encypher-provenance'); ?></a>
                    </p>
                    <p>
                        <strong><?php esc_html_e('Elapsed Time:', 'encypher-provenance'); ?></strong>
                        <span id="encypher-elapsed-time">0s</span>
                    </p>
                </div>

                <div class="encypher-error-log" style="display:none;">
                    <h3><?php esc_html_e('Error Log', 'encypher-provenance'); ?></h3>
                    <ul id="encypher-error-list"></ul>
                </div>

                <p class="encypher-progress-actions">
                    <button type="button" id="encypher-pause-bulk-mark" class="button">
                        <?php esc_html_e('Pause', 'encypher-provenance'); ?>
                    </button>
                    <button type="button" id="encypher-cancel-bulk-mark" class="button">
                        <?php esc_html_e('Cancel', 'encypher-provenance'); ?>
                    </button>
                </p>
            </div>

            <div class="encypher-bulk-complete" style="display:none;">
                <h2><?php esc_html_e('Bulk Marking Complete!', 'encypher-provenance'); ?></h2>

                <div class="notice notice-success">
                    <p>
                        <strong><?php esc_html_e('Successfully marked:', 'encypher-provenance'); ?></strong>
                        <span id="encypher-final-success-count">0</span> <?php esc_html_e('posts', 'encypher-provenance'); ?>
                    </p>
                    <?php /* phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped */ ?>
                    <p id="encypher-final-errors" style="display:none;">
                        <strong><?php esc_html_e('Failed:', 'encypher-provenance'); ?></strong>
                        <span id="encypher-final-error-count">0</span> <?php esc_html_e('posts', 'encypher-provenance'); ?>
                    </p>
                </div>

                <p>
                    <button type="button" id="encypher-start-new-bulk" class="button button-primary">
                        <?php esc_html_e('Mark More Posts', 'encypher-provenance'); ?>
                    </button>
                </p>
            </div>
        </div>
        <?php
    }

    private function normalize_usage_snapshot(array $usage, string $tier): array
    {
        $default_limit = 'free' === $tier ? 1000 : -1;
        $api_calls = isset($usage['api_calls']) && is_array($usage['api_calls']) ? $usage['api_calls'] : $usage;

        $used = isset($api_calls['used']) ? max(0, (int) $api_calls['used']) : 0;
        $limit = isset($api_calls['limit']) ? (int) $api_calls['limit'] : $default_limit;
        $is_unlimited = isset($api_calls['is_unlimited']) ? (bool) $api_calls['is_unlimited'] : ($limit < 0);

        if ($is_unlimited) {
            return [
                'api_calls' => [
                    'used' => $used,
                    'limit' => -1,
                    'remaining' => -1,
                    'percentage_used' => 0.0,
                    'is_unlimited' => true,
                ],
            ];
        }

        if ($limit <= 0) {
            $limit = $default_limit > 0 ? $default_limit : 1000;
        }

        $remaining = isset($api_calls['remaining'])
            ? max(0, (int) $api_calls['remaining'])
            : max(0, $limit - $used);
        $percentage_used = isset($api_calls['percentage_used'])
            ? (float) $api_calls['percentage_used']
            : ($limit > 0 ? round(($used / $limit) * 100, 2) : 0.0);

        return [
            'api_calls' => [
                'used' => $used,
                'limit' => $limit,
                'remaining' => $remaining,
                'percentage_used' => min(100.0, max(0.0, $percentage_used)),
                'is_unlimited' => false,
            ],
        ];
    }

    private function render_usage_progress_bar(array $usage): void
    {
        $api_calls = isset($usage['api_calls']) && is_array($usage['api_calls']) ? $usage['api_calls'] : [];
        $used = isset($api_calls['used']) ? (int) $api_calls['used'] : 0;
        $limit = isset($api_calls['limit']) ? (int) $api_calls['limit'] : 1000;
        $remaining = isset($api_calls['remaining']) ? (int) $api_calls['remaining'] : max(0, $limit - $used);
        $percentage = isset($api_calls['percentage_used']) ? (float) $api_calls['percentage_used'] : 0.0;
        $is_unlimited = ! empty($api_calls['is_unlimited']) || $limit < 0;
        ?>
        <div class="encypher-bulk-usage-progress">
            <h2><?php esc_html_e('Monthly API call usage', 'encypher-provenance'); ?></h2>
            <?php if ($is_unlimited): ?>
                <p>
                    <strong><?php esc_html_e('Monthly API calls this month:', 'encypher-provenance'); ?></strong>
                    <?php echo esc_html(number_format_i18n($used)); ?>
                    <span class="description"><?php esc_html_e('Unlimited plan', 'encypher-provenance'); ?></span>
                </p>
            <?php else: ?>
                <p>
                    <strong><?php esc_html_e('Monthly API calls this month:', 'encypher-provenance'); ?></strong>
                    <?php echo esc_html(number_format_i18n($used)); ?> / <?php echo esc_html(number_format_i18n($limit)); ?>
                    (<?php echo esc_html(number_format_i18n((int) round($percentage))); ?>%)
                </p>
                <div class="encypher-usage-progress-track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="<?php echo esc_attr((int) round($percentage)); ?>">
                    <div class="encypher-usage-progress-fill" style="width: <?php echo esc_attr($percentage); ?>%;"></div>
                </div>
                <p class="description">
                    <strong><?php esc_html_e('API calls remaining this month:', 'encypher-provenance'); ?></strong>
                    <?php echo esc_html(number_format_i18n(max(0, $remaining))); ?>
                </p>
            <?php endif; ?>
        </div>
        <?php
    }

    private function get_archive_pricing(string $tier): array
    {
        return [
            'archive_price_per_document' => 0.01,
            'free_monthly_limit' => 1000,
            'free_overage_per_document' => 0.02,
            'archive_backfill_included' => in_array($tier, ['enterprise', 'strategic_partner'], true),
        ];
    }

    private function build_archive_billing_url(int $quantity): string
    {
        $params = [
            'addon' => 'bulk-archive-backfill',
            'source' => 'wordpress-plugin',
        ];

        if ($quantity > 0) {
            $params['quantity'] = $quantity;
        }

        return 'https://dashboard.encypherai.com/billing?' . http_build_query($params);
    }

    /**
     * Handle AJAX request to mark a batch of posts.
     */
    public function handle_bulk_mark_batch(): void
    {
        check_ajax_referer('encypher_bulk_mark', 'nonce');

        if (! current_user_can('manage_options')) {
            wp_send_json_error(['message' => __('Insufficient permissions.', 'encypher-provenance')]);
        }

        // Accept post_ids as JSON string to avoid max_input_vars limit
        $post_ids = [];
        if (isset($_POST['post_ids_json']) && is_string($_POST['post_ids_json'])) {
            $decoded = json_decode(stripslashes($_POST['post_ids_json']), true);
            if (is_array($decoded)) {
                $post_ids = array_map('intval', $decoded);
            }
        } elseif (isset($_POST['post_ids'])) {
            // Fallback for legacy array format
            $post_ids = array_map('intval', (array) $_POST['post_ids']);
        }

        if (empty($post_ids)) {
            wp_send_json_error(['message' => __('No post IDs provided.', 'encypher-provenance')]);
        }

        $results = [];
        $rest = new Rest();

        foreach ($post_ids as $post_id) {
            $post = get_post($post_id);

            if (! $post) {
                $results[] = [
                    'post_id' => $post_id,
                    'success' => false,
                    'error' => __('Post not found.', 'encypher-provenance')
                ];
                continue;
            }

            // Create a mock REST request
            $request = new \WP_REST_Request('POST', '/encypher-provenance/v1/sign');
            $request->set_param('post_id', $post_id);
            $request->set_param('metadata', []);

            try {
                $response = $rest->handle_sign_request($request);
            } catch (\Throwable $e) {
                $results[] = [
                    'post_id' => $post_id,
                    'post_title' => $post->post_title,
                    'success' => false,
                    'error' => $e->getMessage()
                ];
                continue;
            }

            if (is_wp_error($response)) {
                $results[] = [
                    'post_id' => $post_id,
                    'post_title' => $post->post_title,
                    'success' => false,
                    'error' => $response->get_error_message()
                ];
            } else {
                $results[] = [
                    'post_id' => $post_id,
                    'post_title' => $post->post_title,
                    'success' => true
                ];
            }
        }

        wp_send_json_success(['results' => $results]);
    }

    /**
     * Handle AJAX request to get bulk marking status.
     */
    public function handle_get_bulk_status(): void
    {
        check_ajax_referer('encypher_bulk_mark', 'nonce');

        if (! current_user_can('manage_options')) {
            wp_send_json_error(['message' => __('Insufficient permissions.', 'encypher-provenance')]);
        }

        $post_types = isset($_POST['post_types']) ? array_map('sanitize_text_field', (array) $_POST['post_types']) : ['post'];
        $status_filter = isset($_POST['status_filter']) ? sanitize_text_field($_POST['status_filter']) : 'unmarked';
        $date_range = isset($_POST['date_range']) ? sanitize_text_field($_POST['date_range']) : 'all';

        $args = [
            'post_type' => $post_types,
            'post_status' => 'publish',
            'posts_per_page' => -1,
            'fields' => 'ids',
            'no_found_rows' => true,
            'update_post_meta_cache' => false,
            'update_post_term_cache' => false,
        ];

        // Filter by marking status
        if ('unmarked' === $status_filter) {
            $args['meta_query'] = [
                'relation' => 'OR',
                [
                    'key' => '_encypher_marked',
                    'compare' => 'NOT EXISTS',
                ],
                [
                    'key' => '_encypher_marked',
                    'value' => '1',
                    'compare' => '!=',
                ],
            ];
        }

        // Filter by date range
        if ('all' !== $date_range) {
            $date_query = $this->get_date_query_for_range($date_range);
            if ($date_query) {
                $args['date_query'] = $date_query;
            }
        }

        $query = new WP_Query($args);
        $post_ids = $query->posts;

        wp_send_json_success([
            'total' => count($post_ids),
            'post_ids' => $post_ids,
        ]);
    }

    /**
     * Get date query array for a given range.
     */
    private function get_date_query_for_range(string $range): ?array
    {
        $date_query = null;

        switch ($range) {
            case 'last_month':
                $date_query = [
                    [
                        'after' => '1 month ago',
                        'inclusive' => true,
                    ],
                ];
                break;
            case 'last_3_months':
                $date_query = [
                    [
                        'after' => '3 months ago',
                        'inclusive' => true,
                    ],
                ];
                break;
            case 'last_6_months':
                $date_query = [
                    [
                        'after' => '6 months ago',
                        'inclusive' => true,
                    ],
                ];
                break;
            case 'last_year':
                $date_query = [
                    [
                        'after' => '1 year ago',
                        'inclusive' => true,
                    ],
                ];
                break;
        }

        return $date_query;
    }
}
