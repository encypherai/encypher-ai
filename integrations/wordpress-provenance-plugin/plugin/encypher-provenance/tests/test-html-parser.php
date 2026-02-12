#!/usr/bin/env php
<?php
/**
 * Comprehensive tests for the HtmlParser class.
 *
 * Run inside the WordPress container:
 *   docker exec <wordpress-container> php \
 *     /var/www/html/wp-content/plugins/encypher-provenance/tests/test-html-parser.php
 *
 * Tests cover all WordPress block types and HTML elements.
 */

// Bootstrap WordPress if not already loaded
if (!defined('ABSPATH')) {
    $wp_load = '/var/www/html/wp-load.php';
    if (file_exists($wp_load)) {
        require_once $wp_load;
    } else {
        if (!defined('ABSPATH')) {
            define('ABSPATH', __DIR__ . '/../');
        }
    }
}

require_once __DIR__ . '/../includes/class-encypher-provenance-html-parser.php';

class HtmlParserTest
{
    private \EncypherProvenance\HtmlParser $parser;
    private int $passed = 0;
    private int $failed = 0;

    public function __construct()
    {
        $this->parser = new \EncypherProvenance\HtmlParser();
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
            echo "    In: " . json_encode(mb_substr($haystack, 0, 200)) . "...\n";
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

    // =========================================================================
    // extract_text tests
    // =========================================================================

    public function test_simple_paragraphs(): void
    {
        echo "\n=== test_simple_paragraphs ===\n";
        $html = '<!-- wp:paragraph -->
<p>Hello world. This is a test.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Second paragraph here.</p>
<!-- /wp:paragraph -->';

        $result = $this->parser->extract_text($html);
        $this->assert_equals(
            'Hello world. This is a test. Second paragraph here.',
            $result,
            'Extracts plain text from simple paragraphs'
        );
        $this->assert_not_contains('wp:paragraph', $result, 'No block comments');
        $this->assert_not_contains('<p>', $result, 'No HTML tags');
    }

    public function test_inline_elements(): void
    {
        echo "\n=== test_inline_elements ===\n";
        $html = '<!-- wp:paragraph -->
<p>This has <strong>bold</strong> and <em>italic</em> text.</p>
<!-- /wp:paragraph -->';

        $result = $this->parser->extract_text($html);
        $this->assert_equals(
            'This has bold and italic text.',
            $result,
            'Preserves text from inline elements'
        );
    }

    public function test_headings(): void
    {
        echo "\n=== test_headings ===\n";
        $html = '<!-- wp:heading -->
<h2 class="wp-block-heading">My Heading</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Paragraph after heading.</p>
<!-- /wp:paragraph -->';

        $result = $this->parser->extract_text($html);
        $this->assert_equals(
            'My Heading Paragraph after heading.',
            $result,
            'Extracts heading and paragraph text'
        );
    }

    public function test_unordered_list(): void
    {
        echo "\n=== test_unordered_list ===\n";
        $html = '<!-- wp:list -->
<ul><!-- wp:list-item -->
<li><strong>Proof of origin</strong> for any text content</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><strong>Tamper-evident signatures</strong> that survive copy-paste</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><strong>Interoperability</strong> across platforms</li>
<!-- /wp:list-item --></ul>
<!-- /wp:list -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Proof of origin', $result, 'Contains first list item bold text');
        $this->assert_contains('for any text content', $result, 'Contains first list item plain text');
        $this->assert_contains('Tamper-evident signatures', $result, 'Contains second list item');
        $this->assert_contains('Interoperability', $result, 'Contains third list item');
        $this->assert_not_contains('<li>', $result, 'No li tags');
        $this->assert_not_contains('<strong>', $result, 'No strong tags');
        $this->assert_not_contains('wp:list', $result, 'No block comments');
    }

    public function test_ordered_list(): void
    {
        echo "\n=== test_ordered_list ===\n";
        $html = '<!-- wp:list {"ordered":true} -->
<ol><!-- wp:list-item -->
<li>First item</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li>Second item</li>
<!-- /wp:list-item --></ol>
<!-- /wp:list -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('First item', $result, 'Contains first ordered item');
        $this->assert_contains('Second item', $result, 'Contains second ordered item');
    }

    public function test_nested_list(): void
    {
        echo "\n=== test_nested_list ===\n";
        $html = '<!-- wp:list -->
<ul><li>Parent item
<ul><li>Child item one</li>
<li>Child item two</li></ul></li>
<li>Another parent</li></ul>
<!-- /wp:list -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Parent item', $result, 'Contains parent item');
        $this->assert_contains('Child item one', $result, 'Contains first child');
        $this->assert_contains('Child item two', $result, 'Contains second child');
        $this->assert_contains('Another parent', $result, 'Contains second parent');
    }

    public function test_blockquote(): void
    {
        echo "\n=== test_blockquote ===\n";
        $html = '<!-- wp:quote -->
<blockquote class="wp-block-quote">
<p>This is a quoted paragraph.</p>
<cite>Author Name</cite>
</blockquote>
<!-- /wp:quote -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('This is a quoted paragraph.', $result, 'Contains quote text');
        $this->assert_contains('Author Name', $result, 'Contains citation');
    }

    public function test_pullquote(): void
    {
        echo "\n=== test_pullquote ===\n";
        $html = '<!-- wp:pullquote -->
<figure class="wp-block-pullquote"><blockquote><p>A pullquote for emphasis.</p><cite>Source</cite></blockquote></figure>
<!-- /wp:pullquote -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('A pullquote for emphasis.', $result, 'Contains pullquote text');
        $this->assert_contains('Source', $result, 'Contains pullquote source');
    }

    public function test_table(): void
    {
        echo "\n=== test_table ===\n";
        $html = '<!-- wp:table -->
<figure class="wp-block-table"><table><thead><tr><th>Header 1</th><th>Header 2</th></tr></thead><tbody><tr><td>Cell A</td><td>Cell B</td></tr><tr><td>Cell C</td><td>Cell D</td></tr></tbody></table></figure>
<!-- /wp:table -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Header 1', $result, 'Contains table header 1');
        $this->assert_contains('Header 2', $result, 'Contains table header 2');
        $this->assert_contains('Cell A', $result, 'Contains cell A');
        $this->assert_contains('Cell D', $result, 'Contains cell D');
    }

    public function test_preformatted(): void
    {
        echo "\n=== test_preformatted ===\n";
        $html = '<!-- wp:preformatted -->
<pre class="wp-block-preformatted">Some preformatted text here.</pre>
<!-- /wp:preformatted -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Some preformatted text here.', $result, 'Contains preformatted text');
    }

    public function test_verse(): void
    {
        echo "\n=== test_verse ===\n";
        $html = '<!-- wp:verse -->
<pre class="wp-block-verse">Roses are red,
Violets are blue.</pre>
<!-- /wp:verse -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Roses are red,', $result, 'Contains first verse line');
        $this->assert_contains('Violets are blue.', $result, 'Contains second verse line');
    }

    public function test_columns(): void
    {
        echo "\n=== test_columns ===\n";
        $html = '<!-- wp:columns -->
<div class="wp-block-columns"><!-- wp:column -->
<div class="wp-block-column"><!-- wp:paragraph -->
<p>Column one text.</p>
<!-- /wp:paragraph --></div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column"><!-- wp:paragraph -->
<p>Column two text.</p>
<!-- /wp:paragraph --></div>
<!-- /wp:column --></div>
<!-- /wp:columns -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Column one text.', $result, 'Contains column one');
        $this->assert_contains('Column two text.', $result, 'Contains column two');
    }

    public function test_group(): void
    {
        echo "\n=== test_group ===\n";
        $html = '<!-- wp:group -->
<div class="wp-block-group"><!-- wp:paragraph -->
<p>Grouped paragraph.</p>
<!-- /wp:paragraph --></div>
<!-- /wp:group -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Grouped paragraph.', $result, 'Contains grouped text');
    }

    public function test_details_block(): void
    {
        echo "\n=== test_details_block ===\n";
        $html = '<!-- wp:details -->
<details class="wp-block-details"><summary>Click to expand</summary>
<!-- wp:paragraph -->
<p>Hidden content here.</p>
<!-- /wp:paragraph --></details>
<!-- /wp:details -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Click to expand', $result, 'Contains summary text');
        $this->assert_contains('Hidden content here.', $result, 'Contains details content');
    }

    // =========================================================================
    // Skip blocks tests
    // =========================================================================

    public function test_skip_image_block(): void
    {
        echo "\n=== test_skip_image_block ===\n";
        $html = '<!-- wp:paragraph -->
<p>Before image.</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":123} -->
<figure class="wp-block-image"><img src="test.jpg" alt="Test"/><figcaption>Caption text</figcaption></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>After image.</p>
<!-- /wp:paragraph -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Before image.', $result, 'Contains text before image');
        $this->assert_contains('After image.', $result, 'Contains text after image');
        $this->assert_not_contains('Caption text', $result, 'Image caption is skipped');
    }

    public function test_skip_code_block(): void
    {
        echo "\n=== test_skip_code_block ===\n";
        $html = '<!-- wp:paragraph -->
<p>Before code.</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>function hello() { return "world"; }</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>After code.</p>
<!-- /wp:paragraph -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Before code.', $result, 'Contains text before code');
        $this->assert_contains('After code.', $result, 'Contains text after code');
        $this->assert_not_contains('function hello', $result, 'Code block content is skipped');
    }

    public function test_skip_embed_block(): void
    {
        echo "\n=== test_skip_embed_block ===\n";
        $html = '<!-- wp:paragraph -->
<p>Check out this video.</p>
<!-- /wp:paragraph -->

<!-- wp:embed {"url":"https://youtube.com/watch?v=123"} -->
<figure class="wp-block-embed"><div class="wp-block-embed__wrapper">https://youtube.com/watch?v=123</div></figure>
<!-- /wp:embed -->

<!-- wp:paragraph -->
<p>What do you think?</p>
<!-- /wp:paragraph -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Check out this video.', $result, 'Contains text before embed');
        $this->assert_contains('What do you think?', $result, 'Contains text after embed');
        $this->assert_not_contains('youtube.com', $result, 'Embed URL is skipped');
    }

    public function test_skip_separator_spacer(): void
    {
        echo "\n=== test_skip_separator_spacer ===\n";
        $html = '<!-- wp:paragraph -->
<p>Before separator.</p>
<!-- /wp:paragraph -->

<!-- wp:separator -->
<hr class="wp-block-separator"/>
<!-- /wp:separator -->

<!-- wp:spacer {"height":"50px"} -->
<div style="height:50px" class="wp-block-spacer"></div>
<!-- /wp:spacer -->

<!-- wp:paragraph -->
<p>After spacer.</p>
<!-- /wp:paragraph -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Before separator.', $result, 'Contains text before separator');
        $this->assert_contains('After spacer.', $result, 'Contains text after spacer');
    }

    public function test_skip_buttons(): void
    {
        echo "\n=== test_skip_buttons ===\n";
        $html = '<!-- wp:paragraph -->
<p>Click below to learn more.</p>
<!-- /wp:paragraph -->

<!-- wp:buttons -->
<div class="wp-block-buttons"><!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link">Learn More</a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons -->

<!-- wp:paragraph -->
<p>More content here.</p>
<!-- /wp:paragraph -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Click below to learn more.', $result, 'Contains paragraph text');
        $this->assert_contains('More content here.', $result, 'Contains text after buttons');
        $this->assert_not_contains('Learn More', $result, 'Button text is skipped');
    }

    public function test_skip_self_closing_image(): void
    {
        echo "\n=== test_skip_self_closing_image ===\n";
        $html = '<!-- wp:paragraph -->
<p>Text here.</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":42,"sizeSlug":"large"} /-->

<!-- wp:paragraph -->
<p>More text.</p>
<!-- /wp:paragraph -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Text here.', $result, 'Contains first paragraph');
        $this->assert_contains('More text.', $result, 'Contains second paragraph');
    }

    // =========================================================================
    // HTML entity handling
    // =========================================================================

    public function test_html_entities(): void
    {
        echo "\n=== test_html_entities ===\n";
        $html = '<!-- wp:paragraph -->
<p>Founder &amp; CEO of Encypher</p>
<!-- /wp:paragraph -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Founder & CEO', $result, 'Decodes &amp; entity');
    }

    public function test_nbsp_entities(): void
    {
        echo "\n=== test_nbsp_entities ===\n";
        $html = '<!-- wp:paragraph -->
<p>The&nbsp;<strong>C2PA 2.3 specification</strong>&nbsp;is live.</p>
<!-- /wp:paragraph -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('C2PA 2.3 specification', $result, 'Contains text across nbsp boundaries');
        $this->assert_contains('is live.', $result, 'Contains text after nbsp');
    }

    public function test_inline_code(): void
    {
        echo "\n=== test_inline_code ===\n";
        $html = '<!-- wp:paragraph -->
<p>The <code>C2PATextManifestWrapper</code> structure uses Unicode variation selectors.</p>
<!-- /wp:paragraph -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('C2PATextManifestWrapper', $result, 'Contains inline code text');
        $this->assert_contains('structure uses Unicode', $result, 'Contains text around code');
    }

    public function test_links(): void
    {
        echo "\n=== test_links ===\n";
        $html = '<!-- wp:paragraph -->
<p>Visit <a href="https://example.com">our website</a> for more info.</p>
<!-- /wp:paragraph -->';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Visit our website for more info.', $result, 'Contains link text inline');
        $this->assert_not_contains('https://example.com', $result, 'No href URL in text');
    }

    // =========================================================================
    // Script/style skipping
    // =========================================================================

    public function test_skip_script_style(): void
    {
        echo "\n=== test_skip_script_style ===\n";
        $html = '<p>Visible text.</p><script>var x = 1;</script><style>.foo { color: red; }</style><p>More text.</p>';

        $result = $this->parser->extract_text($html);
        $this->assert_contains('Visible text.', $result, 'Contains visible text');
        $this->assert_contains('More text.', $result, 'Contains more text');
        $this->assert_not_contains('var x', $result, 'No script content');
        $this->assert_not_contains('color: red', $result, 'No style content');
    }

    // =========================================================================
    // Fragment extraction tests
    // =========================================================================

    public function test_extract_fragments_simple(): void
    {
        echo "\n=== test_extract_fragments_simple ===\n";
        $html = '<!-- wp:paragraph -->
<p>Hello world.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Second paragraph.</p>
<!-- /wp:paragraph -->';

        $fragments = $this->parser->extract_fragments($html);
        $this->assert_equals(2, count($fragments), 'Two text fragments');
        $this->assert_equals('Hello world.', trim($fragments[0][2]), 'First fragment');
        $this->assert_equals('Second paragraph.', trim($fragments[1][2]), 'Second fragment');
    }

    public function test_extract_fragments_with_entities(): void
    {
        echo "\n=== test_extract_fragments_with_entities ===\n";
        $html = '<p>Founder &amp; CEO</p>';

        $fragments = $this->parser->extract_fragments($html);
        $this->assert_equals(1, count($fragments), 'One fragment');
        $this->assert_contains('&amp;', $fragments[0][2], 'Raw fragment contains entity');
    }

    public function test_extract_fragments_skips_script(): void
    {
        echo "\n=== test_extract_fragments_skips_script ===\n";
        $html = '<p>Text</p><script>var x = 1;</script><p>More</p>';

        $fragments = $this->parser->extract_fragments($html);
        $this->assert_equals(2, count($fragments), 'Two fragments (script skipped)');
        $this->assert_equals('Text', trim($fragments[0][2]), 'First fragment');
        $this->assert_equals('More', trim($fragments[1][2]), 'Second fragment');
    }

    // =========================================================================
    // Embed signed text tests
    // =========================================================================

    public function test_embed_preserves_html(): void
    {
        echo "\n=== test_embed_preserves_html ===\n";
        $html = '<!-- wp:paragraph -->
<p>Hello world.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Second paragraph.</p>
<!-- /wp:paragraph -->';

        $signed = 'Hello world. Second paragraph.';
        $result = $this->parser->embed_signed_text($html, $signed);

        $this->assert_contains('<!-- wp:paragraph -->', $result, 'Block comments preserved');
        $this->assert_contains('<p>', $result, 'P tags preserved');
        $this->assert_contains('Hello world.', $result, 'First paragraph text');
        $this->assert_contains('Second paragraph.', $result, 'Second paragraph text');
    }

    public function test_embed_no_nested_p_tags(): void
    {
        echo "\n=== test_embed_no_nested_p_tags ===\n";
        $html = '<!-- wp:paragraph -->
<p>First.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Second.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Third.</p>
<!-- /wp:paragraph -->';

        $signed = 'First. Second. Third.';
        $result = $this->parser->embed_signed_text($html, $signed);

        $this->assert_equals(false, (bool) preg_match('/<p>\s*<p>|<p><p>/', $result), 'No nested <p> tags');
        $this->assert_equals(3, substr_count($result, '<!-- wp:paragraph -->'), 'Three block comments');
    }

    public function test_embed_with_entities(): void
    {
        echo "\n=== test_embed_with_entities ===\n";
        $html = '<p>Founder &amp; CEO</p>';
        $signed = 'Founder & CEO';

        $result = $this->parser->embed_signed_text($html, $signed);
        $this->assert_contains('<p>', $result, 'P tag preserved');
        $this->assert_contains('Founder', $result, 'Contains text');
    }

    public function test_embed_with_nbsp(): void
    {
        echo "\n=== test_embed_with_nbsp ===\n";
        $html = '<p>The&nbsp;<strong>bold text</strong>&nbsp;here.</p>';
        // Signed text has NBSP decoded
        $signed = "The\xC2\xA0bold text\xC2\xA0here.";

        $result = $this->parser->embed_signed_text($html, $signed);
        $this->assert_contains('<strong>', $result, 'Strong tag preserved');
        $this->assert_contains('bold text', $result, 'Bold text present');
    }

    public function test_embed_list_items(): void
    {
        echo "\n=== test_embed_list_items ===\n";
        $html = '<ul><li><strong>Item one</strong> details</li><li><strong>Item two</strong> details</li></ul>';
        $signed = 'Item one details Item two details';

        $result = $this->parser->embed_signed_text($html, $signed);
        $this->assert_contains('<ul>', $result, 'UL tag preserved');
        $this->assert_contains('<li>', $result, 'LI tags preserved');
        $this->assert_contains('<strong>', $result, 'Strong tags preserved');
        $this->assert_contains('Item one', $result, 'First item text');
        $this->assert_contains('Item two', $result, 'Second item text');
    }

    // =========================================================================
    // Sanitize block comments tests
    // =========================================================================

    public function test_sanitize_wp_block_comments(): void
    {
        echo "\n=== test_sanitize_wp_block_comments ===\n";
        $cases = [
            ['<!-- /wp :paragraph -->', '<!-- /wp:paragraph -->'],
            ['<!-- wp :paragraph -->', '<!-- wp:paragraph -->'],
            ['<!-- wp :heading -->', '<!-- wp:heading -->'],
            ['<!-- /wp :heading -->', '<!-- /wp:heading -->'],
            ['<!-- wp:paragraph -->', '<!-- wp:paragraph -->'],
        ];

        foreach ($cases as [$input, $expected]) {
            $result = $this->parser->sanitize_wp_block_comments($input);
            $this->assert_equals($expected, $result, "Sanitize: {$input}");
        }
    }

    // =========================================================================
    // extract_text_for_verify tests
    // =========================================================================

    public function test_extract_text_for_verify_preserves_vs(): void
    {
        echo "\n=== test_extract_text_for_verify_preserves_vs ===\n";
        // Simulate HTML with VS chars embedded in text
        $vs_char = "\xEF\xB8\x80"; // U+FE00 (VS1)
        $html = '<p>Hello' . $vs_char . ' world.</p>';

        $result = $this->parser->extract_text_for_verify($html);
        $this->assert_contains($vs_char, $result, 'VS char preserved in verify text');
        $this->assert_contains('Hello', $result, 'Text before VS preserved');
        $this->assert_contains('world.', $result, 'Text after VS preserved');
    }

    // =========================================================================
    // Round-trip test (extract → sign → embed → verify)
    // =========================================================================

    public function test_roundtrip_complex_html(): void
    {
        echo "\n=== test_roundtrip_complex_html ===\n";
        $html = '<!-- wp:heading -->
<h2 class="wp-block-heading">What This Means</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>For the first time, there is an&nbsp;<strong>official, global standard</strong>&nbsp;for embedding cryptographic provenance into plain text. This enables:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul><!-- wp:list-item -->
<li><strong>Proof of origin</strong> for any text content</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><strong>Tamper-evident signatures</strong> that survive copy-paste</li>
<!-- /wp:list-item --></ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>The specification is live at:&nbsp;<a href="https://spec.c2pa.org">C2PA Section A.7</a></p>
<!-- /wp:paragraph -->';

        // Step 1: Extract text
        $text = $this->parser->extract_text($html);
        $this->assert_contains('What This Means', $text, 'Roundtrip: heading extracted');
        $this->assert_contains('official, global standard', $text, 'Roundtrip: bold text extracted');
        $this->assert_contains('Proof of origin', $text, 'Roundtrip: list item extracted');
        $this->assert_contains('C2PA Section A.7', $text, 'Roundtrip: link text extracted');

        // Step 2: Simulate signed text (same text, no actual VS markers)
        $signed = $text;

        // Step 3: Embed back into HTML
        $result = $this->parser->embed_signed_text($html, $signed);

        // Step 4: Verify HTML structure preserved
        $this->assert_contains('<!-- wp:heading -->', $result, 'Roundtrip: heading block preserved');
        $this->assert_contains('<!-- wp:list -->', $result, 'Roundtrip: list block preserved');
        $this->assert_contains('<strong>', $result, 'Roundtrip: strong tags preserved');
        $this->assert_contains('<a href="https://spec.c2pa.org">', $result, 'Roundtrip: link preserved');
        $this->assert_contains('What This Means', $result, 'Roundtrip: heading text in result');
        $this->assert_contains('Proof of origin', $result, 'Roundtrip: list item in result');
    }

    // =========================================================================
    // C2PA detection tests
    // =========================================================================

    public function test_detect_no_embeddings(): void
    {
        echo "\n=== test_detect_no_embeddings ===\n";
        $result = $this->parser->detect_c2pa_embeddings('Hello world, no embeddings here.');
        $this->assert_equals(0, $result['count'], 'No embeddings in plain text');
    }

    public function test_strip_embeddings(): void
    {
        echo "\n=== test_strip_embeddings ===\n";
        $vs = "\xEF\xB8\x80"; // U+FE00
        $text = "Hello{$vs} world{$vs}.";
        $result = $this->parser->strip_c2pa_embeddings($text);
        $this->assert_equals('Hello world.', $result, 'VS chars stripped');
    }

    // =========================================================================
    // Run all
    // =========================================================================

    public function run_all(): void
    {
        echo "Running HtmlParser comprehensive tests...\n";

        // extract_text
        $this->test_simple_paragraphs();
        $this->test_inline_elements();
        $this->test_headings();
        $this->test_unordered_list();
        $this->test_ordered_list();
        $this->test_nested_list();
        $this->test_blockquote();
        $this->test_pullquote();
        $this->test_table();
        $this->test_preformatted();
        $this->test_verse();
        $this->test_columns();
        $this->test_group();
        $this->test_details_block();

        // Skip blocks
        $this->test_skip_image_block();
        $this->test_skip_code_block();
        $this->test_skip_embed_block();
        $this->test_skip_separator_spacer();
        $this->test_skip_buttons();
        $this->test_skip_self_closing_image();

        // HTML entities
        $this->test_html_entities();
        $this->test_nbsp_entities();
        $this->test_inline_code();
        $this->test_links();

        // Script/style
        $this->test_skip_script_style();

        // Fragments
        $this->test_extract_fragments_simple();
        $this->test_extract_fragments_with_entities();
        $this->test_extract_fragments_skips_script();

        // Embed
        $this->test_embed_preserves_html();
        $this->test_embed_no_nested_p_tags();
        $this->test_embed_with_entities();
        $this->test_embed_with_nbsp();
        $this->test_embed_list_items();

        // Sanitize
        $this->test_sanitize_wp_block_comments();

        // Verify
        $this->test_extract_text_for_verify_preserves_vs();

        // Round-trip
        $this->test_roundtrip_complex_html();

        // C2PA detection
        $this->test_detect_no_embeddings();
        $this->test_strip_embeddings();

        echo "\n=== Results ===\n";
        echo "Passed: {$this->passed}\n";
        echo "Failed: {$this->failed}\n";
        echo ($this->failed === 0 ? "ALL TESTS PASSED" : "SOME TESTS FAILED") . "\n";

        exit($this->failed > 0 ? 1 : 0);
    }
}

$test = new HtmlParserTest();
$test->run_all();
