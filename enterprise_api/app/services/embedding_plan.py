"""Embedding plan generation for formatting-preserving clients."""

from __future__ import annotations

from typing import Optional

from app.schemas.sign_schemas import EmbeddingPlan, EmbeddingPlanOperation
from app.utils.legacy_safe_crypto import CHARS_BASE6_SET


def _is_embedding_char(ch: str) -> bool:
    code_point = ord(ch)
    return ch in CHARS_BASE6_SET or code_point == 0xFEFF or 0xFE00 <= code_point <= 0xFE0F or 0xE0100 <= code_point <= 0xE01EF


def build_embedding_plan(*, visible_text: str, signed_text: str) -> Optional[EmbeddingPlan]:
    """Return index-based marker insert operations or None when text does not align."""

    visible_chars = list(visible_text or "")
    visible_idx = 0
    pending = ""
    operations: list[EmbeddingPlanOperation] = []

    for ch in signed_text or "":
        if _is_embedding_char(ch):
            pending += ch
            continue

        if visible_idx >= len(visible_chars) or ch != visible_chars[visible_idx]:
            return None

        if pending:
            operations.append(
                EmbeddingPlanOperation(
                    insert_after_index=visible_idx - 1,
                    marker=pending,
                )
            )
            pending = ""

        visible_idx += 1

    if visible_idx != len(visible_chars):
        return None

    if pending:
        operations.append(
            EmbeddingPlanOperation(
                insert_after_index=(len(visible_chars) - 1) if visible_chars else -1,
                marker=pending,
            )
        )

    return EmbeddingPlan(index_unit="codepoint", operations=operations)
