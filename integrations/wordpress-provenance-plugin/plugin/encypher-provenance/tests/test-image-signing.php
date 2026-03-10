<?php
/**
 * Tests for CDN image provenance signing on publish (Phase 2).
 *
 * These are standalone PHP unit tests with no framework dependency.
 * Run directly: php tests/test-image-signing.php
 *
 * Covered behaviours
 * ------------------
 * 1. sign_featured_image — returns early (no HTTP call) when the post has no
 *    featured image thumbnail.
 * 2. sign_featured_image — returns early when the attached file does not exist
 *    on disk (attachment meta present but file missing).
 * 3. sign_featured_image — returns early for unsupported MIME types (e.g.
 *    image/gif).
 * 4. sign_featured_image — on a successful 201 response stores record_id and
 *    manifest_url in post meta for the post AND the attachment.
 * 5. sign_featured_image — on a non-200/201 HTTP status does NOT write post
 *    meta.
 * 6. inject_image_provenance_header — emits "C2PA-Manifest-URL: <url>" header
 *    when manifest_url meta is present.
 * 7. inject_image_provenance_header — emits no header when manifest_url meta
 *    is absent.
 * 8. get_image_record_id — returns the stored record ID string.
 * 9. get_image_manifest_url — returns the stored manifest URL string.
 */

declare(strict_types=1);

// ---------------------------------------------------------------------------
// Minimal WordPress stubs so the class can be loaded without a WP bootstrap.
// ---------------------------------------------------------------------------

if (!defined('ABSPATH')) {
    define('ABSPATH', '/tmp/');
}
if (!defined('ENCYPHER_PROVENANCE_VERSION')) {
    define('ENCYPHER_PROVENANCE_VERSION', '0.0.0-test');
}

// --- Post meta store (per-post, per-key) ------------------------------------
$_post_meta_store = [];

function update_post_meta(int $post_id, string $key, $value): void
{
    global $_post_meta_store;
    $_post_meta_store[$post_id][$key] = $value;
}

function get_post_meta(int $post_id, string $key, bool $single = false)
{
    global $_post_meta_store;
    $v = $_post_meta_store[$post_id][$key] ?? '';
    return $single ? $v : [$v];
}

function delete_post_meta(int $post_id, string $key): void
{
    global $_post_meta_store;
    unset($_post_meta_store[$post_id][$key]);
}

// --- WordPress option store --------------------------------------------------
$_option_store = [];

function get_option(string $option, $default = false)
{
    global $_option_store;
    return $_option_store[$option] ?? $default;
}

function update_option(string $option, $value): void
{
    global $_option_store;
    $_option_store[$option] = $value;
}

// --- Minimal WP helpers used by the class ------------------------------------

function sanitize_text_field(string $v): string  { return trim(strip_tags($v)); }
function esc_url_raw(string $v): string           { return $v; }
function esc_url(string $v): string               { return htmlspecialchars($v, ENT_QUOTES); }
function wp_generate_password(int $length, bool $special_chars = true): string
{
    return substr(str_repeat('abcdefghijklmnopqrstuvwxyz0123456789', 2), 0, $length);
}
function get_the_title(int $post_id): string      { return "Test Post {$post_id}"; }
function wp_get_attachment_url(int $id)           { return "https://example.com/wp-content/uploads/photo.jpg"; }
function get_post_mime_type(int $id): string
{
    global $_attachment_mime;
    return $_attachment_mime[$id] ?? 'image/jpeg';
}
function get_attached_file(int $id)
{
    global $_attachment_file;
    return $_attachment_file[$id] ?? false;
}
function get_post_thumbnail_id(int $post_id)
{
    global $_thumbnail_id;
    return $_thumbnail_id[$post_id] ?? false;
}
function is_wp_error($thing): bool { return $thing instanceof WP_Error; }
function wp_remote_retrieve_response_code($response): int
{
    return is_array($response) ? ($response['response']['code'] ?? 0) : 0;
}
function wp_remote_retrieve_body($response): string
{
    return is_array($response) ? ($response['body'] ?? '') : '';
}
function is_singular(): bool
{
    global $_is_singular;
    return $_is_singular ?? false;
}
function get_the_ID()
{
    global $_current_post_id;
    return $_current_post_id ?? false;
}
function header(string $header): void
{
    global $_sent_headers;
    $_sent_headers[] = $header;
}

// wp_remote_post is overridable via global
$_wp_remote_post_mock = null;
function wp_remote_post(string $url, array $args = [])
{
    global $_wp_remote_post_mock;
    return is_callable($_wp_remote_post_mock) ? ($_wp_remote_post_mock)($url, $args) : [];
}

// Stub WP_Error
class WP_Error
{
    public string $code;
    public string $message;
    public function __construct(string $code = '', string $message = '') {
        $this->code    = $code;
        $this->message = $message;
    }
    public function get_error_message(): string { return $this->message; }
    public function get_error_code(): string    { return $this->code; }
}

// Stubs for other classes referenced by Rest
namespace EncypherProvenance {
    class HtmlParser {
        public function extract_text(string $html): string { return strip_tags($html); }
    }
    class Plugin {
        public static function get_verify_slug(): string { return 'verify'; }
    }
    class ErrorLog {
        public static function record_success(int $post_id): void {}
        public static function record_failure(int $post_id, string $code, string $msg, string $ctx): void {}
        public static function get_consecutive_failures(int $post_id): int { return 0; }
        public static function maybe_fire_webhook(int $post_id, array $data): void {}
    }
}

namespace {

// ---------------------------------------------------------------------------
// Load the class under test
// ---------------------------------------------------------------------------
require_once __DIR__ . '/../includes/class-encypher-provenance-rest.php';

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

$passed = 0;
$failed = 0;

function assert_true(bool $condition, string $message): void
{
    global $passed, $failed;
    if ($condition) {
        echo "  PASS: {$message}\n";
        $passed++;
    } else {
        echo "  FAIL: {$message}\n";
        $failed++;
    }
}

function assert_equals($expected, $actual, string $message): void
{
    assert_true($expected === $actual, $message . " (expected " . var_export($expected, true) . ", got " . var_export($actual, true) . ")");
}

function reset_globals(): void
{
    global $_post_meta_store, $_option_store, $_attachment_mime, $_attachment_file,
           $_thumbnail_id, $_wp_remote_post_mock, $_sent_headers,
           $_is_singular, $_current_post_id;
    $_post_meta_store      = [];
    $_option_store         = [];
    $_attachment_mime      = [];
    $_attachment_file      = [];
    $_thumbnail_id         = [];
    $_wp_remote_post_mock  = null;
    $_sent_headers         = [];
    $_is_singular          = false;
    $_current_post_id      = false;
}

// Create a testable subclass that exposes the private method
class TestableRest extends \EncypherProvenance\Rest
{
    public function call_sign_featured_image(int $post_id): void
    {
        // Use Reflection to invoke the private method
        $ref = new ReflectionMethod(parent::class, 'sign_featured_image');
        $ref->setAccessible(true);
        $ref->invoke($this, $post_id);
    }
}

// ---------------------------------------------------------------------------
// Test 1: returns early when no featured image
// ---------------------------------------------------------------------------
echo "\nTest 1: sign_featured_image returns early when post has no featured image\n";
reset_globals();

$rest = new TestableRest();
$rest->call_sign_featured_image(42);

assert_true(
    empty($GLOBALS['_post_meta_store'][42] ?? []),
    'No post meta written when thumbnail is missing'
);

// ---------------------------------------------------------------------------
// Test 2: returns early when attached file does not exist on disk
// ---------------------------------------------------------------------------
echo "\nTest 2: sign_featured_image returns early when image file is missing on disk\n";
reset_globals();

$GLOBALS['_thumbnail_id'][99]     = 7;
$GLOBALS['_attachment_file'][7]   = '/tmp/nonexistent_encypher_test_image_xyz.jpg';
$GLOBALS['_attachment_mime'][7]   = 'image/jpeg';

$rest = new TestableRest();
$rest->call_sign_featured_image(99);

assert_true(
    !isset($GLOBALS['_post_meta_store'][99]['_encypher_image_record_id']),
    'No record_id written when file is missing on disk'
);

// ---------------------------------------------------------------------------
// Test 3: returns early for unsupported MIME type
// ---------------------------------------------------------------------------
echo "\nTest 3: sign_featured_image returns early for unsupported mime type (image/gif)\n";
reset_globals();

// Create a real temp file so file_exists passes
$tmp_file = tempnam(sys_get_temp_dir(), 'encypher_test_');
file_put_contents($tmp_file, 'GIF89a');

$GLOBALS['_thumbnail_id'][55]   = 8;
$GLOBALS['_attachment_file'][8] = $tmp_file;
$GLOBALS['_attachment_mime'][8] = 'image/gif';

$http_called = false;
$GLOBALS['_wp_remote_post_mock'] = function () use (&$http_called) {
    $http_called = true;
    return [];
};

$rest = new TestableRest();
$rest->call_sign_featured_image(55);

assert_true(!$http_called, 'No HTTP call made for unsupported mime type');
assert_true(
    !isset($GLOBALS['_post_meta_store'][55]['_encypher_image_record_id']),
    'No post meta written for unsupported mime type'
);

unlink($tmp_file);

// ---------------------------------------------------------------------------
// Test 4: successful 201 response stores record_id and manifest_url
// ---------------------------------------------------------------------------
echo "\nTest 4: sign_featured_image stores record_id and manifest_url on success (HTTP 201)\n";
reset_globals();

$tmp_file = tempnam(sys_get_temp_dir(), 'encypher_test_');
file_put_contents($tmp_file, str_repeat("\xFF\xD8\xFF", 10)); // fake JPEG bytes

$GLOBALS['_thumbnail_id'][10]    = 20;
$GLOBALS['_attachment_file'][20] = $tmp_file;
$GLOBALS['_attachment_mime'][20] = 'image/jpeg';

$GLOBALS['_option_store']['encypher_provenance_settings'] = [
    'api_key' => 'test-key-abc', // pragma: allowlist secret
    'api_url' => 'https://enterprise.encypherai.com',
];

$GLOBALS['_wp_remote_post_mock'] = function (string $url, array $args) {
    return [
        'response' => ['code' => 201],
        'body'     => json_encode([
            'record_id'    => 'rec-00001',
            'manifest_url' => 'https://cdn.encypherai.com/manifests/rec-00001.json',
        ]),
    ];
};

$rest = new TestableRest();
$rest->call_sign_featured_image(10);

assert_equals(
    'rec-00001',
    $GLOBALS['_post_meta_store'][10]['_encypher_image_record_id'] ?? '',
    'record_id stored in post meta'
);
assert_equals(
    'https://cdn.encypherai.com/manifests/rec-00001.json',
    $GLOBALS['_post_meta_store'][10]['_encypher_image_manifest_url'] ?? '',
    'manifest_url stored in post meta'
);
assert_equals(
    'rec-00001',
    $GLOBALS['_post_meta_store'][20]['_encypher_image_record_id'] ?? '',
    'record_id also stored on the attachment'
);

unlink($tmp_file);

// ---------------------------------------------------------------------------
// Test 5: non-200/201 HTTP status does not write post meta
// ---------------------------------------------------------------------------
echo "\nTest 5: sign_featured_image does NOT write meta on non-2xx HTTP status\n";
reset_globals();

$tmp_file = tempnam(sys_get_temp_dir(), 'encypher_test_');
file_put_contents($tmp_file, 'fake-image-data');

$GLOBALS['_thumbnail_id'][30]    = 31;
$GLOBALS['_attachment_file'][31] = $tmp_file;
$GLOBALS['_attachment_mime'][31] = 'image/png';

$GLOBALS['_option_store']['encypher_provenance_settings'] = [
    'api_key' => 'key', // pragma: allowlist secret
    'api_url' => 'https://enterprise.encypherai.com',
];

$GLOBALS['_wp_remote_post_mock'] = function () {
    return [
        'response' => ['code' => 500],
        'body'     => json_encode(['error' => 'server error']),
    ];
};

$rest = new TestableRest();
$rest->call_sign_featured_image(30);

assert_true(
    !isset($GLOBALS['_post_meta_store'][30]['_encypher_image_record_id']),
    'No record_id stored on HTTP 500'
);

unlink($tmp_file);

// ---------------------------------------------------------------------------
// Test 6: inject_image_provenance_header emits header when manifest_url set
// ---------------------------------------------------------------------------
echo "\nTest 6: inject_image_provenance_header emits C2PA-Manifest-URL header\n";
reset_globals();

$GLOBALS['_is_singular']    = true;
$GLOBALS['_current_post_id'] = 77;
$GLOBALS['_post_meta_store'][77]['_encypher_image_manifest_url'] =
    'https://cdn.encypherai.com/manifests/rec-abc.json';

$rest = new TestableRest();
$rest->inject_image_provenance_header();

$found = false;
foreach ($GLOBALS['_sent_headers'] as $h) {
    if (strpos($h, 'C2PA-Manifest-URL:') === 0) {
        $found = true;
        break;
    }
}
assert_true($found, 'C2PA-Manifest-URL header emitted');

// ---------------------------------------------------------------------------
// Test 7: inject_image_provenance_header emits no header when meta absent
// ---------------------------------------------------------------------------
echo "\nTest 7: inject_image_provenance_header emits no header when manifest_url absent\n";
reset_globals();

$GLOBALS['_is_singular']     = true;
$GLOBALS['_current_post_id'] = 88;
// No manifest_url in post meta

$rest = new TestableRest();
$rest->inject_image_provenance_header();

$found = false;
foreach ($GLOBALS['_sent_headers'] as $h) {
    if (strpos($h, 'C2PA-Manifest-URL:') === 0) {
        $found = true;
        break;
    }
}
assert_true(!$found, 'No C2PA-Manifest-URL header when manifest_url absent');

// ---------------------------------------------------------------------------
// Test 8: get_image_record_id returns stored record ID
// ---------------------------------------------------------------------------
echo "\nTest 8: get_image_record_id returns stored record ID string\n";
reset_globals();

$GLOBALS['_post_meta_store'][5]['_encypher_image_record_id'] = 'rec-xyz-789';

$rest = new TestableRest();
assert_equals('rec-xyz-789', $rest->get_image_record_id(5), 'get_image_record_id returns correct value');

// ---------------------------------------------------------------------------
// Test 9: get_image_manifest_url returns stored manifest URL
// ---------------------------------------------------------------------------
echo "\nTest 9: get_image_manifest_url returns stored manifest URL\n";
reset_globals();

$GLOBALS['_post_meta_store'][6]['_encypher_image_manifest_url'] =
    'https://cdn.encypherai.com/manifests/rec-xyz-789.json';

$rest = new TestableRest();
assert_equals(
    'https://cdn.encypherai.com/manifests/rec-xyz-789.json',
    $rest->get_image_manifest_url(6),
    'get_image_manifest_url returns correct value'
);

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------
echo "\n---\n";
echo "Results: {$passed} passed, {$failed} failed\n";
exit($failed > 0 ? 1 : 0);

} // end namespace {}
