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

        // Check if already signed (prevent duplicate signing)
        $is_marked = get_post_meta($post_id, '_encypher_marked', true);
        if ($is_marked) {
            return new WP_Error(
                'already_signed',
                __('This post is already signed with C2PA. To update the signature, edit and re-publish the post.', 'encypher-provenance'),
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
        
        // Build Enterprise API payload for /enterprise/embeddings/encode-with-embeddings
        $payload = [
            'text' => $clean_content,
            'document_id' => 'wp_post_' . $post_id,
            'organization_id' => 'org_demo',  // TODO: Get from settings
            'action' => $action_type,
            'previous_instance_id' => $previous_instance_id,
            // Free tier: document-level only (no segmentation, one C2PA wrapper)
            // Pro/Enterprise: sentence-level segmentation + one C2PA wrapper
            'segmentation_level' => ($tier === 'free') ? 'document' : 'sentence',
            'metadata' => [
                'title' => $post->post_title,
                'author' => get_the_author_meta('display_name', $post->post_author),
                'published_at' => $post->post_date,
                'url' => get_permalink($post),
                'wordpress_post_id' => $post_id,
                'tier' => $tier,
            ],
            'embedding_options' => [
                'metadata_format' => $metadata_format,
                'add_hard_binding' => $add_hard_binding,
                'claim_generator' => 'WordPress/Encypher Plugin v' . ENCYPHER_ASSURANCE_VERSION,
            ],
        ];
        
        // Add license info if available
        if (isset($metadata['license_type'])) {
            $payload['license_info'] = [
                'type' => sanitize_text_field($metadata['license_type']),
                'url' => isset($metadata['license_url']) ? esc_url_raw($metadata['license_url']) : '',
            ];
        }

        $response = $this->call_backend('/enterprise/embeddings/encode-with-embeddings', $payload, true);
        if (is_wp_error($response)) {
            return $response;
        }

        // Extract embedded content from Enterprise API response
        $embedded_content = $response['embedded_content'] ?? null;
        if (! is_string($embedded_content) || '' === $embedded_content) {
            return new WP_Error('invalid_response', __('Unexpected response from Enterprise API.', 'encypher-provenance'), ['status' => 502]);
        }

        // Verify the embedded content has exactly ONE C2PA wrapper (spec compliant)
        $final_check = $this->detect_c2pa_embeddings($embedded_content);
        if ($final_check['count'] !== 1) {
            error_log(sprintf(
                'Encypher: C2PA compliance violation! Expected 1 wrapper, found %d in post %d',
                $final_check['count'],
                $post_id
            ));
            return new WP_Error(
                'c2pa_compliance_violation',
                sprintf(
                    __('C2PA compliance check failed: Expected 1 wrapper, found %d. Please contact support.', 'encypher-provenance'),
                    $final_check['count']
                ),
                ['status' => 500]
            );
        }
        
        error_log(sprintf(
            'Encypher: Post %d successfully signed with C2PA wrapper (spec compliant)',
            $post_id
        ));

        $document_id = isset($response['document_id']) ? sanitize_text_field((string) $response['document_id']) : '';
        $merkle_tree = $response['merkle_tree'] ?? [];
        $statistics = $response['statistics'] ?? [];
        $total_sentences = isset($statistics['total_sentences']) ? (int) $statistics['total_sentences'] : 0;
        
        // Generate verification URL using instance_id from embedded content
        // Extract instance_id from the C2PA manifest in embedded_content
        $instance_id = null;
        if ($embedded_content) {
            // The instance_id will be available after verification
            // For now, use document_id as fallback
            $verification_url = home_url('/c2pa-verify/') . urlencode($document_id);
        } else {
            $verification_url = home_url('/c2pa-verify/') . urlencode($document_id);
        }

        $this->is_signing = true;
        $updated = wp_update_post([
            'ID' => $post_id,
            'post_content' => $embedded_content,
        ], true);
        $this->is_signing = false;

        if (is_wp_error($updated)) {
            return $updated;
        }

        // Extract instance_id from response for provenance chain
        $new_instance_id = null;
        if (!empty($response['metadata']['instance_id'])) {
            $new_instance_id = sanitize_text_field($response['metadata']['instance_id']);
        }
        
        // Store metadata about the C2PA marking
        update_post_meta($post_id, '_encypher_marked', true); // Mark as signed
        update_post_meta($post_id, '_encypher_assurance_cached_content_hash', md5((string) $embedded_content));
        update_post_meta($post_id, '_encypher_assurance_status', 'c2pa_protected');
        update_post_meta($post_id, '_encypher_assurance_document_id', $document_id);
        update_post_meta($post_id, '_encypher_assurance_verification_url', $verification_url);
        update_post_meta($post_id, '_encypher_assurance_total_sentences', $total_sentences);
        update_post_meta($post_id, '_encypher_assurance_last_signed', current_time('mysql'));
        update_post_meta($post_id, '_encypher_manifest_id', $document_id);
        update_post_meta($post_id, '_encypher_marked_date', current_time('mysql'));
        
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
        if (!empty($merkle_tree)) {
            update_post_meta($post_id, '_encypher_merkle_root_hash', $merkle_tree['root_hash'] ?? '');
            update_post_meta($post_id, '_encypher_merkle_total_leaves', $merkle_tree['total_leaves'] ?? 0);
        }
        
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
        ]);
    }

    public function handle_verify_request(WP_REST_Request $request)
    {
        $post_id = (int) $request->get_param('post_id');
        $post = get_post($post_id);
        if (! $post) {
            return new WP_Error('invalid_post', __('Invalid post.', 'encypher-provenance'), ['status' => 400]);
        }

        // Get raw post content to preserve invisible Unicode characters
        $raw_content = get_post_field('post_content', $post_id, 'raw');

        // Check for cached verification (disabled in development, 5 minute cache in production)
        // Set WP_DEBUG to true in wp-config.php for development mode
        $cache_enabled = !defined('WP_DEBUG') || !WP_DEBUG;
        $cache_key = 'encypher_verify_' . $post_id . '_' . md5($raw_content);
        
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

        // Use public verification API endpoint (no auth required)
        $payload = [
            'text' => $raw_content,
        ];

        error_log(sprintf('Encypher: Calling /public/extract-and-verify for post %d (content length: %d)', $post_id, strlen($raw_content)));
        $response = $this->call_backend('/public/extract-and-verify', $payload, false);
        if (is_wp_error($response)) {
            error_log(sprintf('Encypher: Verification API error for post %d: %s', $post_id, $response->get_error_message()));
            return $response;
        }
        error_log(sprintf('Encypher: Verification response for post %d: valid=%s', $post_id, isset($response['valid']) ? ($response['valid'] ? 'true' : 'false') : 'null'));

        // Cache the verification result for 5 minutes (only if caching is enabled)
        if ($cache_enabled) {
            set_transient($cache_key, $response, 5 * MINUTE_IN_SECONDS);
        }

        // Store verification result in post meta
        update_post_meta($post_id, '_encypher_assurance_verification', $response);
        update_post_meta($post_id, '_encypher_assurance_last_verified', current_time('mysql'));
        
        // Store instance_id for public provenance lookup
        if (!empty($response['metadata']['instance_id'])) {
            update_post_meta($post_id, '_encypher_assurance_instance_id', $response['metadata']['instance_id']);
        }
        
        // Update status based on verification
        $status = 'not_signed';
        if (!empty($response['valid'])) {
            $status = 'c2pa_verified';
        } elseif (!empty($response['error'])) {
            $status = 'verification_failed';
        }
        update_post_meta($post_id, '_encypher_assurance_status', $status);

        $response['cached'] = false;
        return new WP_REST_Response($response);
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
            $query = new WP_Query($args);
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
            ],
            'verification' => $verification ?: null,
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
        $auto_sign = isset($settings['auto_sign_on_publish']) ? (bool) $settings['auto_sign_on_publish'] : true;
        
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
            
            // Temporarily bypass the "already signed" check for updates
            if ($is_update) {
                delete_post_meta($post_id, '_encypher_marked');
            }
            
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
        
        $variation_selector_pattern = '/[\x{FE00}-\x{FE0F}\x{E0100}-\x{E01EF}]+/u';
        preg_match_all($variation_selector_pattern, $text, $matches, PREG_OFFSET_CAPTURE);
        
        // Count sequences that are long enough to be C2PA wrappers (minimum ~100 chars for header + small manifest)
        $embedding_count = 0;
        $positions = [];
        
        foreach ($matches[0] as $match) {
            $sequence_length = mb_strlen($match[0], 'UTF-8');
            if ($sequence_length >= 50) { // Minimum size for a C2PA wrapper
                $embedding_count++;
                $positions[] = $match[1];
            }
        }
        
        return [
            'count' => $embedding_count,
            'positions' => $positions
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

        // Check if API key is configured
        if (!empty($api_key)) {
            $result['api_key_configured'] = true;
            $result['auth_note'] = 'API key configured (will be validated during signing)';
            
            // Check if it's the demo key
            if ($api_key === 'demo-local-key') {
                $result['organization'] = [
                    'organization_id' => 'org_demo',
                    'name' => 'Demo Organization',
                    'tier' => 'free'
                ];
            }
        } else {
            $result['api_key_configured'] = false;
            $result['auth_note'] = 'No API key configured - using demo mode';
            $result['organization'] = [
                'organization_id' => 'org_demo',
                'name' => 'Demo Organization',
                'tier' => 'free'
            ];
        }

        return new WP_REST_Response($result);
    }
}
