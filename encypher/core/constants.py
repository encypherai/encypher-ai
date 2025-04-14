"""
Constants for the EncypherAI core module.

This module contains constants used throughout the EncypherAI core module,
particularly for metadata embedding and extraction.
"""

from enum import Enum, auto

# Metadata embedding constants
MAX_BIT_INDEX = 255  # Maximum bit index for embedding
METADATA_PREFIX = "ENCYPHER"  # Prefix for metadata
METADATA_DELIMITER = ":"  # Delimiter for metadata sections

# Unicode variation selectors used for embedding
VARIATION_SELECTORS = [
    # Basic variation selectors (FE00-FE0F)
    0xFE00,
    0xFE01,
    0xFE02,
    0xFE03,
    0xFE04,
    0xFE05,
    0xFE06,
    0xFE07,
    0xFE08,
    0xFE09,
    0xFE0A,
    0xFE0B,
    0xFE0C,
    0xFE0D,
    0xFE0E,
    0xFE0F,
    # Variation selectors supplement (E0100-E01EF) - first few shown here
    0xE0100,
    0xE0101,
    0xE0102,
    0xE0103,
    0xE0104,
    0xE0105,
    0xE0106,
    0xE0107,
    # ... more can be added as needed
]


class MetadataTarget(Enum):
    """Enum for metadata embedding targets."""

    NONE = auto()
    WHITESPACE = auto()
    PUNCTUATION = auto()
    FIRST_LETTER = auto()
    LAST_LETTER = auto()
    ALL_CHARACTERS = auto()
