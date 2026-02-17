#!/usr/bin/env php
<?php
/**
 * Unit tests for HTML text extraction and embedding.
 *
 * Run inside the WordPress container:
 *   docker exec <wordpress-container> php \
 *     /var/www/html/wp-content/plugins/encypher-provenance/tests/test-html-text-extraction.php
 *
 * Or with WordPress bootstrapped:
 *   php -d auto_prepend_file=/var/www/html/wp-load.php tests/test-html-text-extraction.php
 *
 * These tests verify the extract_text_from_html(), embed_signed_text_in_html(),
 * and extract_html_text_fragments() methods work correctly with WordPress block
 * HTML content.
 */

// Bootstrap WordPress if not already loaded (needed for wp_strip_all_tags etc.)
if (!defined('ABSPATH')) {
    // Try to find wp-load.php
    $wp_load = '/var/www/html/wp-load.php';
    if (file_exists($wp_load)) {
        require_once $wp_load;
    } else {
        // Minimal stubs for standalone execution
        if (!function_exists('wp_strip_all_tags')) {
            function wp_strip_all_tags(string $text): string {
                return strip_tags($text);
            }
        }
        if (!defined('ABSPATH')) {
            define('ABSPATH', __DIR__ . '/../');
        }
    }
}

// Load the class under test
require_once __DIR__ . '/../includes/class-encypher-provenance-rest.php';

class HtmlTextExtractionTest
{
    private $rest;
    private $extract_method;
    private $embed_method;
    private $extract_fragments_method;
    private $sanitize_method;
    private $resolve_signing_identity_method;
    private $instance;
    private int $passed = 0;
    private int $failed = 0;

    public function __construct()
    {
        $this->rest = new ReflectionClass(\EncypherProvenance\Rest::class);
        $this->instance = $this->rest->newInstanceWithoutConstructor();

        $this->extract_method = $this->rest->getMethod('extract_text_from_html');
        $this->extract_method->setAccessible(true);

        $this->embed_method = $this->rest->getMethod('embed_signed_text_in_html');
        $this->embed_method->setAccessible(true);

        $this->extract_fragments_method = $this->rest->getMethod('extract_html_text_fragments');
        $this->extract_fragments_method->setAccessible(true);

        $this->sanitize_method = $this->rest->getMethod('sanitize_wp_block_comments');
        $this->sanitize_method->setAccessible(true);

        $this->resolve_signing_identity_method = $this->rest->getMethod('resolve_signing_identity');
        $this->resolve_signing_identity_method->setAccessible(true);
    }

    private function assert_equals($expected, $actual, string $message): void
    {
        if ($expected === $actual) {
            $this->passed++;
            echo "  ✓ {$message}\n";
        } else {
            $this->failed++;
            echo "  ✗ {$message}\n";
            echo "    Expected: " . json_encode($expected) . "\n";
            echo "    Actual:   " . json_encode($actual) . "\n";
        }
    }

    private function assert_contains(string $needle, string $haystack, string $message): void
    {
        if (strpos($haystack, $needle) !== false) {
            $this->passed++;
            echo "  ✓ {$message}\n";
        } else {
            $this->failed++;
            echo "  ✗ {$message}\n";
            echo "    Expected to contain: " . json_encode($needle) . "\n";
            echo "    In: " . json_encode(substr($haystack, 0, 200)) . "...\n";
        }
    }

    private function assert_not_contains(string $needle, string $haystack, string $message): void
    {
        if (strpos($haystack, $needle) === false) {
            $this->passed++;
            echo "  ✓ {$message}\n";
        } else {
            $this->failed++;
            echo "  ✗ {$message}\n";
            echo "    Expected NOT to contain: " . json_encode($needle) . "\n";
        }
    }

    public function test_extract_simple_paragraphs(): void
    {
        echo "\n=== test_extract_simple_paragraphs ===\n";

        $html = '<!-- wp:paragraph -->
<p>Hello world. This is a test.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Second paragraph here.</p>
<!-- /wp:paragraph -->';

        $result = $this->extract_method->invoke($this->instance, $html);

        $this->assert_equals(
            'Hello world. This is a test. Second paragraph here.',
            $result,
            'Extracts plain text from WordPress block HTML'
        );

        $this->assert_not_contains('wp:paragraph', $result, 'No WordPress block comments in output');
        $this->assert_not_contains('<p>', $result, 'No HTML tags in output');
    }

    public function test_extract_with_inline_elements(): void
    {
        echo "\n=== test_extract_with_inline_elements ===\n";

        $html = '<!-- wp:paragraph -->
<p>This has <strong>bold</strong> and <em>italic</em> text.</p>
<!-- /wp:paragraph -->';

        $result = $this->extract_method->invoke($this->instance, $html);

        $this->assert_equals(
            'This has bold and italic text.',
            $result,
            'Preserves text from inline elements'
        );
    }

    public function test_extract_with_headings(): void
    {
        echo "\n=== test_extract_with_headings ===\n";

        $html = '<!-- wp:heading -->
<h2>My Heading</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Paragraph after heading.</p>
<!-- /wp:paragraph -->';

        $result = $this->extract_method->invoke($this->instance, $html);

        $this->assert_equals(
            'My Heading Paragraph after heading.',
            $result,
            'Extracts heading and paragraph text'
        );
    }

    public function test_extract_full_wordpress_article(): void
    {
        echo "\n=== test_extract_full_wordpress_article ===\n";

        $html = '<!-- wp:paragraph -->
<p>testing encypher post. Sentence-level.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>For the last two years, the content industry has been at a crime scene. We see the impact, we feel the loss, but the trail goes cold.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>This evidence gap has locked us in a defensive battle, forcing us to ask: "How do we stop AI from using our work?"</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>It\'s the wrong question.</p>
<!-- /wp:paragraph -->';

        $result = $this->extract_method->invoke($this->instance, $html);

        // Should contain all sentences without HTML noise
        $this->assert_contains('testing encypher post.', $result, 'Contains first sentence');
        $this->assert_contains('Sentence-level.', $result, 'Contains second sentence');
        $this->assert_contains('crime scene.', $result, 'Contains crime scene sentence');
        $this->assert_contains('trail goes cold.', $result, 'Contains trail goes cold');
        $this->assert_contains('wrong question.', $result, 'Contains wrong question');
        $this->assert_not_contains('wp:paragraph', $result, 'No block comments');
        $this->assert_not_contains('<p>', $result, 'No p tags');

        // Count approximate sentences (split on ". " or "? " or ".")
        $sentences = preg_split('/(?<=[.!?])\s+/', $result);
        $sentences = array_filter($sentences, function($s) { return strlen(trim($s)) > 2; });
        echo "  Sentence count: " . count($sentences) . "\n";
        $this->assert_equals(true, count($sentences) >= 5 && count($sentences) <= 7, 'Reasonable sentence count (5-7)');
    }

    public function test_extract_fragments(): void
    {
        echo "\n=== test_extract_fragments ===\n";

        $html = '<!-- wp:paragraph -->
<p>Hello world.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Second paragraph.</p>
<!-- /wp:paragraph -->';

        $fragments = $this->extract_fragments_method->invoke($this->instance, $html);

        echo "  Fragment count: " . count($fragments) . "\n";
        foreach ($fragments as $i => [$offset, $length, $text]) {
            echo "  Fragment {$i}: offset={$offset}, len={$length}, text=" . json_encode(trim($text)) . "\n";
        }

        $this->assert_equals(2, count($fragments), 'Two text fragments (one per paragraph)');
        $this->assert_equals('Hello world.', trim($fragments[0][2]), 'First fragment is paragraph text');
        $this->assert_equals('Second paragraph.', trim($fragments[1][2]), 'Second fragment is paragraph text');
    }

    public function test_embed_preserves_html_structure(): void
    {
        echo "\n=== test_embed_preserves_html_structure ===\n";

        $html = '<!-- wp:paragraph -->
<p>Hello world.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Second paragraph.</p>
<!-- /wp:paragraph -->';

        // Simulate signed text (just the plain text, no actual VS markers for this test)
        $signed = 'Hello world. Second paragraph.';

        $result = $this->embed_method->invoke($this->instance, $html, $signed);

        $this->assert_contains('<!-- wp:paragraph -->', $result, 'WordPress block comments preserved');
        $this->assert_contains('<!-- /wp:paragraph -->', $result, 'Closing block comments preserved');
        $this->assert_contains('<p>', $result, 'P tags preserved');
        $this->assert_contains('</p>', $result, 'Closing P tags preserved');
        $this->assert_contains('Hello world.', $result, 'First paragraph text present');
        $this->assert_contains('Second paragraph.', $result, 'Second paragraph text present');
    }

    public function test_extract_skips_script_and_style(): void
    {
        echo "\n=== test_extract_skips_script_and_style ===\n";

        $html = '<p>Visible text.</p><script>var x = 1;</script><style>.foo { color: red; }</style><p>More text.</p>';

        $result = $this->extract_method->invoke($this->instance, $html);

        $this->assert_contains('Visible text.', $result, 'Contains visible text');
        $this->assert_contains('More text.', $result, 'Contains more text');
        $this->assert_not_contains('var x', $result, 'No script content');
        $this->assert_not_contains('color: red', $result, 'No style content');
    }

    public function test_sanitize_wp_block_comments(): void
    {
        echo "\n=== test_sanitize_wp_block_comments ===\n";

        $cases = [
            ['<!-- /wp :paragraph -->', '<!-- /wp:paragraph -->'],
            ['<!-- wp :paragraph -->', '<!-- wp:paragraph -->'],
            ['<!-- wp :heading -->', '<!-- wp:heading -->'],
            ['<!-- /wp :heading -->', '<!-- /wp:heading -->'],
            ['<!-- wp:paragraph -->', '<!-- wp:paragraph -->'],
            ['<!-- /wp:paragraph -->', '<!-- /wp:paragraph -->'],
        ];

        foreach ($cases as [$input, $expected]) {
            $result = $this->sanitize_method->invoke($this->instance, $input);
            $this->assert_equals($expected, $result, 'Sanitize: ' . $input);
        }

        // Full content test
        $corrupted = "<!-- wp:paragraph -->\n<p>Text.</p>\n<!-- /wp :paragraph -->";
        $fixed = $this->sanitize_method->invoke($this->instance, $corrupted);
        $this->assert_not_contains('/wp :paragraph', $fixed, 'Full content: no corrupted closing comment');
        $this->assert_contains('<!-- /wp:paragraph -->', $fixed, 'Full content: correct closing comment');
    }

    public function test_embed_no_nested_p_tags(): void
    {
        echo "\n=== test_embed_no_nested_p_tags ===\n";

        $html = '<!-- wp:paragraph -->
<p>First sentence.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Second sentence.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Third sentence.</p>
<!-- /wp:paragraph -->';

        $signed = 'First sentence. Second sentence. Third sentence.';

        $result = $this->embed_method->invoke($this->instance, $html, $signed);

        $this->assert_equals(false, (bool) preg_match('/<p>\\s*<p>|<p><p>/', $result), 'No nested <p> tags');
        $this->assert_equals(3, substr_count($result, '<!-- wp:paragraph -->'), 'Three opening block comments');
        $this->assert_equals(3, substr_count($result, '<!-- /wp:paragraph -->'), 'Three closing block comments');
    }

    public function test_resolve_signing_identity_prefers_publisher_name_over_identifier(): void
    {
        echo "\n=== test_resolve_signing_identity_prefers_publisher_name_over_identifier ===\n";

        $verdict = [
            'c2pa' => [
                'assertions' => [
                    [
                        'label' => 'c2pa.metadata',
                        'data' => [
                            'publisher' => [
                                'identifier' => 'user_a1621dd6-3298-473f-b2ad-232ca72c3df5',
                                'name' => 'Encypher',
                            ],
                        ],
                    ],
                ],
            ],
        ];

        $resolved = $this->resolve_signing_identity_method->invoke($this->instance, $verdict);
        $this->assert_equals('Encypher', $resolved, 'Uses publisher name for UI display when available');
    }

    public function test_resolve_signing_identity_falls_back_to_identifier_when_name_missing(): void
    {
        echo "\n=== test_resolve_signing_identity_falls_back_to_identifier_when_name_missing ===\n";

        $verdict = [
            'c2pa' => [
                'assertions' => [
                    [
                        'label' => 'c2pa.metadata',
                        'data' => [
                            'publisher' => [
                                'identifier' => 'org_encypher',
                            ],
                        ],
                    ],
                ],
            ],
        ];

        $resolved = $this->resolve_signing_identity_method->invoke($this->instance, $verdict);
        $this->assert_equals('org_encypher', $resolved, 'Falls back to identifier when publisher name is unavailable');
    }

    public function run_all(): void
    {
        echo "Running HTML text extraction tests...\n";

        $this->test_extract_simple_paragraphs();
        $this->test_extract_with_inline_elements();
        $this->test_extract_with_headings();
        $this->test_extract_full_wordpress_article();
        $this->test_extract_fragments();
        $this->test_embed_preserves_html_structure();
        $this->test_extract_skips_script_and_style();
        $this->test_sanitize_wp_block_comments();
        $this->test_embed_no_nested_p_tags();
        $this->test_resolve_signing_identity_prefers_publisher_name_over_identifier();
        $this->test_resolve_signing_identity_falls_back_to_identifier_when_name_missing();

        echo "\n=== Results ===\n";
        echo "Passed: {$this->passed}\n";
        echo "Failed: {$this->failed}\n";
        echo ($this->failed === 0 ? "ALL TESTS PASSED" : "SOME TESTS FAILED") . "\n";

        exit($this->failed > 0 ? 1 : 0);
    }
}

$test = new HtmlTextExtractionTest();
$test->run_all();
