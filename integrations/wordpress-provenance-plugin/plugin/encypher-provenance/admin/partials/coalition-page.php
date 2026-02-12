<?php
/**
 * Coalition Full Page Template
 * Displays detailed coalition dashboard
 *
 * @var array|null $stats Coalition statistics from API
 * @var string $tier User's current tier (free, enterprise, strategic_partner)
 */

if (! defined('ABSPATH')) {
    exit;
}
?>

<div class="wrap encypher-coalition-page">
    <!-- Page Header -->
    <div class="coalition-page-header">
        <h1><?php esc_html_e('Coalition Dashboard', 'encypher-provenance'); ?></h1>
        <p><?php esc_html_e('Track your coalition membership and content contribution.', 'encypher-provenance'); ?></p>
    </div>

    <?php if ($stats): ?>
        
        <!-- Stats Overview -->
        <div class="coalition-revenue-section">
            <h2><?php esc_html_e('Your Coalition Stats', 'encypher-provenance'); ?></h2>
            
            <div class="coalition-stat-grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 24px;">
                <div class="stat-item">
                    <span class="stat-label"><?php esc_html_e('Signed Posts', 'encypher-provenance'); ?></span>
                    <span class="stat-value"><?php echo esc_html(number_format($stats['content_stats']['total_documents'] ?? 0)); ?></span>
                </div>
                <div class="stat-item">
                    <span class="stat-label"><?php esc_html_e('Total Words', 'encypher-provenance'); ?></span>
                    <span class="stat-value"><?php echo esc_html(number_format($stats['content_stats']['total_word_count'] ?? 0)); ?></span>
                </div>
                <div class="stat-item">
                    <span class="stat-label"><?php esc_html_e('Verifications', 'encypher-provenance'); ?></span>
                    <span class="stat-value"><?php echo esc_html(number_format($stats['content_stats']['verification_count'] ?? 0)); ?></span>
                </div>
                <div class="stat-item">
                    <span class="stat-label"><?php esc_html_e('Last Signed', 'encypher-provenance'); ?></span>
                    <span class="stat-value" style="font-size: 14px;">
                        <?php
                        $last_signed = $stats['content_stats']['last_signed'] ?? null;
                        echo $last_signed ? esc_html(human_time_diff(strtotime($last_signed), current_time('timestamp')) . ' ago') : esc_html__('Never', 'encypher-provenance');
                        ?>
                    </span>
                </div>
            </div>
        </div>

        <!-- Coalition Overview -->
        <div class="coalition-revenue-section">
            <h2><?php esc_html_e('Coalition Overview', 'encypher-provenance'); ?></h2>
            <div class="coalition-stat-grid" style="grid-template-columns: repeat(3, 1fr);">
                <div class="stat-item">
                    <span class="stat-label"><?php esc_html_e('Total Members', 'encypher-provenance'); ?></span>
                    <span class="stat-value"><?php echo esc_html(number_format($stats['coalition_stats']['total_members'] ?? 0)); ?></span>
                </div>
                <div class="stat-item">
                    <span class="stat-label"><?php esc_html_e('Content Pool', 'encypher-provenance'); ?></span>
                    <span class="stat-value"><?php echo esc_html(number_format($stats['coalition_stats']['total_content_pool'] ?? 0)); ?></span>
                </div>
                <div class="stat-item">
                    <span class="stat-label"><?php esc_html_e('Active Agreements', 'encypher-provenance'); ?></span>
                    <span class="stat-value"><?php echo esc_html(number_format($stats['coalition_stats']['active_agreements'] ?? 0)); ?></span>
                </div>
            </div>

            <div class="coalition-info" style="margin-top: 16px;">
                <p>
                    <?php esc_html_e('The coalition pools content from all members to license in bulk to AI companies for training data.', 'encypher-provenance'); ?>
                </p>
                <p>
                    <a href="https://encypherai.com/coalition" target="_blank"><?php esc_html_e('Learn more about how the coalition works →', 'encypher-provenance'); ?></a>
                </p>
            </div>
        </div>

    <?php else: ?>
        
        <!-- Error State -->
        <div class="coalition-revenue-section">
            <div class="encypher-coalition-error">
                <p>
                    <span class="dashicons dashicons-warning"></span>
                    <?php esc_html_e('Unable to load coalition stats. Please check your API connection.', 'encypher-provenance'); ?>
                </p>
                <a href="<?php echo esc_url(admin_url('admin.php?page=encypher-provenance')); ?>" class="button button-primary">
                    <?php esc_html_e('Check Settings', 'encypher-provenance'); ?>
                </a>
            </div>
        </div>

    <?php endif; ?>
</div>
