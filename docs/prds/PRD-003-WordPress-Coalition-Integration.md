# PRD-003: WordPress Plugin Coalition Integration

**Status**: ✅ Implemented  
**Priority**: P1 (High)  
**Estimated Effort**: 1-2 weeks  
**Owner**: WordPress Team  
**Created**: 2025-01-04  
**Updated**: 2025-11-04  
**Depends On**: PRD-001 (Coalition Infrastructure)

---

## Executive Summary

Integrate coalition features into the WordPress plugin so small publishers can view their coalition stats, revenue, and membership status directly from their WordPress admin dashboard.

---

## Problem Statement

### Current State
- WordPress plugin only handles signing/verification
- No visibility into coalition membership or revenue
- Users must visit separate dashboard to see coalition stats
- Missing key value proposition for small publishers

### Desired State
- Coalition stats widget in WordPress admin
- Revenue tracking panel showing earnings
- One-click access to detailed coalition dashboard
- Seamless integration with existing plugin features

---

## User Stories

### Story 1: Sarah (Small Publisher) - View Coalition Stats
**As a** WordPress user with the Encypher plugin  
**I want to** see my coalition stats in my WordPress dashboard  
**So that** I don't need to visit a separate website

**Acceptance Criteria:**
- [x] Coalition widget on WordPress admin dashboard
- [x] Display: signed posts, verifications, revenue earned
- [x] Link to full coalition dashboard
- [x] Auto-refresh stats every hour (1-hour transient cache)

---

## Technical Implementation

### New PHP Classes

```php
// includes/class-encypher-provenance-coalition.php
class Encypher_Provenance_Coalition {
    public function __construct() {
        add_action('wp_dashboard_setup', [$this, 'add_coalition_widget']);
        add_action('admin_menu', [$this, 'add_coalition_page']);
    }
    
    public function add_coalition_widget() {
        wp_add_dashboard_widget(
            'encypher_coalition_widget',
            'Encypher Coalition Stats',
            [$this, 'render_coalition_widget']
        );
    }
    
    public function render_coalition_widget() {
        $stats = $this->get_coalition_stats();
        include plugin_dir_path(__FILE__) . '../admin/partials/coalition-widget.php';
    }
    
    public function get_coalition_stats() {
        $api_base = get_option('encypher_api_base_url');
        $api_key = get_option('encypher_api_key');
        
        $response = wp_remote_get(
            $api_base . '/coalition/stats',
            [
                'headers' => [
                    'Authorization' => 'Bearer ' . $api_key,
                    'Content-Type' => 'application/json'
                ],
                'timeout' => 15
            ]
        );
        
        if (is_wp_error($response)) {
            return null;
        }
        
        $body = json_decode(wp_remote_retrieve_body($response), true);
        return $body['data'] ?? null;
    }
}
```

### Widget Template

```php
// admin/partials/coalition-widget.php
<?php if ($stats): ?>
<div class="encypher-coalition-stats">
    <div class="coalition-stat-grid">
        <div class="stat-item">
            <span class="stat-label">Signed Posts</span>
            <span class="stat-value"><?php echo esc_html($stats['content_stats']['total_documents']); ?></span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Verifications</span>
            <span class="stat-value"><?php echo esc_html($stats['content_stats']['verification_count']); ?></span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Revenue Earned</span>
            <span class="stat-value">$<?php echo number_format($stats['revenue_stats']['total_earned'], 2); ?></span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Pending</span>
            <span class="stat-value">$<?php echo number_format($stats['revenue_stats']['pending'], 2); ?></span>
        </div>
    </div>
    
    <div class="coalition-info">
        <p>
            <strong>Coalition Members:</strong> <?php echo number_format($stats['coalition_stats']['total_members']); ?><br>
            <strong>Content Pool:</strong> <?php echo number_format($stats['coalition_stats']['total_content_pool']); ?> documents
        </p>
    </div>
    
    <a href="<?php echo admin_url('admin.php?page=encypher-coalition'); ?>" class="button button-primary">
        View Full Coalition Dashboard
    </a>
</div>
<?php else: ?>
<div class="encypher-coalition-error">
    <p>Unable to load coalition stats. Please check your API connection.</p>
</div>
<?php endif; ?>
```

### CSS Styling

```css
/* assets/css/coalition-widget.css */
.encypher-coalition-stats {
    padding: 12px;
}

.coalition-stat-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 16px;
}

.stat-item {
    background: #f0f0f1;
    padding: 12px;
    border-radius: 4px;
    text-align: center;
}

.stat-label {
    display: block;
    font-size: 11px;
    color: #646970;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.stat-value {
    display: block;
    font-size: 24px;
    font-weight: 600;
    color: #1d2327;
}

.coalition-info {
    background: #e7f5fe;
    padding: 12px;
    border-radius: 4px;
    margin-bottom: 12px;
    font-size: 13px;
}
```

---

## Settings Integration

Add coalition settings to existing settings page:

```php
// includes/class-encypher-provenance-admin.php

public function register_coalition_settings() {
    add_settings_section(
        'encypher_coalition_section',
        'Coalition Settings',
        [$this, 'render_coalition_section'],
        'encypher-provenance-settings'
    );
    
    add_settings_field(
        'encypher_coalition_enabled',
        'Coalition Membership',
        [$this, 'render_coalition_enabled_field'],
        'encypher-provenance-settings',
        'encypher_coalition_section'
    );
}

public function render_coalition_enabled_field() {
    $enabled = get_option('encypher_coalition_enabled', true);
    ?>
    <label>
        <input type="checkbox" name="encypher_coalition_enabled" value="1" <?php checked($enabled, true); ?>>
        Participate in Encypher Coalition (Required for free tier)
    </label>
    <p class="description">
        Coalition membership allows you to earn revenue from AI company licensing deals.
        <a href="https://encypherai.com/coalition" target="_blank">Learn more</a>
    </p>
    <?php
}
```

---

## Rollout Plan

### Week 1: Core Integration ✅ COMPLETE
- [x] Create coalition PHP class
- [x] Implement API integration
- [x] Build dashboard widget
- [x] Add CSS styling

### Week 2: Polish & Testing ✅ COMPLETE
- [x] Add coalition settings page (integrated into existing settings)
- [x] Error handling and fallbacks
- [x] Coalition settings section in admin
- [x] Tier-specific coalition messaging
- [ ] Testing with real API (pending backend endpoint - PRD-001)
- [ ] Documentation updates (pending testing)

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Widget load time | <2s |
| API call success rate | >99% |
| User engagement | 50% view coalition stats weekly |
| Support tickets | <5 coalition-related tickets/month |

---

## Related PRDs
- **PRD-001**: Coalition Infrastructure
- **PRD-002**: Licensing Agreement Management
- **PRD-MASTER**: Coalition Roadmap

---

## Implementation Notes (2025-11-04)

### ✅ Completed Features

1. **Coalition Class** (`class-encypher-provenance-coalition.php`)
   - API integration for coalition stats
   - Revenue split calculations (tiered: 65/35, 70/30, 75/25)
   - Pro upgrade ROI calculator
   - Caching with 1-hour transients

2. **Dashboard Widget** (`admin/partials/coalition-widget.php`)
   - Stats grid (signed posts, verifications, revenue, pending)
   - Revenue split display with tier badge
   - Pro upgrade CTA with ROI calculation
   - Error handling and fallback states

3. **Full Coalition Page** (`admin/partials/coalition-page.php`)
   - Detailed stats overview
   - Revenue breakdown
   - Coalition overview
   - Pro tier comparison and upgrade section

4. **Styling** (`assets/css/coalition-widget.css`)
   - Responsive grid layout
   - Tier-specific badge colors
   - Pro upgrade CTA with gradient
   - Mobile-friendly design

5. **Plugin Integration**
   - Updated main plugin class to instantiate Coalition
   - Registered hooks in boot sequence
   - Added coalition submenu page

6. **Admin Settings Integration** (`class-encypher-provenance-admin.php`)
   - Added coalition settings section
   - Tier-specific coalition status display
   - Free tier: Always enabled with 65/35 split, $50 threshold
   - Pro tier: Optional with 70/30 split, $10 threshold
   - Enterprise tier: Optional with 75/25 split, no threshold
   - Links to coalition dashboard and learn more

### Revenue Model Updates

**Implemented Tiered Revenue Splits:**
- **Free Tier**: 65/35 split (65% to publishers, 35% to Encypher)
  - $50 minimum payout threshold
- **Pro Tier**: 70/30 split (70% to publishers, 30% to Encypher)
  - $10 minimum payout threshold
  - Priority content placement
  - Advanced analytics
- **Enterprise Tier**: 75/25 split (75% to publishers, 25% to Encypher)
  - No minimum payout (monthly automatic)
  - Custom licensing deals

**Key Features:**
- Real-time ROI calculator shows Pro upgrade value
- Displays break-even point for Pro tier
- Shows monthly gain based on current earnings
- Encourages upgrade when profitable

### Testing Checklist

- [ ] Widget displays correctly on dashboard
- [ ] API connection works with valid API key
- [ ] Stats refresh every hour (transient cache)
- [ ] Pro upgrade CTA shows correct calculations
- [ ] Full coalition page loads without errors
- [ ] CSS styling works on mobile devices
- [ ] Error states display properly
- [ ] Tier badges show correct colors

### Next Steps

1. **Backend API**: Implement `/api/v1/coalition/stats` endpoint (PRD-001)
2. **Testing**: Test with real coalition data
3. **Documentation**: Update WordPress plugin README
4. **Localization**: Add translation strings for i18n
