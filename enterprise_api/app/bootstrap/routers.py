from fastapi import FastAPI

from app.api.v1.api import api_router as api_v1_router
from app.routers import (
    account,
    admin,
    audit,
    batch,
    byok,
    cdn_analytics,
    cdn_integrations,
    cdn_provenance,
    chat,
    coalition,
    discovery,
    documents,
    integrations,
    keys,
    licensing,
    lookup,
    notices,
    onboarding,
    organizations_proxy,
    partner,
    rich_signing,
    rights,
    rights_licensing,
    signing,
    streaming,
    team,
    tools,
    usage,
    verification,
    webhooks,
)
from app.routers import status as status_router

ROUTER_SPECS = [
    (account.router, "/api/v1", ["Account"]),
    (admin.router, "/api/v1", ["Admin"]),
    (byok.router, "/api/v1", ["BYOK"]),
    (documents.router, "/api/v1", ["Documents"]),
    (keys.router, "/api/v1", ["API Keys"]),
    (webhooks.router, "/api/v1", ["Webhooks"]),
    (signing.router, "/api/v1", ["Signing"]),
    (rich_signing.router, "/api/v1", ["Rich Signing"]),
    (verification.router, "/api/v1", ["Verification"]),
    (lookup.router, "/api/v1", ["Lookup"]),
    (onboarding.router, "/api/v1/onboarding", ["Onboarding"]),
    (streaming.router, "/api/v1", ["Streaming"]),
    (chat.router, "/api/v1", ["Chat"]),
    (licensing.router, "/api/v1", ["Licensing"]),
    (usage.router, "/api/v1", ["Usage"]),
    (audit.router, "/api/v1", ["Audit"]),
    (team.router, "/api/v1", ["Team Management"]),
    (team.invite_router, "/api/v1", ["Team Invites"]),
    (coalition.router, "/api/v1", ["Coalition"]),
    (status_router.router, "/api/v1", ["Status & Revocation"]),
    (batch.router, None, None),
    (tools.router, "/api/v1", ["Public Tools"]),
    (organizations_proxy.router, "/api/v1", ["Organizations Proxy"]),
    (integrations.router, "/api/v1", ["Integrations"]),
    (cdn_analytics.router, "/api/v1", ["CDN Analytics"]),
    (cdn_integrations.router, "/api/v1", ["CDN Integrations"]),
    (cdn_provenance.router, "/api/v1", ["CDN Provenance"]),
    (cdn_provenance.well_known_router, None, ["CDN Provenance"]),
    (rights.router, "/api/v1", ["Rights Management"]),
    (notices.router, "/api/v1", ["Formal Notices"]),
    (rights_licensing.router, "/api/v1", ["Rights Licensing Transactions"]),
    (partner.router, "/api/v1", ["Partner"]),
    (discovery.router, None, ["Discovery"]),
    (api_v1_router, "/api/v1", None),
]


def register_application_routers(app: FastAPI) -> None:
    for router, prefix, tags in ROUTER_SPECS:
        kwargs: dict[str, object] = {}
        if prefix is not None:
            kwargs["prefix"] = prefix
        if tags is not None:
            kwargs["tags"] = tags
        app.include_router(router, **kwargs)
