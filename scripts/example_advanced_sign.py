#!/usr/bin/env python3
"""
Example script demonstrating the Enterprise API signing endpoint.

This script shows how to use the /api/v1/sign endpoint with:
- micro manifest mode (compact invisible embedding, ecc + c2pa by default)
- full manifest mode (standard C2PA)
- All configurable options exposed as CLI arguments

Usage:
    # Basic usage with defaults (micro mode)
    python scripts/example_advanced_sign.py --api-key YOUR_API_KEY

    # With custom text
    python scripts/example_advanced_sign.py --api-key YOUR_API_KEY --text "Your content here"

    # Full customization
    python scripts/example_advanced_sign.py \
        --api-key YOUR_API_KEY \
        --base-url https://api.encypherai.com \
        --manifest-mode micro \
        --segmentation-level sentence \
        --embedding-strategy distributed \
        --distribution-target whitespace \
        --add-dual-binding

Requirements:
    pip install requests

Tier Requirements:
    - micro / full: Free tier and higher
    - distributed_redundant strategy: Enterprise tier
    - add_dual_binding: Enterprise tier
    - disable_c2pa: Enterprise tier
"""

import argparse
import json
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import requests

# Default configuration
DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_TEXT = """This is an example document that will be signed with invisible embeddings.

Each sentence in this document will receive its own cryptographic signature, allowing for
granular verification of content authenticity. The Merkle tree structure enables efficient
proof generation for any subset of the content.

This technology helps publishers protect their content and establish provenance."""


def create_sign_request(
    document_id: str,
    text: str,
    segmentation_level: str = "sentence",
    segmentation_levels: Optional[list] = None,
    manifest_mode: str = "micro",
    embedding_strategy: str = "single_point",
    distribution_target: Optional[str] = None,
    disable_c2pa: bool = False,
    add_dual_binding: bool = False,
    action: str = "c2pa.created",
    previous_instance_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    digital_source_type: Optional[str] = None,
    index_for_attribution: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Create request payload for the signing endpoint.

    Args:
        document_id: Unique identifier for the document
        text: Full document text to encode
        segmentation_level: Level of text segmentation (document, word, sentence, paragraph, section)
        segmentation_levels: Optional list of Merkle segmentation levels to build
        manifest_mode: Manifest mode - 'full' (standard C2PA) or 'micro' (compact invisible)
        embedding_strategy: Embedding placement strategy (single_point, distributed, distributed_redundant)
        distribution_target: Target chars for distributed embedding (whitespace, punctuation, all_chars)
        disable_c2pa: If True, only basic metadata is embedded (Enterprise tier)
        add_dual_binding: Enable additional integrity binding (Enterprise tier)
        action: C2PA action type (c2pa.created or c2pa.edited)
        previous_instance_id: Previous manifest instance_id (required if action=c2pa.edited)
        metadata: Optional document metadata (title, author, etc.)
        digital_source_type: IPTC digital source type URI
        index_for_attribution: Whether to index segments for attribution queries

    Returns:
        Request payload dictionary
    """
    options: Dict[str, Any] = {
        "segmentation_level": segmentation_level,
        "manifest_mode": manifest_mode,
        "embedding_strategy": embedding_strategy,
        "action": action,
        "embedding_options": {
            "format": "plain",
            "method": "invisible",
            "include_text": True,
        },
    }

    if disable_c2pa:
        options["disable_c2pa"] = True
    if add_dual_binding:
        options["add_dual_binding"] = True
    if segmentation_levels:
        options["segmentation_levels"] = segmentation_levels
    if distribution_target:
        options["distribution_target"] = distribution_target
    if previous_instance_id:
        options["previous_instance_id"] = previous_instance_id
    if digital_source_type:
        options["digital_source_type"] = digital_source_type
    if index_for_attribution is not None:
        options["index_for_attribution"] = index_for_attribution

    request: Dict[str, Any] = {
        "document_id": document_id,
        "text": text,
        "options": options,
    }

    if metadata:
        request["metadata"] = metadata

    return request


def call_sign(
    base_url: str,
    api_key: str,
    request_payload: Dict[str, Any],
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Call the signing endpoint.

    Args:
        base_url: API base URL
        api_key: API key for authentication
        request_payload: Request body
        timeout: Request timeout in seconds

    Returns:
        API response as dictionary
    """
    url = f"{base_url}/api/v1/sign"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        url,
        headers=headers,
        json=request_payload,
        timeout=timeout,
    )

    response.raise_for_status()
    return response.json()


def print_response_summary(response: Dict[str, Any]) -> None:
    """Print a formatted summary of the API response."""
    print("\n" + "=" * 60)
    print("RESPONSE SUMMARY")
    print("=" * 60)

    print(f"\nSuccess: {response.get('success', False)}")
    print(f"Document ID: {response.get('document_id', 'N/A')}")

    # Merkle tree info
    merkle = response.get("merkle_tree")
    if merkle:
        print(f"\nMerkle Tree:")
        print(f"  Root Hash: {merkle.get('root_hash', 'N/A')[:32]}...")
        print(f"  Total Leaves: {merkle.get('total_leaves', 'N/A')}")
        print(f"  Tree Depth: {merkle.get('tree_depth', 'N/A')}")

    # Multi-level merkle trees
    merkle_trees = response.get("merkle_trees")
    if merkle_trees:
        print(f"\nMerkle Trees (multi-level):")
        for level, tree in merkle_trees.items():
            print(f"  {level}:")
            print(f"    Root Hash: {tree.get('root_hash', 'N/A')[:32]}...")
            print(f"    Leaves: {tree.get('total_leaves', 'N/A')}")
            print(f"    Indexed: {tree.get('indexed', False)}")

    # Embeddings summary
    embeddings = response.get("embeddings", [])
    print(f"\nEmbeddings: {len(embeddings)} segments")
    if embeddings:
        print("  First 3 segments:")
        for emb in embeddings[:3]:
            text_preview = emb.get("text", "")[:50]
            if len(emb.get("text", "")) > 50:
                text_preview += "..."
            print(f"    [{emb.get('leaf_index')}] {text_preview}")

    # Statistics
    stats = response.get("statistics", {})
    if stats:
        print(f"\nStatistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    # Metadata (check for instance_id - indicates C2PA was used)
    metadata = response.get("metadata", {})
    if metadata:
        print(f"\nMetadata:")
        if "instance_id" in metadata:
            print(f"  Instance ID: {metadata['instance_id']}")
            print("  (C2PA manifest was embedded)")
        else:
            print("  (No instance_id - C2PA was disabled, basic metadata only)")
        for key, value in metadata.items():
            if key != "instance_id":
                print(f"  {key}: {value}")

    # Embedded content preview
    embedded = response.get("embedded_content", "")
    if embedded:
        print(f"\nEmbedded Content Preview (first 200 chars):")
        print(f"  {embedded[:200]}...")
        print(f"\n  Total length: {len(embedded)} chars")


def main():
    parser = argparse.ArgumentParser(
        description="Example script for Enterprise API signing endpoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with micro mode (compact invisible embedding)
  python scripts/example_advanced_sign.py --api-key YOUR_KEY

  # Use full C2PA manifest
  python scripts/example_advanced_sign.py --api-key YOUR_KEY --manifest-mode full

  # Enterprise tier: distributed redundant embedding with dual binding
  python scripts/example_advanced_sign.py --api-key YOUR_KEY \\
      --manifest-mode micro \\
      --embedding-strategy distributed_redundant \\
      --distribution-target all_chars \\
      --add-dual-binding
        """,
    )

    # Required arguments
    parser.add_argument(
        "--api-key",
        required=True,
        help="API key for authentication (required)",
    )

    # Connection settings
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )

    # Document settings
    parser.add_argument(
        "--document-id",
        default=None,
        help="Document ID (default: auto-generated UUID)",
    )
    parser.add_argument(
        "--text",
        default=DEFAULT_TEXT,
        help="Text content to sign (default: example text)",
    )
    parser.add_argument(
        "--text-file",
        type=str,
        help="Read text from file instead of --text argument",
    )

    # Segmentation options
    parser.add_argument(
        "--segmentation-level",
        choices=["document", "word", "sentence", "paragraph", "section"],
        default="sentence",
        help="Segmentation level (default: sentence)",
    )
    parser.add_argument(
        "--segmentation-levels",
        nargs="+",
        choices=["sentence", "paragraph", "section"],
        help="Multiple segmentation levels for Merkle indexing",
    )

    # Manifest mode
    parser.add_argument(
        "--manifest-mode",
        choices=["full", "micro"],
        default="micro",
        help="Manifest mode: 'micro' = compact invisible embedding (default), "
        "'full' = standard C2PA manifest",
    )

    # Embedding strategy (tier-gated)
    parser.add_argument(
        "--embedding-strategy",
        choices=["single_point", "distributed", "distributed_redundant"],
        default="single_point",
        help="Embedding placement strategy (default: single_point). "
        "distributed_redundant requires Enterprise tier",
    )
    parser.add_argument(
        "--distribution-target",
        choices=["whitespace", "punctuation", "all_chars"],
        help="Target for distributed embedding (only with distributed strategies)",
    )

    # C2PA options
    parser.add_argument(
        "--disable-c2pa",
        action="store_true",
        default=True,
        help="Disable C2PA embedding (default: True - only basic metadata)",
    )
    parser.add_argument(
        "--enable-c2pa",
        action="store_true",
        help="Enable C2PA embedding (overrides --disable-c2pa)",
    )
    parser.add_argument(
        "--action",
        choices=["c2pa.created", "c2pa.edited"],
        default="c2pa.created",
        help="C2PA action type (default: c2pa.created)",
    )
    parser.add_argument(
        "--previous-instance-id",
        help="Previous manifest instance_id (required for c2pa.edited action)",
    )

    # Advanced options (tier-gated)
    parser.add_argument(
        "--add-dual-binding",
        action="store_true",
        help="Enable additional integrity binding (Enterprise tier)",
    )
    parser.add_argument(
        "--index-for-attribution",
        action="store_true",
        help="Enforce Merkle indexing quotas for attribution workflows",
    )
    parser.add_argument(
        "--no-index-for-attribution",
        action="store_true",
        help="Disable Merkle indexing for attribution",
    )

    # Metadata options
    parser.add_argument(
        "--title",
        help="Document title (added to metadata)",
    )
    parser.add_argument(
        "--author",
        help="Document author (added to metadata)",
    )
    parser.add_argument(
        "--digital-source-type",
        help="IPTC digital source type URI (e.g., for AI-generated content)",
    )

    # Output options
    parser.add_argument(
        "--output",
        "-o",
        help="Write embedded content to file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output full response as JSON",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Minimal output (just success/failure)",
    )

    args = parser.parse_args()

    # Handle text input
    text = args.text
    if args.text_file:
        try:
            with open(args.text_file) as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading text file: {e}", file=sys.stderr)
            sys.exit(1)

    # Generate document ID if not provided
    document_id = args.document_id or f"doc_{uuid.uuid4().hex[:12]}"

    # Build metadata dict
    metadata = {}
    if args.title:
        metadata["title"] = args.title
    if args.author:
        metadata["author"] = args.author
    metadata["signed_at"] = datetime.utcnow().isoformat()

    # Determine C2PA setting
    disable_c2pa = args.disable_c2pa and not args.enable_c2pa

    # Determine index_for_attribution
    index_for_attribution = None
    if args.index_for_attribution:
        index_for_attribution = True
    elif args.no_index_for_attribution:
        index_for_attribution = False

    # Create request payload
    request_payload = create_sign_request(
        document_id=document_id,
        text=text,
        segmentation_level=args.segmentation_level,
        segmentation_levels=args.segmentation_levels,
        manifest_mode=args.manifest_mode,
        embedding_strategy=args.embedding_strategy,
        distribution_target=args.distribution_target,
        disable_c2pa=disable_c2pa,
        add_dual_binding=args.add_dual_binding,
        action=args.action,
        previous_instance_id=args.previous_instance_id,
        metadata=metadata if metadata else None,
        digital_source_type=args.digital_source_type,
        index_for_attribution=index_for_attribution,
    )

    if not args.quiet:
        print("=" * 60)
        print("ENTERPRISE API - SIGN")
        print("=" * 60)
        print(f"\nEndpoint: {args.base_url}/api/v1/sign/advanced")
        print(f"Document ID: {document_id}")
        print(f"Text length: {len(text)} chars")
        print(f"\nConfiguration:")
        print(f"  Manifest Mode: {args.manifest_mode}")
        print(f"  Segmentation: {args.segmentation_level}")
        print(f"  Embedding Strategy: {args.embedding_strategy}")
        if args.distribution_target:
            print(f"  Distribution Target: {args.distribution_target}")
        print(f"  C2PA Disabled: {disable_c2pa}")
        print(f"  Dual Binding: {args.add_dual_binding}")

    try:
        if not args.quiet:
            print("\nSending request...")

        response = call_sign(
            base_url=args.base_url,
            api_key=args.api_key,
            request_payload=request_payload,
            timeout=args.timeout,
        )

        if args.json:
            print(json.dumps(response, indent=2, default=str))
        elif args.quiet:
            print("Success" if response.get("success") else "Failed")
        else:
            print_response_summary(response)

        # Write embedded content to file if requested
        if args.output and response.get("embedded_content"):
            with open(args.output, "w") as f:
                f.write(response["embedded_content"])
            if not args.quiet:
                print(f"\nEmbedded content written to: {args.output}")

        sys.exit(0 if response.get("success") else 1)

    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_detail = e.response.json()
        except Exception:
            error_detail = e.response.text
        print(f"HTTP Error: {e}", file=sys.stderr)
        print(f"Response: {error_detail}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: Could not connect to {args.base_url}", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
