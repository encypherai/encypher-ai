<?php
namespace EncypherProvenance;

if (! defined('ABSPATH')) {
    exit;
}

/**
 * Encypher Verify Ability for the WordPress Abilities API.
 *
 * Registers `encypher/verify` as a callable ability. Third-party plugins
 * and WordPress/ai experiments can call:
 *
 *   wp_do_ability('encypher/verify', ['text' => 'Content to verify'])
 *
 * Returns an array with provenance details on success, WP_Error on failure.
 * Note: verification does NOT require an API key (public endpoint).
 */
class Encypher_Verify_Ability
{
    private const OPTION_KEY = 'encypher_provenance_settings';

    public function get_name(): string
    {
        return 'encypher/verify';
    }

    public function get_label(): string
    {
        return __('Encypher: Verify Provenance', 'encypher-provenance');
    }

    public function get_description(): string
    {
        return __('Verify whether text content has valid Encypher C2PA provenance. Returns provenance metadata including the signing model, timestamp, and content hash. No API key required.', 'encypher-provenance');
    }

    /**
     * Verification is always available (no API key needed).
     */
    public function can_execute(): bool
    {
        return true;
    }

    /**
     * Execute the verify ability.
     *
     * @param array $args {
     *   @type string $text Required. The text to verify.
     * }
     * @return array|\WP_Error Provenance data array or WP_Error.
     */
    public function execute(array $args)
    {
        $text = $args['text'] ?? '';
        if (empty(trim($text))) {
            return new \WP_Error('encypher_verify_empty', __('Text is required to verify.', 'encypher-provenance'));
        }

        $settings = get_option(self::OPTION_KEY, []);
        $api_base = rtrim($settings['api_base_url'] ?? 'https://api.encypher.com/api/v1', '/');

        $response = wp_remote_post(
            $api_base . '/verify',
            [
                'headers' => ['Content-Type' => 'application/json'],
                'body'    => wp_json_encode(['text' => $text]),
                'timeout' => 15,
            ]
        );

        if (is_wp_error($response)) {
            return new \WP_Error('encypher_verify_request_failed', $response->get_error_message());
        }

        $status = wp_remote_retrieve_response_code($response);
        if ($status < 200 || $status >= 300) {
            $decoded = json_decode(wp_remote_retrieve_body($response), true);
            $message = isset($decoded['message']) ? $decoded['message'] : sprintf('HTTP %d', $status);
            return new \WP_Error('encypher_verify_api_error', $message);
        }

        $data = json_decode(wp_remote_retrieve_body($response), true);
        if (!is_array($data)) {
            return new \WP_Error('encypher_verify_invalid_response', __('Invalid API response.', 'encypher-provenance'));
        }

        return isset($data['data']) && is_array($data['data']) ? $data['data'] : $data;
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
