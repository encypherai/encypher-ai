<?php
namespace EncypherAssurance;

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

        wp_enqueue_script(
            'encypher-bulk-mark',
            ENCYPHER_ASSURANCE_PLUGIN_URL . 'assets/js/bulk-mark.js',
            ['jquery'],
            ENCYPHER_ASSURANCE_VERSION,
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
            ]
        );

        wp_enqueue_style(
            'encypher-bulk-mark-css',
            ENCYPHER_ASSURANCE_PLUGIN_URL . 'assets/css/bulk-mark.css',
            [],
            ENCYPHER_ASSURANCE_VERSION
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

        $settings = get_option('encypher_assurance_settings', []);
        $tier = $settings['tier'] ?? 'starter';
        $post_types = get_post_types(['public' => true], 'objects');
        
        ?>
        <div class="wrap encypher-bulk-mark-page">
            <h1><?php esc_html_e('Bulk Mark WordPress Archives', 'encypher-provenance'); ?></h1>
            
            <div class="encypher-bulk-intro">
                <p><?php esc_html_e('Programmatically mark existing WordPress content with C2PA-compliant invisible embeddings.', 'encypher-provenance'); ?></p>
            </div>

            <?php if ('starter' === $tier): ?>
            <div class="notice notice-info">
                <p>
                    <strong><?php esc_html_e('Free Tier Limit:', 'encypher-provenance'); ?></strong>
                    <?php esc_html_e('You can mark up to 100 posts per bulk operation.', 'encypher-provenance'); ?>
                    <a href="https://encypherai.com/pricing" target="_blank"><?php esc_html_e('Upgrade to Pro for unlimited marking', 'encypher-provenance'); ?></a>
                </p>
            </div>
            <?php endif; ?>

            <div class="encypher-bulk-form">
                <h2><?php esc_html_e('Select Content to Mark', 'encypher-provenance'); ?></h2>
                
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
                    <?php if ('starter' === $tier): ?>
                    <p class="encypher-tier-limit">
                        <strong><?php esc_html_e('Free tier limit:', 'encypher-provenance'); ?></strong>
                        <?php esc_html_e('100 posts', 'encypher-provenance'); ?>
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

    /**
     * Handle AJAX request to mark a batch of posts.
     */
    public function handle_bulk_mark_batch(): void
    {
        check_ajax_referer('encypher_bulk_mark', 'nonce');

        if (! current_user_can('manage_options')) {
            wp_send_json_error(['message' => __('Insufficient permissions.', 'encypher-provenance')]);
        }

        $post_ids = isset($_POST['post_ids']) ? array_map('intval', (array) $_POST['post_ids']) : [];
        
        if (empty($post_ids)) {
            wp_send_json_error(['message' => __('No post IDs provided.', 'encypher-provenance')]);
        }

        // Check tier limits
        $settings = get_option('encypher_assurance_settings', []);
        $tier = $settings['tier'] ?? 'starter';
        
        if ('starter' === $tier && count($post_ids) > 100) {
            wp_send_json_error([
                'message' => __('Free tier limit: 100 posts per bulk operation. Upgrade to Pro for unlimited marking.', 'encypher-provenance')
            ]);
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

            $response = $rest->handle_sign_request($request);

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
                    'success' => true,
                    'data' => $response->get_data()
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
