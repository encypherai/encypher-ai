"""
Streaming support for real-time LLM content signing.
"""
import re
from typing import Iterator, AsyncIterator, List
from .client import EncypherClient
from .async_client import AsyncEncypherClient
from .exceptions import StreamingError


class StreamingSigner:
    """
    Real-time signer for streaming LLM responses.

    Buffers incoming text chunks and signs complete sentences as they arrive,
    enabling real-time C2PA signing of streaming chat completions.

    Example:
        >>> signer = StreamingSigner(client)
        >>> for chunk in openai_stream:
        ...     content = chunk.choices[0].delta.content
        ...     if content:
        ...         signed_chunk = signer.process_chunk(content)
        ...         if signed_chunk:
        ...             print(signed_chunk, end='')
        >>> final_text = signer.finalize()
    """

    def __init__(
        self,
        client: EncypherClient,
        buffer_size: int = 1000,
        sign_on_sentence: bool = True,
        **sign_kwargs
    ):
        """
        Initialize streaming signer.

        Args:
            client: EncypherClient instance
            buffer_size: Maximum buffer size before forcing a sign
            sign_on_sentence: Sign when complete sentences are detected
            **sign_kwargs: Additional arguments passed to client.sign()
        """
        self.client = client
        self.buffer = ""
        self.signed_parts: List[str] = []
        self.buffer_size = buffer_size
        self.sign_on_sentence = sign_on_sentence
        self.sign_kwargs = sign_kwargs

    def process_chunk(self, chunk: str) -> str:
        """
        Process incoming chunk and return signed version if available.

        Args:
            chunk: Text chunk from stream

        Returns:
            Signed text if a sentence boundary was reached, empty string otherwise
        """
        self.buffer += chunk

        if self.sign_on_sentence:
            # Check for sentence boundaries (., !, ?)
            sentences = re.split(r'([.!?])\s+', self.buffer)

            if len(sentences) > 1:
                # We have complete sentences
                complete_text = ''.join(sentences[:-1])
                self.buffer = sentences[-1]

                # Sign complete sentences
                try:
                    signed = self.client.sign(complete_text, **self.sign_kwargs)
                    self.signed_parts.append(signed.signed_text)
                    return signed.signed_text
                except Exception as e:
                    raise StreamingError(f"Failed to sign chunk: {e}")

        elif len(self.buffer) >= self.buffer_size:
            # Buffer full, sign what we have
            try:
                signed = self.client.sign(self.buffer, **self.sign_kwargs)
                self.signed_parts.append(signed.signed_text)
                self.buffer = ""
                return signed.signed_text
            except Exception as e:
                raise StreamingError(f"Failed to sign chunk: {e}")

        return ""

    def finalize(self) -> str:
        """
        Finalize streaming and return complete signed text.

        Returns:
            Complete signed text from all chunks
        """
        if self.buffer:
            # Sign remaining buffer
            try:
                signed = self.client.sign(self.buffer, **self.sign_kwargs)
                self.signed_parts.append(signed.signed_text)
            except Exception as e:
                raise StreamingError(f"Failed to sign final chunk: {e}")

        return ''.join(self.signed_parts)


class AsyncStreamingSigner:
    """
    Async version of StreamingSigner for async LLM streams.

    Example:
        >>> signer = AsyncStreamingSigner(async_client)
        >>> async for chunk in openai_async_stream:
        ...     content = chunk.choices[0].delta.content
        ...     if content:
        ...         signed_chunk = await signer.process_chunk(content)
        ...         if signed_chunk:
        ...             print(signed_chunk, end='')
        >>> final_text = await signer.finalize()
    """

    def __init__(
        self,
        client: AsyncEncypherClient,
        buffer_size: int = 1000,
        sign_on_sentence: bool = True,
        **sign_kwargs
    ):
        """
        Initialize async streaming signer.

        Args:
            client: AsyncEncypherClient instance
            buffer_size: Maximum buffer size
            sign_on_sentence: Sign when complete sentences are detected
            **sign_kwargs: Additional arguments for signing
        """
        self.client = client
        self.buffer = ""
        self.signed_parts: List[str] = []
        self.buffer_size = buffer_size
        self.sign_on_sentence = sign_on_sentence
        self.sign_kwargs = sign_kwargs

    async def process_chunk(self, chunk: str) -> str:
        """
        Async process incoming chunk.

        Args:
            chunk: Text chunk from stream

        Returns:
            Signed text if available
        """
        self.buffer += chunk

        if self.sign_on_sentence:
            sentences = re.split(r'([.!?])\s+', self.buffer)

            if len(sentences) > 1:
                complete_text = ''.join(sentences[:-1])
                self.buffer = sentences[-1]

                try:
                    signed = await self.client.sign(complete_text, **self.sign_kwargs)
                    self.signed_parts.append(signed.signed_text)
                    return signed.signed_text
                except Exception as e:
                    raise StreamingError(f"Failed to sign chunk: {e}")

        elif len(self.buffer) >= self.buffer_size:
            try:
                signed = await self.client.sign(self.buffer, **self.sign_kwargs)
                self.signed_parts.append(signed.signed_text)
                self.buffer = ""
                return signed.signed_text
            except Exception as e:
                raise StreamingError(f"Failed to sign chunk: {e}")

        return ""

    async def finalize(self) -> str:
        """
        Async finalize streaming.

        Returns:
            Complete signed text
        """
        if self.buffer:
            try:
                signed = await self.client.sign(self.buffer, **self.sign_kwargs)
                self.signed_parts.append(signed.signed_text)
            except Exception as e:
                raise StreamingError(f"Failed to sign final chunk: {e}")

        return ''.join(self.signed_parts)


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
        >>> content_stream = (
        ...     chunk.choices[0].delta.content
        ...     for chunk in openai_stream
        ...     if chunk.choices[0].delta.content
        ... )
        >>> for signed_chunk in sign_stream(client, content_stream):
        ...     print(signed_chunk, end='')
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
    """
    Async wrap a text stream and sign content as it arrives.

    Args:
        client: AsyncEncypherClient instance
        stream: Async iterator yielding text chunks
        **kwargs: Additional arguments for AsyncStreamingSigner

    Yields:
        Signed text chunks

    Example:
        >>> async for signed_chunk in async_sign_stream(async_client, async_stream):
        ...     print(signed_chunk, end='')
    """
    signer = AsyncStreamingSigner(client, **kwargs)

    async for chunk in stream:
        signed_chunk = await signer.process_chunk(chunk)
        if signed_chunk:
            yield signed_chunk

    # Yield final signed content
    final = await signer.finalize()
    if final:
        yield final
