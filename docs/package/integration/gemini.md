# Google Gemini Integration

This guide demonstrates how to integrate EncypherAI with Google's Gemini API to embed and verify metadata in AI-generated content.

## Prerequisites

- Python 3.8 or higher
- An API key for Google Gemini (obtainable from [Google AI Studio](https://aistudio.google.com/app/apikey))
- EncypherAI package installed

## Installation

```bash
pip install encypher-ai google-generativeai
```

## Basic Usage

### Setting Up

```python
import os
import time
from google import genai
from google.genai import types
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes

# Configure Google Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Generate key pair (replace with your actual key management)
private_key, public_key = generate_key_pair()

# Example public key resolver function
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    # In a real application, you'd fetch the key based on the ID
    if key_id == "gemini-key-1":
        return public_key
    return None

### Simple Text Generation with Metadata

```python
# Initialize the Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

# Generate content with Gemini
prompt = "Explain the concept of quantum computing in simple terms"
response = model.generate_content(prompt)
generated_text = response.text

# Embed metadata into the generated text
encoded_text = UnicodeMetadata.embed_metadata(
    text=generated_text,
    model_id="gemini-1.5-flash",
    timestamp=int(time.time()),
    key_id="gemini-key-1", # Identifier for the key
    custom_metadata={
        "prompt": prompt,
        "version": "2.0.0"
    },
    private_key=private_key
)

# Later, verify and extract the metadata
is_valid, metadata = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=resolve_public_key
)

if is_valid:
    print(f"Verified metadata: {metadata}")
    print(f"Model used: {metadata['model_id']}")
    print(f"Timestamp: {metadata['timestamp']}")
    print(f"Prompt: {metadata['custom']['prompt']}")
else:
    print("Warning: Metadata verification failed!")
```

## Chat Conversations

### Setting Up a Chat Session

```python
from google.genai import types
from encypher.core.unicode_metadata import UnicodeMetadata

# Initialize a chat session
chat = model.start_chat(history=[])

# Function to process and encode responses
def process_gemini_response(response_text, prompt):
    return UnicodeMetadata.embed_metadata(
        text=response_text,
        key_id="gemini-key-1",
        model_id="gemini-1.5-flash",
        timestamp=int(time.time()),
        custom_metadata={
            "prompt": prompt,
            "chat_id": chat.session_id,
            "version": "2.0.0"
        },
        private_key=private_key
    )

# Send messages and encode responses
user_message = "What are three interesting facts about space?"
response = chat.send_message(user_message)
encoded_response = process_gemini_response(response.text, user_message)

print("Encoded response:")
print(encoded_response)

# Continue the conversation
follow_up = "Tell me more about the first fact"
response2 = chat.send_message(follow_up)
encoded_response2 = process_gemini_response(response2.text, follow_up)

print("\nEncoded follow-up response:")
print(encoded_response2)

# Verify any response
is_valid, metadata = UnicodeMetadata.verify_metadata(
    text=encoded_response,
    public_key_resolver=resolve_public_key
)

if is_valid:
    print(f"\nVerified metadata from first response: {metadata}")
else:
    print("\nWarning: Metadata verification failed!")
```

## Function Calling with Metadata

Google Gemini supports function calling, which can be combined with EncypherAI for metadata embedding:

```python
from google.genai import types

# Define a function declaration
get_weather_declaration = {
    "name": "get_weather",
    "description": "Get the current weather for a location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state or country",
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "The unit of temperature",
            },
        },
        "required": ["location"],
    },
}

# Mock implementation of the function
def get_weather(location, unit="celsius"):
    """Mock weather function that would normally call a weather API"""
    # In a real implementation, this would call a weather API
    return {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "unit": unit,
        "condition": "sunny"
    }

# Set up tools configuration
tools = types.Tool(function_declarations=[get_weather_declaration])
config = types.GenerateContentConfig(tools=[tools])

# Create model with function calling capability
model = genai.GenerativeModel('gemini-1.5-flash')

# User query that might trigger function calling
user_query = "What's the weather like in San Francisco?"
contents = [
    types.Content(
        role="user", parts=[types.Part(text=user_query)]
    )
]

# Send request with function declarations
response = model.generate_content(
    config=config,
    contents=contents
)

# Process function call if present
if hasattr(response.candidates[0].content.parts[0], 'function_call'):
    function_call = response.candidates[0].content.parts[0].function_call
    function_name = function_call.name
    function_args = function_call.args

    # Execute the function
    if function_name == "get_weather":
        weather_data = get_weather(**function_args)

        # Create a response with the function results
        function_response = [
            types.Content(
                role="function",
                parts=[
                    types.Part(
                        function_response={
                            "name": function_name,
                            "response": weather_data,
                        }
                    )
                ],
            )
        ]

        # Get model's final response
        contents.extend(function_response)
        final_response = model.generate_content(contents=contents)
        final_text = final_response.text

        # Embed metadata in the final response
        metadata_to_embed = {
            "model_id": "gemini-1.5-flash",
            "timestamp": int(time.time()),
            "key_id": "gemini-key-1",
            "custom_metadata": {
                "prompt": user_query,
                "function_called": function_name,
                "function_args": function_args,
                "function_result": weather_data,
                "version": "2.0.0"
            }
        }

        # Embed metadata into the final text response
        encoded_response_text = UnicodeMetadata.embed_metadata(
            text=final_text,
            **metadata_to_embed,
            private_key=private_key
        )
        print(f"\nFinal response with embedded metadata:\n{encoded_response_text}")

        # Verify the response
        is_valid, metadata = UnicodeMetadata.verify_metadata(
            text=encoded_response_text,
            public_key_resolver=resolve_public_key
        )
        if is_valid:
            print(f"\nVerified function call response metadata: {metadata}")
    else:
        # Handle regular text response
        encoded_response_text = UnicodeMetadata.embed_metadata(
            text=response.text,
            key_id="gemini-key-1",
            model_id="gemini-1.5-flash",
            timestamp=int(time.time()),
            custom_metadata={
                "prompt": user_query,
                "version": "2.0.0"
            },
            private_key=private_key
        )
        print(f"\nRegular response with embedded metadata:\n{encoded_response_text}")

        # Verify the response
        is_valid, metadata = UnicodeMetadata.verify_metadata(
            text=encoded_response_text,
            public_key_resolver=resolve_public_key
        )
        if is_valid:
            print(f"\nVerified regular response metadata: {metadata}")
```

## Multimodal Content

Gemini supports multimodal inputs. Here's how to handle text responses from multimodal prompts:

```python
import PIL.Image
from google.genai import types

# Load an image
image = PIL.Image.open("example_image.jpg")

# Create a multimodal prompt
multimodal_prompt = [
    types.Part(text="Describe what you see in this image:"),
    types.Part(inline_data=types.Blob(
        mime_type="image/jpeg",
        data=image.tobytes()
    ))
]

# Generate content with multimodal input
response = model.generate_content(multimodal_prompt)
image_description = response.text

# Embed metadata into the response
encoded_text = UnicodeMetadata.embed_metadata(
    text=image_description,
    key_id="gemini-key-1",
    model_id="gemini-1.5-flash",
    timestamp=int(time.time()),
    custom_metadata={
        "content_type": "image_description",
        "image_filename": "example_image.jpg",
        "version": "2.0.0"
    },
    private_key=private_key
)

print("Encoded image description:")
print(encoded_text)

# Verify the metadata
is_valid, metadata = UnicodeMetadata.verify_metadata(
    text=encoded_text,
    public_key_resolver=resolve_public_key
)

if is_valid:
    print(f"\nVerified metadata: {metadata}")
else:
    print("\nWarning: Metadata verification failed!")
```

## Streaming Responses

For streaming responses from Gemini, use the StreamingHandler from EncypherAI:

```python
from encypher.streaming import StreamingHandler

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

# Create metadata
metadata = {
    "model_id": "gemini-1.5-flash",
    "timestamp": int(time.time()),
    "key_id": "gemini-key-1",
    "custom_metadata": {
        "stream_type": "gemini",
        "version": "2.0.0"
    }
}

# Initialize the streaming handler
handler = StreamingHandler(
    metadata=metadata,
    private_key=private_key # Use the private key
)

# Start the streaming generation
response = model.generate_content(
    "Write a short story about a time traveler",
    stream=True
)

# Process the stream with the handler
full_response = ""
for chunk in response:
    processed_chunk = handler.process_chunk(chunk.text)
    if processed_chunk:
        print(processed_chunk, end="", flush=True)
        full_response += processed_chunk

# Finalize the stream to process any remaining buffer
final_chunk = handler.finalize()
if final_chunk:
    print(final_chunk, end="", flush=True)
    full_response += final_chunk

print("\n\nStreaming completed!")

# Verify the complete response
is_valid, metadata = UnicodeMetadata.verify_metadata(
    text=full_response, # Verify the assembled text
    public_key_resolver=resolve_public_key
)

if is_valid:
    print(f"\nVerified metadata from streaming response: {metadata}")
else:
    print("\nWarning: Metadata verification failed for streaming response!")
```

## Advanced Configuration

### Safety Settings

When working with Gemini, you can configure safety settings while still embedding metadata:

```python
from google.genai import types

# Configure safety settings
safety_settings = {
    types.HarmCategory.HARM_CATEGORY_HARASSMENT: types.SafetySetting.BLOCK_MEDIUM_AND_ABOVE,
    types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: types.SafetySetting.BLOCK_MEDIUM_AND_ABOVE,
    types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: types.SafetySetting.BLOCK_MEDIUM_AND_ABOVE,
    types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: types.SafetySetting.BLOCK_MEDIUM_AND_ABOVE,
}

# Create model with safety settings
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    safety_settings=safety_settings
)

# Generate content with safety settings
prompt = "Write a children's story about friendship"
response = model.generate_content(prompt)
safe_text = response.text

# Embed metadata including safety information
encoded_text = UnicodeMetadata.embed_metadata(
    text=safe_text,
    key_id="gemini-key-1",
    model_id="gemini-1.5-flash",
    timestamp=int(time.time()),
    custom_metadata={
        "prompt": prompt,
        "safety_settings": "medium_and_above_blocked",
        "version": "2.0.0"
    },
    private_key=private_key
)

print("Encoded text with safety settings:")
print(encoded_text)
```

### Generation Parameters

Customize generation parameters while embedding metadata:

```python
# Configure generation parameters
generation_config = {
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 1024,
}

# Create model with generation config
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    generation_config=generation_config
)

# Generate content with custom parameters
prompt = "Write a concise summary of quantum computing"
response = model.generate_content(prompt)
generated_text = response.text

# Embed metadata including generation parameters
encoded_text = UnicodeMetadata.embed_metadata(
    text=generated_text,
    key_id="gemini-key-1",
    model_id="gemini-1.5-flash",
    timestamp=int(time.time()),
    custom_metadata={
        "prompt": prompt,
        "temperature": 0.2,
        "top_p": 0.8,
        "top_k": 40,
        "max_tokens": 1024,
        "version": "2.0.0"
    },
    private_key=private_key
)

print("Encoded text with generation parameters:")
print(encoded_text)
```

## Complete Example

Here's a complete example that combines multiple features:

```python
import os
import time
from google import genai
from google.genai import types
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.keys import generate_key_pair
from cryptography.hazmat.primitives import serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes

# Configure API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Generate key pair (replace with your actual key management)
private_key, public_key = generate_key_pair()

# Example public key resolver function
def resolve_public_key(key_id: str) -> Optional[PublicKeyTypes]:
    # In a real application, you'd fetch the key based on the ID
    if key_id == "gemini-key-1":
        return public_key
    return None

# Initialize chat session
chat = genai.GenerativeModel('gemini-1.5-flash').start_chat(history=[])

# Function to process and encode responses
def process_gemini_response(response_text, prompt, metadata=None):
    custom_metadata = {
        "prompt": prompt,
        "chat_id": chat.session_id,
        "version": "2.0.0"
    }

    # Add any additional metadata
    if metadata:
        custom_metadata.update(metadata)

    return UnicodeMetadata.embed_metadata(
        text=response_text,
        key_id="gemini-key-1", # Identifier for the key
        model_id="gemini-1.5-flash",
        timestamp=int(time.time()),
        custom_metadata=custom_metadata,
        private_key=private_key
    )

# Start conversation
user_message = "I need a 5-day itinerary for visiting Tokyo, Japan"
response = chat.send_message(user_message)
encoded_response = process_gemini_response(
    response.text,
    user_message,
    {"content_type": "itinerary", "location": "Tokyo, Japan"}
)

print("Encoded response:")
print(encoded_response)

# Continue conversation
follow_up = "Can you recommend some vegetarian restaurants in Tokyo?"
response2 = chat.send_message(follow_up)
encoded_response2 = process_gemini_response(
    response2.text,
    follow_up,
    {"content_type": "recommendations", "cuisine": "vegetarian"}
)

print("\nEncoded follow-up response:")
print(encoded_response2)

# Verify responses
for i, text in enumerate([encoded_response, encoded_response2], 1):
    is_valid, metadata = UnicodeMetadata.verify_metadata(
        text=text,
        public_key_resolver=resolve_public_key
    )

    if is_valid:
        print(f"\nResponse {i} verified with metadata: {metadata}")
    else:
        print(f"\nWarning: Metadata verification failed for response {i}!")
```

## Conclusion

This guide demonstrates how to integrate Google's Gemini API with EncypherAI to embed and verify metadata in AI-generated content. By following these examples, you can ensure that content generated by Gemini models includes verifiable metadata for tracking, attribution, and security purposes.

For more information, refer to:
- [Google Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [EncypherAI Documentation](https://github.com/encypherai/encypher-ai)

## Troubleshooting

1. **API Key Issues**: Ensure `GEMINI_API_KEY` is set correctly.
2. **Package Installation**: Make sure `google-generativeai` and `encypher` are installed.
3. **Verification Failures**:
   - Check if the text content was modified *after* embedding.
   - Ensure the `public_key_resolver` correctly retrieves the public key corresponding to the `key_id` used during signing.
   - Verify that the `private_key` used for signing matches the `public_key` returned by the resolver for the given `key_id`.
