# Encypher — CMS HTML Signing Kit

Sign your CMS HTML pages with invisible, verifiable content credentials powered by the [Encypher](https://encypherai.com) API. The signed HTML is visually identical to the original — invisible Unicode markers are embedded in the article text, enabling anyone to verify authorship and integrity.

## Quick Start

### Using uv (recommended)

[uv](https://docs.astral.sh/uv/) is a fast Python package manager. Install it if you haven't already:

```bash
# Install uv (macOS / Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then set up and run:

```bash
# 1. Install dependencies
uv sync

# 2. Configure your API key
cp .env.example .env
# Edit .env and set ENCYPHER_API_KEY to your key

# 3. Sign an HTML page
uv run python encypher_sign_html.py page.html page_signed.html
```

### Using pip

```bash
# 1. Create a virtual environment and install
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install .

# 2. Configure your API key
cp .env.example .env
# Edit .env and set ENCYPHER_API_KEY to your key

# 3. Sign an HTML page
python encypher_sign_html.py page.html page_signed.html
```

## How It Works

1. **Extracts** the article text from your HTML (configurable CSS selector)
2. **Signs** the text via the Encypher API with invisible Unicode markers
3. **Embeds** the signed text back into the original HTML text nodes
4. **Verifies** the signature round-trip automatically
5. **Outputs** the complete HTML page — tags, images, scripts, styles all untouched

The signed HTML can be served directly by your CMS. Readers can verify the content by copying the article text and pasting it into [encypherai.com/tools/verify](https://encypherai.com/tools/verify).

## Usage

```bash
# Sign with micro_ecc_c2pa (default — C2PA manifest + Reed-Solomon error correction)
uv run python encypher_sign_html.py input.html output.html

# Sign with micro_c2pa (compact C2PA manifest, no error correction)
uv run python encypher_sign_html.py input.html output.html --mode micro_c2pa

# Sign with basic mode (per-sentence signatures only, no C2PA manifest)
uv run python encypher_sign_html.py input.html output.html --mode basic

# Custom content selector (default: article)
uv run python encypher_sign_html.py input.html output.html --selector "main .content"
uv run python encypher_sign_html.py input.html output.html --selector "#post-body"

# Specify document title (auto-detected from <h1> if omitted)
uv run python encypher_sign_html.py input.html output.html --title "My Article"

# Use a specific env file
uv run python encypher_sign_html.py input.html output.html --env-file /path/to/.env

# Pass API key directly (not recommended for production)
uv run python encypher_sign_html.py input.html output.html --api-key ency_...
```

## Configuration

Set these in your `.env` file (see `.env.example`):

| Variable | Required | Default | Description |
|---|---|---|---|
| `ENCYPHER_API_KEY` | **Yes** | — | Your Encypher API key |
| `ENCYPHER_BASE_URL` | No | `https://api.encypherai.com` | API base URL |

Priority order: CLI flags → `.env` file → environment variables.

## Signing Modes

| Mode | Markers | C2PA Manifest | Error Correction | Best For |
|---|---|---|---|---|
| `micro_ecc_c2pa` | Per-sentence + document | Yes | Reed-Solomon | **Default** — recommended |
| `micro_c2pa` | Per-sentence + document | Yes | No | Standard use |
| `basic` | Per-sentence only | No | No | Lightweight |

## Content Selector

By default, the script signs text inside the `<article>` element. Use `--selector` to target a different container:

- `article` — default, works with most CMS themes
- `main` — main content area
- `.post-content` — class-based selector
- `#entry-body` — ID-based selector
- `main .content` — nested selector

Everything outside the selected element (nav, footer, scripts, styles, sidebar) is left untouched.

## Integration Example

```python
from encypher_sign_html import sign_html

# In your CMS publishing pipeline:
original_html = get_page_from_cms()

signed_html = sign_html(
    html=original_html,
    api_key="your-api-key",
    manifest_mode="micro_ecc_c2pa",
    content_selector="article",
)

publish_to_cdn(signed_html)
```

## Verification

Readers can verify signed content in two ways:

1. **Web tool**: Copy article text → paste into [encypherai.com/tools/verify](https://encypherai.com/tools/verify)
2. **API**: `POST /api/v1/verify` with the text content

## Requirements

- Python 3.9+
- `requests` — HTTP client
- `beautifulsoup4` — HTML parsing
- `python-dotenv` — Environment file loading (for `.env` file support)

## License

This software is proprietary to Encypher AI, Inc. and is licensed for use under the terms of your API license agreement. See [LICENSE](LICENSE) for details.

## Support

Contact [support@encypherai.com](mailto:support@encypherai.com) for API key provisioning and technical support.
