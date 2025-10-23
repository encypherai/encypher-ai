# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "encypher",  # Use local project
#   "fastapi>=0.100.0", # For the web server
#   "uvicorn[standard]>=0.20.0", # For running FastAPI
#   "python-multipart>=0.0.5", # For form data (file uploads)
#   "requests>=2.25.0", # For self-testing HTTP calls
#   "rich>=13.0.0", # For pretty console output
#   "cryptography>=3.4", # For key generation and handling
# ]
# ///
"""
FastAPI Example Implementation for Encypher

This example demonstrates how to integrate Encypher with FastAPI
to create a simple API that encodes metadata into text and decodes it.
When run directly, it starts a server, runs automated tests against its own endpoints,
prints the results, and then shuts down.
"""

import json
import multiprocessing
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Union

import requests

# --- Imports for self-testing ---
import uvicorn  # For running the server programmatically
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.syntax import Syntax

from encypher.core.keys import generate_ed25519_key_pair as generate_key_pair
from encypher.core.payloads import BasicPayload, ManifestPayload
from encypher.core.unicode_metadata import UnicodeMetadata

# --- End imports for self-testing ---

# --- Configuration & Global Variables ---
# For a real application, manage keys securely and load from a proper config system.
EXAMPLE_KEYS_DIR = os.path.join(os.path.dirname(__file__), "example_fastapi_keys")
EXAMPLE_PRIVATE_KEY_PATH = os.path.join(EXAMPLE_KEYS_DIR, "private_key.pem")
EXAMPLE_PUBLIC_KEYS_DIR = os.path.join(EXAMPLE_KEYS_DIR, "public_keys")
DEFAULT_SIGNER_ID = "fastapi-example-signer"

EXAMPLE_PRIVATE_KEY: Optional[Ed25519PrivateKey] = None
EXAMPLE_PUBLIC_KEY_PROVIDER: Optional[Callable[[str], Optional[Ed25519PublicKey]]] = None

# Initialize FastAPI app
app = FastAPI(
    title="Encypher FastAPI Example API",
    description="Example API for Encypher metadata encoding with digital signatures",
    version="2.3.0",
)

console = Console()  # For self-testing output


@app.on_event("startup")
async def startup_event():
    global EXAMPLE_PRIVATE_KEY, EXAMPLE_PUBLIC_KEY_PROVIDER
    console.print("[ FastAPI Server ] Initializing keys for the example...", style="yellow")

    os.makedirs(EXAMPLE_KEYS_DIR, exist_ok=True)
    os.makedirs(EXAMPLE_PUBLIC_KEYS_DIR, exist_ok=True)

    if not os.path.exists(EXAMPLE_PRIVATE_KEY_PATH):
        priv_key, pub_key = generate_key_pair()

        with open(EXAMPLE_PRIVATE_KEY_PATH, "wb") as f:
            f.write(
                priv_key.private_bytes(
                    encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()
                )
            )
        default_public_key_path = os.path.join(EXAMPLE_PUBLIC_KEYS_DIR, f"{DEFAULT_SIGNER_ID}.pem")
        with open(default_public_key_path, "wb") as f:
            f.write(pub_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo))
        console.print(f"[ FastAPI Server ] Generated dummy private key at [cyan]{EXAMPLE_PRIVATE_KEY_PATH}[/cyan]", style="yellow")
        console.print(
            f"[ FastAPI Server ] Generated dummy public key for '{DEFAULT_SIGNER_ID}' at [cyan]{default_public_key_path}[/cyan]", style="yellow"
        )

    with open(EXAMPLE_PRIVATE_KEY_PATH, "rb") as f:
        private_key_pem_bytes = f.read()
    EXAMPLE_PRIVATE_KEY = serialization.load_pem_private_key(private_key_pem_bytes, password=None)

    if not EXAMPLE_PRIVATE_KEY:
        # This would be a fatal error for the server if run normally
        console.print(f"[ FastAPI Server ] [bold red]FATAL: Failed to load private key from {EXAMPLE_PRIVATE_KEY_PATH}.[/bold red]")
        raise RuntimeError(f"Failed to load private key from {EXAMPLE_PRIVATE_KEY_PATH}. Please ensure it exists or can be generated.")

    def provider(signer_id_to_lookup: str) -> Optional[Ed25519PublicKey]:
        key_file_path = os.path.join(EXAMPLE_PUBLIC_KEYS_DIR, f"{signer_id_to_lookup}.pem")
        if os.path.exists(key_file_path):
            with open(key_file_path, "rb") as f:
                public_key_pem_bytes = f.read()
            return serialization.load_pem_public_key(public_key_pem_bytes)
        return None

    EXAMPLE_PUBLIC_KEY_PROVIDER = provider
    console.print("[ FastAPI Server ] Key initialization complete.", style="green")


# --- Add a health check endpoint for the self-test ---
@app.get("/health", status_code=200)
async def health_check():
    return {"status": "ok"}


# --- End health check ---


# Request and response models
class EncodeRequest(BaseModel):
    text: str = Field(..., description="Text to encode metadata into")
    signer_id: Optional[str] = Field(None, description=f"Signer ID. If not provided, '{DEFAULT_SIGNER_ID}' will be used.")
    custom_metadata: Optional[Dict[str, Any]] = Field(None, description="Custom JSON metadata to embed")


class EncodeResponse(BaseModel):
    encoded_text: str = Field(..., description="Text with encoded metadata")
    signer_id_used: str = Field(..., description="The signer_id that was used for embedding")
    timestamp_used: int = Field(..., description="The Unix timestamp that was used for embedding")
    embedded_custom_metadata: Optional[Dict[str, Any]] = Field(None, description="The custom metadata that was embedded")


class DecodeRequest(BaseModel):
    text: str = Field(..., description="Text with encoded metadata to decode and verify")


class DecodeResponse(BaseModel):
    is_valid: bool = Field(..., description="Whether the signature is valid")
    signer_id: Optional[str] = Field(None, description="Extracted signer ID, if signature is valid or metadata is present")
    payload: Optional[Dict[str, Any]] = Field(None, description="Extracted payload, if signature is valid or metadata is present")
    original_text: Optional[str] = Field(None, description="Original text without metadata")
    error_message: Optional[str] = Field(None, description="Error message if decoding fails")


class StreamRequest(BaseModel):
    text_chunks: List[str] = Field(..., description="List of text chunks to simulate streaming")
    signer_id: Optional[str] = Field(None, description=f"Signer ID. If not provided, '{DEFAULT_SIGNER_ID}' will be used.")
    custom_metadata: Optional[Dict[str, Any]] = Field(None, description="Custom JSON metadata to embed in the stream")
    encode_first_chunk_only: Optional[bool] = Field(True, description="Whether to encode metadata only in the first chunk")


@app.post("/encode", response_model=EncodeResponse)
async def encode_text(request: EncodeRequest):
    """
    Encode metadata into text using Unicode variation selectors and Ed25519 digital signatures.
    """
    if EXAMPLE_PRIVATE_KEY is None:
        raise HTTPException(status_code=500, detail="Server error: Private key not loaded.")

    try:
        actual_signer_id = request.signer_id or DEFAULT_SIGNER_ID
        current_custom_metadata = request.custom_metadata or {}
        timestamp = int(datetime.now(timezone.utc).timestamp())

        # Call embed_metadata as a class method
        encoded_text_result = UnicodeMetadata.embed_metadata(
            text=request.text,
            private_key=EXAMPLE_PRIVATE_KEY,
            signer_id=actual_signer_id,
            timestamp=timestamp,
            custom_metadata=current_custom_metadata,
            # public_key_resolver is not needed for encoding
        )

        return EncodeResponse(
            encoded_text=encoded_text_result,
            signer_id_used=actual_signer_id,
            timestamp_used=timestamp,
            embedded_custom_metadata=current_custom_metadata,
        )
    except Exception as e:
        console.print(f"[ FastAPI Server ] Error during encoding: {e}", style="red")
        raise HTTPException(status_code=500, detail=f"Error encoding metadata: {str(e)}")


@app.post("/decode", response_model=DecodeResponse)
async def decode_text(request: DecodeRequest):
    console.print(f"\n[ FastAPI Server ] Received /decode request with text: '{request.text[:100]}...'", style="dim blue")
    try:
        # Unpacking is (is_valid_bool, signer_id_str, payload_dict_or_model)
        # Runtime observation with local package: payload is a dict -> This comment is outdated.
        # With v2.3.0, extracted_payload will be a BasicPayload or ManifestPayload object, or None.
        is_valid: bool
        extracted_signer_id: Optional[str]
        verified_payload_object: Union[BasicPayload, ManifestPayload, None]

        is_valid, extracted_signer_id, verified_payload_object = UnicodeMetadata.verify_metadata(
            text=request.text, public_key_provider=EXAMPLE_PUBLIC_KEY_PROVIDER
        )

        # Debug prints with original variable names
        console.print(f"[ FastAPI Server DEBUG ] is_valid: {is_valid!r} (type: {type(is_valid)})", style="yellow")
        console.print(f"[ FastAPI Server DEBUG ] extracted_signer_id: {extracted_signer_id!r} (type: {type(extracted_signer_id)})", style="yellow")
        console.print(
            f"[ FastAPI Server DEBUG ] verified_payload_object: {verified_payload_object!r} (type: {type(verified_payload_object)})", style="yellow"
        )

        payload_as_dict: Optional[Dict[str, Any]] = None
        if verified_payload_object:
            payload_as_dict = verified_payload_object

        if is_valid:
            return DecodeResponse(
                is_valid=is_valid,
                signer_id=extracted_signer_id,
                payload=payload_as_dict,
                original_text=None,  # verify_metadata does not return original_text
                error_message=None,
            )
        else:
            return DecodeResponse(
                is_valid=is_valid,
                signer_id=extracted_signer_id,  # May still be present if header was parsed but signature failed
                payload=payload_as_dict,  # May be present if return_payload_on_failure=True was used (not default)
                original_text=None,
                error_message="Signature verification failed or metadata not found/parsable",
            )

    except Exception as e:
        console.print(f"[ FastAPI Server ] Error during decoding: {e}", style="red")
        raise HTTPException(status_code=500, detail=f"Error decoding metadata: {str(e)}")


# --- Self-testing logic ---
def run_server(host="127.0.0.1", port=8000):
    """Runs the Uvicorn server."""
    # Suppress uvicorn's own logging for cleaner test output if desired, or let it run
    # uvicorn.run(app, host=host, port=port, log_level="warning")
    uvicorn.run(app, host=host, port=port)


def run_tests(base_url="http://127.0.0.1:8000"):
    console.print(Panel("Running Self-Tests for FastAPI Example", title="[bold blue]Encypher FastAPI Test[/bold blue]", expand=False))
    session = requests.Session()
    test_text = "This is a test sentence for the FastAPI example self-test!"
    test_signer_id = DEFAULT_SIGNER_ID  # Use the one for which keys are auto-generated
    test_custom_metadata = {"source": "fastapi_self_test", "version": "2.3.0", "status": "testing"}

    # --- Encode Test ---
    console.print(Panel("1. Testing /encode Endpoint", style="bold green"))
    encode_payload = {"text": test_text, "signer_id": test_signer_id, "custom_metadata": test_custom_metadata}
    console.print("[bold]Request to /encode:[/bold]")
    console.print(JSON(json.dumps(encode_payload)))
    try:
        response = session.post(f"{base_url}/encode", json=encode_payload, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        encode_response_data = response.json()
        console.print("[bold]Response from /encode:[/bold]")
        console.print(JSON(json.dumps(encode_response_data)))

        encoded_text = encode_response_data.get("encoded_text")
        signer_id_used = encode_response_data.get("signer_id_used")
        assert encoded_text, "Encoded text not found in response"
        assert signer_id_used == test_signer_id, f"Signer ID mismatch: expected {test_signer_id}, got {signer_id_used}"
        console.print("Encode test [bold green]PASSED[/bold green].\n")

    except requests.exceptions.RequestException as e:
        console.print(f"Encode test [bold red]FAILED[/bold red]: {e}")
        return  # Stop tests if encode fails
    except AssertionError as e:
        console.print(f"Encode test assertion [bold red]FAILED[/bold red]: {e}")
        return

    # --- Decode Test ---
    console.print(Panel("2. Testing /decode Endpoint", style="bold green"))
    decode_payload = {"text": encoded_text}
    console.print("[bold]Request to /decode:[/bold]")
    console.print(JSON(json.dumps(decode_payload)))
    # console.print(f"Encoded text being sent: {encoded_text}") # For debugging if needed
    console.print(Syntax(encoded_text, "text", theme="ansi_dark", line_numbers=False, word_wrap=True))

    try:
        response = session.post(f"{base_url}/decode", json=decode_payload, timeout=10)
        response.raise_for_status()
        decode_response_data = response.json()
        console.print("[bold]Response from /decode:[/bold]")
        console.print(JSON(json.dumps(decode_response_data)))

        is_valid = decode_response_data.get("is_valid")
        decoded_signer_id = decode_response_data.get("signer_id")
        # Further checks on payload can be added here if desired
        assert is_valid, "Signature validation failed (is_valid is false)"
        assert decoded_signer_id == test_signer_id, f"Decoded signer ID mismatch: expected {test_signer_id}, got {decoded_signer_id}"
        console.print("Decode test [bold green]PASSED[/bold green].\n")

    except requests.exceptions.RequestException as e:
        console.print(f"Decode test [bold red]FAILED[/bold red]: {e}")
    except AssertionError as e:
        console.print(f"Decode test assertion [bold red]FAILED[/bold red]: {e}")

    console.print(Panel("Self-Tests Complete", style="bold blue", expand=False))


if __name__ == "__main__":
    # Ensure keys directory exists for this example run
    os.makedirs(EXAMPLE_KEYS_DIR, exist_ok=True)
    os.makedirs(EXAMPLE_PUBLIC_KEYS_DIR, exist_ok=True)

    # It's good practice to use a specific port for the example if possible
    # to avoid conflicts, but 8000 is common for FastAPI examples.
    server_port = 8001  # Using a slightly different port for self-test to avoid collision if another 8000 is running
    server_host = "127.0.0.1"
    base_url = f"http://{server_host}:{server_port}"

    # Start the server in a separate process
    # Note: Uvicorn might not log to console when run via multiprocessing this way
    # depending on how it handles stdout/stderr in subprocesses.
    # For debugging server issues, running it directly (uvicorn fastapi_example:app) is better.
    server_process = multiprocessing.Process(target=run_server, args=(server_host, server_port))
    server_process.daemon = True  # Ensures it exits when main process exits
    console.print(f"[ Self-Test Runner ] Starting FastAPI server in background on {base_url}...", style="yellow")
    server_process.start()

    # Wait for the server to be ready
    max_wait_time = 20  # seconds
    wait_interval = 0.5  # seconds
    waited_time = 0
    server_ready = False
    console.print("[ Self-Test Runner ] Waiting for server to become available...", style="yellow")
    while waited_time < max_wait_time:
        try:
            # Using the new /health endpoint
            health_response = requests.get(f"{base_url}/health", timeout=1)
            if health_response.status_code == 200:
                console.print("[ Self-Test Runner ] Server is UP! Proceeding with tests.", style="green")
                server_ready = True
                break
        except requests.ConnectionError:
            pass  # Server not yet ready
        except requests.Timeout:
            console.print("[ Self-Test Runner ] Health check timed out.", style="yellow")
        time.sleep(wait_interval)
        waited_time += wait_interval
        sys.stdout.write(".")  # Progress indicator
        sys.stdout.flush()

    print()  # Newline after progress dots

    if not server_ready:
        console.print("[ Self-Test Runner ] [bold red]Server did not start within the expected time. Aborting tests.[/bold red]")
    else:
        try:
            run_tests(base_url=base_url)
        except Exception as e:
            console.print(f"[ Self-Test Runner ] [bold red]An error occurred during tests: {e}[/bold red]")

    console.print(f"[ Self-Test Runner ] Shutting down FastAPI server (PID: {server_process.pid})...", style="yellow")
    server_process.terminate()
    server_process.join(timeout=5)  # Wait for graceful termination
    if server_process.is_alive():
        console.print("[ Self-Test Runner ] Server did not terminate gracefully, killing...", style="orange3")
        server_process.kill()  # Force kill if terminate doesn't work
        server_process.join()

    console.print("[ Self-Test Runner ] FastAPI example finished.", style="blue")

# To run this example directly:
# Ensure you have uv installed (pipx install uv)
# Then from the project root: uv run encypher/examples/fastapi_example.py
