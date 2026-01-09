import unittest

import c2pa_text

from encypher.interop.c2pa.text_wrapper import find_and_decode


class TestC2PATextWrapperByteOffsets(unittest.TestCase):
    def test_find_and_decode_handles_multibyte_prefix(self):
        # Prefix contains multibyte UTF-8 chars so byte offsets != char offsets
        prefix = "Café ñ ø 世界"  # includes é, ñ, ø, and CJK
        base_text = prefix + " -- signed content"

        manifest_bytes = b"test-manifest-bytes"
        embedded = c2pa_text.embed_manifest(base_text, manifest_bytes)

        extracted_bytes, clean_text, span = find_and_decode(embedded)

        self.assertEqual(extracted_bytes, manifest_bytes)
        self.assertEqual(clean_text, base_text)
        self.assertIsNotNone(span)

        # wrapper segment should start with ZWNBSP and run to end of text
        wrapper_segment = embedded[span[0] : span[1]]
        self.assertTrue(wrapper_segment.startswith("\ufeff"))
        self.assertEqual(span[1], len(embedded))
