<?php
/**
 * Coalition Full Page Template
 * Displays detailed coalition dashboard
 *
 * @var array|null $stats Coalition statistics from API
 * @var string $tier User's current tier (free, pro, enterprise)
 */

if (! defined('ABSPATH')) {
    exit;
}

$revenue_split = $this->get_revenue_split($tier);
?>

<div class="wrap encypher-coalition-page">
    <!-- Page Header -->
    <div class="coalition-page-header">
        <h1><?php esc_html_e('Coalition Dashboard', 'encypher-provenance'); ?></h1>
        <p><?php esc_html_e('Track your coalition membership, content contribution, and revenue earnings.', 'encypher-provenance'); ?></p>
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

            <!-- Revenue Details -->
            <h3><?php esc_html_e('Revenue Breakdown', 'encypher-provenance'); ?></h3>
            <div class="coalition-stat-grid" style="grid-template-columns: repeat(3, 1fr);">
                <div class="stat-item">
                    <span class="stat-label"><?php esc_html_e('Total Earned', 'encypher-provenance'); ?></span>
                    <span class="stat-value">$<?php echo esc_html(number_format($stats['revenue_stats']['total_earned'] ?? 0, 2)); ?></span>
                </div>
                <div class="stat-item">
                    <span class="stat-label"><?php esc_html_e('Pending', 'encypher-provenance'); ?></span>
                    <span class="stat-value">$<?php echo esc_html(number_format($stats['revenue_stats']['pending'] ?? 0, 2)); ?></span>
                </div>
                <div class="stat-item">
                    <span class="stat-label"><?php esc_html_e('Paid Out', 'encypher-provenance'); ?></span>
                    <span class="stat-value">$<?php echo esc_html(number_format($stats['revenue_stats']['paid'] ?? 0, 2)); ?></span>
                </div>
            </div>

            <!-- Revenue Split Info -->
            <div class="coalition-info" style="margin-top: 16px;">
                <p>
                    <strong><?php esc_html_e('Your Revenue Split:', 'encypher-provenance'); ?></strong>
                    <?php echo esc_html($revenue_split['member_percent']); ?>% <?php esc_html_e('to you', 'encypher-provenance'); ?>,
                    <?php echo esc_html($revenue_split['encypher_percent']); ?>% <?php esc_html_e('to Encypher', 'encypher-provenance'); ?>
                    <span class="tier-badge tier-<?php echo esc_attr($tier); ?>"><?php echo esc_html(ucfirst($tier)); ?> <?php esc_html_e('Tier', 'encypher-provenance'); ?></span>
                </p>
                <p>
                    <strong><?php esc_html_e('Payout Threshold:', 'encypher-provenance'); ?></strong>
                    <?php if ($revenue_split['payout_threshold'] > 0): ?>
                        $<?php echo esc_html(number_format($revenue_split['payout_threshold'], 2)); ?>
                    <?php else: ?>
                        <?php esc_html_e('No minimum (monthly automatic payout)', 'encypher-provenance'); ?>
                    <?php endif; ?>
                </p>
                <?php if (isset($stats['revenue_stats']['next_payout_date'])): ?>
                <p>
                    <strong><?php esc_html_e('Next Payout:', 'encypher-provenance'); ?></strong>
                    <?php echo esc_html(date_i18n(get_option('date_format'), strtotime($stats['revenue_stats']['next_payout_date']))); ?>
                </p>
                <?php endif; ?>
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
                    <?php esc_html_e('The coalition pools content from all members to license in bulk to AI companies for training data. Revenue is distributed based on your content contribution to the pool.', 'encypher-provenance'); ?>
                </p>
                <p>
                    <a href="https://encypherai.com/coalition" target="_blank"><?php esc_html_e('Learn more about how the coalition works →', 'encypher-provenance'); ?></a>
                </p>
            </div>
        </div>

        <!-- Pro Upgrade Section (if free tier) -->
        <?php if ($tier === 'starter'): ?>
            <?php
            $pending = $stats['revenue_stats']['pending'] ?? 0;
            $roi = $this->calculate_pro_upgrade_roi($pending, $tier);
            ?>
            <div class="coalition-revenue-section">
                <h2><?php esc_html_e('Maximize Your Earnings', 'encypher-provenance'); ?></h2>
                
                <div class="coalition-upgrade-cta" style="margin: 0;">
                    <h4><?php esc_html_e('Upgrade to Pro Tier', 'encypher-provenance'); ?></h4>
                    <p>
                        <?php esc_html_e('Get a better revenue split, faster payouts, and priority content placement.', 'encypher-provenance'); ?>
                    </p>

                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin: 16px 0;">
                        <div>
                            <strong><?php esc_html_e('Free Tier (Current)', 'encypher-provenance'); ?></strong>
                            <ul class="upgrade-benefits">
                                <li>• 65/35 revenue split</li>
                                <li>• $50 payout threshold</li>
                                <li>• Standard placement</li>
                                <li>• Basic analytics</li>
                            </ul>
                        </div>
                        <div>
                            <strong><?php esc_html_e('Pro Tier', 'encypher-provenance'); ?></strong>
                            <ul class="upgrade-benefits">
                                <li>70/30 revenue split (+5%)</li>
                                <li>$10 payout threshold</li>
                                <li>Priority placement</li>
                                <li>Advanced analytics</li>
                            </ul>
                        </div>
                    </div>

                    <?php if ($roi['show_upgrade'] && $pending > 0): ?>
                    <div style="background: rgba(255,255,255,0.2); padding: 12px; border-radius: 4px; margin: 16px 0;">
                        <p style="margin: 0; font-size: 14px;">
                            <strong><?php esc_html_e('Based on your current earnings:', 'encypher-provenance'); ?></strong><br>
                            <?php
                            printf(
                                esc_html__('You would earn $%s more per month with Pro tier.', 'encypher-provenance'),
                                number_format($roi['monthly_gain'], 2)
                            );
                            ?>
                            <?php if ($roi['is_profitable']): ?>
                                <br><strong><?php printf(esc_html__('Net benefit: $%s/month after plan cost!', 'encypher-provenance'), number_format($roi['net_benefit'], 2)); ?></strong>
                            <?php else: ?>
                                <br><?php printf(esc_html__('Pro becomes profitable at $%s/month in coalition earnings.', 'encypher-provenance'), number_format($roi['break_even_earnings'], 2)); ?>
                            <?php endif; ?>
                        </p>
                    </div>
                    <?php endif; ?>

                    <a href="https://encypherai.com/pricing" class="button button-primary" target="_blank">
                        <?php esc_html_e('Upgrade to Pro - $99/month', 'encypher-provenance'); ?>
                    </a>
                </div>
            </div>
        <?php endif; ?>

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
