"""
Script to create example files with Encypher metadata for testing purposes.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import the shared library
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    # Import from the core Encypher package as used in shared_commercial_libs
    # Import from our shared commercial library
    from rich.console import Console

    from encypher.core.keys import load_private_key_from_data, load_public_key_from_data
    from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata
    from encypher_commercial_shared import Encypher

    console = Console()

    # Directory to save example files
    EXAMPLE_DIR = Path(__file__).parent / "example_files"
    EXAMPLE_DIR.mkdir(exist_ok=True)

    # Create example key files for testing
    KEY_DIR = EXAMPLE_DIR / "keys"
    KEY_DIR.mkdir(exist_ok=True)

    # Generate a test private/public key pair for signing
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519

    def generate_key_pair(private_key_path, public_key_path):
        """Generate a test Ed25519 key pair for signing and verification."""
        # Generate a private key
        private_key = ed25519.Ed25519PrivateKey.generate()

        # Serialize private key to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()
        )

        # Serialize public key to PEM format
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)

        # Write keys to files
        with open(private_key_path, "wb") as f:
            f.write(private_pem)

        with open(public_key_path, "wb") as f:
            f.write(public_pem)

        return private_key, public_key

    # Generate keys for test-signer
    test_signer_private_key_path = KEY_DIR / "test-signer-private.pem"
    test_signer_public_key_path = KEY_DIR / "test-signer-public.pem"
    generate_key_pair(test_signer_private_key_path, test_signer_public_key_path)
    console.print(f"[green]Generated test signer keys at {KEY_DIR}[/green]")

    # Generate keys for unknown-signer
    unknown_signer_private_key_path = KEY_DIR / "unknown-signer-private.pem"
    unknown_signer_public_key_path = KEY_DIR / "unknown-signer-public.pem"
    generate_key_pair(unknown_signer_private_key_path, unknown_signer_public_key_path)
    console.print(f"[green]Generated unknown signer keys at {KEY_DIR}[/green]")

    # Create example files with metadata

    # Example 1: Valid metadata from test-signer
    ea_test = Encypher(
        private_key_path=str(test_signer_private_key_path), public_key_path=str(test_signer_public_key_path), signer_id="test-signer", verbose=True
    )

    # Example text content
    example1_text = """This is an example file with valid Encypher metadata.
The metadata is embedded in this text file and can be verified
using the test-signer public key.

This file should pass verification when scanned by the audit-log-cli tool.
"""

    # Embed metadata
    try:
        # Get current timestamp
        from datetime import datetime

        current_time = datetime.now()

        # Create custom metadata without timestamp
        custom_metadata = {"purpose": "testing", "example": "valid"}

        # Let's modify the Encypher.embed_metadata method to accept a timestamp parameter
        # and pass it to UnicodeMetadata.embed_metadata
        from types import MethodType

        def embed_metadata_with_timestamp(
            self, text, custom_metadata=None, model_id=None, metadata_format="basic", target=MetadataTarget.WHITESPACE, timestamp=None
        ):
            if not self._private_key:
                raise ValueError("Private key is required for embedding metadata")
            if not self._signer_id:
                raise ValueError("Signer ID is required for embedding metadata")

            try:
                from encypher.core.unicode_metadata import UnicodeMetadata

                result = UnicodeMetadata.embed_metadata(
                    text=text,
                    private_key=self._private_key,
                    signer_id=self._signer_id,
                    metadata_format=metadata_format,
                    model_id=model_id,
                    custom_metadata=custom_metadata,
                    target=target,
                    timestamp=timestamp,
                )
                if self.verbose:
                    console.print("[green]Successfully embedded metadata[/green]")
                return result
            except Exception as e:
                if self.verbose:
                    console.print(f"[red]Error embedding metadata: {e}[/red]")
                raise

        # Replace the method temporarily
        ea_test.embed_metadata = MethodType(embed_metadata_with_timestamp, ea_test)

        # Now call with timestamp
        example1_with_metadata = ea_test.embed_metadata(
            text=example1_text, custom_metadata=custom_metadata, model_id="test-model-1", metadata_format="basic", timestamp=current_time
        )

        # Write to file
        example1_path = EXAMPLE_DIR / "example1_valid.txt"
        with open(example1_path, "w", encoding="utf-8") as f:
            f.write(example1_with_metadata)
        console.print(f"[green]Created example file with valid metadata: {example1_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error creating example1: {e}[/red]")

    # Example 2: Valid metadata from unknown-signer
    ea_unknown = Encypher(
        private_key_path=str(unknown_signer_private_key_path),
        public_key_path=str(unknown_signer_public_key_path),
        signer_id="unknown-signer",
        verbose=True,
    )

    # Example text content
    example2_text = """This is an example file with valid Encypher metadata,
but from an unknown signer that is not in the trusted signers list.

This file should have valid metadata but fail verification when scanned
by the audit-log-cli tool with trusted signers specified.
"""

    # Embed metadata
    try:
        # Get current timestamp
        from datetime import datetime

        current_time = datetime.now()

        # Create custom metadata without timestamp
        custom_metadata = {"purpose": "testing", "example": "unknown-signer"}

        # Replace the method temporarily for the unknown signer
        ea_unknown.embed_metadata = MethodType(embed_metadata_with_timestamp, ea_unknown)

        # Now call with timestamp
        example2_with_metadata = ea_unknown.embed_metadata(
            text=example2_text, custom_metadata=custom_metadata, model_id="test-model-2", metadata_format="basic", timestamp=current_time
        )

        # Write to file
        example2_path = EXAMPLE_DIR / "example2_unknown_signer.txt"
        with open(example2_path, "w", encoding="utf-8") as f:
            f.write(example2_with_metadata)
        console.print(f"[green]Created example file with unknown signer: {example2_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error creating example2: {e}[/red]")

    # Example 3: File without any metadata
    example3_text = """This is an example file without any Encypher metadata.

This file should be detected as having no metadata when scanned
by the audit-log-cli tool.
"""

    # Write to file
    example3_path = EXAMPLE_DIR / "example3_no_metadata.txt"
    with open(example3_path, "w", encoding="utf-8") as f:
        f.write(example3_text)
    console.print(f"[green]Created example file without metadata: {example3_path}[/green]")

    # Example 4: File with tampered metadata - sophisticated approach
    try:
        # Create a file with valid metadata, then modify the content to simulate tampering
        example4_text = """This is an example file with tampered Encypher metadata.
The metadata was originally valid, but the content has been modified
after the metadata was embedded.

This file should fail verification when scanned by the audit-log-cli tool.
"""

        # Get current timestamp
        import copy
        import json
        from datetime import datetime, timezone

        current_time = datetime.now(timezone.utc)

        # Create original metadata
        original_metadata = {"purpose": "testing", "example": "tampered", "document_id": "doc-original-123", "version": "1.0.0"}

        # First, create a file with the original metadata
        original_with_metadata = ea_test.embed_metadata(
            text=example4_text, custom_metadata=original_metadata, model_id="test-model-4", metadata_format="basic", timestamp=current_time
        )

        # Save the original file for reference
        original_path = EXAMPLE_DIR / "example4_original.txt"
        with open(original_path, "w", encoding="utf-8") as f:
            f.write(original_with_metadata)
        console.print(f"[green]Created original example file: {original_path}[/green]")

        # Now create a tampered file by modifying the text content AFTER the metadata has been embedded
        # This will cause verification to fail because the content doesn't match the signature
        lines = original_with_metadata.split("\n")
        if len(lines) > 2:
            # Add a clear indication that the file was tampered with
            lines[1] = lines[1] + " [THIS TEXT WAS MODIFIED AFTER SIGNING]"
            tampered_text = "\n".join(lines)
        else:
            # Fallback if we can't split by lines
            tampered_text = original_with_metadata.replace(
                "This file should fail verification", "This file should fail verification [THIS TEXT WAS MODIFIED AFTER SIGNING]"
            )

        # Write the tampered file
        sophisticated_path = EXAMPLE_DIR / "example4_sophisticated_tamper.txt"
        with open(sophisticated_path, "w", encoding="utf-8") as f:
            f.write(tampered_text)

        console.print(f"[green]Created sophisticated tampered example: {sophisticated_path}[/green]")
        console.print("[green]This file has modified text content after metadata was embedded[/green]")
        console.print("[green]This should fail verification when scanned by the audit-log-cli tool[/green]")
    except Exception as e:
        console.print(f"[red]Error creating example4: {e}[/red]")

    console.print("[bold green]Successfully created all example files![/bold green]")
    console.print("\nTo use these files with the audit-log-cli tool, run:")
    console.print("uv run -- python -m app.main --target tests/example_files --trusted-signers tests/example_files/keys")

except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you have installed all the required dependencies.")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
