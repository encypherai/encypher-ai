# Browser Extension Verification

This example shows how to verify text directly from Chrome or Firefox using a simple browser extension.

## Overview

The extension highlights selected text and displays the verification result provided by a local FastAPI service built with EncypherAI.

## 1. Start the Verification API

Create a public/private key pair using `generate_keys.py` and run the API server:

```bash
uv pip install encypher-ai fastapi uvicorn
python -m encypher.examples.generate_keys  # produces private_key.pem and public_key.pem
uvicorn encypher.examples.browser_extension_api:app --reload
```

By default the server expects `public_key.pem` in the working directory and listens on `http://localhost:8000`.

## 2. Load the Extension

The `extension` folder contains all required files (`manifest.json`, scripts and popup HTML). Load this folder as an unpacked extension in Chrome/Firefox.

1. Open your browser's extensions page.
2. Enable developer mode and choose **Load unpacked**.
3. Select the `extension` directory from this repository.

## 3. Verify Text

Select any text on a page, right‑click and choose **"Verify with EncypherAI"**. The extension sends the text to the local API and highlights the selection in green if valid or red if invalid. A small overlay shows the signer and model information if present. An EncypherAI logo icon appears to the left of the metadata so users can quickly identify the verification source.
