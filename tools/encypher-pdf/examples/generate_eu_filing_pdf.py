"""Generate the EU AI Act Code of Practice public comment as a signed PDF.

Uses the encypher-pdf library with Encypher design-system brand colors.
Signs the full submission text via the enterprise API at sentence-level
granularity, then renders into a PDF that preserves all invisible
provenance markers for round-trip verification.

Usage:
    # With signing (requires enterprise API running on localhost:8000):
    python generate_eu_filing_pdf.py

    # Layout preview without signing:
    python generate_eu_filing_pdf.py --no-sign

    # Custom output path:
    python generate_eu_filing_pdf.py --output /path/to/output.pdf
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
from urllib import error, request

from encypher_pdf.writer import Alignment, Document, TextStyle

# ---------------------------------------------------------------------------
# Brand colors (from packages/design-system/src/styles/theme.css)
# ---------------------------------------------------------------------------
DELFT_BLUE = (0.106, 0.184, 0.314)  # #1b2f50
BLUE_NCS = (0.165, 0.529, 0.769)  # #2a87c4
BODY_BLACK = (0.12, 0.12, 0.12)  # soft black for body text
GRAY_MUTED = (0.40, 0.40, 0.40)  # metadata lines

# ---------------------------------------------------------------------------
# Typography styles
# ---------------------------------------------------------------------------
STYLE_DOC_TITLE = TextStyle(
    font_size=16,
    bold=True,
    alignment=Alignment.CENTER,
    line_height=1.25,
    color=DELFT_BLUE,
    space_after=4,
)

STYLE_DOC_SUBTITLE = TextStyle(
    font_size=11,
    alignment=Alignment.CENTER,
    line_height=1.3,
    color=DELFT_BLUE,
    space_after=3,
)

STYLE_META = TextStyle(
    font_size=9,
    alignment=Alignment.CENTER,
    line_height=1.3,
    color=GRAY_MUTED,
    space_after=2,
)

STYLE_SECTION_HEADING = TextStyle(
    font_size=12,
    bold=True,
    line_height=1.2,
    color=DELFT_BLUE,
    space_before=16,
    space_after=6,
)

STYLE_BODY = TextStyle(
    font_size=10,
    line_height=1.4,
    alignment=Alignment.JUSTIFY,
    color=BODY_BLACK,
    space_after=6,
)

STYLE_BODY_FIRST = TextStyle(
    font_size=10,
    line_height=1.4,
    alignment=Alignment.JUSTIFY,
    color=BODY_BLACK,
    space_after=6,
    first_line_indent=0,
)

STYLE_RECOMMENDATION = TextStyle(
    font_size=10,
    bold=True,
    line_height=1.4,
    alignment=Alignment.JUSTIFY,
    color=BLUE_NCS,
    space_before=4,
    space_after=6,
    left_indent=0,
)

STYLE_SALUTATION = TextStyle(
    font_size=10,
    line_height=1.4,
    color=BODY_BLACK,
    space_after=8,
)

STYLE_SIGNOFF = TextStyle(
    font_size=10,
    line_height=1.2,
    color=BODY_BLACK,
    space_before=0,
    space_after=0,
)

STYLE_SIGNOFF_FIRST = TextStyle(
    font_size=10,
    line_height=1.2,
    color=BODY_BLACK,
    space_before=8,
    space_after=0,
)

STYLE_SIGNING_LINE = TextStyle(
    font_size=8,
    italic=True,
    alignment=Alignment.CENTER,
    line_height=1.3,
    color=GRAY_MUTED,
    space_before=16,
    space_after=0,
)

STYLE_BOLD_LABEL = TextStyle(
    font_size=10,
    bold=True,
    line_height=1.4,
    color=BODY_BLACK,
    space_after=4,
)

# ---------------------------------------------------------------------------
# Submission content (clean filing-ready text, no internal sections)
# ---------------------------------------------------------------------------

TITLE = "Encypher Corporation: Public Comment on the EU AI Act Code of Practice"
SUBTITLE = "Second Draft - Code of Practice for Transparency of AI-Generated Content"
META_LINES = [
    "Submitted by: Erik Svilich, Co-Chair, C2PA Text Provenance Task Force; Founder and CEO, Encypher Corporation",
    "Re: Second Draft Code of Practice for Transparency of AI-Generated Content under Articles 50(2) and 50(4) of the EU AI Act",
]

SALUTATION = "Dear Members of the Drafting Committee,"

INTRO = (
    "I am the Co-Chair of the C2PA Text Provenance Task Force and the specification author "
    'for C2PA 2.3 Section A.7 ("Embedding Manifests into Unstructured Text," published '
    "January 8, 2026). The task force includes Google, BBC, OpenAI, Adobe, and Microsoft. "
    "I submit these comments as technical input from the task force responsible for the text "
    "provenance standard this Code references."
)

INTRO_2 = (
    "The second draft is stronger than the first. The consolidation of measures, the added "
    "flexibility, and the removal of the AI-generated versus AI-assisted taxonomy all move "
    "the framework toward something that can be implemented and enforced in practice. One "
    "pattern warrants attention: the shift from mandatory to voluntary language between drafts. "
    'Several provisions that were requirements in the first draft are now "encouraged." Where '
    "this submission recommends strengthening specific provisions, it is because production-ready "
    "technology exists to meet the obligation and because voluntary compliance creates gaps the "
    "regulation was designed to close. Nine observations follow, each with a specific recommendation."
)


@dataclass
class Section:
    heading: str
    paragraphs: list[str]
    recommendation: str


SECTIONS: list[Section] = [
    Section(
        heading="1. C2PA as the Reference Interoperability Framework",
        paragraphs=[
            "The two-layered marking approach in this draft, secured metadata combined with "
            "watermarking, only works if providers and deployers across all 27 member states use "
            "a common technical standard. Without one, each provider builds proprietary marking. "
            "Detection tools multiply. Cross-provider verification becomes impossible. Deployers "
            "face a matrix of incompatible formats.",
            "C2PA 2.3, published January 8, 2026 and governed by the Joint Development Foundation "
            "under the Linux Foundation with over 100 member organizations, is the only published "
            "multi-stakeholder standard for content provenance with production implementations "
            "deployed at scale. The specification already defines machine-readable AI content "
            "assertion types (c2pa.ai_generated, c2pa.ai_training), providing the structured "
            "metadata vocabulary this Code requires. No competing standard offers equivalent "
            "multi-stakeholder governance, production deployment, media-type coverage, or "
            "established AI content assertion vocabularies.",
            "C2PA manifests are cryptographically signed assertions about content origin, the AI "
            'system involved, and any human review. That is what "secured metadata" means in '
            "practice. Combined with invisible embedding techniques (the watermarking layer), this "
            "delivers the two-layered architecture the Code of Practice describes.",
            "C2PA is an open specification. Anyone can implement it. Reference implementations are "
            "available under open-source licenses. Designating C2PA as the baseline creates "
            "interoperability, not vendor lock-in. GDPR references ISO standards for the same reason.",
        ],
        recommendation=(
            "Recommendation: Designate C2PA as the reference technical standard for content "
            "provenance marking under Article 50, while permitting additional complementary "
            "methods above this baseline."
        ),
    ),
    Section(
        heading="2. The Value of Granular, Sub-Document Marking",
        paragraphs=[
            "The draft contemplates document-level marking. A document is AI-generated or it is "
            "not. The C2PA standard, as published in Section A.7, provides this document-level "
            "baseline: a cryptographically signed manifest attesting to the provenance of a "
            "document as a whole. That baseline is production-ready and sufficient for minimum "
            "compliance.",
            "But content workflows do not produce clean documents. A news article contains an "
            "AI-generated summary alongside reporter-written analysis. A legal brief uses AI "
            "drafting for certain sections while counsel authors others. A corporate report blends "
            "AI-produced data summaries with human-written conclusions. In each case, the document "
            "is neither fully AI-generated nor fully human-authored. It is both.",
            "Document-level marking forces a binary choice that does not match this reality. "
            "Technologies exist today that extend beyond the C2PA document-level baseline to "
            "authenticate individual sentences, paragraphs, or sections within a document, binding "
            "provenance to specific text segments rather than to the document as a whole. The result "
            "is provenance that can identify which portions of a document involved AI generation, "
            "detect tampering at the specific passage that was modified, and verify whether an "
            "individual quotation is accurate or fabricated.",
            "These capabilities go beyond the C2PA standard. They are not required for minimum "
            "compliance. But they serve the regulation's transparency purpose more faithfully when "
            "content is hybrid, which is increasingly the norm.",
        ],
        recommendation=(
            "Recommendation: Note that best-practice implementations may provide sub-document "
            "granularity beyond the document-level baseline, and that such granularity better "
            "serves the transparency objective for hybrid human-AI content."
        ),
    ),
    Section(
        heading="3. Fingerprinting Should Be Recommended, Not Merely Optional",
        paragraphs=[
            "The draft makes fingerprinting and logging optional. For smaller providers, that is "
            "proportionate. For providers processing content at scale, it leaves a gap.",
            "Watermarks embedded in text can be stripped by paraphrasing, summarization, translation, "
            "and restructuring. AI systems perform these transformations routinely. An AI model that "
            "ingests a watermarked article and outputs a paraphrased summary has consumed the original "
            "content but destroyed the watermark. The provenance signal disappears at exactly the "
            "point where it matters most.",
            "Fingerprinting addresses this. Techniques such as locality-sensitive hashing identify "
            "content that has been transformed, not just copied verbatim. Fingerprinting is what "
            "distinguishes a detection framework that works only for exact copies from one that works "
            "for the derivatives AI systems actually produce.",
            "Without fingerprinting at the provider level, the detection protocol the Code of Practice "
            "envisions has a structural limitation: it catches verbatim reproduction but misses "
            "paraphrased use. For providers whose systems ingest and transform millions of documents, "
            "that limitation is not marginal.",
            "The privacy considerations the Committee weighed in making fingerprinting optional are "
            "real but addressable. Fingerprinting does not require linking content to individual "
            "identity. A provenance attestation system functions as a notary: it certifies that "
            "specific content existed in a specific state at a specific time, and whether it was "
            "subsequently modified. That attestation can be bound to a system or organization rather "
            "than a natural person.",
            "Privacy-preserving fingerprinting, using techniques such as locality-sensitive hashing "
            "that reduce content to non-reversible signatures, provides the detection benefit without "
            "creating a surveillance mechanism. Data minimization requirements (limiting retention "
            "duration, prohibiting reconstruction of original content from fingerprints, restricting "
            "access to authorized verification queries) can be specified alongside the fingerprinting "
            "recommendation.",
        ],
        recommendation=(
            'Recommendation: Characterize fingerprinting as "recommended for providers processing '
            'content at scale or for high-risk applications," rather than purely optional. Specify '
            "that fingerprinting implementations must comply with data minimization principles: "
            "non-reversible signatures, limited retention, no reconstruction of original content, "
            "and no linkage to natural persons without explicit legal basis. This is proportionate. "
            "It does not burden smaller operators. It closes the detection gap for the providers "
            "whose scale makes manual attribution impossible."
        ),
    ),
    Section(
        heading="4. Marking Must Survive Content Distribution",
        paragraphs=[
            "A news article generated by AI is published on one site, syndicated through a wire "
            "service, aggregated by three platforms, and quoted on social media. All of this happens "
            "within hours. If the marking is stripped at the first copy-paste, the compliance "
            "obligation is satisfied at publication and violated everywhere the content actually "
            "reaches readers.",
            "This is not a hypothetical scenario. It is how content distribution works today, and "
            "it is the primary channel through which AI-generated content reaches end users.",
            "The two-layered approach the Code of Practice describes addresses this, but only if "
            "both layers are understood as serving distinct functions:",
            "Secured metadata (C2PA manifests) provides the authoritative, cryptographically signed "
            "provenance record. It is rich and structured. It can be stripped by copy-paste. "
            "Invisible embedding (watermarking within the text itself, using techniques such as "
            "non-rendering Unicode characters) survives copy-paste, reformatting, and redistribution. "
            "It carries less data but persists where metadata does not.",
            "These layers are not redundant. One provides depth. The other provides resilience. "
            "Together they provide marking that works at the point of publication and at every "
            "subsequent point of redistribution.",
        ],
        recommendation=(
            "Recommendation: Include a distribution survival principle. Marking methods should "
            "demonstrate resilience across common distribution paths: copy-paste, syndication, "
            "aggregation, and cross-platform sharing. The two-layered approach should be understood "
            "as complementary layers serving metadata richness and distribution resilience, not as "
            "two methods applied in parallel for redundancy alone. Distribution survival should be "
            "a mandatory quality criterion under Commitment 3, not merely an implied benefit of "
            "the multi-layered approach."
        ),
    ),
    Section(
        heading="5. Streaming and Real-Time Content Should Be Explicitly Addressed",
        paragraphs=[
            "The Code's obligations extend to all AI systems generating synthetic text content. "
            "The highest-volume category of such content, chat-based and API-based AI interactions, "
            "produces output as a token-by-token stream rather than a static document. A chatbot "
            "emits tokens one at a time over seconds or minutes. An API returns a response as a "
            "server-sent event stream. The completed output may never exist as a static file. The "
            "user consumes it in real time.",
            "Marking protocols that require a completed document before signing can begin do not "
            "work for this content. Between the first token and the last, the output exists in an "
            "unmarked state. For chat-based AI applications, the primary consumer interface for "
            "generative AI, that unmarked state spans the entire interaction.",
            "Incremental authentication during streaming is technically feasible. Cryptographic "
            "authentication structures can be constructed progressively as tokens are generated, "
            "with the final proof computed when generation completes. Production implementations "
            "of this approach exist today.",
        ],
        recommendation=(
            "Recommendation: Clarify that marking obligations apply to streaming and real-time "
            "AI-generated content, and that incremental authentication during generation is a "
            "valid compliance method. Providers of chat-based and API-based AI systems should not "
            "be understood as exempt from marking obligations because their outputs are delivered "
            "as streams rather than static documents."
        ),
    ),
    Section(
        heading="6. Short Text Segments Should Not Be Exempted",
        paragraphs=[
            "The draft includes a carve-out for short text segments. This exemption should be " "removed.",
            "The premise behind the carve-out is that marking short text is technically infeasible. "
            "That premise is incorrect for standards-based provenance approaches. A C2PA manifest is "
            "metadata attached to content, not a statistical signal hidden inside it. There is no "
            "minimum content length. A manifest can be attached to a single sentence, a one-word "
            "chatbot reply, an automated caption, or any other short-form output. A chatbot that "
            'responds "OK" to a user query can have a provenance manifest attached to that '
            "two-character response. Production implementations handle text of any length today, "
            "with no minimum character threshold.",
            "The concern driving the carve-out applies to a specific category of watermarking "
            "techniques, those that embed signals by modifying statistical properties of the text "
            "itself. Those techniques do need space to work. But the two-layered approach the Code "
            "of Practice already envisions solves this: the secured metadata layer (C2PA manifest) "
            "functions at any content length, while the watermarking layer adds resilience for "
            "content long enough to support embedding. For a one-word chatbot reply, the manifest "
            "alone provides the provenance signal. For a 2,000-word article, both layers apply.",
            "Three reasons to remove the carve-out:",
            "Volume. Short-form AI-generated content is the highest-volume category of AI output "
            "reaching consumers. Chatbot interactions, generated summaries, automated replies, "
            "social media posts, image captions. Collectively, these represent more AI-generated "
            "text encounters per day than all long-form content combined. Exempting short text "
            "creates a transparency gap that covers the majority of what consumers actually see.",
            "Perverse incentive. The carve-out invites fragmentation. A provider generating a "
            "500-word response can present it as a sequence of short messages, each below the "
            "threshold. The obligation disappears not because the content is different, but because "
            "it was chunked.",
            "Consumer exposure. Chatbots, automated customer service agents, and generated social "
            "media replies are the AI applications most likely to be mistaken for human "
            "communication. They produce short-form text, and they are exactly the outputs where "
            "transparency serves the regulation's purpose most directly.",
        ],
        recommendation=(
            "Recommendation: Remove the short text carve-out. C2PA manifests provide a technically "
            "feasible marking method for text of any length, including single sentences. If the "
            "Committee determines a transition accommodation is necessary, it should define a "
            "specific and narrow character threshold, include a sunset date, and require providers "
            "to demonstrate that no technically feasible marking method exists for their output "
            "type. A blanket exemption based on length alone is not justified by the current state "
            "of the technology. At minimum, if a length threshold is retained, it should apply only "
            "to the watermarking layer (Sub-measure 1.1.2), not to the secured metadata layer "
            "(Sub-measure 1.1.1). A C2PA manifest can be generated for text of any length. There "
            "is no technical basis for exempting short text from metadata-based provenance."
        ),
    ),
    Section(
        heading="7. Verification Must Be Freely Accessible",
        paragraphs=[
            "Marking AI-generated content has value only if third parties can check the markings. "
            "Journalists, researchers, regulators, platforms, and ordinary citizens all need the "
            "ability to verify whether content carries provenance signals and what those signals "
            "assert.",
            "Measure 2.1 already moves in this direction by requiring that an interface be made "
            "available free of charge for verification. This is the right instinct. The "
            "recommendation here is to make this principle explicit and universal: free verification "
            "should apply to all marking layers, not only to the detection interface the provider "
            "operates. Third-party verification tools, whether browser-based, server-side, or "
            "purpose-built for research, should be able to verify provenance markings without "
            "commercial agreements or API keys.",
            "If verification requires payment, proprietary software, or a commercial account, the "
            "transparency framework creates a two-tier system. Organizations that pay see provenance "
            "data. The general public does not. That outcome contradicts the regulation's purpose.",
            "Free, unauthenticated verification of content provenance is technically and commercially "
            "feasible. Production implementations offer it today across text, images, audio, video, "
            "and documents, at no cost and with no account required. The browser-based tools that "
            "perform this verification are freely available as extensions that any user can install. "
            "Verification can be a public good while the infrastructure for creating and embedding "
            "provenance remains a commercial service. The marginal cost of verification is low "
            "relative to the cost of signing.",
            "Free verification also generates a network effect. Every check strengthens the trust "
            "chain. Journalists verifying content before publication, platforms checking provenance "
            "before hosting, and researchers auditing AI outputs all contribute to the transparency "
            "infrastructure the regulation aims to build. Gating verification behind payment reduces "
            "the number of checks, which reduces the value of the entire framework.",
        ],
        recommendation=(
            "Recommendation: Require that verification of content provenance markings be freely "
            "accessible to any party, without commercial agreements, proprietary software, or "
            "authentication. Providers should offer or support a publicly accessible verification "
            "mechanism for the markings they embed."
        ),
    ),
    Section(
        heading="8. The Removal of the AI-Generated vs. AI-Assisted Taxonomy Is Correct",
        paragraphs=[
            'The second draft removes the distinction between "AI-generated" and "AI-assisted" '
            "content. This is the right decision. The first draft's taxonomy was unenforceable and "
            "should not return.",
            "The problem with the distinction was measurement. No reliable method exists to determine "
            "whether a document is 51% AI-generated or 49% AI-generated. Any threshold would be "
            "arbitrary. Any self-reporting obligation would create incentives to understate AI "
            "involvement. A company using AI to draft an entire document could claim it was "
            '"AI-assisted" because a human clicked approve. The compliance framework would depend '
            "on a distinction that cannot be objectively measured, consistently applied, or "
            "meaningfully audited.",
            "A provenance-based approach solves this. Rather than classifying the degree of AI "
            "involvement, provenance records what happened: which AI system was used, what actions "
            "it performed, what human review occurred, and a cryptographic verification of the final "
            "output. The C2PA specification already defines the assertion vocabulary for this: "
            "c2pa.ai_generated, c2pa.ai_training, and structured action records. The question shifts "
            'from "how much AI was in this?" to "what is the verifiable chain of origin?"',
            "For deployers, the removal simplifies compliance. The obligation becomes binary: if an "
            "AI system was involved in producing this content, attach provenance metadata and "
            "disclose accordingly. That obligation is clear, implementable, and auditable. The "
            "previous taxonomy made it ambiguous.",
        ],
        recommendation=(
            "Recommendation: Maintain the current approach. Affirm that provenance-based marking, "
            "recording what AI system was involved and what human review occurred, satisfies the "
            "transparency obligation without requiring quantitative classification of AI contribution."
        ),
    ),
    Section(
        heading="9. Editorial Review Claims Should Be Verifiable Through Standardized Provenance Records",
        paragraphs=[
            "Commitment 4 of Section 2 allows deployers to forgo disclosure of AI-generated text "
            "when human review or editorial control has occurred and a natural or legal person holds "
            "editorial responsibility. This exception is appropriate. It recognizes that professional "
            "editorial workflows already provide the transparency the regulation seeks.",
            "But the exception currently requires only internal documentation: a description of "
            "organizational measures and the identity of the responsible person. This creates an "
            "enforcement gap. A deployer can claim editorial review occurred without any externally "
            "verifiable evidence that it did.",
            "Provenance standards can close this gap. A C2PA manifest can record not only that "
            "content was AI-generated, but also that a human review step occurred, who or what "
            "organization performed it, and when. This record is cryptographically signed and "
            "externally verifiable. It transforms the editorial review exception from a self-reported "
            "assertion into a provenance-backed attestation.",
            "This does not impose a new burden. It uses the same provenance infrastructure that "
            "providers are already required to implement under Section 1. The deployer's obligation "
            "is simply to add a human-review assertion to the existing provenance chain before "
            "publication.",
        ],
        recommendation=(
            "Recommendation: Specify that deployers relying on the editorial review exception under "
            "Commitment 4 should document the human review step using standardized, externally "
            "verifiable provenance records, such as C2PA manifests with human-review assertions, "
            "rather than internal documentation alone. This ensures the exception is auditable by "
            "regulators and credible to the public."
        ),
    ),
]

CLOSING_PARAGRAPHS = [
    "The C2PA text provenance specification was published January 8, 2026. It was developed "
    "collaboratively by publishers, AI companies, technology platforms, and media organizations. "
    "Production implementations are deployed. The specification defines the secured metadata "
    "format, the AI content assertion vocabulary, and the verification protocol this Code of "
    "Practice needs as its technical foundation.",
    "The nine recommendations above address areas where the current draft either understates "
    "what the technology can do (short text, streaming, fingerprinting, editorial review "
    "verification) or misses an opportunity to require interoperability and accountability "
    "(C2PA reference, free verification, distribution survival, deployer-side provenance). In "
    "several cases, the shift from mandatory to voluntary language between drafts weakens "
    "provisions that production-ready technology can support. In each case, the technology to "
    "meet a stronger requirement exists today.",
    "The C2PA Text Provenance Task Force is available to provide technical support to the "
    "Committee as the Code of Practice moves toward finalization.",
]

SIGNOFF_LINES = [
    "Erik Svilich",
    "Co-Chair, C2PA Text Provenance Task Force",
    "Founder and CEO, Encypher Corporation",
    "erik.svilich@encypher.com",
    "encypher.com",
]

SIGNING_LINE = "This document is signed with C2PA content provenance at sentence-level granularity. " "Verify at encypher.com/tools/verify"

# ---------------------------------------------------------------------------
# Enterprise API signing
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# URLs and UTM tracking
# ---------------------------------------------------------------------------
UTM_PARAMS = "utm_source=eu_ai_act_filing&utm_medium=document&utm_campaign=public_comment_2026"
VERIFY_URL = f"https://encypher.com/tools/verify?{UTM_PARAMS}"
FOOTER_URL = f"https://encypher.com?{UTM_PARAMS}"

ENTERPRISE_API_URL = "https://api.encypher.com/api/v1/sign"


def _post_json(url: str, payload: dict[str, Any], headers: Optional[dict[str, str]] = None, timeout: int = 120) -> dict[str, Any]:
    raw = json.dumps(payload).encode("utf-8")
    hdrs = {
        "Content-Type": "application/json",
        "User-Agent": "encypher-pdf/0.1.0",
    }
    if headers:
        hdrs.update(headers)
    req = request.Request(url, data=raw, headers=hdrs, method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body}") from exc


LOCAL_API_URL = "http://localhost:8000/api/v1/sign"
LOCAL_DEFAULT_KEY = "enterprise-api-key-for-testing"  # pragma: allowlist secret


def sign_text(full_text: str, use_local: bool = False) -> str:
    """Sign the full submission text via the enterprise API at sentence level."""
    api_url = LOCAL_API_URL if use_local else ENTERPRISE_API_URL
    api_key = os.environ.get("ENCYPHER_API_KEY") or os.environ.get("ENTERPRISE_API_KEY")
    if not api_key:
        if use_local:
            api_key = LOCAL_DEFAULT_KEY
        else:
            raise RuntimeError("Set ENCYPHER_API_KEY env var for live API signing")

    payload = {
        "text": full_text,
        "document_title": "EU AI Act Code of Practice - Public Comment",
        "options": {
            "segmentation_level": "sentence",
            "manifest_mode": "micro",
            "ecc": True,
            "legacy_safe": False,
            "store_c2pa_manifest": True,
            "action": "c2pa.created",
            "document_type": "article",
        },
    }

    print(f"  API: {api_url}")
    data = _post_json(
        api_url,
        payload,
        headers={"Authorization": f"Bearer {api_key}"},
    )

    # Response structure: {success, data: {document: {signed_text, ...}, ...}}
    inner = data.get("data", data)
    doc_data = inner.get("document", inner)

    signed_text = doc_data.get("signed_text") or doc_data.get("encoded_text") or data.get("encoded_text")
    if not isinstance(signed_text, str) or not signed_text:
        error = data.get("error")
        if error:
            raise RuntimeError(f"Signing API error: {error}")
        raise RuntimeError(f"Signing API returned no signed text. Response keys: {list(data.keys())}")

    doc_id = doc_data.get("document_id", "unknown")
    segments = doc_data.get("total_segments") or inner.get("total_segments", "?")
    print(f"  Signed: document_id={doc_id}, segments={segments}")
    return signed_text


# ---------------------------------------------------------------------------
# Build the plain text for signing (all visible text, joined by \n\n)
# ---------------------------------------------------------------------------


def build_plain_text() -> str:
    """Assemble the full submission as plain text for signing."""
    parts: list[str] = []

    parts.append(TITLE)
    parts.append(SUBTITLE)
    for line in META_LINES:
        parts.append(line)
    parts.append(SALUTATION)
    parts.append(INTRO)
    parts.append(INTRO_2)

    for section in SECTIONS:
        parts.append(section.heading)
        for para in section.paragraphs:
            parts.append(para)
        parts.append(section.recommendation)

    parts.append("Closing")
    for para in CLOSING_PARAGRAPHS:
        parts.append(para)
    for line in SIGNOFF_LINES:
        parts.append(line)
    parts.append(SIGNING_LINE)

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Build the PDF
# ---------------------------------------------------------------------------


def build_pdf(output_path: Path, signed_text: Optional[str] = None) -> None:
    """Render the submission as a branded PDF.

    If signed_text is provided, the signed (marker-embedded) version of each
    paragraph is rendered instead of the plain text, and the full signed text
    is stored in the EncypherSignedText metadata stream.
    """
    # If we have signed text, split it back into paragraphs aligned with
    # the plain text structure. The signer preserves \n\n paragraph breaks.
    signed_parts: Optional[list[str]] = None
    if signed_text:
        signed_parts = signed_text.split("\n\n")

    part_idx = 0

    def _text(plain: str) -> str:
        """Return signed version of a paragraph if available, else plain."""
        nonlocal part_idx
        if signed_parts and part_idx < len(signed_parts):
            result = signed_parts[part_idx]
            part_idx += 1
            return result
        part_idx += 1
        return plain

    doc = Document(
        margin_top=60,
        margin_bottom=54,
        margin_left=62,
        margin_right=62,
        footer_text="Encypher Corporation  |  encypher.com  |  Content Provenance Infrastructure",
        footer_url=FOOTER_URL,
    )

    # Title block
    doc.add_text(_text(TITLE), STYLE_DOC_TITLE)
    doc.add_text(_text(SUBTITLE), STYLE_DOC_SUBTITLE)
    doc.add_spacer(4)

    # Metadata
    for line in META_LINES:
        doc.add_text(_text(line), STYLE_META)
    doc.add_spacer(10)

    # Salutation
    doc.add_text(_text(SALUTATION), STYLE_SALUTATION)

    # Intro paragraphs
    doc.add_text(_text(INTRO), STYLE_BODY_FIRST)
    doc.add_text(_text(INTRO_2), STYLE_BODY)

    # Nine sections
    for section in SECTIONS:
        doc.add_text(_text(section.heading), STYLE_SECTION_HEADING)
        for i, para in enumerate(section.paragraphs):
            style = STYLE_BODY_FIRST if i == 0 else STYLE_BODY
            doc.add_text(_text(para), style)
        doc.add_text(_text(section.recommendation), STYLE_RECOMMENDATION)

    # Closing
    doc.add_text(_text("Closing"), STYLE_SECTION_HEADING)
    for i, para in enumerate(CLOSING_PARAGRAPHS):
        style = STYLE_BODY_FIRST if i == 0 else STYLE_BODY
        doc.add_text(_text(para), style)

    # Sign-off
    doc.add_spacer(4)
    for i, line in enumerate(SIGNOFF_LINES):
        style = STYLE_SIGNOFF_FIRST if i == 0 else STYLE_SIGNOFF
        doc.add_text(_text(line), style)

    # Signing line (clickable)
    doc.add_text(_text(SIGNING_LINE), STYLE_SIGNING_LINE, url=VERIFY_URL)

    # Store signed text for lossless extraction
    if signed_text:
        doc.set_signed_text(signed_text)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    print(f"  PDF saved: {output_path} ({output_path.stat().st_size:,} bytes)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
# PDF-level C2PA signing (document_signing_service)
# ---------------------------------------------------------------------------

ENTERPRISE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "enterprise_api"
CERTS_DIR = ENTERPRISE_DIR / "tests" / "c2pa_test_certs"


def sign_pdf_c2pa(pdf_path: Path) -> None:
    """Apply document-level C2PA signing to the PDF binary.

    This adds a COSE_Sign1 manifest embedded per the C2PA spec, covering the
    entire PDF byte stream. Layered on top of the sentence-level text signing.
    """
    import sys

    sys.path.insert(0, str(ENTERPRISE_DIR))

    from app.services.document_signing_service import sign_document

    key_path = CERTS_DIR / "private_key.pem"
    chain_path = CERTS_DIR / "cert_chain.pem"
    if not key_path.exists() or not chain_path.exists():
        print(f"  WARNING: Test certs not found at {CERTS_DIR}, skipping PDF C2PA signing")
        return

    private_key_pem = key_path.read_text()
    cert_chain_pem = chain_path.read_text()

    pdf_bytes = pdf_path.read_bytes()
    print(f"  PDF C2PA signing: {len(pdf_bytes):,} bytes input")

    result = sign_document(
        pdf_bytes,
        "application/pdf",
        title="EU AI Act Code of Practice - Public Comment - Encypher Corporation",
        org_id="encypher_corporation",
        document_id="eu_ai_act_public_comment_2026",
        asset_id="eu_ai_act_cop_filing_v3",
        action="c2pa.created",
        private_key_pem=private_key_pem,
        cert_chain_pem=cert_chain_pem,
    )

    pdf_path.write_bytes(result.signed_bytes)
    print(f"  PDF C2PA signed: {len(result.signed_bytes):,} bytes output (+{len(result.signed_bytes) - len(pdf_bytes):,} manifest bytes)")
    if result.instance_id:
        print(f"  C2PA instance_id: {result.instance_id}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate EU AI Act public comment PDF")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output PDF path (default: examples/output/eu_ai_act_public_comment.pdf)",
    )
    parser.add_argument(
        "--no-sign",
        action="store_true",
        help="Skip signing (layout preview only)",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use local API (localhost:8000) instead of live api.encypher.com",
    )
    parser.add_argument(
        "--no-pdf-sign",
        action="store_true",
        help="Skip PDF-level C2PA signing (text signing only)",
    )
    args = parser.parse_args()

    output_path = Path(args.output) if args.output else Path(__file__).resolve().parent / "output" / "eu_ai_act_public_comment.pdf"

    print("Building EU AI Act public comment PDF...")
    plain_text = build_plain_text()
    print(f"  Plain text: {len(plain_text):,} characters")

    signed_text: Optional[str] = None
    if not args.no_sign:
        target = "local API" if args.local else "live API (api.encypher.com)"
        print(f"  Signing text via {target}...")
        signed_text = sign_text(plain_text, use_local=args.local)
        print(f"  Signed text: {len(signed_text):,} characters ({len(signed_text) - len(plain_text):,} invisible markers)")
    else:
        print("  Skipping text signing (--no-sign)")

    build_pdf(output_path, signed_text)

    if not args.no_sign and not args.no_pdf_sign:
        print("  Applying PDF-level C2PA signing...")
        sign_pdf_c2pa(output_path)

    print("Done.")


if __name__ == "__main__":
    main()
