<?php
namespace EncypherProvenance;

if (! defined('ABSPATH')) {
    exit;
}

/**
 * Encypher Sign Ability for the WordPress Abilities API.
 *
 * Registers `encypher/sign` as a callable ability. Third-party plugins
 * and WordPress/ai experiments can call:
 *
 *   wp_do_ability('encypher/sign', ['text' => 'Content to sign', 'metadata' => [...]])
 *
 * Returns the signed text string on success, WP_Error on failure.
 */
class Encypher_Sign_Ability
{
    private const OPTION_KEY = 'encypher_provenance_settings';

    public function get_name(): string
    {
        return 'encypher/sign';
    }

    public function get_label(): string
    {
        return __('Encypher: Sign Content', 'encypher-provenance');
    }

    public function get_description(): string
    {
        return __('Embed a C2PA-compatible cryptographic provenance signature into text content using the Encypher API. The signed text includes an invisible Unicode watermark that survives copy-paste.', 'encypher-provenance');
    }

    /**
     * Check if this ability can be executed (API key configured).
     */
    public function can_execute(): bool
    {
        $settings = get_option(self::OPTION_KEY, []);
        return !empty($settings['api_key']);
    }

    /**
     * Execute the sign ability.
     *
     * @param array $args {
     *   @type string $text     Required. The text to sign.
     *   @type array  $metadata Optional. Metadata to embed in the manifest.
     * }
     * @return string|\WP_Error Signed text or WP_Error.
     */
    public function execute(array $args)
    {
        $text = $args['text'] ?? '';
        if (empty(trim($text))) {
            return new \WP_Error('encypher_sign_empty', __('Text is required to sign.', 'encypher-provenance'));
        }

        if (!$this->can_execute()) {
            return new \WP_Error('encypher_no_api_key', __('Encypher API key not configured.', 'encypher-provenance'));
        }

        $settings = get_option(self::OPTION_KEY, []);
        $api_base = rtrim($settings['api_base_url'] ?? 'https://api.encypher.com/api/v1', '/');
        $api_key  = $settings['api_key'];

        $body = ['text' => $text];
        if (!empty($args['metadata']) && is_array($args['metadata'])) {
            $body['metadata'] = $args['metadata'];
        }

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
            return new \WP_Error('encypher_sign_request_failed', $response->get_error_message());
        }

        $status = wp_remote_retrieve_response_code($response);
        if ($status < 200 || $status >= 300) {
            $decoded = json_decode(wp_remote_retrieve_body($response), true);
            $message = isset($decoded['message']) ? $decoded['message'] : sprintf('HTTP %d', $status);
            return new \WP_Error('encypher_sign_api_error', $message);
        }

        $data        = json_decode(wp_remote_retrieve_body($response), true);
        $signed_text = $data['signed_text'] ?? $data['data']['signed_text'] ?? $data['text'] ?? null;

        if (!is_string($signed_text) || empty($signed_text)) {
            return new \WP_Error('encypher_sign_no_result', __('API returned no signed text.', 'encypher-provenance'));
        }

        return $signed_text;
    }

    /**
     * Register this ability with WordPress/ai Abilities API if available.
     */
    public function register(): void
    {
        if (function_exists('wp_register_ability')) {
            wp_register_ability($this->get_name(), [$this, 'execute'], [
                'label'       => $this->get_label(),
                'description' => $this->get_description(),
                'can_execute' => [$this, 'can_execute'],
            ]);
        }
    }
}
