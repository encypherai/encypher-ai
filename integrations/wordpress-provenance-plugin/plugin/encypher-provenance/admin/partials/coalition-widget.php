<?php
/**
 * Coalition Widget Template
 * Displays coalition stats on WordPress dashboard
 *
 * @var array|null $stats Coalition statistics from API
 * @var string $tier User's current tier (free, pro, enterprise)
 */

if (! defined('ABSPATH')) {
    exit;
}

$revenue_split = $this->get_revenue_split($tier);
?>

<?php if ($stats): ?>
<div class="encypher-coalition-stats">
    <!-- Stats Grid -->
    <div class="coalition-stat-grid">
        <div class="stat-item">
            <span class="stat-label"><?php esc_html_e('Signed Posts', 'encypher-provenance'); ?></span>
            <span class="stat-value"><?php echo esc_html(number_format($stats['content_stats']['total_documents'] ?? 0)); ?></span>
        </div>
        <div class="stat-item">
            <span class="stat-label"><?php esc_html_e('Verifications', 'encypher-provenance'); ?></span>
            <span class="stat-value"><?php echo esc_html(number_format($stats['content_stats']['verification_count'] ?? 0)); ?></span>
        </div>
        <div class="stat-item">
            <span class="stat-label"><?php esc_html_e('Revenue Earned', 'encypher-provenance'); ?></span>
            <span class="stat-value">$<?php echo esc_html(number_format($stats['revenue_stats']['total_earned'] ?? 0, 2)); ?></span>
        </div>
        <div class="stat-item">
            <span class="stat-label"><?php esc_html_e('Pending', 'encypher-provenance'); ?></span>
            <span class="stat-value">$<?php echo esc_html(number_format($stats['revenue_stats']['pending'] ?? 0, 2)); ?></span>
        </div>
    </div>

    <!-- Revenue Split Info -->
    <div class="coalition-info">
        <p>
            <strong><?php esc_html_e('Your Revenue Split:', 'encypher-provenance'); ?></strong>
            <?php echo esc_html($revenue_split['member_percent']); ?>% <?php esc_html_e('to you', 'encypher-provenance'); ?>,
            <?php echo esc_html($revenue_split['encypher_percent']); ?>% <?php esc_html_e('to Encypher', 'encypher-provenance'); ?>
            <span class="tier-badge tier-<?php echo esc_attr($tier); ?>"><?php echo esc_html(ucfirst($tier)); ?> <?php esc_html_e('Tier', 'encypher-provenance'); ?></span>
        </p>
        <p class="coalition-members">
            <strong><?php esc_html_e('Coalition:', 'encypher-provenance'); ?></strong>
            <?php echo esc_html(number_format($stats['coalition_stats']['total_members'] ?? 0)); ?> <?php esc_html_e('members', 'encypher-provenance'); ?> •
            <?php echo esc_html(number_format($stats['coalition_stats']['total_content_pool'] ?? 0)); ?> <?php esc_html_e('documents', 'encypher-provenance'); ?>
        </p>
    </div>

    <!-- Pro Upgrade CTA (if free tier) -->
    <?php if ($tier === 'starter' && isset($stats['revenue_stats']['pending'])): ?>
        <?php
        $pending = $stats['revenue_stats']['pending'] ?? 0;
        $roi = $this->calculate_pro_upgrade_roi($pending, $tier);
        ?>
        <?php if ($roi['show_upgrade'] && $pending > 50): ?>
        <div class="coalition-upgrade-cta">
            <h4><?php esc_html_e('Upgrade to Pro', 'encypher-provenance'); ?></h4>
            <p>
                <?php
                printf(
                    esc_html__('With Pro tier (70/30 split), you would earn $%s more this month!', 'encypher-provenance'),
                    number_format($roi['monthly_gain'], 2)
                );
                ?>
            </p>
            <ul class="upgrade-benefits">
                <li><?php esc_html_e('70/30 revenue split (vs 65/35)', 'encypher-provenance'); ?></li>
                <li><?php esc_html_e('$10 payout threshold (vs $50)', 'encypher-provenance'); ?></li>
                <li><?php esc_html_e('Priority content placement', 'encypher-provenance'); ?></li>
                <li><?php esc_html_e('Advanced analytics', 'encypher-provenance'); ?></li>
            </ul>
            <a href="https://encypherai.com/pricing" class="button button-primary" target="_blank">
                <?php esc_html_e('Upgrade to Pro - $99/month', 'encypher-provenance'); ?>
            </a>
        </div>
        <?php endif; ?>
    <?php endif; ?>

    <!-- Action Buttons -->
    <div class="coalition-actions">
        <a href="<?php echo esc_url(admin_url('admin.php?page=encypher-coalition')); ?>" class="button button-secondary">
            <?php esc_html_e('View Full Dashboard', 'encypher-provenance'); ?>
        </a>
        <a href="https://encypherai.com/coalition" class="button button-link" target="_blank">
            <?php esc_html_e('Learn About Coalition', 'encypher-provenance'); ?>
        </a>
    </div>
</div>

<?php else: ?>
<div class="encypher-coalition-error">
    <p>
        <span class="dashicons dashicons-warning"></span>
        <?php esc_html_e('Unable to load coalition stats. Please check your API connection.', 'encypher-provenance'); ?>
    </p>
    <a href="<?php echo esc_url(admin_url('admin.php?page=encypher-provenance')); ?>" class="button button-small">
        <?php esc_html_e('Check Settings', 'encypher-provenance'); ?>
    </a>
</div>
<?php endif; ?>
