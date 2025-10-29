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
}
