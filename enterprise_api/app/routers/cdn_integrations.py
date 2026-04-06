"""
CDN Integration router.

Provides config CRUD for CDN log-ingestion integrations and a public
webhook endpoint that Cloudflare Logpush (and future CDN providers) POST
batches of access logs to.

Authenticated routes (require org API key):
    POST   /cdn/cloudflare           -- create or update integration
    GET    /cdn/cloudflare           -- get current config (secret masked)
    DELETE /cdn/cloudflare           -- remove integration

Public webhook (HMAC auth via x-cf-secret header):
    POST   /cdn/cloudflare/webhook/{org_id}
"""

import logging

import bcrypt
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Request, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization_dep
from app.models.cdn_integration import CdnIntegration
from app.schemas.cdn_schemas import CdnIntegrationCreate, CdnIntegrationResponse, CdnWorkerConfigResponse, LogpushIngestResult
from app.services.logpush_service import ingest_logpush_batch

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cdn", tags=["CDN Integrations"])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PROVIDER_CLOUDFLARE = "cloudflare"
_MAX_BODY_BYTES = 10 * 1024 * 1024  # 10 MB per batch


def _hash_secret(secret: str) -> str:
    """Hash the webhook secret with bcrypt for storage."""
    return bcrypt.hashpw(secret.encode(), bcrypt.gensalt()).decode()


def _verify_secret(secret: str, hashed: str) -> bool:
    """Constant-time bcrypt comparison."""
    try:
        return bcrypt.checkpw(secret.encode(), hashed.encode())
    except Exception:
        return False


def _make_webhook_url(request: Request, org_id: str) -> str:
    """Build the full webhook URL to show the publisher in the dashboard."""
    base = str(request.base_url).rstrip("/")
    return f"{base}/api/v1/cdn/cloudflare/webhook/{org_id}"


# ---------------------------------------------------------------------------
# Authenticated config endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/cloudflare",
    status_code=status.HTTP_200_OK,
    summary="Create or update Cloudflare Logpush integration",
    description="""
Save (or replace) the Cloudflare Logpush configuration for the authenticated
organization. Returns the webhook URL to paste into the Cloudflare Logpush
job destination field and the truncated zone_id for confirmation.

The webhook_secret is stored hashed (bcrypt) and cannot be retrieved after
creation. Store it safely before submitting.
    """,
    response_model=CdnIntegrationResponse,
)
async def save_cdn_integration(
    payload: CdnIntegrationCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    org_context: dict = Depends(get_current_organization_dep),
) -> CdnIntegrationResponse:
    org_id: str = org_context["organization_id"]

    # Upsert: delete existing if present, then insert fresh
    existing = await db.execute(
        select(CdnIntegration).where(
            and_(
                CdnIntegration.organization_id == org_id,
                CdnIntegration.provider == _PROVIDER_CLOUDFLARE,
            )
        )
    )
    existing_row = existing.scalar_one_or_none()
    if existing_row is not None:
        await db.delete(existing_row)
        await db.flush()

    secret_hash = _hash_secret(payload.webhook_secret)
    integration = CdnIntegration(
        organization_id=org_id,
        provider=_PROVIDER_CLOUDFLARE,
        zone_id=payload.zone_id,
        webhook_secret_hash=secret_hash,
        enabled=payload.enabled,
    )
    db.add(integration)
    await db.flush()
    await db.refresh(integration)

    return CdnIntegrationResponse(
        id=str(integration.id),
        provider=integration.provider,
        zone_id=integration.zone_id,
        enabled=integration.enabled,
        created_at=integration.created_at,
        updated_at=integration.updated_at,
        webhook_url=_make_webhook_url(request, org_id),
    )


@router.get(
    "/cloudflare",
    status_code=status.HTTP_200_OK,
    summary="Get current Cloudflare Logpush integration config",
    description="Retrieve the current Cloudflare Logpush integration configuration for the authenticated organization.",
    response_model=CdnIntegrationResponse,
)
async def get_cdn_integration(
    request: Request,
    db: AsyncSession = Depends(get_db),
    org_context: dict = Depends(get_current_organization_dep),
) -> CdnIntegrationResponse:
    org_id: str = org_context["organization_id"]

    result = await db.execute(
        select(CdnIntegration).where(
            and_(
                CdnIntegration.organization_id == org_id,
                CdnIntegration.provider == _PROVIDER_CLOUDFLARE,
            )
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Cloudflare integration configured for this organization.",
        )

    return CdnIntegrationResponse(
        id=str(row.id),
        provider=row.provider,
        zone_id=row.zone_id,
        enabled=row.enabled,
        created_at=row.created_at,
        updated_at=row.updated_at,
        webhook_url=_make_webhook_url(request, org_id),
    )


@router.delete(
    "/cloudflare",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove Cloudflare Logpush integration",
    description="Remove the Cloudflare Logpush integration configuration for the authenticated organization.",
)
async def delete_cdn_integration(
    db: AsyncSession = Depends(get_db),
    org_context: dict = Depends(get_current_organization_dep),
) -> None:
    org_id: str = org_context["organization_id"]

    result = await db.execute(
        select(CdnIntegration).where(
            and_(
                CdnIntegration.organization_id == org_id,
                CdnIntegration.provider == _PROVIDER_CLOUDFLARE,
            )
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Cloudflare integration found.",
        )

    await db.delete(row)
    await db.flush()


# ---------------------------------------------------------------------------
# Worker config generation
# ---------------------------------------------------------------------------

# Inline Cloudflare Worker template (placeholder; can be replaced with a real
# file read from integrations/cloudflare-workers/cdn-provenance-worker.js
# once the file exists).
_CF_WORKER_TEMPLATE = """\
/**
 * Encypher CDN Provenance Worker
 *
 * Intercepts image responses and calls the Encypher provenance API to
 * verify / register images transparently at the CDN edge.
 *
 * Configuration is injected at deploy time by the Encypher dashboard.
 * Do NOT commit credentials to source control.
 */
const ENCYPHER_API_URL = "{{ENCYPHER_API_URL}}";
const ORG_ID = "{{ORG_ID}}";
const INTEGRATION_ID = "{{INTEGRATION_ID}}";

export default {
  async fetch(request, env, ctx) {
    const response = await fetch(request);
    const contentType = response.headers.get("content-type") || "";
    if (!contentType.startsWith("image/")) {
      return response;
    }
    // Background provenance check — non-blocking
    ctx.waitUntil(
      checkProvenance(request.url, response.clone(), env)
    );
    return response;
  },
};

async function checkProvenance(url, response, env) {
  try {
    const body = await response.arrayBuffer();
    const formData = new FormData();
    formData.append("file", new Blob([body]), "image");
    formData.append("original_url", url);
    await fetch(`${ENCYPHER_API_URL}/api/v1/cdn/images/register`, {
      method: "POST",
      headers: {
        "X-Org-ID": ORG_ID,
        "X-Integration-ID": INTEGRATION_ID,
      },
      body: formData,
    });
  } catch (_) {
    // Best-effort only
  }
}
"""

_WRANGLER_TOML_TEMPLATE = """\
name = "encypher-cdn-provenance-{{INTEGRATION_ID}}"
main = "worker.js"
compatibility_date = "2024-01-01"

[vars]
ENCYPHER_API_URL = "{{ENCYPHER_API_URL}}"
ORG_ID = "{{ORG_ID}}"
INTEGRATION_ID = "{{INTEGRATION_ID}}"
"""


@router.post(
    "/integrations/{integration_id}/generate-worker-config",
    response_model=CdnWorkerConfigResponse,
    status_code=200,
    summary="Generate Cloudflare Worker config for CDN provenance",
    description="""
Generate a ready-to-deploy Cloudflare Worker script and wrangler.toml for the
specified CDN integration, with API URL, org ID, and integration ID
substituted.
    """,
)
async def generate_worker_config(
    integration_id: str = Path(..., description="CDN integration UUID"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    org_context: dict = Depends(get_current_organization_dep),
) -> CdnWorkerConfigResponse:
    org_id: str = org_context["organization_id"]

    # Verify the integration belongs to this org
    result = await db.execute(
        select(CdnIntegration).where(
            and_(
                CdnIntegration.id == integration_id,
                CdnIntegration.organization_id == org_id,
            )
        )
    )
    integration = result.scalar_one_or_none()
    if integration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CDN integration not found.",
        )

    base_url = str(request.base_url).rstrip("/") if request else "https://api.encypher.com"

    # Attempt to load external template file; fall back to embedded template
    import os

    template_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "integrations",
        "cloudflare-workers",
        "cdn-provenance-worker.js",
    )
    worker_template = _CF_WORKER_TEMPLATE
    if os.path.isfile(template_path):
        try:
            with open(template_path) as f:
                worker_template = f.read()
        except OSError:
            pass  # Fall through to embedded template

    def _substitute(template: str) -> str:
        return template.replace("{{ENCYPHER_API_URL}}", base_url).replace("{{ORG_ID}}", org_id).replace("{{INTEGRATION_ID}}", str(integration.id))

    return CdnWorkerConfigResponse(
        worker_script=_substitute(worker_template),
        wrangler_toml=_substitute(_WRANGLER_TOML_TEMPLATE),
        integration_id=str(integration.id),
    )


# ---------------------------------------------------------------------------
# Public Logpush webhook
# ---------------------------------------------------------------------------


@router.post(
    "/cloudflare/webhook/{org_id}",
    status_code=status.HTTP_200_OK,
    summary="Cloudflare Logpush webhook receiver",
    description="""
Public endpoint that Cloudflare Logpush POSTs batches of NDJSON access logs
to. Authentication is performed via the x-cf-secret header, which must
contain the plaintext secret that was registered via the config endpoint.

Cloudflare Logpush configuration:
    Destination: POST https://<api-host>/api/v1/cdn/cloudflare/webhook/{org_id}
    Custom header: x-cf-secret: <your-secret>
    Log format: HTTP requests (NDJSON)
    """,
    response_model=LogpushIngestResult,
    include_in_schema=False,  # internal webhook, not in public OpenAPI docs
)
async def cloudflare_webhook(
    org_id: str = Path(..., description="Organization ID"),
    request: Request = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
) -> LogpushIngestResult:
    # ---- Authenticate via x-cf-secret header ----
    incoming_secret = request.headers.get("x-cf-secret", "")
    if not incoming_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing x-cf-secret header.",
        )

    # Look up the integration config
    result = await db.execute(
        select(CdnIntegration).where(
            and_(
                CdnIntegration.organization_id == org_id,
                CdnIntegration.provider == _PROVIDER_CLOUDFLARE,
                CdnIntegration.enabled.is_(True),
            )
        )
    )
    integration = result.scalar_one_or_none()
    if integration is None:
        # Return 401 rather than 404 to avoid leaking org existence
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or disabled integration.",
        )

    if not _verify_secret(incoming_secret, integration.webhook_secret_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret.",
        )

    # ---- Read body (guard against oversized payloads) ----
    body = await request.body()
    if len(body) > _MAX_BODY_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Payload exceeds {_MAX_BODY_BYTES // (1024 * 1024)} MB limit.",
        )

    # ---- Ingest ----
    result_summary = await ingest_logpush_batch(
        organization_id=org_id,
        body=body,
        db=db,
    )

    logger.info(
        "logpush: org=%s lines=%d bots=%d bypass=%d events=%d errors=%d",
        org_id,
        result_summary.lines_received,
        result_summary.bots_detected,
        result_summary.bypass_flags,
        result_summary.events_created,
        result_summary.errors,
    )

    return result_summary
