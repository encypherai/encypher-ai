"""
Pytest configuration for integration tests.
"""

import os


def pytest_ignore_collect(collection_path, config):
    """
    Skip collection of test files that require external API keys when those keys aren't available.
    This prevents import errors during collection when dependencies aren't installed.
    """
    # Ignore large diagnostic artifacts (e.g., test_file_end_results*.txt)
    # These may be encoded with BOM/UTF-16 and are not meant to be collected as tests.
    if collection_path.suffix.lower() == ".txt":
        return True

    # Skip Gemini integration tests if API key is not set
    if collection_path.name == "test_gemini_integration.py" and not os.getenv("GEMINI_API_KEY"):
        return True

    return False
