# Hardware-Verified Human Authorship Attestation

**Created:** March 23, 2026
**Status:** Concept / Pre-Development
**Owner:** Product + Engineering
**Parent Product Line:** Encypher Attest
**Distribution:** Executive, Product, Engineering, Legal

---

## Concept Summary

Add a creation-time attestation layer to Encypher Attest that cryptographically proves content
was physically typed by a human on verified hardware. A firmware-level agent leverages the
TPM 2.0 / Secure Enclave already present on enterprise machines to produce hardware-backed
attestation tokens that get embedded as assertions inside Encypher's C2PA manifests alongside
the existing sentence-level Merkle tree.

This closes the one attestation gap Attest currently has: Attest proves what happened
*after* content exists (signing, review, approval, integrity). Hardware-verified authorship
proves something about the creation moment itself -- that physical keystrokes produced the
content on real hardware.

---

## Strategic Rationale

### The Gap in Current Attest

Attest today captures:
1. What AI-assisted content was generated (original AI text)
2. What changed during human review (diff tracking)
3. Who approved it (approval chain)
4. Whether final output is authentic (tamper detection via Merkle trees)

Attest is agnostic about *how* content was created. A user could paste AI-generated text,
claim they wrote it, and Attest would sign it as-is. For the publisher coalition motion this
is fine -- the goal is provenance, not authorship verification. But for the Attest enterprise
verticals (legal, finserv, healthcare, governance), "prove a human actually wrote this" is a
distinct and increasingly valuable claim.

### EU AI Act Compliance Deadline

The EU AI Act enforcement deadline is **August 2, 2026** -- five months away. The draft
Code of Practice requires machine-readable marking and watermarking with a multilayered
approach (visible + invisible). Hardware-verified human authorship attestation provides
enterprises with a compliance-ready mechanism to distinguish human-authored content from
AI-generated content with cryptographic evidence, not just policy declarations.

### Market Context: Software-Only Approaches Are Emerging

WritersLogic (David Condrey) is building a software-only "Proof of Process" framework using
Verifiable Delay Functions and behavioral entropy ("jitter seals") to distinguish human typing
from algorithmic generation. This is published as IETF Internet-Drafts (draft-condrey-rats-pop
series) and presented at IETF 125 dispatch (March 16, 2026). Condrey has a patent application
(USPTO 19/460,364) on his software approach.

The software-only approach has a fundamental adversarial weakness: any software-level keystroke
capture can be spoofed by other software. AI can generate text character-by-character to mimic
human typing patterns. Recorded sessions can be replayed. VDFs prove time elapsed, but not
that a human was on the other end.

Hardware-verified attestation solves this by anchoring the trust chain to a physical device
that software cannot forge.

---

## Technical Architecture

### Recommended Approach: Firmware Agent with TPM 2.0

A firmware-level agent (kernel driver / OS secure enclave integration) that:

1. **Captures keystroke events** at the OS input layer with high-resolution timing
2. **Produces behavioral metrics** -- typing cadence, inter-key intervals, pause patterns,
   revision behavior, editing entropy -- without capturing content
3. **Signs the metrics via TPM 2.0** -- the TPM produces an attestation token binding the
   behavioral evidence to a hardware-backed key. This proves the evidence originated from
   a real machine with a real TPM, not from a software simulator
4. **Generates a RATS-format Evidence claim** -- compatible with IETF RATS architecture
   (RFC 9334) for interoperability
5. **Embeds the attestation as a C2PA assertion** inside the Encypher manifest alongside
   the Merkle tree, producing a combined claim: "this content was physically authored on
   verified hardware AND its integrity is cryptographically guaranteed at sentence level"

### Why Firmware Agent Over Physical USB Device

| Dimension | Firmware Agent (Recommended) | Physical USB Device |
|---|---|---|
| Trust anchor | Strong -- TPM 2.0 / Secure Enclave | Strongest -- independent secure element |
| Deployability | Software push via MDM/GPO | Hardware procurement cycle |
| Keyboard compatibility | All types (built-in, USB, Bluetooth, wireless) | USB keyboards only |
| Laptop built-in keyboards | Works | Does not work without adapter |
| Marginal cost per seat | ~$0 (software) | $30-80 BOM + logistics |
| Update/patch cycle | Standard software deployment | Firmware flash (risky, slow) |
| Enterprise IT acceptance | Familiar (endpoint agent) | Resistance (another device) |
| OS support required | Windows, macOS, Linux builds needed | OS-agnostic |
| Telemetry richness | Full (keys, mouse, timing, app context) | Limited (USB HID events only) |

The firmware agent is the right v1 because:
- TPM 2.0 is already mandated on every Windows 11 enterprise machine
- Apple Secure Enclave is standard on all modern Macs
- Enterprise IT deploys software agents, not hardware dongles
- The threat model (proving human authorship for compliance) does not require defense against
  kernel-level rootkits -- it requires defense against casual AI output misrepresentation

A physical USB device can be offered as a premium tier for high-security verticals (defense,
intelligence, classified environments) if demand materializes.

### Privacy Architecture

Critical design constraint: the firmware agent must **never capture or transmit content**.

What it captures:
- Keystroke timing and cadence (inter-key intervals, hold durations)
- Input entropy metrics (statistical distribution of timing jitter)
- Editing pattern metadata (insertions, deletions, cursor movements -- as counts, not content)
- Session duration and activity density
- Hardware attestation token from TPM (proves real hardware)

What it does NOT capture:
- Actual characters typed
- Screen content or clipboard content
- Application data or document text
- Passwords or sensitive input (configurable exclusion by application/window)

This separation is essential. "Cryptographic proof of human authorship without seeing what was
written" is a defensible privacy story. "Enterprise keylogger" is not.

### Integration with Existing Attest Architecture

```
                     Encypher Attest Manifest (C2PA)
                     +-----------------------------------+
                     |                                   |
                     |  [Assertion 1] Merkle Tree Root   |  <-- Content integrity (existing)
                     |    - sentence-level hashes         |
                     |    - tamper detection              |
                     |                                   |
                     |  [Assertion 2] Authorship Attest   |  <-- NEW: Hardware-verified creation
                     |    - TPM attestation token         |
                     |    - behavioral entropy metrics    |
                     |    - session metadata              |
                     |    - RATS Evidence format           |
                     |                                   |
                     |  [Assertion 3] Review Chain        |  <-- Approval workflow (existing)
                     |    - AI original -> human edits    |
                     |    - approver identity             |
                     |                                   |
                     |  [Signature] Encypher CA           |
                     +-----------------------------------+
```

The authorship attestation assertion is additive -- it does not modify the existing Merkle tree
or review chain assertions. Manifests without authorship attestation continue to work exactly
as they do today. This is an optional enrichment, not a required dependency.

---

## Target Verticals

These map directly to the existing Attest verticals, with authorship attestation adding
specific value to each:

### Legal
- **Use case:** Prove that a contract draft, legal memo, or court filing was human-authored,
  not generated by AI and passed off as attorney work product
- **Buyer pain:** Bar associations and courts are increasingly requiring AI disclosure;
  attorneys face sanctions for undisclosed AI use (see SDNY standing orders)
- **Value:** Hardware-backed proof that the document was physically typed, not pasted from
  ChatGPT -- stronger than an attorney's self-declaration

### Financial Services
- **Use case:** Prove that analyst reports, research notes, and regulatory filings were
  human-authored where regulations require it
- **Buyer pain:** SEC and FINRA guidance on AI-generated content in investment communications
  is tightening; firms need audit-ready evidence
- **Value:** Compliance evidence that withstands regulatory examination -- "our TPM signed
  the authorship attestation at the time of creation"

### Healthcare
- **Use case:** Prove that clinical documentation, treatment plans, and patient communications
  were authored by licensed practitioners, not AI
- **Buyer pain:** Liability exposure if AI-generated medical advice is presented as
  physician-authored; HIPAA implications of AI in clinical documentation
- **Value:** Hardware-verified chain from physical keyboard to signed clinical record

### Enterprise Governance / EU AI Act
- **Use case:** Organization-wide policy enforcement -- which content is human-authored vs.
  AI-assisted vs. AI-generated
- **Buyer pain:** EU AI Act (August 2, 2026) requires transparency about AI-generated content;
  enterprises need systematic evidence, not per-document declarations
- **Value:** Automated, cryptographic classification of content origin at creation time

---

## Competitive Positioning

### vs. Software-Only Behavioral Attestation (WritersLogic / PoP)

"Software behavioral analysis can distinguish typing patterns, but software can also simulate
them. Our hardware-verified approach anchors the attestation to a physical TPM that software
cannot forge. The attestation token proves the evidence originated from real hardware -- not
from a replay attack or an AI typing simulator."

### vs. AI Detection Tools (GPTZero, Originality.ai, etc.)

"AI detection tools are probabilistic -- they give you a confidence score that degrades as
models improve. Hardware-verified authorship attestation is deterministic -- either the TPM
signed the creation evidence or it did not. You don't get false positives, and the proof
doesn't degrade over time."

### vs. Self-Declaration / Honor System

"A checkbox that says 'I confirm this was not AI-generated' is a policy control, not evidence.
Hardware-verified attestation produces cryptographic proof bound to a physical device and
timestamped by a trusted authority. The difference is the same as a verbal promise vs. a
notarized document."

---

## IP and Patent Considerations

### CIP Opportunity on ENC0100

The hardware-verified authorship attestation concept is a natural continuation-in-part (CIP)
extension to ENC0100 (Granular Content Attribution, filed January 7, 2026). Specifically:

- ENC0100 Claims 56-62 cover evidence generation processes
- ENC0100's manifest structure (Claims 1-7, Merkle trees) is the container for the
  authorship assertion
- The CIP would add claims covering:
  - Hardware-backed attestation of content creation process
  - TPM-bound behavioral entropy signing
  - Integration of RATS-format evidence into C2PA manifests
  - Privacy-preserving keystroke attestation (metrics without content capture)

**Action required:** Patent counsel should evaluate CIP timing. The provisional patent has a
12-month deadline from January 7, 2026 (deadline: January 7, 2027) to file the
non-provisional. CIP claims can be added during this window.

### Freedom-to-Operate Considerations

- WritersLogic / David Condrey has USPTO Application No. 19/460,364 ("Falsifiable Process
  Evidence via Cryptographic Causality Locks and Behavioral Attestation"). FTO search should
  confirm that hardware TPM-based attestation is outside the scope of his software-specific
  VDF/jitter seal claims before development begins.
- IETF RATS (RFC 9334) is an open standard -- implementing the RATS Evidence format for
  interoperability does not create IP entanglement.

---

## Prerequisites

### Before Development

1. **FTO search** on USPTO 19/460,364 (Condrey/WritersLogic) to confirm clean design space
2. **Patent counsel evaluation** of CIP opportunity on ENC0100
3. **TPM 2.0 / Secure Enclave capability audit** -- verify attestation APIs available on
   target enterprise platforms (Windows 11 TPM 2.0, macOS Secure Enclave, Linux TPM2-TSS)
4. **Privacy review** -- ensure the "metrics without content" architecture satisfies GDPR,
   HIPAA, and enterprise DLP requirements
5. **Kernel signing certificates** -- required for Windows kernel drivers (WHQL) and macOS
   System Extensions (Apple Developer Program + notarization)

### Before GTM

1. At least one signed publisher coalition deal (Attest remains gated behind publisher motion)
2. EU AI Act enforcement timeline creates natural demand pull (August 2, 2026)
3. Attest product line reactivated from future_product_concepts to active development

---

## Risks and Mitigations

### Risk: OS kernel access is increasingly restricted
Apple moved from kernel extensions to System Extensions (DriverKit) and is progressively
locking down low-level access. Windows requires WHQL signing for kernel drivers.
**Mitigation:** Build on System Extensions (macOS) and user-mode TPM access (Windows) from
day one. Avoid kernel-mode dependency where platform APIs provide user-mode alternatives.

### Risk: Enterprise security teams resist endpoint agents
Another agent on the endpoint competes with existing EDR, DLP, and monitoring tools.
**Mitigation:** Position as a lightweight attestation service, not a monitoring agent.
Publish independent security audit. Provide enterprise IT with full telemetry scope
documentation before deployment.

### Risk: Behavioral metrics alone may be insufficient
Sophisticated adversaries could develop hardware-level replay devices.
**Mitigation:** Combine behavioral entropy with TPM-bound session nonces and timestamp
anchoring. A replay attack would need to forge TPM attestation tokens, which requires
physical access to the specific TPM -- a dramatically higher bar than software spoofing.

### Risk: Privacy perception as "enterprise keylogger"
Regardless of technical architecture, the concept may face perception challenges.
**Mitigation:** Lead with "proof of human authorship" framing, never "keystroke monitoring."
Third-party privacy audit confirming no content capture. Enterprise-controlled opt-in with
transparent scope documentation. Configurable application exclusions (password managers,
banking sites, etc.).

### Risk: WritersLogic establishes software-only approach as the de facto standard
If Condrey's IETF RATS drafts gain adoption before we ship a hardware-backed alternative,
the market may accept software-only behavioral attestation as "good enough."
**Mitigation:** We co-chair the C2PA text provenance task force. We control what gets
endorsed as the reference approach for text provenance attestation. Software-only PoP does
not enter C2PA without our evaluation. Additionally, hardware-backed attestation is strictly
stronger -- it can always be positioned as the "enterprise grade" tier above software-only.

---

## Estimated Effort

Not estimated. This concept requires prerequisite completion (FTO, CIP evaluation, platform
API audit) before scoping is meaningful. The concept document is intended to inform strategic
direction and patent timing, not to initiate a development sprint.

---

## Relationship to WritersLogic Inbound (March 2026)

David Condrey (WritersLogic) reached out proposing integration of his software-only
"Proof of Process" attestation into Encypher's manifest structure. After evaluation:

- His technical work is real (5+ IETF drafts, IETF 125 presentation, working implementation)
- His approach is software-only (VDFs + jitter seals) -- weaker trust anchor than hardware
- He has a patent application (USPTO 19/460,364) that may or may not overlap with this concept
- A 15-minute intelligence call is warranted (with NDA, without Erik on first call)
- No partnership or integration is recommended at this time
- If his IETF RATS drafts gain traction, we evaluate at the standards level through normal
  C2PA task force process -- we do not need a bilateral partnership to implement support for
  a standard assertion type

The hardware-verified approach described in this document is strategically superior to his
software-only approach and can be developed independently using publicly available TPM APIs
and the IETF RATS Evidence format (RFC 9334).
