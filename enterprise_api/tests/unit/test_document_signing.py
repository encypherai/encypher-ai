"""E2E tests for C2PA document signing (PDF + ZIP-based formats).

Tests the full signing pipeline: placeholder insertion, content hashing,
CBOR claim building, COSE signing, JUMBF serialization, and embedding.
Verifies structural integrity of the output.
"""

import io
import struct
import zipfile

import cbor2
import pytest


# ---- Test fixtures ----


@pytest.fixture
def test_certs():
    """Load test signing certificates."""
    import os

    cert_dir = os.path.join(os.path.dirname(__file__), "..", "c2pa_test_certs")
    with open(os.path.join(cert_dir, "private_key.pem")) as f:
        private_key = f.read()
    with open(os.path.join(cert_dir, "cert_chain.pem")) as f:
        cert_chain = f.read()
    return private_key, cert_chain


def make_test_epub() -> bytes:
    """Create a minimal valid EPUB file."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        # EPUB requires mimetype as first entry (uncompressed)
        zf.writestr(
            zipfile.ZipInfo("mimetype", date_time=(2024, 1, 1, 0, 0, 0)),
            "application/epub+zip",
            compress_type=zipfile.ZIP_STORED,
        )
        zf.writestr(
            "META-INF/container.xml",
            '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>',
        )
        zf.writestr(
            "content.opf",
            '<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0"><metadata><dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Test</dc:title></metadata></package>',
        )
        zf.writestr("chapter1.xhtml", "<html><body><p>Hello World</p></body></html>")
    return buf.getvalue()


def make_test_docx() -> bytes:
    """Create a minimal DOCX (OOXML) file."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/></Types>',
        )
        zf.writestr(
            "_rels/.rels",
            '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>',
        )
        zf.writestr(
            "word/document.xml",
            '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Test document</w:t></w:r></w:p></w:body></w:document>',
        )
    return buf.getvalue()


def make_test_odt() -> bytes:
    """Create a minimal ODT file."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.text", compress_type=zipfile.ZIP_STORED)
        zf.writestr(
            "content.xml",
            '<?xml version="1.0"?><office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"><office:body><office:text><text:p>Test</text:p></office:text></office:body></office:document-content>',
        )
        zf.writestr(
            "META-INF/manifest.xml",
            '<?xml version="1.0"?><manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"><manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/></manifest:manifest>',
        )
    return buf.getvalue()


def make_test_pdf() -> bytes:
    """Create a minimal valid PDF."""
    # Minimal PDF 1.4
    objects = []
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    objects.append(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n")

    body = b"%PDF-1.4\n"
    offsets = []
    for obj in objects:
        offsets.append(len(body))
        body += obj

    xref_offset = len(body)
    xref = b"xref\n0 4\n"
    xref += b"0000000000 65535 f \n"
    for off in offsets:
        xref += f"{off:010d} 00000 n \n".encode()

    trailer = f"trailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode()
    return body + xref + trailer


# ---- JUMBF tests ----


class TestJumbfSerializer:
    def test_box_basic(self):
        from app.utils.jumbf import _box

        result = _box(b"test", b"\x01\x02\x03")
        assert len(result) == 8 + 3
        assert struct.unpack(">I", result[:4])[0] == 11
        assert result[4:8] == b"test"
        assert result[8:] == b"\x01\x02\x03"

    def test_description_box(self):
        from app.utils.jumbf import UUID_MANIFEST_STORE, description_box

        desc = description_box(UUID_MANIFEST_STORE, "c2pa")
        assert len(desc) > 8
        assert desc[4:8] == b"jumd"

    def test_superbox(self):
        from app.utils.jumbf import UUID_MANIFEST_STORE, cbor_box, superbox

        content = cbor_box(cbor2.dumps({"test": True}))
        box = superbox(UUID_MANIFEST_STORE, "c2pa", [content])
        assert box[4:8] == b"jumb"

    def test_build_manifest_store(self):
        from app.utils.jumbf import build_manifest_store, cbor_box, superbox, UUID_MANIFEST

        inner = superbox(UUID_MANIFEST, "urn:c2pa:test", [cbor_box(b"\xa0")])
        store = build_manifest_store([inner])
        assert store[4:8] == b"jumb"
        assert len(store) > 0


# ---- COSE signer tests ----


class TestCoseSigner:
    def test_sign_claim_produces_tagged_cose(self, test_certs):
        from app.utils.cose_signer import sign_claim

        private_key, cert_chain = test_certs

        claim_cbor = cbor2.dumps({"test": "claim"})
        result = sign_claim(claim_cbor, private_key, cert_chain)

        # Should be CBOR-decodable
        decoded = cbor2.loads(result)
        assert isinstance(decoded, cbor2.CBORTag)
        assert decoded.tag == 18  # COSE_Sign1

        # Inner structure: [protected, unprotected, nil, signature]
        inner = decoded.value
        assert len(inner) == 4
        assert inner[2] is None  # detached payload
        assert len(inner[3]) > 0  # signature bytes

    def test_sign_claim_includes_cert_chain(self, test_certs):
        from app.utils.cose_signer import sign_claim, COSE_HDR_X5CHAIN

        private_key, cert_chain = test_certs

        claim_cbor = cbor2.dumps({"test": "claim"})
        result = sign_claim(claim_cbor, private_key, cert_chain)

        decoded = cbor2.loads(result)
        unprotected = decoded.value[1]
        assert "x5chain" in unprotected

    def test_sign_claim_protected_has_alg(self, test_certs):
        from app.utils.cose_signer import sign_claim, COSE_HDR_ALG

        private_key, cert_chain = test_certs

        claim_cbor = cbor2.dumps({"test": "claim"})
        result = sign_claim(claim_cbor, private_key, cert_chain)

        decoded = cbor2.loads(result)
        protected = cbor2.loads(decoded.value[0])
        assert COSE_HDR_ALG in protected


# ---- Claim builder tests ----


class TestClaimBuilder:
    def test_build_actions_assertion(self):
        from app.utils.c2pa_claim_builder import build_actions_assertion

        result = build_actions_assertion("c2pa.created")
        assert "actions" in result
        assert result["actions"][0]["action"] == "c2pa.created"
        assert "digitalSourceType" in result["actions"][0]

    def test_build_collection_data_hash(self):
        from app.utils.c2pa_claim_builder import build_collection_data_hash

        result = build_collection_data_hash(
            [{"uri": "test.txt", "hash": b"\x00" * 32}],
            b"\x00" * 32,
        )
        assert "uris" in result
        assert result["alg"] == "sha256"
        assert result["zip_central_directory_hash"] == b"\x00" * 32

    def test_build_data_hash(self):
        from app.utils.c2pa_claim_builder import build_data_hash

        result = build_data_hash(b"\x00" * 32, [{"start": 100, "length": 200}])
        assert result["hash"] == b"\x00" * 32
        assert len(result["exclusions"]) == 1
        assert result["exclusions"][0]["start"] == 100

    def test_build_claim_cbor(self):
        from app.utils.c2pa_claim_builder import build_claim_cbor

        result = build_claim_cbor(
            "urn:c2pa:test",
            [("c2pa.actions.v2", b"\x00" * 50)],
            dc_format="application/pdf",
            title="Test Doc",
        )
        claim = cbor2.loads(result)
        assert "claim_generator_info" in claim
        assert "created_assertions" in claim
        assert len(claim["created_assertions"]) == 1
        assert claim["dc:title"] == "Test Doc"


# ---- ZIP embedder tests ----


class TestZipEmbedder:
    def test_create_zip_with_placeholder(self):
        from app.utils.zip_c2pa_embedder import MANIFEST_PATH, create_zip_with_placeholder

        epub = make_test_epub()
        result = create_zip_with_placeholder(epub, 1024)

        with zipfile.ZipFile(io.BytesIO(result)) as zf:
            names = zf.namelist()
            assert MANIFEST_PATH in names
            manifest_data = zf.read(MANIFEST_PATH)
            assert len(manifest_data) == 1024
            assert manifest_data == b"\x00" * 1024

    def test_compute_collection_hashes(self):
        from app.utils.zip_c2pa_embedder import compute_collection_hashes, create_zip_with_placeholder

        epub = make_test_epub()
        zip_bytes = create_zip_with_placeholder(epub)

        file_hashes, cd_hash = compute_collection_hashes(zip_bytes)
        assert len(file_hashes) > 0
        assert all(len(fh["hash"]) == 32 for fh in file_hashes)
        assert len(cd_hash) == 32
        # Manifest should not be in file hashes
        assert all(fh["uri"] != "META-INF/content_credential.c2pa" for fh in file_hashes)

    def test_replace_manifest(self):
        from app.utils.zip_c2pa_embedder import MANIFEST_PATH, create_zip_with_placeholder, replace_manifest_in_zip

        epub = make_test_epub()
        zip_bytes = create_zip_with_placeholder(epub, 1024)

        manifest = b"FAKE_MANIFEST_DATA_HERE"
        result = replace_manifest_in_zip(zip_bytes, manifest)

        with zipfile.ZipFile(io.BytesIO(result)) as zf:
            data = zf.read(MANIFEST_PATH)
            # In-place patch pads manifest to fill placeholder; data starts with manifest bytes
            assert data[: len(manifest)] == manifest
            assert len(data) == 1024  # Full placeholder size preserved

    def test_original_files_preserved(self):
        from app.utils.zip_c2pa_embedder import MANIFEST_PATH, create_zip_with_placeholder

        epub = make_test_epub()

        with zipfile.ZipFile(io.BytesIO(epub)) as orig:
            orig_names = set(orig.namelist())

        result = create_zip_with_placeholder(epub)
        with zipfile.ZipFile(io.BytesIO(result)) as new:
            new_names = set(new.namelist())

        # All original files should be present, plus the manifest
        assert orig_names.issubset(new_names)
        assert MANIFEST_PATH in new_names


# ---- PDF embedder tests ----


class TestPdfEmbedder:
    def test_create_pdf_with_placeholder(self):
        from app.utils.pdf_c2pa_embedder import create_pdf_with_placeholder

        pdf = make_test_pdf()
        result, start, length = create_pdf_with_placeholder(pdf, 4096)

        assert len(result) > len(pdf)
        assert start > 0
        assert length > 0
        assert start + length <= len(result)

    def test_compute_pdf_hash(self):
        from app.utils.pdf_c2pa_embedder import compute_pdf_hash, create_pdf_with_placeholder

        pdf = make_test_pdf()
        result, start, length = create_pdf_with_placeholder(pdf)

        h = compute_pdf_hash(result, start, length)
        assert len(h) == 32  # SHA-256

    def test_replace_manifest(self):
        from app.utils.pdf_c2pa_embedder import create_pdf_with_placeholder, replace_manifest_in_pdf

        pdf = make_test_pdf()
        result, start, length = create_pdf_with_placeholder(pdf, 4096)

        manifest = b"FAKE_MANIFEST" + b"\x00" * (length - 13)
        final = replace_manifest_in_pdf(result, manifest[:length], start, length)
        assert len(final) == len(result)

    def test_manifest_too_large_raises(self):
        from app.utils.pdf_c2pa_embedder import create_pdf_with_placeholder, replace_manifest_in_pdf

        pdf = make_test_pdf()
        result, start, length = create_pdf_with_placeholder(pdf, 100)

        with pytest.raises(ValueError, match="exceeds placeholder"):
            replace_manifest_in_pdf(result, b"\x00" * (length + 1), start, length)


# ---- E2E signing tests ----


class TestDocumentSigningE2E:
    """Full end-to-end signing tests for each document format."""

    def test_epub_sign_e2e(self, test_certs):
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs
        epub = make_test_epub()

        result = sign_document(
            epub,
            "application/epub+zip",
            title="Test EPUB",
            org_id="org_test",
            document_id="doc_test",
            asset_id="asset_test",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )

        assert result.signed_size > result.original_size
        assert result.mime_type == "application/epub+zip"
        assert result.manifest_label.startswith("urn:c2pa:")

        # Verify the manifest is in the ZIP
        with zipfile.ZipFile(io.BytesIO(result.signed_bytes)) as zf:
            assert "META-INF/content_credential.c2pa" in zf.namelist()
            manifest_data = zf.read("META-INF/content_credential.c2pa")
            assert len(manifest_data) > 0
            # Verify JUMBF structure: first 4 bytes = length, next 4 = "jumb"
            assert manifest_data[4:8] == b"jumb"

        # Verify original content preserved
        with zipfile.ZipFile(io.BytesIO(result.signed_bytes)) as zf:
            assert zf.read("chapter1.xhtml") == b"<html><body><p>Hello World</p></body></html>"

    def test_docx_sign_e2e(self, test_certs):
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs
        docx = make_test_docx()

        result = sign_document(
            docx,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            title="Test DOCX",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )

        assert result.signed_size > result.original_size
        with zipfile.ZipFile(io.BytesIO(result.signed_bytes)) as zf:
            assert "META-INF/content_credential.c2pa" in zf.namelist()

    def test_odt_sign_e2e(self, test_certs):
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs
        odt = make_test_odt()

        result = sign_document(
            odt,
            "application/vnd.oasis.opendocument.text",
            title="Test ODT",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )

        assert result.signed_size > result.original_size
        with zipfile.ZipFile(io.BytesIO(result.signed_bytes)) as zf:
            assert "META-INF/content_credential.c2pa" in zf.namelist()

    def test_pdf_sign_e2e(self, test_certs):
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs
        pdf = make_test_pdf()

        result = sign_document(
            pdf,
            "application/pdf",
            title="Test PDF",
            org_id="org_test",
            document_id="doc_test",
            asset_id="asset_test",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )

        assert result.signed_size > result.original_size
        assert result.mime_type == "application/pdf"
        assert result.manifest_label.startswith("urn:c2pa:")
        # PDF should still start with %PDF
        assert result.signed_bytes[:5] == b"%PDF-"

    def test_unsupported_mime_raises(self, test_certs):
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs

        with pytest.raises(ValueError, match="Unsupported"):
            sign_document(
                b"data",
                "text/plain",
                private_key_pem=private_key,
                cert_chain_pem=cert_chain,
            )


class TestManifestStructure:
    """Verify the JUMBF manifest store structure is valid."""

    def test_epub_manifest_has_valid_jumbf(self, test_certs):
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs
        epub = make_test_epub()

        result = sign_document(
            epub,
            "application/epub+zip",
            title="JUMBF Structure Test",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )

        with zipfile.ZipFile(io.BytesIO(result.signed_bytes)) as zf:
            manifest = zf.read("META-INF/content_credential.c2pa")

        # Parse JUMBF structure
        # Manifest store: jumb box -- actual manifest bytes before zero padding
        assert manifest[4:8] == b"jumb"
        store_size = struct.unpack(">I", manifest[:4])[0]
        assert store_size <= len(manifest)

        # Find description box (jumd) inside the store
        inner = manifest[8:]
        desc_size = struct.unpack(">I", inner[:4])[0]
        assert inner[4:8] == b"jumd"

    def test_epub_manifest_contains_cose_signature(self, test_certs):
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs
        epub = make_test_epub()

        result = sign_document(
            epub,
            "application/epub+zip",
            title="COSE Test",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )

        with zipfile.ZipFile(io.BytesIO(result.signed_bytes)) as zf:
            manifest = zf.read("META-INF/content_credential.c2pa")

        # The manifest should contain CBOR-encoded COSE data somewhere
        # Search for COSE_Sign1 tag (0xd2 = tag 18 in CBOR)
        assert b"\xd2" in manifest or b"\x12" in manifest  # CBOR tag encoding

    def test_collection_hash_covers_all_files(self, test_certs):
        """Verify that the collection data hash references all non-manifest files."""
        from app.utils.zip_c2pa_embedder import compute_collection_hashes, create_zip_with_placeholder

        epub = make_test_epub()
        zip_bytes = create_zip_with_placeholder(epub)

        file_hashes, cd_hash = compute_collection_hashes(zip_bytes)

        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            expected_files = [n for n in zf.namelist() if n != "META-INF/content_credential.c2pa"]

        hashed_files = {fh["uri"] for fh in file_hashes}
        for f in expected_files:
            assert f in hashed_files, f"File {f} not in collection hash"


# ---- Font fixture ----


def make_test_otf() -> bytes:
    """Create a minimal valid OTF (TrueType-flavored SFNT) for testing."""
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen

    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder([".notdef", "space"])
    fb.setupCharacterMap({32: "space"})
    pen = TTGlyphPen(None)
    pen.moveTo((0, 0))
    pen.lineTo((500, 0))
    pen.lineTo((500, 700))
    pen.lineTo((0, 700))
    pen.closePath()
    fb.setupGlyf({".notdef": pen.glyph(), "space": TTGlyphPen(None).glyph()})
    fb.setupHorizontalMetrics({"space": (250, 0), ".notdef": (500, 0)})
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({"familyName": "TestFont", "styleName": "Regular"})
    fb.setupOS2()
    fb.setupPost()
    fb.setupHead(unitsPerEm=1000)
    buf = io.BytesIO()
    fb.font.save(buf)
    return buf.getvalue()


# ---- Font embedder tests ----


class TestFontEmbedder:
    def test_parse_sfnt(self):
        from app.utils.font_c2pa_embedder import parse_sfnt

        font = make_test_otf()
        info = parse_sfnt(font)
        assert info["version"] in (b"\x00\x01\x00\x00", b"OTTO")
        assert len(info["tables"]) >= 5  # head, hhea, hmtx, etc.

    def test_parse_sfnt_invalid(self):
        from app.utils.font_c2pa_embedder import parse_sfnt

        with pytest.raises(ValueError, match="Not a valid SFNT"):
            parse_sfnt(b"NOT_A_FONT_FILE_AT_ALL")

    def test_create_font_with_placeholder(self):
        from app.utils.font_c2pa_embedder import C2PA_TAG, create_font_with_placeholder, parse_sfnt

        font = make_test_otf()
        result, offset, length = create_font_with_placeholder(font, 4096)

        assert len(result) > len(font)
        assert offset > 0
        assert length == 4096

        # Verify C2PA table exists
        info = parse_sfnt(result)
        c2pa_tables = [t for t in info["tables"] if t["tag"] == C2PA_TAG]
        assert len(c2pa_tables) == 1
        assert c2pa_tables[0]["offset"] == offset
        assert c2pa_tables[0]["length"] == length

    def test_tables_sorted(self):
        from app.utils.font_c2pa_embedder import create_font_with_placeholder, parse_sfnt

        font = make_test_otf()
        result, _, _ = create_font_with_placeholder(font)
        info = parse_sfnt(result)
        tags = [t["tag"] for t in info["tables"]]
        assert tags == sorted(tags), "SFNT tables must be sorted by tag"

    def test_compute_font_hash(self):
        from app.utils.font_c2pa_embedder import compute_font_hash, create_font_with_placeholder

        font = make_test_otf()
        result, offset, length = create_font_with_placeholder(font)
        h = compute_font_hash(result, offset, length)
        assert len(h) == 32  # SHA-256

    def test_replace_manifest(self):
        from app.utils.font_c2pa_embedder import create_font_with_placeholder, replace_manifest_in_font

        font = make_test_otf()
        result, offset, length = create_font_with_placeholder(font, 4096)
        manifest = b"FAKE_C2PA_MANIFEST" + b"\x00" * (length - 18)
        final = replace_manifest_in_font(result, manifest[:length], offset, length)
        assert len(final) == len(result)
        # Verify the manifest is embedded at the right offset
        assert final[offset : offset + 18] == b"FAKE_C2PA_MANIFEST"

    def test_manifest_too_large_raises(self):
        from app.utils.font_c2pa_embedder import create_font_with_placeholder, replace_manifest_in_font

        font = make_test_otf()
        result, offset, length = create_font_with_placeholder(font, 100)
        with pytest.raises(ValueError, match="exceeds"):
            replace_manifest_in_font(result, b"\x00" * (length + 1), offset, length)

    def test_original_tables_preserved(self):
        from app.utils.font_c2pa_embedder import C2PA_TAG, create_font_with_placeholder, parse_sfnt

        font = make_test_otf()
        orig_info = parse_sfnt(font)
        orig_tags = {t["tag"] for t in orig_info["tables"]}

        result, _, _ = create_font_with_placeholder(font)
        new_info = parse_sfnt(result)
        new_tags = {t["tag"] for t in new_info["tables"]}

        # All original tables plus C2PA
        assert orig_tags.issubset(new_tags)
        assert C2PA_TAG in new_tags


# ---- Font E2E signing test ----


class TestFontSigningE2E:
    def test_otf_sign_e2e(self, test_certs):
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs
        font = make_test_otf()

        result = sign_document(
            font,
            "font/otf",
            title="TestFont Regular",
            org_id="org_test",
            document_id="font_test",
            asset_id="font_asset_1",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )

        assert result.signed_size > result.original_size
        assert result.mime_type == "font/otf"
        assert result.manifest_label.startswith("urn:c2pa:")

        # Verify the signed font is still a valid SFNT
        from app.utils.font_c2pa_embedder import C2PA_TAG, parse_sfnt

        info = parse_sfnt(result.signed_bytes)
        c2pa_tables = [t for t in info["tables"] if t["tag"] == C2PA_TAG]
        assert len(c2pa_tables) == 1

        # C2PA table should contain JUMBF (LBox(4 bytes) + "jumb")
        t = c2pa_tables[0]
        manifest = result.signed_bytes[t["offset"] : t["offset"] + t["length"]]
        # JUMBF box starts at byte 0: first 4 bytes = LBox (size), next 4 = "jumb"
        assert manifest[4:8] == b"jumb", f"C2PA table should contain JUMBF manifest store, got {manifest[4:8]!r}"

    def test_otf_sign_preserves_font_data(self, test_certs):
        """Verify the signed font can still be parsed by fontTools."""
        from fontTools.ttLib import TTFont
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs
        font = make_test_otf()

        result = sign_document(
            font,
            "font/otf",
            title="TestFont Preserved",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )

        # fontTools should be able to parse the signed font
        tt = TTFont(io.BytesIO(result.signed_bytes))
        assert "head" in tt
        assert "hmtx" in tt
        assert "C2PA" in tt  # Our custom table
        tt.close()


# ---- JUMBF Parser tests ----


class TestJumbfParser:
    def test_parse_box(self):
        from app.utils.jumbf import _box, parse_box

        original = _box(b"test", b"\x01\x02\x03")
        box_type, payload, next_off = parse_box(original)
        assert box_type == b"test"
        assert payload == b"\x01\x02\x03"
        assert next_off == len(original)

    def test_parse_superbox(self):
        from app.utils.jumbf import UUID_MANIFEST_STORE, cbor_box, parse_superbox, superbox

        content = cbor_box(cbor2.dumps({"test": True}))
        box = superbox(UUID_MANIFEST_STORE, "c2pa", [content])
        parsed = parse_superbox(box)
        assert parsed["label"] == "c2pa"
        assert parsed["type_uuid"] == UUID_MANIFEST_STORE
        assert len(parsed["content_boxes"]) == 1

    def test_roundtrip_manifest_store(self, test_certs):
        """Sign a document, then parse the manifest store from the output."""
        from app.services.document_signing_service import sign_document
        from app.utils.jumbf import parse_manifest_store

        private_key, cert_chain = test_certs
        epub = make_test_epub()

        result = sign_document(
            epub,
            "application/epub+zip",
            title="Parse Test",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )

        with zipfile.ZipFile(io.BytesIO(result.signed_bytes)) as zf:
            manifest_bytes = zf.read("META-INF/content_credential.c2pa")

        store = parse_manifest_store(manifest_bytes)
        assert len(store["manifests"]) == 1
        m = store["manifests"][0]
        assert m["label"].startswith("urn:c2pa:")
        assert "c2pa.actions.v2" in m["assertions"]
        assert m["claim_cbor"] is not None
        assert m["signature_cose"] is not None


# ---- COSE Verification tests ----


class TestCoseVerification:
    def test_sign_then_verify(self, test_certs):
        from app.utils.cose_signer import sign_claim, verify_cose_sign1

        private_key, cert_chain = test_certs

        claim = cbor2.dumps({"test": "verification_roundtrip"})
        cose_bytes = sign_claim(claim, private_key, cert_chain)
        result = verify_cose_sign1(cose_bytes, claim)

        assert result.valid is True
        assert result.error is None
        assert result.certificate_der is not None

    def test_tampered_claim_fails(self, test_certs):
        from app.utils.cose_signer import sign_claim, verify_cose_sign1

        private_key, cert_chain = test_certs

        claim = cbor2.dumps({"test": "original"})
        cose_bytes = sign_claim(claim, private_key, cert_chain)

        tampered = cbor2.dumps({"test": "tampered"})
        result = verify_cose_sign1(cose_bytes, tampered)
        assert result.valid is False

    def test_invalid_cose_bytes(self):
        from app.utils.cose_signer import verify_cose_sign1

        result = verify_cose_sign1(b"not valid cbor", b"claim")
        assert result.valid is False


# ---- Full Sign + Verify Roundtrip Tests ----


class TestSignVerifyRoundtrip:
    """The critical tests: sign a document, extract the manifest,
    parse JUMBF, verify the COSE signature, and check hash binding."""

    def _verify_signed_zip(self, signed_bytes: bytes, test_certs):
        """Common verification logic for ZIP-based documents."""
        from app.utils.cose_signer import verify_cose_sign1
        from app.utils.jumbf import parse_manifest_store
        from app.utils.zip_c2pa_embedder import compute_collection_hashes

        # 1. Extract manifest from ZIP
        with zipfile.ZipFile(io.BytesIO(signed_bytes)) as zf:
            manifest_bytes = zf.read("META-INF/content_credential.c2pa")

        # 2. Parse JUMBF manifest store
        store = parse_manifest_store(manifest_bytes)
        assert len(store["manifests"]) >= 1
        m = store["manifests"][0]

        # 3. Verify COSE signature
        assert m["claim_cbor"] is not None
        assert m["signature_cose"] is not None
        cose_result = verify_cose_sign1(m["signature_cose"], m["claim_cbor"])
        assert cose_result.valid is True, f"COSE verification failed: {cose_result.error}"

        # 4. Verify claim structure
        claim = cbor2.loads(m["claim_cbor"])
        assert "claim_generator_info" in claim
        assert "created_assertions" in claim
        assert "signature" in claim

        # 5. Verify collection data hash assertion exists
        assert "c2pa.hash.collection.data" in m["assertions"]
        collection_hash = cbor2.loads(m["assertions"]["c2pa.hash.collection.data"])
        assert "uris" in collection_hash
        assert "zip_central_directory_hash" in collection_hash

        # 6. Verify hash binding: recompute and compare
        file_hashes, cd_hash = compute_collection_hashes(signed_bytes)
        stored_uris = {u["uri"]: u["hash"] for u in collection_hash["uris"]}
        for fh in file_hashes:
            assert fh["uri"] in stored_uris, f"File {fh['uri']} not in manifest"
            assert fh["hash"] == stored_uris[fh["uri"]], f"Hash mismatch for {fh['uri']}"

        return True

    def _verify_signed_font(self, signed_bytes: bytes, test_certs):
        """Common verification logic for SFNT fonts."""
        from app.utils.cose_signer import verify_cose_sign1
        from app.utils.font_c2pa_embedder import C2PA_TAG, compute_font_hash, parse_sfnt
        from app.utils.jumbf import parse_manifest_store

        # 1. Extract manifest from C2PA SFNT table
        info = parse_sfnt(signed_bytes)
        c2pa_tables = [t for t in info["tables"] if t["tag"] == C2PA_TAG]
        assert len(c2pa_tables) == 1
        t = c2pa_tables[0]
        manifest_bytes = signed_bytes[t["offset"] : t["offset"] + t["length"]]

        # 2. Parse JUMBF
        store = parse_manifest_store(manifest_bytes)
        assert len(store["manifests"]) >= 1
        m = store["manifests"][0]

        # 3. Verify COSE signature
        cose_result = verify_cose_sign1(m["signature_cose"], m["claim_cbor"])
        assert cose_result.valid is True, f"COSE verification failed: {cose_result.error}"

        # 4. Verify data hash assertion
        assert "c2pa.hash.data" in m["assertions"]
        data_hash_assertion = cbor2.loads(m["assertions"]["c2pa.hash.data"])
        assert "hash" in data_hash_assertion
        assert "exclusions" in data_hash_assertion

        # 5. Verify hash binding
        excl = data_hash_assertion["exclusions"][0]
        recomputed = compute_font_hash(signed_bytes, excl["start"], excl["length"])
        assert recomputed == data_hash_assertion["hash"], "Font data hash mismatch"

        return True

    def _verify_signed_pdf(self, signed_bytes: bytes, test_certs):
        """Common verification logic for PDF documents."""
        from app.utils.cose_signer import verify_cose_sign1
        from app.utils.jumbf import parse_manifest_store
        from app.utils.pdf_c2pa_embedder import _PLACEHOLDER_MARKER

        # 1. Find the JUMBF manifest in the PDF
        # The manifest is embedded in a PDF stream -- locate the JUMBF start
        jumb_offset = signed_bytes.find(b"jumb")
        assert jumb_offset > 0, "No JUMBF found in PDF"
        # The LBox is 4 bytes before "jumb"
        manifest_start = jumb_offset - 4
        lbox = struct.unpack(">I", signed_bytes[manifest_start : manifest_start + 4])[0]
        manifest_bytes = signed_bytes[manifest_start : manifest_start + lbox]

        # 2. Parse JUMBF
        store = parse_manifest_store(manifest_bytes)
        assert len(store["manifests"]) >= 1
        m = store["manifests"][0]

        # 3. Verify COSE signature
        cose_result = verify_cose_sign1(m["signature_cose"], m["claim_cbor"])
        assert cose_result.valid is True, f"COSE verification failed: {cose_result.error}"

        # 4. Verify claim structure
        claim = cbor2.loads(m["claim_cbor"])
        assert "created_assertions" in claim

        return True

    def test_epub_sign_verify_roundtrip(self, test_certs):
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs
        result = sign_document(
            make_test_epub(),
            "application/epub+zip",
            title="EPUB Verify",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )
        assert self._verify_signed_zip(result.signed_bytes, test_certs)

    def test_docx_sign_verify_roundtrip(self, test_certs):
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs
        result = sign_document(
            make_test_docx(),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            title="DOCX Verify",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )
        assert self._verify_signed_zip(result.signed_bytes, test_certs)

    def test_odt_sign_verify_roundtrip(self, test_certs):
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs
        result = sign_document(
            make_test_odt(),
            "application/vnd.oasis.opendocument.text",
            title="ODT Verify",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )
        assert self._verify_signed_zip(result.signed_bytes, test_certs)

    def test_pdf_sign_verify_roundtrip(self, test_certs):
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs
        result = sign_document(
            make_test_pdf(),
            "application/pdf",
            title="PDF Verify",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )
        assert self._verify_signed_pdf(result.signed_bytes, test_certs)

    def _verify_signed_flac(self, signed_bytes: bytes, test_certs):
        """Common verification logic for FLAC audio files."""
        from app.utils.cose_signer import verify_cose_sign1
        from app.utils.flac_c2pa_embedder import (
            C2PA_APP_ID,
            FLAC_MAGIC,
            _parse_metadata_blocks,
            compute_flac_hash,
        )
        from app.utils.jumbf import parse_manifest_store

        # 1. Verify FLAC structure
        assert signed_bytes[:4] == FLAC_MAGIC
        blocks = _parse_metadata_blocks(signed_bytes)
        app_blocks = [b for b in blocks if b["type"] == 2 and signed_bytes[b["data_offset"] : b["data_offset"] + 4] == C2PA_APP_ID]
        assert len(app_blocks) == 1
        ab = app_blocks[0]
        manifest_offset = ab["data_offset"] + 4  # after app_id
        manifest_length = ab["length"] - 4

        # 2. Extract and parse JUMBF manifest
        manifest_bytes = signed_bytes[manifest_offset : manifest_offset + manifest_length]
        # Trim trailing zeros (padding)
        manifest_bytes = manifest_bytes.rstrip(b"\x00")
        store = parse_manifest_store(manifest_bytes)
        assert len(store["manifests"]) >= 1
        m = store["manifests"][0]

        # 3. Verify COSE signature
        cose_result = verify_cose_sign1(m["signature_cose"], m["claim_cbor"])
        assert cose_result.valid is True, f"COSE verification failed: {cose_result.error}"

        # 4. Verify data hash assertion
        assert "c2pa.hash.data" in m["assertions"]
        data_hash_assertion = cbor2.loads(m["assertions"]["c2pa.hash.data"])
        assert "hash" in data_hash_assertion
        assert "exclusions" in data_hash_assertion

        # 5. Verify hash binding
        excl = data_hash_assertion["exclusions"][0]
        recomputed = compute_flac_hash(signed_bytes, excl["start"], excl["length"])
        assert recomputed == data_hash_assertion["hash"], "FLAC data hash mismatch"

        return True

    def test_otf_sign_verify_roundtrip(self, test_certs):
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs
        result = sign_document(
            make_test_otf(),
            "font/otf",
            title="Font Verify",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )
        assert self._verify_signed_font(result.signed_bytes, test_certs)

    def test_flac_sign_verify_roundtrip(self, test_certs):
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs
        # Minimal FLAC: fLaC + STREAMINFO header + 34 bytes data
        flac_bytes = (
            b"fLaC"
            + bytes([0x80])
            + b"\x00\x00\x22"  # is_last=1, type=0, length=34
            + b"\x10\x00\x10\x00"
            + b"\x00\x00\x00\x00\x00\x00"
            + b"\x0a\xc4\x40\xf0\x00\x00\x00\x00"
            + b"\x00" * 16
        )
        result = sign_document(
            flac_bytes,
            "audio/flac",
            title="FLAC Verify",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )
        assert result.mime_type == "audio/flac"
        assert result.signed_size > result.original_size
        assert self._verify_signed_flac(result.signed_bytes, test_certs)

    def test_tampered_zip_fails_hash_check(self, test_certs):
        """Modify a file in the signed ZIP and verify hash mismatch."""
        from app.services.document_signing_service import sign_document
        from app.utils.zip_c2pa_embedder import compute_collection_hashes
        from app.utils.jumbf import parse_manifest_store

        private_key, cert_chain = test_certs
        result = sign_document(
            make_test_epub(),
            "application/epub+zip",
            title="Tamper Test",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )

        # Tamper: modify a file in the ZIP
        tampered_buf = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(result.signed_bytes)) as src:
            with zipfile.ZipFile(tampered_buf, "w") as dst:
                for info in src.infolist():
                    data = src.read(info.filename)
                    if info.filename == "chapter1.xhtml":
                        data = b"<html><body><p>TAMPERED</p></body></html>"
                    dst.writestr(info, data)
        tampered = tampered_buf.getvalue()

        # Re-compute hashes -- they should NOT match
        with zipfile.ZipFile(io.BytesIO(tampered)) as zf:
            manifest_bytes = zf.read("META-INF/content_credential.c2pa")

        store = parse_manifest_store(manifest_bytes)
        m = store["manifests"][0]
        collection_hash = cbor2.loads(m["assertions"]["c2pa.hash.collection.data"])
        stored_uris = {u["uri"]: u["hash"] for u in collection_hash["uris"]}

        file_hashes, _ = compute_collection_hashes(tampered)
        tampered_files = {fh["uri"]: fh["hash"] for fh in file_hashes}

        # chapter1.xhtml hash should differ
        assert tampered_files.get("chapter1.xhtml") != stored_uris.get("chapter1.xhtml"), "Tampered file should have different hash"


# ---- JXL C2PA embedder tests ----


def make_test_jxl() -> bytes:
    """Create a minimal JXL ISOBMFF container file."""
    result = bytearray()
    # JXL signature box
    result.extend(b"\x00\x00\x00\x0cJXL \r\n\x87\n")
    # ftyp box: brand='jxl ', minor=0, compat='jxl '
    ftyp_payload = b"jxl " + struct.pack(">I", 0) + b"jxl "
    result.extend(struct.pack(">I", 8 + len(ftyp_payload)) + b"ftyp" + ftyp_payload)
    # jxlc box: minimal codestream (signature + padding)
    codestream = b"\xff\x0a" + b"\x00" * 64
    result.extend(struct.pack(">I", 8 + len(codestream)) + b"jxlc" + codestream)
    return bytes(result)


class TestJxlEmbedder:
    def test_parse_jxl_boxes(self):
        from app.utils.jxl_c2pa_embedder import parse_jxl_boxes

        boxes = parse_jxl_boxes(make_test_jxl())
        types = [b["type"] for b in boxes]
        assert b"JXL " in types
        assert b"ftyp" in types
        assert b"jxlc" in types

    def test_parse_rejects_bare_codestream(self):
        from app.utils.jxl_c2pa_embedder import parse_jxl_boxes

        with pytest.raises(ValueError, match="bare codestream"):
            parse_jxl_boxes(b"\xff\x0a\x00\x00")

    def test_create_placeholder(self):
        from app.utils.jxl_c2pa_embedder import create_jxl_with_placeholder, parse_jxl_boxes

        jxl = make_test_jxl()
        result, offset, length = create_jxl_with_placeholder(jxl, 4096)
        assert len(result) > len(jxl)
        assert length == 4096
        # c2pa box should be present
        boxes = parse_jxl_boxes(result)
        c2pa_boxes = [b for b in boxes if b["type"] == b"c2pa"]
        assert len(c2pa_boxes) == 1
        # Placeholder should be zeroed
        assert result[offset : offset + length] == b"\x00" * 4096

    def test_replace_manifest(self):
        from app.utils.jxl_c2pa_embedder import (
            create_jxl_with_placeholder,
            replace_manifest_in_jxl,
        )

        jxl = make_test_jxl()
        jxl_ph, offset, length = create_jxl_with_placeholder(jxl, 1024)
        manifest = b"FAKE_JUMBF_MANIFEST" * 5
        result = replace_manifest_in_jxl(jxl_ph, manifest, offset, length)
        assert len(result) == len(jxl_ph)
        assert result[offset : offset + len(manifest)] == manifest

    def test_replace_manifest_too_large(self):
        from app.utils.jxl_c2pa_embedder import (
            create_jxl_with_placeholder,
            replace_manifest_in_jxl,
        )

        jxl = make_test_jxl()
        jxl_ph, offset, length = create_jxl_with_placeholder(jxl, 64)
        with pytest.raises(ValueError, match="exceeds placeholder"):
            replace_manifest_in_jxl(jxl_ph, b"\x00" * 128, offset, length)

    def test_hash_excludes_manifest_range(self):
        from app.utils.jxl_c2pa_embedder import (
            compute_jxl_hash,
            create_jxl_with_placeholder,
            replace_manifest_in_jxl,
        )

        jxl = make_test_jxl()
        jxl_ph, offset, length = create_jxl_with_placeholder(jxl, 1024)

        hash1 = compute_jxl_hash(jxl_ph, offset, length)

        # Replace manifest with different data -- hash should be identical
        manifest_a = b"MANIFEST_A" * 10
        manifest_b = b"MANIFEST_B" * 10
        signed_a = replace_manifest_in_jxl(jxl_ph, manifest_a, offset, length)
        signed_b = replace_manifest_in_jxl(jxl_ph, manifest_b, offset, length)

        hash_a = compute_jxl_hash(signed_a, offset, length)
        hash_b = compute_jxl_hash(signed_b, offset, length)

        assert hash_a == hash_b == hash1

    def test_existing_c2pa_box_removed(self):
        from app.utils.jxl_c2pa_embedder import create_jxl_with_placeholder, parse_jxl_boxes

        jxl = make_test_jxl()
        # First pass
        jxl_ph1, _, _ = create_jxl_with_placeholder(jxl, 512)
        # Second pass on already-placeholdered file
        jxl_ph2, _, _ = create_jxl_with_placeholder(jxl_ph1, 1024)
        boxes = parse_jxl_boxes(jxl_ph2)
        c2pa_count = sum(1 for b in boxes if b["type"] == b"c2pa")
        assert c2pa_count == 1, "Should have exactly one c2pa box after re-embedding"


class TestJxlSigning:
    def test_sign_jxl_roundtrip(self, test_certs):
        """Full E2E: sign a JXL file and verify the JUMBF manifest is structurally valid."""
        from app.services.document_signing_service import sign_jxl
        from app.utils.jumbf import parse_manifest_store
        from app.utils.jxl_c2pa_embedder import parse_jxl_boxes

        private_key, cert_chain = test_certs
        jxl = make_test_jxl()

        result = sign_jxl(
            jxl,
            title="C2PA Conformance Test -- JXL",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )

        assert result.mime_type == "image/jxl"
        assert result.signed_size > result.original_size
        assert result.manifest_label.startswith("urn:c2pa:")

        # Verify ISOBMFF structure still valid
        boxes = parse_jxl_boxes(result.signed_bytes)
        types = [b["type"] for b in boxes]
        assert b"JXL " in types
        assert b"ftyp" in types
        assert b"jxlc" in types
        assert b"c2pa" in types

        # Extract and parse manifest
        c2pa_box = next(b for b in boxes if b["type"] == b"c2pa")
        manifest_data = result.signed_bytes[c2pa_box["data_offset"] : c2pa_box["offset"] + c2pa_box["size"]]
        # Trim trailing zero padding
        manifest_data = manifest_data.rstrip(b"\x00")
        store = parse_manifest_store(manifest_data)

        assert len(store["manifests"]) == 1
        m = store["manifests"][0]
        assert m["label"] == result.manifest_label

        # Verify assertions present
        assert "c2pa.actions.v2" in m["assertions"]
        assert "c2pa.hash.data" in m["assertions"]
        assert "com.encypher.provenance" in m["assertions"]

        # Verify claim
        claim = cbor2.loads(m["claim_cbor"])
        assert "created_assertions" in claim

    def test_sign_jxl_via_dispatcher(self, test_certs):
        """Verify sign_document routes image/jxl correctly."""
        from app.services.document_signing_service import sign_document

        private_key, cert_chain = test_certs
        result = sign_document(
            make_test_jxl(),
            "image/jxl",
            title="JXL Dispatcher Test",
            private_key_pem=private_key,
            cert_chain_pem=cert_chain,
        )
        assert result.mime_type == "image/jxl"
        assert result.signed_size > result.original_size
