"""
EncypherAI Core Package

A Python package for embedding and extracting metadata in text using Unicode
variation selectors.
This package provides tools for invisible metadata encoding in AI-generated text.
"""

__version__ = "1.0.0"

from encypher.config.settings import Settings
from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata
from encypher.streaming.handlers import StreamingHandler

__all__ = ["UnicodeMetadata", "MetadataTarget", "Settings", "StreamingHandler"]
