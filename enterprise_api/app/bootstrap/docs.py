from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse, Response

from app.config import settings

_INTERNAL_DOC_TAGS = {
    "Admin",
    "Licensing",
    "Kafka",
    "Provisioning",
    "Audit",
    "Team Management",
}

_DOCS_PAGE_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Encypher Enterprise API</title>
  <link rel="icon" href="https://encypher.com/favicon.ico" />
  <link rel="stylesheet" href="/docs/assets/design-system.css" />
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
  <style>
    :root {
      --header-bg: #1b2f50;
      --accent: #2a87c4;
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: var(--font-sans, \"Roboto\", system-ui, sans-serif); background: hsl(var(--background, 0 0% 100%)); color: hsl(var(--foreground, 222 47% 20%)); }
    .header { background: var(--header-bg); color: #fff; padding: 24px 32px; }
    .header-inner { max-width: 1400px; margin: 0 auto; display: flex; align-items: center; gap: 24px; flex-wrap: wrap; }
    .logo { height: 40px; width: auto; }
    .header h1 { margin: 0; font-size: 1.5rem; font-weight: 600; }
    .header-desc { margin: 0; opacity: 0.85; font-size: 0.95rem; flex-basis: 100%; }
    .intro { max-width: 1400px; margin: 0 auto; padding: 24px 32px; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
    .intro-card { background: hsl(var(--card, 0 0% 100%)); border: 1px solid hsl(var(--border, 214 32% 91%)); border-radius: 12px; padding: 20px; }
    .intro-card h3 { margin: 0 0 8px; font-size: 1rem; color: var(--accent); }
    .intro-card p { margin: 0; font-size: 0.9rem; line-height: 1.5; color: hsl(var(--muted-foreground, 215 16% 47%)); }
    .swagger-container { max-width: 1400px; margin: 0 auto; padding: 0 32px 48px; }
    .swagger-ui .topbar { display: none; }
    .swagger-ui .info { margin: 20px 0 0; }
    .swagger-ui .info hgroup.main { margin: 0; }
    .swagger-ui .info .title { font-size: 1.25rem; }
  </style>
</head>
<body>
  <header class="header">
    <div class="header-inner">
      <img src="https://encypher.com/encypher_full_logo_white.svg" alt="Encypher" class="logo" />
      <h1>Enterprise API</h1>
      <p class="header-desc">C2PA-compliant content signing and verification infrastructure for publishers, legal/finance firms, AI labs, and enterprises.</p>
    </div>
  </header>

  <section class="intro">
    <div class="intro-card">
      <h3>Public Endpoints</h3>
      <p>Verify signed content, validate manifests, and perform public C2PA verification workflows. No authentication required.</p>
    </div>
    <div class="intro-card">
      <h3>Publisher Endpoints</h3>
      <p>Sign content with C2PA manifests, batch processing, streaming signatures, and other authenticated operations.</p>
    </div>
    <div class="intro-card">
      <h3>Getting Started</h3>
      <p>Obtain an API key from <a href="https://dashboard.encypher.com" style="color:var(--accent);">dashboard.encypher.com</a>, then use the endpoints below.</p>
    </div>
    <div class="intro-card">
      <h3>Client SDKs</h3>
      <p>Auto-generated from this API spec: <a href="https://github.com/encypherai/sdk-python" style="color:var(--accent);">Python</a>, <a href="https://github.com/encypherai/sdk-typescript" style="color:var(--accent);">TypeScript</a>, <a href="https://github.com/encypherai/sdk-go" style="color:var(--accent);">Go</a>, <a href="https://github.com/encypherai/sdk-rust" style="color:var(--accent);">Rust</a>. Always in sync with the API.</p>
    </div>
    <div class="intro-card">
      <h3>Open-Source Package</h3>
      <p>Looking for the AGPL-licensed <code>encypher-ai</code> Python package? See <a href="https://docs.encypher.com" style="color:var(--accent);">docs.encypher.com</a>.</p>
    </div>
  </section>

  <div class="swagger-container">
    <div id="swagger-ui"></div>
  </div>

  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => {
      SwaggerUIBundle({
        url: "/docs/openapi.json",
        dom_id: "#swagger-ui",
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
        layout: "BaseLayout",
        deepLinking: true,
        defaultModelsExpandDepth: 0,
      });
    };
  </script>
</body>
</html>
"""


def _collect_schema_refs(obj: object, out: set[str]) -> None:
    if isinstance(obj, dict):
        ref = obj.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            out.add(ref.removeprefix("#/components/schemas/"))
        for value in obj.values():
            _collect_schema_refs(value, out)
    elif isinstance(obj, list):
        for item in obj:
            _collect_schema_refs(item, out)


def _prune_schemas(openapi: dict) -> dict:
    components = openapi.get("components")
    if not isinstance(components, dict):
        return openapi
    schemas = components.get("schemas")
    if not isinstance(schemas, dict):
        return openapi

    referenced: set[str] = set()
    _collect_schema_refs(openapi.get("paths", {}), referenced)

    kept: dict[str, object] = {}
    stack = list(referenced)
    while stack:
        name = stack.pop()
        if name in kept:
            continue
        schema = schemas.get(name)
        if schema is None:
            continue
        kept[name] = schema
        before = len(referenced)
        _collect_schema_refs(schema, referenced)
        if len(referenced) > before:
            for new_name in referenced:
                if new_name not in kept:
                    stack.append(new_name)

    components["schemas"] = kept
    return openapi


def _filter_openapi_for_public(openapi: dict) -> dict:
    paths = openapi.get("paths")
    if not isinstance(paths, dict):
        return openapi

    filtered_paths: dict[str, object] = {}
    for path, ops in paths.items():
        if not isinstance(ops, dict):
            continue
        kept_ops: dict[str, object] = {}
        for method, op in ops.items():
            if not isinstance(op, dict):
                continue
            tags = op.get("tags", [])
            if any(tag in _INTERNAL_DOC_TAGS for tag in (tags or [])):
                continue
            kept_ops[method] = op
        if kept_ops:
            filtered_paths[path] = kept_ops

    openapi["paths"] = filtered_paths

    tags = openapi.get("tags")
    if isinstance(tags, list):
        openapi["tags"] = [tag for tag in tags if isinstance(tag, dict) and tag.get("name") not in _INTERNAL_DOC_TAGS]

    return _prune_schemas(openapi)


def build_public_openapi(app: FastAPI) -> JSONResponse:
    base = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    return JSONResponse(_filter_openapi_for_public(base))


def build_public_docs_html() -> HTMLResponse:
    return HTMLResponse(_DOCS_PAGE_HTML, media_type="text/html")


def register_docs_routes(app: FastAPI, require_super_admin_dep) -> None:
    @app.get("/docs/assets/design-system.css", include_in_schema=False)
    async def docs_design_system_css() -> Response:
        if not settings.enable_public_api_docs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
        repo_root = Path(__file__).resolve().parents[2]
        theme_path = repo_root / "packages" / "design-system" / "src" / "styles" / "theme.css"
        globals_path = repo_root / "packages" / "design-system" / "src" / "styles" / "globals.css"

        theme_css = theme_path.read_text(encoding="utf-8")
        globals_css = globals_path.read_text(encoding="utf-8")
        globals_css = "\n".join(
            line for line in globals_css.splitlines() if "@import './theme.css'" not in line and '@import "./theme.css"' not in line
        )

        bundled = f"{theme_css}\n\n{globals_css}\n"
        return Response(content=bundled, media_type="text/css")

    @app.get("/docs/assets/{filename:path}", include_in_schema=False)
    async def docs_static_asset(filename: str) -> Response:
        if not settings.enable_public_api_docs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
        repo_root = Path(__file__).resolve().parents[2]
        asset_path = repo_root / "apps" / "marketing-site" / "public" / filename

        if not asset_path.exists() or not asset_path.is_file():
            raise HTTPException(status_code=404, detail="Asset not found")

        suffix = asset_path.suffix.lower()
        content_types = {
            ".svg": "image/svg+xml",
            ".png": "image/png",
            ".ico": "image/x-icon",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }
        content_type = content_types.get(suffix, "application/octet-stream")

        content = asset_path.read_bytes()
        return Response(content=content, media_type=content_type)

    @app.get("/docs", include_in_schema=False)
    async def docs_landing(request: Request) -> HTMLResponse:
        if not settings.enable_public_api_docs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
        return build_public_docs_html()

    @app.get("/docs/openapi.json", include_in_schema=False)
    async def public_openapi(request: Request) -> JSONResponse:
        if not settings.enable_public_api_docs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
        return build_public_openapi(app)

    @app.get("/docs/swagger", include_in_schema=False)
    async def public_swagger_ui(request: Request) -> HTMLResponse:
        if not settings.enable_public_api_docs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
        return get_swagger_ui_html(
            openapi_url="/docs/openapi.json",
            title="Encypher Enterprise API - Docs",
        )

    @app.get(
        "/internal/openapi.json",
        include_in_schema=False,
        dependencies=[Depends(require_super_admin_dep)],
    )
    async def internal_openapi() -> JSONResponse:
        base = get_openapi(
            title=f"{app.title} (Internal)",
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        return JSONResponse(base)

    @app.get("/internal/docs", include_in_schema=False, dependencies=[Depends(require_super_admin_dep)])
    async def internal_swagger_ui() -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url="/internal/openapi.json",
            title="Encypher Enterprise API - Internal Docs",
        )
