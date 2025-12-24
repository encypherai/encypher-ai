"""API endpoints for minimal signed embeddings."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.api_key_auth import require_embedding_permission
from app.schemas.embeddings import EncodeWithEmbeddingsRequest, EncodeWithEmbeddingsResponse
from app.services.embedding_executor import encode_document_with_embeddings

router = APIRouter(prefix="/enterprise/embeddings", tags=["Enterprise - Embeddings"])


async def _do_encode_with_embeddings(
    request: EncodeWithEmbeddingsRequest,
    db: AsyncSession,
    organization: dict,
) -> EncodeWithEmbeddingsResponse:
    """Core encoding logic shared by both endpoints."""
    return await encode_document_with_embeddings(request=request, organization=organization, db=db)


@router.post(
    "/encode-with-embeddings",
    response_model=EncodeWithEmbeddingsResponse,
    status_code=status.HTTP_201_CREATED,
)
async def encode_with_embeddings(
    request: EncodeWithEmbeddingsRequest,
    db: AsyncSession = Depends(get_db),
    organization: dict = Depends(require_embedding_permission),
) -> EncodeWithEmbeddingsResponse:
    """
    Encode a document with invisible embeddings.

    **Alias:** POST /enterprise/sign/advanced
    """
    return await _do_encode_with_embeddings(request, db, organization)


@router.post(
    "/sign/advanced",
    response_model=EncodeWithEmbeddingsResponse,
    status_code=status.HTTP_201_CREATED,
)
async def sign_advanced(
    request: EncodeWithEmbeddingsRequest,
    db: AsyncSession = Depends(get_db),
    organization: dict = Depends(require_embedding_permission),
) -> EncodeWithEmbeddingsResponse:
    """
    Sign a document with advanced invisible embeddings.

    This is an alias for POST /enterprise/embeddings/encode-with-embeddings
    with a clearer name. Creates C2PA-compliant invisible signatures.

    Requires Professional or Enterprise tier.
    """
    return await _do_encode_with_embeddings(request, db, organization)

