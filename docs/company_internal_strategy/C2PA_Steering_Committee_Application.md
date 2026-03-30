# C2PA Steering Committee Application
## Working Draft -- Encypher Corporation

**Last Updated:** March 29, 2026
**Status:** Draft -- Awaiting Track 3 Fact Confirmations
**Owner:** Erik Svilich
**Distribution:** Executive Only

> **IMPORTANT:** This is a working draft. Brackets [ ] indicate facts that require
> confirmation before submission. Do not submit until all brackets are resolved.
> The questionnaire says "brevity and concise answers are appreciated." Honor that.
> Every answer should be under 200 words unless the evidence demands more.

---

## Pre-Submission Checklist

- [x] Resolve Eddan Katz engagement status: fractional/part-time; SC seat triggers part-time hire with path to dedicated C2PA + gov't/regulatory role
- [x] Resolve Madhav Chinnappa engagement status: strategic advisor; participates in capacity available, not weekly commitment
- [x] Confirm Erik's current weekly C2PA hours: 1-3 meetings/week (task force + working groups)
- [ ] Confirm WordPress 7.0 inclusion status (LOI, confirmed, or "PR submitted and under review")
- [ ] Confirm Prebid implementation status (formal commitment, evaluation, or "in discussion")
- [ ] Confirm Freestar/PubOS partnership status (signed, in legal review, or "in discussion")
- [ ] Confirm NPR evaluation status (SC reference ask sent 2026-03-30; awaiting Erica's confirmation)
- [ ] Confirm SPUR collaboration characterization (partnership, collaboration, or "engaged")
- [ ] Confirm conformance program timeline (expected completion date for implementation review)
- [ ] Count consecutive weeks of C2PA meeting attendance (specific number for Q3/Q11)
- [ ] Madhav: identify Google SC representatives and assess personal relationship
- [ ] Eddan: identify Meta SC representatives and assess personal relationship
- [ ] Charlie Hartford: inform of SC application, request informal internal advocacy at BBC

---

## Company Information

**Legal entity name:** Encypher Corporation

**Industry served:** Content provenance infrastructure (publishing, media, AI)

**Headquarters location:** [Confirm city, state]

**Primary contact:** Erik Svilich, Founder & CEO, [email]

**Secondary technical contact:** [Confirm -- Erik or another team member]

**Brief organizational overview (150 words):**

Encypher Corporation builds content provenance infrastructure on the C2PA standard.
Erik Svilich, Encypher's founder, authored Section A.7 of C2PA 2.3, the text
provenance specification published January 8, 2026, and co-chairs the C2PA Text
Provenance Task Force. The company built the production reference implementation
of that specification: an enterprise signing API covering 31 MIME types across text,
images, audio, video, documents, and fonts with C2PA manifests, a WordPress plugin
(PR #294) bringing text provenance to the web's dominant CMS layer, a Chrome
verification extension, and an open-source reference implementation under AGPL-3.0.
Encypher has submitted to the C2PA Conformance Program, passing the generator
product security review with implementation review [in progress / complete]. The
C2PA team includes Eddan Katz (policy advisor; AI governance, copyright law, former
Meta C2PA policy support) and Madhav Chinnappa (strategic advisor; former Google
News director, BBC News, Reuters Institute Fellow).

---

## Q1. Why is your organization seeking a Steering Committee role?

> **Home evidence:** Text provenance governance gap. Domain authority argument.
> **Cross-references from:** Q7 (spec authorship, brief mention), Q13 (adoption phase)

Text provenance is C2PA's newest domain. The specification published January 8,
2026. The transition from published spec to real-world adoption is the phase where
governance decisions shape whether text provenance succeeds or stalls.

Encypher authored the text provenance specification (Section A.7), built the
reference implementation, and is the only organization with active publisher
coalition relationships translating the standard into adoption. The person who
wrote the spec and built the implementation should be at the governance table
during this transition, not because of organizational ambition, but because
informed governance of text provenance requires the domain expertise we bring.

C2PA's historical strength is visual media. As text provenance scales, the
Steering Committee will face decisions about text-specific conformance criteria,
publisher onboarding frameworks, and AI company integration standards. We bring
the technical depth and ecosystem relationships to inform those decisions.

---

## Q2. How will your organization support the mission, Guiding Principles, and Charter of the C2PA?

> **Home evidence:** Track record of existing support (shift from "we will" to "we have been").
> **Cross-references from:** Q3 (involvement, brief), Q7 (contributions, brief)

We already do. Erik Svilich has attended [X] consecutive weekly C2PA working group
sessions as Co-Chair of the Text Provenance Task Force. Our support for C2PA's
mission is embedded in our business model, not a side activity:

- **Specification development:** Authored Section A.7, extending C2PA into
  unstructured text.
- **Reference implementation:** Open-source implementation (AGPL-3.0) ensures
  every developer starts with a standards-compliant foundation.
- **Free verification:** Our public verification API covers all media types at no
  cost, removing friction from the trust chain. Every verification strengthens
  the C2PA ecosystem.
- **Regulatory advocacy:** Submitted formal public comment on the EU Code of
  Practice on AI-Generated Content, advocating mandatory C2PA signing.
- **Publisher adoption:** Building coalition relationships (NMA, SPUR, enterprise
  publishers) that translate the standard into real-world implementation.

SC membership would expand this work into governance, subcommittee participation,
and cross-domain coordination.

---

## Q3. Describe your organization's current involvement in provenance, authenticity, or related standards.

> **Home evidence:** Comprehensive inventory of current involvement.
> **Cross-references from:** Q7 (material impact -- spec authorship gets full treatment there)

Current C2PA involvement:

- **Co-Chair,** C2PA Text Provenance Task Force (active since [date])
- **Specification author,** Section A.7 of C2PA 2.3 (published January 8, 2026)
- **[X] consecutive weeks** of weekly working group meeting attendance
- **Conformance Program** participant (generator security review passed;
  implementation review [in progress / complete])
- **Patent holder,** ENC0100 (83 claims, filed January 7, 2026), extending C2PA
  with sentence-level content authentication

Standards and policy engagement beyond C2PA:

- **EU Code of Practice** on AI-Generated Content: formal public comment submitted,
  advocating mandatory C2PA signing for AI-generated text
- **News Media Alliance (NMA):** Presented to AI Licensing Working Group
  (February 2026)
- **SPUR Coalition (UK):** [Active collaboration / engaged] on publisher standards
  convergence with BBC, FT, Guardian, Sky News, Telegraph
- **Scott Cunningham / AAM:** Standards stack alignment mapping C2PA alongside
  IAB Tech Lab, NMA, and AAM frameworks

---

## Q4. Describe your technical expertise relevant to C2PA.

> **Home evidence:** C2PA-specific technical depth. Patent details.
> **Cross-references from:** Q5 (implementations -- products get full treatment there)

Our technical expertise comes from building the specification and implementing it
at production scale:

**Specification-level expertise:**
- Authored the C2PA text provenance specification (Section A.7), including manifest
  embedding architecture for unstructured text
- Deep familiarity with JUMBF/COSE manifest structures, trust list management,
  certificate chain validation, and C2PA assertion schemas
- Live video stream signing per C2PA 2.3 Section 19 (per-segment manifests with
  backwards-linked provenance chain)

**Implementation expertise:**
- Production signing across 31 MIME types in 6 media categories (text, images,
  audio, video, documents, fonts)
- Two verification pipelines: c2pa-python (c2pa-rs) for natively supported formats
  and custom JUMBF/COSE structural verification for extended formats
- Perceptual hash (pHash) attribution search for fuzzy derivative matching across
  resized and reformatted image variants

**Patent-pending extensions (ENC0100, 83 claims):**
- Sentence-level Merkle tree authentication extending C2PA's document-level approach
- Per-character attribution and distributed invisible embedding
- Cryptographic evidence generation for provenance verification

---

## Q5. What C2PA-related products, prototypes, or implementations have you built or deployed?

> **Home evidence:** Definitive product list. Production status for each.
> **Cross-references from:** Q12 (reach -- adoption numbers there), Q8 (OSS contributions)

All items below are production systems, not prototypes:

- **Enterprise Signing API:** Production API generating C2PA JUMBF manifests for 31
  MIME types across text, images (13 formats), audio (6 formats), video (4 formats),
  documents (5 formats), and fonts (3 formats). Includes live video stream signing.

- **Open-Source Reference Implementation** (c2pa-text): Document-level C2PA text
  provenance under AGPL-3.0. Available on GitHub.

- **WordPress Plugin** (PR #294): C2PA text provenance integration for the CMS
  powering [40%+] of the web. [Confirmed for WordPress 7.0 / PR submitted and
  under review.]

- **Chrome Verification Extension:** Browser-level Content Credentials verification
  for text content. Publicly available.

- **Public Verification API:** No-authentication verification endpoint covering all
  supported media types. Free for any third party.

- **Enterprise Dashboard:** Signing management, provenance monitoring, and
  attribution analytics.

Submitted to the C2PA Conformance Program. Generator product security review
passed. Implementation review [in progress / complete -- cite expected date].

---

## Q6. Have you submitted or plan to submit any products or services to C2PA's Conformance Program?

> **Home evidence:** Conformance status. This is the definitive answer.

Yes. Encypher has submitted to the C2PA Conformance Program.

- **Generator product security review:** Passed.
- **Implementation review:** [In progress, expected completion [date] / Complete,
  certification granted [date].]
- **Scope:** [Specify which products and capabilities were included in the
  submission.]

[If certification is complete before submission, lead with: "Encypher is C2PA
Conformance Certified as of [date]." If still in progress, state timeline
confidently.]

---

## Q7. Please identify how your organization has materially impacted the technical and/or advocacy goals of the C2PA.

> **Home evidence:** Spec authorship (definitive treatment here). Advocacy record.
> **Cross-references from:** Q1 (brief mention), Q3 (listed), Q8 (OSS subset)

**Technical impact:**

Erik Svilich authored Section A.7 of C2PA 2.3, "Embedding Manifests into
Unstructured Text," published January 8, 2026. This extended C2PA's provenance
framework from visual media into text for the first time. As Co-Chair of the Text
Provenance Task Force, Erik led the specification development process through
publication and continues to lead the working group through the adoption phase.

Encypher built the production reference implementation of the specification,
providing the starting point for developers implementing C2PA text provenance.
Patent application ENC0100 (83 claims) extends C2PA's document-level approach
with sentence-level Merkle tree authentication, contributing capabilities that
strengthen the ecosystem while remaining standard-compatible.

**Advocacy impact:**

- Submitted formal public comment on the EU Code of Practice on AI-Generated
  Content, advocating mandatory C2PA signing for AI-generated text content.
- Presented to the News Media Alliance AI Licensing Working Group (February 2026),
  connecting C2PA text provenance to publisher adoption pathways.
- Building publisher coalition relationships (NMA, SPUR, enterprise publishers)
  that translate C2PA from specification into adoption infrastructure.

---

## Q8. Please identify material contributions from your organization that were accepted into open-source software or standards development organizations.

> **Home evidence:** Verifiable, accepted contributions only. Short list.

1. **C2PA Specification 2.3, Section A.7:** "Embedding Manifests into Unstructured
   Text." Authored by Erik Svilich. Accepted and published January 8, 2026.
   [Link: https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#embedding_manifests_into_unstructured_text]

2. **c2pa-text:** Open-source C2PA text provenance reference implementation.
   AGPL-3.0. [Link: GitHub repository URL]

3. **WordPress PR #294:** C2PA text provenance integration submitted to WordPress
   core. [Link: GitHub PR URL]

---

## Q9. Please identify up to 3 experts from your organization who will be collaborating to address the problems identified in C2PA's guiding documents. (100 words each)

> **Home evidence:** Three expert profiles. Each maps to a specific SC function.
> **Structure:** Erik = primary (weekly meetings + SC), Eddan = dedicated subcommittee
> coverage (part-time, Gov Affairs + Comms), Madhav = strategic advisor (publisher
> ecosystem expertise for adoption workstreams).

**Erik Svilich** -- Founder & CEO, Encypher Corporation. Author of C2PA 2.3
Section A.7, the text provenance specification published January 8, 2026.
Co-Chair, C2PA Text Provenance Task Force. Patent holder (ENC0100, 83 claims)
for sentence-level content authentication extending C2PA capabilities. Built
production reference implementation including enterprise signing API, WordPress
integration (PR #294), and Chrome verification extension. Attends 1-3 C2PA
meetings weekly. Submitted formal public comment on EU Code of Practice on
AI-Generated Content advocating mandatory C2PA signing. Full decision-making
authority as CEO. Covers Steering Committee, Text Provenance Task Force, and
technical working groups.

**Eddan Katz** -- Policy Advisor, Encypher Corporation. Research Fellow at UC Law
SF focusing on copyright and AI Agent liability, the legal questions at the center
of C2PA's mission. Directly supported Meta's C2PA engagement on the AI Policy
team, conducting policy research for the company's standards negotiations. First
Executive Director of Yale Law School's Information Society Project. International
Affairs Director at the Electronic Frontier Foundation. AI Governance Platform
Lead at the World Economic Forum's Centre for the Fourth Industrial Revolution.
Co-founder, TechnoEthos (responsible AI governance). Covers C2PA's Governmental
Affairs and Communications subcommittees.

**Madhav Chinnappa** -- Strategic Advisor, Encypher Corporation. Reuters Institute
Visiting Fellow (Oxford) and Future Insights Board member at Mediahuis. Former
Director of News Ecosystem Development at Google (13 years), leading global
publisher partnerships, innovation programs, and sustainability funds including the
Digital News Innovation Fund and Google News Initiative. Former Head of Development
& Rights at BBC News. Former Deputy Director at Associated Press Television. Three
decades building publisher-technology ecosystem infrastructure globally. Expertise
in content rights, news sustainability, and the publisher adoption dynamics
critical to scaling C2PA text provenance. Advises on publisher ecosystem adoption
workstreams.

---

## Q10. Describe your organization's experience with standards bodies or multi-stakeholder governance.

> **Home evidence:** Range of standards body experience across the team.
> **Cross-references from:** Q3 (current C2PA involvement)

**Encypher (organizational):**
- C2PA Text Provenance Task Force: Co-Chair, active weekly participant
- EU Code of Practice on AI-Generated Content: formal public comment
- News Media Alliance: AI Licensing Working Group presenter and ongoing engagement
- SPUR Coalition (UK): [Collaboration / engagement] on multi-stakeholder publisher
  standards convergence

**Team experience:**
- **Eddan Katz:** World Economic Forum global AI ethics initiatives. United Nations
  digital rights coalition representation. Meta standards negotiations support.
  Credo AI regulatory governance frameworks.
- **Madhav Chinnappa:** 13 years leading Google's global publisher partnership and
  standards programs (Digital News Innovation Fund, Google News Initiative). BBC
  content rights frameworks. Reuters Institute research fellowship.

The team brings experience across technical standards development (C2PA),
regulatory engagement (EU, UN), industry coalition governance (NMA, SPUR), and
platform-publisher standards infrastructure (Google, BBC).

---

## Q11. What resources do you plan to commit to the Steering Committee, Working Groups, and Task Forces?

> **Home evidence:** Demonstrated track record first, then forward commitment.
> **Frame:** "We already do this. The SC seat formalizes what's sustained."

Erik Svilich currently attends 1-3 C2PA meetings per week as Co-Chair of the
Text Provenance Task Force and active working group participant. He has maintained
this cadence since [date -- confirm]. The SC seat expands an existing weekly
commitment, not a new obligation.

**C2PA team structure with SC membership:**

- **Erik Svilich (CEO):** Primary representative. Steering Committee meetings,
  Text Provenance Task Force (Co-Chair, continuing), and technical working groups.
  1-3 meetings/week currently; SC participation adds to this baseline. Full
  decision-making authority.

- **Eddan Katz (Policy Advisor):** Governmental Affairs and Communications
  subcommittees. Part-time dedicated commitment covering C2PA's policy and
  regulatory workstreams. Expertise in EU AI Act, US state AI legislation, and
  multi-stakeholder governance. SC membership formalizes a dedicated C2PA
  regulatory role within Encypher.

- **Madhav Chinnappa (Strategic Advisor):** Publisher ecosystem adoption
  workstreams. Available for specific initiatives, briefings, and working sessions
  where publisher-technology ecosystem expertise is required. Three decades of
  relationships across BBC, Google, AP, and the global news industry inform
  Encypher's approach to scaling C2PA text provenance adoption.

The team covers three lanes: technical governance and standards development
(Erik), policy, regulation, and governmental affairs (Eddan), and publisher
ecosystem adoption and industry relationships (Madhav).

SC membership supports Encypher's planned expansion of dedicated C2PA resources.
The governance commitment justifies 1-2 full-time roles focused on standards
development, policy engagement, and ecosystem coordination, building sustained
institutional capacity beyond the founding team's current allocation.

---

## Q12. Describe your organization's reach (users, customers, partners).

> **Home evidence:** Infrastructure reach, not customer count. Framing sentence first.
> **Cross-references from:** Q5 (product details there, not here)
> **Critical:** Track 3 fact confirmations determine this answer's ceiling.

Encypher's reach operates at infrastructure integration points rather than direct
consumer endpoints. Our implementation is positioned at the CMS layer, the ad-tech
layer, and the publisher platform layer, creating distribution leverage through
integration rather than audience scale.

**CMS layer:**
- WordPress plugin [confirmed for WordPress 7.0 / submitted as PR #294]. WordPress
  powers [40%+] of websites globally.

**Publisher platform layer:**
- Freestar/PubOS: [Partnership status -- CONFIRM]. Network of 700+ publishers
  including Reuters, Fortune, and Al Jazeera.
- NPR: [Evaluating Encypher's provenance infrastructure for their full media
  portfolio, including text, audio, and broadcast distribution / CONFIRM -- ask sent, awaiting permission].

**Ad-tech layer:**
- Prebid: [Implementation status -- CONFIRM]. Prebid's ecosystem spans [70K+]
  publisher sites.

**Standards ecosystem:**
- NMA (News Media Alliance): Engaged with US news publisher membership.
- SPUR Coalition: [Collaboration status -- CONFIRM] with UK publishers (BBC, FT,
  Guardian, Sky News, Telegraph).

**Open ecosystem:**
- Open-source reference implementation: publicly available (AGPL-3.0).
- Chrome verification extension: publicly available.
- Public verification API: free, no authentication required, all media types.

---

## Q13. How would SC membership enable broader adoption of C2PA?

> **Home evidence:** What C2PA needs that Encypher delivers. Forward-looking.
> **Cross-references from:** Q1 (governance gap, brief), Q14 (ecosystem leverage)

Text provenance is C2PA's newest capability and its least adopted. SC membership
would accelerate adoption in three ways:

**Publisher ecosystem bridge.** Encypher maintains active relationships with
publisher coalitions on both sides of the Atlantic (NMA in the US, SPUR in the
UK) and with individual publishers evaluating implementation (AP, NPR, Taylor &
Francis, Freestar's 700+ publisher network). SC membership connects these adoption
conversations directly to governance decisions, ensuring that publisher needs
inform C2PA's text provenance roadmap.

**CMS-layer distribution.** The WordPress integration path could make C2PA text
provenance available to [40%+] of the web through a single plugin. SC
coordination would help align this distribution with C2PA's broader adoption
strategy and conformance requirements.

**Regulatory preparation.** The EU AI Act enforcement deadline for AI content
transparency is August 2, 2026. Encypher has already submitted formal public
comment on the Code of Practice advocating C2PA. SC membership would help
coordinate C2PA's positioning on text provenance as the regulatory window narrows.

---

## Q14. What unique ecosystem leverage do you bring?

> **Home evidence:** The combination argument. "Bridge" frame.
> **Cross-references from:** Q7 (spec authorship, brief), Q12 (reach, brief)

Encypher is the only organization that combines C2PA specification authorship,
production reference implementation, and active publisher adoption relationships.

No other applicant connects these three layers simultaneously:

1. **Standards authority:** Authored Section A.7. Co-Chair of the task force that
   developed it. Patent portfolio (ENC0100) extends C2PA capabilities while
   remaining standard-compatible.

2. **Implementation infrastructure:** Production signing API, open-source reference
   implementation, WordPress integration, and conformance program participation.
   Developers implementing C2PA text provenance start with our code.

3. **Adoption ecosystem:** Publisher coalition relationships (NMA, SPUR, AP, NPR,
   Freestar), platform integration points (WordPress, Prebid), and the
   four-layer standards stack alignment (C2PA + IAB Tech Lab + NMA + AAM)
   identified through collaboration with Scott Cunningham, founder of IAB Tech
   Lab and TAG.

This combination means SC decisions about text provenance would be informed by
someone who wrote the spec, built the implementation, and works daily with the
publishers who will adopt it.

---

## Q15. What gaps or opportunities do you believe C2PA should address in the next 12-24 months?

> **Home evidence:** Governance-level vision beyond Encypher's own product.
> **Tone:** Constructive. "Here's what I see coming" not "here's what's wrong."

Three areas where C2PA governance can shape outcomes over the next 12-24 months:

**1. Text-specific conformance criteria.** The Conformance Program was designed
around visual media. Text provenance has different security surfaces: invisible
character stripping by platforms, copy-paste transformation, CMS normalization,
and format conversion. C2PA should develop text-specific conformance test suites
that account for these realities. The reference implementation and our conformance
submission provide a foundation for defining those criteria.

**2. AI ingestion-time provenance framework.** C2PA Content Credentials can
currently be verified on the open web (surface-level detection). The next
adoption milestone is AI companies checking for C2PA manifests during data
ingestion. This requires a collaborative framework, not a technical specification
alone. Several SC members (OpenAI, Google, Meta, Amazon, Microsoft) operate AI
pipelines where this framework would apply. SC coordination is the right venue
to develop it.

**3. EU AI Act content transparency.** The enforcement deadline is August 2, 2026.
The draft Code of Practice explicitly requires machine-readable marking and
watermarking with a multilayered approach. C2PA should position proactively as
compliance infrastructure for text content, not wait for regulatory interpretation
to settle. Encypher has already engaged this process through formal public comment.

---

## Q16. Links to relevant products, demos, documentation, or public statements.

> **Home evidence:** Curated list. Each link verifies a specific claim made elsewhere.

| Resource | Link | Verifies |
|---|---|---|
| C2PA 2.3 Section A.7 | https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#embedding_manifests_into_unstructured_text | Spec authorship (Q7) |
| Open-source reference implementation | [GitHub repo URL] | OSS contribution (Q8) |
| WordPress PR #294 | [GitHub PR URL] | CMS integration (Q5, Q8) |
| EU Code of Practice public comment | [Link if publicly accessible] | Regulatory advocacy (Q7) |
| Chrome verification extension | [Chrome Web Store URL] | Verification tooling (Q5) |
| Enterprise API documentation | [URL] | Production implementation (Q5) |
| Company website | [encypher.com URL] | Organizational overview |
| Patent application ENC0100 | [Reference number or public filing link if available] | Technical extension (Q4) |
| [Published blog posts on content provenance] | [URLs] | Public commitment (Q2) |

---

## Q17. Ownership disclosure.

Encypher Corporation is a privately held Delaware corporation. The company is
founder-controlled. Erik Svilich (CEO) holds majority equity and full
decision-making authority. No external entity or government directs or controls
the management or decisions of the organization.

---

## Internal Notes (Do Not Submit)

### Track 2: Private Conversations (Schedule Before SC Deliberation)

| Conversation | Who Initiates | Target | Status |
|---|---|---|---|
| Madhav -> Google SC reps | Madhav Chinnappa | Google's C2PA SC representatives | [ ] Identify reps. [ ] Confirm personal relationship. [ ] Schedule call. |
| Eddan -> Meta SC reps | Eddan Katz | Meta's C2PA SC representatives | [ ] Identify reps. [ ] Confirm team continuity. [ ] Schedule call. |
| Charlie Hartford -> BBC SC reps | Erik (informs Charlie) | BBC's C2PA SC representatives | [ ] Inform Charlie of application. [ ] Request informal internal advocacy. |

**Timing:** These conversations should happen after questionnaire submission but
before SC members confer on their top-3 picks. Too early and it is forgotten.
Too late and the decision is made.

### Track 3: Fact Confirmations (Resolve Before Final Draft)

| Fact | Contact | Accurate Characterization | Confirmed? |
|---|---|---|---|
| WordPress 7.0 inclusion | Automattic/WordPress contact | [ ] "Confirmed for 7.0" / [ ] "PR submitted, under review" / [ ] Other | [ ] |
| Prebid implementation | Prebid contact | [ ] "Formal commitment" / [ ] "In evaluation" / [ ] "In discussion" | [ ] |
| Freestar/PubOS partnership | Kurt Donnell | [ ] "Partnership signed" / [ ] "In legal review" / [ ] "In discussion" | [ ] |
| NPR evaluation | Erica (NPR, BD/Licensing) | [ ] "Evaluating full media portfolio" / [ ] Other | Ask sent 2026-03-30; awaiting reply |
| SPUR collaboration | Charlie Hatford | [ ] "Formal collaboration" / [ ] "Active engagement" / [ ] Other | [ ] |
| Conformance timeline | C2PA Conformance Program | [ ] Expected completion date | [ ] |
| Erik's C2PA weekly hours | Erik | [ ] Specific number | [ ] |
| Consecutive weeks attendance | Erik | [ ] Specific count | [ ] |
| Eddan engagement status | Eddan Katz | [ ] Employee / Advisor / Contractor. [ ] Hours/week | [ ] |
| Madhav engagement status | Madhav Chinnappa | [ ] Employee / Advisor / Contractor. [ ] Hours/week | [ ] |

### Evidence Deduplication Map

Each evidence point has one "home" question where it gets full treatment.
Other questions cross-reference briefly. Do not restate the same facts at length
in multiple answers.

| Evidence Point | Home Question | Brief Cross-Reference In |
|---|---|---|
| Section A.7 authorship | Q7 (material impact) | Q1 (one sentence), Q3 (listed), Q4 (context) |
| Reference implementation | Q5 (implementations) | Q7 (supporting), Q8 (listed) |
| WordPress PR #294 | Q5 (implementations) | Q8 (listed), Q12 (reach context) |
| Patent ENC0100 | Q4 (technical expertise) | Q7 (supporting), Q14 (leverage) |
| EU Code of Practice | Q7 (advocacy) | Q2 (listed), Q10 (standards experience), Q15 (context) |
| Conformance program | Q6 (home) | Q3 (listed), Q5 (brief mention) |
| Publisher coalitions (NMA, SPUR) | Q13 (adoption) | Q3 (listed), Q12 (reach) |
| 31 MIME types | Q5 (implementations) | Q4 (technical breadth) |
| Free verification | Q2 (mission support) | Q5 (listed), Q14 (leverage) |
| Three experts | Q9 (home) | Q11 (resource commitment) |

### Change Log

- **2026-03-29:** Initial working draft created. All questions drafted with
  evidence mapping. Track 2 and Track 3 checklists included. Awaiting fact
  confirmations before finalizing.
