"""
FastAPI Example Implementation for EncypherAI

This example demonstrates how to integrate EncypherAI with FastAPI
to create a simple API that encodes metadata into text and decodes it.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing_extensions import AsyncGenerator

from encypher.config.settings import Settings
from encypher.core.metadata_encoder import MetadataEncoder
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.streaming.handlers import StreamingHandler

# Initialize settings
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="EncypherAI Example API",
    description="Example API for EncypherAI metadata encoding",
    version="0.1.0",
)

# Initialize metadata encoder
encoder = MetadataEncoder(secret_key=settings.get_hmac_secret_key())


# Request and response models
class EncodeRequest(BaseModel):
    text: str = Field(..., description="Text to encode metadata into")
    model_id: Optional[str] = Field(None, description="Model ID to embed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata to embed")
    target: Optional[str] = Field(
        "whitespace",
        description="Where to embed metadata (whitespace, punctuation, first_letter, last_letter, all_characters)",
    )


class EncodeResponse(BaseModel):
    encoded_text: str = Field(..., description="Text with encoded metadata")
    metadata: Dict[str, Any] = Field(..., description="Metadata that was encoded")


class DecodeRequest(BaseModel):
    text: str = Field(..., description="Text with encoded metadata to decode")


class DecodeResponse(BaseModel):
    original_text: str = Field(..., description="Original text without metadata")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Extracted metadata or None if not found")
    is_valid: bool = Field(..., description="Whether the metadata is valid")


class StreamRequest(BaseModel):
    text_chunks: List[str] = Field(..., description="List of text chunks to simulate streaming")
    model_id: Optional[str] = Field(None, description="Model ID to embed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata to embed")
    metadata_target: Optional[str] = Field("whitespace", description="Where to embed metadata")
    encode_first_chunk_only: Optional[bool] = Field(True, description="Whether to encode metadata only in the first chunk")


@app.post("/encode", response_model=EncodeResponse)
async def encode_text(request: EncodeRequest) -> EncodeResponse:
    """
    Encode metadata into text using Unicode variation selectors.
    """
    try:
        # Prepare metadata
        metadata = request.metadata or {}
        if request.model_id:
            metadata["model_id"] = request.model_id
        if "timestamp" not in metadata:
            metadata["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Encode metadata
        model_id = metadata.get("model_id")
        timestamp = metadata.get("timestamp")
        target = request.target if request.target is not None else "whitespace"

        encoded_text = UnicodeMetadata.embed_metadata(
            text=request.text,
            model_id=model_id if model_id is not None else "",
            timestamp=(timestamp if timestamp is not None else datetime.now(timezone.utc).isoformat()),
            target=target,
            custom_metadata={k: v for k, v in metadata.items() if k not in ["model_id", "timestamp"]},
        )

        return EncodeResponse(encoded_text=encoded_text, metadata=metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encoding metadata: {str(e)}")


@app.post("/decode", response_model=DecodeResponse)
async def decode_text(request: DecodeRequest) -> DecodeResponse:
    """
    Decode metadata from text with embedded Unicode variation selectors.
    """
    try:
        # Try both decoding methods
        metadata = UnicodeMetadata.extract_metadata(request.text)

        # If UnicodeMetadata didn't find anything, try MetadataEncoder
        if not metadata.get("model_id") and not metadata.get("timestamp"):
            is_valid, alt_metadata, clean_text = encoder.verify_text(request.text)
            if is_valid and alt_metadata:
                return DecodeResponse(original_text=clean_text, metadata=alt_metadata, is_valid=True)

        # If we found metadata with UnicodeMetadata
        if metadata.get("model_id") or metadata.get("timestamp"):
            # Remove the metadata from the text
            # This is a simplified approach - in a real implementation,
            # you would need to properly remove the variation selectors
            clean_text = request.text

            return DecodeResponse(original_text=clean_text, metadata=metadata, is_valid=True)

        # If no metadata found
        return DecodeResponse(original_text=request.text, metadata=None, is_valid=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decoding metadata: {str(e)}")


@app.post("/stream")
async def stream_text(request: StreamRequest) -> StreamingResponse:
    """
    Simulate streaming text with metadata encoding.
    """

    async def generate() -> AsyncGenerator[str, None]:
        # Initialize streaming handler
        metadata = request.metadata or {}
        if request.model_id:
            metadata["model_id"] = request.model_id

        # Create streaming handler with proper type handling
        handler = StreamingHandler(
            metadata=metadata,
            target=request.metadata_target or "whitespace",  # Default to whitespace if None
            encode_first_chunk_only=bool(request.encode_first_chunk_only),  # Convert to bool
        )

        # Process each chunk
        for chunk in request.text_chunks:
            # Add a small delay to simulate streaming
            await asyncio.sleep(0.2)

            # Process the chunk
            processed_chunk = handler.process_chunk(chunk)

            # Yield the processed chunk as a server-sent event
            yield f"data: {json.dumps({'chunk': processed_chunk})}\n\n"

        # End of stream
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


if __name__ == "__main__":
    import asyncio

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
