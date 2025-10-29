# Compliance Readiness Dashboard

The dashboard pairs operational analytics with Encypher's Enterprise API (see `enterprise_api/docs/API.md`) to sign, verify, and audit AI-generated assets. The backend orchestrates requests to the Enterprise API so every feature mirrors the public contract exposed under `/api/v1`.

## Architecture

- **Frontend** (`frontend/`): Next.js 13 app router project (React, TypeScript, Tailwind).
- **Backend** (`backend/`): FastAPI service responsible for auth, policy validation ingest, and proxying all signing operations through the Enterprise API.
- **Enterprise API** (`../enterprise_api`): Preview C2PA service that performs signing/verification via the local `encypher-ai` package.

Refer to `enterprise_api/docs/API.md` for the canonical endpoint reference. The dashboard uses:

- `POST /api/v1/sign` for single document signing.
- `POST /api/v1/verify` for verification flows (profile reports).
- `GET /api/v1/dashboard` for organization usage metrics (future work).
- `POST /api/v1/sign` repeatedly from our directory signing workflow.

## Prerequisites

- Node.js 18+ and pnpm (or npm/yarn) for the frontend.
- Python 3.11+ with Poetry/uv/virtualenv for the backend.
- The Enterprise API running locally (see its README) with access to the preview `encypher-ai` package.

## Configuration

1. **Enterprise API**
   - Copy `enterprise_api/.env.example` to `.env`.
   - Set database credentials, encryption keys, and (optionally) configure a demo key:
     ```env
     DEMO_API_KEY=demo-key-local
     DEMO_PRIVATE_KEY_HEX=<optional 64 hex characters>
     ```
     When `DEMO_API_KEY` is set, the Enterprise API will authenticate requests without touching the database, using a transient signing key if no private key is provided.

2. **Dashboard backend**
   - Duplicate `dashboard_app/backend/.env.example` to `.env` and add:
     ```env
     ENTERPRISE_API_BASE_URL=http://localhost:9000/api/v1
     ENTERPRISE_API_KEY=demo-key-local          # or real key provisioned in Enterprise API
     ENTERPRISE_API_TIMEOUT=30
     ```
   - These settings allow the backend to call the same `/api/v1/sign` endpoint described in `API.md`.

3. **Dashboard frontend**
   - Copy `dashboard_app/frontend/.env.example` to `.env.local` as needed. Most flows are proxied through the backend so no additional keys are required on the client.

## Local Development

```bash
# Terminal 1 – Enterprise API
cd enterprise_api
uv run uvicorn app.main:app --reload --port 9000

# Terminal 2 – Dashboard backend
cd dashboard_app/backend
uv run uvicorn app.main:app --reload --port 8000

# Terminal 3 – Dashboard frontend
cd dashboard_app/frontend
pnpm install
pnpm dev --port 3000
```

Visit `http://localhost:3000` and sign in with a dashboard user. Superusers can trigger directory signing and CLI workflows.

> **Docker Compose:** `docker-compose up --build` remains available for an all-in-one local stack if you prefer containers.

## Directory Signing Workflow

Navigate to **Dashboard → Directory Signing** to sign every text file in a folder through the Enterprise API:

1. Provide a directory path accessible to the backend host.
2. (Optional) Scope the run with file extension allowlists, exclude patterns, recursion, or encoding.
3. Supply a JSON schema that maps file attributes to the API payload. The form feeds that schema into `POST /api/v1/sign` requests. Example:

```json
{
  "document_title": "{file_stem}",
  "document_url": "file://{absolute_path}",
  "document_type": "article"
}
```

### Available Template Placeholders

You can reference the following keys inside the schema (they are generated per file):

| Placeholder        | Description                                                |
| ------------------ | ---------------------------------------------------------- |
| `{file_name}`      | Full filename with extension                               |
| `{file_stem}`      | Filename without extension                                 |
| `{extension}`      | File extension (with leading dot)                          |
| `{absolute_path}`  | Absolute filesystem path                                   |
| `{relative_path}`  | Path relative to the selected directory                    |
| `{parent_dir}`     | Parent directory path                                      |
| `{file_size}`      | Size in bytes                                              |
| `{created_at}`     | File creation timestamp (ISO 8601, UTC)                    |
| `{modified_at}`    | Last modified timestamp (ISO 8601, UTC)                    |
| `{sha256}`         | SHA-256 hash of the file contents                          |
| `{generated_at}`   | Timestamp when the signing run executed (ISO 8601, UTC)    |
| `{base_directory}` | Absolute path of the root directory provided in the form   |

The backend renders these placeholders before dispatching to the Enterprise API, ensuring every request conforms to the schema documented in `enterprise_api/docs/API.md`. Output can be written as `.signed` sidecar files, overwrite the originals, or skipped entirely in dry-run mode.

## Feature Matrix

| Capability                 | Backing Enterprise API Endpoint |
| -------------------------- | ------------------------------- |
| Single document signing    | `POST /api/v1/sign`             |
| Directory signing (batch)  | `POST /api/v1/sign` (looped)    |
| Verification (profile tab) | `POST /api/v1/verify`           |
| Usage metrics (todo)       | `GET /api/v1/dashboard`         |

## Testing

- Backend: `cd dashboard_app/backend && pytest`
- Frontend: `cd dashboard_app/frontend && pnpm test`

End-to-end flows depend on the Enterprise API; use the demo key mode for smoke tests without provisioning certificates.
