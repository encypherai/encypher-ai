"""
Ghost CMS integration service.

Handles the full signing flow for Ghost posts:
1. Receive webhook → identify org
2. Read post from Ghost Admin API
3. Extract plain text from HTML
4. Call internal signing service
5. Embed signed text back into HTML
6. Update post in Ghost via Admin API

Also provides a Ghost Admin API client and HTML text extraction/embedding utilities.
"""

import hashlib
import logging
import re
import time
import uuid
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple

import httpx
import jwt

logger = logging.getLogger(__name__)

# =============================================================================
# In-flight lock for loop prevention
# =============================================================================

_in_flight: Dict[str, float] = {}
_IN_FLIGHT_TTL_SECONDS = 30


def is_in_flight(post_id: str) -> bool:
    """Check if a post is currently being signed (loop prevention)."""
    ts = _in_flight.get(post_id)
    if ts is None:
        return False
    if time.time() - ts > _IN_FLIGHT_TTL_SECONDS:
        _in_flight.pop(post_id, None)
        return False
    return True


def set_in_flight(post_id: str) -> None:
    _in_flight[post_id] = time.time()


def clear_in_flight(post_id: str) -> None:
    _in_flight.pop(post_id, None)


# =============================================================================
# Ghost Admin API Client
# =============================================================================


class GhostAdminClient:
    """Async client for the Ghost Admin API using JWT authentication."""

    def __init__(self, ghost_url: str, admin_api_key: str, api_version: str = "v5.0"):
        self.ghost_url = ghost_url.rstrip("/")
        self.admin_api_key = admin_api_key
        self.api_version = api_version

        parts = admin_api_key.split(":")
        if len(parts) != 2:
            raise ValueError("Ghost Admin API key must be in format {id}:{secret}")
        self.key_id = parts[0]
        self.key_secret = bytes.fromhex(parts[1])

    def _make_token(self) -> str:
        """Generate a short-lived JWT for Ghost Admin API authentication."""
        iat = int(time.time())
        payload = {
            "iat": iat,
            "exp": iat + 300,  # 5 minutes
            "aud": "/admin/",
        }
        return jwt.encode(payload, self.key_secret, algorithm="HS256", headers={"kid": self.key_id})

    def _api_url(self, path: str) -> str:
        return f"{self.ghost_url}/ghost/api/admin/{path}"

    async def read_post(self, post_id: str) -> Dict[str, Any]:
        """Read a single post by ID, including HTML and tags."""
        url = self._api_url(f"posts/{post_id}/")
        token = self._make_token()
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                url,
                params={"formats": "html", "include": "tags,authors"},
                headers={"Authorization": f"Ghost {token}"},
            )
            resp.raise_for_status()
            data = resp.json()
            return data["posts"][0]

    async def read_page(self, page_id: str) -> Dict[str, Any]:
        """Read a single page by ID, including HTML and tags."""
        url = self._api_url(f"pages/{page_id}/")
        token = self._make_token()
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                url,
                params={"formats": "html", "include": "tags,authors"},
                headers={"Authorization": f"Ghost {token}"},
            )
            resp.raise_for_status()
            data = resp.json()
            return data["pages"][0]

    async def update_post(
        self,
        post_id: str,
        html: str,
        updated_at: str,
        *,
        codeinjection_foot: Optional[str] = None,
        tags: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Update a post's HTML content via the Admin API."""
        url = self._api_url(f"posts/{post_id}/")
        token = self._make_token()

        payload: Dict[str, Any] = {
            "id": post_id,
            "html": html,
            "updated_at": updated_at,
        }
        if codeinjection_foot is not None:
            payload["codeinjection_foot"] = codeinjection_foot
        if tags is not None:
            payload["tags"] = tags

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.put(
                url,
                json={"posts": [payload]},
                params={"source": "html"},
                headers={
                    "Authorization": f"Ghost {token}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["posts"][0]

    async def update_page(
        self,
        page_id: str,
        html: str,
        updated_at: str,
        *,
        codeinjection_foot: Optional[str] = None,
        tags: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Update a page's HTML content via the Admin API."""
        url = self._api_url(f"pages/{page_id}/")
        token = self._make_token()

        payload: Dict[str, Any] = {
            "id": page_id,
            "html": html,
            "updated_at": updated_at,
        }
        if codeinjection_foot is not None:
            payload["codeinjection_foot"] = codeinjection_foot
        if tags is not None:
            payload["tags"] = tags

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.put(
                url,
                json={"pages": [payload]},
                params={"source": "html"},
                headers={
                    "Authorization": f"Ghost {token}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["pages"][0]


# =============================================================================
# HTML Text Extraction / Embedding
# =============================================================================

# Unicode Variation Selector ranges used by C2PA embeddings
_VS_PATTERN = re.compile(r"[\uFE00-\uFE0F\uFEFF\U000E0100-\U000E01EF]")

# Ghost Koenig card classes to skip (non-textual)
_SKIP_CARD_CLASSES = frozenset(
    {
        "kg-image-card",
        "kg-gallery-card",
        "kg-video-card",
        "kg-audio-card",
        "kg-embed-card",
        "kg-code-card",
        "kg-html-card",
    }
)


_VOID_ELEMENTS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)

_TAG_SPLIT_RE = re.compile(r"(<[^>]+>)")
_TAG_NAME_RE = re.compile(r"^</?\s*([a-zA-Z0-9:_-]+)")
_CLASS_ATTR_RE = re.compile(r"\bclass\s*=\s*(['\"])(.*?)\1", re.IGNORECASE | re.DOTALL)


class _TextExtractor(HTMLParser):
    """HTML parser that extracts visible text, skipping non-textual Ghost cards."""

    def __init__(self) -> None:
        super().__init__()
        self.texts: List[str] = []
        self._skip_depth = 0
        self._in_skip = False

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        attr_dict = dict(attrs)
        classes = set((attr_dict.get("class") or "").split())

        if classes & _SKIP_CARD_CLASSES:
            self._in_skip = True
            self._skip_depth = 1
            return

        if self._in_skip:
            if tag not in _VOID_ELEMENTS:
                self._skip_depth += 1
            return

        # Skip <script>, <style>, <code>, <pre>
        if tag in ("script", "style", "code", "pre"):
            self._in_skip = True
            self._skip_depth = 1

    def handle_endtag(self, tag: str) -> None:
        if self._in_skip:
            self._skip_depth -= 1
            if self._skip_depth <= 0:
                self._in_skip = False
                self._skip_depth = 0

    def handle_data(self, data: str) -> None:
        if not self._in_skip:
            stripped = data.strip()
            if stripped:
                self.texts.append(stripped)


def extract_text_from_html(html: str) -> str:
    """Extract visible text from Ghost post HTML, skipping non-textual cards."""
    parser = _TextExtractor()
    parser.feed(html)
    return "\n".join(parser.texts)


def strip_c2pa_embeddings(text: str) -> str:
    """Remove all C2PA invisible Unicode markers from text."""
    return _VS_PATTERN.sub("", text)


def detect_c2pa_embeddings(text: str) -> int:
    """Count the number of C2PA invisible Unicode markers in text."""
    return len(_VS_PATTERN.findall(text))


def embed_signed_text_in_html(original_html: str, signed_text: str) -> str:
    """
    Replace the extracted text portions in the original HTML with signed text.

    Strategy: find the first <p> or block-level element's text content and
    replace the entire text content with the signed version. This is a
    simplified approach — the signed text from the API already contains the
    full text with VS chars embedded, so we replace the body content.
    """
    # The signed text from the Enterprise API contains the full text with
    # invisible markers. We need to replace the text nodes in the HTML.
    # Simple approach: replace the text content of the first <p> tag's
    # content with the full signed text wrapped in a single <p>.
    #
    # More robust approach: map each paragraph to its signed counterpart.
    # For now, we use the simple approach since the Enterprise API returns
    # the full signed text as a single string.

    clean_html = strip_c2pa_embeddings(original_html)
    original_text = extract_text_from_html(clean_html)
    if not original_text.strip():
        return original_html

    signed_parts = [p.strip() for p in signed_text.split("\n") if p.strip()]
    if not signed_parts:
        return clean_html

    parts = _TAG_SPLIT_RE.split(clean_html)
    output_parts: List[str] = []
    signed_index = 0
    in_skip = False
    skip_depth = 0

    for part in parts:
        if not part:
            continue

        if part.startswith("<") and part.endswith(">"):
            output_parts.append(part)

            tag_match = _TAG_NAME_RE.match(part)
            if not tag_match:
                continue

            tag_name = tag_match.group(1).lower()
            is_end = part.startswith("</")
            is_self_closing = part.rstrip().endswith("/>") or tag_name in _VOID_ELEMENTS

            if is_end:
                if in_skip:
                    skip_depth -= 1
                    if skip_depth <= 0:
                        in_skip = False
                        skip_depth = 0
                continue

            if in_skip:
                if not is_self_closing:
                    skip_depth += 1
                continue

            class_match = _CLASS_ATTR_RE.search(part)
            classes = set((class_match.group(2) if class_match else "").split())
            should_skip = bool(classes & _SKIP_CARD_CLASSES) or tag_name in ("script", "style", "code", "pre")
            if should_skip:
                in_skip = True
                skip_depth = 1
            continue

        if in_skip:
            output_parts.append(part)
            continue

        stripped = part.strip()
        if stripped and signed_index < len(signed_parts):
            output_parts.append(part.replace(stripped, signed_parts[signed_index], 1))
            signed_index += 1
        else:
            output_parts.append(part)

    return "".join(output_parts)


# =============================================================================
# Badge Injection
# =============================================================================


def generate_badge_script(document_id: str, instance_id: str, verify_base_url: str = "https://verify.encypherai.com") -> str:
    """Generate the verification badge JavaScript snippet for Ghost code injection."""
    return f"""<!-- Encypher Provenance Badge -->
<script>
(function() {{
  var badge = document.createElement('div');
  badge.innerHTML = '<a href="{verify_base_url}/{document_id}" target="_blank" rel="noopener" '
    + 'style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;'
    + 'border-radius:6px;background:#f0f9ff;border:1px solid #bae6fd;'
    + 'color:#0369a1;font-size:13px;font-family:system-ui,sans-serif;'
    + 'text-decoration:none;margin-top:24px">'
    + '\\u2713 Encypher Verified</a>';
  var article = document.querySelector('.gh-content, .post-content, article');
  if (article) article.appendChild(badge);
}})();
</script>"""


def merge_badge_injection(existing_foot: Optional[str], badge_script: str) -> str:
    """Merge badge script into existing codeinjection_foot, replacing any previous badge."""
    marker_start = "<!-- Encypher Provenance Badge -->"
    if existing_foot:
        # Remove previous badge
        idx = existing_foot.find(marker_start)
        if idx >= 0:
            # Find the closing </script> after the marker
            end_idx = existing_foot.find("</script>", idx)
            if end_idx >= 0:
                existing_foot = existing_foot[:idx] + existing_foot[end_idx + len("</script>") :]
            existing_foot = existing_foot.strip()

        if existing_foot:
            return f"{existing_foot}\n{badge_script}"

    return badge_script


def _normalize_manifest_mode_for_sign_options(manifest_mode: str) -> tuple[str, Optional[bool], Optional[bool]]:
    """Normalize persisted Ghost manifest mode values for SignOptions.

    Supports legacy aliases from older Ghost integration configs while
    preserving intended micro mode behavior.
    """
    from app.schemas.signing_constants import MANIFEST_MODES

    mode = (manifest_mode or "micro").strip().lower().replace("-", "_")
    legacy_aliases: dict[str, tuple[str, Optional[bool], Optional[bool]]] = {
        "micro_ecc_c2pa": ("micro", True, True),
        "micro_ecc": ("micro", True, False),
    }

    if mode in legacy_aliases:
        normalized_mode, ecc_override, embed_c2pa_override = legacy_aliases[mode]
        logger.info(
            "Normalized legacy Ghost manifest mode '%s' to mode='%s' (ecc=%s, embed_c2pa=%s)",
            manifest_mode,
            normalized_mode,
            ecc_override,
            embed_c2pa_override,
        )
        return normalized_mode, ecc_override, embed_c2pa_override

    if mode in MANIFEST_MODES:
        return mode, None, None

    logger.warning(
        "Unsupported Ghost manifest mode '%s'; defaulting to 'micro'",
        manifest_mode,
    )
    return "micro", None, None


# =============================================================================
# Signing Orchestration
# =============================================================================


async def sign_ghost_post(
    *,
    ghost_client: GhostAdminClient,
    post_id: str,
    post_type: str,
    organization: Dict[str, Any],
    core_db: Any,
    content_db: Any,
    manifest_mode: str = "micro",
    segmentation_level: str = "sentence",
    ecc: bool = True,
    embed_c2pa: bool = True,
    badge_enabled: bool = True,
) -> Dict[str, Any]:
    """
    Full signing orchestration for a Ghost post.

    Returns a dict with success status and signing metadata.
    """
    from app.schemas.sign_schemas import SignOptions, UnifiedSignRequest
    from app.services.unified_signing_service import execute_unified_signing

    # 1. Read post from Ghost
    try:
        if post_type == "page":
            post = await ghost_client.read_page(post_id)
        else:
            post = await ghost_client.read_post(post_id)
    except Exception as e:
        logger.error("Failed to read %s %s from Ghost: %s", post_type, post_id, e)
        return {"success": False, "error": f"Failed to read {post_type}: {e}"}

    html = post.get("html") or ""
    if not html.strip():
        logger.warning("Post %s has no HTML content", post_id)
        return {"success": False, "error": "Post has no HTML content"}

    # 2. Strip existing C2PA embeddings
    clean_html = strip_c2pa_embeddings(html)

    # 3. Extract plain text
    extracted_text = extract_text_from_html(clean_html)
    if not extracted_text.strip():
        logger.warning("No text content found in post %s", post_id)
        return {"success": False, "error": "No text content found"}

    content_hash = hashlib.md5(extracted_text.encode()).hexdigest()

    # 4. Determine action type
    existing_vs = detect_c2pa_embeddings(html)
    action_type = "c2pa.edited" if existing_vs > 0 else "c2pa.created"

    # 5. Build document ID
    unique_doc_id = f"ghost_{post_type}_{post_id}_v{int(time.time())}_{uuid.uuid4().hex[:8]}"

    logger.info(
        "Signing Ghost %s %s (action=%s, text_len=%d, html_len=%d)",
        post_type,
        post_id,
        action_type,
        len(extracted_text),
        len(clean_html),
    )

    # 6. Build signing request and call internal signing service
    author_name = "Unknown"
    authors = post.get("authors") or []
    if authors:
        author_name = authors[0].get("name", "Unknown")

    tags = post.get("tags") or []
    tag_names = [t.get("name", "") for t in tags]

    correlation_id = f"ghost-{uuid.uuid4().hex[:12]}"

    normalized_manifest_mode, ecc_override, embed_c2pa_override = _normalize_manifest_mode_for_sign_options(manifest_mode)

    sign_options: dict[str, Any] = {
        "document_type": "article",
        "claim_generator": "Ghost/Encypher Integration v1.0.0",
        "action": action_type,
        "manifest_mode": normalized_manifest_mode,
        "segmentation_level": segmentation_level,
        "ecc": ecc,
        "embed_c2pa": embed_c2pa,
        "index_for_attribution": True,
    }
    if ecc_override is not None:
        sign_options["ecc"] = ecc_override
    if embed_c2pa_override is not None:
        sign_options["embed_c2pa"] = embed_c2pa_override

    sign_request = UnifiedSignRequest(
        text=extracted_text,
        document_id=unique_doc_id,
        document_title=post.get("title", ""),
        document_url=post.get("url", ""),
        metadata={
            "author": author_name,
            "ghost_post_id": post_id,
            "ghost_post_type": post_type,
            "tags": tag_names,
            "source": "ghost_integration",
        },
        options=SignOptions(**sign_options),
    )

    try:
        sign_result = await execute_unified_signing(
            request=sign_request,
            organization=organization,
            core_db=core_db,
            content_db=content_db,
            correlation_id=correlation_id,
        )
    except Exception as e:
        logger.error("Signing failed for post %s: %s", post_id, e)
        return {"success": False, "error": f"Signing failed: {e}"}

    if not sign_result.get("success"):
        error_msg = sign_result.get("error", {})
        if isinstance(error_msg, dict):
            error_msg = error_msg.get("message", "Unknown signing error")
        return {"success": False, "error": f"Signing error: {error_msg}"}

    # 7. Extract signed text from response
    data = sign_result.get("data", {})
    doc_data = data.get("document", {})
    signed_text = doc_data.get("signed_text") or doc_data.get("embedded_text") or doc_data.get("embedded_content") or ""
    document_id = doc_data.get("document_id", unique_doc_id)
    instance_id = doc_data.get("instance_id", "")
    total_segments = doc_data.get("total_segments", 0)

    if not signed_text:
        logger.error("No signed text in response for post %s", post_id)
        return {"success": False, "error": "No signed text in signing response"}

    # 8. Embed signed text back into HTML
    embedded_html = embed_signed_text_in_html(clean_html, signed_text)

    logger.info(
        "Embedded signed text into Ghost %s %s (html_len=%d → %d)",
        post_type,
        post_id,
        len(clean_html),
        len(embedded_html),
    )

    # 9. Prepare update options
    codeinjection_foot = None
    if badge_enabled:
        badge_script = generate_badge_script(document_id, instance_id)
        codeinjection_foot = merge_badge_injection(post.get("codeinjection_foot"), badge_script)

    # Add #encypher-signed tag if not present
    existing_tags = [{"id": t.get("id"), "name": t.get("name"), "slug": t.get("slug")} for t in tags]
    has_encypher_tag = any(t.get("slug") == "hash-encypher-signed" for t in tags)
    update_tags = None
    if not has_encypher_tag:
        update_tags = existing_tags + [{"name": "#encypher-signed"}]

    # 10. Re-read post for latest updated_at, then update
    try:
        if post_type == "page":
            fresh = await ghost_client.read_page(post_id)
            await ghost_client.update_page(
                post_id,
                embedded_html,
                fresh["updated_at"],
                codeinjection_foot=codeinjection_foot,
                tags=update_tags,
            )
        else:
            fresh = await ghost_client.read_post(post_id)
            await ghost_client.update_post(
                post_id,
                embedded_html,
                fresh["updated_at"],
                codeinjection_foot=codeinjection_foot,
                tags=update_tags,
            )
    except Exception as e:
        logger.error("Failed to update Ghost %s %s: %s", post_type, post_id, e)
        return {
            "success": False,
            "error": f"Ghost update failed: {e}",
            "document_id": document_id,
            "instance_id": instance_id,
        }

    logger.info(
        "Ghost %s %s signed successfully (doc=%s, segments=%d)",
        post_type,
        post_id,
        document_id,
        total_segments,
    )

    return {
        "success": True,
        "document_id": document_id,
        "instance_id": instance_id,
        "total_segments": total_segments,
        "action_type": action_type,
        "content_hash": content_hash,
    }
