---
title: "31 Media Types, One Standard: Inside Encypher's v2.0.0 API"
date: "2026-04-14"
excerpt: "Encypher v2.0.0 extends C2PA content provenance to 31 media types across images, audio, video, documents, and fonts - all through a single /sign/media endpoint with free verification."
author: "Erik Svilich"
tags: ["ContentProvenance", "C2PA", "MediaTypes"]
---

**By: Erik Svilich, Founder & CEO | Encypher | C2PA Text Provenance Co-Chair**

Encypher's v2.0.0 API adds C2PA content provenance to 31 media types. This post explains what that means in practice: what the five media categories cover, how the unified endpoint works, how embedding differs by format, and why free verification for all formats was a design requirement from the start.

---

## Why Media Type Coverage Matters

The original version of Encypher's signing infrastructure focused on text. Text is where we started, because text is the dominant medium for AI training data and the format where provenance infrastructure was most absent. C2PA 2.3 Section A.7 defined the text provenance standard; our implementation extended it with sentence-level granularity.

But content provenance only works as infrastructure if it covers the formats that content actually exists in. A news photograph, a podcast episode, a corporate training video, a PDF contract, and a web font are all content that carries rights, originates from a creator, and travels through distribution channels. Without provenance, any of these formats can be scraped, redistributed, or modified without leaving a rights signal behind.

Version 2.0.0 closes that gap. Every major media format used in professional content production now has a supported signing path.

---

## The Five Media Categories

[The full media types reference](/c2pa-standard/media-types) covers all 31 formats with embedding details for each. Here is the category breakdown.

### Images (13 formats)

The image category covers: JPEG, PNG, WebP, AVIF, HEIC, TIFF, GIF, BMP, SVG, DNG, CR2, NEF, ARW.

JPEG, PNG, WebP, TIFF, AVIF, and HEIC support native C2PA embedding via the c2pa-python library, which handles the JUMBF container insertion directly into the file structure. DNG, CR2, NEF, and ARW, the major RAW camera formats, use custom JUMBF and COSE implementation where the library does not yet provide native support. GIF, BMP, and SVG use a companion manifest approach, where the manifest is embedded in a sidecar format or a custom metadata block within the file.

The content hash in each image manifest covers the pixel data, not the container metadata. This means a re-encode at lower JPEG quality invalidates the manifest (the pixel data changed), while a metadata strip of EXIF fields does not necessarily invalidate it (the manifest is in the C2PA block, not EXIF).

For images already in circulation without provenance, [Encypher's platform supports perceptual hash search](/content-provenance/images) to identify derivative uses of originally signed images, since pixel-perfect matching fails on rescaled or re-encoded copies.

### Audio (6 formats)

The audio category covers: MP3, WAV, FLAC, AAC, OGG, M4A.

MP3 uses the ID3v2 PRIV frame to carry the C2PA manifest. WAV uses the RIFF INFO chunk structure. FLAC uses a custom METADATA_BLOCK_PICTURE-style approach adapted for JUMBF content. AAC, OGG, and M4A use format-appropriate metadata blocks with custom JUMBF and COSE implementation.

Audio provenance matters most in two contexts: music distribution, where unauthorized use in AI training and commercial sampling are the primary concerns, and spoken content such as podcasts and news audio, where transcription pipelines strip the audio to text and discard all origin metadata.

A podcast episode with an embedded C2PA manifest carries provenance through the audio file itself. When that episode is transcribed by an AI service, the manifest is present in the source file. The text output lacks that signal, which is a known gap in the transcription pipeline, but the rights holder can demonstrate that the source audio carried provenance at the time of ingestion.

### Video (4 formats)

The video category covers: MP4, MOV, WebM, MKV.

MP4 and MOV use the BMFF box structure (specifically, uuid boxes) to embed C2PA manifests. WebM and MKV use Matroska tag blocks with custom JUMBF and COSE content. All four formats support the full C2PA ingredient model, which means a composited video can carry manifests from each source clip, establishing provenance for the edit as a whole and for each component.

For live streams, v2.0.0 supports per-segment manifest embedding following C2PA 2.3 Section 19. Each CMAF segment in an HLS or DASH stream carries its own manifest that back-links to the previous segment's manifest hash. This creates a verifiable chain where any segment that was replaced or edited after the fact is detectable during playback verification.

### Documents (5 formats)

The document category covers: PDF, EPUB, DOCX, PPTX, HTML.

PDF uses the C2PA manifest stored in a dedicated metadata stream with a cross-reference to the document's content hash. EPUB uses a manifest file added to the ZIP container. DOCX and PPTX use custom XML parts added to the Office Open XML structure. HTML uses a script tag with type "application/c2pa+json" embedded in the document head.

The document category addresses a specific gap: documents circulate through legal, academic, and enterprise contexts where provenance questions have direct institutional consequences. A contract, a research paper, a regulatory filing, and a press release all need demonstrable provenance if their contents are disputed.

The [document provenance gap](/c2pa-standard/media-types) is one of the least-discussed aspects of the AI training data problem. PDFs of books, academic papers, and legal documents make up a large fraction of LLM training data. Without provenance, there is no machine-readable rights signal on any of that content.

### Fonts (3 formats)

The font category covers: TTF, OTF, WOFF2.

Fonts are intellectual property. Type foundries license fonts under specific terms that prohibit modification, redistribution as standalone files, and use in AI training datasets designed to replicate the typeface. C2PA manifests embedded in font files carry rights assertions that specify permitted uses.

The implementation uses a custom metadata table added to the font binary structure, distinct from existing font metadata tables (name, head, etc.) to avoid conflicts with rendering engines.

---

## The Unified /sign/media Endpoint

All 31 formats use the same endpoint: `POST /sign/media`.

The request includes the media file (as multipart form data or a base64-encoded body), the signer's credentials, optional assertions (AI-generated flag, rights claims, permitted uses), and optional ingredient manifests for composite content.

The endpoint detects the media type from the Content-Type header or file extension, routes the signing operation to the appropriate embedding implementation, and returns the signed file with the manifest embedded.

This unification matters for two reasons.

First, it simplifies integration. A CMS that wants to sign every piece of content it publishes does not need to implement 31 separate signing paths. It sends content to one endpoint and receives signed content back. The format-specific logic is handled server-side.

Second, it enables consistent manifest structure across formats. Every signed file, regardless of format, produces a manifest with the same claims structure, the same signer identity format, and the same content hash binding. This means a verification tool can parse manifests from a JPEG and an MP3 using the same parser, with format-specific manifest extraction handled transparently.

---

## Free Verification for All Formats

Verification is free for all 31 media types and requires no authentication.

The `POST /verify/media` endpoint accepts any supported file, extracts the embedded manifest, verifies the cryptographic signature against the signer's public key (retrieved from the signer's certificate or a public key registry), checks the content hash against the file, and returns the full manifest contents including signer identity, timestamp, and assertions.

The decision to make verification free and unauthenticated reflects a specific view about how content provenance infrastructure should work. Provenance is only useful as a trust signal if verification is widely accessible. A verification system that requires a subscription creates an asymmetry: creators pay to embed provenance, but readers cannot verify it without also paying. That asymmetry reduces adoption.

The [verification endpoint documentation](/content-provenance/verification) includes examples for all five media categories and shows how to interpret manifest contents for each assertion type.

---

## How Ingredients Work

C2PA supports the concept of ingredients, which are source assets that contributed to a derived work. The ingredient model lets a composite piece of content carry provenance for all its components.

A documentary film edited from footage shot on two different cameras, with licensed music, and a narration track can carry four ingredient manifests: one from each camera's footage, one from the music license, and one from the narration. The documentary's own manifest references each ingredient manifest by its content hash. During verification, a tool can walk the full ingredient chain and display the provenance of every component.

In v2.0.0, the /sign/media endpoint accepts an `ingredients` field in the request body. Each ingredient is specified as a content hash and an optional manifest URI. The signing operation embeds the ingredient references into the derived work's manifest.

This is particularly relevant for the music industry, where a produced track might derive from dozens of recorded elements, each with its own rights status. Ingredient provenance transforms a flat content hash into a verifiable production record.

---

## What Is Coming Next

Three additions are on the roadmap.

First, batch signing. The current endpoint handles one file per request. A batch endpoint will accept multiple files and return a signed bundle, supporting the use case of signing an entire content archive or a daily publication output.

Second, hardware security module integration. High-security signing environments require private keys that never leave HSM hardware. We are adding HSM key provider support for enterprise deployments where the signing operation must be executed in a certified hardware environment.

Third, stream signing for live video. While per-segment manifest embedding for CMAF streams is supported in v2.0.0, the streaming signing infrastructure requires server-side implementation at the ingest point. We are developing a signing proxy component that can sit between an encoder and a CDN ingest endpoint and embed per-segment manifests in real time.

---

## Getting Started

The API documentation covers all 31 media types with code examples in Python, TypeScript, Go, and Rust. The verification endpoint is available without authentication at the URL listed in the docs.

If you are building content provenance into a publishing platform, a CMS, or a content distribution system, the [unified media signing endpoint](/content-provenance/verification) is the starting point. We can handle the format complexity; your integration needs only one endpoint.

---

*Erik Svilich is Founder & CEO of Encypher and Co-Chair of the C2PA Text Provenance Task Force. He authored C2PA Section A.7: Embedding Manifests into Unstructured Text.*
