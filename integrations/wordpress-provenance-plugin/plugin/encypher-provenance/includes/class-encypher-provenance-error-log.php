<?php
namespace EncypherProvenance;

if (! defined('ABSPATH')) {
    exit;
}

/**
 * Persistent error log ring buffer for Encypher signing/verification failures.
 *
 * Stores up to MAX_ENTRIES entries in wp_options. All tiers can read the last
 * DISPLAY_FREE entries. Enterprise/strategic_partner tiers see the full buffer
 * and can export as CSV.
 *
 * Each entry:
 *   - timestamp  (ISO 8601 UTC)
 *   - post_id    (int, 0 for site-level errors)
 *   - post_title (string)
 *   - error_code (string)
 *   - error_message (string)
 *   - context    ('auto_sign' | 'manual_sign' | 'verify' | 'connection')
 *   - consecutive_failures (int) — count of unbroken failures for this post
 */
class ErrorLog
{
    const OPTION_KEY       = 'encypher_error_log';
    const MAX_ENTRIES      = 50;
    const DISPLAY_FREE     = 10;
    const CONSECUTIVE_META = '_encypher_consecutive_failures';

    /**
     * Record a signing or verification failure.
     *
     * @param int    $post_id
     * @param string $error_code
     * @param string $error_message
     * @param string $context  'auto_sign' | 'manual_sign' | 'verify' | 'connection'
     */
    public static function record_failure(int $post_id, string $error_code, string $error_message, string $context = 'auto_sign'): void
    {
        $consecutive = 0;
        if ($post_id > 0) {
            $consecutive = (int) get_post_meta($post_id, self::CONSECUTIVE_META, true);
            $consecutive++;
            update_post_meta($post_id, self::CONSECUTIVE_META, $consecutive);
            update_post_meta($post_id, '_encypher_last_sign_error', [
                'timestamp'   => gmdate('c'),
                'error_code'  => sanitize_text_field($error_code),
                'message'     => sanitize_text_field($error_message),
                'context'     => sanitize_text_field($context),
                'consecutive' => $consecutive,
            ]);
        }

        $post_title = $post_id > 0 ? (get_the_title($post_id) ?: sprintf('Post #%d', $post_id)) : '';

        $entry = [
            'timestamp'           => gmdate('c'),
            'post_id'             => $post_id,
            'post_title'          => sanitize_text_field($post_title),
            'error_code'          => sanitize_text_field($error_code),
            'error_message'       => sanitize_text_field($error_message),
            'context'             => sanitize_text_field($context),
            'consecutive_failures' => $consecutive,
        ];

        $log = self::get_raw_log();
        array_unshift($log, $entry);
        if (count($log) > self::MAX_ENTRIES) {
            $log = array_slice($log, 0, self::MAX_ENTRIES);
        }
        update_option(self::OPTION_KEY, $log, false);
    }

    /**
     * Clear the failure streak for a post after a successful sign.
     */
    public static function record_success(int $post_id): void
    {
        if ($post_id > 0) {
            delete_post_meta($post_id, self::CONSECUTIVE_META);
            delete_post_meta($post_id, '_encypher_last_sign_error');
        }
    }

    /**
     * Return the full raw log array (up to MAX_ENTRIES).
     *
     * @return array<int, array<string, mixed>>
     */
    public static function get_raw_log(): array
    {
        $log = get_option(self::OPTION_KEY, []);
        return is_array($log) ? $log : [];
    }

    /**
     * Return entries visible to the current tier.
     *
     * @param string $tier  'free' | 'enterprise' | 'strategic_partner'
     * @return array<int, array<string, mixed>>
     */
    public static function get_log_for_tier(string $tier): array
    {
        $log = self::get_raw_log();
        if (in_array($tier, ['enterprise', 'strategic_partner'], true)) {
            return $log;
        }
        return array_slice($log, 0, self::DISPLAY_FREE);
    }

    /**
     * Clear the entire log (admin action).
     */
    public static function clear(): void
    {
        update_option(self::OPTION_KEY, [], false);
    }

    /**
     * Return the consecutive failure count for a post.
     */
    public static function get_consecutive_failures(int $post_id): int
    {
        return $post_id > 0 ? (int) get_post_meta($post_id, self::CONSECUTIVE_META, true) : 0;
    }

    /**
     * Fire a webhook if the post has hit the consecutive-failure threshold.
     * Only fires when a webhook URL is configured (enterprise add-on).
     *
     * @param int    $post_id
     * @param array  $last_entry  The most recent log entry for context
     * @param int    $threshold   Number of consecutive failures before firing
     */
    public static function maybe_fire_webhook(int $post_id, array $last_entry, int $threshold = 3): void
    {
        $settings = get_option('encypher_provenance_settings', []);
        $webhook_url = isset($settings['error_webhook_url']) ? trim((string) $settings['error_webhook_url']) : '';
        if ('' === $webhook_url) {
            return;
        }

        $consecutive = $last_entry['consecutive_failures'] ?? 0;
        if ($consecutive < $threshold || ($consecutive % $threshold !== 0)) {
            return;
        }

        $site_name = get_bloginfo('name');
        $site_url  = get_bloginfo('url');

        $payload = [
            'event'       => 'encypher.sign_failure',
            'site_name'   => $site_name,
            'site_url'    => $site_url,
            'post_id'     => $post_id,
            'post_title'  => $last_entry['post_title'] ?? '',
            'post_url'    => $post_id > 0 ? get_permalink($post_id) : '',
            'error_code'  => $last_entry['error_code'] ?? '',
            'error_message' => $last_entry['error_message'] ?? '',
            'consecutive_failures' => $consecutive,
            'timestamp'   => $last_entry['timestamp'] ?? gmdate('c'),
        ];

        wp_remote_post($webhook_url, [
            'timeout'     => 10,
            'blocking'    => false,
            'headers'     => ['Content-Type' => 'application/json'],
            'body'        => wp_json_encode($payload),
        ]);
    }
}
