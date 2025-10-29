<?php
namespace EncypherAssurance;

use WP_Error;
use WP_REST_Request;
use WP_REST_Response;
use WP_REST_Server;

if (! defined('ABSPATH')) {
    exit;
}

/**
 * Registers custom REST endpoints for signing and verification actions.
 */
class Rest
{
    private bool $is_signing = false;

    public function register_hooks(): void
    {
        add_action('rest_api_init', [$this, 'register_routes']);
        add_action('save_post', [$this, 'mark_post_needs_verification'], 20, 3);
    }

    public function register_routes(): void
    {
        register_rest_route('encypher-assurance/v1', '/sign', [
            'methods' => WP_REST_Server::CREATABLE,
            'permission_callback' => [$this, 'can_edit_post'],
            'args' => [
                'post_id' => [
                    'required' => true,
                    'type' => 'integer',
                ],
                'metadata' => [
                    'required' => false,
                    'type' => 'object',
                ],
            ],
            'callback' => [$this, 'handle_sign_request'],
        ]);

        register_rest_route('encypher-assurance/v1', '/status', [
            'methods' => WP_REST_Server::READABLE,
            'permission_callback' => [$this, 'can_edit_post'],
            'args' => [
                'post_id' => [
                    'required' => true,
                    'type' => 'integer',
                ],
            ],
            'callback' => [$this, 'handle_status_request'],
        ]);

        register_rest_route('encypher-assurance/v1', '/verify', [
            'methods' => WP_REST_Server::CREATABLE,
            'permission_callback' => [$this, 'can_edit_post'],
            'args' => [
                'post_id' => [
                    'required' => true,
                    'type' => 'integer',
                ],
            ],
            'callback' => [$this, 'handle_verify_request'],
        ]);
    }

    public function can_edit_post(WP_REST_Request $request): bool
    {
        $post_id = (int) $request['post_id'];
        if (! $post_id) {
            return current_user_can('edit_posts');
        }

        return current_user_can('edit_post', $post_id);
    }

    public function handle_sign_request(WP_REST_Request $request)
    {
        $post_id = (int) $request->get_param('post_id');
        $post = get_post($post_id);

        if (! $post || 'trash' === $post->post_status) {
            return new WP_Error('invalid_post', __('Invalid post.', 'encypher-assurance'), ['status' => 400]);
        }

        $metadata = $request->get_param('metadata');
        if (! is_array($metadata)) {
            $metadata = [];
        }

        $payload = [
            'text' => $post->post_content,
        ];

        $document_title = isset($metadata['document_title']) ? sanitize_text_field((string) $metadata['document_title']) : $post->post_title;
        if ($document_title) {
            $payload['document_title'] = $document_title;
        }

        $fallback_url = get_permalink($post);
        $document_url = null;
        if (isset($metadata['document_url'])) {
            $document_url = esc_url_raw((string) $metadata['document_url']);
        } elseif (isset($metadata['canonical_url'])) {
            $document_url = esc_url_raw((string) $metadata['canonical_url']);
        } elseif ($fallback_url) {
            $document_url = esc_url_raw($fallback_url);
        }
        if ($document_url) {
            $payload['document_url'] = $document_url;
        }

        $allowed_types = ['article', 'legal_brief', 'contract', 'ai_output'];
        $document_type = $metadata['document_type'] ?? ($metadata['documentType'] ?? null);
        if (! is_string($document_type) || ! in_array($document_type, $allowed_types, true)) {
            $document_type = 'article';
        }
        $payload['document_type'] = $document_type;

        $response = $this->call_backend('/sign', $payload, true);
        if (is_wp_error($response)) {
            return $response;
        }

        $signed_text = $response['signed_text'] ?? null;
        if (! is_string($signed_text) || '' === $signed_text) {
            return new WP_Error('invalid_response', __('Unexpected response from signing endpoint.', 'encypher-assurance'), ['status' => 502]);
        }

        $document_id = isset($response['document_id']) ? sanitize_text_field((string) $response['document_id']) : '';
        $verification_url = isset($response['verification_url']) ? esc_url_raw((string) $response['verification_url']) : '';
        $total_sentences = isset($response['total_sentences']) ? (int) $response['total_sentences'] : 0;

        $this->is_signing = true;
        $updated = wp_update_post([
            'ID' => $post_id,
            'post_content' => $signed_text,
        ], true);
        $this->is_signing = false;

        if (is_wp_error($updated)) {
            return $updated;
        }

        update_post_meta($post_id, '_encypher_assurance_cached_content_hash', md5((string) $signed_text));
        update_post_meta($post_id, '_encypher_assurance_status', 'signed');
        update_post_meta($post_id, '_encypher_assurance_signature', $document_id);
        update_post_meta($post_id, '_encypher_assurance_document_id', $document_id);
        update_post_meta($post_id, '_encypher_assurance_verification_url', $verification_url);
        update_post_meta($post_id, '_encypher_assurance_total_sentences', $total_sentences);
        update_post_meta($post_id, '_encypher_assurance_last_signed', current_time('mysql'));
        delete_post_meta($post_id, '_encypher_assurance_verification');

        return new WP_REST_Response([
            'status' => 'signed',
            'document_id' => $document_id,
            'verification_url' => $verification_url,
            'signed_text' => $signed_text,
            'total_sentences' => $total_sentences,
        ]);
    }

    public function handle_status_request(WP_REST_Request $request)
    {
        $post_id = (int) $request->get_param('post_id');
        $status = get_post_meta($post_id, '_encypher_assurance_status', true);
        $signature = get_post_meta($post_id, '_encypher_assurance_signature', true);
        $document_id = get_post_meta($post_id, '_encypher_assurance_document_id', true);
        $verification_url = get_post_meta($post_id, '_encypher_assurance_verification_url', true);
        $total_sentences = (int) get_post_meta($post_id, '_encypher_assurance_total_sentences', true);
        $last_signed = get_post_meta($post_id, '_encypher_assurance_last_signed', true);
        $verification = get_post_meta($post_id, '_encypher_assurance_verification', true);

        return new WP_REST_Response([
            'status' => $status ?: 'not_signed',
            'signature' => $signature,
            'document_id' => $document_id,
            'verification_url' => $verification_url,
            'total_sentences' => $total_sentences,
            'last_signed' => $last_signed,
            'verification' => $verification,
        ]);
    }

    public function handle_verify_request(WP_REST_Request $request)
    {
        $post_id = (int) $request->get_param('post_id');
        $post = get_post($post_id);
        if (! $post) {
            return new WP_Error('invalid_post', __('Invalid post.', 'encypher-assurance'), ['status' => 400]);
        }

        $payload = [
            'text' => $post->post_content,
        ];

        $response = $this->call_backend('/verify', $payload, false);
        if (is_wp_error($response)) {
            return $response;
        }

        update_post_meta($post_id, '_encypher_assurance_verification', $response);
        update_post_meta($post_id, '_encypher_assurance_status', $this->derive_status_from_verification($response));

        return new WP_REST_Response($response);
    }

    public function mark_post_needs_verification($post_id, $post, $update): void
    {
        if (wp_is_post_revision($post_id) || 'auto-draft' === $post->post_status) {
            return;
        }

        if ($this->is_signing) {
            update_post_meta($post_id, '_encypher_assurance_cached_content_hash', md5((string) $post->post_content));
            return;
        }

        if ($update) {
            // If content changes manually, mark status stale.
            $previous_content = get_post_meta($post_id, '_encypher_assurance_cached_content_hash', true);
            $current_hash = md5((string) $post->post_content);
            if ($previous_content && $previous_content !== $current_hash) {
                update_post_meta($post_id, '_encypher_assurance_status', 'modified');
                delete_post_meta($post_id, '_encypher_assurance_verification');
            }
            update_post_meta($post_id, '_encypher_assurance_cached_content_hash', $current_hash);
        }
    }

    private function derive_status_from_verification(array $response): string
    {
        if (! empty($response['is_valid'])) {
            return 'verified';
        }

        if (isset($response['tampered']) && $response['tampered']) {
            return 'tampered';
        }

        return 'signed';
    }

    /**
     * Perform HTTP request to backend and decode JSON response.
     */
    private function call_backend(string $path, array $body, bool $require_auth)
    {
        $settings = get_option('encypher_assurance_settings', []);
        $base_url = isset($settings['api_base_url']) ? rtrim($settings['api_base_url'], '/') : '';
        if (! $base_url) {
            return new WP_Error('missing_configuration', __('Please configure the Encypher API base URL.', 'encypher-assurance'), ['status' => 400]);
        }

        $url = $base_url . $path;
        $headers = [
            'Content-Type' => 'application/json',
            'Accept' => 'application/json',
        ];

        $api_key = isset($settings['api_key']) ? trim((string) $settings['api_key']) : '';
        if ($api_key) {
            $headers['Authorization'] = 'Bearer ' . sanitize_text_field($api_key);
        } elseif ($require_auth) {
            return new WP_Error('missing_api_key', __('Please configure an Encypher API key before signing.', 'encypher-assurance'), ['status' => 401]);
        }

        $args = [
            'headers' => $headers,
            'body' => wp_json_encode($body),
            'timeout' => 20,
        ];

        $response = wp_remote_post($url, $args);
        if (is_wp_error($response)) {
            return new WP_Error('http_error', $response->get_error_message(), ['status' => 500]);
        }

        $status_code = wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);
        $decoded = json_decode($body, true);

        if (null === $decoded && '' !== trim((string) $body)) {
            return new WP_Error('invalid_json', __('Unable to parse backend response.', 'encypher-assurance'), ['status' => 502]);
        }

        if ($status_code >= 400) {
            $message = '';
            $code = 'backend_error';
            if (is_array($decoded)) {
                if (isset($decoded['error']['message'])) {
                    $message = (string) $decoded['error']['message'];
                } elseif (isset($decoded['message'])) {
                    $message = (string) $decoded['message'];
                } elseif (isset($decoded['detail'])) {
                    $message = (string) $decoded['detail'];
                }
                if (isset($decoded['error']['code'])) {
                    $code = (string) $decoded['error']['code'];
                }
            }
            if (! $message) {
                $message = $body;
            }
            return new WP_Error($code, sprintf(__('Backend responded with status %d: %s', 'encypher-assurance'), $status_code, $message), ['status' => $status_code]);
        }

        if (is_array($decoded) && array_key_exists('success', $decoded) && true !== $decoded['success']) {
            $message = isset($decoded['error']['message']) ? (string) $decoded['error']['message'] : (isset($decoded['message']) ? (string) $decoded['message'] : __('The Encypher API rejected the request.', 'encypher-assurance'));
            $code = isset($decoded['error']['code']) ? (string) $decoded['error']['code'] : 'api_error';
            $error_status = isset($decoded['error']['status']) ? (int) $decoded['error']['status'] : 400;
            return new WP_Error($code, $message, ['status' => $error_status]);
        }

        return is_array($decoded) ? $decoded : [];
    }
}
