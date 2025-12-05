#!/usr/bin/env python3
"""
C2PA Text CLI - Command-line tool for signing and verifying text.

This CLI properly handles Unicode variation selectors, avoiding the encoding
issues that affect PowerShell, curl on Windows, and other tools.

Usage:
    # Sign text
    python -m c2pa_text.cli sign --api-key YOUR_KEY --text "Hello, world!"

    # Sign text from file
    python -m c2pa_text.cli sign --api-key YOUR_KEY --file input.txt --output signed.txt

    # Verify text
    python -m c2pa_text.cli verify --api-key YOUR_KEY --text "signed text here"

    # Verify text from file
    python -m c2pa_text.cli verify --api-key YOUR_KEY --file signed.txt

    # Sign and verify (test round-trip)
    python -m c2pa_text.cli test --api-key YOUR_KEY --text "Test document"
"""

import argparse
import json
import sys
from typing import Optional

from .http import C2PAHTTPError, sign_and_verify, sign_text, verify_text

DEFAULT_BASE_URL = "https://api.encypherai.com/api/v1"


def cmd_sign(args: argparse.Namespace) -> int:
    """Handle the sign command."""
    text = args.text
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()

    if not text:
        print("Error: No text provided. Use --text or --file.", file=sys.stderr)
        return 1

    custom_metadata = None
    if args.metadata:
        try:
            custom_metadata = json.loads(args.metadata)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in --metadata: {e}", file=sys.stderr)
            return 1

    try:
        result = sign_text(
            api_url=f"{args.base_url.rstrip('/')}/sign",
            api_key=args.api_key,
            text=text,
            custom_metadata=custom_metadata,
        )
    except C2PAHTTPError as e:
        print(f"API Error: {e}", file=sys.stderr)
        if e.response_body:
            print(f"Response: {e.response_body}", file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result.get("signed_text", ""))
        print(f"Signed text written to: {args.output}")
        print(f"Document ID: {result.get('document_id')}")
        print(f"Verification URL: {result.get('verification_url')}")
    elif args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("=== Sign Result ===")
        print(f"Success: {result.get('success')}")
        print(f"Document ID: {result.get('document_id')}")
        print(f"Verification URL: {result.get('verification_url')}")
        print(f"Signed text length: {len(result.get('signed_text', ''))} chars")
        if args.verbose:
            print(f"\nSigned text:\n{result.get('signed_text')}")

    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Handle the verify command."""
    text = args.text
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()

    if not text:
        print("Error: No text provided. Use --text or --file.", file=sys.stderr)
        return 1

    try:
        result = verify_text(
            api_url=f"{args.base_url.rstrip('/')}/verify",
            api_key=args.api_key,
            text=text,
        )
    except C2PAHTTPError as e:
        print(f"API Error: {e}", file=sys.stderr)
        if e.response_body:
            print(f"Response: {e.response_body}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        data = result.get("data", {})
        print("=== Verify Result ===")
        print(f"Valid: {data.get('valid')}")
        print(f"Tampered: {data.get('tampered')}")
        print(f"Reason: {data.get('reason_code')}")
        print(f"Signer ID: {data.get('signer_id')}")
        print(f"Signer Name: {data.get('signer_name')}")
        if args.verbose:
            print(f"\nFull manifest:\n{json.dumps(data.get('details', {}).get('manifest', {}), indent=2)}")

    return 0 if data.get("valid") else 1


def cmd_test(args: argparse.Namespace) -> int:
    """Handle the test (sign + verify) command."""
    text = args.text
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()

    if not text:
        print("Error: No text provided. Use --text or --file.", file=sys.stderr)
        return 1

    custom_metadata = None
    if args.metadata:
        try:
            custom_metadata = json.loads(args.metadata)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in --metadata: {e}", file=sys.stderr)
            return 1

    try:
        result = sign_and_verify(
            base_url=args.base_url.rstrip("/"),
            api_key=args.api_key,
            text=text,
            custom_metadata=custom_metadata,
        )
    except C2PAHTTPError as e:
        print(f"API Error: {e}", file=sys.stderr)
        if e.response_body:
            print(f"Response: {e.response_body}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        sign_resp = result["sign_response"]
        verify_resp = result["verify_response"]
        verify_data = verify_resp.get("data", {})

        print("=== Sign + Verify Test ===")
        print(f"Sign Success: {sign_resp.get('success')}")
        print(f"Document ID: {sign_resp.get('document_id')}")
        print(f"Verify Valid: {verify_data.get('valid')}")
        print(f"Verify Tampered: {verify_data.get('tampered')}")
        print(f"Signer ID: {verify_data.get('signer_id')}")
        print(f"Signer Name: {verify_data.get('signer_name')}")

        if verify_data.get("valid"):
            print("\n✅ Round-trip test PASSED")
            return 0
        else:
            print(f"\n❌ Round-trip test FAILED: {verify_data.get('reason_code')}")
            return 1

    return 0


def main(argv: Optional[list] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="c2pa-text",
        description="C2PA Text CLI - Sign and verify text with proper Unicode handling",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--api-key",
        required=True,
        help="Your Encypher API key",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sign command
    sign_parser = subparsers.add_parser("sign", help="Sign text")
    sign_parser.add_argument("--text", "-t", help="Text to sign")
    sign_parser.add_argument("--file", "-f", help="File containing text to sign")
    sign_parser.add_argument("--output", "-o", help="Output file for signed text")
    sign_parser.add_argument("--metadata", "-m", help="Custom metadata as JSON string")
    sign_parser.add_argument("--json", action="store_true", help="Output as JSON")
    sign_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    sign_parser.set_defaults(func=cmd_sign)

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify signed text")
    verify_parser.add_argument("--text", "-t", help="Signed text to verify")
    verify_parser.add_argument("--file", "-f", help="File containing signed text")
    verify_parser.add_argument("--json", action="store_true", help="Output as JSON")
    verify_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    verify_parser.set_defaults(func=cmd_verify)

    # Test command
    test_parser = subparsers.add_parser("test", help="Sign and verify (round-trip test)")
    test_parser.add_argument("--text", "-t", help="Text to test")
    test_parser.add_argument("--file", "-f", help="File containing text to test")
    test_parser.add_argument("--metadata", "-m", help="Custom metadata as JSON string")
    test_parser.add_argument("--json", action="store_true", help="Output as JSON")
    test_parser.set_defaults(func=cmd_test)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
