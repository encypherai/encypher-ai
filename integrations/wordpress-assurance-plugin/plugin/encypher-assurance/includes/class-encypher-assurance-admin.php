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
    public function register_hooks(): void
    {
        add_action('admin_menu', [$this, 'register_settings_page']);
        add_action('admin_init', [$this, 'register_settings']);
        add_action('enqueue_block_editor_assets', [$this, 'enqueue_block_editor_assets']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_classic_assets']);
        add_action('add_meta_boxes', [$this, 'register_classic_meta_box']);
        
        // Auto-mark on publish/update hooks
        add_action('publish_post', [$this, 'auto_mark_on_publish'], 10, 2);
        add_action('publish_page', [$this, 'auto_mark_on_publish'], 10, 2);
        add_action('post_updated', [$this, 'auto_mark_on_update'], 10, 3);
    }

    public function register_settings_page(): void
    {
        add_options_page(
            __('Encypher Assurance', 'encypher-assurance'),
            __('Encypher Assurance', 'encypher-assurance'),
            'manage_options',
            'encypher-assurance-settings',
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
                'tier' => 'free',
                'post_types' => ['post', 'page'],
            ],
        ]);

        add_settings_section(
            'encypher_assurance_main_section',
            __('API Configuration', 'encypher-assurance'),
            function () {
                echo '<p>' . esc_html__('Configure the Encypher backend connection for signing and verification.', 'encypher-assurance') . '</p>';
            },
            'encypher-assurance-settings'
        );

        add_settings_field(
            'encypher_assurance_api_base_url',
            __('API Base URL', 'encypher-assurance'),
            [$this, 'render_api_base_url_field'],
            'encypher-assurance-settings',
            'encypher_assurance_main_section'
        );

        add_settings_field(
            'encypher_assurance_api_key',
            __('API Key', 'encypher-assurance'),
            [$this, 'render_api_key_field'],
            'encypher-assurance-settings',
            'encypher_assurance_main_section'
        );

        add_settings_field(
            'encypher_assurance_auto_verify',
            __('Automatically verify content on render', 'encypher-assurance'),
            [$this, 'render_auto_verify_field'],
            'encypher-assurance-settings',
            'encypher_assurance_main_section'
        );
    }

    public function sanitize_settings(array $settings): array
    {
        $sanitized = [];
        $sanitized['api_base_url'] = isset($settings['api_base_url']) ? esc_url_raw(trim($settings['api_base_url'])) : 'https://api.encypherai.com/api/v1';
        $sanitized['api_base_url'] = rtrim($sanitized['api_base_url'], '/');
        $sanitized['api_key'] = isset($settings['api_key']) ? sanitize_text_field($settings['api_key']) : '';
        $sanitized['auto_verify'] = isset($settings['auto_verify']) ? (bool) $settings['auto_verify'] : false;
        $sanitized['auto_mark_on_publish'] = isset($settings['auto_mark_on_publish']) ? (bool) $settings['auto_mark_on_publish'] : true;
        $sanitized['auto_mark_on_update'] = isset($settings['auto_mark_on_update']) ? (bool) $settings['auto_mark_on_update'] : true;
        $sanitized['metadata_format'] = isset($settings['metadata_format']) && in_array($settings['metadata_format'], ['basic', 'c2pa'], true) ? $settings['metadata_format'] : 'c2pa';
        $sanitized['add_hard_binding'] = isset($settings['add_hard_binding']) ? (bool) $settings['add_hard_binding'] : true;
        $sanitized['tier'] = isset($settings['tier']) && in_array($settings['tier'], ['free', 'pro', 'enterprise'], true) ? $settings['tier'] : 'free';
        $sanitized['post_types'] = isset($settings['post_types']) && is_array($settings['post_types']) ? array_map('sanitize_text_field', $settings['post_types']) : ['post', 'page'];
        return $sanitized;
    }

    public function render_settings_page(): void
    {
        if (! current_user_can('manage_options')) {
            return;
        }

        ?>
        <div class="wrap">
            <h1><?php esc_html_e('Encypher Assurance Settings', 'encypher-assurance'); ?></h1>
            <form method="post" action="options.php">
                <?php
                settings_fields('encypher_assurance_settings_group');
                do_settings_sections('encypher-assurance-settings');
                submit_button(__('Save Changes', 'encypher-assurance'));
                ?>
            </form>
        </div>
        <?php
    }

    public function render_api_base_url_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $value = isset($options['api_base_url']) ? esc_url($options['api_base_url']) : '';
        ?>
        <input type="url" class="regular-text" name="encypher_assurance_settings[api_base_url]" value="<?php echo esc_attr($value); ?>" placeholder="https://api.encypherai.com/api/v1" required />
        <p class="description"><?php esc_html_e('Base URL for the Encypher Enterprise API (override this only when pointing at a self-hosted instance).', 'encypher-assurance'); ?></p>
        <?php
    }

    public function render_api_key_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $value = isset($options['api_key']) ? $options['api_key'] : '';
        ?>
        <input type="password" class="regular-text" name="encypher_assurance_settings[api_key]" value="<?php echo esc_attr($value); ?>" autocomplete="off" />
        <p class="description"><?php esc_html_e('Enterprise API keys authenticate requests using the Authorization Bearer scheme. Generate a free key from the Encypher dashboard.', 'encypher-assurance'); ?></p>
        <?php
    }

    public function render_auto_verify_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $checked = ! empty($options['auto_verify']);
        ?>
        <label>
            <input type="checkbox" name="encypher_assurance_settings[auto_verify]" value="1" <?php checked($checked); ?> />
            <?php esc_html_e('Verify signed content when rendering posts/pages.', 'encypher-assurance'); ?>
        </label>
        <?php
    }

    public function enqueue_block_editor_assets(): void
    {
        $asset_path = ENCYPHER_ASSURANCE_PLUGIN_URL . 'assets/js/editor-sidebar.js';
        wp_enqueue_script(
            'encypher-assurance-editor-sidebar',
            $asset_path,
            ['wp-plugins', 'wp-edit-post', 'wp-components', 'wp-element', 'wp-data', 'wp-api-fetch'],
            ENCYPHER_ASSURANCE_VERSION,
            true
        );

        $settings = get_option('encypher_assurance_settings', []);
        wp_localize_script(
            'encypher-assurance-editor-sidebar',
            'EncypherAssuranceConfig',
            [
                'restUrl' => esc_url_raw(rest_url('encypher-assurance/v1/')),
                'nonce' => wp_create_nonce('wp_rest'),
                'autoVerify' => ! empty($settings['auto_verify']),
            ]
        );

        wp_enqueue_style(
            'encypher-assurance-editor-css',
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
            'encypher-assurance-classic',
            ENCYPHER_ASSURANCE_PLUGIN_URL . 'assets/js/classic-meta-box.js',
            ['jquery'],
            ENCYPHER_ASSURANCE_VERSION,
            true
        );

        wp_localize_script(
            'encypher-assurance-classic',
            'EncypherAssuranceClassic',
            [
                'restUrl' => esc_url_raw(rest_url('encypher-assurance/v1/')),
                'nonce' => wp_create_nonce('wp_rest'),
            ]
        );
    }

    public function register_classic_meta_box(): void
    {
        add_meta_box(
            'encypher-assurance-meta-box',
            __('Encypher Assurance', 'encypher-assurance'),
            [$this, 'render_classic_meta_box'],
            ['post', 'page'],
            'side',
            'high'
        );
    }

    public function render_classic_meta_box($post): void
    {
        wp_nonce_field('encypher_assurance_meta_box', 'encypher_assurance_meta_box_nonce');
        $status = get_post_meta($post->ID, '_encypher_assurance_status', true);
        $document_id = get_post_meta($post->ID, '_encypher_assurance_document_id', true);
        $verification_url = get_post_meta($post->ID, '_encypher_assurance_verification_url', true);
        $total_sentences = (int) get_post_meta($post->ID, '_encypher_assurance_total_sentences', true);
        ?>
        <div class="encypher-assurance-classic">
            <p class="status-row">
                <strong><?php esc_html_e('Status:', 'encypher-assurance'); ?></strong>
                <span class="status-value"><?php echo esc_html($status ? $status : __('Not signed', 'encypher-assurance')); ?></span>
            </p>
            <p class="document-id-row">
                <strong><?php esc_html_e('Document ID:', 'encypher-assurance'); ?></strong>
                <span class="document-id-value">
                    <?php echo $document_id ? esc_html($document_id) : esc_html__('Not available', 'encypher-assurance'); ?>
                </span>
            </p>
            <p class="verification-link"<?php echo $verification_url ? '' : ' style="display:none;"'; ?>>
                <a href="<?php echo $verification_url ? esc_url($verification_url) : '#'; ?>" target="_blank" rel="noopener">
                    <?php esc_html_e('View provenance report', 'encypher-assurance'); ?>
                </a>
            </p>
            <p class="sentences-count"<?php echo $total_sentences ? '' : ' style="display:none;"'; ?>>
                <strong><?php esc_html_e('Sentences protected:', 'encypher-assurance'); ?></strong>
                <span class="sentences-value"><?php echo $total_sentences ? esc_html((string) $total_sentences) : '0'; ?></span>
            </p>
            <button type="button" class="button button-primary encypher-assurance-sign" data-post-id="<?php echo esc_attr($post->ID); ?>">
                <?php esc_html_e('Sign Content', 'encypher-assurance'); ?>
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
}
