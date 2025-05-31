# Dashboard Backend

This is the FastAPI backend for the EncypherAI Compliance Readiness Dashboard.

## Setup

1.  Ensure Python and UV are installed.
2.  Navigate to this directory (`dashboard_app/backend`).
3.  Create and activate a virtual environment:
    ```bash
    uv venv
    source .venv/bin/activate  # Linux/macOS
    # .\.venv\Scripts\activate # Windows PowerShell
    ```
4.  Install dependencies:
    ```bash
    uv pip sync
    ```

## Running the Development Server

```bash
uv run uvicorn app.main:app --reload
```
