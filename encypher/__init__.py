"""
EncypherAI Core Package

A Python package for embedding and extracting metadata in text using Unicode
variation selectors.
This package provides tools for invisible metadata encoding in AI-generated text.
"""

__version__ = "2.3.0"

from encypher.config.settings import Settings
from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata
from encypher.pdf_generator import EncypherPDF
from encypher.streaming.handlers import StreamingHandler

__all__ = ["UnicodeMetadata", "MetadataTarget", "Settings", "StreamingHandler", "EncypherPDF"]
