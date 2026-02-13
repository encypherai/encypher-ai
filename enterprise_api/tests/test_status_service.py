"""
Tests for the StatusService (Bitstring Status Lists).

TEAM_002: Tests for per-document revocation at internet scale.
"""

import base64
import gzip
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.status_list import (
    BITS_PER_LIST,
    BYTES_PER_LIST,
    RevocationReason,
)
from app.services.status_service import StatusService


class TestStatusServiceAllocation:
    """Tests for status index allocation during signing."""

    @pytest.mark.asyncio
    async def test_allocate_status_index_creates_new_list(self):
        """First allocation for an org should create a new list."""
        service = StatusService()
        db = AsyncMock()

        # Mock: no existing lists
        db.execute.return_value.scalar_one_or_none.return_value = None
        db.execute.return_value.scalar.return_value = None  # No max index

        # Mock the add and flush
        db.add = MagicMock()
        db.flush = AsyncMock()

        list_index, bit_index, url = await service.allocate_status_index(
            db=db,
            organization_id="org_test",
            document_id="doc_123",
        )

        assert list_index == 0
        assert bit_index == 0
        assert url.startswith("https://verify.encypherai.com/status/v1/lists/")
        assert len(url.split("/lists/")[1]) == 36  # UUID format

    @pytest.mark.asyncio
    async def test_allocate_status_index_uses_existing_list(self):
        """Allocation should use existing non-full list."""
        service = StatusService()
        db = AsyncMock()

        # Mock: existing list with space
        existing_metadata = MagicMock()
        existing_metadata.list_index = 0
        existing_metadata.next_bit_index = 42
        existing_metadata.is_full = False

        db.execute.return_value.scalar_one_or_none.return_value = existing_metadata
        db.add = MagicMock()
        db.flush = AsyncMock()

        list_index, bit_index, url = await service.allocate_status_index(
            db=db,
            organization_id="org_test",
            document_id="doc_456",
        )

        assert list_index == 0
        assert bit_index == 42
        assert existing_metadata.next_bit_index == 43


class TestStatusServiceRevocation:
    """Tests for document revocation and reinstatement."""

    @pytest.mark.asyncio
    async def test_revoke_document_success(self):
        """Revoking a document should update the entry."""
        service = StatusService()
        db = AsyncMock()

        # Mock: existing entry
        entry = MagicMock()
        entry.revoked = False
        entry.list_index = 0

        db.execute.return_value.scalar_one_or_none.return_value = entry
        db.flush = AsyncMock()

        result = await service.revoke_document(
            db=db,
            organization_id="org_test",
            document_id="doc_123",
            reason=RevocationReason.FACTUAL_ERROR,
            reason_detail="Incorrect statistics",
            revoked_by="user_abc",
        )

        assert result.revoked is True
        assert result.revoked_reason == "factual_error"
        assert result.revoked_reason_detail == "Incorrect statistics"
        assert result.revoked_by == "user_abc"

    @pytest.mark.asyncio
    async def test_revoke_document_not_found(self):
        """Revoking non-existent document should raise ValueError."""
        service = StatusService()
        db = AsyncMock()

        db.execute.return_value.scalar_one_or_none.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await service.revoke_document(
                db=db,
                organization_id="org_test",
                document_id="doc_nonexistent",
                reason=RevocationReason.OTHER,
            )

    @pytest.mark.asyncio
    async def test_reinstate_document_success(self):
        """Reinstating a revoked document should clear revocation."""
        service = StatusService()
        db = AsyncMock()

        # Mock: revoked entry
        entry = MagicMock()
        entry.revoked = True
        entry.list_index = 0

        db.execute.return_value.scalar_one_or_none.return_value = entry
        db.flush = AsyncMock()

        result = await service.reinstate_document(
            db=db,
            organization_id="org_test",
            document_id="doc_123",
            reinstated_by="user_abc",
        )

        assert result.revoked is False
        assert result.reinstated_by == "user_abc"


class TestStatusServiceBitstring:
    """Tests for bitstring generation and checking."""

    @pytest.mark.asyncio
    async def test_generate_status_list_empty(self):
        """Empty list should generate all-zeros bitstring."""
        service = StatusService()
        db = AsyncMock()

        # Mock: no entries
        db.execute.return_value.all.return_value = []
        db.flush = AsyncMock()

        credential = await service.generate_status_list(
            db=db,
            organization_id="org_test",
            list_index=0,
        )

        assert credential["type"] == ["VerifiableCredential", "StatusList2021Credential"]
        assert credential["credentialSubject"]["type"] == "StatusList2021"
        assert credential["credentialSubject"]["statusPurpose"] == "revocation"

        # Decode and verify all zeros
        encoded = credential["credentialSubject"]["encodedList"]
        compressed = base64.b64decode(encoded)
        bitstring = gzip.decompress(compressed)

        assert len(bitstring) == BYTES_PER_LIST
        assert all(b == 0 for b in bitstring)

    @pytest.mark.asyncio
    async def test_generate_status_list_with_revocations(self):
        """List with revocations should have correct bits set."""
        service = StatusService()
        db = AsyncMock()

        # Mock: some revoked entries
        db.execute.return_value.all.return_value = [
            (0, True),  # bit 0 revoked
            (1, False),  # bit 1 active
            (7, True),  # bit 7 revoked
            (8, True),  # bit 8 revoked (second byte)
        ]
        db.flush = AsyncMock()

        credential = await service.generate_status_list(
            db=db,
            organization_id="org_test",
            list_index=0,
        )

        # Decode and verify bits
        encoded = credential["credentialSubject"]["encodedList"]
        compressed = base64.b64decode(encoded)
        bitstring = gzip.decompress(compressed)

        # Check specific bits (MSB first per W3C spec)
        # Bit 0 is at position 7 of byte 0
        assert bitstring[0] & 0b10000000  # bit 0 set
        assert not (bitstring[0] & 0b01000000)  # bit 1 not set
        assert bitstring[0] & 0b00000001  # bit 7 set
        assert bitstring[1] & 0b10000000  # bit 8 set

    @pytest.mark.asyncio
    async def test_check_revocation_active(self):
        """Active document should return False."""
        service = StatusService()

        # Pre-populate cache with empty bitstring
        url = "https://verify.encypherai.com/status/v1/lists/00000000-0000-0000-0000-000000000001"
        service._list_cache[url] = (bytes(BYTES_PER_LIST), float("inf"))

        is_revoked, error = await service.check_revocation(
            status_list_url=url,
            bit_index=42,
        )

        assert is_revoked is False
        assert error is None

    @pytest.mark.asyncio
    async def test_check_revocation_revoked(self):
        """Revoked document should return True."""
        service = StatusService()

        # Create bitstring with bit 42 set
        bitstring = bytearray(BYTES_PER_LIST)
        byte_index = 42 // 8  # = 5
        bit_position = 7 - (42 % 8)  # = 7 - 2 = 5
        bitstring[byte_index] |= 1 << bit_position

        url = "https://verify.encypherai.com/status/v1/lists/00000000-0000-0000-0000-000000000001"
        service._list_cache[url] = (bytes(bitstring), float("inf"))

        is_revoked, error = await service.check_revocation(
            status_list_url=url,
            bit_index=42,
        )

        assert is_revoked is True
        assert error is None

    @pytest.mark.asyncio
    async def test_check_revocation_failure_returns_unknown(self):
        service = StatusService()

        with patch.object(service, "_get_status_list", new=AsyncMock(side_effect=ValueError("boom"))):
            is_revoked, error = await service.check_revocation(
                status_list_url="https://verify.encypherai.com/status/v1/lists/00000000-0000-0000-0000-000000000001",
                bit_index=42,
            )

        assert is_revoked is None
        assert isinstance(error, str)


class TestStatusServiceCache:
    """Tests for status list caching."""

    def test_invalidate_cache_specific(self):
        """Invalidating specific URL should only clear that entry."""
        service = StatusService()

        service._list_cache["url1"] = (b"data1", 1000)
        service._list_cache["url2"] = (b"data2", 1000)

        service.invalidate_cache("url1")

        assert "url1" not in service._list_cache
        assert "url2" in service._list_cache

    def test_invalidate_cache_all(self):
        """Invalidating without URL should clear all entries."""
        service = StatusService()

        service._list_cache["url1"] = (b"data1", 1000)
        service._list_cache["url2"] = (b"data2", 1000)

        service.invalidate_cache()

        assert len(service._list_cache) == 0


class TestBitstringOperations:
    """Tests for low-level bitstring operations."""

    def test_bit_indexing_msb_first(self):
        """Verify MSB-first bit indexing per W3C spec."""
        # W3C StatusList2021 uses MSB-first ordering
        # Bit 0 is the most significant bit of byte 0

        bitstring = bytearray(2)

        # Set bit 0 (MSB of byte 0)
        bit_index = 0
        byte_index = bit_index // 8
        bit_position = 7 - (bit_index % 8)
        bitstring[byte_index] |= 1 << bit_position

        assert bitstring[0] == 0b10000000

        # Set bit 7 (LSB of byte 0)
        bit_index = 7
        byte_index = bit_index // 8
        bit_position = 7 - (bit_index % 8)
        bitstring[byte_index] |= 1 << bit_position

        assert bitstring[0] == 0b10000001

        # Set bit 8 (MSB of byte 1)
        bit_index = 8
        byte_index = bit_index // 8
        bit_position = 7 - (bit_index % 8)
        bitstring[byte_index] |= 1 << bit_position

        assert bitstring[1] == 0b10000000

    def test_capacity_constants(self):
        """Verify capacity constants are correct."""
        assert BITS_PER_LIST == 131072
        assert BYTES_PER_LIST == 16384
        assert BITS_PER_LIST == BYTES_PER_LIST * 8


class TestStatusServiceFetch:
    """Tests for fetching and decoding status lists from CDN URLs."""

    @pytest.mark.asyncio
    async def test_get_status_list_fetches_and_decodes_encoded_list(self):
        service = StatusService(cache_ttl_seconds=300)

        # Create bitstring with bit 42 set
        bitstring = bytearray(BYTES_PER_LIST)
        byte_index = 42 // 8
        bit_position = 7 - (42 % 8)
        bitstring[byte_index] |= 1 << bit_position

        encoded = base64.b64encode(gzip.compress(bytes(bitstring), compresslevel=9)).decode("ascii")
        credential = {
            "credentialSubject": {
                "encodedList": encoded,
            }
        }

        url = "https://verify.encypherai.com/status/v1/lists/00000000-0000-0000-0000-000000000001"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = credential
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        with patch("app.services.status_service.httpx.AsyncClient", return_value=mock_client):
            fetched = await service._get_status_list(url)

        assert len(fetched) == BYTES_PER_LIST
        assert fetched[byte_index] & (1 << bit_position)

    @pytest.mark.asyncio
    async def test_get_status_list_rejects_untrusted_url(self):
        service = StatusService(cache_ttl_seconds=300)
        with pytest.raises(ValueError, match="Untrusted status list url"):
            await service._get_status_list("https://example.com/status/list")
