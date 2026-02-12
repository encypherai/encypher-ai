<?php
namespace EncypherProvenance;

if (! defined('ABSPATH')) {
    exit;
}

/**
 * Handles automatic verification on the frontend.
 */
class Verification
{
    private Rest $rest;

    public function __construct(Rest $rest)
    {
        $this->rest = $rest;
    }

    public function register_hooks(): void
    {
        add_action('wp_enqueue_scripts', [$this, 'enqueue_frontend_assets']);
        // Disabled: The floating badge provides better UX
        // add_filter('the_content', [$this, 'append_verification_badge'], 20);
    }

    public function enqueue_frontend_assets(): void
    {
        wp_enqueue_style(
            'encypher-provenance-frontend',
            ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/css/editor.css',
            [],
            ENCYPHER_PROVENANCE_VERSION
        );
    }

    public function append_verification_badge(string $content): string
    {
        if (is_admin() || ! is_singular(['post', 'page'])) {
            return $content;
        }

        $post_id = get_the_ID();
        if (! $post_id) {
            return $content;
        }

        $settings = get_option('encypher_provenance_settings', []);
        $auto_verify = ! empty($settings['auto_verify']);
        $verification = get_post_meta($post_id, '_encypher_provenance_verification', true);
        $document_id = get_post_meta($post_id, '_encypher_provenance_document_id', true);
        $verification_url = get_post_meta($post_id, '_encypher_provenance_verification_url', true);
        $total_sentences = (int) get_post_meta($post_id, '_encypher_provenance_total_sentences', true);
        $last_signed = get_post_meta($post_id, '_encypher_provenance_last_signed', true);
        $status = get_post_meta($post_id, '_encypher_provenance_status', true);

        if ($auto_verify && (! is_array($verification) || ! array_key_exists('is_valid', $verification))) {
            $request = new \WP_REST_Request('POST', '/encypher-provenance/v1/verify');
            $request->set_param('post_id', $post_id);
            $request->set_param('context', 'frontend');
            $result = rest_do_request($request);
            if (! $result->is_error()) {
                $verification = $result->get_data();
            }
        }

        if (! $document_id && (! is_array($verification) || ! array_key_exists('is_valid', $verification))) {
            return $content;
        }

        $is_valid = is_array($verification) && ! empty($verification['is_valid']);
        $tampered = is_array($verification) && isset($verification['tampered']) ? (bool) $verification['tampered'] : false;
        $organization = is_array($verification) && isset($verification['organization_name']) ? $verification['organization_name'] : null;
        $signer_id = is_array($verification) && isset($verification['signer_id']) ? $verification['signer_id'] : null;
        $timestamp = is_array($verification) && isset($verification['signature_timestamp']) ? $verification['signature_timestamp'] : null;
        $manifest = is_array($verification) && isset($verification['manifest']) && is_array($verification['manifest']) ? $verification['manifest'] : null;

        ob_start();
        ?>
        <section class="encypher-provenance-verification" aria-label="<?php echo esc_attr__('Encypher verification status', 'encypher-provenance'); ?>">
            <h2 class="verification-title">
                <?php
                if ($tampered) {
                    esc_html_e('Potential tampering detected', 'encypher-provenance');
                } elseif ($is_valid) {
                    esc_html_e('Content authenticity verified', 'encypher-provenance');
                } else {
                    esc_html_e('Signature not verified', 'encypher-provenance');
                }
                ?>
            </h2>
            <ul class="verification-meta">
                <?php if ($document_id) : ?>
                    <li><strong><?php esc_html_e('Document ID:', 'encypher-provenance'); ?></strong> <?php echo esc_html($document_id); ?></li>
                <?php endif; ?>
                <?php if ($status) : ?>
                    <li><strong><?php esc_html_e('Status:', 'encypher-provenance'); ?></strong> <?php echo esc_html($status); ?></li>
                <?php endif; ?>
                <?php if ($organization) : ?>
                    <li><strong><?php esc_html_e('Signed by:', 'encypher-provenance'); ?></strong> <?php echo esc_html($organization); ?><?php if ($signer_id) : ?> (<?php echo esc_html($signer_id); ?>)<?php endif; ?></li>
                <?php elseif ($signer_id) : ?>
                    <li><strong><?php esc_html_e('Signer ID:', 'encypher-provenance'); ?></strong> <?php echo esc_html($signer_id); ?></li>
                <?php endif; ?>
                <?php if ($timestamp) : ?>
                    <li><strong><?php esc_html_e('Signed at:', 'encypher-provenance'); ?></strong> <?php echo esc_html($timestamp); ?></li>
                <?php endif; ?>
                <?php if ($last_signed) : ?>
                    <li><strong><?php esc_html_e('Last signed in WordPress:', 'encypher-provenance'); ?></strong> <?php echo esc_html($last_signed); ?></li>
                <?php endif; ?>
                <?php if ($total_sentences) : ?>
                    <li><strong><?php esc_html_e('Sentences protected:', 'encypher-provenance'); ?></strong> <?php echo esc_html((string) $total_sentences); ?></li>
                <?php endif; ?>
            </ul>
            <?php if ($verification_url) : ?>
                <p class="verification-link">
                    <a href="<?php echo esc_url($verification_url); ?>" target="_blank" rel="noopener">
                        <?php esc_html_e('View provenance report', 'encypher-provenance'); ?>
                    </a>
                </p>
            <?php endif; ?>
            <?php if ($manifest) : ?>
                <details class="verification-details">
                    <summary><?php esc_html_e('View manifest JSON', 'encypher-provenance'); ?></summary>
                    <pre><?php echo esc_html(wp_json_encode($manifest, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES)); ?></pre>
                </details>
            <?php endif; ?>
        </section>
        <?php
        $badge = ob_get_clean();

        return $content . $badge;
    }
}
