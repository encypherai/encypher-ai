# PRD: WordPress Plugin - Enterprise Features

**Status:** In Progress  
**Priority:** P1 (High)  
**Owner:** TBD  
**Created:** November 11, 2025  
**Target Completion:** December 5, 2025

---

## Executive Summary

Upgrade the WordPress Provenance Plugin to support all Enterprise API features, including enhanced embeddings, Merkle tree visualization, sentence-level verification, and batch operations.

---

## 🎯 Objectives

1. **Enhanced Embeddings** - Support sentence-level signing with Merkle trees
2. **Visual Provenance** - Display Merkle trees and verification status
3. **Batch Operations** - Sign/verify multiple posts at once
4. **Auto-Signing** - Automatic signing on publish/update
5. **Admin Dashboard** - Comprehensive settings and analytics

---

## 📋 Current Status

### Existing Features ✅
- [x] Basic C2PA signing
- [x] Gutenberg block for signing
- [x] Classic editor support
- [x] Manual sign/verify buttons
- [x] API key configuration

### Missing Enterprise Features 🔴
- [ ] Enhanced embeddings (sentence-level)
- [ ] Merkle tree visualization
- [ ] Sentence-level verification
- [ ] Batch signing/verification
- [ ] Auto-signing on publish
- [ ] Verification badge display
- [ ] Analytics dashboard

---

## 📋 Requirements

### 1. Enhanced Embeddings Support

#### Settings Page Updates

```php
// Add signing mode selector
add_settings_field(
    'encypher_signing_mode',
    __('Signing Mode', 'encypher'),
    'encypher_signing_mode_callback',
    'encypher-settings',
    'encypher_main_section'
);

function encypher_signing_mode_callback() {
    $mode = get_option('encypher_signing_mode', 'c2pa');
    ?>
    <select name="encypher_signing_mode" id="encypher_signing_mode">
        <option value="c2pa" <?php selected($mode, 'c2pa'); ?>>
            C2PA Only (Fast, Document-level)
        </option>
        <option value="embeddings" <?php selected($mode, 'embeddings'); ?>>
            Enhanced Embeddings (Sentence-level, Detailed)
        </option>
    </select>
    <p class="description">
        C2PA: 15.6x faster, document-level provenance<br>
        Embeddings: Sentence-level provenance, 3.6x more granular
    </p>
    <?php
}
```

#### API Integration

```php
// Update signing function to support both modes
function encypher_sign_content($post_id) {
    $mode = get_option('encypher_signing_mode', 'c2pa');
    $api_key = get_option('encypher_api_key');
    $api_url = get_option('encypher_api_url', 'https://api.encypherai.com');
    
    $post = get_post($post_id);
    $content = $post->post_content;
    
    if ($mode === 'embeddings') {
        // Enhanced embeddings endpoint
        $endpoint = $api_url . '/api/v1/enterprise/embeddings/encode-with-embeddings';
        $body = array(
            'document_id' => 'wp-post-' . $post_id,
            'text' => $content,
            'segmentation_level' => 'sentence',
        );
    } else {
        // C2PA endpoint
        $endpoint = $api_url . '/api/v1/sign';
        $body = array(
            'document_id' => 'wp-post-' . $post_id,
            'text' => $content,
        );
    }
    
    $response = wp_remote_post($endpoint, array(
        'headers' => array(
            'Authorization' => 'Bearer ' . $api_key,
            'Content-Type' => 'application/json',
        ),
        'body' => json_encode($body),
        'timeout' => 30,
    ));
    
    if (is_wp_error($response)) {
        return $response;
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    
    // Store metadata
    if ($mode === 'embeddings') {
        update_post_meta($post_id, '_encypher_embedded_content', $data['embedded_content']);
        update_post_meta($post_id, '_encypher_merkle_tree', json_encode($data['merkle_tree']));
        update_post_meta($post_id, '_encypher_embeddings', json_encode($data['embeddings']));
        update_post_meta($post_id, '_encypher_mode', 'embeddings');
    } else {
        update_post_meta($post_id, '_encypher_signed_content', $data['signed_content']);
        update_post_meta($post_id, '_encypher_mode', 'c2pa');
    }
    
    update_post_meta($post_id, '_encypher_signed', true);
    update_post_meta($post_id, '_encypher_signed_at', current_time('mysql'));
    
    return $data;
}
```

### 2. Merkle Tree Visualization

#### Admin Meta Box

```php
// Add Merkle tree meta box
add_action('add_meta_boxes', 'encypher_add_merkle_tree_meta_box');

function encypher_add_merkle_tree_meta_box() {
    add_meta_box(
        'encypher_merkle_tree',
        __('Content Provenance Tree', 'encypher'),
        'encypher_merkle_tree_callback',
        'post',
        'side',
        'high'
    );
}

function encypher_merkle_tree_callback($post) {
    $mode = get_post_meta($post->ID, '_encypher_mode', true);
    $is_signed = get_post_meta($post->ID, '_encypher_signed', true);
    
    if (!$is_signed) {
        echo '<p>' . __('This post has not been signed yet.', 'encypher') . '</p>';
        return;
    }
    
    if ($mode !== 'embeddings') {
        echo '<p>' . __('Merkle tree only available for Enhanced Embeddings mode.', 'encypher') . '</p>';
        return;
    }
    
    $merkle_tree = json_decode(get_post_meta($post->ID, '_encypher_merkle_tree', true), true);
    $embeddings = json_decode(get_post_meta($post->ID, '_encypher_embeddings', true), true);
    
    ?>
    <div class="encypher-merkle-tree">
        <div class="encypher-stats">
            <p><strong><?php _e('Root Hash:', 'encypher'); ?></strong><br>
            <code><?php echo esc_html(substr($merkle_tree['root_hash'], 0, 16)); ?>...</code></p>
            
            <p><strong><?php _e('Sentences:', 'encypher'); ?></strong> 
            <?php echo count($embeddings); ?></p>
            
            <p><strong><?php _e('Tree Depth:', 'encypher'); ?></strong> 
            <?php echo $merkle_tree['depth']; ?></p>
        </div>
        
        <button type="button" class="button" id="encypher-view-tree">
            <?php _e('View Full Tree', 'encypher'); ?>
        </button>
        
        <button type="button" class="button" id="encypher-verify-sentences">
            <?php _e('Verify Sentences', 'encypher'); ?>
        </button>
    </div>
    
    <script>
    jQuery(document).ready(function($) {
        $('#encypher-view-tree').on('click', function() {
            // Open modal with tree visualization
            EncypherTreeViewer.show(<?php echo json_encode($merkle_tree); ?>);
        });
        
        $('#encypher-verify-sentences').on('click', function() {
            // Verify each sentence and highlight results
            EncypherVerifier.verifySentences(<?php echo $post->ID; ?>);
        });
    });
    </script>
    <?php
}
```

#### Tree Visualization (JavaScript)

```javascript
// assets/js/tree-viewer.js
const EncypherTreeViewer = {
    show: function(merkleTree) {
        // Create modal
        const modal = document.createElement('div');
        modal.className = 'encypher-modal';
        modal.innerHTML = `
            <div class="encypher-modal-content">
                <span class="encypher-modal-close">&times;</span>
                <h2>Content Provenance Tree</h2>
                <div id="encypher-tree-container"></div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Render tree using D3.js or similar
        this.renderTree(merkleTree, '#encypher-tree-container');
        
        // Close handler
        modal.querySelector('.encypher-modal-close').onclick = function() {
            modal.remove();
        };
    },
    
    renderTree: function(merkleTree, container) {
        // Use D3.js or Canvas to render tree
        // Show nodes, hashes, and relationships
        const svg = d3.select(container)
            .append('svg')
            .attr('width', 800)
            .attr('height', 600);
        
        // ... tree rendering logic
    }
};
```

### 3. Sentence-Level Verification

#### Content Highlighter

```php
// Add verification status to content
add_filter('the_content', 'encypher_highlight_sentences');

function encypher_highlight_sentences($content) {
    if (!is_single()) {
        return $content;
    }
    
    global $post;
    $mode = get_post_meta($post->ID, '_encypher_mode', true);
    
    if ($mode !== 'embeddings') {
        return $content;
    }
    
    $embeddings = json_decode(get_post_meta($post->ID, '_encypher_embeddings', true), true);
    
    if (empty($embeddings)) {
        return $content;
    }
    
    // Wrap each sentence with verification data
    $sentences = explode('. ', $content);
    $highlighted = '';
    
    foreach ($sentences as $index => $sentence) {
        if (isset($embeddings[$index])) {
            $hash = $embeddings[$index]['hash'];
            $highlighted .= sprintf(
                '<span class="encypher-sentence" data-index="%d" data-hash="%s">%s</span>. ',
                $index,
                esc_attr($hash),
                esc_html($sentence)
            );
        } else {
            $highlighted .= $sentence . '. ';
        }
    }
    
    return $highlighted;
}
```

#### Verification JavaScript

```javascript
// assets/js/sentence-verifier.js
const EncypherVerifier = {
    verifySentences: async function(postId) {
        const sentences = document.querySelectorAll('.encypher-sentence');
        
        for (const sentence of sentences) {
            const index = sentence.dataset.index;
            const hash = sentence.dataset.hash;
            
            try {
                const response = await fetch('/wp-json/encypher/v1/verify-sentence', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': encypherData.nonce
                    },
                    body: JSON.stringify({
                        post_id: postId,
                        sentence_index: index,
                        expected_hash: hash
                    })
                });
                
                const result = await response.json();
                
                if (result.valid) {
                    sentence.classList.add('encypher-verified');
                    sentence.title = 'Verified ✓';
                } else {
                    sentence.classList.add('encypher-tampered');
                    sentence.title = 'Tampered ✗';
                }
            } catch (error) {
                console.error('Verification error:', error);
                sentence.classList.add('encypher-error');
            }
        }
    }
};
```

### 4. Batch Operations

#### Bulk Actions

```php
// Add bulk actions
add_filter('bulk_actions-edit-post', 'encypher_register_bulk_actions');

function encypher_register_bulk_actions($bulk_actions) {
    $bulk_actions['encypher_sign'] = __('Sign with Encypher', 'encypher');
    $bulk_actions['encypher_verify'] = __('Verify with Encypher', 'encypher');
    return $bulk_actions;
}

// Handle bulk actions
add_filter('handle_bulk_actions-edit-post', 'encypher_handle_bulk_actions', 10, 3);

function encypher_handle_bulk_actions($redirect_to, $action, $post_ids) {
    if ($action === 'encypher_sign') {
        $signed = 0;
        $failed = 0;
        
        foreach ($post_ids as $post_id) {
            $result = encypher_sign_content($post_id);
            if (is_wp_error($result)) {
                $failed++;
            } else {
                $signed++;
            }
        }
        
        $redirect_to = add_query_arg(array(
            'encypher_signed' => $signed,
            'encypher_failed' => $failed,
        ), $redirect_to);
    }
    
    if ($action === 'encypher_verify') {
        // Similar logic for verification
    }
    
    return $redirect_to;
}

// Show admin notice
add_action('admin_notices', 'encypher_bulk_action_notices');

function encypher_bulk_action_notices() {
    if (!empty($_REQUEST['encypher_signed'])) {
        $signed = intval($_REQUEST['encypher_signed']);
        $failed = intval($_REQUEST['encypher_failed']);
        
        printf(
            '<div class="notice notice-success is-dismissible"><p>%s</p></div>',
            sprintf(
                __('Signed %d posts. %d failed.', 'encypher'),
                $signed,
                $failed
            )
        );
    }
}
```

### 5. Auto-Signing

#### Publish Hook

```php
// Auto-sign on publish
add_action('publish_post', 'encypher_auto_sign', 10, 2);

function encypher_auto_sign($post_id, $post) {
    // Check if auto-signing is enabled
    if (!get_option('encypher_auto_sign', false)) {
        return;
    }
    
    // Skip if already signed
    if (get_post_meta($post_id, '_encypher_signed', true)) {
        return;
    }
    
    // Skip revisions and autosaves
    if (wp_is_post_revision($post_id) || wp_is_post_autosave($post_id)) {
        return;
    }
    
    // Sign the content
    encypher_sign_content($post_id);
}

// Add setting
add_settings_field(
    'encypher_auto_sign',
    __('Auto-Sign on Publish', 'encypher'),
    'encypher_auto_sign_callback',
    'encypher-settings',
    'encypher_main_section'
);

function encypher_auto_sign_callback() {
    $auto_sign = get_option('encypher_auto_sign', false);
    ?>
    <label>
        <input type="checkbox" name="encypher_auto_sign" value="1" 
               <?php checked($auto_sign, true); ?>>
        <?php _e('Automatically sign posts when published', 'encypher'); ?>
    </label>
    <?php
}
```

### 6. Verification Badge

#### Frontend Display

```php
// Add verification badge to posts
add_filter('the_content', 'encypher_add_verification_badge');

function encypher_add_verification_badge($content) {
    if (!is_single()) {
        return $content;
    }
    
    global $post;
    $is_signed = get_post_meta($post->ID, '_encypher_signed', true);
    
    if (!$is_signed) {
        return $content;
    }
    
    $mode = get_post_meta($post->ID, '_encypher_mode', true);
    $signed_at = get_post_meta($post->ID, '_encypher_signed_at', true);
    
    $badge = sprintf(
        '<div class="encypher-verification-badge">
            <div class="encypher-badge-icon">✓</div>
            <div class="encypher-badge-text">
                <strong>%s</strong><br>
                <small>%s | %s</small>
            </div>
        </div>',
        __('Verified Content', 'encypher'),
        $mode === 'embeddings' ? __('Sentence-level', 'encypher') : __('Document-level', 'encypher'),
        sprintf(__('Signed %s', 'encypher'), human_time_diff(strtotime($signed_at)))
    );
    
    return $badge . $content;
}
```

#### Badge Styles

```css
/* assets/css/verification-badge.css */
.encypher-verification-badge {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 8px;
    margin-bottom: 24px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.encypher-badge-icon {
    font-size: 32px;
    line-height: 1;
}

.encypher-badge-text strong {
    font-size: 16px;
    display: block;
    margin-bottom: 4px;
}

.encypher-badge-text small {
    font-size: 12px;
    opacity: 0.9;
}

.encypher-sentence.encypher-verified {
    background-color: rgba(76, 175, 80, 0.1);
    border-bottom: 2px solid #4caf50;
    cursor: help;
}

.encypher-sentence.encypher-tampered {
    background-color: rgba(244, 67, 54, 0.1);
    border-bottom: 2px solid #f44336;
    cursor: help;
}
```

### 7. Analytics Dashboard

#### Dashboard Widget

```php
// Add dashboard widget
add_action('wp_dashboard_setup', 'encypher_add_dashboard_widget');

function encypher_add_dashboard_widget() {
    wp_add_dashboard_widget(
        'encypher_stats',
        __('Encypher Statistics', 'encypher'),
        'encypher_dashboard_widget_callback'
    );
}

function encypher_dashboard_widget_callback() {
    global $wpdb;
    
    // Get stats
    $total_posts = wp_count_posts('post')->publish;
    $signed_posts = $wpdb->get_var("
        SELECT COUNT(*) FROM {$wpdb->postmeta}
        WHERE meta_key = '_encypher_signed' AND meta_value = '1'
    ");
    $embeddings_posts = $wpdb->get_var("
        SELECT COUNT(*) FROM {$wpdb->postmeta}
        WHERE meta_key = '_encypher_mode' AND meta_value = 'embeddings'
    ");
    
    $percentage = $total_posts > 0 ? round(($signed_posts / $total_posts) * 100) : 0;
    
    ?>
    <div class="encypher-dashboard-stats">
        <div class="encypher-stat">
            <div class="encypher-stat-value"><?php echo $signed_posts; ?></div>
            <div class="encypher-stat-label"><?php _e('Signed Posts', 'encypher'); ?></div>
        </div>
        
        <div class="encypher-stat">
            <div class="encypher-stat-value"><?php echo $percentage; ?>%</div>
            <div class="encypher-stat-label"><?php _e('Coverage', 'encypher'); ?></div>
        </div>
        
        <div class="encypher-stat">
            <div class="encypher-stat-value"><?php echo $embeddings_posts; ?></div>
            <div class="encypher-stat-label"><?php _e('Enhanced Embeddings', 'encypher'); ?></div>
        </div>
    </div>
    
    <div class="encypher-dashboard-actions">
        <a href="<?php echo admin_url('edit.php?encypher_filter=unsigned'); ?>" class="button">
            <?php _e('View Unsigned Posts', 'encypher'); ?>
        </a>
        <a href="<?php echo admin_url('options-general.php?page=encypher-settings'); ?>" class="button">
            <?php _e('Settings', 'encypher'); ?>
        </a>
    </div>
    <?php
}
```

---

## 📦 Deliverables

### Phase 1: Enhanced Embeddings (Week 1-2)
- [ ] Add signing mode selector to settings
- [ ] Update API integration for embeddings endpoint
- [ ] Store Merkle tree and embeddings metadata
- [ ] Basic Merkle tree meta box

### Phase 2: Visualization (Week 3-4)
- [ ] Merkle tree visualization modal
- [ ] Sentence highlighter in content
- [ ] Verification badge frontend display
- [ ] CSS styling for all components

### Phase 3: Batch & Auto (Week 5-6)
- [ ] Bulk sign/verify actions
- [ ] Auto-signing on publish
- [ ] Batch processing UI
- [ ] Progress indicators

### Phase 4: Analytics & Polish (Week 7-8)
- [ ] Dashboard widget with stats
- [ ] Analytics page
- [ ] Documentation updates
- [ ] Testing and bug fixes

---

## 🎯 Success Criteria

- [ ] All enterprise features functional
- [ ] Merkle tree visualization working
- [ ] Sentence-level verification working
- [ ] Batch operations tested with 100+ posts
- [ ] Auto-signing reliable
- [ ] Documentation complete
- [ ] Compatible with WordPress 6.0+
- [ ] Compatible with PHP 8.0+
- [ ] No performance degradation

---

**Last Updated:** November 11, 2025  
**Next Review:** November 18, 2025
