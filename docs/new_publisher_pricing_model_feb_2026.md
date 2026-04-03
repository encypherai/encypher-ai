# Encypher Publisher Pricing & Feature Schema

**Version 1.2 | February 2026 | Confidential**

---

## Pricing Philosophy

Every signed document strengthens the coalition. Every publisher in the network increases leverage for all members. We don't charge for signing because signing is the supply that makes the marketplace valuable. We charge for the tools that extract value from the network — enforcement, evidence, analytics, and identity.

**Model:** Free infrastructure → Paid enforcement tools → Licensing revenue share

---

## Two-Track Licensing Model

All licensing revenue — regardless of tier — follows one of two tracks:

**Coalition Deals (60/40):** Encypher negotiates licensing deals on behalf of the coalition. We do the work — formal notice, evidence, negotiation. Publishers get 60%, Encypher takes 40%. This is revenue that wouldn't exist without the infrastructure and collective leverage.

**Self-Service Deals (80/20):** Publishers use our signing tech, formal notice tools, and evidence packages to negotiate their own deals directly with AI companies. They do the work — they keep more. Publisher gets 80%, Encypher takes 20%.

Both tracks available to all tiers. Choose per deal. Use coalition for some AI companies and self-service for others. The split reflects who does the work.

---

## Free Tier — Full Signing Infrastructure

### The Principle

Signing content is free because every signed document makes the coalition more valuable. We don't monetize supply — we monetize the enforcement and licensing tools that the network enables.

### Signing & Provenance

- ✅ C2PA 2.3-compliant document signing (Section A.7)
- ✅ Sentence-level Merkle tree authentication (patent-pending ENC0100)
- ✅ Invisible Unicode embeddings — survive copy-paste, B2B distribution, scraping
- ✅ Public verification pages with shareable URLs for every signed document
- ✅ Public verification API — anyone can verify signed content, no auth required
- ✅ Tamper detection — know if signed content has been modified
- ✅ Custom metadata (author, publisher, license, tags)

### Distribution & Tools

- ✅ WordPress plugin — auto-sign on publish, verification badge, one-click install
- ✅ REST API with Python SDK (Node.js, Go, Ruby planned)
- ✅ CLI tool for local signing (`encypher sign article.md`)
- ✅ GitHub Action for CI/CD integration (auto-sign on commit)
- ✅ Browser extension for verification

### Coalition Membership

- ✅ Auto-enrolled in Encypher Coalition on first signed document
- ✅ Content indexed for coalition licensing negotiations
- ✅ Basic attribution view — see where your signed content appears in AI outputs
- ✅ Coalition dashboard with content stats and corpus contribution

### Licensing Revenue

- ✅ Coalition deals: 60% to publisher / 40% to Encypher
- ✅ Self-service deals: 80% to publisher / 20% to Encypher
- ✅ No licensing revenue = no payment to Encypher

### Usage Limits

| Resource | Free Limit | Overage |
|----------|-----------|---------|
| New documents signed | 1,000/month | $0.02/doc |
| Verification requests | Unlimited | — |
| Public API lookups | Unlimited | — |
| Sentence-level tracking | Included with signing | — |
| Invisible embeddings | Included with signing | — |
| Coalition membership | Included | — |

### Who This Is For

Individual bloggers and creators, small to mid-size publishers, independent media, academic researchers, content marketing teams, WordPress site owners — anyone who creates text content and wants provenance protection. No procurement process. No sales call. Sign up, get API key, start signing.

> **NMA Members:** All NMA member publishers receive Free tier with full features immediately. No application required. The more publishers signing content, the stronger every member's licensing position.

---

## Freemium Add-Ons — Self-Service, No Sales Call Required

Every add-on can be purchased with a credit card directly from the dashboard. No procurement process, no contract negotiation. Buy what you need, when you need it. Cancel monthly add-ons anytime.

### Enforcement Add-Ons (Revenue Pipeline)

These three tools form the enforcement pipeline: find where your content appears → notify the companies → build the evidence for licensing or litigation.

#### Attribution Analytics — $299/month

Full dashboard showing where your signed content appears in AI outputs. Usage patterns, frequency, context analysis. This is the intelligence layer that makes everything else rational — without knowing which AI companies are using your content, you're guessing at who to target.

- Where your signed content appears in AI model outputs
- Which AI companies are using your content and how frequently
- Usage context — training, grounding, retrieval, direct reproduction
- Trend data over time
- Export targeting lists for formal notice campaigns
- Less than a single hour of outside counsel — pays for itself on the first notice it informs

#### Formal Notice Package — $499/notice

Cryptographically-backed formal notice to a specific AI company establishing that your content is marked, owned, and verifiable. Triggers the willful infringement framework — after notice, continued unauthorized use transforms from "we didn't know" to "you knew and ignored it."

Each notice includes:
- Formal notification letter with cryptographic evidence citations
- Verification API access instructions for the recipient
- Documentation of marked content in their training pipeline
- Chain-of-custody record for the notification itself
- Delivery confirmation and timestamped proof of receipt

**What this replaces:** Outside counsel drafting bespoke notices at $800–1,500/hour. Multiple hours per notice. Our $499 package produces a cryptographically-backed notice that strengthens a willful infringement argument at 90%+ cost reduction.

**Volume pricing:**

| Quantity | Per Notice | Savings |
|----------|-----------|---------|
| 1 | $499 | — |
| 5-pack | $399/each ($1,995) | 20% off |
| 10-pack | $349/each ($3,490) | 30% off |
| 20-pack | $299/each ($5,980) | 40% off |

#### Evidence Package — $999/package

Court-ready evidence bundle for a specific infringement claim. Designed for litigation leverage or licensing negotiation — the goal is a package your outside counsel is comfortable submitting.

Each package includes:
- Merkle tree proofs establishing sentence-level provenance
- Chain-of-custody documentation from signing through detection
- Tamper-evident manifest records
- Formal notice delivery records (if notice was previously sent)
- Timeline reconstruction — when content was signed, when it appeared in AI output, when notice was served
- Cryptographic verification instructions for opposing counsel or court
- Export in standard litigation support formats

**What this replaces:** $15–30K in associate time and forensic vendor fees to build a comparable evidence bundle. At $999, a publisher can buy one speculatively to have litigation counsel evaluate the format.

**Volume pricing:**

| Quantity | Per Package | Savings |
|----------|-----------|---------|
| 1 | $999 | — |
| 3-pack | $849/each ($2,547) | 15% off |
| 5-pack | $749/each ($3,745) | 25% off |

---

### Enforcement Bundle — $999/month

The "I want to start licensing" package. One subscription that covers the full enforcement pipeline.

**Includes:**
- Attribution Analytics (find where your content appears)
- 2 Formal Notices per month (create liability)
- 1 Evidence Package per month (close the deal)

**Value vs. à la carte:** Analytics ($299) + 2 notices ($998) + 1 evidence package ($999) = $2,296/month. Bundle price: $999/month. **57% savings.**

**Who it's for:** Publishers ready to move from "our content is signed" to "we're actively licensing." This bundle provides the targeting intelligence, the legal notices, and the evidentiary foundation to start generating licensing revenue.

> Additional notices and evidence packages beyond the monthly allocation are available at standard à la carte pricing.

---

### Infrastructure Add-Ons

#### Custom Signing Identity — $499/month

Sign content as your brand ("Associated Press") instead of "Encypher Coalition Member." Your name and logo on every verification page. Custom publisher badge. Professional presentation when AI companies or third parties verify your content.

#### White-Label Verification — $299/month

Verification pages hosted on your domain with your branding. Custom URL (verify.yourpublisher.com). Remove Encypher branding from all public-facing verification. Requires Custom Signing Identity.

#### Custom Verification Domain — $29/month

Point a custom domain to your verification pages without full white-label. Quick DNS setup, no development required. Encypher branding remains.

#### BYOK (Bring Your Own Keys) — $499/month

Use your organization's existing PKI infrastructure and signing certificates. Required by some enterprise security policies. Validated against C2PA trust list.

---

### Operations Add-Ons

#### Bulk Archive Backfill — $0.01/document

One-time batch signing of existing content archives. Sign 5 years of articles in one operation. Priced per document, billed once. No monthly commitment.

| Archive Size | Cost | Example |
|-------------|------|---------|
| 10,000 docs | $100 | Small publisher back-catalog |
| 100,000 docs | $1,000 | Mid-size publisher archive |
| 1,000,000 docs | $10,000 | Major publisher full archive |

#### Data Export (Full) — $49/export

Full export of all attribution and analytics data as CSV/JSON. Free tier basic view included. Full export for licensing negotiations and internal analysis.

#### Priority Support — $199/month

Email support with 4-hour response SLA during business hours. Dedicated onboarding assistance. Priority bug fixes.

---

### Bundle Summary

| Bundle | Monthly Price | Includes | Savings vs. À La Carte |
|--------|-------------|----------|----------------------|
| **Enforcement Bundle** | $999/mo | Attribution Analytics + 2 Notices/mo + 1 Evidence Package/mo | 57% |
| **Publisher Identity** | $749/mo | Custom Signing Identity + White-Label Verification + Custom Domain | 7% |
| **Full Stack** | $1,699/mo | Enforcement Bundle + Publisher Identity | 51% |

---

## Enterprise Tier — Publishing Industry

### For Major Publishers With Significant Licensing Potential

Enterprise is a relationship, not a subscription. Custom pricing reflects content volume, licensing potential, and coalition role. Everything in Free + all add-ons included at no additional charge, plus exclusive capabilities.

### Everything in Free Tier — Unlimited

- ✅ Unlimited document signing (no monthly cap)
- ✅ Unlimited sentence-level Merkle tree authentication
- ✅ Unlimited invisible embeddings
- ✅ Unlimited verification and public API

### All Add-Ons Included — No Additional Charge

- ✅ Attribution Analytics — full dashboard, unlimited
- ✅ Formal Notice Generation — unlimited
- ✅ Evidence Package Generation — unlimited
- ✅ Custom Signing Identity — your brand on everything
- ✅ White-Label Verification — your domain
- ✅ Bulk Archive Backfill — unlimited
- ✅ BYOK / Custom Certificates
- ✅ Full Data Export — unlimited
- ✅ Priority Support — included

### Enterprise-Exclusive Capabilities

**Signing & Provenance**
- Streaming LLM signing (WebSocket/SSE — sign AI-generated content in real time)
- OpenAI-compatible `/chat/completions` endpoint with automatic signing
- Custom C2PA assertions and schema registry
- C2PA provenance chain — full edit history tracking
- Batch operations (100+ documents per request)
- Document revocation capability (StatusList2021)

**Advanced Attribution & Detection**
- Robust fingerprinting — survives paraphrasing, rewriting, and translation
- Multi-source attribution with authority ranking
- Fuzzy fingerprint matching for misquotes and lightly edited reuse
- Plagiarism detection with Merkle proof linkage

**Operations & Security**
- Dedicated SLA — 99.9% uptime guarantee, 15-minute incident response
- 24/7 priority support with named account manager
- SSO integration (SAML, OAuth)
- Team management with role-based access controls
- Webhooks for signing, verification, and attribution events
- Full audit trail for compliance

**Coalition & Licensing**
- Same 60/40 (coalition) and 80/20 (self-service) licensing splits
- Priority coalition positioning in licensing negotiations
- Advisory board participation
- Syracuse Symposium seat — define market licensing frameworks

### Enterprise Pricing Framework

| | Tier 1 Publisher | Tier 2 Publisher | Tier 3 Publisher |
|---|---|---|---|
| **Licensing Potential** | >$20M | $3–20M | <$3M |
| **Implementation Fee** | $30K | $20K | $10K |
| **Coalition Licensing** | 60/40 | 60/40 | 60/40 |
| **Self-Service Licensing** | 80/20 | 80/20 | 80/20 |
| **Syracuse Symposium** | ✅ Included | ✅ Included | Advisory only |
| **Advisory Board** | ✅ Included | Optional | — |
| **Dedicated Account Mgr** | ✅ Named | ✅ Named | Shared |
| **Implementation Timeline** | 2–4 weeks | 2–4 weeks | 1–2 weeks |

### Founding Coalition — First 20 Publishers

- Implementation fee waived
- Same 60/40 and 80/20 licensing splits
- Syracuse Symposium seat — define market licensing frameworks
- Advisory board participation
- Priority coalition positioning in all licensing negotiations

---

## Enforcement Pipeline — How It Works Together

```
STEP 1: SIGN (Free)
├── Content signed with C2PA + sentence-level Merkle trees
├── Invisible embeddings survive copy-paste and distribution
└── Content auto-indexed in coalition

STEP 2: DETECT (Attribution Analytics — $299/mo or Enterprise)
├── Dashboard shows where signed content appears in AI outputs
├── Identifies which AI companies to target
└── Provides targeting intelligence for notices

STEP 3: NOTIFY (Formal Notice — $499/notice or Enterprise)
├── Cryptographically-backed notice served to AI company
├── Establishes "you knew" — kills "we didn't know" defense
└── Triggers willful infringement framework (3x damages)

STEP 4: PROVE (Evidence Package — $999/pkg or Enterprise)
├── Court-ready Merkle proofs and chain-of-custody
├── Formal notice delivery records
└── Litigation leverage or licensing negotiation support

STEP 5: LICENSE (60/40 coalition or 80/20 self-service)
├── Coalition: Encypher negotiates, publisher gets 60%
├── Self-service: Publisher negotiates, keeps 80%
└── No revenue = no payment to Encypher
```

---

## Worked Examples

### Mid-Size Publisher (~$10M/year) — Self-Service Track

1. Signs content on Free tier (no cost)
2. Adds Attribution Analytics ($299/mo) to identify which AI companies use their content
3. Buys a 5-pack of Formal Notices ($1,995) to notify the top 5 AI companies
4. Buys 1 Evidence Package ($999) for the highest-value target
5. Negotiates a $2M licensing deal directly

**Publisher keeps $1.6M (80%).** Encypher receives $400K (20%).
Total enforcement spend: ~$3,300 + $299/mo. Net new revenue: ~$1.595M.

### Major Wire Service — Coalition Track

1. Enterprise tier — unlimited signing, all tools included
2. Encypher identifies widespread content usage across 8 AI companies
3. Encypher serves formal notices, builds evidence packages, leads negotiation
4. Coalition negotiates $15M deal; wire service's attributed share: $5M

**Publisher keeps $3M (60%).** Encypher receives $2M (40%).
Publisher effort: zero deal negotiation. Encypher handles everything.

### Regional News Publisher (~$2M/year) — Enforcement Bundle

1. Signs content on Free tier (no cost)
2. Subscribes to Enforcement Bundle ($999/mo)
3. Attribution Analytics reveals content appearing in 3 AI company outputs
4. Sends formal notices with monthly allocation
5. Uses evidence package to support $300K licensing deal (self-service)

**Publisher keeps $240K (80%).** Encypher receives $60K (20%).
Annual enforcement spend: ~$12K. Net new revenue: $228K.

---

## Summary

| Layer | What It Includes | Revenue Model |
|-------|-----------------|---------------|
| **Free Infrastructure** | Full signing, verification, embeddings, coalition membership, WordPress plugin, API, CLI | No charge — builds coalition supply |
| **Freemium Add-Ons** | Attribution analytics, formal notices, evidence packages, identity, white-label, backfill | Self-service credit card purchases |
| **Enforcement Bundle** | Analytics + notices + evidence in one subscription | $999/month |
| **Enterprise** | Unlimited everything + exclusive capabilities + dedicated support | Custom implementation fee |
| **Licensing Revenue** | Coalition (60/40) or self-service (80/20) | Success-based — no revenue = no payment |

**Free to sign. Paid to enforce. Aligned on outcomes.**

---

*encypher.com | C2PA Text Provenance Standard — Section A.7 — Published January 8, 2026*
