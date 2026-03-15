<?php
namespace EncypherProvenance;

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
    private ?HtmlParser $parser = null;

    public function __construct()
    {
        $this->parser = new HtmlParser();
    }

    private function get_parser(): HtmlParser
    {
        if ($this->parser === null) {
            $this->parser = new HtmlParser();
        }
        return $this->parser;
    }

    private function debug_log(string $message): void
    {
        if (defined('WP_DEBUG') && WP_DEBUG) {
            error_log('Encypher: ' . $message);
        }
    }

    public function register_hooks(): void
    {
        add_action('rest_api_init', [$this, 'register_routes']);
        add_action('save_post', [$this, 'mark_post_needs_verification'], 20, 3);
        add_action('transition_post_status', [$this, 'auto_sign_on_publish'], 10, 3);
        add_action('save_post', [$this, 'auto_sign_on_update'], 30, 3); // Higher priority to run after mark_post_needs_verification
        add_action('admin_notices', [$this, 'render_sign_error_notice']);
        add_action('wp_ajax_encypher_dismiss_sign_error', [$this, 'ajax_dismiss_sign_error']);
        add_action('send_headers', [$this, 'inject_image_provenance_header']);
    }

    public function handle_public_extract_request(WP_REST_Request $request)
    {
        $text = $request->get_param('text');
        if (! is_string($text) || '' === trim($text)) {
            return new WP_Error('invalid_text', __('A text payload containing the embedded manifesto is required.', 'encypher-provenance'), ['status' => 400]);
        }

        // Enforce a hard limit to prevent abuse (default 200k chars)
        $max_length = apply_filters('encypher_public_extract_max_length', 200000);
        if ($max_length && strlen($text) > $max_length) {
            return new WP_Error(
                'text_too_large',
                sprintf(
                    /* translators: %d: max characters */
                    __('Text exceeds the maximum length of %d characters.', 'encypher-provenance'),
                    $max_length
                ),
                ['status' => 413]
            );
        }

        $payload = [
            'text' => $text,
        ];

        $response = $this->call_backend('/verify', $payload, false);
        if (is_wp_error($response)) {
            return $response;
        }

        return new WP_REST_Response($response);
    }

    public function register_routes(): void
    {
        register_rest_route('encypher-provenance/v1', '/sign', [
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

        register_rest_route('encypher-provenance/v1', '/status', [
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

        register_rest_route('encypher-provenance/v1', '/verify', [
            'methods' => WP_REST_Server::CREATABLE,
            'permission_callback' => '__return_true', // Public endpoint for frontend verification
            'args' => [
                'post_id' => [
                    'required' => true,
                    'type' => 'integer',
                ],
            ],
            'callback' => [$this, 'handle_verify_request'],
        ]);

        register_rest_route('encypher-provenance/v1', '/provenance', [
            'methods' => WP_REST_Server::READABLE,
            'permission_callback' => '__return_true', // Public endpoint
            'args' => [
                'post_id' => [
                    'required' => false,
                    'type' => 'integer',
                ],
                'instance_id' => [
                    'required' => false,
                    'type' => 'string',
                ],
            ],
            'callback' => [$this, 'handle_provenance_request'],
        ]);

        register_rest_route('encypher-provenance/v1', '/wordpress-ai-status', [
            'methods' => WP_REST_Server::READABLE,
            'permission_callback' => [$this, 'can_edit_post'],
            'args' => [
                'post_id' => [
                    'required' => true,
                    'type' => 'integer',
                ],
            ],
            'callback' => [$this, 'handle_wordpress_ai_status_request'],
        ]);

        register_rest_route('encypher-provenance/v1', '/extract', [
            'methods' => WP_REST_Server::CREATABLE,
            'permission_callback' => '__return_true', // Public endpoint
            'args' => [
                'text' => [
                    'required' => true,
                    'type' => 'string',
                ],
            ],
            'callback' => [$this, 'handle_public_extract_request'],
        ]);

        register_rest_route('encypher-provenance/v1', '/test-connection', [
            'methods' => WP_REST_Server::CREATABLE,
            'permission_callback' => function() {
                return current_user_can('manage_options');
            },
            'args' => [
                'api_base_url' => [
                    'type' => 'string',
                    'required' => false,
                    'sanitize_callback' => 'sanitize_text_field',
                ],
                'api_key' => [
                    'type' => 'string',
                    'required' => false,
                    'sanitize_callback' => 'sanitize_text_field',
                ],
            ],
            'callback' => [$this, 'handle_test_connection_request'],
        ]);

        register_rest_route('encypher-provenance/v1', '/quick-connect', [
            'methods' => WP_REST_Server::CREATABLE,
            'permission_callback' => function () {
                return current_user_can('manage_options');
            },
            'args' => [
                'api_base_url' => [
                    'type' => 'string',
                    'required' => true,
                    'sanitize_callback' => 'sanitize_text_field',
                ],
                'api_key' => [
                    'type' => 'string',
                    'required' => true,
                    'sanitize_callback' => 'sanitize_text_field',
                ],
            ],
            'callback' => [$this, 'handle_quick_connect_request'],
        ]);

        register_rest_route('encypher-provenance/v1', '/connect/start', [
            'methods' => WP_REST_Server::CREATABLE,
            'permission_callback' => function () {
                return current_user_can('manage_options');
            },
            'args' => [
                'email' => [
                    'type' => 'string',
                    'required' => true,
                    'sanitize_callback' => 'sanitize_email',
                ],
                'api_base_url' => [
                    'type' => 'string',
                    'required' => false,
                    'sanitize_callback' => 'sanitize_text_field',
                ],
            ],
            'callback' => [$this, 'handle_connect_start_request'],
        ]);

        register_rest_route('encypher-provenance/v1', '/connect/poll', [
            'methods' => WP_REST_Server::READABLE,
            'permission_callback' => function () {
                return current_user_can('manage_options');
            },
            'callback' => [$this, 'handle_connect_poll_request'],
        ]);

        register_rest_route('encypher-provenance/v1', '/payment-status', [
            'methods' => WP_REST_Server::READABLE,
            'permission_callback' => function () {
                return current_user_can('manage_options');
            },
            'callback' => [$this, 'handle_payment_status'],
        ]);

        register_rest_route('encypher-provenance/v1', '/payment-setup', [
            'methods' => WP_REST_Server::CREATABLE,
            'permission_callback' => function () {
                return current_user_can('manage_options');
            },
            'callback' => [$this, 'handle_payment_setup'],
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
            return new WP_Error('invalid_post', __('Invalid post.', 'encypher-provenance'), ['status' => 400]);
        }

        // Only allow signing of published posts (not drafts, pending, etc.)
        if ('publish' !== $post->post_status) {
            return new WP_Error(
                'invalid_post_status',
                __('Only published posts can be signed with C2PA. Please publish the post first.', 'encypher-provenance'),
                ['status' => 400]
            );
        }

        $metadata = $request->get_param('metadata');
        if (! is_array($metadata)) {
            $metadata = [];
        }

        // Get settings for C2PA configuration
        $settings = get_option('encypher_provenance_settings', []);
        $metadata_format = $settings['metadata_format'] ?? 'c2pa';
        $add_hard_binding = $settings['add_hard_binding'] ?? true;

        // Always strip invisible provenance markers before re-signing.
        // Some historical payloads contain sentence-level VS markers without a
        // full C2PA wrapper magic sequence. If we only strip when wrapper magic
        // is detected, those invisible markers leak back into the next /sign
        // request and can break HTML re-embedding.
        $clean_content = $this->strip_c2pa_embeddings($post->post_content);
        if ($clean_content !== $post->post_content) {
            $this->debug_log(sprintf(
                'Post %d contained existing invisible provenance markers. Stripped before re-signing.',
                $post_id
            ));
        }

        // Repair WordPress block comments that may have been corrupted by
        // VS char stripping. Previous signings could embed VS chars adjacent
        // to block comment delimiters; stripping them leaves stray spaces
        // (e.g. "<!-- /wp :paragraph -->" instead of "<!-- /wp:paragraph -->")
        // which breaks Gutenberg's block parser.
        $clean_content = $this->sanitize_wp_block_comments($clean_content);

        // Verify wrapper stripping was successful.
        $verify_clean = $this->detect_c2pa_embeddings($clean_content);
        if ($verify_clean['count'] > 0) {
            return new WP_Error(
                'embedding_strip_failed',
                __('Failed to strip existing C2PA embeddings. Please contact support.', 'encypher-provenance'),
                ['status' => 500]
            );
        }

        // Determine action type (c2pa.created or c2pa.edited)
        $action_type = get_post_meta($post_id, '_encypher_action_type', true);
        if (!$action_type) {
            $is_marked = get_post_meta($post_id, '_encypher_marked', true);
            $action_type = $is_marked ? 'c2pa.edited' : 'c2pa.created';
        }

        // Get previous instance_id for edit provenance chain
        $previous_instance_id = null;
        if ($action_type === 'c2pa.edited') {
            $previous_instance_id = get_post_meta($post_id, '_encypher_provenance_instance_id', true);
            if ($previous_instance_id) {
                $this->debug_log(sprintf(
                    'Post %d is being edited. Previous instance_id: %s',
                    $post_id,
                    $previous_instance_id
                ));
            }
        }

        // Get tier from settings (default to free)
        $tier = isset($settings['tier']) ? $settings['tier'] : 'free';

        $is_free = ($tier === 'free');
        $organization_name = ! empty($settings['organization_name']) ? sanitize_text_field((string) $settings['organization_name']) : '';
        $signing_mode = isset($settings['signing_mode']) ? $settings['signing_mode'] : 'managed';
        if ($is_free) {
            $signing_mode = 'managed';
        }
        $signing_profile_id = '';
        if ('byok' === $signing_mode && ! empty($settings['signing_profile_id'])) {
            $signing_profile_id = sanitize_text_field((string) $settings['signing_profile_id']);
        }

        // Generate unique document_id per signing instance to avoid collisions on re-signing
        // Format: wp_post_{post_id}_v{timestamp}_{random}
        $unique_document_id = sprintf(
            'wp_post_%d_v%d_%s',
            $post_id,
            time(),
            substr(md5(uniqid((string) $post_id, true)), 0, 8)
        );

        // Extract plain text from HTML for signing.
        // WordPress post_content contains block comments (<!-- wp:paragraph -->)
        // and HTML tags that confuse the sentence segmenter, inflating the
        // segment count.  We sign the plain text and embed markers back into
        // the HTML afterwards (same pattern as encypher-cms-signing-kit).
        $extracted_text = $this->extract_text_from_html($clean_content);
        if ('' === trim($extracted_text)) {
            return new WP_Error(
                'empty_content',
                __('No text content found in the post to sign.', 'encypher-provenance'),
                ['status' => 400]
            );
        }

        $this->debug_log(sprintf(
            'Post %d extracted %d chars of plain text from %d chars of HTML',
            $post_id,
            strlen($extracted_text),
            strlen($clean_content)
        ));

        // Build unified /sign request with tier-gated options
        // Features are automatically gated server-side based on API key tier
        $payload = [
            'text' => $extracted_text,
            'document_id' => $unique_document_id,
            'document_title' => $post->post_title,
            'document_url' => get_permalink($post),
            'metadata' => [
                'author' => get_the_author_meta('display_name', $post->post_author),
                'published_at' => $post->post_date,
                'wordpress_post_id' => $post_id,
                'tier' => $tier,
                'organization_name' => $organization_name,
                'signing_mode' => $signing_mode,
            ],
            'options' => [
                'document_type' => 'article',
                'claim_generator' => 'WordPress/Encypher Plugin v' . ENCYPHER_PROVENANCE_VERSION,
                'action' => $action_type,
                'manifest_mode' => 'micro',
                'ecc' => true,
                'embed_c2pa' => true,
                'segmentation_level' => 'sentence',
                'index_for_attribution' => true,
                'return_embedding_plan' => true,
            ],
        ];

        // Add previous_instance_id for edit provenance chain
        if ($previous_instance_id) {
            $payload['options']['previous_instance_id'] = $previous_instance_id;
        }

        // All tiers get sentence-level segmentation and attribution indexing
        // (TEAM_166 freemium model — no feature gating needed)

        // Add license info if provided
        if (isset($metadata['license_type'])) {
            $payload['options']['license'] = [
                'type' => sanitize_text_field($metadata['license_type']),
                'url' => isset($metadata['license_url']) ? esc_url_raw($metadata['license_url']) : '',
            ];
        }

        // Use unified /sign endpoint - features gated by tier server-side
        $response = $this->call_backend('/sign', $payload, true);
        if (is_wp_error($response)) {
            return $response;
        }

        // Handle new unified response format: { success, data: { document: {...} }, meta: {...} }
        // Also support legacy format for backward compatibility
        $result = $response;
        if (isset($response['data']['document'])) {
            $result = $response['data']['document'];
        } elseif (isset($response['data'])) {
            $result = $response['data'];
        }

        // Normalize fields that may be returned at response.data level instead of
        // nested response.data.document in some backend builds.
        if (!isset($result['embedding_plan']) && isset($response['data']['embedding_plan']) && is_array($response['data']['embedding_plan'])) {
            $result['embedding_plan'] = $response['data']['embedding_plan'];
        }
        if (!isset($result['signed_text']) && isset($response['data']['signed_text']) && is_string($response['data']['signed_text'])) {
            $result['signed_text'] = $response['data']['signed_text'];
        }
        if (!isset($result['embedded_content']) && isset($response['data']['embedded_content']) && is_string($response['data']['embedded_content'])) {
            $result['embedded_content'] = $response['data']['embedded_content'];
        }

        // Prefer reconstructing signed text from embedding_plan (format-preserving),
        // then fall back to signed_text/embedded_content for compatibility.
        $signed_text = $this->resolve_signed_text_with_embedding_plan($result, $extracted_text);
        if (! is_string($signed_text) || '' === $signed_text) {
            return new WP_Error('invalid_response', __('Unexpected response from Enterprise API.', 'encypher-provenance'), ['status' => 502]);
        }

        $final_check = $this->detect_c2pa_embeddings($signed_text);
        if ($final_check['count'] < 1) {
            $this->debug_log(sprintf(
                'C2PA compliance violation! Expected at least 1 wrapper, found %d in post %d',
                $final_check['count'],
                $post_id
            ));
            return new WP_Error(
                'c2pa_compliance_violation',
                sprintf(
                    __('C2PA compliance check failed: Expected at least 1 wrapper, found %d. Please contact support.', 'encypher-provenance'),
                    $final_check['count']
                ),
                ['status' => 500]
            );
        }

        // Embed signed text (with invisible markers) back into the original HTML
        $embedded_content = $this->embed_signed_text_in_html($clean_content, $signed_text);

        $embedded_check = $this->detect_c2pa_embeddings($embedded_content);
        if ($embedded_check['count'] < 1) {
            $this->debug_log(sprintf(
                'C2PA embed persistence failure! Signed text had %d wrappers but embedded HTML has %d for post %d',
                $final_check['count'],
                $embedded_check['count'],
                $post_id
            ));
            return new WP_Error(
                'c2pa_embed_persist_failed',
                __('C2PA embedding could not be persisted into the WordPress post content. Please contact support.', 'encypher-provenance'),
                ['status' => 500]
            );
        }

        $this->debug_log(sprintf(
            'Post %d successfully signed with C2PA wrapper (spec compliant). HTML: %d chars, signed text: %d chars',
            $post_id,
            strlen($embedded_content),
            strlen($signed_text)
        ));

        $document_id = isset($result['document_id']) ? sanitize_text_field((string) $result['document_id']) : '';
        $total_sentences = 0;
        if (isset($result['total_segments'])) {
            $total_sentences = (int) $result['total_segments'];
        } elseif (isset($result['total_sentences'])) {
            $total_sentences = (int) $result['total_sentences'];
        }

        $instance_id = '';
        if (!empty($result['instance_id'])) {
            $instance_id = sanitize_text_field((string) $result['instance_id']);
        } elseif (!empty($result['metadata']['instance_id'])) {
            $instance_id = sanitize_text_field((string) $result['metadata']['instance_id']);
        }
        $verification_id = $instance_id ?: $document_id;
        $verify_slug = Plugin::get_verify_slug();
        $verification_url = $verification_id ? home_url('/' . $verify_slug . '/') . urlencode($verification_id) : '';

        $this->is_signing = true;
        $updated = wp_update_post([
            'ID' => $post_id,
            'post_content' => $embedded_content,
        ], true);
        $this->is_signing = false;

        if (is_wp_error($updated)) {
            return $updated;
        }

        // Extract instance_id from result for provenance chain
        $new_instance_id = $instance_id ?: null;

        // Store metadata about the C2PA marking
        update_post_meta($post_id, '_encypher_marked', true);
        update_post_meta($post_id, '_encypher_provenance_cached_content_hash', md5((string) $embedded_content));
        update_post_meta($post_id, '_encypher_provenance_status', 'c2pa_protected');
        update_post_meta($post_id, '_encypher_provenance_document_id', $document_id);
        update_post_meta($post_id, '_encypher_provenance_verification_url', $verification_url);
        update_post_meta($post_id, '_encypher_provenance_total_sentences', $total_sentences);
        update_post_meta($post_id, '_encypher_provenance_last_signed', current_time('mysql'));
        update_post_meta($post_id, '_encypher_manifest_id', $document_id);
        update_post_meta($post_id, '_encypher_marked_date', current_time('mysql'));
        update_post_meta($post_id, '_encypher_provenance_signing_mode', $signing_mode);

        $settings_after_sign = get_option('encypher_provenance_settings', []);
        if (is_array($settings_after_sign)) {
            $sign_api_base_url = isset($settings_after_sign['api_base_url']) ? (string) $settings_after_sign['api_base_url'] : '';
            $sign_api_key = isset($settings_after_sign['api_key']) ? (string) $settings_after_sign['api_key'] : '';
            $signed_count = count(get_posts([
                'post_type' => 'any',
                'post_status' => 'any',
                'meta_key' => '_encypher_marked',
                'meta_value' => true,
                'fields' => 'ids',
                'posts_per_page' => -1,
                'suppress_filters' => true,
            ]));
            $this->sync_remote_wordpress_status($sign_api_base_url, $sign_api_key, [
                'connection_status' => 'connected',
                'site_url' => home_url('/'),
                'admin_url' => admin_url('admin.php?page=encypher-settings'),
                'site_name' => get_bloginfo('name'),
                'environment' => function_exists('wp_get_environment_type') ? wp_get_environment_type() : 'production',
                'network_id' => is_multisite() ? (string) get_current_network_id() : null,
                'blog_id' => is_multisite() ? get_current_blog_id() : null,
                'is_multisite' => is_multisite(),
                'is_primary' => true,
                'organization_id' => isset($settings_after_sign['organization_id']) ? (string) $settings_after_sign['organization_id'] : '',
                'organization_name' => isset($settings_after_sign['organization_name']) ? (string) $settings_after_sign['organization_name'] : '',
                'plugin_version' => ENCYPHER_PROVENANCE_VERSION,
                'plugin_installed' => true,
                'connection_tested' => true,
                'last_connection_checked_at' => gmdate('c'),
                'last_signed_at' => gmdate('c'),
                'last_signed_post_id' => $post_id,
                'last_signed_post_url' => get_permalink($post_id),
                'signed_post_count' => $signed_count,
            ]);
        }
        if ($signing_profile_id) {
            update_post_meta($post_id, '_encypher_provenance_signing_profile_id', $signing_profile_id);
        } else {
            delete_post_meta($post_id, '_encypher_provenance_signing_profile_id');
        }

        // Store new instance_id for next edit's provenance chain
        if ($new_instance_id) {
            update_post_meta($post_id, '_encypher_provenance_instance_id', $new_instance_id);
            $this->debug_log(sprintf(
                'Stored new instance_id for post %d: %s',
                $post_id,
                $new_instance_id
            ));
        }

        // Clear action type meta so it doesn't get reused
        delete_post_meta($post_id, '_encypher_action_type');

        $response_embeddings = [];
        if (isset($result['embeddings']) && is_array($result['embeddings'])) {
            $response_embeddings = $result['embeddings'];
        } elseif (isset($response['data']['embeddings']) && is_array($response['data']['embeddings'])) {
            $response_embeddings = $response['data']['embeddings'];
        } elseif (isset($response['embeddings']) && is_array($response['embeddings'])) {
            $response_embeddings = $response['embeddings'];
        }

        $this->persist_sentence_segments($post_id, $response_embeddings);

        // Clear any pending marking flags
        delete_post_meta($post_id, '_encypher_needs_marking');
        delete_post_meta($post_id, '_encypher_action_type');
        delete_post_meta($post_id, '_encypher_provenance_verification');

        // Record success in error log (clears any previous failure streak)
        ErrorLog::record_success($post_id);

        $settings_for_usage = get_option('encypher_provenance_settings', []);
        $updated_usage = $this->resolve_usage_snapshot($settings_for_usage, true);

        return new WP_REST_Response([
            'status' => 'c2pa_protected',
            'document_id' => $document_id,
            'verification_url' => $verification_url,
            'embedded_content' => $embedded_content,
            'total_sentences' => $total_sentences,
            'usage' => $updated_usage,
        ]);
    }

    /**
     * Return the WordPress/ai content provenance status for a post.
     *
     * Reads the `_encypher_wpai_experiments` post meta stored by the
     * WordPress_AI_Compat layer whenever it signs an AI-generated snippet.
     * Combines that with the overall post signing status to produce a
     * shield-badge-ready status string.
     *
     * Response shape:
     *   { status: 'verified'|'unverified'|'tampered'|'none', details: { experiments: [...] } }
     */
    public function handle_wordpress_ai_status_request(WP_REST_Request $request)
    {
        $post_id = (int) $request->get_param('post_id');

        $experiments = get_post_meta($post_id, '_encypher_wpai_experiments', true);
        if (!is_array($experiments) || empty($experiments)) {
            return new WP_REST_Response([
                'status'  => 'none',
                'details' => ['experiments' => []],
            ]);
        }

        // Derive shield status from the overall post signing state.
        $post_status = get_post_meta($post_id, '_encypher_provenance_status', true);

        if (in_array($post_status, ['c2pa_protected', 'c2pa_verified', 'signed', 'verified'], true)) {
            $shield_status = 'verified';
        } elseif ($post_status === 'tampered') {
            $shield_status = 'tampered';
        } else {
            // Experiments were signed inline but the post hasn't been fully signed yet
            // (e.g. still a draft). Show as unverified rather than none.
            $shield_status = 'unverified';
        }

        return new WP_REST_Response([
            'status'  => $shield_status,
            'details' => [
                'experiments' => array_values($experiments),
            ],
        ]);
    }

    public function handle_status_request(WP_REST_Request $request)
    {
        $post_id = (int) $request->get_param('post_id');
        $status = get_post_meta($post_id, '_encypher_provenance_status', true);
        $signature = get_post_meta($post_id, '_encypher_provenance_signature', true);
        $document_id = get_post_meta($post_id, '_encypher_provenance_document_id', true);
        $instance_id = get_post_meta($post_id, '_encypher_provenance_instance_id', true);
        $total_sentences = (int) get_post_meta($post_id, '_encypher_provenance_total_sentences', true);
        $last_signed = get_post_meta($post_id, '_encypher_provenance_last_signed', true);
        $verification = get_post_meta($post_id, '_encypher_provenance_verification', true);
        $sentences = $this->get_sentence_segments_payload($post_id);
        $settings = get_option('encypher_provenance_settings', []);
        if (!is_array($settings)) {
            $settings = [];
        }
        $tier = isset($settings['tier']) ? (string) $settings['tier'] : 'free';
        $usage = $this->resolve_usage_snapshot($settings, true);

        // Generate verification URL using instance_id if available, otherwise document_id
        $verification_id = $instance_id ?: $document_id;
        $verify_slug = Plugin::get_verify_slug();
        $verification_url = $verification_id ? home_url('/' . $verify_slug . '/') . urlencode($verification_id) : '';

        return new WP_REST_Response([
            'status' => $status ?: 'not_signed',
            'signature' => $signature,
            'document_id' => $document_id,
            'instance_id' => $instance_id,
            'verification_url' => $verification_url,
            'total_sentences' => $total_sentences,
            'last_signed' => $last_signed,
            'verification' => $verification,
            'sentences' => $sentences['items'],
            'sentences_total' => $sentences['total'],
            'usage' => $usage,
            'tier' => $tier,
            'signing_mode' => isset($settings['signing_mode']) ? $settings['signing_mode'] : 'managed',
        ]);
    }

    public function handle_verify_request(WP_REST_Request $request)
    {
        $post_id = (int) $request->get_param('post_id');
        $post = get_post($post_id);
        if (! $post) {
            return new WP_Error('invalid_post', __('Invalid post.', 'encypher-provenance'), ['status' => 400]);
        }

        if ('publish' !== $post->post_status) {
            return new WP_Error('invalid_post_status', __('Post not found or not published.', 'encypher-provenance'), ['status' => 404]);
        }

        // Get raw post content to preserve invisible Unicode characters
        $raw_content = get_post_field('post_content', $post_id, 'raw');

        // Extract plain text from HTML for verification.
        // The signing pipeline signs plain text (extracted from HTML), so the
        // C2PA content hash is computed on plain text. We must send the same
        // plain text (with VS markers intact) to /verify so the hash matches.
        // extract_text_from_html strips VS chars via DOMDocument, so we use
        // extract_html_text_fragments which works at the byte level and
        // preserves all invisible characters.
        $verify_text = $this->extract_text_for_verify($raw_content);

        $endpoint = '/verify';
        $require_auth = false;

        // Check for cached verification (disabled in development, 5 minute cache in production)
        // Set WP_DEBUG to true in wp-config.php for development mode
        $cache_enabled = !defined('WP_DEBUG') || !WP_DEBUG;
        $cache_key = 'encypher_verify_' . $post_id . '_' . md5($verify_text . '|' . $endpoint);

        if ($cache_enabled) {
            $cached = get_transient($cache_key);
            if (false !== $cached && is_array($cached)) {
                $this->debug_log(sprintf('Returning cached verification for post %d', $post_id));
                $cached['cached'] = true;
                return new WP_REST_Response($cached);
            }
        } else {
            $this->debug_log(sprintf('Cache disabled (WP_DEBUG=true), performing fresh verification for post %d', $post_id));
        }

        $payload = [
            'text' => $verify_text,
        ];

        $verification_mode = 'standard';
        $this->debug_log(sprintf('Calling %s for post %d (content length: %d)', $endpoint, $post_id, strlen($raw_content)));
        $response = $this->call_backend($endpoint, $payload, $require_auth);
        if (is_wp_error($response)) {
            $this->debug_log(sprintf('Verification API error for post %d: %s', $post_id, $response->get_error_message()));
            return $response;
        }

        $normalized = [
            'valid' => false,
            'tampered' => false,
            'reason_code' => null,
            'signer_id' => null,
            'signer_name' => null,
            'signing_identity' => null,
            'verified_at' => null,
            'metadata' => null,
            'error' => null,
            'cached' => false,
            'verification_mode' => $verification_mode,
            'correlation_id' => null,
            'attribution' => null,
            'plagiarism' => null,
            'fuzzy_search' => null,
        ];

        if (isset($response['success']) && $response['success'] && isset($response['data']) && is_array($response['data'])) {
            $verdict = $response['data'];
            $normalized['valid'] = !empty($verdict['valid']);
            $normalized['tampered'] = !empty($verdict['tampered']);
            $normalized['reason_code'] = isset($verdict['reason_code']) ? (string) $verdict['reason_code'] : null;
            $normalized['signer_id'] = isset($verdict['signer_id']) ? (string) $verdict['signer_id'] : null;
            $normalized['signing_identity'] = $this->resolve_signing_identity($verdict);
            $normalized['signer_name'] = $normalized['signing_identity'] ?: $this->resolve_signer_display($verdict);
            $normalized['verified_at'] = isset($verdict['timestamp']) ? (string) $verdict['timestamp'] : null;
            $normalized['metadata'] = $this->build_manifest_payload_for_display($verdict);
            if (isset($response['correlation_id'])) {
                $normalized['correlation_id'] = (string) $response['correlation_id'];
            }
            if (isset($response['attribution']) && is_array($response['attribution'])) {
                $normalized['attribution'] = $response['attribution'];
            }
            if (isset($response['plagiarism']) && is_array($response['plagiarism'])) {
                $normalized['plagiarism'] = $response['plagiarism'];
            }
            if (isset($response['fuzzy_search']) && is_array($response['fuzzy_search'])) {
                $normalized['fuzzy_search'] = $response['fuzzy_search'];
            }
            if (!$normalized['valid']) {
                $normalized['error'] = $normalized['tampered']
                    ? __('Manifest found but signature verification failed. The content may have been modified.', 'encypher-provenance')
                    : __('Manifest found but could not be verified.', 'encypher-provenance');
            }
        } elseif (isset($response['error']) && is_array($response['error']) && isset($response['error']['message'])) {
            $normalized['error'] = (string) $response['error']['message'];
        }

        $this->debug_log(sprintf('Verification response for post %d: valid=%s', $post_id, $normalized['valid'] ? 'true' : 'false'));

        // Cache the verification result for 5 minutes (only if caching is enabled)
        if ($cache_enabled) {
            set_transient($cache_key, $normalized, 5 * MINUTE_IN_SECONDS);
        }

        // Store verification result in post meta
        update_post_meta($post_id, '_encypher_provenance_verification', $normalized);
        update_post_meta($post_id, '_encypher_provenance_last_verified', current_time('mysql'));

        // Store instance_id for public provenance lookup
        if (!empty($normalized['metadata']['instance_id'])) {
            update_post_meta($post_id, '_encypher_provenance_instance_id', $normalized['metadata']['instance_id']);
        }

        // Update status based on verification
        $status = 'not_signed';
        if (!empty($normalized['valid'])) {
            $status = 'c2pa_verified';
        } elseif (!empty($normalized['error'])) {
            $status = 'verification_failed';
        }
        update_post_meta($post_id, '_encypher_provenance_status', $status);

        $normalized['cached'] = false;

        $verify_settings = get_option('encypher_provenance_settings', []);
        if (is_array($verify_settings)) {
            $verify_api_base_url = isset($verify_settings['api_base_url']) ? (string) $verify_settings['api_base_url'] : '';
            $verify_api_key = isset($verify_settings['api_key']) ? (string) $verify_settings['api_key'] : '';
            $this->sync_remote_wordpress_verification_event($verify_api_base_url, $verify_api_key, [
                'install_id' => $this->ensure_local_install_id($verify_settings),
                'post_id' => $post_id,
                'post_url' => get_permalink($post_id),
                'valid' => ! empty($normalized['valid']),
                'tampered' => ! empty($normalized['tampered']),
                'status' => $status,
                'verified_at' => gmdate('c'),
            ]);
        }

        // Increment site-wide verification hit counter
        $this->increment_verify_hits();

        return new WP_REST_Response($normalized);
    }

    /**
     * Increment the site-wide verification hit counter and daily bucket.
     */
    private function increment_verify_hits(): void
    {
        // Total lifetime counter
        $total = (int) get_option('encypher_verify_hits', 0);
        update_option('encypher_verify_hits', $total + 1, false);

        // Daily bucket: array keyed by 'Y-m-d', last 30 days retained
        $today = gmdate('Y-m-d');
        $daily = get_option('encypher_verify_hits_daily', []);
        if (! is_array($daily)) {
            $daily = [];
        }
        $daily[$today] = ($daily[$today] ?? 0) + 1;

        // Prune entries older than 30 days
        $cutoff = gmdate('Y-m-d', strtotime('-30 days'));
        foreach (array_keys($daily) as $date) {
            if ($date < $cutoff) {
                unset($daily[$date]);
            }
        }
        update_option('encypher_verify_hits_daily', $daily, false);
    }

    /**
     * Resolve signing identity for UI display.
     *
     * Prefer explicit API fields, then fall back to C2PA metadata assertion
     * publisher identifiers when available in DB-backed manifests.
     */
    private function resolve_signing_identity(array $verdict): ?string
    {
        $candidates = [
            $verdict['signing_identity'] ?? null,
            $verdict['publisher_display_name'] ?? null,
        ];

        if (isset($verdict['c2pa']) && is_array($verdict['c2pa']) && isset($verdict['c2pa']['assertions']) && is_array($verdict['c2pa']['assertions'])) {
            foreach ($verdict['c2pa']['assertions'] as $assertion) {
                if (!is_array($assertion) || ($assertion['label'] ?? null) !== 'c2pa.metadata' || !isset($assertion['data']) || !is_array($assertion['data'])) {
                    continue;
                }
                $meta = $assertion['data'];
                if (isset($meta['publisher']) && is_array($meta['publisher'])) {
                    $candidates[] = $meta['publisher']['name'] ?? null;
                    $candidates[] = $meta['publisher']['identifier'] ?? null;
                }
                $candidates[] = $meta['author'] ?? null;
            }
        }

        foreach ($candidates as $candidate) {
            if (is_string($candidate) && '' !== trim($candidate)) {
                return trim($candidate);
            }
        }

        return null;
    }

    /**
     * Resolve signer display label, preferring signing identity when present.
     */
    private function resolve_signer_display(array $verdict): ?string
    {
        $candidates = [
            $verdict['publisher_display_name'] ?? null,
            $verdict['signer_name'] ?? null,
            $verdict['organization_name'] ?? null,
            $verdict['signer_id'] ?? null,
        ];

        foreach ($candidates as $candidate) {
            if (is_string($candidate) && '' !== trim($candidate)) {
                return trim($candidate);
            }
        }

        return null;
    }

    /**
     * Build a display-friendly manifest payload for the frontend modal.
     *
     * Prefer the full DB-backed C2PA assertion set when available, then merge
     * verification details (segment_uuid / total_signatures) for UX summaries.
     */
    private function build_manifest_payload_for_display(array $verdict): ?array
    {
        $manifest = [];

        if (isset($verdict['c2pa']) && is_array($verdict['c2pa'])) {
            $c2pa = $verdict['c2pa'];
            if (isset($c2pa['assertions']) && is_array($c2pa['assertions']) && !empty($c2pa['assertions'])) {
                $manifest['assertions'] = $c2pa['assertions'];
            }
            foreach (['manifest_url', 'manifest_hash', 'validated', 'validation_type', 'certificate_chain'] as $key) {
                if (array_key_exists($key, $c2pa) && null !== $c2pa[$key]) {
                    $manifest[$key] = $c2pa[$key];
                }
            }
        }

        if (isset($verdict['details']) && is_array($verdict['details']) && isset($verdict['details']['manifest']) && is_array($verdict['details']['manifest'])) {
            foreach ($verdict['details']['manifest'] as $key => $value) {
                if (!array_key_exists($key, $manifest)) {
                    $manifest[$key] = $value;
                }
            }
        }

        return !empty($manifest) ? $manifest : null;
    }

    public function handle_provenance_request(WP_REST_Request $request)
    {
        // Support lookup by instance_id or post_id
        $instance_id = $request->get_param('instance_id');
        $post_id = $request->get_param('post_id');

        if ($instance_id) {
            // Query posts by instance_id stored in verification metadata
            $args = [
                'post_type' => 'any',
                'post_status' => 'publish',
                'posts_per_page' => 1,
                'meta_query' => [
                    [
                        'key' => '_encypher_provenance_instance_id',
                        'value' => $instance_id,
                        'compare' => '='
                    ]
                ]
            ];
            $query = new \WP_Query($args);
            if (!$query->have_posts()) {
                return new WP_Error('not_found', __('No content found with this C2PA instance ID.', 'encypher-provenance'), ['status' => 404]);
            }
            $post = $query->posts[0];
            $post_id = $post->ID;
        } else {
            $post_id = (int) $post_id;
            $post = get_post($post_id);
            if (! $post || 'publish' !== $post->post_status) {
                return new WP_Error('invalid_post', __('Post not found or not published.', 'encypher-provenance'), ['status' => 404]);
            }
        }

        // Get all stored metadata
        $document_id = get_post_meta($post_id, '_encypher_provenance_document_id', true);
        $status = get_post_meta($post_id, '_encypher_provenance_status', true);
        $total_sentences = (int) get_post_meta($post_id, '_encypher_provenance_total_sentences', true);
        $last_signed = get_post_meta($post_id, '_encypher_provenance_last_signed', true);
        $last_verified = get_post_meta($post_id, '_encypher_provenance_last_verified', true);
        $verification = get_post_meta($post_id, '_encypher_provenance_verification', true);
        $sentences = $this->get_sentence_segments_payload($post_id);

        // Build provenance report
        $report = [
            'post' => [
                'id' => $post_id,
                'title' => $post->post_title,
                'author' => get_the_author_meta('display_name', $post->post_author),
                'published' => $post->post_date,
                'modified' => $post->post_modified,
                'url' => get_permalink($post),
            ],
            'c2pa' => [
                'document_id' => $document_id,
                'status' => $status,
                'last_signed' => $last_signed,
                'last_verified' => $last_verified,
                'total_sentences' => $total_sentences,
            ],
            'verification' => $verification ?: null,
            'sentences' => $sentences,
        ];

        return new WP_REST_Response($report);
    }

    public function mark_post_needs_verification($post_id, $post, $update): void
    {
        if (wp_is_post_revision($post_id) || 'auto-draft' === $post->post_status) {
            return;
        }

        if ($this->is_signing) {
            update_post_meta($post_id, '_encypher_provenance_cached_content_hash', md5((string) $post->post_content));
            return;
        }

        if ($update) {
            // If content changes manually, mark status stale.
            $previous_content = get_post_meta($post_id, '_encypher_provenance_cached_content_hash', true);
            $current_hash = md5((string) $post->post_content);
            $is_marked = (bool) get_post_meta($post_id, '_encypher_marked', true);
            if ($is_marked && $previous_content && $previous_content !== $current_hash) {
                update_post_meta($post_id, '_encypher_provenance_status', 'modified');
                delete_post_meta($post_id, '_encypher_provenance_verification');
                // Keep the previous signed-content hash so auto_sign_on_update can
                // detect the content delta and trigger a c2pa.edited re-sign.
                return;
            }
            update_post_meta($post_id, '_encypher_provenance_cached_content_hash', $current_hash);
        }
    }

    /**
     * Auto-sign posts when they transition to published status.
     *
     * Handles: New post being published (draft -> publish)
     *
     * @param string $new_status New post status
     * @param string $old_status Old post status
     * @param WP_Post $post Post object
     */
    public function auto_sign_on_publish(string $new_status, string $old_status, $post): void
    {
        // Only act when post becomes published (not already published)
        if ('publish' !== $new_status || 'publish' === $old_status) {
            return;
        }

        // Check if auto-signing is enabled and post type is configured
        $settings = get_option('encypher_provenance_settings', []);
        $auto_sign = isset($settings['auto_mark_on_publish']) ? (bool) $settings['auto_mark_on_publish'] : true;

        if (!$auto_sign) {
            return;
        }

        $configured_post_types = isset($settings['post_types']) && is_array($settings['post_types'])
            ? $settings['post_types']
            : ['post', 'page'];

        if (!in_array($post->post_type, $configured_post_types, true)) {
            return;
        }

        // Sign the new post
        $this->perform_signing($post->ID);
    }

    /**
     * Auto-sign posts when they are updated (already published).
     *
     * Handles: Published post being updated (publish -> publish with content changes)
     *
     * @param int $post_id Post ID
     * @param WP_Post $post Post object after update
     * @param WP_Post $post_before Post object before update
     */
    public function auto_sign_on_update(int $post_id, $post, $post_before): void
    {
        // Skip if this is the signing operation itself
        if ($this->is_signing) {
            $this->debug_log('Skipping auto_sign_on_update - is_signing flag is true');
            return;
        }

        // Skip autosaves and revisions
        if (wp_is_post_autosave($post_id) || wp_is_post_revision($post_id)) {
            return;
        }

        // Only process published posts
        if ('publish' !== $post->post_status) {
            $this->debug_log(sprintf('Post %d status is %s, not publish', $post_id, $post->post_status));
            return;
        }

        // Don't trigger on initial publish (status change from non-publish to publish)
        // The initial signing will be handled by auto_sign_on_publish
        if ($post_before && is_object($post_before) && $post_before->post_status !== 'publish') {
            $this->debug_log(sprintf('Skipping auto_sign_on_update - initial publish (status changed from %s to publish)', $post_before->post_status));
            return;
        }

        // Check if auto-signing on update is enabled and post type is configured
        $settings = get_option('encypher_provenance_settings', []);
        $auto_sign_on_update = isset($settings['auto_mark_on_update']) ? (bool) $settings['auto_mark_on_update'] : true;

        if (!$auto_sign_on_update) {
            $this->debug_log('Auto-signing on update is disabled in settings');
            return;
        }

        $configured_post_types = isset($settings['post_types']) && is_array($settings['post_types'])
            ? $settings['post_types']
            : ['post', 'page'];

        if (!in_array($post->post_type, $configured_post_types, true)) {
            return;
        }

        // Check if post is already marked
        $is_marked = get_post_meta($post_id, '_encypher_marked', true);
        $this->debug_log(sprintf('Post %d is_marked = %s', $post_id, $is_marked ? 'true' : 'false'));

        if (!$is_marked) {
            // Not signed yet - sign it now with c2pa.created
            $this->debug_log(sprintf('Post %d not marked yet, signing now with c2pa.created', $post_id));
            update_post_meta($post_id, '_encypher_action_type', 'c2pa.created');
            $this->perform_signing($post_id, false); // false = new signing
            return;
        }

        // Check if action type is already set (e.g., by admin hooks)
        $action_type = get_post_meta($post_id, '_encypher_action_type', true);
        if ($action_type === 'c2pa.edited') {
            // Action already set to edited - honor it and re-sign
            $this->debug_log(sprintf('Post %d action type already set to c2pa.edited, performing re-sign', $post_id));
            $this->perform_signing($post_id, true); // true = is_update
            return;
        }

        // Post is already signed - check if content changed
        // Compare against the CACHED content hash (which was set after the last signing)
        // This prevents re-signing when the only change is the C2PA wrapper itself
        $cached_hash = get_post_meta($post_id, '_encypher_provenance_cached_content_hash', true);
        $current_hash = md5($post->post_content);

        $this->debug_log(sprintf(
            'Post %d hash check - cached: %s, current: %s',
            $post_id,
            $cached_hash ? substr($cached_hash, 0, 8) : 'none',
            substr($current_hash, 0, 8)
        ));

        if ($cached_hash && $cached_hash === $current_hash) {
            // Content unchanged since last signing - skip re-signing
            $this->debug_log(sprintf('Post %d content unchanged since last signing, skipping re-sign', $post_id));
            return;
        }

        // Content changed - re-sign with c2pa.edited action
        $this->debug_log(sprintf('Content changed for post %d, triggering re-sign with c2pa.edited', $post_id));
        update_post_meta($post_id, '_encypher_action_type', 'c2pa.edited');
        $this->perform_signing($post_id, true); // true = is_update
    }

    /**
     * Perform the actual signing operation.
     *
     * @param int $post_id Post ID to sign
     * @param bool $is_update Whether this is an update (re-signing)
     */
    private function perform_signing(int $post_id, bool $is_update = false): void
    {
        // Prevent recursion
        if ($this->is_signing) {
            return;
        }

        try {
            // Create a mock request for the sign endpoint
            $request = new WP_REST_Request('POST', '/encypher-provenance/v1/sign');
            $request->set_param('post_id', $post_id);
            $request->set_param('metadata', []);

            // Call the sign handler
            $response = $this->handle_sign_request($request);

            if (is_wp_error($response)) {
                $this->debug_log(sprintf(
                    'Auto-sign failed for post %d: %s',
                    $post_id,
                    $response->get_error_message()
                ));
                $context = $is_update ? 'auto_sign' : 'auto_sign';
                ErrorLog::record_failure(
                    $post_id,
                    $response->get_error_code(),
                    $response->get_error_message(),
                    $context
                );
                $consecutive = ErrorLog::get_consecutive_failures($post_id);
                ErrorLog::maybe_fire_webhook($post_id, [
                    'post_title'          => get_the_title($post_id) ?: sprintf('Post #%d', $post_id),
                    'error_code'          => $response->get_error_code(),
                    'error_message'       => $response->get_error_message(),
                    'consecutive_failures' => $consecutive,
                    'timestamp'           => gmdate('c'),
                    'context'             => $context,
                ]);
            } else {
                $this->debug_log(sprintf(
                    'Auto-signed post %d (%s)',
                    $post_id,
                    $is_update ? 'updated' : 'new'
                ));
                ErrorLog::record_success($post_id);
                // Sign the featured image for CDN provenance continuity
                $this->sign_featured_image($post_id);
            }
        } catch (\Exception $e) {
            $this->debug_log(sprintf(
                'Auto-sign exception for post %d: %s',
                $post_id,
                $e->getMessage()
            ));
            ErrorLog::record_failure(
                $post_id,
                'exception',
                $e->getMessage(),
                'auto_sign'
            );
            ErrorLog::maybe_fire_webhook($post_id, [
                'post_title'          => get_the_title($post_id) ?: sprintf('Post #%d', $post_id),
                'error_code'          => 'exception',
                'error_message'       => $e->getMessage(),
                'consecutive_failures' => ErrorLog::get_consecutive_failures($post_id),
                'timestamp'           => gmdate('c'),
                'context'             => 'auto_sign',
            ]);
        }
    }

    /**
     * Show a dismissible admin notice on the post edit screen when the last
     * auto-sign attempt failed.
     */
    public function render_sign_error_notice(): void
    {
        $screen = function_exists('get_current_screen') ? get_current_screen() : null;
        if (! $screen || ! in_array($screen->base, ['post', 'post-new'], true)) {
            return;
        }

        $post_id = isset($_GET['post']) ? (int) $_GET['post'] : 0;
        if ($post_id <= 0) {
            return;
        }

        $dismissed = get_post_meta($post_id, '_encypher_sign_error_dismissed', true);
        if ($dismissed) {
            return;
        }

        $error = get_post_meta($post_id, '_encypher_last_sign_error', true);
        if (! is_array($error) || empty($error['message'])) {
            return;
        }

        $consecutive = (int) ($error['consecutive'] ?? 1);
        $timestamp   = isset($error['timestamp']) ? wp_date(get_option('date_format') . ' ' . get_option('time_format'), strtotime($error['timestamp'])) : '';
        $nonce       = wp_create_nonce('encypher_dismiss_sign_error_' . $post_id);
        ?>
        <div class="notice notice-error encypher-sign-error-notice" style="position:relative;padding-right:48px;">
            <p>
                <strong><?php esc_html_e('Encypher: Auto-sign failed', 'encypher-provenance'); ?></strong>
                <?php if ($timestamp): ?>
                    <span style="color:#646970;font-size:12px;margin-left:8px;"><?php echo esc_html($timestamp); ?></span>
                <?php endif; ?>
            </p>
            <p>
                <?php echo esc_html($error['message']); ?>
                <?php if ($consecutive > 1): ?>
                    <span style="color:#d63638;margin-left:8px;">
                        <?php echo esc_html(sprintf(
                            /* translators: %d: number of consecutive failures */
                            _n('%d consecutive failure', '%d consecutive failures', $consecutive, 'encypher-provenance'),
                            $consecutive
                        )); ?>
                    </span>
                <?php endif; ?>
            </p>
            <p>
                <a href="<?php echo esc_url(admin_url('admin.php?page=encypher-analytics#error-log')); ?>">
                    <?php esc_html_e('View error log', 'encypher-provenance'); ?>
                </a>
                &nbsp;&middot;&nbsp;
                <a href="<?php echo esc_url(admin_url('admin.php?page=encypher-settings')); ?>">
                    <?php esc_html_e('Check API settings', 'encypher-provenance'); ?>
                </a>
            </p>
            <button type="button"
                class="notice-dismiss"
                onclick="jQuery.post(ajaxurl, {action:'encypher_dismiss_sign_error', post_id:<?php echo (int) $post_id; ?>, _wpnonce:'<?php echo esc_js($nonce); ?>'});"
                style="position:absolute;top:8px;right:8px;">
                <span class="screen-reader-text"><?php esc_html_e('Dismiss this notice', 'encypher-provenance'); ?></span>
            </button>
        </div>
        <?php
    }

    /**
     * AJAX handler: dismiss the sign-error notice for a post.
     */
    public function ajax_dismiss_sign_error(): void
    {
        $post_id = isset($_POST['post_id']) ? (int) $_POST['post_id'] : 0;
        if ($post_id <= 0 || ! current_user_can('edit_post', $post_id)) {
            wp_send_json_error('Unauthorized', 403);
        }
        check_ajax_referer('encypher_dismiss_sign_error_' . $post_id);
        update_post_meta($post_id, '_encypher_sign_error_dismissed', true);
        wp_send_json_success();
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

    private function resolve_signed_text_with_embedding_plan(array $result, string $visible_text): ?string
    {
        if (isset($result['embedding_plan']) && is_array($result['embedding_plan'])) {
            $resolved = $this->apply_embedding_plan($visible_text, $result['embedding_plan']);
            if (is_string($resolved) && '' !== $resolved) {
                return $resolved;
            }
        }

        $signed_text = $result['signed_text'] ?? ($result['embedded_content'] ?? null);
        if (is_string($signed_text) && '' !== $signed_text) {
            return $signed_text;
        }

        return null;
    }

    private function apply_embedding_plan(string $visible_text, array $embedding_plan): ?string
    {
        if (
            !isset($embedding_plan['index_unit'])
            || !is_string($embedding_plan['index_unit'])
            || 'codepoint' !== $embedding_plan['index_unit']
        ) {
            return null;
        }

        if (!isset($embedding_plan['operations']) || !is_array($embedding_plan['operations']) || empty($embedding_plan['operations'])) {
            return null;
        }

        $chars = $this->mb_str_split_safe($visible_text);
        $char_count = count($chars);
        $markers_by_position = [];

        foreach ($embedding_plan['operations'] as $operation) {
            if (!is_array($operation)) {
                return null;
            }

            if (!isset($operation['insert_after_index'], $operation['marker'])) {
                return null;
            }

            if (!is_int($operation['insert_after_index']) || !is_string($operation['marker']) || '' === $operation['marker']) {
                return null;
            }

            $insert_after_index = $operation['insert_after_index'];
            if ($insert_after_index < -1 || $insert_after_index >= $char_count) {
                return null;
            }

            if (!isset($markers_by_position[$insert_after_index])) {
                $markers_by_position[$insert_after_index] = [];
            }
            $markers_by_position[$insert_after_index][] = $operation['marker'];
        }

        $output = '';

        if (isset($markers_by_position[-1])) {
            foreach ($markers_by_position[-1] as $marker) {
                $output .= $marker;
            }
        }

        for ($idx = 0; $idx < $char_count; $idx++) {
            $output .= $chars[$idx];
            if (isset($markers_by_position[$idx])) {
                foreach ($markers_by_position[$idx] as $marker) {
                    $output .= $marker;
                }
            }
        }

        return $output;
    }

    // =========================================================================
    // HTML parsing — delegated to HtmlParser
    // =========================================================================

    private function extract_text_from_html(string $html): string
    {
        return $this->get_parser()->extract_text($html);
    }

    private function embed_signed_text_in_html(string $html, string $signed): string
    {
        return $this->get_parser()->embed_signed_text($html, $signed);
    }

    private function extract_html_text_fragments(string $html): array
    {
        return $this->get_parser()->extract_fragments($html);
    }

    private function extract_text_for_verify(string $html): string
    {
        return $this->get_parser()->extract_text_for_verify($html);
    }

    private function sanitize_wp_block_comments(string $content): string
    {
        return $this->get_parser()->sanitize_wp_block_comments($content);
    }

    private function mb_str_split_safe(string $str): array
    {
        return $this->get_parser()->mb_str_split_safe($str);
    }

    private function is_vs_char(string $ch): bool
    {
        return $this->get_parser()->is_vs_char($ch);
    }

    private function is_vs_or_whitespace(string $ch): bool
    {
        return $this->get_parser()->is_vs_or_whitespace($ch);
    }

    private function detect_c2pa_embeddings(string $text): array
    {
        return $this->get_parser()->detect_c2pa_embeddings($text);
    }

    private function strip_c2pa_embeddings(string $text): string
    {
        return $this->get_parser()->strip_c2pa_embeddings($text);
    }

    private function persist_sentence_segments(int $post_id, array $embeddings): void
    {
        if (empty($embeddings) || !is_array($embeddings)) {
            delete_post_meta($post_id, '_encypher_provenance_sentence_segments');
            return;
        }

        $normalized = [];
        foreach ($embeddings as $segment) {
            if (!is_array($segment) || !isset($segment['leaf_index'])) {
                continue;
            }

            $preview = '';
            if (isset($segment['text'])) {
                $preview = wp_strip_all_tags((string) $segment['text']);
            }
            $snippet = function_exists('mb_substr') ? mb_substr($preview, 0, 160) : substr($preview, 0, 160);
            $char_count = function_exists('mb_strlen') ? mb_strlen($preview) : strlen($preview);

            $normalized[] = [
                'leaf_index' => (int) $segment['leaf_index'],
                'preview' => $snippet,
                'characters' => $char_count,
                'ref_id' => isset($segment['ref_id']) ? sanitize_text_field((string) $segment['ref_id']) : '',
                'verification_url' => isset($segment['verification_url']) ? esc_url_raw((string) $segment['verification_url']) : '',
            ];
        }

        if (!empty($normalized)) {
            update_post_meta($post_id, '_encypher_provenance_sentence_segments', $normalized);
        } else {
            delete_post_meta($post_id, '_encypher_provenance_sentence_segments');
        }
    }

    private function get_sentence_segments_payload(int $post_id): array
    {
        $segments = get_post_meta($post_id, '_encypher_provenance_sentence_segments', true);
        if (!is_array($segments)) {
            return [
                'items' => [],
                'total' => 0,
            ];
        }

        $items = [];
        foreach ($segments as $segment) {
            if (!is_array($segment) || !isset($segment['leaf_index'])) {
                continue;
            }
            $preview = isset($segment['preview']) ? $segment['preview'] : '';
            $char_count = isset($segment['characters']) ? (int) $segment['characters'] : (function_exists('mb_strlen') ? mb_strlen($preview) : strlen($preview));
            $items[] = [
                'leaf_index' => (int) $segment['leaf_index'],
                'preview' => $preview,
                'characters' => $char_count,
                'verification_url' => isset($segment['verification_url']) ? $segment['verification_url'] : '',
                'ref_id' => isset($segment['ref_id']) ? $segment['ref_id'] : '',
            ];
        }

        return [
            'items' => array_slice($items, 0, 50),
            'total' => count($items),
        ];
    }

    /**
     * Handle GET /payment-status: return cached payment method status from billing-service.
     */
    public function handle_payment_status(WP_REST_Request $request)
    {
        $cached = get_transient('encypher_payment_status');
        if (false !== $cached && is_array($cached)) {
            return new WP_REST_Response($cached);
        }

        $settings = get_option('encypher_provenance_settings', []);
        $api_base_url = isset($settings['api_base_url']) ? rtrim($settings['api_base_url'], '/') : '';
        $api_key = isset($settings['api_key']) ? trim((string) $settings['api_key']) : '';

        if ('' === $api_base_url || '' === $api_key) {
            return new WP_Error(
                'missing_configuration',
                __('API key and base URL must be configured.', 'encypher-provenance'),
                ['status' => 400]
            );
        }

        $url = $api_base_url . '/billing/payment-status';
        $response = wp_remote_get($url, [
            'timeout' => 15,
            'headers' => [
                'Accept'        => 'application/json',
                'Authorization' => 'Bearer ' . sanitize_text_field($api_key),
            ],
        ]);

        if (is_wp_error($response)) {
            return new WP_Error('http_error', $response->get_error_message(), ['status' => 502]);
        }

        $status_code = wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);

        if ($status_code >= 400 || ! is_array($data)) {
            $detail = is_array($data) && isset($data['detail']) ? $data['detail'] : __('Unable to fetch payment status.', 'encypher-provenance');
            return new WP_Error('backend_error', $detail, ['status' => $status_code ?: 502]);
        }

        set_transient('encypher_payment_status', $data, 5 * MINUTE_IN_SECONDS);

        return new WP_REST_Response($data);
    }

    /**
     * Handle POST /payment-setup: create a Stripe setup session via billing-service.
     */
    public function handle_payment_setup(WP_REST_Request $request)
    {
        $settings = get_option('encypher_provenance_settings', []);
        $api_base_url = isset($settings['api_base_url']) ? rtrim($settings['api_base_url'], '/') : '';
        $api_key = isset($settings['api_key']) ? trim((string) $settings['api_key']) : '';

        if ('' === $api_base_url || '' === $api_key) {
            return new WP_Error(
                'missing_configuration',
                __('API key and base URL must be configured.', 'encypher-provenance'),
                ['status' => 400]
            );
        }

        $success_url = admin_url('admin.php?page=encypher-bulk-mark&payment_setup=success');

        $url = $api_base_url . '/billing/payment-methods/setup';
        $response = wp_remote_post($url, [
            'timeout' => 15,
            'headers' => [
                'Content-Type'  => 'application/json',
                'Accept'        => 'application/json',
                'Authorization' => 'Bearer ' . sanitize_text_field($api_key),
            ],
            'body' => wp_json_encode([
                'success_url' => $success_url,
            ]),
        ]);

        if (is_wp_error($response)) {
            return new WP_Error('http_error', $response->get_error_message(), ['status' => 502]);
        }

        $status_code = wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);

        if ($status_code >= 400 || ! is_array($data) || empty($data['checkout_url'])) {
            $detail = is_array($data) && isset($data['detail']) ? $data['detail'] : __('Unable to create payment setup session.', 'encypher-provenance');
            return new WP_Error('backend_error', $detail, ['status' => $status_code ?: 502]);
        }

        // Clear payment status cache so it refreshes after setup
        delete_transient('encypher_payment_status');

        return new WP_REST_Response(['checkout_url' => $data['checkout_url']]);
    }

    /**
     * Perform HTTP request to backend and decode JSON response.
     */
    private function call_backend(string $path, array $body, bool $require_auth)
    {
        $settings = get_option('encypher_provenance_settings', []);
        $base_url = isset($settings['api_base_url']) ? rtrim($settings['api_base_url'], '/') : '';
        if (! $base_url) {
            return new WP_Error('missing_configuration', __('Please configure the Encypher API base URL.', 'encypher-provenance'), ['status' => 400]);
        }

        $url = $base_url . $path;
        $headers = [
            'Content-Type' => 'application/json',
            'Accept' => 'application/json',
        ];

        $api_key = isset($settings['api_key']) ? trim((string) $settings['api_key']) : '';
        if ($require_auth && $api_key) {
            $headers['Authorization'] = 'Bearer ' . sanitize_text_field($api_key);
        } elseif ($require_auth) {
            return new WP_Error('missing_api_key', __('Please configure an Encypher API key before signing.', 'encypher-provenance'), ['status' => 401]);
        }

        $args = [
            'headers' => $headers,
            'body' => wp_json_encode($body),
            'timeout' => 20,
        ];

        // Retry once on transient server errors (5xx) or network-level failures.
        $response = null;
        $last_error = null;
        for ($attempt = 1; $attempt <= 2; $attempt++) {
            $response = wp_remote_post($url, $args);
            if (is_wp_error($response)) {
                $last_error = $response;
                if ($attempt < 2) {
                    sleep(2);
                }
                continue;
            }
            $attempt_code = wp_remote_retrieve_response_code($response);
            if ($attempt_code >= 500 && $attempt < 2) {
                $last_error = null;
                sleep(2);
                continue;
            }
            $last_error = null;
            break;
        }
        if ($last_error !== null) {
            return new WP_Error('http_error', $last_error->get_error_message(), ['status' => 500]);
        }

        $status_code = wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);
        $decoded = json_decode($body, true);

        if (null === $decoded && '' !== trim((string) $body)) {
            return new WP_Error('invalid_json', __('Unable to parse backend response.', 'encypher-provenance'), ['status' => 502]);
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
                    // FastAPI validation errors return detail as array
                    if (is_array($decoded['detail'])) {
                        $message = wp_json_encode($decoded['detail'], JSON_PRETTY_PRINT);
                        $this->debug_log('Validation error details: ' . $message);
                    } else {
                        $message = (string) $decoded['detail'];
                    }
                }
                if (isset($decoded['error']['code'])) {
                    $code = (string) $decoded['error']['code'];
                }
            }
            if (! $message) {
                $message = $body;
            }
            return new WP_Error($code, sprintf(__('Backend responded with status %d: %s', 'encypher-provenance'), $status_code, $message), ['status' => $status_code]);
        }

        if (is_array($decoded) && array_key_exists('success', $decoded) && true !== $decoded['success']) {
            $message = isset($decoded['error']['message']) ? (string) $decoded['error']['message'] : (isset($decoded['message']) ? (string) $decoded['message'] : __('The Encypher API rejected the request.', 'encypher-provenance'));
            $code = isset($decoded['error']['code']) ? (string) $decoded['error']['code'] : 'api_error';
            $error_status = isset($decoded['error']['status']) ? (int) $decoded['error']['status'] : 400;
            return new WP_Error($code, $message, ['status' => $error_status]);
        }

        return is_array($decoded) ? $decoded : [];
    }

    /**
     * Probe the API server to verify it is reachable.
     *
     * Strategy (in order):
     *   1. GET /health        — fastest, no auth needed
     *   2. GET /readyz        — fallback lightweight probe
     *   3. GET /api/v1/account — always routed in Traefik; 401 still proves the
     *                            API is up (gateway is routing, not 404-ing)
     *
     * Returns decoded JSON body on 200, empty array on any other "API is up"
     * response (401/403 from account probe), or WP_Error on genuine failure.
     *
     * @param string $api_base_url Already-normalized base URL (ending with /api/v1).
     * @return array|WP_Error
     */
    private function probe_health(string $api_base_url)
    {
        $root = preg_replace('#/api/v1/?$#', '', rtrim($api_base_url, '/'));

        // --- Phase 1: root-level health probes ---
        foreach (['/health', '/readyz'] as $probe_path) {
            $response = wp_remote_get($root . $probe_path, ['timeout' => 10]);

            if (is_wp_error($response)) {
                return new WP_Error(
                    'connection_failed',
                    sprintf(
                        __('Connection failed: %s', 'encypher-provenance'),
                        $response->get_error_message()
                    ),
                    ['status' => 500]
                );
            }

            $status_code = wp_remote_retrieve_response_code($response);

            if ($status_code === 200) {
                return json_decode(wp_remote_retrieve_body($response), true) ?: [];
            }

            if ($status_code === 404) {
                continue; // Path not routed yet — try next
            }

            return new WP_Error(
                'health_check_failed',
                sprintf(__('Health check failed with status %d', 'encypher-provenance'), $status_code),
                ['status' => $status_code]
            );
        }

        // --- Phase 2: account endpoint fallback ---
        // /api/v1/account is guaranteed to be routed by Traefik.
        // A 401/403 response proves the API gateway is up and routing correctly.
        $account_probe = wp_remote_get(rtrim($api_base_url, '/') . '/account', ['timeout' => 10]);

        if (is_wp_error($account_probe)) {
            return new WP_Error(
                'connection_failed',
                sprintf(
                    __('Connection failed: %s', 'encypher-provenance'),
                    $account_probe->get_error_message()
                ),
                ['status' => 500]
            );
        }

        $status_code = wp_remote_retrieve_response_code($account_probe);

        // 2xx, 401, 403 all mean the API is reachable
        if ($status_code < 500 && $status_code !== 404) {
            return [];
        }

        return new WP_Error(
            'health_check_failed',
            sprintf(__('API host unreachable (status %d).', 'encypher-provenance'), $status_code),
            ['status' => $status_code]
        );
    }

    /**
     * Normalizes an API base URL to always end with /api/v1 (no trailing slash).
     * Accepts both https://api.encypherai.com/ and https://api.encypherai.com/api/v1.
     */
    private static function normalize_api_base_url(string $url): string
    {
        $url = rtrim(trim($url), '/');
        if ('' === $url) {
            return '';
        }
        if (! str_ends_with($url, '/api/v1')) {
            $url .= '/api/v1';
        }
        return $url;
    }

    /**
     * Handle connection test request (server-side).
     *
     * @param WP_REST_Request $request
     * @return WP_REST_Response|WP_Error
     */
    public function handle_test_connection_request(WP_REST_Request $request)
    {
        // Use provided values from request, or fall back to saved settings
        $api_base_url = $request->get_param('api_base_url');
        $api_key = $request->get_param('api_key');

        // If not provided in request, use saved settings
        if (empty($api_base_url)) {
            $settings = get_option('encypher_provenance_settings', []);
            $api_base_url = isset($settings['api_base_url']) ? $settings['api_base_url'] : '';
            $api_key = isset($settings['api_key']) ? $settings['api_key'] : '';
        }

        $api_base_url = self::normalize_api_base_url($api_base_url);

        if (empty($api_base_url)) {
            return new WP_Error(
                'no_api_url',
                __('No API URL configured', 'encypher-provenance'),
                ['status' => 400]
            );
        }

        $health = $this->probe_health($api_base_url);
        if (is_wp_error($health)) {
            return $health;
        }

        $health_data = $health;

        // Build response
        $result = [
            'success' => true,
            'status' => 'connected',
            'api_url' => $api_base_url,
            'health' => $health_data,
        ];

        $result['organization'] = [
            'organization_id' => 'org_demo',
            'name' => 'Demo Organization',
            'tier' => 'free'
        ];

        // Check if API key is configured
        if (!empty($api_key)) {
            $result['api_key_configured'] = true;
            $result['auth_note'] = 'API key configured (will be validated during signing)';

            $account = $this->fetch_remote_account($api_base_url, $api_key);
            if (! is_wp_error($account)) {
                $result['organization'] = [
                    'organization_id' => $account['organization_id'] ?: 'org_unknown',
                    'name' => $account['organization_name'] ?: ($account['organization_id'] ?: __('Your organization', 'encypher-provenance')),
                    'tier' => $account['tier'],
                ];
            }
        } else {
            $result['api_key_configured'] = false;
            $result['auth_note'] = 'No API key configured - using demo mode';
        }

        if (! empty($api_key) && ! empty($result['organization']['organization_id'])) {
            $this->sync_remote_wordpress_status($api_base_url, $api_key, [
                'connection_status' => 'connected',
                'site_url' => home_url('/'),
                'admin_url' => admin_url('admin.php?page=encypher-settings'),
                'site_name' => get_bloginfo('name'),
                'environment' => function_exists('wp_get_environment_type') ? wp_get_environment_type() : 'production',
                'network_id' => is_multisite() ? (string) get_current_network_id() : null,
                'blog_id' => is_multisite() ? get_current_blog_id() : null,
                'is_multisite' => is_multisite(),
                'is_primary' => true,
                'organization_id' => $result['organization']['organization_id'],
                'organization_name' => $result['organization']['name'],
                'plugin_version' => ENCYPHER_PROVENANCE_VERSION,
                'plugin_installed' => true,
                'connection_tested' => true,
                'last_connection_checked_at' => gmdate('c'),
            ]);
        }

        return new WP_REST_Response($result);
    }

    /**
     * Verify credentials and persist them without a full settings-form submit.
     * Called automatically when the user pastes an API key on the settings page.
     */
    public function handle_quick_connect_request(WP_REST_Request $request)
    {
        $api_base_url = self::normalize_api_base_url((string) $request->get_param('api_base_url'));
        $api_key      = trim((string) $request->get_param('api_key'));

        if ('' === $api_base_url || '' === $api_key) {
            return new WP_Error(
                'missing_params',
                __('API URL and API key are required.', 'encypher-provenance'),
                ['status' => 400]
            );
        }

        $health = $this->probe_health($api_base_url);
        if (is_wp_error($health)) {
            return $health;
        }

        // Fetch account / tier info
        $account  = $this->fetch_remote_account($api_base_url, $api_key);
        $tier     = 'free';
        $features = [];
        $usage    = [];
        $org      = [
            'organization_id' => '',
            'name'            => '',
            'tier'            => 'free',
        ];

        if (! is_wp_error($account)) {
            $tier     = $account['tier'] ?? 'free';
            $features = $account['features'] ?? [];
            $usage    = $account['usage'] ?? [];
            $org_name = $account['organization_name'] ?? '';
            $org_id   = $account['organization_id'] ?? '';
            $org      = [
                'organization_id' => $org_id,
                'name'            => $org_name ?: ($org_id ?: __('Your organization', 'encypher-provenance')),
                'tier'            => $tier,
            ];
        }

        // Persist only connection-related fields; leave all other settings untouched
        $current = get_option('encypher_provenance_settings', []);
        if (! is_array($current)) {
            $current = [];
        }
        $current['api_base_url']               = $api_base_url;
        $current['api_key']                    = $api_key;
        $current['tier']                       = $tier;
        $current['organization_id']            = $org['organization_id'];
        $current['organization_name']          = $org['name'];
        $current['features']                   = $features;
        $current['usage']                      = $usage;
        $current['connection_last_status']     = 'connected';
        $current['connection_last_checked_at'] = gmdate('c');

        update_option('encypher_provenance_settings', $current);

        if (! empty($org['organization_id'])) {
            $this->sync_remote_wordpress_status($api_base_url, $api_key, [
                'connection_status' => 'connected',
                'site_url' => home_url('/'),
                'admin_url' => admin_url('admin.php?page=encypher-settings'),
                'site_name' => get_bloginfo('name'),
                'environment' => function_exists('wp_get_environment_type') ? wp_get_environment_type() : 'production',
                'network_id' => is_multisite() ? (string) get_current_network_id() : null,
                'blog_id' => is_multisite() ? get_current_blog_id() : null,
                'is_multisite' => is_multisite(),
                'is_primary' => true,
                'organization_id' => $org['organization_id'],
                'organization_name' => $org['name'],
                'plugin_version' => ENCYPHER_PROVENANCE_VERSION,
                'plugin_installed' => true,
                'connection_tested' => true,
                'last_connection_checked_at' => gmdate('c'),
            ]);
        }

        // Bust the account transient so the next full-save fetches fresh data
        $cache_key = 'encypher_account_' . md5(strtolower($api_base_url) . '|' . substr(hash('sha256', $api_key), 0, 16));
        delete_site_transient($cache_key);

        return new WP_REST_Response([
            'success'      => true,
            'status'       => 'connected',
            'api_url'      => $api_base_url,
            'tier'         => $tier,
            'organization' => $org,
        ]);
    }

    public function handle_connect_start_request(WP_REST_Request $request)
    {
        $email = sanitize_email((string) $request->get_param('email'));
        $settings = get_option('encypher_provenance_settings', []);
        if (! is_array($settings)) {
            $settings = [];
        }

        $api_base_url = self::normalize_api_base_url((string) $request->get_param('api_base_url'));
        if ('' === $api_base_url) {
            $api_base_url = isset($settings['api_base_url']) ? self::normalize_api_base_url((string) $settings['api_base_url']) : 'https://api.encypherai.com/api/v1';
        }

        if ('' === $email) {
            return new WP_Error('invalid_email', __('A valid email address is required.', 'encypher-provenance'), ['status' => 400]);
        }

        $install_id = $this->ensure_local_install_id($settings);
        $response = wp_remote_post($api_base_url . '/integrations/wordpress/connect/start', [
            'timeout' => 15,
            'headers' => [
                'Accept' => 'application/json',
                'Content-Type' => 'application/json',
            ],
            'body' => wp_json_encode([
                'email' => $email,
                'install_id' => $install_id,
                'site_url' => home_url('/'),
                'admin_url' => admin_url('admin.php?page=encypher-settings'),
                'site_name' => get_bloginfo('name'),
                'environment' => function_exists('wp_get_environment_type') ? wp_get_environment_type() : 'production',
                'api_base_url' => $api_base_url,
            ]),
        ]);

        if (is_wp_error($response)) {
            return $response;
        }

        $body = json_decode(wp_remote_retrieve_body($response), true);
        if (! is_array($body) || empty($body['success']) || ! isset($body['data']['session_id'])) {
            return new WP_Error('connect_start_failed', __('Unable to start WordPress connect flow.', 'encypher-provenance'), ['status' => 500]);
        }

        $settings['connect_email'] = $email;
        $settings['connect_session_id'] = sanitize_text_field((string) $body['data']['session_id']);
        $settings['api_base_url'] = $api_base_url;
        $settings['install_id'] = $install_id;
        update_option('encypher_provenance_settings', $settings);

        return new WP_REST_Response([
            'success' => true,
            'data' => [
                'session_id' => $settings['connect_session_id'],
                'email' => $email,
                'status' => $body['data']['status'] ?? 'pending_email_verification',
                'email_sent' => ! empty($body['data']['email_sent']),
            ],
        ]);
    }

    public function handle_connect_poll_request(WP_REST_Request $request)
    {
        $settings = get_option('encypher_provenance_settings', []);
        if (! is_array($settings)) {
            $settings = [];
        }

        $session_id = isset($settings['connect_session_id']) ? trim((string) $settings['connect_session_id']) : '';
        $api_base_url = isset($settings['api_base_url']) ? self::normalize_api_base_url((string) $settings['api_base_url']) : 'https://api.encypherai.com/api/v1';
        if ('' === $session_id) {
            return new WP_Error('missing_connect_session', __('No active WordPress connect session found.', 'encypher-provenance'), ['status' => 404]);
        }

        $response = wp_remote_get($api_base_url . '/integrations/wordpress/connect/session/' . rawurlencode($session_id), [
            'timeout' => 15,
            'headers' => [
                'Accept' => 'application/json',
            ],
        ]);

        if (is_wp_error($response)) {
            return $response;
        }

        $body = json_decode(wp_remote_retrieve_body($response), true);
        if (! is_array($body) || empty($body['success']) || ! isset($body['data']) || ! is_array($body['data'])) {
            return new WP_Error('connect_poll_failed', __('Unable to check WordPress connect status.', 'encypher-provenance'), ['status' => 500]);
        }

        $data = $body['data'];
        if (($data['status'] ?? '') === 'completed' && ! empty($data['api_key'])) {
            $settings['api_key'] = sanitize_text_field((string) $data['api_key']);
            $settings['organization_id'] = isset($data['organization_id']) ? sanitize_text_field((string) $data['organization_id']) : '';
            $settings['organization_name'] = isset($data['organization_name']) ? sanitize_text_field((string) $data['organization_name']) : '';
            $settings['connect_session_id'] = '';
            $settings['connect_email'] = '';

            $account = $this->fetch_remote_account($api_base_url, $settings['api_key']);
            if (! is_wp_error($account)) {
                $settings['tier'] = $account['tier'] ?? 'free';
            }

            update_option('encypher_provenance_settings', $settings);

            $this->sync_remote_wordpress_status($api_base_url, $settings['api_key'], [
                'connection_status' => 'connected',
                'organization_id' => $settings['organization_id'],
                'organization_name' => $settings['organization_name'],
                'plugin_installed' => true,
                'connection_tested' => true,
                'last_connection_checked_at' => gmdate('c'),
            ]);
        }

        return new WP_REST_Response([
            'success' => true,
            'data' => $data,
        ]);
    }

    private function fetch_remote_account(string $api_base_url, string $api_key)
    {
        $base = self::normalize_api_base_url($api_base_url);
        if ('' === $base || '' === trim($api_key)) {
            return new \WP_Error('invalid_configuration', __('Missing API base URL or API key.', 'encypher-provenance'));
        }

        $account_url = $base . '/account';
        $cache_key = 'encypher_account_' . md5(strtolower($base) . '|' . substr(hash('sha256', $api_key), 0, 16));
        $cached = get_site_transient($cache_key);
        if (is_array($cached)) {
            return $cached;
        }

        $response = wp_remote_get($account_url, [
            'timeout' => 15,
            'headers' => [
                'Accept' => 'application/json',
                'Authorization' => 'Bearer ' . sanitize_text_field($api_key),
            ],
        ]);

        if (is_wp_error($response)) {
            return $response;
        }

        $status_code = wp_remote_retrieve_response_code($response);
        if ($status_code >= 400) {
            return new \WP_Error('stats_http_error', sprintf(__('Stats request failed with status %d.', 'encypher-provenance'), $status_code));
        }

        $body = json_decode(wp_remote_retrieve_body($response), true);
        if (! is_array($body)) {
            return new \WP_Error('account_parse_error', __('Unable to parse account response.', 'encypher-provenance'));
        }

        $data = isset($body['data']) && is_array($body['data']) ? $body['data'] : [];
        $tier = $data['tier'] ?? 'free';
        if (! in_array($tier, ['free', 'enterprise', 'strategic_partner'], true)) {
            $tier = 'free';
        }

        $account = [
            'tier' => $tier,
            'organization_id' => isset($data['organization_id']) ? sanitize_text_field((string) $data['organization_id']) : '',
            'organization_name' => isset($data['organization_name']) ? sanitize_text_field((string) $data['organization_name']) : '',
        ];

        set_site_transient($cache_key, $account, 15 * MINUTE_IN_SECONDS);

        return $account;
    }

    private function ensure_local_install_id(array $settings): string
    {
        $install_id = isset($settings['install_id']) ? trim((string) $settings['install_id']) : '';
        if ('' !== $install_id) {
            return $install_id;
        }

        $install_id = 'wpi_' . substr(md5(home_url('/') . '|' . admin_url('admin.php?page=encypher-settings') . '|' . wp_generate_uuid4()), 0, 16);
        $settings['install_id'] = $install_id;
        update_option('encypher_provenance_settings', $settings);
        return $install_id;
    }

    private function build_install_payload(array $settings): array
    {
        return [
            'install_id' => $this->ensure_local_install_id($settings),
            'site_url' => home_url('/'),
            'admin_url' => admin_url('admin.php?page=encypher-settings'),
            'site_name' => get_bloginfo('name'),
            'environment' => function_exists('wp_get_environment_type') ? wp_get_environment_type() : 'production',
            'network_id' => is_multisite() ? (string) get_current_network_id() : null,
            'blog_id' => is_multisite() ? get_current_blog_id() : null,
            'is_multisite' => is_multisite(),
            'is_primary' => true,
            'plugin_version' => ENCYPHER_PROVENANCE_VERSION,
        ];
    }

    private function register_remote_wordpress_install(string $api_base_url, string $api_key, array $settings): string
    {
        $base = self::normalize_api_base_url($api_base_url);
        if ('' === $base || '' === trim($api_key)) {
            return isset($settings['install_id']) ? (string) $settings['install_id'] : '';
        }

        $payload = $this->build_install_payload($settings);
        $response = wp_remote_post($base . '/integrations/wordpress/register-install', [
            'timeout' => 15,
            'headers' => [
                'Accept' => 'application/json',
                'Content-Type' => 'application/json',
                'Authorization' => 'Bearer ' . sanitize_text_field($api_key),
            ],
            'body' => wp_json_encode($payload),
        ]);

        if (! is_wp_error($response)) {
            $body = json_decode(wp_remote_retrieve_body($response), true);
            if (is_array($body) && isset($body['data']['registered_install']['install_id'])) {
                $settings['install_id'] = sanitize_text_field((string) $body['data']['registered_install']['install_id']);
                update_option('encypher_provenance_settings', $settings);
                return $settings['install_id'];
            }
        }

        return $payload['install_id'];
    }

    private function sync_remote_wordpress_status(string $api_base_url, string $api_key, array $payload): void
    {
        $base = self::normalize_api_base_url($api_base_url);
        if ('' === $base || '' === trim($api_key)) {
            return;
        }

        $settings = get_option('encypher_provenance_settings', []);
        if (! is_array($settings)) {
            $settings = [];
        }
        $install_id = $this->register_remote_wordpress_install($api_base_url, $api_key, $settings);
        $settings['install_id'] = $install_id;
        $payload = array_merge($this->build_install_payload($settings), $payload, [
            'install_id' => $install_id,
        ]);

        $response = wp_remote_post($base . '/integrations/wordpress/status-sync', [
            'timeout' => 15,
            'headers' => [
                'Accept' => 'application/json',
                'Content-Type' => 'application/json',
                'Authorization' => 'Bearer ' . sanitize_text_field($api_key),
            ],
            'body' => wp_json_encode($payload),
        ]);

        if (is_wp_error($response)) {
            $this->debug_log('WordPress status sync failed: ' . $response->get_error_message());
            return;
        }

        $status_code = wp_remote_retrieve_response_code($response);
        if ($status_code >= 400) {
            $this->debug_log('WordPress status sync returned status ' . $status_code);
            return;
        }

        $this->process_remote_wordpress_actions($base, $api_key, $install_id);
    }

    private function sync_remote_wordpress_verification_event(string $api_base_url, string $api_key, array $payload): void
    {
        $base = self::normalize_api_base_url($api_base_url);
        if ('' === $base || '' === trim($api_key)) {
            return;
        }

        wp_remote_post($base . '/integrations/wordpress/verification-event', [
            'timeout' => 15,
            'headers' => [
                'Accept' => 'application/json',
                'Content-Type' => 'application/json',
                'Authorization' => 'Bearer ' . sanitize_text_field($api_key),
            ],
            'body' => wp_json_encode($payload),
        ]);
    }

    private function process_remote_wordpress_actions(string $api_base_url, string $api_key, string $install_id): void
    {
        if ('' === $install_id) {
            return;
        }

        $response = wp_remote_post($api_base_url . '/integrations/wordpress/' . rawurlencode($install_id) . '/actions/pull', [
            'timeout' => 15,
            'headers' => [
                'Accept' => 'application/json',
                'Authorization' => 'Bearer ' . sanitize_text_field($api_key),
            ],
        ]);

        if (is_wp_error($response)) {
            return;
        }

        $body = json_decode(wp_remote_retrieve_body($response), true);
        $actions = isset($body['data']['actions']) && is_array($body['data']['actions']) ? $body['data']['actions'] : [];
        foreach ($actions as $action) {
            if (! is_array($action) || empty($action['action_id']) || empty($action['action_type'])) {
                continue;
            }

            $result = $this->execute_remote_wordpress_action((string) $action['action_type'], (string) ($action['note'] ?? ''), $api_base_url, $api_key);
            $this->ack_remote_wordpress_action(
                $api_base_url,
                $api_key,
                $install_id,
                (string) $action['action_id'],
                [
                    'status' => $result['status'],
                    'result_message' => $result['result_message'],
                    'completed_at' => gmdate('c'),
                ]
            );
        }
    }

    private function execute_remote_wordpress_action(string $action_type, string $note, string $api_base_url, string $api_key): array
    {
        if ('refresh_status' === $action_type) {
            return [
                'status' => 'completed',
                'result_message' => $note !== '' ? $note : 'Status refresh acknowledged by WordPress.',
            ];
        }

        if ('test_connection' === $action_type) {
            $health = $this->probe_health($api_base_url);
            if (is_wp_error($health)) {
                return [
                    'status' => 'failed',
                    'result_message' => $health->get_error_message(),
                ];
            }

            $settings = get_option('encypher_provenance_settings', []);
            if (is_array($settings)) {
                $settings['connection_last_status'] = 'connected';
                $settings['connection_last_checked_at'] = gmdate('c');
                update_option('encypher_provenance_settings', $settings);
            }

            return [
                'status' => 'completed',
                'result_message' => 'Connection test completed successfully.',
            ];
        }

        return [
            'status' => 'failed',
            'result_message' => 'Unsupported remote action: ' . $action_type,
        ];
    }

    private function ack_remote_wordpress_action(string $api_base_url, string $api_key, string $install_id, string $action_id, array $payload): void
    {
        wp_remote_post($api_base_url . '/integrations/wordpress/' . rawurlencode($install_id) . '/actions/' . rawurlencode($action_id) . '/ack', [
            'timeout' => 15,
            'headers' => [
                'Accept' => 'application/json',
                'Content-Type' => 'application/json',
                'Authorization' => 'Bearer ' . sanitize_text_field($api_key),
            ],
            'body' => wp_json_encode($payload),
        ]);
    }

    private function resolve_usage_snapshot($settings, bool $refresh_remote = false): array
    {
        if (!is_array($settings)) {
            $settings = [];
        }

        $tier = isset($settings['tier']) ? (string) $settings['tier'] : 'free';
        $usage = $this->normalize_usage_snapshot(
            isset($settings['usage']) && is_array($settings['usage']) ? $settings['usage'] : [],
            $tier
        );

        if (! $refresh_remote) {
            return $usage;
        }

        $api_key = isset($settings['api_key']) ? trim((string) $settings['api_key']) : '';
        $api_base_url = isset($settings['api_base_url']) ? trim((string) $settings['api_base_url']) : '';
        if ('' === $api_key || '' === $api_base_url) {
            return $usage;
        }

        $remote_usage = $this->fetch_remote_usage_quota($api_base_url, $api_key, $tier, [
            'usage' => $usage,
        ]);

        if (isset($remote_usage['api_calls']) && is_array($remote_usage['api_calls'])) {
            return $remote_usage;
        }

        return $usage;
    }

    private function fetch_remote_usage_quota(string $api_base_url, string $api_key, string $tier, array $fallback = []): array
    {
        $fallback_usage = isset($fallback['usage']) && is_array($fallback['usage'])
            ? $fallback['usage']
            : [];
        $normalized_fallback = $this->normalize_usage_snapshot($fallback_usage, $tier);
        $base = rtrim((string) $api_base_url, '/');
        if ('' === $base || '' === trim($api_key)) {
            return $normalized_fallback;
        }

        $cache_key = 'encypher_usage_' . md5(strtolower($base) . '|' . substr(hash('sha256', $api_key), 0, 16));
        $cached = get_site_transient($cache_key);
        if (is_array($cached) && isset($cached['api_calls']) && is_array($cached['api_calls'])) {
            return $cached;
        }

        $quota_url = $base . '/account/quota';
        $response = wp_remote_get($quota_url, [
            'timeout' => 15,
            'headers' => [
                'Accept' => 'application/json',
                'Authorization' => 'Bearer ' . sanitize_text_field($api_key),
            ],
        ]);

        if (is_wp_error($response)) {
            return $normalized_fallback;
        }

        $status_code = wp_remote_retrieve_response_code($response);
        if ($status_code >= 400) {
            return $normalized_fallback;
        }

        $body = json_decode(wp_remote_retrieve_body($response), true);
        if (! is_array($body)) {
            return $normalized_fallback;
        }

        $data = isset($body['data']) && is_array($body['data']) ? $body['data'] : [];
        $metrics = isset($data['metrics']) && is_array($data['metrics']) ? $data['metrics'] : [];
        $api_calls = isset($metrics['api_calls']) && is_array($metrics['api_calls']) ? $metrics['api_calls'] : [];

        if (empty($api_calls)) {
            return $normalized_fallback;
        }

        $resolved_usage = $this->normalize_usage_snapshot([
            'api_calls' => [
                'used' => isset($api_calls['used']) ? (int) $api_calls['used'] : 0,
                'limit' => isset($api_calls['limit']) ? (int) $api_calls['limit'] : ('free' === $tier ? 1000 : -1),
                'remaining' => isset($api_calls['remaining']) ? (int) $api_calls['remaining'] : 0,
                'percentage_used' => isset($api_calls['percentage_used']) ? (float) $api_calls['percentage_used'] : 0,
                'is_unlimited' => isset($api_calls['limit']) ? ((int) $api_calls['limit'] < 0) : ('free' !== $tier),
                'reset_date' => isset($data['reset_date']) ? sanitize_text_field((string) $data['reset_date']) : '',
                'period_end' => isset($data['period_end']) ? sanitize_text_field((string) $data['period_end']) : '',
            ],
        ], $tier);

        // Keep this cache short so editor-sidebar status checks remain close to API truth.
        set_site_transient($cache_key, $resolved_usage, 30);

        return $resolved_usage;
    }

    private function normalize_usage_snapshot(array $usage, string $tier): array
    {
        $default_limit = 'free' === $tier ? 1000 : -1;
        $api_calls = isset($usage['api_calls']) && is_array($usage['api_calls']) ? $usage['api_calls'] : $usage;

        $used = isset($api_calls['used']) ? max(0, (int) $api_calls['used']) : 0;
        $limit = isset($api_calls['limit']) ? (int) $api_calls['limit'] : $default_limit;
        $is_unlimited = isset($api_calls['is_unlimited']) ? (bool) $api_calls['is_unlimited'] : ($limit < 0);

        if ($is_unlimited) {
            $limit = -1;
            $remaining = -1;
            $percentage_used = 0.0;
        } else {
            if ($limit <= 0) {
                $limit = $default_limit > 0 ? $default_limit : 1000;
            }
            $remaining = isset($api_calls['remaining'])
                ? max(0, (int) $api_calls['remaining'])
                : max(0, $limit - $used);
            $percentage_used = isset($api_calls['percentage_used'])
                ? (float) $api_calls['percentage_used']
                : ($limit > 0 ? round(($used / $limit) * 100, 2) : 0.0);
        }

        if (! $is_unlimited) {
            $percentage_used = min(100.0, max(0.0, $percentage_used));
        }

        return [
            'api_calls' => [
                'used' => $used,
                'limit' => $limit,
                'remaining' => $remaining,
                'percentage_used' => $percentage_used,
                'is_unlimited' => $is_unlimited,
                'reset_date' => isset($api_calls['reset_date']) ? sanitize_text_field((string) $api_calls['reset_date']) : '',
                'period_end' => isset($api_calls['period_end']) ? sanitize_text_field((string) $api_calls['period_end']) : '',
            ],
        ];
    }

    // =========================================================================
    // CDN Provenance Continuity — Phase 2: WordPress media image signing
    // =========================================================================

    /**
     * Sign the featured image of a post via POST /api/v1/cdn/images/sign and
     * persist the returned record_id / manifest_url as post meta so that the
     * C2PA-Manifest-URL response header can be injected for image-carrying posts.
     */
    private function sign_featured_image(int $post_id): void
    {
        $thumbnail_id = get_post_thumbnail_id($post_id);
        if (!$thumbnail_id) {
            return; // No featured image
        }

        $file_path = get_attached_file($thumbnail_id);
        if (!$file_path || !file_exists($file_path)) {
            $this->debug_log(sprintf('Featured image file not found for post %d (attachment %d)', $post_id, $thumbnail_id));
            return;
        }

        $mime_type = get_post_mime_type($thumbnail_id);
        $supported = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
        if (!in_array($mime_type, $supported, true)) {
            $this->debug_log(sprintf('Unsupported image mime type %s for post %d', $mime_type, $post_id));
            return;
        }

        $image_data = file_get_contents($file_path);
        if ($image_data === false) {
            $this->debug_log(sprintf('Could not read image file for post %d', $post_id));
            return;
        }

        $original_url = wp_get_attachment_url($thumbnail_id) ?: '';

        // POST multipart to /cdn/images/sign
        $boundary = wp_generate_password(24, false);
        $body = "--{$boundary}\r\n";
        $body .= "Content-Disposition: form-data; name=\"file\"; filename=\"" . basename($file_path) . "\"\r\n";
        $body .= "Content-Type: {$mime_type}\r\n\r\n";
        $body .= $image_data . "\r\n";
        $body .= "--{$boundary}\r\n";
        $body .= "Content-Disposition: form-data; name=\"title\"\r\n\r\n";
        $body .= get_the_title($post_id) . "\r\n";
        $body .= "--{$boundary}\r\n";
        $body .= "Content-Disposition: form-data; name=\"original_url\"\r\n\r\n";
        $body .= $original_url . "\r\n";
        $body .= "--{$boundary}--";

        $settings = get_option('encypher_provenance_settings', []);
        $api_key = $settings['api_key'] ?? '';
        $api_url = rtrim($settings['api_url'] ?? 'https://enterprise.encypherai.com', '/');

        $response = wp_remote_post(
            $api_url . '/api/v1/cdn/images/sign',
            [
                'timeout' => 30,
                'headers' => [
                    'Authorization' => 'Bearer ' . $api_key,
                    'Content-Type' => 'multipart/form-data; boundary=' . $boundary,
                ],
                'body' => $body,
            ]
        );

        if (is_wp_error($response)) {
            $this->debug_log(sprintf('Image signing failed for post %d: %s', $post_id, $response->get_error_message()));
            return;
        }

        $status = wp_remote_retrieve_response_code($response);
        if ($status !== 201 && $status !== 200) {
            $this->debug_log(sprintf('Image signing HTTP %d for post %d', $status, $post_id));
            return;
        }

        $data = json_decode(wp_remote_retrieve_body($response), true);
        if (!is_array($data)) {
            return;
        }

        $record_id    = $data['record_id']    ?? '';
        $manifest_url = $data['manifest_url'] ?? '';

        if ($record_id) {
            update_post_meta($post_id, '_encypher_image_record_id', sanitize_text_field($record_id));
            update_post_meta($post_id, '_encypher_image_manifest_url', esc_url_raw($manifest_url));
            update_post_meta($thumbnail_id, '_encypher_image_record_id', sanitize_text_field($record_id));
            $this->debug_log(sprintf('Image signed for post %d: record_id=%s', $post_id, $record_id));
        }
    }

    /**
     * Inject a C2PA-Manifest-URL response header for single post/page responses
     * that have a signed featured image.
     *
     * Hooked on send_headers.
     */
    public function inject_image_provenance_header(): void
    {
        // Only inject on single post/page responses
        if (!is_singular()) {
            return;
        }

        $post_id = get_the_ID();
        if (!$post_id) {
            return;
        }

        $manifest_url = get_post_meta($post_id, '_encypher_image_manifest_url', true);
        if ($manifest_url) {
            header('C2PA-Manifest-URL: ' . esc_url($manifest_url));
        }
    }

    /**
     * Return the CDN image record ID stored for a post's featured image.
     */
    public function get_image_record_id(int $post_id): string
    {
        return (string) get_post_meta($post_id, '_encypher_image_record_id', true);
    }

    /**
     * Return the CDN manifest URL stored for a post's featured image.
     */
    public function get_image_manifest_url(int $post_id): string
    {
        return (string) get_post_meta($post_id, '_encypher_image_manifest_url', true);
    }
}
