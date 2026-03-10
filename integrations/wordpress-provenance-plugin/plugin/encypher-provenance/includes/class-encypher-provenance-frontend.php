<?php
namespace EncypherProvenance;

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
            ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/css/frontend.css',
            [],
            ENCYPHER_PROVENANCE_VERSION
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
        $settings = get_option('encypher_provenance_settings', []);
        $show_badge = isset($settings['show_badge']) ? (bool) $settings['show_badge'] : true; // Default ON

        if (! $show_badge) {
            return $content;
        }

        $badge_position = ! empty($settings['badge_position']) ? $settings['badge_position'] : 'bottom';
        $badge_html = $this->get_badge_html($post_id, 'large');

        $this->add_verification_modal($post_id);

        if ('bottom-right' === $badge_position) {
            add_action('wp_footer', function () use ($badge_html) {
                echo $this->get_badge_wrapper($badge_html, 'floating');
            });

            return $content;
        }

        $placement = 'top' === $badge_position ? 'top' : 'bottom';
        $badge_wrapper = $this->get_badge_wrapper($badge_html, $placement);

        if ('top' === $badge_position) {
            return $badge_wrapper . $content;
        }

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
        if (! is_singular() || ! in_the_loop() || ! is_main_query()) {
            return $title;
        }

        return $title;
    }

    private function add_verification_modal(int $post_id): void
    {
        static $modal_post_ids = [];

        if (isset($modal_post_ids[$post_id])) {
            return;
        }

        add_action('wp_footer', function () use ($post_id) {
            echo $this->get_modal_html($post_id);
        });

        $modal_post_ids[$post_id] = true;
    }

    private function get_badge_wrapper(string $badge_html, string $placement): string
    {
        $classes = 'encypher-c2pa-badge-wrapper';

        if ('floating' === $placement) {
            $classes .= ' encypher-c2pa-badge-floating';
        } elseif ('top' === $placement) {
            $classes .= ' encypher-c2pa-badge-top';
        } else {
            $classes .= ' encypher-c2pa-badge-bottom';
        }

        return '<div class="' . esc_attr($classes) . '">' . $badge_html . '</div>';
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
        $settings = get_option('encypher_provenance_settings', []);
        $tier = isset($settings['tier']) ? $settings['tier'] : 'free';
        $show_branding = isset($settings['show_branding']) ? (bool) $settings['show_branding'] : true;

        // Force branding on Free tier (double check)
        if ('free' === $tier) {
            $show_branding = true;
        }

        $icon_url = ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/images/encypher-icon.png';
        $status = get_post_meta($post_id, '_encypher_provenance_status', true);
        $document_id = get_post_meta($post_id, '_encypher_provenance_document_id', true);
        $last_verified = get_post_meta($post_id, '_encypher_provenance_last_verified', true);
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
        if ('enterprise' === $tier && $is_verified) {
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
        $logo_url = ENCYPHER_PROVENANCE_PLUGIN_URL . 'assets/images/encypher-logo.png';

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
            const modal = document.getElementById('encypher-c2pa-modal');

            if (!modal) {
                return;
            }

            const closeBtn = modal.querySelector('.encypher-c2pa-modal-close');
            const overlay = modal.querySelector('.encypher-c2pa-modal-overlay');
            const loading = modal.querySelector('.encypher-c2pa-modal-loading');
            const result = modal.querySelector('.encypher-c2pa-modal-result');

            function openModal(postId) {
                modal.style.display = 'block';
                document.body.style.overflow = 'hidden';
                loading.style.display = 'block';
                result.style.display = 'none';

                fetch('<?php echo esc_url(rest_url('encypher-provenance/v1/verify')); ?>', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': '<?php echo wp_create_nonce('wp_rest'); ?>'
                    },
                    body: JSON.stringify({ post_id: postId })
                })
                .then(response => {
                    return response.json();
                })
                .then(data => {
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    result.innerHTML = formatVerificationData(data, postId);

                    // Update badge text to show "Verified" after successful verification
                    if (data.valid) {
                        const badge = document.querySelector('.encypher-c2pa-badge[data-post-id="' + postId + '"]');
                        if (badge) {
                            const textSpan = badge.querySelector('span');
                            if (textSpan && !textSpan.textContent.includes('<?php esc_html_e('Verified', 'encypher-provenance'); ?>')) {
                                textSpan.innerHTML = '<?php esc_html_e('Verified', 'encypher-provenance'); ?>';
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

            function findActions(metadata) {
                if (!metadata || !metadata.assertions) return null;
                // Try v2 first, then v1
                const actions = metadata.assertions.find(a => a.label === 'c2pa.actions.v2')
                    || metadata.assertions.find(a => a.label === 'c2pa.actions.v1');
                return (actions && actions.data && actions.data.actions) ? actions.data.actions : null;
            }

            function findMetadataAssertion(metadata) {
                if (!metadata || !metadata.assertions) return null;
                const meta = metadata.assertions.find(a => a.label === 'c2pa.metadata');
                return (meta && meta.data) ? meta.data : null;
            }

            function buildVerificationFailureHint(data) {
                const defaultMessage = '<?php esc_html_e('No valid C2PA manifest found for this content.', 'encypher-provenance'); ?>';
                const rawError = data && data.error ? String(data.error) : '';
                const lowerError = rawError.toLowerCase();

                if (!rawError) {
                    return {
                        message: defaultMessage,
                        hint: '<?php esc_html_e('Try signing this post first, then verify again.', 'encypher-provenance'); ?>'
                    };
                }

                if (lowerError.includes('invalid api key')) {
                    return {
                        message: rawError,
                        hint: '<?php esc_html_e('Invalid API key detected. Check Encypher settings and update your API key. For local E2E, use demo-api-key-for-testing.', 'encypher-provenance'); ?>'
                    };
                }

                if (lowerError.includes('not found or not published') || lowerError.includes('only published posts')) {
                    return {
                        message: rawError,
                        hint: '<?php esc_html_e('Publish the post before verification.', 'encypher-provenance'); ?>'
                    };
                }

                if (lowerError.includes('timed out') || lowerError.includes('http_error') || lowerError.includes('failed to fetch')) {
                    return {
                        message: rawError,
                        hint: '<?php esc_html_e('The verification service is temporarily unavailable. Please try again in a moment.', 'encypher-provenance'); ?>'
                    };
                }

                return {
                    message: rawError,
                    hint: '<?php esc_html_e('Failed to verify content. Please try again.', 'encypher-provenance'); ?>'
                };
            }

            function formatVerificationData(data, postId) {
                if (!data || !data.valid) {
                    const failure = buildVerificationFailureHint(data);
                    let errHtml = '<div class="encypher-error" style="text-align: center; padding: 20px;">';
                    errHtml += '<div style="font-size: 48px; margin-bottom: 12px;">⚠️</div>';
                    errHtml += '<h3 style="margin: 0 0 8px 0; color: #856404;"><?php esc_html_e('Verification Unsuccessful', 'encypher-provenance'); ?></h3>';
                    errHtml += '<p style="color: #666; margin: 0;">' + escapeHtml(failure.message) + '</p>';
                    errHtml += '<p style="color: #555; margin: 10px 0 0 0; font-size: 13px;">' + escapeHtml(failure.hint) + '</p>';
                    errHtml += '</div>';
                    return errHtml;
                }

                // Normalize metadata: for canonical micro mode, the C2PA manifest
                // (with assertions, instance_id, claim_generator) is nested inside
                // data.metadata.manifest_data.  For full C2PA mode, it's directly
                // in data.metadata.  Resolve to a single "manifest" reference.
                const rawMeta = data.metadata || {};
                const manifest = (rawMeta.manifest_data && rawMeta.manifest_data.assertions)
                    ? rawMeta.manifest_data
                    : rawMeta;
                // Top-level document_id may live on rawMeta (micro metadata) or in assertion
                const topDocumentId = rawMeta.document_id || null;
                const totalSignatures = rawMeta.total_signatures || null;
                const totalSegments = rawMeta.total_segments || null;

                let html = '<div class="encypher-verification-success">';
                html += '<div class="encypher-status-badge encypher-status-verified"><?php esc_html_e('Verified', 'encypher-provenance'); ?></div>';

                // Show cache status
                if (data.cached) {
                    html += '<p class="encypher-cache-notice" style="font-size: 0.9em; color: #666; margin: 10px 0;"><em><?php esc_html_e('(Cached result - verified within last 5 minutes)', 'encypher-provenance'); ?></em></p>';
                }

                // Summary section
                html += '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">';
                html += '<h3 style="margin: 0 0 10px 0; font-size: 14px; color: #333;"><?php esc_html_e('Verification Summary', 'encypher-provenance'); ?></h3>';

                // Prefer signing identity when available, then signer name/id fallback
                const signerDisplay = data.signing_identity || data.signer_name || data.signer_id;
                if (signerDisplay) {
                    html += '<p style="margin: 5px 0;"><strong><?php esc_html_e('Signed by:', 'encypher-provenance'); ?></strong> ' + escapeHtml(signerDisplay) + '</p>';
                }

                // Extract action info from manifest (try v2 then v1)
                // Prefer c2pa.created, fall back to c2pa.edited
                const actions = findActions(manifest);
                if (actions) {
                    const primaryAction = actions.find(a => a.label === 'c2pa.created')
                        || actions.find(a => a.label === 'c2pa.edited');
                    if (primaryAction && primaryAction.label) {
                        const actionLabel = primaryAction.label === 'c2pa.edited'
                            ? '<?php esc_html_e('Edited (provenance chain updated)', 'encypher-provenance'); ?>'
                            : '<?php esc_html_e('Created (initial signature)', 'encypher-provenance'); ?>';
                        html += '<p style="margin: 5px 0;"><strong><?php esc_html_e('Latest action:', 'encypher-provenance'); ?></strong> ' + actionLabel + '</p>';
                    }
                    if (primaryAction && primaryAction.when) {
                        const actionDate = new Date(primaryAction.when);
                        html += '<p style="margin: 5px 0;"><strong><?php esc_html_e('Signed:', 'encypher-provenance'); ?></strong> ' + actionDate.toLocaleString() + '</p>';
                    }
                    if (primaryAction && primaryAction.softwareAgent) {
                        html += '<p style="margin: 5px 0;"><strong><?php esc_html_e('Software:', 'encypher-provenance'); ?></strong> ' + escapeHtml(primaryAction.softwareAgent) + '</p>';
                    }
                }

                // Extract document_id: try top-level micro metadata, then c2pa.metadata assertion
                const metaAssertion = findMetadataAssertion(manifest);
                const documentId = topDocumentId || (metaAssertion && metaAssertion.identifier) || null;
                if (documentId) {
                    html += '<p style="margin: 5px 0;"><strong><?php esc_html_e('Document ID:', 'encypher-provenance'); ?></strong> <span style="font-family: monospace; font-size: 12px;">' + escapeHtml(documentId) + '</span></p>';
                }

                // Show sentence/signature count if available
                if (totalSignatures) {
                    html += '<p style="margin: 5px 0;"><strong><?php esc_html_e('Sentences protected:', 'encypher-provenance'); ?></strong> ' + escapeHtml(String(totalSignatures)) + '</p>';
                }

                if (data.verified_at) {
                    const verifiedDate = new Date(data.verified_at);
                    html += '<p style="margin: 5px 0;"><strong><?php esc_html_e('Verified at:', 'encypher-provenance'); ?></strong> ' + verifiedDate.toLocaleString() + '</p>';
                }

                // Show instance_id from manifest
                if (manifest.instance_id) {
                    html += '<p style="margin: 5px 0;"><strong><?php esc_html_e('Instance:', 'encypher-provenance'); ?></strong> <span style="font-family: monospace; font-size: 12px;">' + escapeHtml(manifest.instance_id) + '</span></p>';
                }

                // Assertions chip summary
                if (manifest.assertions && manifest.assertions.length > 0) {
                    html += '<div style="margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px;">';
                    manifest.assertions.forEach(function(assertion) {
                        const label = assertion.label || '';
                        let bgColor = '#e9ecef'; let textColor = '#333';
                        if (label.includes('actions')) { bgColor = '#d4edda'; textColor = '#155724'; }
                        else if (label.includes('hash')) { bgColor = '#cce5ff'; textColor = '#004085'; }
                        else if (label.includes('binding')) { bgColor = '#fff3cd'; textColor = '#856404'; }
                        else if (label.includes('metadata')) { bgColor = '#e2e3e5'; textColor = '#383d41'; }
                        else if (label.includes('status')) { bgColor = '#f8d7da'; textColor = '#721c24'; }
                        html += '<span style="display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 11px; background: ' + bgColor + '; color: ' + textColor + ';">' + escapeHtml(assertion.kind || label.split('.').pop()) + '</span>';
                    });
                    html += '</div>';
                }

                html += '</div>';

                // Provenance chain viewer (if ingredients exist)
                // Use normalized manifest for ingredients check (handles both full C2PA and micro manifest metadata)
                if (manifest.ingredients && manifest.ingredients.length > 0) {
                    html += '<details style="margin: 15px 0;">';
                    html += '<summary style="cursor: pointer; padding: 10px; background: #28a745; color: white; border-radius: 4px; font-weight: 600;"><?php esc_html_e('View Provenance Chain', 'encypher-provenance'); ?></summary>';
                    html += '<div style="padding: 15px; border: 1px solid #dee2e6; border-top: none; border-radius: 0 0 4px 4px; background: #f8f9fa;">';
                    html += '<p style="margin-bottom: 15px; color: #666;"><?php esc_html_e('This content has been edited. View the complete edit history:', 'encypher-provenance'); ?></p>';

                    let chain = [];
                    let current = manifest;
                    let depth = 0;
                    while (current && depth < 10) {
                        const chainActions = findActions(current) || [];
                        const mainAction = chainActions.find(a => a.label === 'c2pa.created' || a.label === 'c2pa.edited');
                        chain.push({
                            instance_id: current.instance_id || 'unknown',
                            action: mainAction?.label || 'unknown',
                            when: mainAction?.when || null,
                            depth: depth
                        });
                        current = current.ingredients?.[0]?.c2pa_manifest;
                        depth++;
                    }

                    html += '<div style="font-size: 13px;">';
                    for (let i = 0; i < chain.length; i++) {
                        const item = chain[i];
                        const label = item.action === 'c2pa.created' ? 'Created' : 'Edited';
                        const color = item.action === 'c2pa.created' ? '#28a745' : '#ffc107';
                        const whenStr = item.when ? new Date(item.when).toLocaleString() : 'unknown';
                        html += '<div style="padding: 8px; margin: 5px 0; background: white; border-left: 3px solid ' + color + '; border-radius: 4px;">';
                        html += '<strong>' + label + '</strong> — ' + whenStr;
                        html += '<br><span style="color: #999; font-size: 11px;">Instance: ' + escapeHtml(item.instance_id.substring(0, 12)) + '...</span>';
                        html += '</div>';
                    }
                    html += '</div>';
                    html += '</div></details>';
                }

                // Full manifest JSON viewer (collapsed by default)
                if (data.metadata) {
                    html += '<details style="margin: 15px 0;">';
                    html += '<summary style="cursor: pointer; padding: 10px; background: #1B2F50; color: white; border-radius: 4px; font-weight: 600;"><?php esc_html_e('View Complete C2PA Manifest (JSON)', 'encypher-provenance'); ?></summary>';
                    html += '<div style="padding: 15px; border: 1px solid #dee2e6; border-top: none; border-radius: 0 0 4px 4px; background: #f8f9fa;">';
                    html += '<pre id="c2pa-manifest-json" style="background: #2b2b2b; color: #f8f8f2; padding: 20px; border-radius: 6px; overflow-x: auto; font-size: 13px; line-height: 1.5; font-family: \'Courier New\', monospace; margin: 0; max-height: 400px;">';
                    html += escapeHtml(JSON.stringify(data.metadata, null, 2));
                    html += '</pre>';
                    html += '<p style="margin-top: 15px; font-size: 12px; color: #666; text-align: center;">';
                    html += '<button id="copy-manifest-btn" style="padding: 8px 16px; background: #2A87C4; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 500;">Copy to Clipboard</button>';
                    html += '</p>';
                    html += '</div></details>';

                    setTimeout(function() {
                        const copyBtn = document.getElementById('copy-manifest-btn');
                        if (copyBtn) {
                            copyBtn.onclick = function() {
                                const json = JSON.stringify(data.metadata, null, 2);
                                navigator.clipboard.writeText(json).then(function() {
                                    copyBtn.textContent = 'Copied!';
                                    setTimeout(function() { copyBtn.textContent = 'Copy to Clipboard'; }, 2000);
                                }).catch(function(err) {
                                    console.error('Failed to copy:', err);
                                    copyBtn.textContent = 'Copy failed';
                                    setTimeout(function() { copyBtn.textContent = 'Copy to Clipboard'; }, 2000);
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

            // Event delegation: the badge wrapper is added to wp_footer AFTER
            // the modal script, so direct querySelectorAll finds 0 elements at
            // script parse time.  Attach to document instead.
            document.addEventListener('click', function(e) {
                const clickedBadge = e.target.closest('.encypher-c2pa-badge');
                if (clickedBadge) {
                    e.preventDefault();
                    openModal(clickedBadge.getAttribute('data-post-id'));
                }
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
