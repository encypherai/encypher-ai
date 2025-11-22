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
        $settings = get_option('encypher_assurance_settings', []);
        $tier = isset($settings['tier']) ? $settings['tier'] : 'free';
        $show_branding = isset($settings['show_branding']) ? (bool) $settings['show_branding'] : true;
        
        // Force branding on Free tier (double check)
        if ('free' === $tier) {
            $show_branding = true;
        }

        $icon_url = ENCYPHER_ASSURANCE_PLUGIN_URL . 'assets/images/encypher-icon.png';
        $status = get_post_meta($post_id, '_encypher_assurance_status', true);
        $document_id = get_post_meta($post_id, '_encypher_assurance_document_id', true);
        $last_verified = get_post_meta($post_id, '_encypher_assurance_last_verified', true);
        $is_verified = ! empty($last_verified);

        $status_class = 'protected';
        $status_text = __('Click to verify content', 'encypher-provenance');
        $title_text = __('Click to verify content authenticity', 'encypher-provenance');
        $text_color = '#666';

        if ($is_verified) {
            $status_class = 'verified';
            $status_text = ('enterprise' === $tier)
                ? __('Enterprise verified', 'encypher-provenance')
                : __('Verified', 'encypher-provenance');
            $title_text = __('Click to view verification details', 'encypher-provenance');
            $text_color = '#2e7d32';
        }

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

        $tier_pill = '';
        if (in_array($tier, ['pro', 'enterprise'], true) && $is_verified) {
            $tier_pill = '<span class="badge-tier">' . esc_html(ucfirst($tier)) . '</span>';
        }

        ob_start();
        ?>
        <button type="button"
                class="encypher-c2pa-badge encypher-c2pa-badge-<?php echo esc_attr($status_class); ?> encypher-tier-<?php echo esc_attr($tier); ?>"
                data-post-id="<?php echo esc_attr($post_id); ?>"
                data-tier="<?php echo esc_attr($tier); ?>"
                aria-label="<?php echo esc_attr($title_text); ?>"
                title="<?php echo esc_attr($title_text); ?>"
                style="display: inline-flex; align-items: center; gap: <?php echo esc_attr($gap); ?>; padding: <?php echo esc_attr($padding); ?>; background: #fff; border: 1px solid #ddd; border-radius: 6px; cursor: pointer; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: <?php echo esc_attr($font_size); ?>; font-weight: 500; color: #333; transition: all 0.2s ease; vertical-align: middle;">
            <?php if ($show_branding) : ?>
                <img src="<?php echo esc_url($icon_url); ?>"
                     alt="<?php esc_attr_e('Encypher', 'encypher-provenance'); ?>"
                     style="width: <?php echo esc_attr($icon_size); ?>; height: <?php echo esc_attr($icon_size); ?>; display: block;" />
            <?php else : ?>
                <!-- Generic Shield Icon (Whitelabel) -->
                <svg width="<?php echo esc_attr($icon_size); ?>" height="<?php echo esc_attr($icon_size); ?>" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: block;">
                    <path d="M12 22C12 22 20 18 20 12V5L12 2L4 5V12C4 18 12 22 12 22Z" stroke="<?php echo esc_attr($text_color); ?>" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <?php if ($is_verified) : ?>
                        <path d="M9 12L11 14L15 10" stroke="<?php echo esc_attr($text_color); ?>" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <?php endif; ?>
                </svg>
            <?php endif; ?>
            
            <span style="color: <?php echo esc_attr($text_color); ?>;"><?php echo esc_html($status_text); ?></span>
            <?php if ($tier_pill) : ?>
                <?php echo $tier_pill; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>
            <?php endif; ?>
            <?php if ($show_doc_id) : ?>
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
                    <button type="button" class="encypher-c2pa-modal-close" aria-label="<?php esc_attr_e('Close', 'encypher-provenance'); ?>">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="encypher-c2pa-modal-body">
                    <h2 id="encypher-modal-title"><?php esc_html_e('C2PA Content Verification', 'encypher-provenance'); ?></h2>
                    <div class="encypher-c2pa-modal-loading">
                        <div class="encypher-c2pa-spinner"></div>
                        <p><?php esc_html_e('Verifying content...', 'encypher-provenance'); ?></p>
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
                fetch('<?php echo esc_url(rest_url('encypher-provenance/v1/verify')); ?>', {
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
                                textSpan.innerHTML = '✓ <?php esc_html_e('Verified', 'encypher-provenance'); ?>';
                                textSpan.style.color = '#2e7d32';
                            }
                        }
                    }
                })
                .catch(error => {
                    console.error('Encypher: API error:', error);
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    result.innerHTML = '<div class="encypher-error"><?php esc_html_e('Failed to verify content. Please try again.', 'encypher-provenance'); ?></div>';
                });
            }
            
            function closeModal() {
                modal.style.display = 'none';
                document.body.style.overflow = '';
            }
            
            function formatVerificationData(data, postId) {
                if (!data || !data.valid) {
                    return '<div class="encypher-error"><?php esc_html_e('Content verification failed or no C2PA manifest found.', 'encypher-provenance'); ?></div>';
                }
                
                let html = '<div class="encypher-verification-success">';
                html += '<div class="encypher-status-badge encypher-status-verified">✓ <?php esc_html_e('Verified', 'encypher-provenance'); ?></div>';
                
                // Show cache status
                if (data.cached) {
                    html += '<p class="encypher-cache-notice" style="font-size: 0.9em; color: #666; margin: 10px 0;"><em><?php esc_html_e('(Cached result - verified within last 5 minutes)', 'encypher-provenance'); ?></em></p>';
                }
                
                // Summary section
                html += '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">';
                html += '<h3 style="margin: 0 0 10px 0; font-size: 14px; color: #333;"><?php esc_html_e('Verification Summary', 'encypher-provenance'); ?></h3>';
                
                if (data.signer_id) {
                    html += '<p style="margin: 5px 0;"><strong><?php esc_html_e('Signed by:', 'encypher-provenance'); ?></strong> ' + escapeHtml(data.signer_id) + '</p>';
                }
                
                if (data.verified_at) {
                    const verifiedDate = new Date(data.verified_at);
                    html += '<p style="margin: 5px 0;"><strong><?php esc_html_e('Verified at:', 'encypher-provenance'); ?></strong> ' + verifiedDate.toLocaleString() + '</p>';
                }
                
                // Extract action info from metadata
                if (data.metadata && data.metadata.assertions) {
                    const actions = data.metadata.assertions.find(a => a.label === 'c2pa.actions.v1');
                    if (actions && actions.data && actions.data.actions) {
                        const createdAction = actions.data.actions.find(a => a.label === 'c2pa.created');
                        if (createdAction) {
                            const createdDate = new Date(createdAction.when);
                            html += '<p style="margin: 5px 0;"><strong><?php esc_html_e('Created:', 'encypher-provenance'); ?></strong> ' + createdDate.toLocaleString() + '</p>';
                        }
                    }
                }
                
                html += '</div>';

        if (data.content) {
            html += '<div class="merkle-proof-row" style="margin: 10px 0; font-size: 13px;">';
            html += '<strong><?php esc_html_e('Sentence leaf:', 'encypher-provenance'); ?></strong> #' + data.content.leaf_index + ' &middot; ' + (data.content.text_preview ? escapeHtml(data.content.text_preview) : 'N/A');
            html += '</div>';
        }

        if (data.merkle_proof) {
            html += '<div class="merkle-proof-row" style="margin: 10px 0; font-size: 13px;">';
            html += '<strong><?php esc_html_e('Merkle root:', 'encypher-provenance'); ?></strong> ' + escapeHtml(data.merkle_proof.root_hash || 'N/A');
            if (data.merkle_proof.verified) {
                html += ' &middot; <?php esc_html_e('Proof verified', 'encypher-provenance'); ?>';
            }
            html += '</div>';
        }

        // Expandable details section (open by default)
                html += '<details open style="margin: 15px 0;">';
                html += '<summary style="cursor: pointer; padding: 10px; background: #e9ecef; border-radius: 4px; font-weight: 600;"><?php esc_html_e('View Full C2PA Manifest', 'encypher-provenance'); ?></summary>';
                html += '<div style="padding: 15px; border: 1px solid #dee2e6; border-top: none; border-radius: 0 0 4px 4px;">';
                
                // Full metadata table
                html += '<table class="encypher-verification-table" style="width: 100%; border-collapse: collapse;">';
                
                // Metadata
                if (data.metadata) {
                    if (data.metadata.claim_generator) {
                        html += '<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong><?php esc_html_e('Claim Generator', 'encypher-provenance'); ?></strong></td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">' + escapeHtml(data.metadata.claim_generator) + '</td></tr>';
                    }
                    if (data.metadata.instance_id) {
                        html += '<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong><?php esc_html_e('Instance ID', 'encypher-provenance'); ?></strong></td><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-family: monospace; font-size: 12px;">' + escapeHtml(data.metadata.instance_id) + '</td></tr>';
                    }
                    
                    // Assertions
                    if (data.metadata.assertions && data.metadata.assertions.length > 0) {
                        html += '<tr><td colspan="2" style="padding: 12px 8px 8px 8px;"><strong><?php esc_html_e('Assertions', 'encypher-provenance'); ?></strong></td></tr>';
                        data.metadata.assertions.forEach(assertion => {
                            html += '<tr><td style="padding: 8px; padding-left: 20px; border-bottom: 1px solid #dee2e6;">' + escapeHtml(assertion.label) + '</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">' + escapeHtml(assertion.kind || 'N/A') + '</td></tr>';
                        });
                    }
                }
                
                html += '</table>';
                html += '</div></details>';
                
                // Add provenance chain viewer (if ingredients exist)
                if (data.metadata && data.metadata.ingredients && data.metadata.ingredients.length > 0) {
                    html += '<details style="margin: 15px 0;">';
                    html += '<summary style="cursor: pointer; padding: 10px; background: #28a745; color: white; border-radius: 4px; font-weight: 600;">🔗 <?php esc_html_e('View Provenance Chain', 'encypher-provenance'); ?></summary>';
                    html += '<div style="padding: 15px; border: 1px solid #dee2e6; border-top: none; border-radius: 0 0 4px 4px; background: #f8f9fa;">';
                    html += '<p style="margin-bottom: 15px; color: #666;"><?php esc_html_e('This content has been edited. View the complete edit history:', 'encypher-provenance'); ?></p>';
                    
                    // Build provenance chain
                    let chain = [];
                    let current = data.metadata;
                    let depth = 0;
                    while (current && depth < 10) {  // Limit depth to prevent infinite loops
                        const actions = current.assertions?.find(a => a.label === 'c2pa.actions.v1')?.data?.actions || [];
                        const mainAction = actions.find(a => a.label === 'c2pa.created' || a.label === 'c2pa.edited');
                        chain.push({
                            instance_id: current.instance_id,
                            action: mainAction?.label || 'unknown',
                            when: mainAction?.when || 'unknown',
                            depth: depth
                        });
                        current = current.ingredients?.[0]?.c2pa_manifest;
                        depth++;
                    }
                    
                    // Display chain
                    html += '<div style="font-family: monospace; font-size: 13px;">';
                    for (let i = 0; i < chain.length; i++) {
                        const item = chain[i];
                        const indent = '  '.repeat(item.depth);
                        const icon = item.action === 'c2pa.created' ? '🌱' : '✏️';
                        const label = item.action === 'c2pa.created' ? 'Created' : 'Edited';
                        const color = item.action === 'c2pa.created' ? '#28a745' : '#ffc107';
                        html += '<div style="padding: 8px; margin: 5px 0; background: white; border-left: 3px solid ' + color + '; border-radius: 4px;">';
                        html += indent + icon + ' <strong>' + label + '</strong> at ' + item.when;
                        html += '<br>' + indent + '   <span style="color: #999; font-size: 11px;">Instance: ' + item.instance_id.substring(0, 8) + '...</span>';
                        html += '</div>';
                    }
                    html += '</div>';
                    html += '</div></details>';
                }
                
                // Add full manifest JSON viewer
                if (data.metadata) {
                    html += '<details style="margin: 15px 0;">';
                    html += '<summary style="cursor: pointer; padding: 10px; background: #1B2F50; color: white; border-radius: 4px; font-weight: 600;"><?php esc_html_e('View Complete C2PA Manifest (JSON)', 'encypher-provenance'); ?></summary>';
                    html += '<div style="padding: 15px; border: 1px solid #dee2e6; border-top: none; border-radius: 0 0 4px 4px; background: #f8f9fa;">';
                    html += '<pre id="c2pa-manifest-json" style="background: #2b2b2b; color: #f8f8f2; padding: 20px; border-radius: 6px; overflow-x: auto; font-size: 13px; line-height: 1.5; font-family: \'Courier New\', monospace; margin: 0;">';
                    html += escapeHtml(JSON.stringify(data.metadata, null, 2));
                    html += '</pre>';
                    html += '<p style="margin-top: 15px; font-size: 12px; color: #666; text-align: center;">';
                    html += '<button id="copy-manifest-btn" style="padding: 8px 16px; background: #2A87C4; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 500;">📋 Copy to Clipboard</button>';
                    html += '</p>';
                    html += '</div></details>';
                    
                    // Add click handler after modal is rendered
                    setTimeout(function() {
                        const copyBtn = document.getElementById('copy-manifest-btn');
                        if (copyBtn) {
                            copyBtn.onclick = function() {
                                const json = JSON.stringify(data.metadata, null, 2);
                                navigator.clipboard.writeText(json).then(function() {
                                    copyBtn.textContent = '✓ Copied!';
                                    setTimeout(function() {
                                        copyBtn.textContent = '📋 Copy to Clipboard';
                                    }, 2000);
                                }).catch(function(err) {
                                    console.error('Failed to copy:', err);
                                    copyBtn.textContent = '❌ Failed';
                                    setTimeout(function() {
                                        copyBtn.textContent = '📋 Copy to Clipboard';
                                    }, 2000);
                                });
                            };
                        }
                    }, 100);
                }
                
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
