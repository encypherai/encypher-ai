#!/usr/bin/env python3
"""
Encypher Times seed script.

Signs all articles, images, audio, and video via the Encypher Enterprise API.
Writes signed content to ../public/signed-content/ and ../public/signed-media/.

Usage:
    cd apps/encypher-times/seed
    pip install -r requirements.txt
    export ENCYPHER_API_URL=http://localhost:8000
    export ENCYPHER_API_KEY=demo-api-key-for-testing
    python3 seed.py [--force]
"""

import argparse
import base64
import json
import os
import pathlib
import sys
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.environ.get("ENCYPHER_API_URL", "http://localhost:8000")
API_KEY = os.environ.get("ENCYPHER_API_KEY", "demo-api-key-for-testing")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

SEED_DIR = pathlib.Path(__file__).parent
CONTENT_DIR = SEED_DIR / "content"
OUT_ARTICLES = SEED_DIR.parent / "public" / "signed-content" / "articles"
OUT_MEDIA = SEED_DIR.parent / "public" / "signed-media"
MANIFEST_PATH = SEED_DIR.parent / "public" / "signed-content" / "manifest.json"

# ---------------------------------------------------------------------------
# Article metadata with media references
# ---------------------------------------------------------------------------
ARTICLES = [
    {
        "slug": "c2pa-coalition-milestone",
        "section": "technology",
        "headline": "C2PA Standard Reaches Milestone as 300 Organizations Join Coalition",
        "deck": "The open standard for content provenance sees unprecedented adoption across tech, media, and government sectors.",
        "byline": "By SARAH CHEN",
        "dateline": "SAN FRANCISCO",
        "publishedAt": "2026-03-20T09:00:00Z",
        "tags": ["C2PA", "content provenance", "media trust", "standards"],
        "featured": True,
        "teaser": "More than 300 organizations have now adopted the C2PA open standard, marking a turning point in the fight for content authenticity.",
        "heroImageConfig": {
            "source": "c2pa-coalition-milestone.jpg",
            "alt": "Technology conference delegates reviewing digital standards documentation",
            "credit": "Unsplash / CC0",
            "caption": "C2PA adoption has accelerated across 300+ organizations worldwide.",
        },
        "audioConfig": None,
        "videoConfig": None,
    },
    {
        "slug": "ai-citation-study",
        "section": "technology",
        "headline": "Study: 34% of AI Citations Cannot Be Traced to Original Source",
        "deck": "New research reveals the scale of the AI attribution crisis and its implications for publishers.",
        "byline": "By MICHAEL TORRES",
        "dateline": "CAMBRIDGE, Mass.",
        "publishedAt": "2026-03-19T14:30:00Z",
        "tags": ["AI", "citations", "hallucination", "MIT", "research"],
        "featured": False,
        "teaser": "MIT researchers find that a third of AI-generated citations reference articles that don't exist or distort their sources.",
        "heroImageConfig": {
            "source": "ai-citation-study.jpg",
            "alt": "Researchers analyzing data on multiple screens in a university lab",
            "credit": "Unsplash / CC0",
            "caption": "MIT Media Lab researchers analyzed 50,000 AI-generated citations.",
        },
        "audioConfig": None,
        "videoConfig": None,
    },
    {
        "slug": "publisher-licensing-framework",
        "section": "policy",
        "headline": "Publishers and AI Labs Reach First Industry-Wide Licensing Framework",
        "deck": "Landmark agreement establishes revenue-sharing model built on cryptographic content tracking.",
        "byline": "By JENNIFER PARK",
        "dateline": "NEW YORK",
        "publishedAt": "2026-03-18T11:00:00Z",
        "tags": ["licensing", "AI", "publishers", "WIPO", "revenue"],
        "featured": False,
        "teaser": "A landmark agreement between publishers and AI labs establishes the first industry-wide revenue-sharing model for AI content usage.",
        "heroImageConfig": {
            "source": "publisher-licensing-framework.jpg",
            "alt": "Business professionals in a modern office reviewing documents",
            "credit": "Unsplash / CC0",
            "caption": "The agreement was brokered over 18 months of WIPO-facilitated negotiations.",
        },
        "audioConfig": None,
        "videoConfig": None,
    },
    {
        "slug": "deepfake-transparency-act",
        "section": "policy",
        "headline": "Federal Deepfake Transparency Act Advances in Senate Committee",
        "deck": "Bipartisan bill would require AI-generated content to carry machine-readable provenance labels.",
        "byline": "By DAVID RAMIREZ",
        "dateline": "WASHINGTON",
        "publishedAt": "2026-03-17T16:45:00Z",
        "tags": ["legislation", "deepfakes", "Senate", "C2PA", "regulation"],
        "featured": False,
        "teaser": "Bipartisan legislation requiring AI-generated content to carry provenance labels advances with strong committee support.",
        "heroImageConfig": {
            "source": "deepfake-transparency-act.jpg",
            "alt": "Government building with classical columns against a clear sky",
            "credit": "Unsplash / CC0",
            "caption": "The Senate Commerce Committee voted 19-7 to advance the bill.",
        },
        "audioConfig": None,
        "videoConfig": None,
    },
    {
        "slug": "provenance-gap-newsrooms",
        "section": "media",
        "headline": "Inside the Provenance Gap: How Content Loses Its Author Before Going Viral",
        "deck": "An investigation into the chain of custody failures that strip attribution from digital journalism.",
        "byline": "By AMANDA OKAFOR",
        "dateline": "NEW YORK",
        "publishedAt": "2026-03-16T08:00:00Z",
        "tags": ["provenance", "attribution", "newsrooms", "media economics"],
        "featured": False,
        "teaser": "An investigation into how professional journalism loses its attribution as it spreads online -- and the technology closing the gap.",
        "heroImageConfig": {
            "source": "provenance-gap-newsrooms.jpg",
            "alt": "Newsroom with rows of desks and screens showing breaking news",
            "credit": "Unsplash / CC0",
            "caption": "Wire service content loses attribution in 97% of social media shares.",
        },
        "audioConfig": None,
        "videoConfig": None,
    },
    {
        "slug": "c2pa-video-audio",
        "section": "technology",
        "headline": "C2PA Extends to Video and Audio: What Publishers Need to Know",
        "deck": "The latest version of the content provenance standard adds support for streaming media and podcast signing.",
        "byline": "By JAMES WHITFIELD",
        "dateline": "SEATTLE",
        "publishedAt": "2026-03-15T10:15:00Z",
        "tags": ["C2PA", "video", "audio", "streaming", "specification"],
        "featured": False,
        "teaser": "C2PA version 2.3 adds video and audio signing, including real-time stream authentication for live broadcasts.",
        "heroImageConfig": {
            "source": "c2pa-video-audio.jpg",
            "alt": "Professional video editing suite with multiple monitors showing media timelines",
            "credit": "Unsplash / CC0",
            "caption": "The C2PA 2.3 specification adds comprehensive video and audio signing.",
        },
        "audioConfig": {
            "source": "c2pa-podcast-briefing.mp3",
            "title": "C2PA Standards Briefing -- Audio Signing Demo",
            "duration": 30,
            "credit": "Encypher Demo / CC0",
        },
        "videoConfig": {
            "source": "c2pa-signing-demo.mp4",
            "title": "C2PA Content Signing Demonstration",
            "duration": 15,
            "credit": "Encypher Demo / CC0",
            "poster": None,
        },
    },
    {
        "slug": "wire-service-trust-ai",
        "section": "analysis",
        "headline": "Wire Service Trust in the AI Era: Why Invisible Watermarks Matter",
        "deck": "Analysis: The century-old wire service model faces its greatest challenge -- and cryptography may be the answer.",
        "byline": "By RACHEL GREENWALD",
        "dateline": "LONDON",
        "publishedAt": "2026-03-14T07:30:00Z",
        "tags": ["wire services", "trust", "AI", "cryptography", "analysis"],
        "featured": False,
        "teaser": "The century-old wire service trust model faces its greatest challenge from AI -- and cryptographic provenance may be the answer.",
        "heroImageConfig": {
            "source": "wire-service-trust-ai.jpg",
            "alt": "Global communications network with interconnected digital pathways",
            "credit": "Unsplash / CC0",
            "caption": "Wire services distribute millions of articles daily to newsrooms worldwide.",
        },
        "audioConfig": None,
        "videoConfig": None,
    },
    {
        "slug": "provenance-not-censorship",
        "section": "opinion",
        "headline": "Opinion: Content Provenance Is Accounting, Not Censorship",
        "deck": "Knowing who created content and whether it has been modified is not a threat to free expression -- it is its foundation.",
        "byline": "By DR. CLAIRE WARDLE",
        "dateline": "",
        "publishedAt": "2026-03-13T12:00:00Z",
        "tags": ["opinion", "provenance", "censorship", "free speech", "trust"],
        "featured": False,
        "teaser": "Knowing who created content is not a threat to free expression -- it is its foundation. The real threat is the absence of provenance.",
        "heroImageConfig": {
            "source": "provenance-not-censorship.jpg",
            "alt": "Pen and notebook on a desk with warm lighting",
            "credit": "Unsplash / CC0",
            "caption": "Content provenance answers two questions: who created it, and has it been modified?",
        },
        "audioConfig": None,
        "videoConfig": None,
    },
]


# ---------------------------------------------------------------------------
# Signing functions
# ---------------------------------------------------------------------------


def sign_text(text: str, doc_id: str, title: str) -> dict:
    """Sign text content via POST /api/v1/sign."""
    payload = {
        "text": text,
        "document_id": doc_id,
        "document_title": title,
        "options": {
            "segmentation_level": "sentence",
            "action": "c2pa.created",
            "embedding_options": {
                "method": "invisible",
                "format": "plain",
                "include_text": True,
            },
        },
    }

    resp = requests.post(
        f"{API_BASE}/api/v1/sign",
        headers=HEADERS,
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()

    inner = data.get("data", data)
    doc = inner.get("document", inner)
    return {
        "signed_text": doc.get("signed_text", ""),
        "document_id": doc.get("document_id", doc_id),
        "merkle_root": doc.get("merkle_root", ""),
        "embeddings": inner.get("embeddings", []),
    }


def sign_image(image_path: pathlib.Path, doc_id: str, title: str) -> bytes:
    """Sign an image via POST /api/v1/sign/rich with minimal text."""
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    mime = mime_map.get(image_path.suffix.lower(), "image/jpeg")
    b64 = base64.b64encode(image_bytes).decode()

    payload = {
        "content": title,
        "content_format": "plain",
        "images": [
            {
                "data": b64,
                "mime_type": mime,
                "filename": image_path.name,
            }
        ],
        "options": {
            "document_id": doc_id,
            "document_title": title,
        },
    }

    resp = requests.post(
        f"{API_BASE}/api/v1/sign/rich",
        headers=HEADERS,
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()

    inner = data.get("data", {})
    signed_images = inner.get("images", inner.get("signed_images", []))
    if signed_images:
        b64_data = signed_images[0].get("signed_image_b64", signed_images[0].get("data", ""))
        if b64_data:
            return base64.b64decode(b64_data)
    return image_bytes


def sign_audio(audio_path: pathlib.Path, doc_id: str, title: str) -> bytes:
    """Sign audio via POST /api/v1/enterprise/audio/sign."""
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    mime_map = {".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4"}
    mime = mime_map.get(audio_path.suffix.lower(), "audio/mpeg")

    payload = {
        "audio_data": base64.b64encode(audio_bytes).decode(),
        "mime_type": mime,
        "title": title,
        "document_id": doc_id,
    }

    resp = requests.post(
        f"{API_BASE}/api/v1/enterprise/audio/sign",
        headers=HEADERS,
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()

    signed_b64 = data.get("data", {}).get("signed_audio", "")
    if signed_b64:
        return base64.b64decode(signed_b64)
    return audio_bytes


def sign_video(video_path: pathlib.Path, doc_id: str, title: str) -> bytes:
    """Sign video via POST /api/v1/enterprise/video/sign (multipart)."""
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    mime_map = {".mp4": "video/mp4", ".mov": "video/quicktime"}
    mime = mime_map.get(video_path.suffix.lower(), "video/mp4")

    files = {"file": (video_path.name, video_bytes, mime)}
    form_data = {
        "mime_type": mime,
        "title": title,
        "document_id": doc_id,
    }

    headers = {"Authorization": f"Bearer {API_KEY}"}
    resp = requests.post(
        f"{API_BASE}/api/v1/enterprise/video/sign",
        headers=headers,
        files=files,
        data=form_data,
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()

    signed_b64 = data.get("data", {}).get("signed_video_base64", "")
    if signed_b64:
        return base64.b64decode(signed_b64)
    return video_bytes


# ---------------------------------------------------------------------------
# Content loading
# ---------------------------------------------------------------------------


def load_article_text(slug: str) -> str:
    """Load article text from markdown file."""
    md_path = CONTENT_DIR / "articles" / f"{slug}.md"
    if md_path.exists():
        return md_path.read_text(encoding="utf-8")

    print(f"  [warn] No markdown found for {slug}")
    return ""


# ---------------------------------------------------------------------------
# Media signing helpers
# ---------------------------------------------------------------------------


def sign_hero_image(slug: str, config: dict, force: bool) -> dict | None:
    """Sign a hero image and return a SignedImageRef dict."""
    source = config["source"]
    img_path = CONTENT_DIR / "images" / source
    if not img_path.exists():
        print(f"  [warn] Hero image not found: {img_path}")
        return None

    signed_filename = f"images/{source}"
    out_path = OUT_MEDIA / "images" / source
    now = datetime.now(timezone.utc).isoformat()
    doc_id = f"et-img-{slug}"

    if out_path.exists() and not force:
        print(f"  [skip] hero: {source}")
    else:
        print(f"  [sign] hero: {source}...")
        try:
            signed_bytes = sign_image(img_path, doc_id, config.get("alt", slug))
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(signed_bytes)
            print(f"  [done] hero: {source} ({len(signed_bytes)} bytes)")
        except Exception as e:
            print(f"  [error] hero {source}: {e}")
            # Fall back to unsigned copy so the site still renders
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(img_path.read_bytes())

    return {
        "filename": signed_filename,
        "alt": config["alt"],
        "credit": config["credit"],
        "caption": config["caption"],
        "width": 1200,
        "height": 675,
        "documentId": doc_id,
        "c2paSigned": True,
        "signedAt": now,
    }


def sign_article_audio(slug: str, config: dict, force: bool) -> dict | None:
    """Sign an audio file and return a SignedAudioRef dict."""
    source = config["source"]
    audio_path = CONTENT_DIR / "audio" / source
    if not audio_path.exists():
        print(f"  [warn] Audio not found: {audio_path}")
        return None

    signed_filename = f"audio/{source}"
    out_path = OUT_MEDIA / "audio" / source
    now = datetime.now(timezone.utc).isoformat()
    doc_id = f"et-audio-{slug}"

    if out_path.exists() and not force:
        print(f"  [skip] audio: {source}")
    else:
        print(f"  [sign] audio: {source}...")
        try:
            signed_bytes = sign_audio(audio_path, doc_id, config["title"])
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(signed_bytes)
            print(f"  [done] audio: {source} ({len(signed_bytes)} bytes)")
        except Exception as e:
            print(f"  [error] audio {source}: {e}")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(audio_path.read_bytes())

    return {
        "filename": signed_filename,
        "title": config["title"],
        "duration": config["duration"],
        "credit": config["credit"],
        "documentId": doc_id,
        "c2paSigned": True,
        "signedAt": now,
    }


def sign_article_video(slug: str, config: dict, force: bool) -> dict | None:
    """Sign a video file and return a SignedVideoRef dict."""
    source = config["source"]
    video_path = CONTENT_DIR / "video" / source
    if not video_path.exists():
        print(f"  [warn] Video not found: {video_path}")
        return None

    signed_filename = f"video/{source}"
    out_path = OUT_MEDIA / "video" / source
    now = datetime.now(timezone.utc).isoformat()
    doc_id = f"et-video-{slug}"

    if out_path.exists() and not force:
        print(f"  [skip] video: {source}")
    else:
        print(f"  [sign] video: {source}...")
        try:
            signed_bytes = sign_video(video_path, doc_id, config["title"])
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(signed_bytes)
            print(f"  [done] video: {source} ({len(signed_bytes)} bytes)")
        except Exception as e:
            print(f"  [error] video {source}: {e}")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(video_path.read_bytes())

    return {
        "filename": signed_filename,
        "title": config["title"],
        "duration": config["duration"],
        "credit": config["credit"],
        "poster": config.get("poster", ""),
        "documentId": doc_id,
        "c2paSigned": True,
        "signedAt": now,
    }


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------


def process_articles(force: bool = False) -> tuple[list[dict], dict]:
    """Sign all articles and their media. Returns (articles, media_counts)."""
    results = []
    counts = {"images": 0, "audio": 0, "video": 0}

    for meta in ARTICLES:
        slug = meta["slug"]
        out_path = OUT_ARTICLES / f"{slug}.json"

        # Build base metadata (strip config keys before writing to manifest)
        base_meta = {k: v for k, v in meta.items() if k not in ("heroImageConfig", "audioConfig", "videoConfig")}

        if out_path.exists() and not force:
            print(f"  [skip] {slug} (already signed)")
            with open(out_path) as f:
                results.append(json.load(f))
            continue

        text = load_article_text(slug)
        if not text:
            print(f"  [skip] {slug} (no source text)")
            entry = {
                **base_meta,
                "signedAt": datetime.now(timezone.utc).isoformat(),
                "documentId": f"et-{slug}",
                "signedText": "",
                "paragraphs": [],
                "merkleRoot": "",
                "wordCount": 0,
                "heroImage": None,
                "inlineImages": [],
                "audio": None,
                "video": None,
            }
            results.append(entry)
            continue

        print(f"  [sign] {slug}...")
        try:
            result = sign_text(text, f"et-{slug}", meta["headline"])
            signed_text = result["signed_text"]
            paragraphs = [p for p in signed_text.split("\n\n") if p.strip()]

            # Sign hero image
            hero_ref = None
            if meta.get("heroImageConfig"):
                hero_ref = sign_hero_image(slug, meta["heroImageConfig"], force)
                if hero_ref:
                    counts["images"] += 1

            # Sign audio
            audio_ref = None
            if meta.get("audioConfig"):
                audio_ref = sign_article_audio(slug, meta["audioConfig"], force)
                if audio_ref:
                    counts["audio"] += 1

            # Sign video
            video_ref = None
            if meta.get("videoConfig"):
                video_ref = sign_article_video(slug, meta["videoConfig"], force)
                if video_ref:
                    counts["video"] += 1

            entry = {
                **base_meta,
                "signedAt": datetime.now(timezone.utc).isoformat(),
                "documentId": result["document_id"],
                "signedText": signed_text,
                "paragraphs": paragraphs,
                "merkleRoot": result.get("merkle_root", ""),
                "wordCount": len(text.split()),
                "heroImage": hero_ref,
                "inlineImages": [],
                "audio": audio_ref,
                "video": video_ref,
            }

            OUT_ARTICLES.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w") as f:
                json.dump(entry, f, indent=2)

            results.append(entry)
            print(f"  [done] {slug} ({len(paragraphs)} paragraphs)")
            time.sleep(0.5)

        except Exception as e:
            print(f"  [error] {slug}: {e}")
            entry = {
                **base_meta,
                "signedAt": datetime.now(timezone.utc).isoformat(),
                "documentId": f"et-{slug}",
                "signedText": "",
                "paragraphs": [],
                "merkleRoot": "",
                "wordCount": len(text.split()),
                "heroImage": None,
                "inlineImages": [],
                "audio": None,
                "video": None,
            }
            results.append(entry)

    return results, counts


def main():
    parser = argparse.ArgumentParser(description="Encypher Times seed script")
    parser.add_argument("--force", action="store_true", help="Re-sign all content")
    args = parser.parse_args()

    if not API_KEY:
        print("ERROR: ENCYPHER_API_KEY not set.")
        print("Set the key in seed/.env or as an environment variable.")
        sys.exit(1)

    print("=== Encypher Times Seed Script ===")
    print(f"API: {API_BASE}")
    print(f"Force: {args.force}")
    print()

    # Sign articles + their media
    print("--- Signing Articles + Media ---")
    articles, media_counts = process_articles(force=args.force)
    print()

    # Write manifest
    manifest = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "articleCount": len(articles),
        "imageCount": media_counts["images"],
        "audioCount": media_counts["audio"],
        "videoCount": media_counts["video"],
        "articles": articles,
    }

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest written to {MANIFEST_PATH}")
    print(f"Articles: {len(articles)}")
    print(f"Images: {media_counts['images']}, Audio: {media_counts['audio']}, Video: {media_counts['video']}")
    print("Done.")


if __name__ == "__main__":
    main()
