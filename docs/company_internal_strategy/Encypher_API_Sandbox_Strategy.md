# Encypher API Sandbox \- Interactive Developer Experience

## Standards-Based Text Provenance Demonstration

**Last Updated:** January 8, 2026
**Status:** Post-Standard Publication (C2PA 2.3 Released)
**Version:** 3.1
**Distribution:** Product & Engineering Teams

---

## Strategic Context

As Co-Chair of the C2PA Text Provenance Task Force, our API sandbox demonstrates both standards compliance AND exclusive enterprise capabilities. This isn't about competing with detection tools--it's about showing the difference between unmarked text (no proof) and cryptographically watermarked text (mathematical proof).

The sandbox drives commercial conversion by showing how our patent-pending sentence-level tracking extends the C2PA standard to enable formal notice, licensing infrastructure, and performance intelligence.

---

## 1\. Objectives

### Primary Objective

Demonstrate the transformation from unmarked text (no proof of origin) to cryptographically watermarked text (mathematical proof that survives copy-paste), showcasing both standard C2PA implementation AND our patent-pending enterprise enhancements.

### Secondary Objectives

- Accelerate developer adoption of our C2PA reference implementation
- Showcase sentence-level tracking for formal notice and licensing
- Generate enterprise leads through capability discovery
- Provide instant "aha moment" about cryptographic watermarking value

---

## 2\. Target Audiences

### Primary: Technical Decision Makers

- CTOs evaluating C2PA implementation options
- Head of Engineering at publishers/enterprises
- Technical architects assessing text provenance infrastructure

### Secondary: Developers

- Software engineers implementing content authentication
- AI/ML engineers adding provenance to models
- Security engineers evaluating cryptographic approaches

---

## 3\. Two-Tier Sandbox Experience

### Tier 1: Free Tier (Full Signing)

- Document-level cryptographic watermarking
- Standard verification
- Basic metadata embedding
- **Message: "This is C2PA standard--proof of origin at document level"**

### Tier 2: Enforcement + Enterprise (Commercial)

- Attribution Analytics (where your signed content appears across the web -- aggregators, RAG systems, scrapers, content platforms)
- Minimal invisible embeddings (Unicode variation selectors)
- Real-time streaming support (WebSocket/SSE)
- Tamper detection showing exact modifications
- Formal notice capability
- Performance intelligence
- Public verification API (no auth required)
- **Message: "This enables licensing, governance, and attribution intelligence"**

---

## 4\. Interactive Features

### Core Functionality:

**Mode Selector:**

- "Free Tier (Full Signing)"
- "Enforcement + Enterprise"
- "Real-Time Streaming Demo"
- "Compare Unmarked vs. Marked"

**Smart Examples:**

- Unmarked text ' marked transformation
- Publisher formal notice scenarios
- AI company attribution intelligence
- Copy-paste survival demonstration
- Real-time LLM signing (streaming)
- Invisible embedding extraction & verification

**Real-Time Comparison:**

- Side-by-side: unmarked / basic / enterprise
- Highlighting cryptographic proof differences
- Formal notice capability
- Attribution intelligence preview

---

## 5\. Sandbox Wireframe

\+------------------------------------------------------------------------+

| \[ENCYPHER API SANDBOX\] |

| |

| H1: From Unmarked to Provable: Text Authentication Standards |

| P: Co-Chair of C2PA Text Provenance Task Force |

| P: See cryptographic watermarking that survives copy-paste |

| |

| \+--------------------------------------------------------------------+ |

| | Mode: \[Unmarked Text\] \[Basic C2PA --\] \[Enterprise --\] \[Compare\] | |

| \+--------------------------------------------------------------------+ |

| |

| \+----------------------------------+ \+------------------------------+ |

| | \[INPUT PANEL\] | | \[OUTPUT PANEL\] | |

| | | | | |

| | Scenario: \[Publisher Notice --\] | | Tab: \[Signed | Verified | | |

| | - Formal Notice | | Copy-Paste Test | | |

| | - Copy-Paste Survival | | Attribution\] | |

| | - Attribution Intel | | | |

| | - Tamper Detection | | \+---------------------------+| |

| | | | | UNMARKED TEXT: || |

| | Content: | | | No proof of origin || |

| | \+------------------------------+ | | | No copy-paste survival || |

| | | Premium content from NYT | | | | || |

| | | describing recent events. | | | | BASIC C2PA: || |

| | | This sentence explains the | | | | ... Document watermarked || |

| | | situation. This was modified | | | | No sentence tracking || |

| | | without detection. | | | | Limited copy-paste || |

| | \+------------------------------+ | | | || |

| | | | | ENTERPRISE: || |

| | Publisher: \[NYT \] | | | ... Document watermarked || |

| | Use: \[Formal Notice \] | | | ... Sentence 1: " || |

| | | | | ... Sentence 2: " || |

| | \[Watermark\] \[Copy-Paste\] \[Verify\]| | | Sentence 3: MODIFIED || |

| | | | | ... Formal Notice Ready || |

| \+----------------------------------+ \+------------------------------+ |

| |

| \+--------------------------------------------------------------------+ |

| | \[CODE GENERATION PANEL\] | |

| | | |

| | Language: \[Python --\] \[Node.js\] \[cURL\] \[Java\] | |

| | | |

| | \`\`\`python | |

| | \# Basic C2PA (Open Source) | |

| | from encypher import C2PA | |

| | signer \= C2PA() | |

| | watermarked \= signer.sign(content, metadata) | |

| | \# Document-level proof of origin | |

| | | |

| | \# Enterprise SDK (Commercial License) | |

| | from encypher\_enterprise import EncypherClient | |

| | client \= EncypherClient(api\_key="encypher\_...") | |

| | | |

| | \# Sign with sentence-level tracking | |

| | result \= client.sign( | |

| | text=content, | |

| | title="Article Title", | |

| | metadata={"author": "Jane Doe"}, | |

| | use\_sentence\_tracking=True \# Patent-pending | |

| | ) | |

| | | |

| | \# Real-time streaming support | |

| | from encypher\_enterprise import StreamingSigner | |

| | signer \= StreamingSigner(client) | |

| | for chunk in llm\_stream: | |

| | signed\_chunk \= signer.process\_chunk(chunk) | |

| | final \= signer.finalize() | |

| | \`\`\` | |

| | | |

| | \[Copy Code\] \[View Documentation\] \[Try Interactive Demo\] | |

| \+--------------------------------------------------------------------+ |

| |

| \+--------------------------------------------------------------------+ |

| | \[CAPABILITY COMPARISON\] | |

| | | |

| | Feature | Unmarked | Basic C2PA | Enterprise | |

| | \---------------------------|----------|------------|------------- | |

| | Proof of Origin | | Document | Sentence | |

| | Survives Copy-Paste | | Limited | ... Yes | |

| | Invisible Embeddings | | | ... Yes | |

| | Real-Time Streaming | | | ... Yes | |

| | Public Verification API | | | ... Yes | |

| | Formal Notice Capability | | | ... Yes | |

| | Sentence-Level Tracking | | | ... Patent | |

| | Tamper Location Detection | | | ... Yes | |

| | Performance Intelligence | | | ... Yes | |

| | Court-Admissible Evidence | | Limited | ... Yes | |

| | | |

| | \[Start Free Trial\] \[Schedule Demo\] \[View Pricing\] | |

| \+--------------------------------------------------------------------+ |

| |

| \[CTA BAR\] |

| "Co-Chair of C2PA Text Provenance Task Force" |

| "Building standards with Google, BBC, OpenAI, Adobe, Microsoft" |

| \[Publisher Demo\] \[AI Company Demo\] \[Enterprise Info\] |

\+------------------------------------------------------------------------+

---

## 6\. Key Interaction Flows (Updated)

### Flow 1: Unmarked ' Marked Transformation

1. User starts with unmarked text sample
2. Shows: no proof of origin, no copy-paste survival
3. User selects "Watermark with C2PA"
4. Comparison shows:
 - Unmarked: No proof
 - Basic: Document-level proof
 - Enterprise: Sentence-level proof \+ formal notice
5. Copy-paste test demonstrates survival
6. CTA: "This enables licensing. See full demo."

### Flow 2: Formal Notice Capability

1. User selects "Publisher Formal Notice" scenario
2. Pre-loaded publisher content appears
3. User watermarks with Enterprise mode
4. Shows formal notice capability enabled
5. Demonstrates sentence-level attribution
6. CTA: "Join the publisher coalition" ' **encypherai.com/publisher-demo**

### Flow 3: AI Provenance Infrastructure

1. User selects "AI Provenance Integration"
2. Shows how AI companies benefit from integrating provenance checking on their ingestion pipeline
3. Tier 1 (no integration): Web-surface detection of signed content on aggregators, RAG systems, scrapers
4. Tier 2 (with integration): Ingestion-time provenance checking -- know what marked content entered your pipeline
5. Enterprise: Sentence-level attribution and performance intelligence when integrated
6. CTA: "Infrastructure for AI companies" ' **encypherai.com/ai-demo**

---

## 7\. API Endpoints to Demonstrate

### Core Endpoints (All Tiers)

**POST /api/v1/sign**

- Sign content with C2PA manifest
- Demo: Show request/response with document ID and verification URL
- Highlight: \<100ms response time

**POST /api/v1/verify**

- Verify signed content and detect tampering
- Demo: Show valid vs. tampered content detection
- Highlight: Exact tamper location identification

**POST /api/v1/lookup**

- Lookup sentence provenance (Professional+)
- Demo: Find original source of any sentence
- Highlight: Context window with surrounding sentences

### Enterprise Endpoints

**POST /api/v1/enterprise/merkle/encode**

- Encode document into Merkle tree for sentence tracking
- Demo: Show tree structure and node count
- Highlight: Patent-pending sentence-level hashing

**POST /api/v1/enterprise/merkle/attribute**

- Find source documents using Merkle tree matching
- Demo: Source attribution with similarity scores
- Highlight: Performance intelligence

**POST /api/v1/enterprise/embeddings/encode-with-embeddings**

- Create invisible signed embeddings using Unicode variation selectors
- Demo: Show invisible embedding in action
- Highlight: Zero visible footprint, survives copy-paste

**GET /api/v1/public/verify/{ref\_id}** (No Auth Required)

- Public verification of embeddings
- Demo: Third-party verification without API key
- Highlight: Partner integration capability

### Streaming Endpoints (NEW)

**WS /api/v1/stream/sign**

- Real-time WebSocket signing for LLM outputs
- Demo: Live streaming with incremental signing
- Highlight: Sign as you generate

**GET /api/v1/stream/events**

- Server-Sent Events (SSE) for streaming
- Demo: Alternative to WebSocket for simpler integration
- Highlight: HTTP-based streaming

**POST /api/v1/stream/session/create**

- Create streaming session with configuration
- Demo: Session management for long-running streams

---

## 8\. SDK Capabilities to Showcase

### Python SDK (encypher-enterprise)

**Repository Signing**

from encypher\_enterprise import RepositorySigner

signer \= RepositorySigner(client)

result \= signer.sign\_directory(

 directory=Path("./articles"),

 patterns=\["\*.md"\],

 incremental=True, \# 10x faster\!

 use\_git\_metadata=True

)

- Demo: Batch sign entire content repositories
- Highlight: Incremental signing (only changed files)

**Streaming Support**

from encypher\_enterprise import StreamingSigner

signer \= StreamingSigner(client)

for chunk in openai\_stream:

 signed \= signer.process\_chunk(chunk)

final \= signer.finalize()

- Demo: Real-time LLM output signing
- Highlight: Works with OpenAI, Anthropic, any LLM

**LLM Integrations**

from encypher\_enterprise.integrations import EncypherLangChain

llm \= EncypherLangChain(

 base\_llm=ChatOpenAI(),

 encypher\_client=client,

 auto\_sign=True

)

- Demo: Drop-in wrappers for LangChain, OpenAI, LiteLLM
- Highlight: Zero code changes to existing LLM pipelines

**Metadata Providers**

from encypher\_enterprise import GitMetadataProvider, FrontmatterMetadataProvider

git\_provider \= GitMetadataProvider()

frontmatter\_provider \= FrontmatterMetadataProvider()

- Demo: Automatic metadata extraction from git history and frontmatter
- Highlight: No manual metadata entry required

**CI/CD Integration**

- GitHub Actions workflow templates included
- GitLab CI configuration examples
- Demo: Auto-sign on every commit
- Highlight: Set up in 2 minutes

---

## 9\. Technical Implementation Notes

### Authentication:

- Demo mode: Pre-configured with limited calls (10 per session)
- Authenticated: Full sandbox with user's API key
- Enterprise trial: 14-day full features
- Public verification: No auth required for embedding verification

### Rate Limiting:

- Demo: 10 requests per session
- Free tier: 100 requests per day
- Enterprise trial: Unlimited

### Backend Requirements:

- Separate endpoints for basic vs. enterprise
- Real-time sentence-level watermarking
- WebSocket/SSE streaming endpoints
- Minimal embedding encoding/extraction
- Public verification API (no auth)
- Copy-paste survival testing
- Formal notice generation
- Performance analytics simulation

---

## 10\. Conversion Elements (Updated)

### Strategic CTAs:

**For Developers:**

- "Get Free C2PA Implementation" ' Capture lead
- "View GitHub Repository" ' Drive open source adoption
- "Join Standards Community" ' Build ecosystem

**For Publishers:**

- "See Formal Notice Demo" ' **encypherai.com/publisher-demo**
- "Calculate Licensing ROI" ' Sales qualification
- "Join Publisher Coalition" ' Nate follow-up

**For AI Companies:**

- "See Attribution Intelligence" ' **encypherai.com/ai-demo**
- "Infrastructure Partnership" ' Collaborative discussion
- "Technical Integration Guide" ' Standards collaboration

### Comparison Points:

Every interaction highlights:

1. Unmarked text has no proof (baseline problem)
2. Basic C2PA provides document-level proof (compliance)
3. Enterprise adds sentence-level capabilities (competitive advantage)
4. Why this matters: formal notice, licensing, intelligence

---

## 11\. Success Metrics

### Engagement Metrics:

- Time in sandbox: \>5 minutes average
- Features tested: 3+ per session
- Copy-paste test performed: 60% of sessions
- Comparison viewed: 80% of sessions

### Conversion Metrics:

- Demo requests: 10% of sandbox users
- API key signups: 30% of sessions
- Enterprise trials: 5% of users
- Sales qualified leads: 20 monthly

---

## 12\. Key Messages Throughout Sandbox

**Opening:** "Text on the open web has no cryptographic proof of origin. As Co-Chair of the C2PA Text Provenance Task Force, we're changing that--building standards with Google, BBC, OpenAI, Adobe, and Microsoft."

**Comparison:** "See the difference between unmarked text (no proof), basic C2PA (document proof), and our patent-pending enhancements (sentence-level proof that enables licensing)."

**Call to Action:** "Ready to implement? Try our reference implementation or explore enterprise capabilities."

**Links:**

- Publishers: **encypherai.com/publisher-demo**
- AI Companies: **encypherai.com/ai-demo**
- Enterprises: **encypherai.com/enterprise**

---

## Conclusion

This sandbox demonstrates the fundamental shift from unmarked text to cryptographically watermarked text, showing how C2PA provides baseline proof while our patent-pending enhancements enable formal notice, licensing infrastructure, and performance intelligence.

The sandbox proves: **Unmarked text has no proof. C2PA provides proof. Our enhancements enable business value.**

---

## Document Control

**Last Updated:** October 31, 2025
**Status:** Post-Customer Discovery Update
**Distribution:** Product & Engineering Teams
**Next Review:** January 2026
**Document Owner:** Chief Product Officer

**Key Updates:**

- ... Removed AI detection comparisons
- ... Added C2PA standards authority messaging
- ... Emphasized unmarked ' marked transformation
- ... Updated website to encypherai.com with demo paths
- ... Added collaborative framing for AI companies
- ... Focused on cryptographic proof vs. no proof
- ... Added real-time streaming capabilities (WebSocket/SSE)
- ... Added minimal invisible embeddings feature
- ... Added public verification API (no auth required)
- ... Updated technical implementation to match production API

