<?php
/**
 * Coalition Widget Template
 * Displays coalition stats on WordPress dashboard
 *
 * @var array|null $stats Coalition statistics from API
 * @var string $tier User's current tier (free, enterprise, strategic_partner)
 */

if (! defined('ABSPATH')) {
    exit;
}
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
    </div>

    <!-- Coalition Info -->
    <div class="coalition-info">
        <p class="coalition-members">
            <strong><?php esc_html_e('Coalition:', 'encypher-provenance'); ?></strong>
            <?php echo esc_html(number_format($stats['coalition_stats']['total_members'] ?? 0)); ?> <?php esc_html_e('members', 'encypher-provenance'); ?> •
            <?php echo esc_html(number_format($stats['coalition_stats']['total_content_pool'] ?? 0)); ?> <?php esc_html_e('documents', 'encypher-provenance'); ?>
        </p>
    </div>

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
