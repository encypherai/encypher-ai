<?php
/**
 * Comprehensive HTML parser for WordPress content.
 *
 * Handles all WordPress block types and HTML elements for:
 * 1. Extracting plain text from HTML (for signing via the Enterprise API)
 * 2. Extracting text fragments with byte offsets (for embedding signed text back)
 * 3. Embedding signed text (with invisible VS markers) back into HTML text nodes
 * 4. Extracting text for verification (preserving VS markers)
 *
 * Mirrors the architecture of tools/encypher-cms-signing-kit/encypher_sign_html.py
 * but handles WordPress-specific block comments and all Gutenberg block types.
 *
 * @package EncypherProvenance
 */

namespace EncypherProvenance;

if (! defined('ABSPATH')) {
    exit;
}

class HtmlParser
{
    // =========================================================================
    // HTML element classification (matches Python CMS kit + WordPress extras)
    // =========================================================================

    /**
     * Block-level elements that introduce paragraph/line breaks in extracted text.
     * Comprehensive list covering HTML5 spec + WordPress Gutenberg output.
     */
    private const BLOCK_ELEMENTS = [
        // Sectioning
        'address', 'article', 'aside', 'body', 'footer', 'header', 'main',
        'nav', 'section',
        // Heading
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hgroup',
        // Flow / grouping
        'blockquote', 'dd', 'details', 'dialog', 'div', 'dl', 'dt',
        'fieldset', 'figcaption', 'figure', 'form', 'hr', 'legend',
        'menu', 'ol', 'p', 'pre', 'search', 'summary', 'ul',
        // List items
        'li',
        // Table
        'caption', 'col', 'colgroup', 'table', 'thead', 'tbody', 'tfoot',
        'tr', 'td', 'th',
        // Line break (treated as block boundary)
        'br',
    ];

    /**
     * Elements whose content is never visible text and should be skipped entirely.
     */
    private const SKIP_ELEMENTS = [
        'script', 'style', 'noscript', 'svg', 'math', 'video', 'audio',
        'canvas', 'iframe', 'object', 'embed', 'source', 'track', 'picture',
        'template', 'img', 'input', 'select', 'textarea', 'button',
        'map', 'area', 'link', 'meta', 'base', 'head', 'title',
    ];

    /**
     * WordPress block types that contain no user-authored text.
     * Their entire HTML output is skipped during text extraction.
     */
    private const WP_SKIP_BLOCKS = [
        'wp:image', 'wp:gallery', 'wp:video', 'wp:audio', 'wp:file',
        'wp:cover', 'wp:media-text',
        'wp:separator', 'wp:spacer', 'wp:more', 'wp:nextpage',
        'wp:buttons', 'wp:button',
        'wp:embed', 'wp:html', 'wp:shortcode', 'wp:archives',
        'wp:calendar', 'wp:categories', 'wp:latest-comments',
        'wp:latest-posts', 'wp:page-list', 'wp:rss', 'wp:search',
        'wp:social-links', 'wp:social-link', 'wp:tag-cloud',
        'wp:navigation', 'wp:navigation-link', 'wp:site-logo',
        'wp:site-title', 'wp:site-tagline', 'wp:query',
        'wp:post-template', 'wp:post-featured-image',
        'wp:post-navigation-link', 'wp:loginout',
        'wp:template-part', 'wp:pattern', 'wp:block',
        'wp:code',
    ];

    /**
     * WordPress block types that contain user-authored text.
     * These are processed normally for text extraction.
     */
    private const WP_TEXT_BLOCKS = [
        'wp:paragraph', 'wp:heading', 'wp:list', 'wp:list-item',
        'wp:quote', 'wp:pullquote', 'wp:verse', 'wp:preformatted',
        'wp:table', 'wp:freeform', 'wp:columns', 'wp:column',
        'wp:group', 'wp:details',
    ];

    // =========================================================================
    // Unicode Variation Selector helpers
    // =========================================================================

    /**
     * Check if a character is a Unicode Variation Selector or ZWNBSP (U+FEFF).
     */
    public function is_vs_char(string $ch): bool
    {
        $cp = mb_ord($ch, 'UTF-8');
        if ($cp === false) {
            return false;
        }
        return ($cp >= 0xFE00 && $cp <= 0xFE0F)
            || ($cp >= 0xE0100 && $cp <= 0xE01EF)
            || $cp === 0xFEFF;
    }

    /**
     * Check if a character is a VS char or any whitespace (including NBSP).
     */
    public function is_vs_or_whitespace(string $ch): bool
    {
        if ($this->is_vs_char($ch)) {
            return true;
        }
        return in_array($ch, [' ', "\t", "\n", "\r", "\xC2\xA0"], true);
    }

    // =========================================================================
    // 1. Extract plain text from HTML (for signing)
    // =========================================================================

    /**
     * Extract plain text from WordPress HTML post content.
     *
     * Strips WordPress block comments, HTML tags, and non-text blocks.
     * Preserves paragraph structure as spaces (matching the API's signing
     * pipeline which joins segments with spaces).
     *
     * Uses DOMDocument for correct handling of nested inline elements,
     * HTML entities, and complex block structures.
     *
     * @param string $html WordPress post_content HTML
     * @return string Plain text suitable for the /sign API
     */
    public function extract_text(string $html): string
    {
        // Phase 1: Strip WordPress block comments for non-text blocks
        $html = $this->strip_non_text_wp_blocks($html);

        // Phase 2: Strip remaining WP block comments (text blocks keep their HTML)
        $html = preg_replace('/<!--\s*\/?wp:\S.*?-->/s', '', $html);

        // Phase 3: Parse with DOMDocument for correct text extraction
        $dom = new \DOMDocument('1.0', 'UTF-8');
        $wrapped = '<?xml encoding="UTF-8"><div>' . $html . '</div>';
        @$dom->loadHTML($wrapped, LIBXML_HTML_NOIMPLIED | LIBXML_HTML_NODEFDTD | LIBXML_NOERROR);

        $root = $dom->getElementsByTagName('div')->item(0);
        if (!$root) {
            return trim(strip_tags($html));
        }

        $chunks = [];
        $this->walk_dom_for_text($root, $chunks);

        // Join chunks, collapse whitespace within lines, join paragraphs with spaces
        $raw = implode('', $chunks);
        $lines = explode("\n", $raw);
        $cleaned = [];
        foreach ($lines as $line) {
            $normalized = trim(preg_replace('/[ \t]+/', ' ', $line));
            if ('' !== $normalized) {
                $cleaned[] = $normalized;
            }
        }

        return implode(' ', $cleaned);
    }

    /**
     * Recursively walk DOM nodes collecting text content.
     *
     * Block elements insert newline boundaries. Skip elements are ignored.
     * Inline elements are traversed transparently.
     *
     * @param \DOMNode $node   Current DOM node
     * @param array    &$chunks Collected text chunks (modified in place)
     */
    private function walk_dom_for_text(\DOMNode $node, array &$chunks): void
    {
        if ($node instanceof \DOMText) {
            $text = $node->nodeValue;
            if ('' !== trim($text)) {
                $chunks[] = $text;
            } elseif ($text && $chunks && substr(end($chunks), -1) !== "\n") {
                // Preserve inter-element whitespace as a single space
                $chunks[] = ' ';
            }
            return;
        }

        if (!($node instanceof \DOMElement)) {
            return;
        }

        $tag = strtolower($node->tagName);

        if (in_array($tag, self::SKIP_ELEMENTS, true)) {
            return;
        }

        $is_block = in_array($tag, self::BLOCK_ELEMENTS, true);

        if ($is_block && $chunks && end($chunks) !== "\n") {
            $chunks[] = "\n";
        }

        foreach ($node->childNodes as $child) {
            $this->walk_dom_for_text($child, $chunks);
        }

        if ($is_block && $chunks && end($chunks) !== "\n") {
            $chunks[] = "\n";
        }
    }

    /**
     * Strip WordPress block comments and content for non-text blocks.
     *
     * Removes the entire block (opening comment + content + closing comment)
     * for blocks in WP_SKIP_BLOCKS. Text blocks are left intact.
     *
     * @param string $html WordPress post_content
     * @return string HTML with non-text blocks removed
     */
    private function strip_non_text_wp_blocks(string $html): string
    {
        foreach (self::WP_SKIP_BLOCKS as $block) {
            // Match <!-- wp:blockname ... --> ... <!-- /wp:blockname -->
            // The block name in comments doesn't have the wp: prefix in the closing tag
            $block_name = $block; // e.g. "wp:image"
            // Handle self-closing blocks: <!-- wp:image {...} /-->
            $html = preg_replace(
                '/<!--\s*' . preg_quote($block_name, '/') . '\b[^>]*?\/-->/s',
                '',
                $html
            );
            // Handle paired blocks: <!-- wp:image --> ... <!-- /wp:image -->
            $html = preg_replace(
                '/<!--\s*' . preg_quote($block_name, '/') . '\b.*?-->.*?<!--\s*\/' . preg_quote($block_name, '/') . '\s*-->/s',
                '',
                $html
            );
        }
        return $html;
    }

    // =========================================================================
    // 2. Extract text fragments with byte offsets (for embedding)
    // =========================================================================

    /**
     * Extract text fragments from HTML with their byte offsets.
     *
     * Finds runs of text between HTML tags and comments, returning each
     * fragment's byte offset, byte length, and raw text content.
     * Skips content inside script/style/noscript tags.
     *
     * @param string $html HTML content
     * @return array List of [byte_offset, byte_length, raw_text] tuples
     */
    public function extract_fragments(string $html): array
    {
        $fragments = [];
        $len = strlen($html);
        $i = 0;

        while ($i < $len) {
            if ($html[$i] === '<') {
                // Skip HTML comments (<!-- ... -->)
                if (substr($html, $i, 4) === '<!--') {
                    $end = strpos($html, '-->', $i + 4);
                    if ($end !== false) {
                        $i = $end + 3;
                    } else {
                        $i = $len;
                    }
                    continue;
                }

                // Parse the tag name
                $tag_end = strpos($html, '>', $i + 1);
                if ($tag_end === false) {
                    $i = $len;
                    continue;
                }

                $tag_content = substr($html, $i, $tag_end - $i + 1);

                // Check for skip elements (script, style, noscript, svg, etc.)
                if (preg_match('/^<(script|style|noscript|svg|math)\b/i', $tag_content, $tag_m)) {
                    $close_tag = '</' . strtolower($tag_m[1]) . '>';
                    $close_pos = stripos($html, $close_tag, $tag_end + 1);
                    if ($close_pos !== false) {
                        $i = $close_pos + strlen($close_tag);
                    } else {
                        $i = $len;
                    }
                    continue;
                }

                $i = $tag_end + 1;
                continue;
            }

            // Text content — collect until next '<'
            $text_start = $i;
            while ($i < $len && $html[$i] !== '<') {
                $i++;
            }
            $text_len = $i - $text_start;
            $raw_text = substr($html, $text_start, $text_len);

            // Only include fragments with non-whitespace content
            if ('' !== trim($raw_text)) {
                $fragments[] = [$text_start, $text_len, $raw_text];
            }
        }

        return $fragments;
    }

    // =========================================================================
    // 3. Embed signed text back into HTML
    // =========================================================================

    /**
     * Embed signed text (with invisible VS markers) back into HTML text nodes.
     *
     * Uses a byte-level approach to avoid DOMDocument::saveHTML() mangling
     * invisible Unicode characters and stripping WordPress block comments.
     *
     * Algorithm:
     * 1. Extract text fragments from the HTML (byte offsets)
     * 2. For each fragment, normalize (decode entities, collapse whitespace)
     * 3. Match normalized fragment against the signed text sequentially
     * 4. Replace the raw HTML fragment with the signed chunk (preserving leading WS)
     * 5. Apply replacements in reverse byte order to preserve offsets
     *
     * @param string $html   Original WordPress post_content HTML
     * @param string $signed Signed plain text from the Enterprise API (contains invisible VS markers)
     * @return string HTML with invisible markers embedded in text nodes
     */
    public function embed_signed_text(string $html, string $signed): string
    {
        $fragments = $this->extract_fragments($html);

        if (empty($fragments)) {
            return $signed;
        }

        // For large texts, use memory-efficient string access instead of array splitting.
        // PHP arrays have ~80 bytes overhead per element, so a 60k char string becomes ~5MB.
        // Threshold of 50k chars balances memory vs CPU tradeoff.
        $signed_len = mb_strlen($signed, 'UTF-8');
        $use_string_access = ($signed_len > 50000);

        if ($use_string_access) {
            // Memory-efficient path: access characters via mb_substr on demand
            $signed_chars = null;
            $get_char = function (int $i) use ($signed): ?string {
                return $this->mb_char_at($signed, $i);
            };
            $get_slice = function (int $start, int $len) use ($signed): string {
                return $this->mb_substring($signed, $start, $len);
            };
        } else {
            // Fast path for smaller texts: use character array
            $signed_chars = $this->mb_str_split_safe($signed);
            $signed_len = count($signed_chars);
            $get_char = function (int $i) use ($signed_chars, $signed_len): ?string {
                return ($i >= 0 && $i < $signed_len) ? $signed_chars[$i] : null;
            };
            $get_slice = function (int $start, int $len) use ($signed_chars): string {
                return implode('', array_slice($signed_chars, $start, $len));
            };
        }
        $cursor = 0;

        $replacements = [];
        $last_frag_idx = null;

        foreach ($fragments as $frag_idx => [$offset, $length, $raw_text]) {
            // Normalize fragment: decode HTML entities, collapse whitespace (Unicode-aware)
            $decoded = html_entity_decode($raw_text, ENT_QUOTES | ENT_HTML5, 'UTF-8');
            $decoded = wp_check_invalid_utf8($decoded, true);
            if (! is_string($decoded) || '' === $decoded) {
                continue;
            }
            $normalized = preg_replace('/\s+/u', ' ', trim($decoded, " \t\n\r\0\x0B\xC2\xA0"));
            if (! is_string($normalized) || '' === $normalized) {
                continue;
            }

            // Collect inter-fragment VS chars and whitespace gap
            $gap_vs = '';
            while ($cursor < $signed_len) {
                $ch = $get_char($cursor);
                if ($ch === null || !$this->is_vs_or_whitespace($ch)) {
                    break;
                }
                if ($this->is_vs_char($ch)) {
                    $gap_vs .= $ch;
                }
                $cursor++;
            }

            // Match visible text, skipping embedded VS chars in the signed text
            $match_start = $cursor;
            $norm_chars = $this->mb_str_split_safe($normalized);
            $ti = 0;
            $si = $cursor;
            $norm_len = count($norm_chars);

            while ($si < $signed_len && $ti < $norm_len) {
                $ch = $get_char($si);
                if ($ch === null) {
                    break;
                }
                if ($this->is_vs_char($ch)) {
                    $si++;
                    continue;
                }
                if ($ch === $norm_chars[$ti]) {
                    $ti++;
                    $si++;
                } elseif ($ch === "\xC2\xA0" && $norm_chars[$ti] === ' ') {
                    // NBSP in signed text matches space in fragment
                    $ti++;
                    $si++;
                } elseif ($norm_chars[$ti] === "\xC2\xA0" && $ch === ' ') {
                    // NBSP in fragment matches space in signed text
                    $ti++;
                    $si++;
                } else {
                    break;
                }
            }

            if ($ti !== $norm_len) {
                // No match — attach gap VS chars to previous fragment
                if ('' !== $gap_vs && $last_frag_idx !== null && isset($replacements[$last_frag_idx])) {
                    $replacements[$last_frag_idx][2] .= $gap_vs;
                }
                continue;
            }

            // Consume trailing VS chars after the matched text
            while ($si < $signed_len) {
                $ch = $get_char($si);
                if ($ch === null || !$this->is_vs_char($ch)) {
                    break;
                }
                $si++;
            }

            // Extract the signed chunk (visible text + embedded VS markers)
            $signed_chunk = $get_slice($match_start, $si - $match_start);
            $cursor = $si;

            // Preserve original leading whitespace from the raw HTML text.
            // Trailing whitespace is intentionally dropped: the signed chunk
            // ends with VS markers whose byte positions are part of the C2PA
            // content hash.
            $leading_ws = '';
            if (preg_match('/^(\s+)/u', $raw_text, $m)) {
                $leading_ws = $m[1];
            }

            $replacement = $leading_ws . $gap_vs . $signed_chunk;
            $replacements[$frag_idx] = [$offset, $length, $replacement];
            $last_frag_idx = $frag_idx;
        }

        // Append any remaining VS chars (tail of C2PA manifest) to the last replacement
        $remaining_vs = '';
        while ($cursor < $signed_len) {
            $ch = $get_char($cursor);
            if ($ch === null) {
                break;
            }
            if ($this->is_vs_char($ch)) {
                $remaining_vs .= $ch;
            }
            $cursor++;
        }
        if ('' !== $remaining_vs && $last_frag_idx !== null && isset($replacements[$last_frag_idx])) {
            $replacements[$last_frag_idx][2] .= $remaining_vs;
        }

        // Apply replacements in reverse byte-offset order to preserve positions
        $result = $html;
        $sorted = $replacements;
        usort($sorted, function ($a, $b) {
            return $b[0] - $a[0];
        });

        foreach ($sorted as [$off, $len, $rep]) {
            $result = substr_replace($result, $rep, $off, $len);
        }

        $matched = count($replacements);
        $total = count($fragments);
        error_log(sprintf('Encypher: Embedded signed text into %d of %d HTML text fragments', $matched, $total));

        return $result;
    }

    // =========================================================================
    // 4. Extract text for verification (preserving VS markers)
    // =========================================================================

    /**
     * Extract plain text from HTML for verification, preserving VS markers.
     *
     * Unlike extract_text() (which uses DOMDocument and may mangle invisible
     * Unicode chars), this method works at the byte level via extract_fragments().
     * It strips HTML tags and block comments while keeping all VS characters
     * intact — critical for C2PA content hash matching.
     *
     * @param string $html WordPress post_content HTML with embedded VS markers
     * @return string Plain text with VS markers preserved
     */
    public function extract_text_for_verify(string $html): string
    {
        $fragments = $this->extract_fragments($html);
        if (empty($fragments)) {
            return '';
        }

        $parts = [];
        $prev_end = null;

        foreach ($fragments as [$offset, $length, $raw_text]) {
            $decoded = html_entity_decode($raw_text, ENT_QUOTES | ENT_HTML5, 'UTF-8');
            $decoded = wp_check_invalid_utf8($decoded, true);
            if (! is_string($decoded) || '' === $decoded) {
                continue;
            }
            // Collapse whitespace but preserve VS chars
            $chars = $this->mb_str_split_safe($decoded);
            $result_chars = [];
            $last_was_ws = false;
            foreach ($chars as $ch) {
                if ($this->is_vs_char($ch)) {
                    $result_chars[] = $ch;
                    $last_was_ws = false;
                } elseif (preg_match('/\s/u', $ch)) {
                    if (!$last_was_ws) {
                        $result_chars[] = ' ';
                        $last_was_ws = true;
                    }
                } else {
                    $result_chars[] = $ch;
                    $last_was_ws = false;
                }
            }
            $content = trim(implode('', $result_chars));
            if ('' !== $content) {
                if ($prev_end !== null) {
                    $gap_html = substr($html, $prev_end, $offset - $prev_end);
                    if ($this->gap_requires_space((string) $gap_html)) {
                        $parts[] = ' ';
                    }
                }
                $parts[] = $content;
                $prev_end = $offset + $length;
            }
        }

        return implode('', $parts);
    }

    /**
     * Determine whether HTML between text fragments implies a single space.
     *
     * This avoids false spaces across inline boundaries (e.g. "foo<em>bar</em>")
     * while still preserving block-level spacing (e.g. "</p><p>").
     */
    private function gap_requires_space(string $gap_html): bool
    {
        if ('' === $gap_html) {
            return false;
        }

        // Explicit whitespace between fragments should collapse to one space.
        if (preg_match('/\s/u', $gap_html)) {
            return true;
        }

        // If the boundary crosses block-level tags, preserve paragraph spacing.
        if (preg_match_all('/<\/?\s*([a-zA-Z0-9:-]+)/', $gap_html, $matches) && !empty($matches[1])) {
            foreach ($matches[1] as $tag_name) {
                $tag = strtolower((string) $tag_name);
                if (in_array($tag, self::BLOCK_ELEMENTS, true)) {
                    return true;
                }
            }
        }

        return false;
    }

    // =========================================================================
    // WordPress block comment utilities
    // =========================================================================

    /**
     * Sanitize WordPress block comments that may have been corrupted.
     *
     * VS char stripping can leave stray spaces in block comment delimiters
     * (e.g. "<!-- /wp :paragraph -->" instead of "<!-- /wp:paragraph -->").
     *
     * @param string $content WordPress post_content
     * @return string Content with sanitized block comments
     */
    public function sanitize_wp_block_comments(string $content): string
    {
        // Fix corrupted opening comments: <!-- wp :blockname --> → <!-- wp:blockname -->
        $content = preg_replace(
            '/<!--\s+wp\s+:(\S+)/s',
            '<!-- wp:$1',
            $content
        );

        // Fix corrupted closing comments: <!-- /wp :blockname --> → <!-- /wp:blockname -->
        $content = preg_replace(
            '/<!--\s+\/wp\s+:(\S+)/s',
            '<!-- /wp:$1',
            $content
        );

        return $content;
    }

    /**
     * Strip all C2PA embeddings (VS chars and ZWNBSP) from content.
     *
     * @param string $content Text or HTML content
     * @return string Content with all VS chars removed
     */
    public function strip_c2pa_embeddings(string $content): string
    {
        return preg_replace('/[\x{FE00}-\x{FE0F}\x{E0100}-\x{E01EF}\x{FEFF}]/u', '', $content);
    }

    /**
     * Detect C2PA embeddings in text.
     *
     * Scans for C2PA text wrapper magic bytes encoded in Unicode variation selectors.
     *
     * @param string $text Text to scan
     * @return array ['count' => int, 'positions' => array]
     */
    public function detect_c2pa_embeddings(string $text): array
    {
        // C2PA magic: "C2PATXT\0" = 0x43 0x32 0x50 0x41 0x54 0x58 0x54 0x00
        // Encoded as VS chars after a ZWNBSP (U+FEFF) prefix
        $magic_bytes = [0x43, 0x32, 0x50, 0x41, 0x54, 0x58, 0x54, 0x00];
        $magic_chars = '';
        foreach ($magic_bytes as $b) {
            if ($b < 16) {
                $magic_chars .= chr(0xEF) . chr(0xB8) . chr(0x80 + $b); // U+FE00 + b
            } else {
                // U+E0100 + (b - 16) encoded in UTF-8
                $cp = 0xE0100 + ($b - 16);
                $magic_chars .= chr(0xF3) . chr(0xA0 | (($cp >> 12) & 0x0F))
                    . chr(0x80 | (($cp >> 6) & 0x3F)) . chr(0x80 | ($cp & 0x3F));
            }
        }

        $positions = [];
        $offset = 0;
        while (($pos = strpos($text, $magic_chars, $offset)) !== false) {
            $positions[] = $pos;
            $offset = $pos + strlen($magic_chars);
        }

        return ['count' => count($positions), 'positions' => $positions];
    }

    // =========================================================================
    // Utility methods
    // =========================================================================

    /**
     * Split a string into an array of multibyte characters.
     *
     * For large strings (>50k chars), this can consume significant memory.
     * Consider using mb_char_at() for on-demand access when processing
     * very large texts.
     *
     * @param string $str Input string
     * @return array Array of single characters
     */
    public function mb_str_split_safe(string $str): array
    {
        if (function_exists('mb_str_split')) {
            return mb_str_split($str);
        }
        $result = preg_split('//u', $str, -1, PREG_SPLIT_NO_EMPTY);
        return is_array($result) ? $result : [];
    }

    /**
     * Get a single multibyte character at a given index.
     *
     * Memory-efficient alternative to mb_str_split for large strings.
     * Uses mb_substr which has O(n) complexity but constant memory.
     *
     * @param string $str Input string
     * @param int $index Character index (0-based)
     * @return string|null Single character or null if out of bounds
     */
    public function mb_char_at(string $str, int $index): ?string
    {
        if ($index < 0) {
            return null;
        }
        $char = mb_substr($str, $index, 1, 'UTF-8');
        return ($char === '' || $char === false) ? null : $char;
    }

    /**
     * Get substring using multibyte-safe extraction.
     *
     * @param string $str Input string
     * @param int $start Start index
     * @param int $length Number of characters
     * @return string Substring
     */
    public function mb_substring(string $str, int $start, int $length): string
    {
        $result = mb_substr($str, $start, $length, 'UTF-8');
        return ($result === false) ? '' : $result;
    }
}
