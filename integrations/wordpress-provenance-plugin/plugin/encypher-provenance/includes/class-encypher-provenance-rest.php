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
        add_action('transition_post_status', [$this, 'auto_sign_on_publish'], 10, 3);
        add_action('save_post', [$this, 'auto_sign_on_update'], 30, 3); // Higher priority to run after mark_post_needs_verification
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
        $settings = get_option('encypher_assurance_settings', []);
        $metadata_format = $settings['metadata_format'] ?? 'c2pa';
        $add_hard_binding = $settings['add_hard_binding'] ?? true;
        
        // Check for existing C2PA embeddings and verify them
        $existing_embeddings = $this->detect_c2pa_embeddings($post->post_content);
        $clean_content = $post->post_content;
        
        if ($existing_embeddings['count'] > 0) {
            // Log existing embeddings for audit trail
            error_log(sprintf(
                'Encypher: Post %d has %d existing C2PA embedding(s). Stripping before re-signing.',
                $post_id,
                $existing_embeddings['count']
            ));
            
            // Strip all existing embeddings to ensure clean re-signing
            $clean_content = $this->strip_c2pa_embeddings($post->post_content);
            
            // Verify stripping was successful
            $verify_clean = $this->detect_c2pa_embeddings($clean_content);
            if ($verify_clean['count'] > 0) {
                return new WP_Error(
                    'embedding_strip_failed',
                    __('Failed to strip existing C2PA embeddings. Please contact support.', 'encypher-provenance'),
                    ['status' => 500]
                );
            }
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
            $previous_instance_id = get_post_meta($post_id, '_encypher_assurance_instance_id', true);
            if ($previous_instance_id) {
                error_log(sprintf(
                    'Encypher: Post %d is being edited. Previous instance_id: %s',
                    $post_id,
                    $previous_instance_id
                ));
            }
        }
        
        // Get tier from settings (default to free)
        $tier = isset($settings['tier']) ? $settings['tier'] : 'free';
        // Coerce legacy tier names to canonical 'free'
        if (in_array($tier, ['starter', 'professional', 'business'], true)) {
            $tier = 'free';
        }
        
        $is_free = ($tier === 'free');
        $is_nma_member = isset($settings['nma_member']) ? (bool) $settings['nma_member'] : false;

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
        
        // Build unified /sign request with tier-gated options
        // Features are automatically gated server-side based on API key tier
        $payload = [
            'text' => $clean_content,
            'document_id' => $unique_document_id,
            'document_title' => $post->post_title,
            'document_url' => get_permalink($post),
            'metadata' => [
                'author' => get_the_author_meta('display_name', $post->post_author),
                'published_at' => $post->post_date,
                'wordpress_post_id' => $post_id,
                'tier' => $tier,
                'nma_member' => $is_nma_member,
                'organization_name' => $organization_name,
                'signing_mode' => $signing_mode,
            ],
            'options' => [
                'document_type' => 'article',
                'claim_generator' => 'WordPress/Encypher Plugin v' . ENCYPHER_ASSURANCE_VERSION,
                'action' => $action_type,
                'manifest_mode' => 'micro_ecc_c2pa',
                'segmentation_level' => 'sentence',
                'index_for_attribution' => true,
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

        // Extract embedded content from Enterprise API response
        $embedded_content = $result['signed_text'] ?? ($result['embedded_content'] ?? null);
        if (! is_string($embedded_content) || '' === $embedded_content) {
            return new WP_Error('invalid_response', __('Unexpected response from Enterprise API.', 'encypher-provenance'), ['status' => 502]);
        }

        $final_check = $this->detect_c2pa_embeddings($embedded_content);
        if ($final_check['count'] < 1) {
            error_log(sprintf(
                'Encypher: C2PA compliance violation! Expected at least 1 wrapper, found %d in post %d',
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
        
        error_log(sprintf(
            'Encypher: Post %d successfully signed with C2PA wrapper (spec compliant)',
            $post_id
        ));

        $document_id = isset($result['document_id']) ? sanitize_text_field((string) $result['document_id']) : '';
        $merkle_root = $result['merkle_root'] ?? null;
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
        $verification_url = $verification_id ? home_url('/c2pa-verify/') . urlencode($verification_id) : '';

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
        update_post_meta($post_id, '_encypher_assurance_cached_content_hash', md5((string) $embedded_content));
        update_post_meta($post_id, '_encypher_assurance_status', 'c2pa_protected');
        update_post_meta($post_id, '_encypher_assurance_document_id', $document_id);
        update_post_meta($post_id, '_encypher_assurance_verification_url', $verification_url);
        update_post_meta($post_id, '_encypher_assurance_total_sentences', $total_sentences);
        update_post_meta($post_id, '_encypher_assurance_last_signed', current_time('mysql'));
        update_post_meta($post_id, '_encypher_manifest_id', $document_id);
        update_post_meta($post_id, '_encypher_marked_date', current_time('mysql'));
        update_post_meta($post_id, '_encypher_assurance_signing_mode', $signing_mode);
        if ($signing_profile_id) {
            update_post_meta($post_id, '_encypher_assurance_signing_profile_id', $signing_profile_id);
        } else {
            delete_post_meta($post_id, '_encypher_assurance_signing_profile_id');
        }
        
        // Store new instance_id for next edit's provenance chain
        if ($new_instance_id) {
            update_post_meta($post_id, '_encypher_assurance_instance_id', $new_instance_id);
            error_log(sprintf(
                'Encypher: Stored new instance_id for post %d: %s',
                $post_id,
                $new_instance_id
            ));
        }
        
        // Clear action type meta so it doesn't get reused
        delete_post_meta($post_id, '_encypher_action_type');
        
        // Store Merkle tree info
        if (!empty($merkle_root)) {
            update_post_meta($post_id, '_encypher_merkle_root_hash', $merkle_root);
        }
        $this->persist_merkle_snapshot($post_id, $merkle_root ? ['root_hash' => $merkle_root] : []);
        $this->persist_sentence_segments(
            $post_id,
            isset($result['embeddings']) && is_array($result['embeddings']) ? $result['embeddings'] : []
        );
        
        // Clear any pending marking flags
        delete_post_meta($post_id, '_encypher_needs_marking');
        delete_post_meta($post_id, '_encypher_action_type');
        delete_post_meta($post_id, '_encypher_assurance_verification');

        return new WP_REST_Response([
            'status' => 'c2pa_protected',
            'document_id' => $document_id,
            'verification_url' => $verification_url,
            'embedded_content' => $embedded_content,
            'total_sentences' => $total_sentences,
            'merkle_tree' => $merkle_tree,
            'statistics' => $statistics,
        ]);
    }

    public function handle_status_request(WP_REST_Request $request)
    {
        $post_id = (int) $request->get_param('post_id');
        $status = get_post_meta($post_id, '_encypher_assurance_status', true);
        $signature = get_post_meta($post_id, '_encypher_assurance_signature', true);
        $document_id = get_post_meta($post_id, '_encypher_assurance_document_id', true);
        $instance_id = get_post_meta($post_id, '_encypher_assurance_instance_id', true);
        $total_sentences = (int) get_post_meta($post_id, '_encypher_assurance_total_sentences', true);
        $last_signed = get_post_meta($post_id, '_encypher_assurance_last_signed', true);
        $merkle_root_hash = get_post_meta($post_id, '_encypher_merkle_root_hash', true);
        $verification = get_post_meta($post_id, '_encypher_assurance_verification', true);
        $sentences = $this->get_sentence_segments_payload($post_id);
        $merkle_snapshot = $this->get_merkle_snapshot($post_id);
        $settings = get_option('encypher_assurance_settings', []);

        // Generate verification URL using instance_id if available, otherwise document_id
        $verification_id = $instance_id ?: $document_id;
        $verification_url = $verification_id ? home_url('/c2pa-verify/') . urlencode($verification_id) : '';

        return new WP_REST_Response([
            'status' => $status ?: 'not_signed',
            'signature' => $signature,
            'document_id' => $document_id,
            'instance_id' => $instance_id,
            'verification_url' => $verification_url,
            'total_sentences' => $total_sentences,
            'last_signed' => $last_signed,
            'merkle_root_hash' => $merkle_root_hash,
            'verification' => $verification,
            'sentences' => $sentences['items'],
            'sentences_total' => $sentences['total'],
            'merkle' => $merkle_snapshot,
            'tier' => isset($settings['tier']) ? $settings['tier'] : 'free',
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

        $settings = get_option('encypher_assurance_settings', []);
        $tier = isset($settings['tier']) ? $settings['tier'] : 'free';
        // /verify is deprecated (410 Gone) — always use /verify/advanced
        $endpoint = '/verify/advanced';
        $require_auth = true;

        // Check for cached verification (disabled in development, 5 minute cache in production)
        // Set WP_DEBUG to true in wp-config.php for development mode
        $cache_enabled = !defined('WP_DEBUG') || !WP_DEBUG;
        $cache_key = 'encypher_verify_' . $post_id . '_' . md5($raw_content . '|' . $endpoint);
        
        if ($cache_enabled) {
            $cached = get_transient($cache_key);
            if (false !== $cached && is_array($cached)) {
                error_log(sprintf('Encypher: Returning cached verification for post %d', $post_id));
                $cached['cached'] = true;
                return new WP_REST_Response($cached);
            }
        } else {
            error_log(sprintf('Encypher: Cache disabled (WP_DEBUG=true), performing fresh verification for post %d', $post_id));
        }

        $payload = [
            'text' => $raw_content,
        ];

        $payload['segmentation_level'] = 'sentence';
        $payload['search_scope'] = 'organization';
        $payload['include_attribution'] = false;
        $payload['detect_plagiarism'] = false;
        $payload['include_heat_map'] = false;
        $payload['min_match_percentage'] = 0.0;

        $verification_mode = 'advanced';
        error_log(sprintf('Encypher: Calling %s for post %d (content length: %d)', $endpoint, $post_id, strlen($raw_content)));
        $response = $this->call_backend($endpoint, $payload, $require_auth);
        if (is_wp_error($response)) {
            error_log(sprintf('Encypher: Verification API error for post %d: %s', $post_id, $response->get_error_message()));
            return $response;
        }

        $normalized = [
            'valid' => false,
            'tampered' => false,
            'reason_code' => null,
            'signer_id' => null,
            'signer_name' => null,
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
            $normalized['signer_name'] = isset($verdict['signer_name']) ? (string) $verdict['signer_name'] : null;
            $normalized['verified_at'] = isset($verdict['timestamp']) ? (string) $verdict['timestamp'] : null;
            if (isset($verdict['details']) && is_array($verdict['details']) && isset($verdict['details']['manifest']) && is_array($verdict['details']['manifest'])) {
                $normalized['metadata'] = $verdict['details']['manifest'];
            }
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

        error_log(sprintf('Encypher: Verification response for post %d: valid=%s', $post_id, $normalized['valid'] ? 'true' : 'false'));

        // Cache the verification result for 5 minutes (only if caching is enabled)
        if ($cache_enabled) {
            set_transient($cache_key, $normalized, 5 * MINUTE_IN_SECONDS);
        }

        // Store verification result in post meta
        update_post_meta($post_id, '_encypher_assurance_verification', $normalized);
        update_post_meta($post_id, '_encypher_assurance_last_verified', current_time('mysql'));
        
        // Store instance_id for public provenance lookup
        if (!empty($normalized['metadata']['instance_id'])) {
            update_post_meta($post_id, '_encypher_assurance_instance_id', $normalized['metadata']['instance_id']);
        }
        
        // Update status based on verification
        $status = 'not_signed';
        if (!empty($normalized['valid'])) {
            $status = 'c2pa_verified';
        } elseif (!empty($normalized['error'])) {
            $status = 'verification_failed';
        }
        update_post_meta($post_id, '_encypher_assurance_status', $status);

        $normalized['cached'] = false;
        return new WP_REST_Response($normalized);
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
                        'key' => '_encypher_assurance_instance_id',
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
        $document_id = get_post_meta($post_id, '_encypher_assurance_document_id', true);
        $status = get_post_meta($post_id, '_encypher_assurance_status', true);
        $total_sentences = (int) get_post_meta($post_id, '_encypher_assurance_total_sentences', true);
        $last_signed = get_post_meta($post_id, '_encypher_assurance_last_signed', true);
        $last_verified = get_post_meta($post_id, '_encypher_assurance_last_verified', true);
        $merkle_root = get_post_meta($post_id, '_encypher_merkle_root_hash', true);
        $merkle_leaves = get_post_meta($post_id, '_encypher_merkle_total_leaves', true);
        $verification = get_post_meta($post_id, '_encypher_assurance_verification', true);
        $sentences = $this->get_sentence_segments_payload($post_id);
        $merkle_snapshot = $this->get_merkle_snapshot($post_id);

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
            'merkle_tree' => [
                'root_hash' => $merkle_root,
                'total_leaves' => $merkle_leaves,
                'tree_depth' => $merkle_snapshot['tree_depth'],
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
        // Only process posts (not pages, custom post types, etc.) - can be configured
        if ('post' !== $post->post_type) {
            return;
        }

        // Only act when post becomes published (not already published)
        if ('publish' !== $new_status || 'publish' === $old_status) {
            return;
        }

        // Check if auto-signing is enabled
        $settings = get_option('encypher_assurance_settings', []);
        $auto_sign = isset($settings['auto_mark_on_publish']) ? (bool) $settings['auto_mark_on_publish'] : true;
        
        if (!$auto_sign) {
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
            error_log("Encypher: Skipping auto_sign_on_update - is_signing flag is true");
            return;
        }

        // Skip autosaves and revisions
        if (wp_is_post_autosave($post_id) || wp_is_post_revision($post_id)) {
            return;
        }

        // Only process posts (not pages, custom post types, etc.)
        if ('post' !== $post->post_type) {
            return;
        }

        // Only process published posts
        if ('publish' !== $post->post_status) {
            error_log(sprintf('Encypher: Post %d status is %s, not publish', $post_id, $post->post_status));
            return;
        }
        
        // Don't trigger on initial publish (status change from non-publish to publish)
        // The initial signing will be handled by the first wp_insert_post_data hook
        if ($post_before && is_object($post_before) && $post_before->post_status !== 'publish') {
            error_log(sprintf('Encypher: Skipping auto_sign_on_update - initial publish (status changed from %s to publish)', $post_before->post_status));
            return;
        }

        // Check if auto-signing on update is enabled
        $settings = get_option('encypher_assurance_settings', []);
        $auto_sign_on_update = isset($settings['auto_mark_on_update']) ? (bool) $settings['auto_mark_on_update'] : true;
        
        if (!$auto_sign_on_update) {
            error_log('Encypher: Auto-signing on update is disabled in settings');
            return;
        }

        // Check if post is already marked
        $is_marked = get_post_meta($post_id, '_encypher_marked', true);
        error_log(sprintf('Encypher: Post %d is_marked = %s', $post_id, $is_marked ? 'true' : 'false'));
        
        if (!$is_marked) {
            // Not signed yet - sign it now with c2pa.created
            error_log(sprintf('Encypher: Post %d not marked yet, signing now with c2pa.created', $post_id));
            update_post_meta($post_id, '_encypher_action_type', 'c2pa.created');
            $this->perform_signing($post_id, false); // false = new signing
            return;
        }

        // Check if action type is already set (e.g., by admin hooks)
        $action_type = get_post_meta($post_id, '_encypher_action_type', true);
        if ($action_type === 'c2pa.edited') {
            // Action already set to edited - honor it and re-sign
            error_log(sprintf('Encypher: Post %d action type already set to c2pa.edited, performing re-sign', $post_id));
            $this->perform_signing($post_id, true); // true = is_update
            return;
        }

        // Post is already signed - check if content changed
        // Compare against the CACHED content hash (which was set after the last signing)
        // This prevents re-signing when the only change is the C2PA wrapper itself
        $cached_hash = get_post_meta($post_id, '_encypher_assurance_cached_content_hash', true);
        $current_hash = md5($post->post_content);
        
        error_log(sprintf(
            'Encypher: Post %d hash check - cached: %s, current: %s',
            $post_id,
            $cached_hash ? substr($cached_hash, 0, 8) : 'none',
            substr($current_hash, 0, 8)
        ));
        
        if ($cached_hash && $cached_hash === $current_hash) {
            // Content unchanged since last signing - skip re-signing
            error_log(sprintf('Encypher: Post %d content unchanged since last signing, skipping re-sign', $post_id));
            return;
        }
        
        // Content changed - re-sign with c2pa.edited action
        error_log(sprintf(
            'Encypher: Content changed for post %d, triggering re-sign with c2pa.edited',
            $post_id
        ));
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
                error_log(sprintf(
                    'Encypher: Auto-sign failed for post %d: %s',
                    $post_id,
                    $response->get_error_message()
                ));
            } else {
                error_log(sprintf(
                    'Encypher: Auto-signed post %d (%s)',
                    $post_id,
                    $is_update ? 'updated' : 'new'
                ));
            }
        } catch (\Exception $e) {
            error_log(sprintf(
                'Encypher: Auto-sign exception for post %d: %s',
                $post_id,
                $e->getMessage()
            ));
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
     * Detect C2PA embeddings in text.
     * 
     * Scans for C2PA text wrapper magic bytes encoded in Unicode variation selectors.
     * Per C2PA spec, each wrapper starts with magic: 0x4332504154585400 ("C2PATXT\0")
     * 
     * @param string $text Text to scan for C2PA embeddings
     * @return array ['count' => int, 'positions' => array] Number of embeddings found and their positions
     */
    private function detect_c2pa_embeddings(string $text): array
    {
        // Look for sequences of variation selectors (indicators of C2PA embedding)
        // C2PA magic bytes: C2PATXT\0 (0x43 0x32 0x50 0x41 0x54 0x58 0x54 0x00)
        // When encoded as variation selectors, this creates a detectable pattern

        $pattern = '/\x{FEFF}([\x{FE00}-\x{FE0F}\x{E0100}-\x{E01EF}]+)/u';
        preg_match_all($pattern, $text, $matches, PREG_OFFSET_CAPTURE);

        $magic = [0x43, 0x32, 0x50, 0x41, 0x54, 0x58, 0x54, 0x00];
        $embedding_count = 0;
        $positions = [];

        foreach ($matches[1] as $index => $match) {
            $vs_sequence = $match[0];
            $chars = preg_split('//u', $vs_sequence, -1, PREG_SPLIT_NO_EMPTY);
            if (!is_array($chars) || count($chars) < 8) {
                continue;
            }

            $decoded = [];
            for ($i = 0; $i < 8; $i++) {
                $codepoint = mb_ord($chars[$i], 'UTF-8');
                $byte = null;

                if ($codepoint >= 0xFE00 && $codepoint <= 0xFE0F) {
                    $byte = $codepoint - 0xFE00;
                } elseif ($codepoint >= 0xE0100 && $codepoint <= 0xE01EF) {
                    $byte = ($codepoint - 0xE0100) + 16;
                }

                if ($byte === null) {
                    $decoded = [];
                    break;
                }

                $decoded[] = $byte;
            }

            if ($decoded === $magic) {
                $embedding_count++;
                $positions[] = $matches[0][$index][1];
            }
        }

        return [
            'count' => $embedding_count,
            'positions' => $positions,
        ];
    }

    /**
     * Strip existing C2PA embeddings from text.
     * 
     * Removes invisible Unicode variation selectors that encode C2PA manifests.
     * This prevents "multiple wrappers" errors when re-signing content.
     * 
     * @param string $text Text potentially containing C2PA embeddings
     * @return string Clean text without C2PA embeddings
     */
    private function strip_c2pa_embeddings(string $text): string
    {
        // Remove Unicode variation selectors used for C2PA embeddings
        // U+FE00-U+FE0F (Variation Selectors 1-16)
        // U+E0100-U+E01EF (Variation Selectors 17-256)
        // U+FEFF (Zero-Width No-Break Space / BOM)
        
        $text = preg_replace('/[\x{FE00}-\x{FE0F}\x{E0100}-\x{E01EF}\x{FEFF}]/u', '', $text);
        
        return $text;
    }

    private function persist_sentence_segments(int $post_id, array $embeddings): void
    {
        if (empty($embeddings) || !is_array($embeddings)) {
            delete_post_meta($post_id, '_encypher_assurance_sentence_segments');
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
            update_post_meta($post_id, '_encypher_assurance_sentence_segments', $normalized);
        } else {
            delete_post_meta($post_id, '_encypher_assurance_sentence_segments');
        }
    }

    private function get_sentence_segments_payload(int $post_id): array
    {
        $segments = get_post_meta($post_id, '_encypher_assurance_sentence_segments', true);
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

    private function persist_merkle_snapshot(int $post_id, array $merkle_tree): void
    {
        if (empty($merkle_tree)) {
            delete_post_meta($post_id, '_encypher_merkle_snapshot');
            return;
        }

        $snapshot = [
            'root_hash' => isset($merkle_tree['root_hash']) ? sanitize_text_field((string) $merkle_tree['root_hash']) : '',
            'total_leaves' => isset($merkle_tree['total_leaves']) ? (int) $merkle_tree['total_leaves'] : 0,
            'tree_depth' => isset($merkle_tree['tree_depth']) ? (int) $merkle_tree['tree_depth'] : null,
        ];

        update_post_meta($post_id, '_encypher_merkle_snapshot', $snapshot);
    }

    private function get_merkle_snapshot(int $post_id): array
    {
        $snapshot = get_post_meta($post_id, '_encypher_merkle_snapshot', true);
        if (!is_array($snapshot)) {
            return [
                'root_hash' => '',
                'total_leaves' => 0,
                'tree_depth' => null,
            ];
        }

        return [
            'root_hash' => isset($snapshot['root_hash']) ? $snapshot['root_hash'] : '',
            'total_leaves' => isset($snapshot['total_leaves']) ? (int) $snapshot['total_leaves'] : 0,
            'tree_depth' => $snapshot['tree_depth'] ?? null,
        ];
    }

    /**
     * Perform HTTP request to backend and decode JSON response.
     */
    private function call_backend(string $path, array $body, bool $require_auth)
    {
        $settings = get_option('encypher_assurance_settings', []);
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
        if ($api_key) {
            $headers['Authorization'] = 'Bearer ' . sanitize_text_field($api_key);
        } elseif ($require_auth) {
            return new WP_Error('missing_api_key', __('Please configure an Encypher API key before signing.', 'encypher-provenance'), ['status' => 401]);
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
                        error_log('Encypher: Validation error details: ' . $message);
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
            $settings = get_option('encypher_assurance_settings', []);
            $api_base_url = isset($settings['api_base_url']) ? $settings['api_base_url'] : '';
            $api_key = isset($settings['api_key']) ? $settings['api_key'] : '';
        }

        if (empty($api_base_url)) {
            return new WP_Error(
                'no_api_url',
                __('No API URL configured', 'encypher-provenance'),
                ['status' => 400]
            );
        }

        // Test health endpoint (at root, not under /api/v1)
        // Remove /api/v1 suffix if present to get base URL
        $base_url = preg_replace('#/api/v1/?$#', '', rtrim($api_base_url, '/'));
        $health_url = $base_url . '/health';
        
        $health_response = wp_remote_get($health_url, [
            'timeout' => 10,
            'headers' => $api_key ? ['Authorization' => 'Bearer ' . $api_key] : [],
        ]);

        if (is_wp_error($health_response)) {
            return new WP_Error(
                'connection_failed',
                sprintf(
                    __('Connection failed: %s', 'encypher-provenance'),
                    $health_response->get_error_message()
                ),
                ['status' => 500]
            );
        }

        $status_code = wp_remote_retrieve_response_code($health_response);
        $body = wp_remote_retrieve_body($health_response);

        if ($status_code !== 200) {
            return new WP_Error(
                'health_check_failed',
                sprintf(
                    __('Health check failed with status %d', 'encypher-provenance'),
                    $status_code
                ),
                ['status' => $status_code]
            );
        }

        $health_data = json_decode($body, true);

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
            
            if ($api_key === 'demo-local-key') {
                $result['organization'] = [
                    'organization_id' => 'org_demo',
                    'name' => 'Demo Organization',
                    'tier' => 'free'
                ];
            } else {
                $account = $this->fetch_remote_account($api_base_url, $api_key);
                if (! is_wp_error($account)) {
                    $result['organization'] = [
                        'organization_id' => $account['organization_id'] ?: 'org_unknown',
                        'name' => $account['organization_name'] ?: ($account['organization_id'] ?: __('Your organization', 'encypher-provenance')),
                        'tier' => $account['tier'],
                    ];
                }
            }
        } else {
            $result['api_key_configured'] = false;
            $result['auth_note'] = 'No API key configured - using demo mode';
        }

        return new WP_REST_Response($result);
    }

    private function fetch_remote_account(string $api_base_url, string $api_key)
    {
        $base = rtrim((string) $api_base_url, '/');
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
        // Coerce legacy tier names to canonical 'free'
        if (in_array($tier, ['starter', 'professional', 'business'], true)) {
            $tier = 'free';
        }
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
}
