"""
HTTP utilities for C2PA Text API calls.

This module provides helper functions that correctly handle Unicode variation
selectors when making HTTP requests. Standard HTTP clients (especially in
PowerShell, curl on Windows, etc.) often corrupt these characters during
JSON serialization.

Usage:
    from c2pa_text.http import sign_text, verify_text

    # Sign text
    result = sign_text(
        api_url="https://api.encypherai.com/api/v1/sign",
        api_key="your_api_key",
        text="Hello, world!",
        custom_metadata={"author": "Your Name"}
    )
    signed_text = result["signed_text"]

    # Verify text
    verification = verify_text(
        api_url="https://api.encypherai.com/api/v1/verify",
        api_key="your_api_key",
        text=signed_text
    )
"""

import json
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class C2PAHTTPError(Exception):
    """Exception raised for C2PA API HTTP errors."""

    def __init__(self, status_code: int, message: str, response_body: Optional[str] = None):
        self.status_code = status_code
        self.message = message
        self.response_body = response_body
        super().__init__(f"HTTP {status_code}: {message}")


def _make_request(
    url: str,
    method: str,
    headers: Dict[str, str],
    body: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Make an HTTP request with proper UTF-8 encoding for C2PA text.

    This function ensures that Unicode variation selectors are correctly
    preserved during JSON serialization and transmission.

    Args:
        url: The API endpoint URL.
        method: HTTP method (GET, POST, etc.).
        headers: HTTP headers to include.
        body: Request body (will be JSON-encoded with ensure_ascii=False).

    Returns:
        Parsed JSON response as a dictionary.

    Raises:
        C2PAHTTPError: If the request fails.
    """
    # Ensure Content-Type is set for JSON
    headers = {**headers, "Content-Type": "application/json; charset=utf-8"}

    # Encode body with ensure_ascii=False to preserve Unicode characters
    data = None
    if body is not None:
        json_str = json.dumps(body, ensure_ascii=False)
        data = json_str.encode("utf-8")

    request = Request(url, data=data, headers=headers, method=method)

    try:
        with urlopen(request) as response:
            response_body = response.read().decode("utf-8")
            return json.loads(response_body)
    except HTTPError as e:
        response_body = e.read().decode("utf-8") if e.fp else None
        raise C2PAHTTPError(e.code, e.reason, response_body) from e
    except URLError as e:
        raise C2PAHTTPError(0, str(e.reason)) from e


def sign_text(
    api_url: str,
    api_key: str,
    text: str,
    custom_metadata: Optional[Dict[str, Any]] = None,
    *,
    use_bearer: bool = True,
) -> Dict[str, Any]:
    """
    Sign text using the Encypher C2PA API.

    This function properly handles Unicode encoding to ensure the signed
    text with variation selectors is correctly returned.

    Args:
        api_url: The sign endpoint URL (e.g., "https://api.encypherai.com/api/v1/sign").
        api_key: Your API key.
        text: The text to sign.
        custom_metadata: Optional metadata to include in the manifest.
        use_bearer: If True, use "Bearer {key}" auth. If False, use "X-API-Key" header.

    Returns:
        API response containing 'signed_text', 'document_id', 'verification_url', etc.

    Raises:
        C2PAHTTPError: If the API request fails.

    Example:
        >>> result = sign_text(
        ...     "https://api.encypherai.com/api/v1/sign",
        ...     "ency_your_api_key",
        ...     "Hello, world!",
        ...     {"author": "Alice"}
        ... )
        >>> print(result["signed_text"])
    """
    headers = {}
    if use_bearer:
        headers["Authorization"] = f"Bearer {api_key}"
    else:
        headers["X-API-Key"] = api_key

    body: Dict[str, Any] = {"text": text}
    if custom_metadata:
        body["custom_metadata"] = custom_metadata

    return _make_request(api_url, "POST", headers, body)


def verify_text(
    api_url: str,
    api_key: str,
    text: str,
    *,
    use_bearer: bool = True,
) -> Dict[str, Any]:
    """
    Verify signed text using the Encypher C2PA API.

    This function properly handles Unicode variation selectors in the
    signed text to ensure accurate verification.

    Args:
        api_url: The verify endpoint URL (e.g., "https://api.encypherai.com/api/v1/verify").
        api_key: Your API key.
        text: The signed text to verify (containing C2PA manifest).
        use_bearer: If True, use "Bearer {key}" auth. If False, use "X-API-Key" header.

    Returns:
        API response containing verification result with 'valid', 'tampered',
        'signer_id', 'signer_name', etc.

    Raises:
        C2PAHTTPError: If the API request fails.

    Example:
        >>> result = verify_text(
        ...     "https://api.encypherai.com/api/v1/verify",
        ...     "ency_your_api_key",
        ...     signed_text
        ... )
        >>> print(f"Valid: {result['data']['valid']}")
    """
    headers = {}
    if use_bearer:
        headers["Authorization"] = f"Bearer {api_key}"
    else:
        headers["X-API-Key"] = api_key

    body = {"text": text}

    return _make_request(api_url, "POST", headers, body)


def sign_and_verify(
    base_url: str,
    api_key: str,
    text: str,
    custom_metadata: Optional[Dict[str, Any]] = None,
    *,
    use_bearer: bool = True,
) -> Dict[str, Any]:
    """
    Sign text and immediately verify it (useful for testing).

    Args:
        base_url: Base API URL (e.g., "https://api.encypherai.com/api/v1").
        api_key: Your API key.
        text: The text to sign and verify.
        custom_metadata: Optional metadata to include.
        use_bearer: If True, use "Bearer {key}" auth.

    Returns:
        Dictionary with 'sign_response' and 'verify_response'.

    Example:
        >>> result = sign_and_verify(
        ...     "https://api.encypherai.com/api/v1",
        ...     "ency_your_api_key",
        ...     "Test document"
        ... )
        >>> print(f"Signed: {result['sign_response']['success']}")
        >>> print(f"Verified: {result['verify_response']['data']['valid']}")
    """
    sign_url = f"{base_url.rstrip('/')}/sign"
    verify_url = f"{base_url.rstrip('/')}/verify"

    sign_response = sign_text(
        sign_url, api_key, text, custom_metadata, use_bearer=use_bearer
    )

    signed_text = sign_response.get("signed_text", "")

    verify_response = verify_text(verify_url, api_key, signed_text, use_bearer=use_bearer)

    return {
        "sign_response": sign_response,
        "verify_response": verify_response,
    }
