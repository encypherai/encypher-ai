"""API endpoints for minimal signed embeddings."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.api_key_auth import require_embedding_permission
from app.schemas.embeddings import EncodeWithEmbeddingsRequest, EncodeWithEmbeddingsResponse
from app.services.embedding_executor import encode_document_with_embeddings

router = APIRouter(prefix="/enterprise/embeddings", tags=["Enterprise - Embeddings"])


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
    """Encode a document with invisible embeddings."""

    return await encode_document_with_embeddings(request=request, organization=organization, db=db)

