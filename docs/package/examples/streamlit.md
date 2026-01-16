# Streamlit Demo App

The Encypher Streamlit demo provides an interactive web-based interface for exploring and testing Encypher's functionality. This demo allows users to experiment with metadata embedding, extraction, and verification in real-time through a user-friendly interface.

![Streamlit Demo Preview](../../assets/streamlit-demo-preview.png)

> Note: Timestamps are optional across all metadata formats, including C2PA. When you omit a timestamp, C2PA action assertions that normally include a `when` field will simply omit it.

## Features

The Streamlit demo showcases all key Encypher capabilities:

1. **Interactive Metadata Embedding**
   - Embed custom metadata into text
   - Choose different embedding targets (whitespace, punctuation, etc.)
   - See real-time results

2. **Metadata Extraction and Visualization**
   - Extract embedded metadata from text
   - View formatted JSON output
   - Compare original and embedded text

3. **Digital Signature Verification**
   - Test content integrity verification
   - Experiment with key pair management
   - Simulate tampering to see detection in action

4. **Streaming Simulation**
   - Visualize chunk-by-chunk processing
   - See how metadata is distributed in streaming scenarios
   - Understand the streaming workflow

## Running the Demo

To run the Streamlit demo:

```bash
# Install required dependencies
uv add encypher-ai streamlit

# Save the example app below as streamlit_app.py, then run it
streamlit run streamlit_app.py
```

## Demo Structure

The Streamlit app is organized into several tabs:

### Basic Embedding

![Basic Embedding Tab](../../assets/streamlit-basic-embedding.png)

This tab allows users to:
- Enter or generate sample text
- Define custom metadata fields
- Choose embedding targets
- See a side-by-side comparison of original and encoded text
- Copy the encoded text to clipboard

### Metadata Extraction

![Metadata Extraction Tab](../../assets/streamlit-extraction.png)

This tab enables users to:
- Paste text containing embedded metadata
- Extract and view the metadata
- See a formatted JSON representation
- Verify the content integrity

### Digital Signature Verification

![Digital Signature Verification Tab](../../assets/streamlit-verification.png)

This tab demonstrates security features:
- Generate and manage key pairs for digital signatures
- Test verification on embedded content
- Simulate tampering and see detection
- Understand how digital signatures protect content integrity

### Streaming Demo

![Streaming Demo Tab](../../assets/streamlit-streaming.png)

This tab simulates streaming scenarios:
- See text generated chunk by chunk
- Observe how metadata is handled in streaming
- Control streaming speed and chunk size
- Compare different streaming strategies

## Code Structure

The Streamlit app is built with a modular structure:

```
examples/
└── streamlit_app.py       # Main Streamlit application
    ├── basic_embedding()  # Basic embedding tab
    ├── extraction()       # Metadata extraction tab
    ├── verification()     # Digital signature verification tab
    └── streaming_demo()   # Streaming simulation tab
```

## Example Code

Here's a simplified version of the code that powers the basic embedding tab:

```python
def basic_embedding():
    st.header("Basic Metadata Embedding")

    # Text input
    sample_text = st.text_area(
        "Enter text to embed metadata into:",
        value="This is a sample text that will have metadata embedded within it. "
              "The metadata will be invisible to human readers but can be extracted "
              "programmatically.",
        height=150
    )

    # Metadata input
    with st.expander("Configure Metadata", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            model = st.text_input("Model Name:", value="gpt-4")
            org = st.text_input("Organization:", value="Encypher")
            timestamp = st.text_input(
                "Timestamp:",
                value=str(int(time.time()))
            )
            version = st.text_input("Version:", value="3.0.2")

        with col2:
            # Additional custom fields
            custom_fields = {}
            if st.checkbox("Add custom metadata fields"):
                for i in range(3):
                    c1, c2 = st.columns(2)
                    key = c1.text_input(f"Key {i+1}:", key=f"key_{i}")
                    value = c2.text_input(f"Value {i+1}:", key=f"value_{i}")
                    if key and value:
                        custom_fields[key] = value

    # Key Pair for Digital Signatures
    st.subheader("Digital Signature Keys")
    private_key_input = st.text_input("Private Key (PEM Format)", type="password", help="Enter the Ed25519 private key in PEM format.")
    public_key_input = st.text_input("Public Key (PEM Format)", help="Enter the corresponding Ed25519 public key in PEM format.")
    signer_id_input = st.text_input("Signer ID", value="streamlit-signer-1", help="A unique identifier for this key pair.")

    # Custom metadata to embed (signer_id is provided separately)
    metadata = {
        "model": model,
        "organization": org,
        "timestamp": int(timestamp) if timestamp.isdigit() else timestamp,
        "version": version,
        **custom_fields,
    }

    # Target selection
    target_options = {
        "Whitespace": "whitespace",
        "Punctuation": "punctuation",
        "First Letter of Words": "first_letter",
        "Last Letter of Words": "last_letter",
        "All Characters": "all_characters"
    }

    target = st.selectbox(
        "Where to embed metadata:",
        options=list(target_options.keys()),
        index=0
    )

    # Embed metadata
    if st.button("Embed Metadata"):
        from encypher.core.unicode_metadata import UnicodeMetadata
        from encypher.core.keys import load_private_key_from_data, load_public_key_from_data

        try:
            private_key = load_private_key_from_data(private_key_input)
        except Exception as e:
            st.error(f"Invalid Private Key: {e}")
            private_key = None

        try:
            with st.spinner("Embedding metadata..."):
                if not private_key:
                    st.error("Embedding requires a valid Ed25519 private key.")
                    st.stop()

                encoded_text = UnicodeMetadata.embed_metadata(
                    text=sample_text,
                    custom_metadata=metadata,
                    private_key=private_key,
                    signer_id=signer_id_input,
                    metadata_format="basic",
                    timestamp=metadata.get("timestamp"),
                    target=target_options[target],
                )

            # Display results
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Original Text")
                st.text_area("", sample_text, height=200, disabled=True)

            with col2:
                st.subheader("Encoded Text")
                st.text_area("", encoded_text, height=200, disabled=True)

            # Metadata display
            st.subheader("Embedded Metadata")
            st.json(metadata)

            # Copy button
            st.button(
                "Copy Encoded Text to Clipboard",
                on_click=lambda: st.write(
                    f'<script>navigator.clipboard.writeText("{encoded_text}");</script>',
                    unsafe_allow_html=True
                )
            )

            # Verification status
            from encypher.core.unicode_metadata import UnicodeMetadata
            is_valid, signer_id, payload_dict = UnicodeMetadata.verify_metadata(
                encoded_text,
                public_key_resolver=lambda key_id: load_public_key_from_data(public_key_input) if key_id == signer_id_input else None,
                return_payload_on_failure=True,
            )

            if is_valid:
                st.success(f"✅ Verification successful! Signer ID: {signer_id}")
                if payload_dict:
                    st.write("Verified Payload:")
                    st.json(payload_dict)
            else:
                st.error(f"❌ Verification failed. Signer ID (if found): {signer_id}")

        except Exception as e:
            st.error(f"Error embedding metadata: {str(e)}")
```

## Complete Streamlit App

Here's a more complete example of a Streamlit app that demonstrates Encypher's capabilities:

```python
import streamlit as st
import time
import json
from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata
from encypher.streaming.handlers import StreamingHandler

# App title and description
st.set_page_config(
    page_title="Encypher Demo",
    page_icon="🔐",
    layout="wide"
)

st.title("Encypher Demo")
st.markdown(
    "This demo showcases the capabilities of Encypher for embedding, "
    "extracting, and verifying metadata in text."
)

# Create tabs
tabs = st.tabs([
    "Basic Embedding",
    "Metadata Extraction",
    "Digital Signature Verification",
    "Streaming Demo"
])

# Basic Embedding Tab
with tabs[0]:
    st.header("Basic Metadata Embedding")

    # Text input
    sample_text = st.text_area(
        "Enter text to embed metadata into:",
        value="This is a sample text that will have metadata embedded within it.",
        height=150
    )

    # Metadata configuration
    col1, col2 = st.columns(2)

    with col1:
        model_id = st.text_input("Model ID:", value="gpt-4-demo")
        org = st.text_input("Organization:", value="StreamlitApp")
        timestamp = st.number_input("Timestamp:", value=int(time.time()))
        version = st.text_input("Version:", value="3.0.2")

    with col2:
        signer_id_input = st.text_input("Signer ID:", value=st.session_state.signer_id)

    # Key Pair for Digital Signatures
    st.subheader("Digital Signature Keys")
    private_key_input = st.text_input("Private Key (PEM Format)", type="password", help="Enter the Ed25519 private key in PEM format.")
    public_key_input = st.text_input("Public Key (PEM Format)", help="Enter the corresponding Ed25519 public key in PEM format.")

    # Custom metadata to embed (signer_id is provided separately)
    metadata = {
        "model_id": model_id,
        "organization": org,
        "timestamp": int(timestamp),
        "version": version,
    }

    # Target selection
    target = st.selectbox(
        "Where to embed metadata:",
        options=["whitespace", "punctuation", "first_letter", "last_letter", "all_characters"],
        index=0
    )

    # Embed button
    if st.button("Embed Metadata", key="embed_btn"):
        from encypher.core.unicode_metadata import UnicodeMetadata
        from encypher.core.keys import load_private_key_from_data, load_public_key_from_data

        try:
            private_key = load_private_key_from_data(private_key_input)
        except Exception as e:
            st.error(f"Invalid Private Key: {e}")
            private_key = None

        try:
            # Embed metadata
            if not private_key:
                st.error("Embedding requires a valid Ed25519 private key.")
                st.stop()

            encoded_text = UnicodeMetadata.embed_metadata(
                text=sample_text,
                custom_metadata=metadata,
                private_key=private_key,
                signer_id=signer_id_input,
                metadata_format="basic",
                timestamp=metadata.get("timestamp"),
                target=target
            )

            st.subheader("Results")
            st.text_area("Encoded Text:", encoded_text, height=150)
            st.json(metadata)

            # Verification
            def resolve_public_key(key_id_to_resolve):
                if key_id_to_resolve == signer_id_input and public_key_input:
                    try:
                        return load_public_key_from_data(public_key_input)
                    except Exception as e:
                        st.error(f"Invalid Public Key for verification: {e}")
                return None

            is_valid, signer_id, payload_dict = UnicodeMetadata.verify_metadata(
                encoded_text,
                public_key_resolver=resolve_public_key,
                return_payload_on_failure=True,
            )

            if is_valid:
                st.success(f"✅ Verification successful! Signer ID: {signer_id}")
            else:
                st.error(f"❌ Verification failed. Signer ID (if found): {signer_id}")

        except Exception as e:
            st.error(f"Error: {str(e)}")

# Metadata Extraction Tab
with tabs[1]:
    st.header("Metadata Extraction")

    # Text input
    encoded_text = st.text_area(
        "Paste text with embedded metadata:",
        height=150
    )

    # Extract button
    if st.button("Extract Metadata", key="extract_btn") and encoded_text:
        from encypher.core.unicode_metadata import UnicodeMetadata
        from encypher.core.keys import load_public_key_from_data

        try:
            # Extract metadata
            metadata = UnicodeMetadata.extract_metadata(encoded_text)

            if metadata:
                st.success("Metadata extracted successfully!")
                st.json(metadata)

                # Verify if requested
                verify = st.checkbox("Verify metadata")
                if verify:
                    public_key_input_verify = st.text_input("Public Key (PEM) for Verification", key="verify_public_key")
                    key_id_verify = st.text_input("Signer ID (for verification)", value="your-signer-id")

                    # Create a simple resolver function
                    def resolve_public_key(key_id_to_resolve):
                        if key_id_to_resolve == key_id_verify and public_key_input_verify:
                            try:
                                return load_public_key_from_data(public_key_input_verify)
                            except Exception as e:
                                st.error(f"Invalid Public Key for verification: {e}")
                        return None

                    is_valid, signer_id, payload_dict = UnicodeMetadata.verify_metadata(
                        text=encoded_text,
                        public_key_resolver=resolve_public_key,
                        return_payload_on_failure=True,
                    )

                    if is_valid:
                        st.success(f"✅ Verification successful! Signer ID: {signer_id}")
                    else:
                        st.error(f"❌ Verification failed. Signer ID (if found): {signer_id}")
            else:
                st.warning("No metadata found in the text.")
        except Exception as e:
            st.error(f"Error extracting metadata: {str(e)}")

# Digital Signature Verification Tab
with tabs[2]:
    st.header("Digital Signature Verification")

    # Key pair
    private_key = st.text_input(
        "Private Key (for digital signature verification):",
        value="your-private-key",
        type="password"
    )
    public_key = st.text_input(
        "Public Key (for digital signature verification):",
        value="your-public-key",
        type="password"
    )

    # Text input
    text = st.text_area(
        "Enter text to embed and verify:",
        value="This text will be protected with digital signature verification.",
        height=100
    )

    # Create metadata
    metadata = {
        "model": "verification-demo",
        "timestamp": int(time.time()),
        "version": "3.0.2",
    }

    signer_id = st.text_input("Signer ID", value=st.session_state.signer_id, key="verify_signer_id")

    # Embed and verify
    if st.button("Embed and Verify", key="verify_btn"):
        from encypher.core.unicode_metadata import UnicodeMetadata
        from encypher.core.keys import load_private_key_from_data, load_public_key_from_data

        try:
            private_key = load_private_key_from_data(private_key)
        except Exception as e:
            st.error(f"Invalid Private Key: {e}")
            private_key = None

        try:
            # Embed metadata
            encoded_text = UnicodeMetadata.embed_metadata(
                text=text,
                custom_metadata=metadata,
                private_key=private_key,
                signer_id=signer_id,
                metadata_format="basic",
                timestamp=metadata.get("timestamp"),
                target="whitespace"
            )

            # Display original text
            st.subheader("Original Text with Metadata")
            st.text_area("", encoded_text, height=100, disabled=True)

            # Simulate tampering
            tampered_text = encoded_text + " This text was added after embedding."
            st.subheader("Tampered Text")
            st.text_area("", tampered_text, height=100, disabled=True)

            # Verify both versions
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Original Verification")
                def resolve_public_key(key_id_to_resolve):
                    if key_id_to_resolve == signer_id and public_key:
                        try:
                            return load_public_key_from_data(public_key)
                        except Exception as e:
                            st.error(f"Invalid Public Key for verification: {e}")
                    return None

                is_valid, signer_id, payload_dict = UnicodeMetadata.verify_metadata(
                    encoded_text,
                    public_key_resolver=resolve_public_key,
                    return_payload_on_failure=True,
                )
                if is_valid:
                    st.success(f"✅ Verification successful! Signer ID: {signer_id}")
                else:
                    st.error(f"❌ Verification failed. Signer ID (if found): {signer_id}")

            with col2:
                st.subheader("Tampered Verification")
                is_valid, signer_id, payload_dict = UnicodeMetadata.verify_metadata(
                    tampered_text,
                    public_key_resolver=resolve_public_key,
                    return_payload_on_failure=True,
                )
                if is_valid:
                    st.success(f"✅ Verification successful! Signer ID: {signer_id}") # Should ideally fail for tampered
                else:
                    st.error(f"❌ Verification failed. Signer ID (if found): {signer_id}") # Expected path for tampered

        except Exception as e:
            st.error(f"Error: {str(e)}")

# Streaming Demo Tab
with tabs[3]:
    st.header("Streaming Demo")

    # Streaming parameters
    st.subheader("Configure Streaming")

    col1, col2 = st.columns(2)

    with col1:
        chunk_size = st.slider("Chunk Size (words):", 1, 10, 3)
        delay = st.slider("Chunk Delay (seconds):", 0.1, 2.0, 0.5)

    with col2:
        model_id = st.text_input("Model ID:", value="gpt-4-stream-demo")
        org = st.text_input("Organization:", value="StreamlitApp")
        timestamp = st.number_input("Timestamp:", value=int(time.time()))
        version = st.text_input("Version:", value="3.0.2")
        signer_id_input = st.text_input("Signer ID:", value=st.session_state.signer_id, key="stream_key_id")
        metadata = {
            "model_id": model_id,
            "organization": org,
            "timestamp": int(timestamp),
            "version": version,
        }
        st.json(metadata)

    # Start streaming
    if st.button("Start Streaming Simulation", key="stream_btn"):
        # Sample text split into words
        text = "The quick brown fox jumps over the lazy dog. This is an example of streaming text generation with embedded metadata."
        words = text.split()

        # Create chunks
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            if i + chunk_size < len(words):
                chunk += " "
            chunks.append(chunk)

        # Initialize streaming handler
        handler = StreamingHandler(
            custom_metadata=metadata,
            private_key=private_key,
            signer_id=signer_id_input,
            timestamp=metadata.get("timestamp"),
            target="whitespace",
            encode_first_chunk_only=False,
            metadata_format="basic",
        )

        # Display streaming progress
        st.subheader("Streaming Progress")
        progress_bar = st.progress(0)

        # Container for streaming output
        stream_container = st.empty()
        accumulated_text = ""

        # Process chunks
        for i, chunk in enumerate(chunks):
            # Process chunk
            processed_chunk = handler.process_chunk(chunk)
            accumulated_text += processed_chunk

            # Update display
            stream_container.text_area("", accumulated_text, height=150, disabled=True)
            progress_bar.progress((i + 1) / len(chunks))

            # Delay
            time.sleep(delay)

        # Finalize
        final_chunk = handler.finalize()
        if final_chunk:
            accumulated_text += final_chunk
            stream_container.text_area("", accumulated_text, height=150, disabled=True)

        # Verify the result
        from encypher.core.unicode_metadata import UnicodeMetadata
        try:
            extracted_metadata = UnicodeMetadata.extract_metadata(accumulated_text)
            def resolve_public_key(key_id_to_resolve):
                if key_id_to_resolve == signer_id_input and public_key:
                    try:
                        return load_public_key_from_data(public_key)
                    except Exception as e:
                        st.error(f"Invalid Public Key for verification: {e}")
                return None

            is_valid, signer_id, payload_dict = UnicodeMetadata.verify_metadata(
                accumulated_text,
                public_key_resolver=resolve_public_key,
                require_hard_binding=False,
                return_payload_on_failure=True,
            )

            st.subheader("Streaming Results")
            st.json(extracted_metadata)

            if is_valid:
                st.success(f"✅ Streaming metadata verified successfully! Signer ID: {signer_id}")
                if payload_dict:
                    st.write("Verified Payload from Stream:")
                    st.json(payload_dict)
            else:
                st.error(f"❌ Streaming metadata verification failed. Signer ID (if found): {signer_id}")

        except Exception as e:
            st.error(f"Error verifying/extracting streaming metadata: {str(e)}")

# Ensure st.session_state is initialized for signer_id if not already
if 'signer_id' not in st.session_state:
    st.session_state.signer_id = 'streamlit-default-signer'

# This demo provides a comprehensive overview of Encypher's features. For more detailed examples and API documentation, refer to the respective sections in this documentation.
