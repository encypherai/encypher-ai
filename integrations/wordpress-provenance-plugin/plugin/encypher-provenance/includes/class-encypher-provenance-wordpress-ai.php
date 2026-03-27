<?php
namespace EncypherProvenance;

if (! defined('ABSPATH')) {
    exit;
}

/**
 * WordPress/ai ("AI Experiments") compatibility layer.
 *
 * Detects the wordpress/ai plugin and hooks into its experiment lifecycle
 * to auto-sign AI-generated content with Encypher C2PA provenance.
 *
 * WordPress/ai filter hooks (from its source):
 *  - `wp_ai_experiment_title_generation_result`     → filter($content, $context)
 *  - `wp_ai_experiment_excerpt_generation_result`   → filter($content, $context)
 *  - `wp_ai_experiment_summary_generation_result`   → filter($content, $context)
 *  - `wp_ai_experiment_review_notes_result`         → filter($content, $context)
 *  - `wp_ai_experiment_alt_text_result`             → filter($content, $context)
 *  - `wp_abilities_api_init`                        → action()
 *
 * If WordPress/ai is NOT active, this class registers no hooks.
 */
class WordPress_AI_Compat
{
    private const OPTION_KEY = 'encypher_provenance_settings';
    private const WPAI_MAIN_CLASS = 'WP_AI\\Plugin'; // The main class of the wordpress/ai plugin

    public function register_hooks(): void
    {
        // Only activate if WordPress/ai is actually active
        add_action('plugins_loaded', [$this, 'maybe_hook_into_wordpress_ai'], 20);
    }

    public function maybe_hook_into_wordpress_ai(): void
    {
        if (!$this->is_wordpress_ai_active()) {
            return;
        }

        $settings = get_option(self::OPTION_KEY, []);
        $enabled = !empty($settings['wordpress_ai_enabled']);
        if (!$enabled) {
            return;
        }

        // Hook into WordPress/ai experiment outputs
        add_filter('wp_ai_experiment_title_generation_result', [$this, 'sign_ai_content'], 10, 2);
        add_filter('wp_ai_experiment_excerpt_generation_result', [$this, 'sign_ai_content'], 10, 2);
        add_filter('wp_ai_experiment_summary_generation_result', [$this, 'sign_ai_content'], 10, 2);
        add_filter('wp_ai_experiment_review_notes_result', [$this, 'sign_ai_content'], 10, 2);
        add_filter('wp_ai_experiment_alt_text_result', [$this, 'sign_ai_content'], 10, 2);

        // Hook into Abilities API init if available
        add_action('wp_abilities_api_init', [$this, 'on_abilities_api_init']);
    }

    /**
     * Check if the wordpress/ai plugin is active by looking for its main file or class.
     */
    public function is_wordpress_ai_active(): bool
    {
        // Check by plugin file
        if (function_exists('is_plugin_active') && is_plugin_active('wordpress-ai/plugin.php')) {
            return true;
        }
        // Check by class existence (more reliable across contexts)
        if (class_exists('WP_AI\\Plugin') || class_exists('WordPressAI\\Plugin') || class_exists('WP_AI_Experiments\\Plugin')) {
            return true;
        }
        // Check by known function from wordpress/ai
        if (function_exists('wp_abilities_api_init') || function_exists('wp_register_ability') || function_exists('wp_do_ability')) {
            return true;
        }
        return false;
    }

    /**
     * Sign AI-generated content with Encypher provenance.
     *
     * @param string $content The AI-generated content.
     * @param array  $context Context array from the experiment (may include post_id, model, provider, etc.)
     * @return string The signed content (with embedded Unicode watermark) or original on failure.
     */
    public function sign_ai_content(string $content, array $context = []): string
    {
        if (empty(trim($content))) {
            return $content;
        }

        $settings = get_option(self::OPTION_KEY, []);
        $api_base = rtrim($settings['api_base_url'] ?? 'https://api.encypher.com/api/v1', '/');
        $api_key  = $settings['api_key'] ?? '';

        if (empty($api_key)) {
            return $content;
        }

        // Build metadata from context
        $metadata = [
            'source' => 'wordpress-ai-experiment',
            'generator' => $context['model'] ?? $context['provider'] ?? 'wordpress/ai',
            'experiment' => $this->get_current_filter_name(),
            'post_id' => $context['post_id'] ?? null,
            'generated_at' => gmdate('c'),
        ];

        $body = [
            'text' => $content,
            'metadata' => array_filter($metadata),
        ];

        $response = wp_remote_post(
            $api_base . '/sign',
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
            $this->debug_log('sign_ai_content error: ' . $response->get_error_message());
            return $content;
        }

        $status = wp_remote_retrieve_response_code($response);
        if ($status < 200 || $status >= 300) {
            $this->debug_log('sign_ai_content non-200 status: ' . $status);
            return $content;
        }

        $data = json_decode(wp_remote_retrieve_body($response), true);
        $signed_text = $data['signed_text'] ?? $data['data']['signed_text'] ?? $data['text'] ?? null;

        if (!is_string($signed_text) || empty($signed_text)) {
            $this->debug_log('sign_ai_content: no signed_text in response');
            return $content;
        }

        // Record the signed experiment so the /wordpress-ai-status endpoint can surface it.
        $post_id = isset($context['post_id']) ? (int) $context['post_id'] : 0;
        if ($post_id > 0) {
            $this->record_signed_experiment($post_id, $metadata);
        }

        return $signed_text;
    }

    /**
     * Store a record of the signed experiment in post meta.
     * The /wordpress-ai-status REST endpoint reads this to build the provenance summary.
     *
     * @param int   $post_id  WordPress post ID.
     * @param array $metadata Experiment metadata used in the signing request.
     */
    private function record_signed_experiment(int $post_id, array $metadata): void
    {
        $existing = get_post_meta($post_id, '_encypher_wpai_experiments', true);
        if (!is_array($existing)) {
            $existing = [];
        }

        $experiment_name = $metadata['experiment'] ?? 'unknown';

        // Update or insert record for this experiment slug.
        $existing[$experiment_name] = [
            'name'       => $experiment_name,
            'generator'  => $metadata['generator'] ?? null,
            'signed_at'  => $metadata['generated_at'] ?? gmdate('c'),
        ];

        update_post_meta($post_id, '_encypher_wpai_experiments', $existing);
    }

    /**
     * Called when WordPress/ai Abilities API is initialised.
     * We register our abilities here as well (in case Epic 2 class is not loaded).
     */
    public function on_abilities_api_init(): void
    {
        // Abilities are registered by the dedicated ability classes (Epic 2).
        // This hook is a no-op here but allows future extension.
        do_action('encypher_abilities_api_ready');
    }

    private function get_current_filter_name(): string
    {
        return current_filter() ?: 'unknown';
    }

    private function debug_log(string $message): void
    {
        if (defined('WP_DEBUG') && WP_DEBUG) {
            error_log('Encypher WordPress/ai: ' . $message);
        }
    }
}
