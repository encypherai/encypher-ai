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

        $tier = isset($settings['tier']) ? $settings['tier'] : 'free';
        $badge_position = isset($settings['badge_position']) ? $settings['badge_position'] : 'bottom-right';
        
        // Free tier: always bottom-right, no customization
        if ('free' === $tier) {
            $badge_position = 'bottom-right';
        }
        
        // Get badge HTML
        $badge_html = $this->get_badge_html($post_id);

        // Always add modal to footer
        add_action('wp_footer', function() use ($post_id) {
            echo $this->get_modal_html($post_id);
        });

        // Add badge based on position
        if ('bottom-right' === $badge_position) {
            // Floating badge in bottom-right corner
            add_action('wp_footer', function() use ($badge_html) {
                echo '<div class="encypher-c2pa-badge-floating">' . $badge_html . '</div>';
            });
            return $content;
        } else {
            // Other positions (Pro/Enterprise only)
            switch ($badge_position) {
                case 'top':
                    return $badge_html . $content;
                case 'bottom':
                default:
                    return $content . $badge_html;
            }
        }
    }

    /**
     * Get badge HTML for a post.
     * 
     * @param int $post_id Post ID
     * @return string Badge HTML
     */
    private function get_badge_html(int $post_id): string
    {
        $icon_url = ENCYPHER_ASSURANCE_PLUGIN_URL . 'assets/images/encypher-icon.png';
        $status = get_post_meta($post_id, '_encypher_assurance_status', true);
        
        $status_class = 'protected';
        $title_text = __('C2PA Protected - Click to verify', 'encypher-assurance');
        
        if ('c2pa_verified' === $status) {
            $status_class = 'verified';
            $title_text = __('C2PA Verified - Click to view details', 'encypher-assurance');
        }

        ob_start();
        ?>
        <button type="button" 
                class="encypher-c2pa-badge encypher-c2pa-badge-<?php echo esc_attr($status_class); ?>" 
                data-post-id="<?php echo esc_attr($post_id); ?>"
                aria-label="<?php echo esc_attr($title_text); ?>"
                title="<?php echo esc_attr($title_text); ?>">
            <img src="<?php echo esc_url($icon_url); ?>" 
                 alt="<?php esc_attr_e('Encypher C2PA Protected', 'encypher-assurance'); ?>" 
                 class="encypher-c2pa-badge-icon" />
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
        
        <script>
        (function() {
            const modal = document.getElementById('encypher-c2pa-modal');
            const badges = document.querySelectorAll('.encypher-c2pa-badge');
            const closeBtn = modal.querySelector('.encypher-c2pa-modal-close');
            const overlay = modal.querySelector('.encypher-c2pa-modal-overlay');
            const loading = modal.querySelector('.encypher-c2pa-modal-loading');
            const result = modal.querySelector('.encypher-c2pa-modal-result');
            
            function openModal(postId) {
                modal.style.display = 'block';
                document.body.style.overflow = 'hidden';
                loading.style.display = 'block';
                result.style.display = 'none';
                
                // Fetch verification data
                fetch('<?php echo esc_url(rest_url('encypher-assurance/v1/verify')); ?>', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': '<?php echo wp_create_nonce('wp_rest'); ?>'
                    },
                    body: JSON.stringify({ post_id: postId })
                })
                .then(response => response.json())
                .then(data => {
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    result.innerHTML = formatVerificationData(data);
                })
                .catch(error => {
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    result.innerHTML = '<div class="encypher-error"><?php esc_html_e('Failed to verify content. Please try again.', 'encypher-assurance'); ?></div>';
                });
            }
            
            function closeModal() {
                modal.style.display = 'none';
                document.body.style.overflow = '';
            }
            
            function formatVerificationData(data) {
                if (!data || !data.valid) {
                    return '<div class="encypher-error"><?php esc_html_e('Content verification failed or no C2PA manifest found.', 'encypher-assurance'); ?></div>';
                }
                
                let html = '<div class="encypher-verification-success">';
                html += '<div class="encypher-status-badge encypher-status-verified">✓ <?php esc_html_e('Verified', 'encypher-assurance'); ?></div>';
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
                badge.addEventListener('click', function() {
                    const postId = this.getAttribute('data-post-id');
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
