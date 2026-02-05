# Coalition GTM Strategy: Sentence-Level Embeddings & Advanced User Flexibility

**Date**: 2026-02-03  
**Team**: TEAM_148  
**Status**: 📋 **PROPOSAL**

---

## Executive Summary

This document proposes strategic enhancements to the WordPress Provenance Plugin to:

1. **Enable sentence-level embeddings for free tier coalition members** - Increase content value for AI licensing
2. **Provide minimal embeddings by default for advanced users** - Reduce overhead while maintaining functionality
3. **Add toggleable advanced signing options** - Give Pro/Enterprise users granular control

---

## Current State Analysis

### Tier-Based Feature Matrix

| Feature | Starter (Free) | Professional | Business | Enterprise |
|---------|----------------|--------------|----------|------------|
| **Endpoint** | `/sign` | `/sign/advanced` | `/sign/advanced` | `/sign/advanced` |
| **Segmentation** | Document-level | Sentence-level | Sentence-level | Sentence-level |
| **Embeddings** | ❌ None | ✅ Full | ✅ Full | ✅ Full |
| **Merkle Trees** | ❌ None | ✅ Yes | ✅ Yes | ✅ Yes |
| **Coalition** | ✅ Required | ✅ Optional | ✅ Optional | ✅ Optional |
| **Provenance Chain** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |

### Coalition Revenue Splits

| Tier | Member % | Encypher % | Payout Threshold |
|------|----------|------------|------------------|
| Starter | 65% | 35% | $50 |
| Professional | 70% | 30% | $10 |
| Business | 75% | 25% | $0 |
| Enterprise | 80% | 20% | $0 |

---

## Problem Statement

### For Free Tier Coalition Members

**Current Issue**: Free tier users only get document-level signing with no embeddings, which:
- ❌ **Reduces content value** for AI licensing (no granular attribution)
- ❌ **Limits plagiarism detection** (can't match sentence-level segments)
- ❌ **Decreases coalition pool quality** (less valuable for bulk licensing)
- ❌ **Reduces upgrade incentive** (unclear value difference between tiers)

**Impact on GTM**:
- Lower licensing revenue per free user
- Less attractive coalition offering for AI companies
- Harder to demonstrate value proposition for upgrades

### For Advanced Users

**Current Issue**: Pro/Enterprise users get full embeddings by default, which:
- ❌ **Increases signing overhead** (longer processing time)
- ❌ **Increases storage costs** (more data per document)
- ❌ **No flexibility** (can't opt for minimal embeddings when not needed)
- ❌ **One-size-fits-all** (no customization for different content types)

**Impact on UX**:
- Slower signing for high-volume publishers
- Unnecessary costs for simple use cases
- No control over advanced features

---

## Proposed Solution

### 1. Coalition-Enhanced Free Tier

**Concept**: Free tier users who opt into the coalition get **minimal sentence-level embeddings** as a benefit.

#### Implementation Strategy

**Option A: Coalition-Gated `/sign/advanced` (Recommended)**

```php
// In class-encypher-provenance-rest.php
$is_starter = ($tier === 'starter');
$coalition_enabled = isset($settings['coalition_enabled']) ? (bool) $settings['coalition_enabled'] : true;

if ($is_starter) {
    if ($coalition_enabled) {
        // Coalition members get minimal sentence-level embeddings
        $unique_document_id = sprintf('wp_post_%d_v%d_%s', $post_id, time(), substr(md5(uniqid((string) $post_id, true)), 0, 8));
        
        $payload = [
            'document_id' => $unique_document_id,
            'text' => $clean_content,
            'segmentation_level' => 'sentence',  // ✅ Sentence-level for coalition
            'action' => $action_type,
            'metadata' => [
                'title' => $post->post_title,
                'url' => get_permalink($post),
                'wordpress_post_id' => $post_id,
                'tier' => 'starter_coalition',  // Special tier identifier
                'coalition_member' => true,
            ],
            // Minimal embedding options
            'embedding_options' => [
                'minimal' => true,  // Flag for minimal embeddings
                'skip_attribution_index' => false,  // Keep for coalition licensing
                'skip_plagiarism_index' => true,   // Not needed for free tier
            ],
        ];
        $response = $this->call_backend('/sign/advanced', $payload, true);
    } else {
        // Non-coalition free users get basic document-level
        $unique_document_id = sprintf('wp_post_%d_v%d_%s', $post_id, time(), substr(md5(uniqid((string) $post_id, true)), 0, 8));
        
        $payload = [
            'text' => $clean_content,
            'document_id' => $unique_document_id,
            'document_title' => $post->post_title,
            'document_url' => get_permalink($post),
            'document_type' => 'article',
            'claim_generator' => 'WordPress/Encypher Plugin v' . ENCYPHER_ASSURANCE_VERSION,
        ];
        $response = $this->call_backend('/sign', $payload, true);
    }
}
```

**Option B: New `/sign/coalition` Endpoint**

Create a dedicated endpoint for coalition members:
- `POST /api/v1/sign/coalition` - Minimal sentence-level embeddings
- Requires `coalition_member: true` in organization metadata
- Automatically applies minimal embedding settings

#### Benefits

✅ **For Free Users**:
- Sentence-level attribution (better licensing value)
- Merkle tree tamper detection
- Increased coalition pool quality
- Clear upgrade path (minimal → full embeddings)

✅ **For Encypher**:
- Higher quality coalition content pool
- Better AI licensing deals (granular attribution)
- Stronger upgrade incentive (full embeddings vs minimal)
- Differentiated free tier value proposition

✅ **For AI Companies**:
- Granular attribution data (sentence-level)
- Better content quality metrics
- More valuable licensing deals

#### Costs

⚠️ **Increased Infrastructure**:
- More embeddings storage for free tier
- Higher compute costs per free user signing
- Larger database footprint

**Mitigation**:
- Minimal embeddings only (no full attribution index)
- Rate limiting per free tier (e.g., 100 signs/month)
- Coalition-only feature (opt-in required)

---

### 2. Minimal Embeddings for Advanced Users

**Concept**: Pro/Enterprise users can choose between **minimal** and **full** embeddings based on their needs.

#### Embedding Levels

| Level | Use Case | Features | Overhead |
|-------|----------|----------|----------|
| **None** | Public content, no attribution needed | C2PA only | Minimal |
| **Minimal** | Coalition licensing, basic attribution | Sentence-level Merkle trees, no full index | Low |
| **Standard** | Attribution tracking, plagiarism detection | Full embeddings, attribution index | Medium |
| **Full** | Advanced analytics, heat maps, fuzzy search | All features, full indexing | High |

#### Implementation

**Plugin Settings UI**:

```php
// In class-encypher-provenance-admin.php
add_settings_field(
    'encypher_assurance_embedding_level',
    __('Embedding Level', 'encypher-provenance'),
    [$this, 'render_embedding_level_field'],
    'encypher-provenance-settings',
    'encypher_assurance_advanced_section'
);

public function render_embedding_level_field(): void
{
    $options = get_option('encypher_assurance_settings', []);
    $tier = $options['tier'] ?? 'starter';
    $embedding_level = $options['embedding_level'] ?? 'standard';
    
    if ($tier === 'starter') {
        echo '<p>' . esc_html__('Embedding level is automatically determined based on coalition membership.', 'encypher-provenance') . '</p>';
        return;
    }
    
    ?>
    <select name="encypher_assurance_settings[embedding_level]">
        <option value="none" <?php selected($embedding_level, 'none'); ?>>
            <?php esc_html_e('None - C2PA only (fastest, no attribution)', 'encypher-provenance'); ?>
        </option>
        <option value="minimal" <?php selected($embedding_level, 'minimal'); ?>>
            <?php esc_html_e('Minimal - Sentence-level Merkle trees (recommended)', 'encypher-provenance'); ?>
        </option>
        <option value="standard" <?php selected($embedding_level, 'standard'); ?>>
            <?php esc_html_e('Standard - Full attribution & plagiarism detection', 'encypher-provenance'); ?>
        </option>
        <option value="full" <?php selected($embedding_level, 'full'); ?>>
            <?php esc_html_e('Full - Advanced analytics & fuzzy search', 'encypher-provenance'); ?>
        </option>
    </select>
    <p class="description">
        <?php esc_html_e('Choose the level of embeddings to generate. Minimal is recommended for most users (fastest signing, lowest overhead).', 'encypher-provenance'); ?>
    </p>
    <?php
}
```

**Payload Construction**:

```php
// In class-encypher-provenance-rest.php
$embedding_level = isset($settings['embedding_level']) ? $settings['embedding_level'] : 'standard';

$payload = [
    'document_id' => 'wp_post_' . $post_id,
    'text' => $clean_content,
    'segmentation_level' => 'sentence',
    'action' => $action_type,
    'previous_instance_id' => $previous_instance_id,
    'metadata' => [/* ... */],
];

// Apply embedding level settings
switch ($embedding_level) {
    case 'none':
        $payload['segmentation_level'] = 'document';
        $payload['index_for_attribution'] = false;
        $payload['index_for_plagiarism'] = false;
        break;
    
    case 'minimal':
        $payload['segmentation_level'] = 'sentence';
        $payload['index_for_attribution'] = true;  // For coalition licensing
        $payload['index_for_plagiarism'] = false;  // Skip expensive indexing
        $payload['embedding_options'] = [
            'minimal' => true,
            'skip_fuzzy_indexing' => true,
        ];
        break;
    
    case 'standard':
        $payload['segmentation_level'] = 'sentence';
        $payload['index_for_attribution'] = true;
        $payload['index_for_plagiarism'] = true;
        break;
    
    case 'full':
        $payload['segmentation_level'] = 'sentence';
        $payload['segmentation_levels'] = ['sentence', 'paragraph'];  // Multi-level
        $payload['index_for_attribution'] = true;
        $payload['index_for_plagiarism'] = true;
        $payload['embedding_options'] = [
            'include_fuzzy_indexing' => true,
            'include_semantic_embeddings' => true,
        ];
        break;
}
```

#### Benefits

✅ **For Advanced Users**:
- **Faster signing** (minimal embeddings = less processing)
- **Lower costs** (less storage, less compute)
- **Flexibility** (choose level per content type)
- **Granular control** (toggle features as needed)

✅ **For Encypher**:
- **Reduced infrastructure costs** (less unnecessary indexing)
- **Better user experience** (faster signing)
- **Clearer value tiers** (minimal → standard → full)

---

### 3. Toggleable Advanced Signing Options

**Concept**: Pro/Enterprise users get granular control over signing features via plugin settings.

#### Proposed Settings

**Advanced Signing Options Section**:

```php
// Settings fields
- [x] Enable sentence-level segmentation
- [x] Enable attribution indexing
- [x] Enable plagiarism detection indexing
- [x] Enable fuzzy search indexing
- [x] Enable multi-level Merkle trees (sentence + paragraph)
- [x] Enable semantic embeddings
- [x] Enable provenance chain tracking
- [x] Enable custom assertions
```

**Per-Post Override**:

Add meta box in Gutenberg editor:
```
┌─────────────────────────────────────┐
│ Encypher Signing Options            │
├─────────────────────────────────────┤
│ Embedding Level: [Minimal ▼]        │
│                                     │
│ Advanced Options:                   │
│ ☑ Attribution indexing              │
│ ☐ Plagiarism detection              │
│ ☐ Fuzzy search                      │
│ ☑ Provenance chain                  │
│                                     │
│ [Sign with C2PA]                    │
└─────────────────────────────────────┘
```

#### Implementation

**Plugin Settings**:

```php
// Default settings (applied globally)
$default_options = [
    'segmentation_level' => 'sentence',
    'enable_attribution' => true,
    'enable_plagiarism' => true,
    'enable_fuzzy_search' => false,  // Expensive, off by default
    'enable_multi_level_merkle' => false,
    'enable_semantic_embeddings' => false,
    'enable_provenance_chain' => true,
];

// Per-post override (stored in post meta)
$post_options = get_post_meta($post_id, '_encypher_signing_options', true);
$effective_options = wp_parse_args($post_options, $default_options);
```

**Payload Construction**:

```php
$payload = [
    'document_id' => 'wp_post_' . $post_id,
    'text' => $clean_content,
    'segmentation_level' => $effective_options['segmentation_level'],
    'action' => $action_type,
    'previous_instance_id' => $previous_instance_id,
    'index_for_attribution' => $effective_options['enable_attribution'],
    'index_for_plagiarism' => $effective_options['enable_plagiarism'],
    'metadata' => [/* ... */],
];

if ($effective_options['enable_multi_level_merkle']) {
    $payload['segmentation_levels'] = ['sentence', 'paragraph'];
}

if ($effective_options['enable_fuzzy_search'] || $effective_options['enable_semantic_embeddings']) {
    $payload['embedding_options'] = [
        'include_fuzzy_indexing' => $effective_options['enable_fuzzy_search'],
        'include_semantic_embeddings' => $effective_options['enable_semantic_embeddings'],
    ];
}
```

---

## Revised Tier Strategy

### Starter (Free) - Coalition-Enhanced

**Default (No Coalition)**:
- Document-level signing via `/sign`
- No embeddings
- No attribution
- Basic C2PA manifest

**Coalition Member** (Recommended):
- ✅ **Sentence-level segmentation**
- ✅ **Minimal embeddings** (Merkle trees only)
- ✅ **Attribution indexing** (for licensing)
- ❌ No plagiarism detection
- ❌ No provenance chain
- ❌ No advanced features

**Value Proposition**: "Join the coalition to unlock sentence-level attribution and earn revenue from AI licensing"

### Professional ($99/mo)

**Default Settings**:
- Sentence-level segmentation
- **Minimal embeddings** (recommended)
- Attribution indexing
- Plagiarism detection
- Provenance chain tracking
- BYOK support

**Toggleable Options**:
- Embedding level (none/minimal/standard/full)
- Fuzzy search indexing
- Multi-level Merkle trees
- Semantic embeddings

**Value Proposition**: "Full control over embeddings, BYOK, and provenance chains"

### Business/Enterprise

**Default Settings**:
- All Professional features
- **Standard embeddings** (full attribution + plagiarism)
- Multi-level Merkle trees
- Priority support

**Toggleable Options**:
- All advanced features
- Custom assertions
- HSM-backed keys (Enterprise)
- Dedicated infrastructure (Enterprise)

**Value Proposition**: "Enterprise-grade security, advanced analytics, and dedicated support"

---

## Implementation Roadmap

### Phase 1: Coalition-Enhanced Free Tier (P0)

**Goal**: Enable minimal sentence-level embeddings for coalition members

**Tasks**:
1. ✅ Fix Starter tier re-signing (unique document_id) - **DONE**
2. Add coalition check to signing logic
3. Implement minimal embedding flag in Enterprise API
4. Update plugin to use `/sign/advanced` for coalition members
5. Add coalition benefits messaging in plugin UI

**Timeline**: 1 week  
**Impact**: Immediate increase in coalition content value

### Phase 2: Minimal Embeddings for Advanced Users (P1)

**Goal**: Add embedding level selector for Pro/Enterprise users

**Tasks**:
1. Add `embedding_level` setting to plugin
2. Update payload construction logic
3. Add UI for embedding level selection
4. Document performance differences
5. Add cost calculator (show savings with minimal)

**Timeline**: 1 week  
**Impact**: Reduced infrastructure costs, faster signing

### Phase 3: Toggleable Advanced Options (P2)

**Goal**: Granular control over signing features

**Tasks**:
1. Add advanced options section to settings
2. Implement per-post override meta box
3. Add presets (minimal/standard/full)
4. Add tooltips explaining each option
5. Add cost/performance indicators

**Timeline**: 2 weeks  
**Impact**: Better UX for power users, clearer value tiers

---

## Success Metrics

### Coalition Metrics

- **Free tier coalition adoption**: Target 80%+ (vs current 100% required)
- **Content value per free user**: +50% (sentence-level vs document-level)
- **AI licensing revenue**: +30% (higher quality content pool)
- **Upgrade rate**: +20% (clearer value proposition)

### Performance Metrics

- **Signing speed (minimal embeddings)**: -40% processing time
- **Storage costs (minimal embeddings)**: -60% per document
- **Infrastructure costs**: -25% overall (less unnecessary indexing)

### User Experience Metrics

- **Advanced user satisfaction**: +30% (more control)
- **Support tickets (performance)**: -50% (faster signing)
- **Feature discovery**: +40% (clearer settings)

---

## Risks & Mitigation

### Risk 1: Increased Free Tier Costs

**Risk**: Sentence-level embeddings for all coalition members increases infrastructure costs

**Mitigation**:
- Rate limit free tier (100 signs/month)
- Minimal embeddings only (no full indexing)
- Coalition-only feature (opt-in required)
- Monitor costs and adjust limits

### Risk 2: User Confusion

**Risk**: Too many options confuse users

**Mitigation**:
- Smart defaults (minimal for Pro, standard for Enterprise)
- Presets (minimal/standard/full)
- Clear tooltips and documentation
- In-app guidance and recommendations

### Risk 3: Coalition Opt-Out

**Risk**: Making coalition optional for free tier reduces participation

**Mitigation**:
- Keep coalition required for free tier
- Sentence-level embeddings as coalition benefit (not opt-in)
- Clear messaging: "Coalition members get better attribution"

---

## Conclusion

**Recommended Approach**:

1. **Enable minimal sentence-level embeddings for free tier coalition members** ✅
   - Increases content value for AI licensing
   - Strengthens coalition offering
   - Clear upgrade path to full embeddings

2. **Default to minimal embeddings for Pro/Enterprise users** ✅
   - Reduces overhead and costs
   - Faster signing performance
   - Better user experience

3. **Add toggleable advanced options** ✅
   - Granular control for power users
   - Clearer value tiers
   - Better cost optimization

**Next Steps**:
1. Review and approve strategy
2. Implement Phase 1 (coalition-enhanced free tier)
3. Test performance and cost impact
4. Roll out Phase 2 and 3 based on results

---

**Prepared by**: TEAM_148  
**Date**: 2026-02-03  
**Status**: Awaiting approval
