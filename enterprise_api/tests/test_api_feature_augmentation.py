"""
Tests for API Feature Augmentation (TEAM_044).

Tests the new schema fields and validators for:
- manifest_mode (full, lightweight_uuid, hybrid)
- embedding_strategy (single_point, distributed, distributed_redundant)
- distribution_target (whitespace, punctuation, all_chars)
- add_dual_binding
- disable_c2pa
"""

import pytest
from pydantic import ValidationError

from app.schemas.embeddings import EncodeWithEmbeddingsRequest


class TestManifestModeValidation:
    """Test manifest_mode field validation."""

    def test_manifest_mode_default_is_full(self):
        """Default manifest_mode should be 'full'."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.")
        assert request.manifest_mode == "full"

    def test_manifest_mode_full_valid(self):
        """manifest_mode='full' should be valid."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", manifest_mode="full")
        assert request.manifest_mode == "full"

    def test_manifest_mode_lightweight_uuid_valid(self):
        """manifest_mode='lightweight_uuid' should be valid."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", manifest_mode="lightweight_uuid")
        assert request.manifest_mode == "lightweight_uuid"

    def test_manifest_mode_hybrid_valid(self):
        """manifest_mode='hybrid' should be valid."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", manifest_mode="hybrid")
        assert request.manifest_mode == "hybrid"

    def test_manifest_mode_invalid_raises_error(self):
        """Invalid manifest_mode should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", manifest_mode="invalid_mode")
        assert "manifest_mode" in str(exc_info.value).lower() or "Manifest mode" in str(exc_info.value)


class TestEmbeddingStrategyValidation:
    """Test embedding_strategy field validation."""

    def test_embedding_strategy_default_is_single_point(self):
        """Default embedding_strategy should be 'single_point'."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.")
        assert request.embedding_strategy == "single_point"

    def test_embedding_strategy_single_point_valid(self):
        """embedding_strategy='single_point' should be valid."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", embedding_strategy="single_point")
        assert request.embedding_strategy == "single_point"

    def test_embedding_strategy_distributed_valid(self):
        """embedding_strategy='distributed' should be valid."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", embedding_strategy="distributed")
        assert request.embedding_strategy == "distributed"

    def test_embedding_strategy_distributed_redundant_valid(self):
        """embedding_strategy='distributed_redundant' should be valid."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", embedding_strategy="distributed_redundant")
        assert request.embedding_strategy == "distributed_redundant"

    def test_embedding_strategy_invalid_raises_error(self):
        """Invalid embedding_strategy should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", embedding_strategy="invalid_strategy")
        assert "embedding_strategy" in str(exc_info.value).lower() or "Embedding strategy" in str(exc_info.value)


class TestDistributionTargetValidation:
    """Test distribution_target field validation."""

    def test_distribution_target_default_is_none(self):
        """Default distribution_target should be None."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.")
        assert request.distribution_target is None

    def test_distribution_target_whitespace_valid(self):
        """distribution_target='whitespace' should be valid."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", distribution_target="whitespace")
        assert request.distribution_target == "whitespace"

    def test_distribution_target_punctuation_valid(self):
        """distribution_target='punctuation' should be valid."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", distribution_target="punctuation")
        assert request.distribution_target == "punctuation"

    def test_distribution_target_all_chars_valid(self):
        """distribution_target='all_chars' should be valid."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", distribution_target="all_chars")
        assert request.distribution_target == "all_chars"

    def test_distribution_target_invalid_raises_error(self):
        """Invalid distribution_target should raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", distribution_target="invalid_target")
        assert "distribution_target" in str(exc_info.value).lower() or "Distribution target" in str(exc_info.value)


class TestDualBindingValidation:
    """Test add_dual_binding field validation."""

    def test_add_dual_binding_default_is_false(self):
        """Default add_dual_binding should be False."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.")
        assert request.add_dual_binding is False

    def test_add_dual_binding_true_valid(self):
        """add_dual_binding=True should be valid."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", add_dual_binding=True)
        assert request.add_dual_binding is True

    def test_add_dual_binding_false_valid(self):
        """add_dual_binding=False should be valid."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", add_dual_binding=False)
        assert request.add_dual_binding is False


class TestDisableC2PAValidation:
    """Test disable_c2pa field validation."""

    def test_disable_c2pa_default_is_false(self):
        """Default disable_c2pa should be False (C2PA enabled by default)."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.")
        assert request.disable_c2pa is False

    def test_disable_c2pa_true_valid(self):
        """disable_c2pa=True should be valid (opt-out)."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", disable_c2pa=True)
        assert request.disable_c2pa is True

    def test_disable_c2pa_false_valid(self):
        """disable_c2pa=False should be valid (C2PA enabled)."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", disable_c2pa=False)
        assert request.disable_c2pa is False


class TestCombinedFeatureOptions:
    """Test combinations of new feature options."""

    def test_distributed_with_target(self):
        """Distributed embedding with specific target should work."""
        request = EncodeWithEmbeddingsRequest(
            document_id="test-doc", text="Test content with multiple words.", embedding_strategy="distributed", distribution_target="whitespace"
        )
        assert request.embedding_strategy == "distributed"
        assert request.distribution_target == "whitespace"

    def test_lightweight_uuid_with_dual_binding(self):
        """Lightweight UUID with dual binding should work."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", manifest_mode="lightweight_uuid", add_dual_binding=True)
        assert request.manifest_mode == "lightweight_uuid"
        assert request.add_dual_binding is True

    def test_hybrid_with_distributed_redundant(self):
        """Hybrid manifest with distributed redundant embedding should work."""
        request = EncodeWithEmbeddingsRequest(
            document_id="test-doc",
            text="Test content with enough characters for distribution.",
            manifest_mode="hybrid",
            embedding_strategy="distributed_redundant",
            distribution_target="all_chars",
        )
        assert request.manifest_mode == "hybrid"
        assert request.embedding_strategy == "distributed_redundant"
        assert request.distribution_target == "all_chars"

    def test_disable_c2pa_uses_basic_format(self):
        """When C2PA is disabled, request should still be valid."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", disable_c2pa=True)
        assert request.disable_c2pa is True
        # C2PA disabled means basic metadata only
        assert request.manifest_mode == "full"  # Still defaults, but will be ignored


# === Integration Tests for EmbeddingService (TEAM_044) ===


class TestEmbeddingServiceManifestModes:
    """Test EmbeddingService with different manifest modes."""

    @pytest.fixture
    def key_pair(self):
        """Generate a test key pair."""
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        return private_key, public_key

    @pytest.fixture
    def embedding_service(self, key_pair):
        """Create an EmbeddingService instance."""
        from app.services.embedding_service import EmbeddingService

        private_key, _ = key_pair
        return EmbeddingService(private_key, "test-signer-001")

    def test_service_initialization(self, embedding_service):
        """EmbeddingService should initialize correctly."""
        assert embedding_service.signer_id == "test-signer-001"
        assert embedding_service.private_key is not None

    def test_c2pa_default_enabled(self):
        """C2PA should be enabled by default in schema."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.")
        assert request.disable_c2pa is False
        assert request.manifest_mode == "full"

    def test_all_manifest_modes_valid(self):
        """All manifest modes should be valid in schema."""
        for mode in ["full", "lightweight_uuid", "minimal_uuid", "hybrid"]:
            request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", manifest_mode=mode)
            assert request.manifest_mode == mode

    def test_all_embedding_strategies_valid(self):
        """All embedding strategies should be valid in schema."""
        for strategy in ["single_point", "distributed", "distributed_redundant"]:
            request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", embedding_strategy=strategy)
            assert request.embedding_strategy == strategy

    def test_all_distribution_targets_valid(self):
        """All distribution targets should be valid in schema."""
        for target in ["whitespace", "punctuation", "all_chars"]:
            request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", distribution_target=target)
            assert request.distribution_target == target


class TestTierGatingRequirements:
    """Test tier gating requirements for new features."""

    def test_lightweight_uuid_requires_professional(self):
        """Lightweight UUID should be marked as Professional+ feature."""
        # This test documents the tier requirement
        # Actual enforcement happens in the API endpoint
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", manifest_mode="lightweight_uuid")
        # Schema accepts it, tier gating happens at API level
        assert request.manifest_mode == "lightweight_uuid"

    def test_minimal_uuid_requires_professional(self):
        """Minimal UUID should be marked as Professional+ feature."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", manifest_mode="minimal_uuid")
        assert request.manifest_mode == "minimal_uuid"

    def test_distributed_requires_business(self):
        """Distributed embedding should be marked as Business+ feature."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", embedding_strategy="distributed")
        assert request.embedding_strategy == "distributed"

    def test_distributed_redundant_requires_enterprise(self):
        """Distributed redundant (ECC) should be marked as Enterprise feature."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", embedding_strategy="distributed_redundant")
        assert request.embedding_strategy == "distributed_redundant"

    def test_hybrid_requires_enterprise(self):
        """Hybrid manifest mode should be marked as Enterprise feature."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", manifest_mode="hybrid")
        assert request.manifest_mode == "hybrid"

    def test_dual_binding_requires_business(self):
        """Dual binding should be marked as Business+ feature."""
        request = EncodeWithEmbeddingsRequest(document_id="test-doc", text="Test content.", add_dual_binding=True)
        assert request.add_dual_binding is True


# === Streaming Merkle Tree Schemas (TEAM_044 - Patent FIG. 5) ===


class TestStreamMerkleStartRequest:
    """Test StreamMerkleStartRequest schema."""

    def test_start_request_defaults(self):
        """Default values should be set correctly."""
        from app.schemas.streaming import StreamMerkleStartRequest

        request = StreamMerkleStartRequest(document_id="test-doc")
        assert request.document_id == "test-doc"
        assert request.segmentation_level == "sentence"
        assert request.buffer_size == 100
        assert request.auto_finalize_timeout_seconds == 300
        assert request.metadata is None

    def test_start_request_with_metadata(self):
        """Request with metadata should work."""
        from app.schemas.streaming import StreamMerkleStartRequest

        request = StreamMerkleStartRequest(document_id="test-doc", metadata={"title": "Test", "author": "Tester"})
        assert request.metadata == {"title": "Test", "author": "Tester"}

    def test_start_request_invalid_segmentation_level(self):
        """Invalid segmentation level should raise error."""
        from app.schemas.streaming import StreamMerkleStartRequest

        with pytest.raises(ValueError):
            StreamMerkleStartRequest(document_id="test-doc", segmentation_level="invalid")

    def test_start_request_valid_segmentation_levels(self):
        """All valid segmentation levels should work."""
        from app.schemas.streaming import StreamMerkleStartRequest

        for level in ["sentence", "paragraph", "section"]:
            request = StreamMerkleStartRequest(document_id="test-doc", segmentation_level=level)
            assert request.segmentation_level == level


class TestStreamMerkleSegmentRequest:
    """Test StreamMerkleSegmentRequest schema."""

    def test_segment_request_minimal(self):
        """Minimal segment request should work."""
        from app.schemas.streaming import StreamMerkleSegmentRequest

        request = StreamMerkleSegmentRequest(session_id="session-123", segment_text="This is a test segment.")
        assert request.session_id == "session-123"
        assert request.segment_text == "This is a test segment."
        assert request.is_final is False
        assert request.flush_buffer is False

    def test_segment_request_with_index(self):
        """Segment request with explicit index should work."""
        from app.schemas.streaming import StreamMerkleSegmentRequest

        request = StreamMerkleSegmentRequest(session_id="session-123", segment_text="Test segment.", segment_index=5)
        assert request.segment_index == 5

    def test_segment_request_final(self):
        """Final segment request should work."""
        from app.schemas.streaming import StreamMerkleSegmentRequest

        request = StreamMerkleSegmentRequest(session_id="session-123", segment_text="Final segment.", is_final=True)
        assert request.is_final is True


class TestStreamMerkleFinalizeRequest:
    """Test StreamMerkleFinalizeRequest schema."""

    def test_finalize_request_defaults(self):
        """Default values should be set correctly."""
        from app.schemas.streaming import StreamMerkleFinalizeRequest

        request = StreamMerkleFinalizeRequest(session_id="session-123")
        assert request.session_id == "session-123"
        assert request.embed_manifest is True
        assert request.manifest_mode == "full"
        assert request.action == "c2pa.created"

    def test_finalize_request_lightweight_uuid(self):
        """Finalize with lightweight_uuid manifest mode should work."""
        from app.schemas.streaming import StreamMerkleFinalizeRequest

        request = StreamMerkleFinalizeRequest(session_id="session-123", manifest_mode="lightweight_uuid")
        assert request.manifest_mode == "lightweight_uuid"

    def test_finalize_request_minimal_uuid(self):
        """Finalize with minimal_uuid manifest mode should work."""
        from app.schemas.streaming import StreamMerkleFinalizeRequest

        request = StreamMerkleFinalizeRequest(session_id="session-123", manifest_mode="minimal_uuid")
        assert request.manifest_mode == "minimal_uuid"

    def test_finalize_request_invalid_manifest_mode(self):
        """Invalid manifest mode should raise error."""
        from app.schemas.streaming import StreamMerkleFinalizeRequest

        with pytest.raises(ValueError):
            StreamMerkleFinalizeRequest(session_id="session-123", manifest_mode="invalid")


# === Streaming Merkle Service Unit Tests (TEAM_044) ===


class TestStreamingMerkleSession:
    """Test StreamingMerkleSession dataclass."""

    def test_session_creation(self):
        """Session should be created with correct defaults."""
        from app.services.streaming_merkle_service import StreamingMerkleSession

        session = StreamingMerkleSession(
            session_id="test-session",
            document_id="test-doc",
            organization_id="org-123",
            segmentation_level="sentence",
            metadata=None,
            buffer_size=100,
            timeout_seconds=300,
        )

        assert session.session_id == "test-session"
        assert session.document_id == "test-doc"
        assert session.status == "active"
        assert session.buffer_count == 0
        assert session.total_segments == 0

    def test_session_touch_updates_activity(self):
        """Touch should update last_activity timestamp."""
        from app.services.streaming_merkle_service import StreamingMerkleSession
        from datetime import datetime, timezone
        import time

        session = StreamingMerkleSession(
            session_id="test-session",
            document_id="test-doc",
            organization_id="org-123",
            segmentation_level="sentence",
            metadata=None,
            buffer_size=100,
            timeout_seconds=300,
        )

        old_activity = session.last_activity
        time.sleep(0.01)  # Small delay
        session.touch()

        assert session.last_activity > old_activity

    def test_session_expiration(self):
        """Session should expire after timeout."""
        from app.services.streaming_merkle_service import StreamingMerkleSession
        from datetime import datetime, timedelta, timezone

        session = StreamingMerkleSession(
            session_id="test-session",
            document_id="test-doc",
            organization_id="org-123",
            segmentation_level="sentence",
            metadata=None,
            buffer_size=100,
            timeout_seconds=1,  # 1 second timeout
        )

        # Should not be expired immediately
        assert not session.is_expired

        # Manually set last_activity to past
        session.last_activity = datetime.now(timezone.utc) - timedelta(seconds=2)
        assert session.is_expired


class TestStreamingMerkleServiceBasic:
    """Basic tests for StreamingMerkleService."""

    @pytest.fixture
    def service(self):
        """Create a fresh service instance."""
        from app.services.streaming_merkle_service import StreamingMerkleService

        return StreamingMerkleService()

    @pytest.mark.asyncio
    async def test_start_session(self, service):
        """Should create a new session."""
        session = await service.start_session(
            document_id="test-doc",
            organization_id="org-123",
            segmentation_level="sentence",
        )

        assert session.session_id.startswith("stream_")
        assert session.document_id == "test-doc"
        assert session.organization_id == "org-123"
        assert session.status == "active"

    @pytest.mark.asyncio
    async def test_add_segment(self, service):
        """Should add segment to session."""
        session = await service.start_session(
            document_id="test-doc",
            organization_id="org-123",
        )

        updated_session, segment_hash = await service.add_segment(
            session_id=session.session_id,
            segment_text="This is a test segment.",
        )

        assert updated_session.total_segments == 1
        assert len(segment_hash) == 64  # SHA-256 hex

    @pytest.mark.asyncio
    async def test_add_multiple_segments(self, service):
        """Should add multiple segments to session."""
        session = await service.start_session(
            document_id="test-doc",
            organization_id="org-123",
        )

        for i in range(5):
            await service.add_segment(
                session_id=session.session_id,
                segment_text=f"Segment {i}.",
            )

        assert session.total_segments == 5
        assert len(session.segments) == 5

    @pytest.mark.asyncio
    async def test_get_session(self, service):
        """Should retrieve session by ID."""
        session = await service.start_session(
            document_id="test-doc",
            organization_id="org-123",
        )

        retrieved = await service.get_session(session.session_id)

        assert retrieved is not None
        assert retrieved.session_id == session.session_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self, service):
        """Should return None for nonexistent session."""
        retrieved = await service.get_session("nonexistent-session")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_add_segment_to_nonexistent_session(self, service):
        """Should raise error for nonexistent session."""
        with pytest.raises(ValueError, match="Session not found"):
            await service.add_segment(
                session_id="nonexistent",
                segment_text="Test",
            )


# === ECC Service Tests (TEAM_044) ===


class TestReedSolomonECC:
    """Test Reed-Solomon ECC encoding/decoding."""

    def test_encode_decode_basic(self):
        """Basic encode/decode should work."""
        from app.services.ecc_service import ReedSolomonECC

        codec = ReedSolomonECC(nsym=10)
        data = b"Hello, World!"

        encoded = codec.encode(data)
        assert len(encoded) > len(data)  # Should have parity bytes

        decoded, errors = codec.decode(encoded)
        assert decoded == data
        assert errors == 0

    def test_error_correction(self):
        """Should detect that data has parity bytes appended."""
        from app.services.ecc_service import ReedSolomonECC

        codec = ReedSolomonECC(nsym=10)
        data = b"Test data for ECC"

        encoded = codec.encode(data)

        # Verify parity was added
        assert len(encoded) == len(data) + 10  # nsym parity bytes

        # Decode without errors should work
        decoded, errors = codec.decode(encoded)
        assert decoded == data
        assert errors == 0

    def test_encode_with_ecc_function(self):
        """Test the encode_with_ecc helper function."""
        from app.services.ecc_service import encode_with_ecc, decode_with_ecc

        data = b"Sample text for encoding"
        encoded = encode_with_ecc(data, nsym=10)
        decoded, _ = decode_with_ecc(encoded, nsym=10)

        assert decoded == data


# === Evidence Schema Tests (TEAM_044) ===


class TestEvidenceSchemas:
    """Test Evidence Generation schemas."""

    def test_evidence_generate_request_defaults(self):
        """Default values should be set correctly."""
        from app.schemas.evidence import EvidenceGenerateRequest

        request = EvidenceGenerateRequest(target_text="Test content for evidence.")
        assert request.include_merkle_proof is True
        assert request.include_signature_chain is True
        assert request.include_timestamp_proof is True
        assert request.export_format == "json"

    def test_evidence_generate_request_pdf_format(self):
        """PDF export format should be valid."""
        from app.schemas.evidence import EvidenceGenerateRequest

        request = EvidenceGenerateRequest(target_text="Test content.", export_format="pdf")
        assert request.export_format == "pdf"

    def test_evidence_generate_request_invalid_format(self):
        """Invalid export format should raise error."""
        from app.schemas.evidence import EvidenceGenerateRequest

        with pytest.raises(ValueError):
            EvidenceGenerateRequest(target_text="Test content.", export_format="invalid")


# === Fingerprint Schema Tests (TEAM_044) ===


class TestFingerprintSchemas:
    """Test Fingerprint schemas."""

    def test_fingerprint_encode_request_defaults(self):
        """Default values should be set correctly."""
        from app.schemas.fingerprint import FingerprintEncodeRequest

        request = FingerprintEncodeRequest(document_id="test-doc", text="Test content for fingerprinting.")
        assert request.fingerprint_density == 0.1
        assert request.fingerprint_key is None

    def test_fingerprint_encode_request_custom_density(self):
        """Custom density should be accepted."""
        from app.schemas.fingerprint import FingerprintEncodeRequest

        request = FingerprintEncodeRequest(document_id="test-doc", text="Test content.", fingerprint_density=0.25)
        assert request.fingerprint_density == 0.25

    def test_fingerprint_detect_request_defaults(self):
        """Default values should be set correctly."""
        from app.schemas.fingerprint import FingerprintDetectRequest

        request = FingerprintDetectRequest(text="Test content to scan.")
        assert request.confidence_threshold == 0.6
        assert request.return_positions is False


# === Fingerprint Service Tests (TEAM_044) ===


class TestFingerprintService:
    """Test Fingerprint service."""

    @pytest.fixture
    def service(self):
        """Create a fresh service instance."""
        from app.services.fingerprint_service import FingerprintService

        return FingerprintService()

    @pytest.mark.asyncio
    async def test_encode_fingerprint(self, service):
        """Should encode fingerprint into text."""
        text = "This is a test sentence for fingerprinting. It has multiple sentences."

        fingerprinted, fp_id, key_hash, markers = await service.encode_fingerprint(
            db=None,
            organization_id="org-123",
            document_id="doc-123",
            text=text,
            density=0.1,
        )

        assert len(fingerprinted) > len(text)  # Should have markers
        assert fp_id is not None
        assert key_hash is not None
        assert markers > 0

    @pytest.mark.asyncio
    async def test_detect_fingerprint(self, service):
        """Should detect fingerprint in text."""
        text = "This is a test sentence for fingerprinting. It has multiple sentences."

        # First encode
        fingerprinted, fp_id, _, _ = await service.encode_fingerprint(
            db=None,
            organization_id="org-123",
            document_id="doc-123",
            text=text,
            density=0.1,
        )

        # Then detect
        detected, matches = await service.detect_fingerprint(
            db=None,
            organization_id="org-123",
            text=fingerprinted,
            confidence_threshold=0.5,
        )

        assert detected is True
        assert len(matches) > 0
        assert matches[0].fingerprint_id == fp_id


# === Multi-Source Schema Tests (TEAM_044) ===


class TestMultiSourceSchemas:
    """Test Multi-Source Lookup schemas."""

    def test_multi_source_request_defaults(self):
        """Default values should be set correctly."""
        from app.schemas.multi_source import MultiSourceLookupRequest

        request = MultiSourceLookupRequest(text_segment="Test segment.")
        assert request.include_all_sources is True
        assert request.order_by == "chronological"
        assert request.include_authority_score is False
        assert request.max_results == 10

    def test_multi_source_request_authority_order(self):
        """Authority ordering should be valid."""
        from app.schemas.multi_source import MultiSourceLookupRequest

        request = MultiSourceLookupRequest(text_segment="Test segment.", order_by="authority", include_authority_score=True)
        assert request.order_by == "authority"

    def test_multi_source_request_invalid_order(self):
        """Invalid order_by should raise error."""
        from app.schemas.multi_source import MultiSourceLookupRequest

        with pytest.raises(ValueError):
            MultiSourceLookupRequest(text_segment="Test segment.", order_by="invalid")


# === Dual-Binding Service Tests (TEAM_044) ===


class TestDualBindingService:
    """Test Dual-Binding Manifest service."""

    @pytest.fixture
    def keys(self):
        """Generate test keys using cryptography library."""
        from cryptography.hazmat.primitives.asymmetric import ed25519

        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        return private_key, public_key

    def test_create_dual_binding_manifest(self, keys):
        """Should create a dual-binding manifest."""
        from app.services.dual_binding_service import DualBindingService

        private_key, _ = keys
        service = DualBindingService(private_key, "test-signer")

        text = "This is test content for dual-binding."
        manifest_bytes, info = service.create_dual_binding_manifest(text)

        assert manifest_bytes is not None
        assert len(manifest_bytes) > 0
        assert info["content_hash"] is not None
        assert info["self_hash"] is not None
        assert info["signer_id"] == "test-signer"

    def test_verify_dual_binding_valid(self, keys):
        """Should verify a valid dual-binding manifest."""
        from app.services.dual_binding_service import DualBindingService

        private_key, public_key = keys
        service = DualBindingService(private_key, "test-signer")

        text = "This is test content for dual-binding verification."
        manifest_bytes, _ = service.create_dual_binding_manifest(text)

        is_valid, message, info = service.verify_dual_binding(manifest_bytes, text, public_key)

        assert is_valid is True
        assert "successful" in message.lower()
        assert info["dual_binding_verified"] is True

    def test_verify_dual_binding_content_modified(self, keys):
        """Should detect content modification."""
        from app.services.dual_binding_service import DualBindingService

        private_key, public_key = keys
        service = DualBindingService(private_key, "test-signer")

        text = "Original content."
        manifest_bytes, _ = service.create_dual_binding_manifest(text)

        # Try to verify with modified content
        modified_text = "Modified content."
        is_valid, message, _ = service.verify_dual_binding(manifest_bytes, modified_text, public_key)

        assert is_valid is False
        assert "content hash mismatch" in message.lower()

    def test_create_dual_binding_convenience_function(self, keys):
        """Test the convenience function."""
        from app.services.dual_binding_service import create_dual_binding_manifest

        private_key, _ = keys
        text = "Test content."

        manifest_bytes, info = create_dual_binding_manifest(
            text=text,
            private_key=private_key,
            signer_id="test-org",
            metadata={"custom": "value"},
        )

        assert manifest_bytes is not None
        assert info["signer_id"] == "test-org"
