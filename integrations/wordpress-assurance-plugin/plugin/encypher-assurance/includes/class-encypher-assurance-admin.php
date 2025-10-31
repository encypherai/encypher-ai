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

        // C2PA Settings Section
        add_settings_section(
            'encypher_assurance_c2pa_section',
            __('C2PA Settings', 'encypher-assurance'),
            function () {
                echo '<p>' . esc_html__('Configure C2PA-compliant text authentication options.', 'encypher-assurance') . '</p>';
            },
            'encypher-assurance-settings'
        );

        add_settings_field(
            'encypher_assurance_auto_mark_on_publish',
            __('Auto-mark on publish', 'encypher-assurance'),
            [$this, 'render_auto_mark_on_publish_field'],
            'encypher-assurance-settings',
            'encypher_assurance_c2pa_section'
        );

        add_settings_field(
            'encypher_assurance_auto_mark_on_update',
            __('Auto-mark on update', 'encypher-assurance'),
            [$this, 'render_auto_mark_on_update_field'],
            'encypher-assurance-settings',
            'encypher_assurance_c2pa_section'
        );

        add_settings_field(
            'encypher_assurance_metadata_format',
            __('Metadata format', 'encypher-assurance'),
            [$this, 'render_metadata_format_field'],
            'encypher-assurance-settings',
            'encypher_assurance_c2pa_section'
        );

        add_settings_field(
            'encypher_assurance_add_hard_binding',
            __('Hard binding', 'encypher-assurance'),
            [$this, 'render_add_hard_binding_field'],
            'encypher-assurance-settings',
            'encypher_assurance_c2pa_section'
        );

        add_settings_field(
            'encypher_assurance_post_types',
            __('Post types to auto-mark', 'encypher-assurance'),
            [$this, 'render_post_types_field'],
            'encypher-assurance-settings',
            'encypher_assurance_c2pa_section'
        );

        // Display Settings Section
        add_settings_section(
            'encypher_assurance_display_section',
            __('Display Settings', 'encypher-assurance'),
            function () {
                echo '<p>' . esc_html__('Configure how C2PA badges appear on your site.', 'encypher-assurance') . '</p>';
            },
            'encypher-assurance-settings'
        );

        add_settings_field(
            'encypher_assurance_show_badge',
            __('Show C2PA badge', 'encypher-assurance'),
            [$this, 'render_show_badge_field'],
            'encypher-assurance-settings',
            'encypher_assurance_display_section'
        );

        add_settings_field(
            'encypher_assurance_badge_position',
            __('Badge position', 'encypher-assurance'),
            [$this, 'render_badge_position_field'],
            'encypher-assurance-settings',
            'encypher_assurance_display_section'
        );

        // Tier Settings Section
        add_settings_section(
            'encypher_assurance_tier_section',
            __('Tier & Subscription', 'encypher-assurance'),
            function () {
                echo '<p>' . esc_html__('Your current subscription tier and upgrade options.', 'encypher-assurance') . '</p>';
            },
            'encypher-assurance-settings'
        );

        add_settings_field(
            'encypher_assurance_tier',
            __('Current tier', 'encypher-assurance'),
            [$this, 'render_tier_field'],
            'encypher-assurance-settings',
            'encypher_assurance_tier_section'
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
        $sanitized['show_badge'] = isset($settings['show_badge']) ? (bool) $settings['show_badge'] : true; // Default ON
        $sanitized['badge_position'] = isset($settings['badge_position']) && in_array($settings['badge_position'], ['top', 'bottom', 'bottom-right'], true) ? $settings['badge_position'] : 'bottom-right';
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
            <?php esc_html_e('Automatically embed C2PA manifests when publishing new posts', 'encypher-assurance'); ?>
        </label>
        <p class="description"><?php esc_html_e('Recommended for all users. Ensures every published post has cryptographic proof of origin.', 'encypher-assurance'); ?></p>
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
            <?php esc_html_e('Re-sign manifests when content is updated', 'encypher-assurance'); ?>
        </label>
        <p class="description"><?php esc_html_e('Preserves provenance chain through ingredient references. Uses c2pa.edited action.', 'encypher-assurance'); ?></p>
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
            <option value="c2pa" <?php selected($value, 'c2pa'); ?>><?php esc_html_e('C2PA (Recommended)', 'encypher-assurance'); ?></option>
            <option value="basic" <?php selected($value, 'basic'); ?>><?php esc_html_e('Basic (Minimal)', 'encypher-assurance'); ?></option>
        </select>
        <p class="description">
            <?php esc_html_e('C2PA format includes full manifest with assertions. Basic format is minimal for testing.', 'encypher-assurance'); ?>
            <a href="https://c2pa.org" target="_blank"><?php esc_html_e('Learn about C2PA', 'encypher-assurance'); ?></a>
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
            <?php esc_html_e('Include c2pa.hash.data assertion', 'encypher-assurance'); ?>
        </label>
        <p class="description"><?php esc_html_e('Provides content hash for tamper detection. Recommended for maximum security.', 'encypher-assurance'); ?></p>
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
        <p class="description"><?php esc_html_e('Select which post types should be automatically marked with C2PA manifests.', 'encypher-assurance'); ?></p>
        <?php
    }

    /**
     * Render tier field.
     */
    public function render_tier_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'free';
        
        $tier_names = [
            'free' => __('Free', 'encypher-assurance'),
            'pro' => __('Pro', 'encypher-assurance'),
            'enterprise' => __('Enterprise', 'encypher-assurance'),
        ];
        
        $tier_features = [
            'free' => [
                __('Auto-mark on publish', 'encypher-assurance'),
                __('Manual marking', 'encypher-assurance'),
                __('Bulk mark up to 100 posts', 'encypher-assurance'),
                __('Shared Encypher signature', 'encypher-assurance'),
            ],
            'pro' => [
                __('All Free features', 'encypher-assurance'),
                __('Custom signature (your organization)', 'encypher-assurance'),
                __('Unlimited bulk marking', 'encypher-assurance'),
                __('Advanced analytics', 'encypher-assurance'),
                __('Priority support', 'encypher-assurance'),
            ],
            'enterprise' => [
                __('All Pro features', 'encypher-assurance'),
                __('Multi-site support', 'encypher-assurance'),
                __('Advanced key management', 'encypher-assurance'),
                __('Custom integrations', 'encypher-assurance'),
                __('SLA and dedicated support', 'encypher-assurance'),
            ],
        ];
        ?>
        <div class="encypher-tier-display">
            <p style="font-size:18px; font-weight:bold; color:#1B2F50;">
                <?php echo esc_html($tier_names[$tier]); ?>
            </p>
            
            <div style="background:#f0f6fc; padding:15px; border-left:4px solid #2A87C4; margin:10px 0;">
                <strong><?php esc_html_e('Features:', 'encypher-assurance'); ?></strong>
                <ul style="margin:10px 0;">
                    <?php foreach ($tier_features[$tier] as $feature): ?>
                        <li><?php echo esc_html($feature); ?></li>
                    <?php endforeach; ?>
                </ul>
            </div>
            
            <?php if ('free' === $tier): ?>
                <p>
                    <a href="https://encypherai.com/pricing" class="button button-primary" target="_blank">
                        <?php esc_html_e('Upgrade to Pro - $99/month', 'encypher-assurance'); ?>
                    </a>
                </p>
            <?php elseif ('pro' === $tier): ?>
                <p>
                    <a href="https://encypherai.com/enterprise" class="button button-primary" target="_blank">
                        <?php esc_html_e('Upgrade to Enterprise', 'encypher-assurance'); ?>
                    </a>
                </p>
            <?php endif; ?>
            
            <input type="hidden" name="encypher_assurance_settings[tier]" value="<?php echo esc_attr($tier); ?>" />
        </div>
        <?php
    }

    /**
     * Render show badge field.
     */
    public function render_show_badge_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $checked = isset($options['show_badge']) ? (bool) $options['show_badge'] : false;
        ?>
        <label>
            <input type="checkbox" name="encypher_assurance_settings[show_badge]" value="1" <?php checked($checked); ?> />
            <?php esc_html_e('Display C2PA badge on marked posts', 'encypher-assurance'); ?>
        </label>
        <p class="description"><?php esc_html_e('Shows a badge indicating the post is C2PA protected. Helps readers verify authenticity.', 'encypher-assurance'); ?></p>
        <?php
    }

    /**
     * Render badge position field.
     */
    public function render_badge_position_field(): void
    {
        $options = get_option('encypher_assurance_settings', []);
        $tier = isset($options['tier']) ? $options['tier'] : 'free';
        $value = isset($options['badge_position']) ? $options['badge_position'] : 'bottom-right';
        
        // Free tier: always bottom-right
        if ('free' === $tier) {
            ?>
            <p>
                <strong><?php esc_html_e('Bottom-right corner (floating)', 'encypher-assurance'); ?></strong>
                <input type="hidden" name="encypher_assurance_settings[badge_position]" value="bottom-right" />
            </p>
            <p class="description">
                <?php esc_html_e('Free tier displays the badge in the bottom-right corner.', 'encypher-assurance'); ?>
                <a href="https://encypherai.com/pricing" target="_blank"><?php esc_html_e('Upgrade to Pro', 'encypher-assurance'); ?></a>
                <?php esc_html_e('for customizable positioning.', 'encypher-assurance'); ?>
            </p>
            <?php
        } else {
            // Pro/Enterprise: customizable
            ?>
            <select name="encypher_assurance_settings[badge_position]">
                <option value="bottom-right" <?php selected($value, 'bottom-right'); ?>><?php esc_html_e('Bottom-right corner (floating)', 'encypher-assurance'); ?></option>
                <option value="top" <?php selected($value, 'top'); ?>><?php esc_html_e('Top of post', 'encypher-assurance'); ?></option>
                <option value="bottom" <?php selected($value, 'bottom'); ?>><?php esc_html_e('Bottom of post', 'encypher-assurance'); ?></option>
            </select>
            <p class="description"><?php esc_html_e('Choose where the C2PA badge appears on posts.', 'encypher-assurance'); ?></p>
            <?php
        }
    }
}
