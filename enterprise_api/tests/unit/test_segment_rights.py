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
