<?php
namespace EncypherAssurance;

if (! defined('ABSPATH')) {
    exit;
}

/**
 * Handles frontend display of C2PA badges and verification links.
 * 
 * Provides optional badges on posts to indicate C2PA protection
 * and links for public verification.
 */
class Frontend
{
    /**
     * Register hooks for frontend display.
     */
    public function register_hooks(): void
    {
        add_filter('the_content', [$this, 'maybe_add_c2pa_badge'], 20);
        add_action('wp_enqueue_scripts', [$this, 'enqueue_frontend_assets']);
        add_filter('the_title', [$this, 'maybe_add_inline_badge'], 20, 2);
    }

    /**
     * Enqueue frontend assets.
     */
    public function enqueue_frontend_assets(): void
    {
        if (! is_singular()) {
            return;
        }

        wp_enqueue_style(
            'encypher-frontend',
            ENCYPHER_ASSURANCE_PLUGIN_URL . 'assets/css/frontend.css',
            [],
            ENCYPHER_ASSURANCE_VERSION
        );
    }

    /**
     * Maybe add C2PA badge to post content.
     * 
     * @param string $content Post content
     * @return string Modified content with badge
     */
    public function maybe_add_c2pa_badge(string $content): string
    {
        if (! is_singular() || ! in_the_loop() || ! is_main_query()) {
            return $content;
        }

        $post_id = get_the_ID();
        if (! $post_id) {
            return $content;
        }

        // Check if post is marked
        $is_marked = get_post_meta($post_id, '_encypher_marked', true);
        if (! $is_marked) {
            return $content;
        }

        // Get settings
        $settings = get_option('encypher_assurance_settings', []);
        $show_badge = isset($settings['show_badge']) ? (bool) $settings['show_badge'] : true; // Default ON
        
        if (! $show_badge) {
            return $content;
        }

        // Get badge position setting (default to end_of_content if not set)
        // For now, always show at end of content (inline header option available but not in settings UI yet)
        $badge_position = !empty($settings['badge_position']) ? $settings['badge_position'] : 'end_of_content';
        
        // Skip if inline_header is explicitly set (for future use)
        if ('inline_header' === $badge_position) {
            return $content;
        }
        
        // Get badge HTML (always show at end of content by default)
        $badge_html = $this->get_badge_html($post_id, 'large');

        // Always add modal to footer
        add_action('wp_footer', function() use ($post_id) {
            echo $this->get_modal_html($post_id);
        });

        // Add badge at the end of content (inline, aligned with content)
        $badge_wrapper = '<div class="encypher-c2pa-badge-wrapper" style="margin: 40px 0 60px 0; padding: 0;">';
        $badge_wrapper .= $badge_html;
        $badge_wrapper .= '</div>';
        
        return $content . $badge_wrapper;
    }

    /**
     * Maybe add inline badge to post title.
     * 
     * @param string $title Post title
     * @param int $post_id Post ID
     * @return string Modified title with badge
     */
    public function maybe_add_inline_badge(string $title, int $post_id): string
    {
        // Only on singular post pages in the main query
        if (! is_singular() || ! in_the_loop() || ! is_main_query()) {
            return $title;
        }

        // Check if post is marked
        $is_marked = get_post_meta($post_id, '_encypher_marked', true);
        if (! $is_marked) {
            return $title;
        }

        // Get settings
        $settings = get_option('encypher_assurance_settings', []);
        $show_badge = isset($settings['show_badge']) ? (bool) $settings['show_badge'] : true;
        
        if (! $show_badge) {
            return $title;
        }

        $badge_position = isset($settings['badge_position']) ? $settings['badge_position'] : 'end_of_content';
        
        // Only add inline badge if that position is selected
        if ('inline_header' !== $badge_position) {
            return $title;
        }

        // Add modal to footer (only once)
        static $modal_added = false;
        if (!$modal_added) {
            add_action('wp_footer', function() use ($post_id) {
                echo $this->get_modal_html($post_id);
            });
            $modal_added = true;
        }

        // Get small badge HTML
        $badge_html = $this->get_badge_html($post_id, 'small');
        
        return $title . ' ' . $badge_html;
    }

    /**
     * Get badge HTML for a post.
     * 
     * @param int $post_id Post ID
     * @param string $size Badge size: 'small' or 'large'
     * @return string Badge HTML
     */
    private function get_badge_html(int $post_id, string $size = 'large'): string
    {
        $icon_url = ENCYPHER_ASSURANCE_PLUGIN_URL . 'assets/images/encypher-icon.png';
        $status = get_post_meta($post_id, '_encypher_assurance_status', true);
        $document_id = get_post_meta($post_id, '_encypher_assurance_document_id', true);
        
        // Determine if content has been verified yet
        $last_verified = get_post_meta($post_id, '_encypher_assurance_last_verified', true);
        $is_verified = !empty($last_verified);
        
        $status_class = 'protected';
        $status_text = __('Click to Verify Content', 'encypher-assurance');
        $title_text = __('Click to verify content authenticity', 'encypher-assurance');
        $text_color = '#666';
        
        if ($is_verified) {
            $status_class = 'verified';
            $status_text = __('Verified', 'encypher-assurance');
            $title_text = __('Click to view verification details', 'encypher-assurance');
            $text_color = '#2e7d32';
        }

        // Size-specific styling
        if ('small' === $size) {
            $icon_size = '18px';
            $padding = '4px 10px';
            $font_size = '12px';
            $gap = '6px';
            $show_doc_id = false;
        } else {
            $icon_size = '24px';
            $padding = '10px 18px';
            $font_size = '14px';
            $gap = '8px';
            $show_doc_id = $is_verified && $document_id;
        }

        ob_start();
        ?>
        <button type="button" 
                class="encypher-c2pa-badge encypher-c2pa-badge-<?php echo esc_attr($status_class); ?>" 
                data-post-id="<?php echo esc_attr($post_id); ?>"
                aria-label="<?php echo esc_attr($title_text); ?>"
                title="<?php echo esc_attr($title_text); ?>"
                style="display: inline-flex; align-items: center; gap: <?php echo esc_attr($gap); ?>; padding: <?php echo esc_attr($padding); ?>; background: #fff; border: 1px solid #ddd; border-radius: 6px; cursor: pointer; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: <?php echo esc_attr($font_size); ?>; font-weight: 500; color: #333; transition: all 0.2s ease; vertical-align: middle;">
            <img src="<?php echo esc_url($icon_url); ?>" 
                 alt="<?php esc_attr_e('Encypher', 'encypher-assurance'); ?>" 
                 style="width: <?php echo esc_attr($icon_size); ?>; height: <?php echo esc_attr($icon_size); ?>; display: block;" />
            <span style="color: <?php echo esc_attr($text_color); ?>;"><?php if ($is_verified): ?>✓ <?php endif; ?><?php echo esc_html($status_text); ?></span>
            <?php if ($show_doc_id): ?>
                <span style="font-size: 11px; color: #666; font-weight: normal;">(<?php echo esc_html(substr($document_id, 0, 12)); ?>...)</span>
            <?php endif; ?>
        </button>
        <?php
        return ob_get_clean();
    }

    /**
     * Get modal HTML for verification display.
     * 
     * @param int $post_id Post ID
     * @return string Modal HTML
     */
    private function get_modal_html(int $post_id): string
    {
        $logo_url = ENCYPHER_ASSURANCE_PLUGIN_URL . 'assets/images/encypher-logo.png';
        
        ob_start();
        ?>
        <div id="encypher-c2pa-modal" class="encypher-c2pa-modal" style="display:none;" role="dialog" aria-modal="true" aria-labelledby="encypher-modal-title">
            <div class="encypher-c2pa-modal-overlay"></div>
            <div class="encypher-c2pa-modal-content">
                <div class="encypher-c2pa-modal-header">
                    <img src="<?php echo esc_url($logo_url); ?>" alt="Encypher" class="encypher-c2pa-modal-logo" />
                    <button type="button" class="encypher-c2pa-modal-close" aria-label="<?php esc_attr_e('Close', 'encypher-assurance'); ?>">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="encypher-c2pa-modal-body">
                    <h2 id="encypher-modal-title"><?php esc_html_e('C2PA Content Verification', 'encypher-assurance'); ?></h2>
                    <div class="encypher-c2pa-modal-loading">
                        <div class="encypher-c2pa-spinner"></div>
                        <p><?php esc_html_e('Verifying content...', 'encypher-assurance'); ?></p>
                    </div>
                    <div class="encypher-c2pa-modal-result" style="display:none;"></div>
                </div>
            </div>
        </div>
        
        <style>
        .encypher-c2pa-badge:hover {
            background: #f5f5f5 !important;
            border-color: #2e7d32 !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        }
        .encypher-c2pa-badge:active {
            transform: scale(0.98);
        }
        </style>
        
        <script>
        (function() {
            console.log('Encypher: Initializing verification modal');
            const modal = document.getElementById('encypher-c2pa-modal');
            const badges = document.querySelectorAll('.encypher-c2pa-badge');
            console.log('Encypher: Found', badges.length, 'badge(s)');
            
            if (!modal) {
                console.error('Encypher: Modal element not found');
                return;
            }
            
            const closeBtn = modal.querySelector('.encypher-c2pa-modal-close');
            const overlay = modal.querySelector('.encypher-c2pa-modal-overlay');
            const loading = modal.querySelector('.encypher-c2pa-modal-loading');
            const result = modal.querySelector('.encypher-c2pa-modal-result');
            
            function openModal(postId) {
                console.log('Encypher: Opening modal for post', postId);
                modal.style.display = 'block';
                document.body.style.overflow = 'hidden';
                loading.style.display = 'block';
                result.style.display = 'none';
                
                // Fetch verification data
                console.log('Encypher: Fetching verification from API');
                fetch('<?php echo esc_url(rest_url('encypher-assurance/v1/verify')); ?>', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': '<?php echo wp_create_nonce('wp_rest'); ?>'
                    },
                    body: JSON.stringify({ post_id: postId })
                })
                .then(response => {
                    console.log('Encypher: API response status:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('Encypher: API response data:', data);
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    result.innerHTML = formatVerificationData(data, postId);
                    
                    // Update badge text to show "Verified" after successful verification
                    if (data.valid) {
                        const badge = document.querySelector('.encypher-c2pa-badge[data-post-id="' + postId + '"]');
                        if (badge) {
                            const textSpan = badge.querySelector('span');
                            if (textSpan && !textSpan.textContent.includes('✓')) {
                                textSpan.innerHTML = '✓ <?php esc_html_e('Verified', 'encypher-assurance'); ?>';
                                textSpan.style.color = '#2e7d32';
                            }
                        }
                    }
                })
                .catch(error => {
                    console.error('Encypher: API error:', error);
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    result.innerHTML = '<div class="encypher-error"><?php esc_html_e('Failed to verify content. Please try again.', 'encypher-assurance'); ?></div>';
                });
            }
            
            function closeModal() {
                modal.style.display = 'none';
                document.body.style.overflow = '';
            }
            
            function formatVerificationData(data, postId) {
                if (!data || !data.valid) {
                    return '<div class="encypher-error"><?php esc_html_e('Content verification failed or no C2PA manifest found.', 'encypher-assurance'); ?></div>';
                }
                
                let html = '<div class="encypher-verification-success">';
                html += '<div class="encypher-status-badge encypher-status-verified">✓ <?php esc_html_e('Verified', 'encypher-assurance'); ?></div>';
                
                // Show cache status
                if (data.cached) {
                    html += '<p class="encypher-cache-notice" style="font-size: 0.9em; color: #666; margin: 10px 0;"><em><?php esc_html_e('(Cached result - verified within last 5 minutes)', 'encypher-assurance'); ?></em></p>';
                }
                
                html += '<table class="encypher-verification-table">';
                
                // Document information
                if (data.document) {
                    html += '<tr><th colspan="2"><?php esc_html_e('Document Information', 'encypher-assurance'); ?></th></tr>';
                    if (data.document.title) html += '<tr><td><?php esc_html_e('Title', 'encypher-assurance'); ?></td><td>' + escapeHtml(data.document.title) + '</td></tr>';
                    if (data.document.author) html += '<tr><td><?php esc_html_e('Author', 'encypher-assurance'); ?></td><td>' + escapeHtml(data.document.author) + '</td></tr>';
                    if (data.document.organization) html += '<tr><td><?php esc_html_e('Organization', 'encypher-assurance'); ?></td><td>' + escapeHtml(data.document.organization) + '</td></tr>';
                }
                
                // Metadata
                if (data.metadata) {
                    html += '<tr><th colspan="2"><?php esc_html_e('C2PA Metadata', 'encypher-assurance'); ?></th></tr>';
                    if (data.metadata.signer_id) html += '<tr><td><?php esc_html_e('Signer ID', 'encypher-assurance'); ?></td><td>' + escapeHtml(data.metadata.signer_id) + '</td></tr>';
                    if (data.metadata.timestamp) html += '<tr><td><?php esc_html_e('Timestamp', 'encypher-assurance'); ?></td><td>' + escapeHtml(data.metadata.timestamp) + '</td></tr>';
                    if (data.metadata.format) html += '<tr><td><?php esc_html_e('Format', 'encypher-assurance'); ?></td><td>' + escapeHtml(data.metadata.format) + '</td></tr>';
                }
                
                // Merkle proof
                if (data.merkle_proof) {
                    html += '<tr><th colspan="2"><?php esc_html_e('Merkle Tree Verification', 'encypher-assurance'); ?></th></tr>';
                    html += '<tr><td><?php esc_html_e('Root Hash', 'encypher-assurance'); ?></td><td><code>' + escapeHtml(data.merkle_proof.root_hash) + '</code></td></tr>';
                    html += '<tr><td><?php esc_html_e('Verified', 'encypher-assurance'); ?></td><td>' + (data.merkle_proof.verified ? '✓ <?php esc_html_e('Yes', 'encypher-assurance'); ?>' : '✗ <?php esc_html_e('No', 'encypher-assurance'); ?>') + '</td></tr>';
                }
                
                html += '</table>';
                
                // Add provenance report link
                const provenanceUrl = '<?php echo esc_url(rest_url('encypher-assurance/v1/provenance')); ?>?post_id=' + postId;
                html += '<p style="margin-top: 15px;"><a href="' + provenanceUrl + '" target="_blank" rel="noopener" class="button button-secondary"><?php esc_html_e('View Full Provenance Report', 'encypher-assurance'); ?></a></p>';
                
                html += '</div>';
                
                return html;
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            // Event listeners
            badges.forEach(badge => {
                console.log('Encypher: Attaching click listener to badge');
                badge.addEventListener('click', function(e) {
                    console.log('Encypher: Badge clicked!');
                    e.preventDefault();
                    const postId = this.getAttribute('data-post-id');
                    console.log('Encypher: Post ID:', postId);
                    openModal(postId);
                });
            });
            
            closeBtn.addEventListener('click', closeModal);
            overlay.addEventListener('click', closeModal);
            
            // Close on Escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && modal.style.display === 'block') {
                    closeModal();
                }
            });
        })();
        </script>
        <?php
        return ob_get_clean();
    }
}
