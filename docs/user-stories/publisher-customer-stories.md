# Publisher Customer Stories — Small, Midsized & Large Org Lifecycles

**Session date**: 2026-02-21
**Context**: Strategy ↔ codebase gap closure (TEAM_216). These stories describe the realistic
lifecycle of a publishing organization from first contact through mature platform usage.
They should inform product, sales, and marketing decisions about where to invest next.

---

## Persona 1 — Small Publisher: Independent Newsletter

**Profile**: Maya runs *The Carbon Brief*, an independent climate newsletter with 8,000 subscribers.
Solo operation, Substack + Ghost hybrid. No engineering staff. Monthly revenue: ~$4,000 (subscriptions + sponsorships).

**Problem**: She noticed her deep-dive articles appearing verbatim in AI chatbot responses without
attribution or her newsletter link. She can't afford a lawyer but feels violated and undercut.

---

### Phase 1 — Discovery (Month 0)

Maya finds Encypher through a tweet from another newsletter writer who says *"I can now prove
AI companies are stealing my work."* She lands on the marketing site `/rights-management` page.

The three-tier licensing model (Bronze/Silver/Gold) immediately makes sense to her as a
non-technical person — it maps to how she already thinks about her content:
- Indexing to find her work: fine
- Using her analysis in AI-generated answers without attribution: not fine
- Training a model on her body of work: absolutely requires a license

She signs up for the free tier. **No credit card required.**

---

### Phase 2 — First Signing (Month 0, Day 3)

Maya installs the Ghost webhook integration (takes 20 minutes following the CMS integration guide).
She publishes her next article and clicks "Sign with Encypher" in the Ghost admin panel.

The signed article now has invisible Unicode embeddings and a C2PA assertion. She pastes
the article text into the playground's **Copy-Paste Survival Tester**:

1. Article text → Sign → copy to clipboard
2. Pastes into the tester's second textarea → "Verify survival"
3. Result: ✅ **Watermark survived** — *"Provenance embeddings intact across clipboard copy."*

This is her "aha moment." She realizes the watermark survives the exact thing AI companies
do when they ingest her content — copy-paste from the web.

---

### Phase 3 — Rights Profile Setup (Month 0, Day 5)

Maya visits Rights → Profile tab. She applies the **"Newsletter/Blog Default"** template:
- Bronze (crawling): Permitted
- Silver (RAG): Permitted — **attribution required** (must link to original article)
- Gold (training): **License required** — not available without negotiation

Every article she publishes from now on embeds her `rights_resolution_url`. Any AI system
checking C2PA provenance finds her terms immediately, machine-readable.

She adds her newsletter's `robots.txt` additions to her Ghost theme:
```
User-agent: GPTBot
Disallow: /
X-Robots-Tag: noai
```

This is belt-and-suspenders: the C2PA embedding is the cryptographic proof; the robots.txt
is the explicit opt-out signal.

---

### Phase 4 — Attribution Analytics Upgrade (Month 3)

Three months in, Maya notices her analytics dashboard shows increasing API hits to her
`rights_resolution_url`. AI crawlers are checking her terms. She upgrades to
**Attribution Analytics ($299/mo)** to see:
- Which AI operators are checking her terms
- Detection frequency by day/week
- How many times her content was served vs acknowledged

She discovers GPTBot checked her rights profile 847 times last month. Most checks are
Bronze-tier (indexing) — consistent. But two checks at Gold-tier (training) came back
with no license record. Something is off.

---

### Phase 5 — Formal Notice (Month 5)

Maya uses attribution analytics to identify that an AI company ingested several of her
Gold-tier articles without a license. She creates a formal notice:

**Rights → Notices → + New notice**
- Recipient: the AI company
- Violation type: Unauthorized Training
- Notice text: detailed account of which articles, dates, evidence

She delivers the notice. From this point, any continued use of her content is **willful**
infringement — not accidental. The legal threshold for damages just increased significantly.

The **Evidence Package** (downloadable JSON) contains:
- SHA-256 hash of the notice content
- Chain-of-custody linked list
- Delivery timestamp
- Cryptographic proof linking the notice to her signed articles

She forwards this to a media law clinic at a local university. They confirm it constitutes
a valid cease-and-desist notice with verifiable provenance. They can advise on collective
action if other newsletter writers have similar evidence.

---

### Phase 6 — Coalition Join (Month 8)

The Encypher coalition team reaches out. With her volume of signed content and established
rights profile, Maya is eligible for the **Publisher Coalition**. She joins:
- Her Gold-tier terms are listed in the coalition's licensing catalog
- AI companies can license her work as part of a bulk coalition deal
- Revenue split: **60% to Maya, 40% to Encypher** (for infrastructure + legal overhead)

First quarter payment: $340 for licensing of her archive to a research AI company.
Not transformative revenue, but meaningful for a solo creator — and it required no
additional work after the initial rights profile setup.

---

### Lifetime Value Trajectory

| Month | Plan | MRR to Encypher | Maya's Position |
|-------|------|-----------------|-----------------|
| 0 | Free | $0 | Just watermarking |
| 3 | Attribution Analytics | $299 | Monitoring crawlers |
| 5 | + Formal Notice ($499) | one-time | Legal protection active |
| 8 | Coalition member | revenue share | Passive licensing income |

**Key insight**: Maya converted from free to paid because she saw crawlers checking her
rights endpoint. The data made the upgrade decision obvious. The "show me who's watching"
moment is the free-to-paid conversion lever for small publishers.

---
---

## Persona 2 — Midsized Publisher: Regional News Organization

**Profile**: *Pacific Standard News*, 85-person newsroom in San Francisco. Digital-native
regional paper. 200k monthly readers, paywall on premium content. CTO-equivalent: Alex Torres.
Annual revenue: $8M.

**Problem**: Multiple AI companies have ingested their investigative journalism archive. The
editorial team is frustrated that their expensive original reporting trains AI models that
then compete with them by synthesizing answers that duplicate their work. They want both
protection and a new revenue stream — their archive is their most valuable asset.

---

### Phase 1 — Technical Evaluation (Month 0)

Alex runs a technical proof-of-concept:

1. Hits the public API directly to sign a sample article
2. Verifies the response contains a valid C2PA manifest
3. Pastes the signed text into the playground copy-paste tester — watermark survives
4. Reads the BYOK docs — confirms they can use their own Ed25519 keys eventually
5. Checks the OpenAPI spec — it's clean, versioned, production-grade

He signs up for the **Growth plan** and pitches it to the editor-in-chief as
*"making our content legally protected from AI scraping for less than one hour of
a junior reporter's time per month."*

---

### Phase 2 — CMS Integration (Month 1)

Alex integrates the Encypher webhook with their Ghost Enterprise installation.
All new articles are automatically signed on publish. No manual steps for editorial staff.

He also runs a **historical signing job** via the API to sign the last 3 years of archive
content (4,200 articles). Batch API call using the Python SDK:

```python
from encypher import EncypherClient
client = EncypherClient(api_key=os.environ["ENCYPHER_API_KEY"])

for article in db.get_all_articles():
    result = client.sign(
        content=article.body_text,
        metadata={
            "title": article.title,
            "author": article.author,
            "published_at": article.published_at.isoformat(),
            "url": article.canonical_url,
        }
    )
    db.update_article(article.id, signed_content=result.signed_text)
```

4,200 articles signed overnight. The entire editorial archive is now provenance-protected.

---

### Phase 3 — Rights Profile (Month 1)

Alex sets a custom rights profile aligned with Pacific Standard News's editorial policy:

- **Bronze**: Permitted (search indexing fine)
- **Silver**: Permitted **only with attribution** — must include author name + canonical URL
- **Gold**: **License required** — rate negotiable, contact licensing@pacificstandard.com

He adds their `rights_resolution_url` to their existing content licensing FAQ page so
any AI company that manually checks their policies gets the same answer as one that
checks programmatically.

---

### Phase 4 — Incoming Licensing Requests (Month 3)

Two AI companies discover Pacific Standard News's rights profile via C2PA provenance
data and submit Gold-tier licensing requests through the platform.

Alex reviews them in **Rights → Licensing**:

**Request 1**: A smaller AI search company wants Silver access for their RAG pipeline.
Terms look fair. Alex approves. Agreement created — both parties have a cryptographic record.

**Request 2**: A major foundation model company wants Gold training access.
Alex forwards this to the editor-in-chief and their media lawyer. They counter-propose
a higher rate via email. The company accepts. Alex updates the agreement in the platform.

**Revenue from licensing in Month 3**: $12,000 from the Gold license.

This is new revenue that didn't exist six months ago, requires no ongoing work from
editorial, and is directly attributable to the archive signing job they ran in Month 1.

---

### Phase 5 — Formal Notice Campaign (Month 6)

Attribution analytics reveal that a third major AI company has been checking Pacific
Standard News content at Gold-tier rates without any license on file. Detection frequency
suggests systematic ingestion.

Alex and their lawyer issue formal notices via the platform:
- Three notices for three distinct content batches (organized by date range)
- Each notice delivered and cryptographically locked
- Evidence packages exported as JSON for the legal team

The notices are forwarded to the AI company's legal counsel. Within 60 days, the company
initiates license negotiations. Final outcome: a $45,000/year training license.

**The formal notice didn't just protect them — it started a revenue conversation.**

---

### Phase 6 — Quote Integrity for Editorial (Month 9)

Pacific Standard's editorial team starts using the **Quote Integrity** feature in a new way:
when they're editing stories that include AI-assisted research, they run suspect quotes
through `POST /api/v1/verify/quote-integrity` to check if the AI hallucinated a citation.

The workflow:
1. Reporter AI-assisted draft includes: *"According to Stanford's 2024 Climate Report..."*
2. Editor submits the quoted text + attribution to Quote Integrity endpoint
3. Response: verdict `hallucinated`, similarity `0.12` — the Stanford report doesn't
   contain this language. The reporter's AI model fabricated it.

This prevents publishing AI-generated hallucinations as facts. It becomes a standard
pre-publication check. The editorial team considers it their most practical use of the
platform — internal quality control, not just external protection.

---

### Lifetime Value Trajectory

| Phase | Product | Annual Encypher Revenue |
|-------|---------|------------------------|
| Month 1-2 | Growth plan | $1,188 |
| Month 3 | + Attribution Analytics | +$3,588/yr |
| Month 6+ | Enforcement bundle | +$11,988/yr |
| Month 9 | Licensing revenue (60/40 split) | variable |
| **Total ARR potential** | | **~$20k+ platform fees** |

**Key insight**: The archive signing job in Month 1 created the asset base that generated
$57k in direct licensing revenue by Month 6. ROI was clear to both Alex and finance.
The upgrade path from Growth → Attribution Analytics → Enforcement was driven by data,
not sales pressure.

---
---

## Persona 3 — Large Publisher: Major Media Company

**Profile**: *Continental Media Group*, 1,200-person global newsroom. Operates 8 regional
mastheads, a wire service, and a syndication arm. Engineering team: 35 people.
Annual revenue: $180M. Head of Platform Engineering: Jordan Kim.

**Problem**: CMG has been in conversations with three major AI companies simultaneously
about content licensing deals. Their legal team wants cryptographic proof of when content
was published, who authored it, and exactly what was ingested — to negotiate from a position
of verifiable evidence rather than contested claims. They also need to ensure their
existing PKI/certificate infrastructure is respected.

---

### Phase 1 — Enterprise Evaluation (Month 0)

CMG's legal and engineering teams evaluate Encypher over 30 days:

- **Legal**: Reviews C2PA 2.3 spec compliance, W3C ODRL support, RSL 1.0 compatibility
- **Engineering**: Reviews API design, OpenAPI spec, Python SDK, TypeScript SDK
- **Security**: Reviews BYOK (Bring Your Own Key) capability — CMG won't store signing keys
  with a third party

Jordan's team POCs BYOK:
```python
# Register their org's Ed25519 public key
client.byok.register_public_key(
    public_key=cmg_pub_key_pem,
    key_id="cmg-prod-signing-key-v1",
    valid_from="2026-01-01T00:00:00Z",
)
# All signing from now on uses CMG's own key
result = client.sign(content=article_text, key_id="cmg-prod-signing-key-v1")
```

The C2PA assertion embeds CMG's own certificate. Independent verifiers can check
the signature against CMG's public key without trusting Encypher at all. This is
the **full key custody** model Jordan's security team required.

---

### Phase 2 — Enterprise Agreement & Custom Integration (Month 1-2)

CMG signs an enterprise agreement (custom pricing, SLA, dedicated support).

Jordan's team builds a custom signing pipeline:
1. Article published in CMG's internal CMS → event fired to Kafka topic
2. Custom consumer reads from Kafka → signs article via Encypher API → stores signed version
3. Signed version distributed to all 8 mastheads simultaneously
4. Archive job runs overnight to backfill 15 years of content (2.1M articles)

The backfill takes 6 days running at 5 req/s (enterprise rate limit is higher than growth tier).
By Day 45, CMG's entire publishable archive has C2PA provenance chains.

---

### Phase 3 — Rights Profiles Per Masthead (Month 2)

CMG doesn't want a single rights profile — each masthead has different policies:

- *The Continental* (flagship): Gold requires board approval
- *Pacific Wire* (wire service): Silver permitted for syndication AI, Gold requires license
- *Local Voices* (community news): Bronze and Silver permitted, Gold restricted
- *Sports Central*: All tiers permitted with license, sports data = high demand

Jordan's team sets a **custom rights profile per `org_id`** for each masthead.
The platform supports multiple `org_id`s under one enterprise account.

AI companies checking provenance of content from any CMG masthead get the correct
rights terms for that specific publication — not a one-size-fits-all response.

---

### Phase 4 — Coalition as Revenue Program (Month 4)

CMG joins the **Publisher Coalition** as a Founding Partner. Their archive is
listed in the coalition catalog with per-masthead terms.

Three AI companies license access to the full CMG coalition catalog (all 8 mastheads):
- Company A: $800k/year for Silver tier (RAG across all mastheads)
- Company B: $1.2M/year for Gold tier (training on Continental + Pacific Wire)
- Company C: Negotiating

CMG's 60% share of coalition revenue: $1.2M/year from Companies A and B alone.

Jordan's team builds a **revenue dashboard** that pulls from the Encypher licensing API
and displays per-masthead attribution to their finance team. The CFO now cites Encypher
licensing revenue in quarterly earnings calls.

---

### Phase 5 — Formal Notice at Scale (Month 6)

CMG's legal team uses attribution analytics to identify five AI companies that appear
to be ingesting Gold-tier content without licenses. They issue formal notices as a batch:

- 5 notices issued via API (automated, not manual UI clicks)
- Each notice references the specific articles, date ranges, and evidence of ingestion
- Evidence packages exported and filed with CMG's legal team

Within 90 days:
- 2 companies open license negotiations → become paying licensees
- 2 companies cease ingestion (confirmed via analytics — no more Gold-tier detection events)
- 1 company disputes → CMG's lawyers submit the evidence package → case ongoing

The evidence package from the Encypher platform includes Merkle proofs linking
the signed articles to their original publication dates. CMG's lawyers note this is
stronger evidence than anything they could have assembled from server logs alone —
because the cryptographic proof is embedded in the content itself, not dependent on
CMG's own infrastructure being trusted.

---

### Phase 6 — Quote Integrity as Product Feature (Month 9)

CMG's product team launches a **"Verified Facts" badge** on their website. When a
reporter cites an external source, the editorial platform runs a Quote Integrity check:

1. Reporter writes: *"Citing IMF data showing 3.2% global growth in 2025..."*
2. System submits quote to Encypher's Quote Integrity endpoint with `org_id` targeting IMF-signed documents
3. Response: verdict `accurate`, similarity `0.97` — the quote matches a signed IMF document
4. Article gets a "Fact verified via C2PA provenance" badge

For quotes from signed Encypher content (including other CMG mastheads), the verification
is instant and cryptographic. For non-C2PA sources, it falls back to fuzzy search.

CMG pitches this as a **trust differentiator** in their subscription renewal campaigns:
*"Our journalism is verified. Every fact, every quote, cryptographically traceable."*

---

### Phase 7 — Streaming AI Integration (Month 12)

CMG launches an AI-assisted research product internally. Reporters use a Claude-powered
research assistant that synthesizes background from CMG's archive. Every AI-generated
output is signed at generation time using streaming LLM signing:

```python
# Sign AI-generated summaries as they stream
with client.sign_stream() as stream:
    for chunk in claude_client.messages.stream(...):
        stream.write_chunk(chunk.text)
    signed_output = stream.finalize()
```

This means even AI-synthesized summaries of CMG's archive carry C2PA provenance:
*"This summary was generated by CMG's research assistant on Feb 21, 2026, sourced
from signed CMG articles [list of article IDs]."*

AI outputs become as auditable as the original journalism.

---

### Lifetime Value Trajectory

| Phase | Product | Annual Value |
|-------|---------|-------------|
| Month 1 | Enterprise plan (custom) | $120k ARR to Encypher |
| Month 4 | Coalition licensing (60/40) | $1.2M CMG revenue; $800k Encypher |
| Month 6 | Formal notices → conversions | $2M+ additional license revenue |
| Month 12 | Full platform (streaming, BYOK, analytics) | Renewal + expansion |

**Key insight**: CMG's ROI from coalition licensing alone ($1.2M/year) dwarfs their
platform cost. The Encypher relationship moves from "software vendor" to "infrastructure
partner enabling a new revenue line." Jordan Kim presents Encypher to the CMG board as
a strategic asset, not an operational expense.

---

## Cross-Persona Patterns

| Pattern | Small (Maya) | Midsized (Alex) | Large (CMG) |
|---------|-------------|-----------------|-------------|
| Entry trigger | AI stealing content, no recourse | Competitive threat, lost revenue | Enterprise licensing negotiation |
| First value | Copy-paste survival "aha moment" | Archive signing = legal asset | BYOK + cryptographic evidence |
| Free-to-paid trigger | Seeing crawlers in analytics | Direct licensing revenue | Enterprise deal from Day 1 |
| Best growth lever | Coalition passive income | Evidence package → license negotiation | Coalition as revenue program |
| Unexpected use case | Media law clinic referral | Quote integrity for editorial QA | Verified Facts product badge |
| Long-term stickiness | Rights profile = their standard | Integration = editorial workflow | Infrastructure = business model |

---

## What These Stories Tell Us About Product Investment

1. **The copy-paste survival tester is the conversion moment for small publishers** — it
   makes invisible infrastructure tangible. It must always work perfectly.

2. **The archive signing job is the midsized publisher wedge** — it creates the asset
   that generates downstream licensing revenue. API ergonomics for bulk operations matter.

3. **BYOK is a hard requirement for large publishers** — it's not a nice-to-have. Any
   enterprise publisher with an existing PKI won't sign a deal without it.

4. **Quote Integrity found unexpected adoption as editorial QA** — the original pitch
   was "detect AI hallucinations about your content." The actual use case emerged as
   "detect AI hallucinations in our own AI-assisted drafts." Design for both.

5. **Formal notice → license negotiation is the most common conversion path** at
   midsized and large scale. The evidence package needs to be court-credible.
   Invest in its format and completeness.
