# ENCYPHER ENTERPRISE SDK - WBS PLAN
## Python SDK for Enterprise API Integration

**Goal:** Production-ready Python SDK for easy integration with the Encypher Enterprise API, optimized for chat streaming workflows and enterprise Python environments.

**Key Requirements:**
- ✅ Simple, intuitive Python API
- ✅ Streaming support for real-time LLM content signing
- ✅ Both sync and async operations
- ✅ Framework integrations (LangChain, OpenAI, LiteLLM)
- ✅ CLI tool for quick testing
- ✅ Comprehensive examples and documentation

**Technology Stack:**
- **Core:** Python 3.9+ with UV package management
- **HTTP Client:** httpx (supports both sync and async)
- **Streaming:** Generator-based streaming with sentence buffering
- **CLI:** Click or Typer
- **Testing:** pytest with async support

**Use Cases:**
```
PRIMARY USE CASES:
├── Real-time LLM Streaming
│   └── Sign streaming GPT-4/Claude responses as they arrive
│
├── Batch Content Signing
│   └── Sign articles, documents, reports
│
├── Integration with AI Frameworks
│   ├── LangChain chains/agents
│   ├── OpenAI API wrappers
│   └── LiteLLM multi-provider support
│
└── CLI Operations
    ├── Quick signing from terminal
    ├── Verification workflows
    └── Batch processing scripts
```

---

## PHASE 1: SDK CORE LIBRARY (Week 1)

### 1.0 Project Setup

**Deliverable:** SDK project structure with UV configuration

- [ ] **1.0.1** Create SDK project structure
  ```bash
  enterprise_sdk/
  ├── encypher_enterprise/
  │   ├── __init__.py
  │   ├── client.py           # Main client class
  │   ├── async_client.py     # Async client
  │   ├── streaming.py        # Streaming signer
  │   ├── models.py           # Request/response models
  │   ├── exceptions.py       # Custom exceptions
  │   ├── config.py           # Configuration
  │   ├── integrations/
  │   │   ├── __init__.py
  │   │   ├── langchain.py   # LangChain integration
  │   │   ├── openai.py      # OpenAI wrapper
  │   │   └── litellm.py     # LiteLLM integration
  │   └── cli/
  │       ├── __init__.py
  │       └── main.py        # CLI commands
  ├── examples/
  │   ├── basic_signing.py
  │   ├── streaming_chat.py
  │   ├── langchain_example.py
  │   └── batch_processing.py
  ├── tests/
  │   ├── test_client.py
  │   ├── test_streaming.py
  │   └── test_integrations.py
  ├── pyproject.toml
  ├── README.md
  └── LICENSE
  ```

- [ ] **1.0.2** Configure pyproject.toml
  ```toml
  [project]
  name = "encypher-enterprise"
  version = "1.0.0"
  description = "Python SDK for Encypher Enterprise API"
  dependencies = [
      "httpx>=0.25.0",
      "pydantic>=2.0.0",
      "python-dotenv>=1.0.0",
      "click>=8.1.0",
      "rich>=13.0.0",
  ]

  [project.optional-dependencies]
  langchain = ["langchain>=0.1.0"]
  openai = ["openai>=1.0.0"]
  litellm = ["litellm>=1.0.0"]
  all = ["langchain>=0.1.0", "openai>=1.0.0", "litellm>=1.0.0"]

  [project.scripts]
  encypher = "encypher_enterprise.cli.main:cli"
  ```

**Success Criteria:**
- Project structure created
- UV workspace configured
- Dependencies specified

**Estimated Time:** 0.5 day
**Cost:** $0 (development)

---

### 1.1 Core Client Implementation

**Deliverable:** Synchronous and asynchronous client classes

- [ ] **1.1.1** Implement base client
  ```python
  # encypher_enterprise/client.py

  class EncypherClient:
      """
      Synchronous client for Encypher Enterprise API.

      Usage:
          client = EncypherClient(api_key="encypher_...")

          # Sign content
          result = client.sign(
              text="Content to sign",
              title="Document Title"
          )

          # Verify content
          verification = client.verify(signed_text)

          # Lookup sentence
          provenance = client.lookup("Some sentence")
      """

      def __init__(
          self,
          api_key: str,
          base_url: str = "https://api.encypherai.com",
          timeout: float = 30.0,
          max_retries: int = 3
      ):
          self.api_key = api_key
          self.base_url = base_url
          self.client = httpx.Client(timeout=timeout)
          self.max_retries = max_retries

      def sign(
          self,
          text: str,
          title: Optional[str] = None,
          url: Optional[str] = None,
          document_type: str = "article"
      ) -> SignResponse:
          """Sign content with C2PA manifest."""
          ...

      def verify(self, text: str) -> VerifyResponse:
          """Verify C2PA manifest in signed content."""
          ...

      def lookup(self, sentence: str) -> LookupResponse:
          """Look up sentence provenance."""
          ...

      def get_stats(self) -> StatsResponse:
          """Get organization usage statistics."""
          ...
  ```

- [ ] **1.1.2** Implement async client
  ```python
  # encypher_enterprise/async_client.py

  class AsyncEncypherClient:
      """
      Asynchronous client for Encypher Enterprise API.

      Usage:
          async with AsyncEncypherClient(api_key="...") as client:
              result = await client.sign(text="Content")
      """

      def __init__(self, api_key: str, **kwargs):
          self.api_key = api_key
          self.client = httpx.AsyncClient(**kwargs)

      async def sign(self, text: str, **kwargs) -> SignResponse:
          """Async sign content."""
          ...

      async def verify(self, text: str) -> VerifyResponse:
          """Async verify content."""
          ...

      async def __aenter__(self):
          return self

      async def __aexit__(self, *args):
          await self.client.aclose()
  ```

- [ ] **1.1.3** Implement Pydantic models
  ```python
  # encypher_enterprise/models.py

  from pydantic import BaseModel
  from typing import Optional, Dict, Any
  from datetime import datetime

  class SignRequest(BaseModel):
      text: str
      document_title: Optional[str] = None
      document_url: Optional[str] = None
      document_type: str = "article"

  class SignResponse(BaseModel):
      success: bool
      document_id: str
      signed_text: str
      total_sentences: int
      verification_url: str

  class VerifyResponse(BaseModel):
      success: bool
      is_valid: bool
      signer_id: str
      organization_name: str
      signature_timestamp: Optional[datetime]
      manifest: Dict[str, Any]
      tampered: bool

  class LookupResponse(BaseModel):
      success: bool
      found: bool
      document_title: Optional[str] = None
      organization_name: Optional[str] = None
      publication_date: Optional[datetime] = None
      sentence_index: Optional[int] = None
      document_url: Optional[str] = None
  ```

- [ ] **1.1.4** Implement error handling
  ```python
  # encypher_enterprise/exceptions.py

  class EncypherError(Exception):
      """Base exception for Encypher SDK."""
      pass

  class AuthenticationError(EncypherError):
      """API key authentication failed."""
      pass

  class QuotaExceededError(EncypherError):
      """Monthly API quota exceeded."""
      pass

  class SigningError(EncypherError):
      """Content signing failed."""
      pass

  class VerificationError(EncypherError):
      """Content verification failed."""
      pass

  class APIError(EncypherError):
      """General API error."""

      def __init__(self, status_code: int, message: str, details: Optional[dict] = None):
          self.status_code = status_code
          self.message = message
          self.details = details
          super().__init__(f"{status_code}: {message}")
  ```

**Success Criteria:**
- Sync client works for all endpoints
- Async client works for all endpoints
- Proper error handling with retries
- Type hints throughout

**Estimated Time:** 2 days
**Cost:** $0 (development)

---

## PHASE 2: STREAMING SUPPORT (Week 1-2)

### 2.0 Streaming Signer Implementation

**Deliverable:** Real-time signing for streaming LLM responses

- [ ] **2.0.1** Implement streaming signer
  ```python
  # encypher_enterprise/streaming.py

  from typing import Iterator, AsyncIterator
  import re

  class StreamingSigner:
      """
      Real-time signer for streaming LLM responses.

      This class buffers incoming text chunks and signs complete
      sentences as they arrive, enabling real-time C2PA signing
      of streaming chat completions.

      Usage:
          signer = StreamingSigner(client)

          # Wrap OpenAI streaming
          for chunk in openai.chat.completions.create(stream=True):
              content = chunk.choices[0].delta.content
              if content:
                  signed_chunk = signer.process_chunk(content)
                  print(signed_chunk, end='')

          # Finalize at end
          final_text = signer.finalize()
      """

      def __init__(
          self,
          client: EncypherClient,
          buffer_size: int = 1000,
          sign_on_sentence: bool = True
      ):
          self.client = client
          self.buffer = ""
          self.signed_parts = []
          self.buffer_size = buffer_size
          self.sign_on_sentence = sign_on_sentence

      def process_chunk(self, chunk: str) -> str:
          """
          Process incoming chunk and return signed version.

          Buffers text until complete sentences are detected,
          then signs them.
          """
          self.buffer += chunk

          if self.sign_on_sentence:
              # Check for sentence boundaries
              sentences = re.split(r'([.!?])\s+', self.buffer)

              if len(sentences) > 1:
                  # We have complete sentences
                  complete_text = ''.join(sentences[:-1])
                  self.buffer = sentences[-1]

                  # Sign complete sentences
                  signed = self.client.sign(complete_text)
                  self.signed_parts.append(signed.signed_text)
                  return signed.signed_text

          elif len(self.buffer) >= self.buffer_size:
              # Buffer full, sign what we have
              signed = self.client.sign(self.buffer)
              self.signed_parts.append(signed.signed_text)
              self.buffer = ""
              return signed.signed_text

          return ""

      def finalize(self) -> str:
          """
          Finalize streaming and return complete signed text.
          """
          if self.buffer:
              # Sign remaining buffer
              signed = self.client.sign(self.buffer)
              self.signed_parts.append(signed.signed_text)

          return ''.join(self.signed_parts)


  class AsyncStreamingSigner:
      """Async version of StreamingSigner."""

      def __init__(self, client: AsyncEncypherClient, **kwargs):
          self.client = client
          self.buffer = ""
          self.signed_parts = []

      async def process_chunk(self, chunk: str) -> str:
          """Async process chunk."""
          # Same logic but with await
          ...

      async def finalize(self) -> str:
          """Async finalize."""
          ...
  ```

- [ ] **2.0.2** Add streaming generator wrapper
  ```python
  def sign_stream(
      client: EncypherClient,
      stream: Iterator[str],
      **kwargs
  ) -> Iterator[str]:
      """
      Wrap a text stream and sign content as it arrives.

      Args:
          client: EncypherClient instance
          stream: Iterator yielding text chunks
          **kwargs: Additional arguments for StreamingSigner

      Yields:
          Signed text chunks

      Example:
          # Wrap OpenAI stream
          stream = openai.chat.completions.create(
              model="gpt-4",
              messages=[...],
              stream=True
          )

          content_stream = (
              chunk.choices[0].delta.content
              for chunk in stream
              if chunk.choices[0].delta.content
          )

          for signed_chunk in sign_stream(client, content_stream):
              print(signed_chunk, end='')
      """
      signer = StreamingSigner(client, **kwargs)

      for chunk in stream:
          signed_chunk = signer.process_chunk(chunk)
          if signed_chunk:
              yield signed_chunk

      # Yield final signed content
      final = signer.finalize()
      if final:
          yield final


  async def async_sign_stream(
      client: AsyncEncypherClient,
      stream: AsyncIterator[str],
      **kwargs
  ) -> AsyncIterator[str]:
      """Async version of sign_stream."""
      signer = AsyncStreamingSigner(client, **kwargs)

      async for chunk in stream:
          signed_chunk = await signer.process_chunk(chunk)
          if signed_chunk:
              yield signed_chunk

      final = await signer.finalize()
      if final:
          yield final
  ```

**Success Criteria:**
- Streaming signer buffers and signs in real-time
- Both sync and async versions work
- Handles sentence boundaries correctly
- Minimal latency overhead

**Estimated Time:** 2 days
**Cost:** $0 (development)

---

## PHASE 3: FRAMEWORK INTEGRATIONS (Week 2)

### 3.0 LangChain Integration

**Deliverable:** LangChain callback handler for automatic signing

- [ ] **3.0.1** Implement LangChain callback
  ```python
  # encypher_enterprise/integrations/langchain.py

  from langchain.callbacks.base import BaseCallbackHandler
  from typing import Any, Dict, List, Optional

  class EncypherCallbackHandler(BaseCallbackHandler):
      """
      LangChain callback handler for automatic content signing.

      Usage:
          from langchain.chat_models import ChatOpenAI
          from encypher_enterprise import EncypherClient
          from encypher_enterprise.integrations.langchain import EncypherCallbackHandler

          client = EncypherClient(api_key="...")
          handler = EncypherCallbackHandler(client)

          llm = ChatOpenAI(callbacks=[handler])
          response = llm.invoke("Tell me about AI")

          # Response is automatically signed
          print(handler.get_signed_response())
      """

      def __init__(self, client: EncypherClient, auto_sign: bool = True):
          super().__init__()
          self.client = client
          self.auto_sign = auto_sign
          self.responses = []
          self.signed_responses = []

      def on_llm_end(self, response: Any, **kwargs: Any) -> None:
          """Called when LLM completes."""
          text = response.generations[0][0].text
          self.responses.append(text)

          if self.auto_sign:
              signed = self.client.sign(text)
              self.signed_responses.append(signed.signed_text)

      def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
          """Called on each streaming token."""
          # For streaming support
          pass

      def get_signed_response(self) -> Optional[str]:
          """Get the most recent signed response."""
          return self.signed_responses[-1] if self.signed_responses else None

      def get_all_signed_responses(self) -> List[str]:
          """Get all signed responses."""
          return self.signed_responses
  ```

---

### 3.1 OpenAI SDK Wrapper

**Deliverable:** Drop-in replacement for OpenAI SDK with automatic signing

- [ ] **3.1.1** Implement OpenAI wrapper
  ```python
  # encypher_enterprise/integrations/openai.py

  from openai import OpenAI
  from typing import Iterator

  class EncypherOpenAI:
      """
      OpenAI SDK wrapper with automatic C2PA signing.

      Usage:
          from encypher_enterprise.integrations.openai import EncypherOpenAI

          client = EncypherOpenAI(
              openai_api_key="sk-...",
              encypher_api_key="encypher_..."
          )

          # Normal OpenAI usage - automatically signed
          response = client.chat.completions.create(
              model="gpt-4",
              messages=[{"role": "user", "content": "Hello"}]
          )

          # Response content is signed with C2PA
          print(response.choices[0].message.content)

          # Streaming also works
          for chunk in client.chat.completions.create(
              model="gpt-4",
              messages=[...],
              stream=True
          ):
              print(chunk.choices[0].delta.content, end='')
      """

      def __init__(
          self,
          openai_api_key: str,
          encypher_api_key: str,
          encypher_base_url: str = "https://api.encypherai.com"
      ):
          self.openai_client = OpenAI(api_key=openai_api_key)
          self.encypher_client = EncypherClient(
              api_key=encypher_api_key,
              base_url=encypher_base_url
          )

          # Wrap OpenAI client
          self.chat = self._wrap_chat()

      def _wrap_chat(self):
          """Wrap chat completions with signing."""
          original_create = self.openai_client.chat.completions.create

          def wrapped_create(*args, **kwargs):
              stream = kwargs.get('stream', False)

              if stream:
                  # Handle streaming
                  response_stream = original_create(*args, **kwargs)
                  return self._sign_stream(response_stream)
              else:
                  # Handle non-streaming
                  response = original_create(*args, **kwargs)
                  return self._sign_response(response)

          # Create wrapper object
          class ChatWrapper:
              class CompletionsWrapper:
                  create = staticmethod(wrapped_create)
              completions = CompletionsWrapper()

          return ChatWrapper()

      def _sign_response(self, response):
          """Sign non-streaming response."""
          content = response.choices[0].message.content
          signed = self.encypher_client.sign(content)
          response.choices[0].message.content = signed.signed_text
          return response

      def _sign_stream(self, stream: Iterator) -> Iterator:
          """Sign streaming response."""
          signer = StreamingSigner(self.encypher_client)

          for chunk in stream:
              content = chunk.choices[0].delta.content
              if content:
                  signed_chunk = signer.process_chunk(content)
                  if signed_chunk:
                      chunk.choices[0].delta.content = signed_chunk
              yield chunk

          # Finalize
          final = signer.finalize()
          # Return final chunk with complete signed text if needed
  ```

---

## PHASE 4: CLI TOOL (Week 2)

### 4.0 Command-Line Interface

**Deliverable:** CLI tool for quick testing and batch operations

- [ ] **4.0.1** Implement CLI commands
  ```python
  # encypher_enterprise/cli/main.py

  import click
  from rich.console import Console
  from rich.table import Table
  from pathlib import Path

  console = Console()

  @click.group()
  @click.option('--api-key', envvar='ENCYPHER_API_KEY', required=True)
  @click.pass_context
  def cli(ctx, api_key):
      """Encypher Enterprise CLI"""
      ctx.obj = EncypherClient(api_key=api_key)

  @cli.command()
  @click.argument('text')
  @click.option('--title', help='Document title')
  @click.option('--type', default='article', help='Document type')
  @click.pass_obj
  def sign(client, text, title, type):
      """Sign content with C2PA manifest."""
      try:
          result = client.sign(text=text, title=title, document_type=type)
          console.print(f"✅ Signed successfully!", style="green")
          console.print(f"Document ID: {result.document_id}")
          console.print(f"Sentences: {result.total_sentences}")
          console.print(f"Verification URL: {result.verification_url}")
          console.print(f"\n[bold]Signed Text:[/bold]\n{result.signed_text}")
      except Exception as e:
          console.print(f"❌ Error: {e}", style="red")

  @cli.command()
  @click.argument('text')
  @click.pass_obj
  def verify(client, text):
      """Verify C2PA manifest."""
      try:
          result = client.verify(text)

          if result.is_valid:
              console.print("✅ Valid signature!", style="green")
          else:
              console.print("❌ Invalid signature (tampered)", style="red")

          table = Table(title="Verification Details")
          table.add_column("Field", style="cyan")
          table.add_column("Value", style="white")

          table.add_row("Valid", str(result.is_valid))
          table.add_row("Signer", result.organization_name)
          table.add_row("Timestamp", str(result.signature_timestamp))
          table.add_row("Tampered", str(result.tampered))

          console.print(table)
      except Exception as e:
          console.print(f"❌ Error: {e}", style="red")

  @cli.command()
  @click.argument('sentence')
  @click.pass_obj
  def lookup(client, sentence):
      """Look up sentence provenance."""
      try:
          result = client.lookup(sentence)

          if result.found:
              console.print("✅ Sentence found!", style="green")
              console.print(f"Document: {result.document_title}")
              console.print(f"Organization: {result.organization_name}")
              console.print(f"Published: {result.publication_date}")
              console.print(f"Sentence index: {result.sentence_index}")
          else:
              console.print("❌ Sentence not found", style="yellow")
      except Exception as e:
          console.print(f"❌ Error: {e}", style="red")

  @cli.command()
  @click.argument('file', type=click.Path(exists=True))
  @click.option('--title', help='Document title')
  @click.option('--output', '-o', help='Output file for signed content')
  @click.pass_obj
  def sign_file(client, file, title, output):
      """Sign content from file."""
      text = Path(file).read_text()

      try:
          result = client.sign(text=text, title=title or Path(file).name)

          if output:
              Path(output).write_text(result.signed_text)
              console.print(f"✅ Signed content written to {output}", style="green")
          else:
              console.print(result.signed_text)

          console.print(f"\nDocument ID: {result.document_id}")
          console.print(f"Sentences: {result.total_sentences}")
      except Exception as e:
          console.print(f"❌ Error: {e}", style="red")

  @cli.command()
  @click.pass_obj
  def stats(client):
      """Show organization statistics."""
      try:
          result = client.get_stats()

          table = Table(title=f"Statistics - {result.organization_name}")
          table.add_column("Metric", style="cyan")
          table.add_column("Value", style="white")

          table.add_row("Tier", result.tier)
          table.add_row("Documents Signed", str(result.usage.documents_signed))
          table.add_row("Sentences Signed", str(result.usage.sentences_signed))
          table.add_row("API Calls (Month)", str(result.usage.api_calls_this_month))
          table.add_row("Monthly Quota", str(result.usage.monthly_quota))
          table.add_row("Quota Remaining", str(result.usage.quota_remaining))

          console.print(table)
      except Exception as e:
          console.print(f"❌ Error: {e}", style="red")

  if __name__ == '__main__':
      cli()
  ```

**Success Criteria:**
- CLI works for all operations
- Rich terminal output
- File I/O support
- Environment variable configuration

**Estimated Time:** 1 day
**Cost:** $0 (development)

---

## PHASE 5: DOCUMENTATION & EXAMPLES (Week 3)

### 5.0 Documentation

**Deliverable:** Complete SDK documentation with examples

- [ ] **5.0.1** Create comprehensive README
- [ ] **5.0.2** Write usage examples for all integrations
- [ ] **5.0.3** Create API reference documentation
- [ ] **5.0.4** Write integration guides (LangChain, OpenAI, etc.)

**Estimated Time:** 1 day
**Cost:** $0 (documentation)

---

## TIMELINE SUMMARY

**Week 1:** Core SDK + Streaming (1.0-2.0)
**Week 2:** Integrations + CLI (3.0-4.0)
**Week 3:** Documentation + Testing (5.0)

**Total Development:** 2-3 weeks

---

## SUCCESS METRICS

- [ ] SDK published to PyPI
- [ ] 100% type hinted
- [ ] 90%+ test coverage
- [ ] <50ms overhead for signing
- [ ] Works with LangChain, OpenAI, LiteLLM
- [ ] CLI tool functional
- [ ] Comprehensive documentation
- [ ] 5+ usage examples

---

## NEXT STEPS

1. Create SDK project structure
2. Implement core client (sync + async)
3. Implement streaming signer
4. Add framework integrations
5. Build CLI tool
6. Write documentation and examples
7. Publish to PyPI

**Status:** Ready to implement
