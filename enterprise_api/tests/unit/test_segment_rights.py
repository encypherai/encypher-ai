"""
Unit tests for segment-level rights.

Validates schema, tier gating, and assertion generation for the
segment_rights feature (Enterprise-only).
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.core.tier_config import get_tier_features
from app.schemas.sign_schemas import (
    RightsMetadata,
    SegmentRightsMapping,
    SignOptions,
)


# ---------------------------------------------------------------------------
# 1. SegmentRightsMapping schema validation
# ---------------------------------------------------------------------------


class TestSegmentRightsMappingSchema:
    """SegmentRightsMapping pairs segment indices with a RightsMetadata."""

    def test_valid_mapping(self) -> None:
        mapping = SegmentRightsMapping(
            segment_indices=[0, 1, 2],
            rights=RightsMetadata(
                copyright_holder="NPR",
                license_url="https://npr.org/terms",
                usage_terms="All rights reserved",
            ),
        )
        assert mapping.segment_indices == [0, 1, 2]
        assert mapping.rights.copyright_holder == "NPR"

    def test_empty_indices_rejected(self) -> None:
        with pytest.raises(ValidationError, match="at least 1"):
            SegmentRightsMapping(
                segment_indices=[],
                rights=RightsMetadata(copyright_holder="NPR"),
            )

    def test_negative_index_rejected(self) -> None:
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            SegmentRightsMapping(
                segment_indices=[-1],
                rights=RightsMetadata(copyright_holder="NPR"),
            )

    def test_rights_with_all_fields(self) -> None:
        mapping = SegmentRightsMapping(
            segment_indices=[3, 4],
            rights=RightsMetadata(
                copyright_holder="NPR",
                license_url="https://npr.org/terms",
                usage_terms="Licensed for non-commercial use",
                syndication_allowed=False,
                embargo_until=datetime(2026, 6, 1, tzinfo=timezone.utc),
                contact_email="licensing@npr.org",
            ),
        )
        assert mapping.rights.syndication_allowed is False
        assert mapping.rights.contact_email == "licensing@npr.org"

    def test_minimal_rights(self) -> None:
        mapping = SegmentRightsMapping(
            segment_indices=[0],
            rights=RightsMetadata(),
        )
        assert mapping.rights.copyright_holder is None


# ---------------------------------------------------------------------------
# 2. SignOptions.segment_rights field
# ---------------------------------------------------------------------------


class TestSignOptionsSegmentRights:
    """segment_rights field on SignOptions."""

    def test_default_is_none(self) -> None:
        opts = SignOptions()
        assert opts.segment_rights is None

    def test_accepts_valid_segment_rights(self) -> None:
        opts = SignOptions(
            segment_rights=[
                SegmentRightsMapping(
                    segment_indices=[0, 1],
                    rights=RightsMetadata(copyright_holder="NPR"),
                ),
                SegmentRightsMapping(
                    segment_indices=[2, 3],
                    rights=RightsMetadata(
                        copyright_holder="AP",
                        syndication_allowed=True,
                    ),
                ),
            ]
        )
        assert len(opts.segment_rights) == 2
        assert opts.segment_rights[0].rights.copyright_holder == "NPR"
        assert opts.segment_rights[1].rights.copyright_holder == "AP"

    def test_segment_rights_coexists_with_document_rights(self) -> None:
        """Document-level rights serve as the default for unmapped segments."""
        opts = SignOptions(
            rights=RightsMetadata(copyright_holder="NPR", usage_terms="Default terms"),
            segment_rights=[
                SegmentRightsMapping(
                    segment_indices=[0],
                    rights=RightsMetadata(copyright_holder="AP"),
                ),
            ],
        )
        assert opts.rights.copyright_holder == "NPR"
        assert opts.segment_rights[0].rights.copyright_holder == "AP"


# ---------------------------------------------------------------------------
# 3. Tier gating
# ---------------------------------------------------------------------------


class TestSegmentRightsTierGating:
    """segment_rights feature flag is Enterprise-only."""

    def test_segment_rights_false_for_free(self) -> None:
        features = get_tier_features("free")
        assert features["segment_rights"] is False

    def test_segment_rights_true_for_enterprise(self) -> None:
        features = get_tier_features("enterprise")
        assert features["segment_rights"] is True

    def test_segment_rights_true_for_strategic_partner(self) -> None:
        features = get_tier_features("strategic_partner")
        assert features["segment_rights"] is True

    def test_segment_rights_false_for_legacy_tiers(self) -> None:
        for legacy in ("starter", "professional", "business"):
            features = get_tier_features(legacy)
            assert features["segment_rights"] is False, f"Failed for tier={legacy!r}"


# ---------------------------------------------------------------------------
# 4. Rights assertion generation
# ---------------------------------------------------------------------------


class TestSegmentRightsAssertion:
    """Compound com.encypher.rights.v2 assertion structure."""

    def _build_v2_assertion(
        self,
        segment_rights: list[SegmentRightsMapping],
        default_rights: RightsMetadata | None = None,
    ) -> dict:
        """Build the expected v2 assertion dict from segment_rights mappings."""
        from app.services.segment_rights_utils import build_segment_rights_assertion

        return build_segment_rights_assertion(segment_rights, default_rights)

    def test_v2_assertion_structure(self) -> None:
        mappings = [
            SegmentRightsMapping(
                segment_indices=[0, 1],
                rights=RightsMetadata(copyright_holder="NPR"),
            ),
            SegmentRightsMapping(
                segment_indices=[2],
                rights=RightsMetadata(copyright_holder="AP", syndication_allowed=True),
            ),
        ]
        assertion = self._build_v2_assertion(mappings)
        assert assertion["label"] == "com.encypher.rights.v2"
        data = assertion["data"]
        assert "segment_rights_map" in data
        assert len(data["segment_rights_map"]) == 2

    def test_v2_assertion_includes_default(self) -> None:
        mappings = [
            SegmentRightsMapping(
                segment_indices=[0],
                rights=RightsMetadata(copyright_holder="AP"),
            ),
        ]
        default = RightsMetadata(copyright_holder="NPR", usage_terms="Default")
        assertion = self._build_v2_assertion(mappings, default)
        data = assertion["data"]
        assert data["default_rights"]["copyright_holder"] == "NPR"

    def test_v2_assertion_omits_default_when_none(self) -> None:
        mappings = [
            SegmentRightsMapping(
                segment_indices=[0],
                rights=RightsMetadata(copyright_holder="NPR"),
            ),
        ]
        assertion = self._build_v2_assertion(mappings, None)
        data = assertion["data"]
        assert data.get("default_rights") is None


# ---------------------------------------------------------------------------
# 5. Per-segment rights resolution (6.3 and 6.4)
# ---------------------------------------------------------------------------


class TestResolveSegmentRights:
    """resolve_segment_rights() returns the correct rights for each segment
    and falls back to document-level defaults for unmapped segments.
    """

    def test_mapped_segment_returns_segment_rights(self) -> None:
        """6.3: segment_rights with matching index returns that mapping's rights."""
        from app.services.segment_rights_utils import resolve_segment_rights

        mappings = [
            SegmentRightsMapping(
                segment_indices=[0, 1],
                rights=RightsMetadata(copyright_holder="NPR", syndication_allowed=False),
            ),
            SegmentRightsMapping(
                segment_indices=[2],
                rights=RightsMetadata(copyright_holder="AP", syndication_allowed=True),
            ),
        ]
        result = resolve_segment_rights(0, mappings)
        assert result is not None
        assert result["copyright_holder"] == "NPR"
        assert result["syndication_allowed"] is False

    def test_second_mapping_resolved_correctly(self) -> None:
        """6.3: segment index in second mapping returns second mapping's rights."""
        from app.services.segment_rights_utils import resolve_segment_rights

        mappings = [
            SegmentRightsMapping(
                segment_indices=[0, 1],
                rights=RightsMetadata(copyright_holder="NPR"),
            ),
            SegmentRightsMapping(
                segment_indices=[2],
                rights=RightsMetadata(copyright_holder="AP"),
            ),
        ]
        result = resolve_segment_rights(2, mappings)
        assert result is not None
        assert result["copyright_holder"] == "AP"

    def test_unmapped_segment_inherits_default_rights(self) -> None:
        """6.4: Segments not in segment_rights map inherit document-level rights."""
        from app.services.segment_rights_utils import resolve_segment_rights

        mappings = [
            SegmentRightsMapping(
                segment_indices=[0],
                rights=RightsMetadata(copyright_holder="AP"),
            ),
        ]
        default_rights = RightsMetadata(copyright_holder="NPR", usage_terms="Default terms")

        # Segment 5 is not in any mapping — should fall back to default_rights
        result = resolve_segment_rights(5, mappings, default_rights)
        assert result is not None
        assert result["copyright_holder"] == "NPR"
        assert result["usage_terms"] == "Default terms"

    def test_unmapped_segment_no_default_returns_none(self) -> None:
        """6.4: When no mapping and no default_rights, returns None."""
        from app.services.segment_rights_utils import resolve_segment_rights

        mappings = [
            SegmentRightsMapping(
                segment_indices=[0],
                rights=RightsMetadata(copyright_holder="AP"),
            ),
        ]
        result = resolve_segment_rights(99, mappings, None)
        assert result is None

    def test_all_indices_in_multi_index_mapping_resolve(self) -> None:
        """6.3: All indices listed in segment_indices resolve to the same rights."""
        from app.services.segment_rights_utils import resolve_segment_rights

        mappings = [
            SegmentRightsMapping(
                segment_indices=[0, 1, 2, 3, 4],
                rights=RightsMetadata(copyright_holder="NPR", syndication_allowed=False),
            ),
        ]
        for idx in range(5):
            result = resolve_segment_rights(idx, mappings)
            assert result is not None
            assert result["copyright_holder"] == "NPR"


# ---------------------------------------------------------------------------
# 6. com.encypher.rights.v2 assertion structure (6.5)
# ---------------------------------------------------------------------------


class TestSegmentRightsV2AssertionStructure:
    """6.5: com.encypher.rights.v2 assertion has the correct shape."""

    def test_assertion_label(self) -> None:
        """Label must be com.encypher.rights.v2."""
        from app.services.segment_rights_utils import build_segment_rights_assertion

        assertion = build_segment_rights_assertion(
            [SegmentRightsMapping(segment_indices=[0], rights=RightsMetadata(copyright_holder="NPR"))],
        )
        assert assertion["label"] == "com.encypher.rights.v2"

    def test_assertion_has_segment_rights_map_key(self) -> None:
        """data must contain segment_rights_map."""
        from app.services.segment_rights_utils import build_segment_rights_assertion

        assertion = build_segment_rights_assertion(
            [SegmentRightsMapping(segment_indices=[0], rights=RightsMetadata(copyright_holder="NPR"))],
        )
        assert "segment_rights_map" in assertion["data"]

    def test_segment_rights_map_entries_have_indices_and_rights(self) -> None:
        """Each entry in segment_rights_map has segment_indices and rights keys."""
        from app.services.segment_rights_utils import build_segment_rights_assertion

        mappings = [
            SegmentRightsMapping(
                segment_indices=[0, 1],
                rights=RightsMetadata(copyright_holder="NPR", syndication_allowed=False),
            ),
            SegmentRightsMapping(
                segment_indices=[2, 3],
                rights=RightsMetadata(copyright_holder="AP", syndication_allowed=True),
            ),
        ]
        assertion = build_segment_rights_assertion(mappings)
        seg_map = assertion["data"]["segment_rights_map"]
        assert len(seg_map) == 2
        for entry in seg_map:
            assert "segment_indices" in entry
            assert "rights" in entry

    def test_default_rights_in_assertion_data(self) -> None:
        """default_rights key is present in data when provided."""
        from app.services.segment_rights_utils import build_segment_rights_assertion

        default = RightsMetadata(copyright_holder="NPR", usage_terms="Default")
        assertion = build_segment_rights_assertion(
            [SegmentRightsMapping(segment_indices=[0], rights=RightsMetadata(copyright_holder="AP"))],
            default,
        )
        data = assertion["data"]
        assert "default_rights" in data
        assert data["default_rights"]["copyright_holder"] == "NPR"

    def test_build_from_raw_produces_same_structure(self) -> None:
        """build_segment_rights_assertion_from_raw produces the same label and structure."""
        from app.services.segment_rights_utils import build_segment_rights_assertion_from_raw

        raw_map = [
            {"segment_indices": [0, 1], "rights": {"copyright_holder": "NPR"}},
            {"segment_indices": [2], "rights": {"copyright_holder": "AP"}},
        ]
        assertion = build_segment_rights_assertion_from_raw(raw_map)
        assert assertion["label"] == "com.encypher.rights.v2"
        data = assertion["data"]
        assert len(data["segment_rights_map"]) == 2
        assert data["segment_rights_map"][0]["rights"]["copyright_holder"] == "NPR"
