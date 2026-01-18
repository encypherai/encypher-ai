"""
Pydantic schemas for demo corpus generation.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

DEFAULT_TOPICS = ["politics", "sports", "tech", "finance", "health"]


class DemoGenerateRequest(BaseModel):
    base_path: str = Field(
        default="demo_corpus",
        description="Base directory where the demo corpus will be created. Can be relative or absolute.",
    )
    topics: Optional[List[str]] = Field(
        default=None,
        description="List of subdirectory names to create (topics). Defaults to a standard set if omitted.",
    )
    files_per_topic: int = Field(default=20, ge=1, le=1000)
    paragraphs_per_file: int = Field(default=3, ge=1, le=20)
    overwrite: bool = Field(
        default=False,
        description="When true, an existing demo corpus under base_path will be removed and recreated.",
    )
    seed: Optional[int] = Field(default=None, description="Optional random seed for reproducible output.")


class DemoGenerateResponse(BaseModel):
    base_path: str
    topics_created: List[str]
    total_files: int
    files_per_topic: int
    paragraphs_per_file: int
