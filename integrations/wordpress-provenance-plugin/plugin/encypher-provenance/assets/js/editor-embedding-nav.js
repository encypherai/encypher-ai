/**
 * Encypher Embedding Navigation Helper
 *
 * Makes invisible Unicode embedding characters (variation selectors,
 * tag characters, zero-width marks) behave as a single deletable unit
 * in the WordPress block editor.
 *
 * Without this, pressing backspace next to an embedding requires one
 * keypress per invisible code point — potentially dozens of presses.
 */
(function () {
    'use strict';

    /**
     * Test whether a Unicode code point is an invisible embedding character.
     *
     * Covers all ranges used by Encypher's steganographic encoding:
     *   - Variation Selectors          U+FE00 – U+FE0F
     *   - Variation Selectors Supplement U+E0100 – U+E01EF
     *   - Tags block                    U+E0001 – U+E007F
     *   - Zero-width / formatting       U+200B, U+200C, U+200D, U+2060, U+FEFF, U+202F
     */
    function isEmbeddingChar(codePoint) {
        // Variation Selectors (VS1–VS16)
        if (codePoint >= 0xFE00 && codePoint <= 0xFE0F) return true;
        // Variation Selectors Supplement (VS17–VS256)
        if (codePoint >= 0xE0100 && codePoint <= 0xE01EF) return true;
        // Tags block (used for sentence-level embeddings)
        if (codePoint >= 0xE0001 && codePoint <= 0xE007F) return true;
        // Zero-width and formatting characters used as markers
        if (codePoint === 0x200B || codePoint === 0x200C ||
            codePoint === 0x200D || codePoint === 0x2060 ||
            codePoint === 0xFEFF || codePoint === 0x202F) return true;
        return false;
    }

    /**
     * Get the full code point at a string position, handling surrogate pairs.
     * Returns { codePoint, size } where size is 1 or 2 (JS string units).
     */
    function codePointAt(str, index) {
        var cp = str.codePointAt(index);
        if (cp === undefined) return null;
        var size = cp > 0xFFFF ? 2 : 1;
        return { codePoint: cp, size: size };
    }

    /**
     * Get the code point ending at (just before) a string position.
     * Handles surrogate pairs by looking back up to 2 units.
     */
    function codePointBefore(str, index) {
        if (index <= 0) return null;
        var lo = str.charCodeAt(index - 1);
        // Check for low surrogate → look back one more for the high surrogate
        if (lo >= 0xDC00 && lo <= 0xDFFF && index >= 2) {
            var hi = str.charCodeAt(index - 2);
            if (hi >= 0xD800 && hi <= 0xDBFF) {
                var cp = ((hi - 0xD800) * 0x400) + (lo - 0xDC00) + 0x10000;
                return { codePoint: cp, size: 2 };
            }
        }
        return { codePoint: lo, size: 1 };
    }

    /**
     * Handle keydown in the editor to skip embedding character clusters.
     */
    function handleKeydown(e) {
        if (e.key !== 'Backspace' && e.key !== 'Delete') return;
        if (e.ctrlKey || e.metaKey || e.altKey) return;

        var sel = window.getSelection();
        if (!sel || !sel.isCollapsed || sel.rangeCount === 0) return;

        var range = sel.getRangeAt(0);
        var node = range.startContainer;

        // Only handle text nodes inside the editor
        if (node.nodeType !== Node.TEXT_NODE) return;
        var text = node.textContent;
        var offset = range.startOffset;

        if (e.key === 'Backspace') {
            // Check if characters before cursor are embedding chars
            var info = codePointBefore(text, offset);
            if (!info || !isEmbeddingChar(info.codePoint)) return;

            // Find the start of the embedding cluster
            var clusterStart = offset - info.size;
            while (clusterStart > 0) {
                var prev = codePointBefore(text, clusterStart);
                if (!prev || !isEmbeddingChar(prev.codePoint)) break;
                clusterStart -= prev.size;
            }

            // Delete the entire cluster in one operation
            e.preventDefault();
            var before = text.substring(0, clusterStart);
            var after = text.substring(offset);
            node.textContent = before + after;

            // Restore cursor position
            var newRange = document.createRange();
            newRange.setStart(node, clusterStart);
            newRange.collapse(true);
            sel.removeAllRanges();
            sel.addRange(newRange);

            // Notify the editor that content changed
            node.dispatchEvent(new Event('input', { bubbles: true }));

        } else if (e.key === 'Delete') {
            // Check if characters after cursor are embedding chars
            var infoFwd = codePointAt(text, offset);
            if (!infoFwd || !isEmbeddingChar(infoFwd.codePoint)) return;

            // Find the end of the embedding cluster
            var clusterEnd = offset + infoFwd.size;
            while (clusterEnd < text.length) {
                var next = codePointAt(text, clusterEnd);
                if (!next || !isEmbeddingChar(next.codePoint)) break;
                clusterEnd += next.size;
            }

            // Delete the entire cluster in one operation
            e.preventDefault();
            var beforeDel = text.substring(0, offset);
            var afterDel = text.substring(clusterEnd);
            node.textContent = beforeDel + afterDel;

            // Restore cursor position
            var newRangeDel = document.createRange();
            newRangeDel.setStart(node, offset);
            newRangeDel.collapse(true);
            sel.removeAllRanges();
            sel.addRange(newRangeDel);

            // Notify the editor that content changed
            node.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    /**
     * Attach the handler to the block editor's content area.
     * Uses MutationObserver to wait for the editor iframe or
     * direct contenteditable to appear.
     */
    function attach() {
        // Gutenberg can render in an iframe (WP 6.x+) or directly in the page
        function bindToDocument(doc) {
            doc.addEventListener('keydown', handleKeydown, true);
        }

        // Bind to the main document immediately
        bindToDocument(document);

        // Watch for the editor iframe that Gutenberg 6.x+ uses
        var observer = new MutationObserver(function (mutations) {
            for (var i = 0; i < mutations.length; i++) {
                var added = mutations[i].addedNodes;
                for (var j = 0; j < added.length; j++) {
                    var node = added[j];
                    if (node.tagName === 'IFRAME' && node.name === 'editor-canvas') {
                        node.addEventListener('load', function () {
                            if (node.contentDocument) {
                                bindToDocument(node.contentDocument);
                            }
                        });
                        // If already loaded
                        if (node.contentDocument && node.contentDocument.readyState === 'complete') {
                            bindToDocument(node.contentDocument);
                        }
                    }
                }
            }
        });

        observer.observe(document.body, { childList: true, subtree: true });

        // Also check for an already-present iframe
        var existing = document.querySelector('iframe[name="editor-canvas"]');
        if (existing && existing.contentDocument) {
            bindToDocument(existing.contentDocument);
        }
    }

    // Wait for DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', attach);
    } else {
        attach();
    }
})();
