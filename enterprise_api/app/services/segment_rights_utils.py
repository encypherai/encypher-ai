"""
Utilities for segment-level rights.

Builds the compound com.encypher.rights.v2 C2PA assertion and resolves
per-segment rights from a list of SegmentRightsMapping entries.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.schemas.sign_schemas import RightsMetadata, SegmentRightsMapping


def _rights_to_dict(rights: RightsMetadata) -> Dict[str, Any]:
    """Serialize a RightsMetadata to a dict, excluding None fields."""
    d = rights.model_dump(exclude_none=True)
    embargo = d.get("embargo_until")
    if embargo is not None and hasattr(embargo, "isoformat"):
        d["embargo_until"] = embargo.isoformat()
    return d


def build_segment_rights_assertion(
    segment_rights: List[SegmentRightsMapping],
    default_rights: Optional[RightsMetadata] = None,
) -> Dict[str, Any]:
    """Build a com.encypher.rights.v2 assertion from segment_rights mappings.

    Returns a dict suitable for appending to the raw_assertions list in the
    embedding executor.
    """
    segment_rights_map = []
    for mapping in segment_rights:
        segment_rights_map.append(
            {
                "segment_indices": mapping.segment_indices,
                "rights": _rights_to_dict(mapping.rights),
            }
        )

    data: Dict[str, Any] = {
        "segment_rights_map": segment_rights_map,
        "default_rights": _rights_to_dict(default_rights) if default_rights else None,
    }

    return {"label": "com.encypher.rights.v2", "data": data}


def build_segment_rights_assertion_from_raw(
    segment_rights_dicts: List[Dict[str, Any]],
    default_rights: Optional[RightsMetadata] = None,
) -> Dict[str, Any]:
    """Build a com.encypher.rights.v2 assertion from pre-serialized dicts.

    Use this when segment_rights have already been serialized to dicts
    (e.g., in the EncodeWithEmbeddingsRequest flow).
    """
    data: Dict[str, Any] = {
        "segment_rights_map": segment_rights_dicts,
        "default_rights": _rights_to_dict(default_rights) if default_rights else None,
    }
    return {"label": "com.encypher.rights.v2", "data": data}


def resolve_segment_rights(
    segment_index: int,
    segment_rights: List[SegmentRightsMapping],
    default_rights: Optional[RightsMetadata] = None,
) -> Optional[Dict[str, Any]]:
    """Resolve the rights profile for a specific segment index.

    Searches the segment_rights mappings for a match. Falls back to
    default_rights if no mapping covers the given index. Returns None
    if neither provides rights.
    """
    for mapping in segment_rights:
        if segment_index in mapping.segment_indices:
            return _rights_to_dict(mapping.rights)
    if default_rights:
        return _rights_to_dict(default_rights)
    return None
