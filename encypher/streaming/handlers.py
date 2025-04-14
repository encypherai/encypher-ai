"""
Streaming handlers for EncypherAI metadata encoding.

This module provides utilities for handling streaming responses from LLMs
and encoding metadata into the streaming chunks.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, Union, cast

# Import necessary types for signature handling
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes

from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata

# Import logger using relative path
from ..core.logging_config import logger


class StreamingHandler:
    """
    Handler for processing streaming chunks from LLM providers and encoding metadata.

    This class ensures that metadata is properly encoded in streaming responses,
    handling the complexities of partial text chunks while maintaining consistency.
    """

    def __init__(
        self,
        metadata: Optional[Dict[str, Any]] = None,
        target: Union[str, MetadataTarget] = "whitespace",
        encode_first_chunk_only: bool = True,
        # New parameters for signature-based embedding
        private_key: Optional[PrivateKeyTypes] = None,
        signer_id: Optional[str] = None,
        metadata_format: Literal["basic", "manifest"] = "basic",
        # Removed hmac_secret_key
    ):
        """
        Initialize the streaming handler.

        Args:
            metadata: Dictionary of metadata to encode. Must include keys required
                      by the chosen `metadata_format`.
            target: Where to embed the metadata (whitespace, punctuation, etc.)
            encode_first_chunk_only: Whether to encode metadata only in the first
                                     non-empty chunk. Currently, only True is fully
                                     supported for signature embedding.
            private_key: The private key for signing the metadata.
            signer_id: An identifier for the signer (associated with the public key).
            metadata_format: The structure ('basic' or 'manifest') of the metadata payload.

        Raises:
            ValueError: If `metadata_format` is invalid, or if `metadata` is provided
                        without `private_key` and `signer_id`.
            TypeError: If `metadata`, `encode_first_chunk_only`, `private_key`,
                       or `signer_id` have incorrect types.
        """
        logger.debug(f"Initializing StreamingHandler with target='{target}', encode_first_chunk_only={encode_first_chunk_only}")

        # --- Input Validation ---
        if metadata_format not in ("basic", "manifest"):
            raise ValueError("metadata_format must be 'basic' or 'manifest'.")
        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError("If provided, 'metadata' must be a dictionary.")
        if not isinstance(encode_first_chunk_only, bool):
            raise TypeError("'encode_first_chunk_only' must be a boolean.")
        if private_key is not None and not isinstance(private_key, PrivateKeyTypes):
            # Note: Using PrivateKeyTypes for broader compatibility if other key types are added later.
            # If strictly Ed25519, use Ed25519PrivateKey from .keys
            raise TypeError("If provided, 'private_key' must be a valid private key type (e.g., Ed25519PrivateKey).")
        if signer_id is not None and not isinstance(signer_id, str):
            raise TypeError("If provided, 'signer_id' must be a string.")

        # Check for key/signer_id presence *if* metadata is intended for embedding
        if metadata and (not private_key or not signer_id):
            raise ValueError("If metadata is provided for embedding, private_key and signer_id must also be provided.")

        self.metadata = metadata or {}
        self.private_key = private_key
        self.signer_id = signer_id
        self.metadata_format = metadata_format

        # Ensure we have a timestamp if not provided and using basic format
        # Manifest format manages its own timestamps within actions/claims
        if self.metadata_format == "basic" and "timestamp" not in self.metadata:
            self.metadata["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Parse target
        if isinstance(target, str):
            try:
                self.target = MetadataTarget(target)
            except ValueError:
                self.target = MetadataTarget.WHITESPACE
        else:
            self.target = target if isinstance(target, MetadataTarget) else MetadataTarget.WHITESPACE

        self.encode_first_chunk_only = encode_first_chunk_only
        self.has_encoded = False
        self.accumulated_text = ""  # Used to accumulate text until we have enough targets
        self.is_accumulating = False  # Flag to indicate if we're in accumulation mode

        logger.info(
            f"StreamingHandler initialized successfully. Signing enabled: {self.private_key is not None}. Metadata format: '{self.metadata_format}'."
        )

    def _has_sufficient_targets(self, text: str) -> bool:
        """
        Check if the text has at least one suitable target for embedding metadata.

        Args:
            text: Text to check for targets

        Returns:
            True if at least one suitable target is found, False otherwise
        """
        try:
            # Use the find_targets method to check if there's at least one target
            target_indices = UnicodeMetadata.find_targets(text, self.target)
            return len(target_indices) > 0
        except Exception:
            return False

    def process_chunk(self, chunk: Union[str, Dict[str, Any]]) -> Union[str, Dict[str, Any]]:
        """
        Process a streaming chunk and encode metadata if needed.

        This method handles both raw text chunks and structured chunks (like those from OpenAI).

        Args:
            chunk: Text chunk or dictionary containing a text chunk

        Returns:
            Processed chunk with encoded metadata, preserving the input chunk type (str or dict).

        Raises:
            ValueError: If the underlying text processing (_process_text_chunk) fails.
            KeyError: If the expected keys ('choices', 'delta', 'content', etc.) are missing.
            IndexError: If the 'choices' list is empty.
        """
        logger.debug(f"Processing chunk (length: {len(str(chunk))}). Encoded status: {self.has_encoded}")

        # Handle different chunk formats
        if isinstance(chunk, str):
            return self._process_text_chunk(chunk)
        elif isinstance(chunk, dict):
            return self._process_dict_chunk(chunk)
        else:
            # If we don't recognize the format, return as is
            return chunk

    def _process_text_chunk(self, chunk: str) -> str:
        """
        Process a text chunk and encode metadata if needed.

        Args:
            chunk: Text chunk

        Returns:
            Processed text chunk with encoded metadata

        Raises:
            ValueError: If UnicodeMetadata.embed_metadata fails (e.g., not enough targets).
        """
        # Skip empty chunks or if metadata is not meant to be embedded
        if not chunk.strip() or not self.metadata or not self.private_key or not self.signer_id:
            return chunk

        # If we're only encoding the first chunk and we've already done so, return as is
        if self.encode_first_chunk_only and self.has_encoded:
            logger.debug("Metadata already encoded and encode_first_chunk_only=True. Returning chunk as is.")
            return chunk

        # Limit embedding to encode_first_chunk_only=True for now
        if not self.encode_first_chunk_only:
            # Future: Could accumulate text and embed at the end, but requires different handling.
            # For now, just return the chunk if not encoding the first one.
            print("StreamingHandler currently only supports embedding metadata in the first chunk when using signatures.")
            return chunk  # Or raise error? Returning unmodified seems safer for now.

        # If we're in accumulation mode or we need to check if this chunk has enough targets
        if self.is_accumulating or not self._has_sufficient_targets(chunk):
            # Accumulate the text
            self.accumulated_text += chunk
            self.is_accumulating = True

            # Check if the accumulated text now has enough targets
            if not self._has_sufficient_targets(self.accumulated_text):
                # Not enough targets yet, return the chunk as is
                return chunk

            # We have enough targets, proceed with embedding
            try:
                # Encode metadata into the accumulated text
                encoded_text = UnicodeMetadata.embed_metadata(
                    text=self.accumulated_text,
                    private_key=self.private_key,
                    signer_id=cast(str, self.signer_id),  # Cast to str, ensured by __init__ logic
                    metadata_format=self.metadata_format,
                    target=self.target,
                    **self.metadata,  # Pass the full metadata dict as kwargs
                )
                # Mark that we've encoded metadata
                self.has_encoded = True
                self.is_accumulating = False
                # Reset accumulated text
                self.accumulated_text = ""
                logger.info(f"Successfully encoded metadata into chunk. Encoded: {self.has_encoded}")
                return encoded_text
            except Exception as e:
                # Handle potential errors during embedding
                logger.error(f"Error embedding metadata in accumulated text: {e}", exc_info=True)
                self.is_accumulating = False
                self.accumulated_text = ""
                return chunk

        try:
            # Encode metadata into this chunk (it has enough targets)
            encoded_chunk = UnicodeMetadata.embed_metadata(
                text=chunk,
                private_key=self.private_key,
                signer_id=cast(str, self.signer_id),  # Cast to str, ensured by __init__ logic
                metadata_format=self.metadata_format,
                target=self.target,
                **self.metadata,  # Pass the full metadata dict as kwargs
            )
            # Mark that we've encoded metadata
            self.has_encoded = True
            logger.info(f"Successfully encoded metadata into chunk. Encoded: {self.has_encoded}")
            return encoded_chunk
        except Exception as e:
            # Handle potential errors during embedding
            logger.error(f"Error embedding metadata in streaming chunk: {e}", exc_info=True)
            return chunk

    def _process_dict_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a dictionary chunk and encode metadata if needed.

        This handles structured chunks like those from OpenAI's streaming API.

        Args:
            chunk: Dictionary containing a text chunk

        Returns:
            Processed dictionary with encoded metadata

        Raises:
            ValueError: If the underlying text processing (_process_text_chunk) fails.
            KeyError: If the expected keys ('choices', 'delta', 'content', etc.) are missing.
            IndexError: If the 'choices' list is empty.
        """
        # Make a copy to avoid modifying the original
        processed_chunk = chunk.copy()

        # --- Common logic for finding content to process ---
        content_to_process: Optional[str] = None
        content_location: Optional[List[Union[str, int]]] = None  # To update the dict later

        # Handle OpenAI-style chat completions delta format
        if "choices" in processed_chunk and isinstance(processed_chunk["choices"], list) and processed_chunk["choices"]:
            choice = processed_chunk["choices"][0]  # Assume first choice
            if "delta" in choice and "content" in choice["delta"] and isinstance(choice["delta"]["content"], str):
                content_to_process = choice["delta"]["content"]
                content_location = ["choices", 0, "delta", "content"]
            # Handle OpenAI-style completions text format (older APIs?)
            elif "text" in choice and isinstance(choice["text"], str):
                content_to_process = choice["text"]
                content_location = ["choices", 0, "text"]

        # --- Process content if found ---
        if content_to_process is not None and content_location is not None:
            # Process the content as a text chunk
            processed_content = self._process_text_chunk(content_to_process)

            # Only update if the content was actually modified
            if processed_content != content_to_process:
                # Update the chunk with processed content using the location path
                temp_dict = processed_chunk
                for i, key_or_index in enumerate(content_location):
                    if i == len(content_location) - 1:
                        temp_dict[key_or_index] = processed_content  # type: ignore [index]
                    else:
                        temp_dict = temp_dict[key_or_index]  # type: ignore [index]

        return processed_chunk

    def finalize(self) -> Optional[str]:
        """
        Finalize the stream and return any accumulated text with encoded metadata.

        This method should be called after all chunks have been processed to handle
        any remaining accumulated text that hasn't been processed yet.

        Returns:
            Processed accumulated text with encoded metadata, or None if no text accumulated

        Raises:
            ValueError: If UnicodeMetadata.embed_metadata fails (e.g., not enough targets).
        """
        if not self.accumulated_text or self.has_encoded:
            return None

        # Try to encode metadata into the accumulated text
        try:
            encoded_text = UnicodeMetadata.embed_metadata(
                text=self.accumulated_text,
                private_key=self.private_key,
                signer_id=cast(str, self.signer_id),  # Cast to str, ensured by __init__ logic
                metadata_format=self.metadata_format,
                target=self.target,
                **self.metadata,  # Pass the full metadata dict as kwargs
            )
            self.has_encoded = True
            self.accumulated_text = ""
            logger.info(f"Successfully encoded metadata into finalized text. Encoded: {self.has_encoded}")
            return encoded_text
        except Exception as e:
            logger.error(f"Error embedding metadata in finalized text: {e}", exc_info=True)
            return self.accumulated_text

    def reset(self) -> None:
        """
        Reset the handler state.

        This is useful when starting a new streaming session.
        """
        self.has_encoded = False
        self.accumulated_text = ""
        self.is_accumulating = False
