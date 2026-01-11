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

        # span is (start_byte, length_byte) in NFC-normalized UTF-8 bytes
        start_byte, length_byte = span
        expected_start = len(base_text.encode("utf-8"))
        expected_length = len(c2pa_text.encode_wrapper(manifest_bytes).encode("utf-8"))
        self.assertEqual(start_byte, expected_start)
        self.assertEqual(length_byte, expected_length)

    def test_multiple_feff_blocks_non_c2pa_is_not_an_error(self):
        base_text = "Hello world"
        manifest_bytes = b"test-manifest-bytes"
        embedded = c2pa_text.embed_manifest(base_text, manifest_bytes)

        fake_payload = b"not-a-c2pa-wrapper" * 4
        fake_wrapper = c2pa_text.encode_wrapper(fake_payload)
        fake_block = "\ufeff" + "\ufe00" + fake_wrapper[2:]
        text_with_two_blocks = embedded + fake_block

        extracted_bytes, clean_text, span = find_and_decode(text_with_two_blocks)
        self.assertEqual(extracted_bytes, manifest_bytes)
        self.assertIsNotNone(span)
        self.assertTrue(clean_text.startswith(base_text))

    def test_multiple_valid_c2pa_wrappers_raises(self):
        base_text = "Hello world"
        first = c2pa_text.embed_manifest(base_text, b"first")
        second_wrapper = c2pa_text.encode_wrapper(b"second")
        text_with_two_wrappers = first + second_wrapper

        with self.assertWarns(UserWarning):
            extracted_bytes, clean_text, span = find_and_decode(text_with_two_wrappers)
        self.assertEqual(extracted_bytes, b"second")
        self.assertEqual(clean_text, base_text)
        self.assertIsNotNone(span)

        start_byte, length_byte = span
        first_wrapper = first[len(base_text) :]
        expected_start = len(base_text.encode("utf-8")) + len(first_wrapper.encode("utf-8"))
        expected_length = len(second_wrapper.encode("utf-8"))
        self.assertEqual(start_byte, expected_start)
        self.assertEqual(length_byte, expected_length)
