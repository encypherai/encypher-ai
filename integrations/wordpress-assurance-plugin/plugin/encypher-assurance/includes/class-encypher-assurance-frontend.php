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
        $show_badge = isset($settings['show_badge']) ? (bool) $settings['show_badge'] : false;
        
        if (! $show_badge) {
            return $content;
        }

        $badge_position = isset($settings['badge_position']) ? $settings['badge_position'] : 'bottom';
        
        // Get badge HTML
        $badge_html = $this->get_badge_html($post_id);

        // Add badge based on position
        switch ($badge_position) {
            case 'top':
                return $badge_html . $content;
            case 'floating':
                // Floating badge doesn't modify content, added via CSS
                add_action('wp_footer', function() use ($badge_html) {
                    echo '<div class="encypher-c2pa-badge-floating">' . $badge_html . '</div>';
                });
                return $content;
            case 'bottom':
            default:
                return $content . $badge_html;
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
        $verification_url = get_post_meta($post_id, '_encypher_assurance_verification_url', true);
        $manifest_id = get_post_meta($post_id, '_encypher_manifest_id', true);
        $marked_date = get_post_meta($post_id, '_encypher_marked_date', true);
        $status = get_post_meta($post_id, '_encypher_assurance_status', true);

        // Format date
        $date_display = '';
        if ($marked_date) {
            $date_display = sprintf(
                /* translators: %s: formatted date */
                __('Marked: %s', 'encypher-assurance'),
                date_i18n(get_option('date_format'), strtotime($marked_date))
            );
        }

        // Status icon and text
        $status_icon = '🔒';
        $status_text = __('C2PA Protected Content', 'encypher-assurance');
        $status_class = 'protected';

        if ('c2pa_verified' === $status) {
            $status_icon = '✅';
            $status_text = __('C2PA Verified Content', 'encypher-assurance');
            $status_class = 'verified';
        }

        ob_start();
        ?>
        <div class="encypher-c2pa-badge encypher-c2pa-badge-<?php echo esc_attr($status_class); ?>">
            <div class="encypher-c2pa-badge-inner">
                <div class="encypher-c2pa-badge-icon">
                    <?php echo $status_icon; ?>
                </div>
                <div class="encypher-c2pa-badge-content">
                    <div class="encypher-c2pa-badge-title">
                        <?php echo esc_html($status_text); ?>
                    </div>
                    <div class="encypher-c2pa-badge-description">
                        <?php esc_html_e('This content is cryptographically authenticated.', 'encypher-assurance'); ?>
                        <?php if ($verification_url): ?>
                            <a href="<?php echo esc_url($verification_url); ?>" 
                               class="encypher-c2pa-verify-link" 
                               target="_blank" 
                               rel="noopener">
                                <?php esc_html_e('Verify authenticity', 'encypher-assurance'); ?> →
                            </a>
                        <?php endif; ?>
                    </div>
                    <?php if ($date_display): ?>
                        <div class="encypher-c2pa-badge-meta">
                            <?php echo esc_html($date_display); ?>
                        </div>
                    <?php endif; ?>
                </div>
            </div>
            <div class="encypher-c2pa-badge-footer">
                <span class="encypher-c2pa-badge-powered">
                    <?php esc_html_e('Powered by', 'encypher-assurance'); ?>
                    <a href="https://encypherai.com" target="_blank" rel="noopener">Encypher</a>
                </span>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
}
