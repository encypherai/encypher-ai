---
# Research Notes
## Topic
The AI Authorship Documentation Gap After the Supreme Court's Thaler Denial

## Proposed Thesis
The Supreme Court's Thaler denial confirmed that AI-generated works need human authorship to be copyrightable but left no bright-line test for how much human involvement qualifies - and machine-readable provenance metadata is the only infrastructure that can document the human contribution chain at the scale organizations now require.

## Suggested Title
AI Authorship After Thaler: The Documentation Gap Courts Left Open

## Suggested Tags
C2PA, AI Copyright, Content Provenance, Copyright Law, AI Governance, Content Authentication, Legal Analysis

## Sources
1. URL: https://www.hklaw.com/en/insights/publications/2026/03/the-final-word-supreme-court-refuses-to-hear-case-on-ai-authorship
   Date: March 2026
   Key finding: The US Supreme Court denied certiorari in Thaler v. Perlmutter on March 2, 2026, leaving intact the DC Circuit ruling that the Copyright Act requires human authorship. Dr. Thaler explicitly disclaimed any human creative input, so the court did not address how much human involvement is necessary for AI-assisted works.
   Exact quotes: Circuit Judge Patricia A. Millett wrote that "The Creativity Machine cannot be the recognized author of a copyrighted work because the Copyright Act of 1976 requires all eligible work to be authored in the first instance by a human being."
   Backup URL: https://www.morganlewis.com/pubs/2026/03/us-supreme-court-declines-to-consider-whether-ai-alone-can-create-copyrighted-works (Morgan Lewis confirming the same ruling and date)
   Supports: The ruling settled the easy question (pure AI output is uncopyrightable) but explicitly left the hard question open (human-AI collaboration threshold).

2. URL: https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf
   Date: January 2025
   Key finding: The US Copyright Office concluded that copyrightability of AI-assisted works must be assessed on a case-by-case basis. The mere provision of prompts does not constitute authorship. The Office identified four categories of potential human contribution: (1) using AI to facilitate human creative process, (2) prompts to generate outputs, (3) expressive inputs, and (4) human modifications or arrangements of AI-generated content. No numerical threshold or bright-line test was provided.
   Exact quotes: The report states that "the mere selection of prompts, even if those prompts are detailed and are the product of some human effort, does not itself yield a copyrightable work."
   Backup URL: https://www.jonesday.com/en/insights/2025/02/copyrightability-of-ai-outputs-us-copyright-office-analyzes-human-authorship-requirement (Jones Day analysis confirming the same conclusions)
   Supports: The case-by-case standard is explicitly unscalable - organizations producing thousands of AI-assisted works per day cannot submit each one for individualized Copyright Office review.

3. URL: https://www.mondaq.com/unitedstates/copyright/1735886/when-600-prompts-still-arent-enough-what-allen-vs-perlmutter-means-for-ownership-copyright-and-creative-contracts
   Date: 2026
   Key finding: In Allen v. Perlmutter (pending in Colorado), Jason Allen's award-winning AI-generated image "Theatre D'opera Spatial" was denied copyright registration despite Allen entering at least 624 prompts, using Midjourney's variation and upscaling tools, and cleaning up the image in Photoshop. The Copyright Office Review Board concluded that Allen's iterative prompting process did not amount to human authorship. This case may provide the first judicial test of where the authorship line falls for AI-assisted works.
   Exact quotes: None confirmed verbatim from this source.
   Backup URL: https://copyrightlately.com/thaler-is-dead-ai-copyright-questions/ (Copyright Lately, confirming Allen v. Perlmutter is pending and may establish the authorship line)
   Supports: Demonstrates that even substantial human effort (624 prompts, post-processing) may not cross the authorship threshold - reinforcing that the standard is unclear and documentation of human contribution is critical.

4. URL: https://copyrightlately.com/thaler-is-dead-ai-copyright-questions/
   Date: March 2026
   Key finding: Analysis argues that the Thaler denial settled the easy case but the harder questions remain. The central unresolved question is whether prompting is closer to authorship or closer to curation. The article also identifies a paradox: AI-generated work may be too machine-authored to own copyright and still close enough to someone else's protected expression to infringe.
   Exact quotes: The article frames the paradox as: "The same AI-generated work may be too machine-authored to own and still close enough to someone else's protected expression to infringe."
   Backup URL: none found
   Supports: Establishes the operational paradox organizations face - they cannot protect their AI-assisted outputs without documenting human contribution, yet the standard for sufficient documentation remains undefined.

5. URL: https://contentauthenticity.org/how-it-works
   Date: Current (evergreen reference)
   Key finding: C2PA Content Credentials embed cryptographically signed metadata documenting the origin of content, the tools used during creation, and any subsequent human edits or modifications. The metadata tracks the specific AI models used, the date of creation, and the human authorship chain. Any tampering breaks the cryptographic signature, making modifications detectable. This provides exactly the kind of verifiable human contribution record that courts and the Copyright Office are implicitly requiring.
   Exact quotes: None verbatim confirmed.
   Backup URL: https://c2pa.org/ (C2PA official site confirming the standard's purpose and capabilities)
   Supports: Content provenance metadata is the technical infrastructure that solves the documentation problem - recording who directed the AI, what modifications were made, and creating a tamper-evident chain of human creative decisions.

## Counterarguments Found
- Case-by-case adjudication may be sufficient: Courts have always evaluated originality on a case-by-case basis (Feist v. Rural). The lack of a bright-line test is not new to copyright law. Rebuttal: The volume of AI-assisted content creation has no precedent. A photographer might register a few hundred works per year. An enterprise using generative AI might produce thousands of documents per day. Case-by-case review does not scale to this volume.
- Prompting may eventually be recognized as authorship: As AI tools evolve and prompting becomes more sophisticated, courts may expand what counts as sufficient human contribution. The Copyright Office itself noted that "this determination could change as technology evolves." Rebuttal: Even if prompting is eventually recognized, the documentation problem remains. Organizations still need to record what prompts were used, what modifications were made, and by whom - exactly the function provenance metadata serves.
- Copyright registration is not required for protection: Copyright exists at the moment of creation, not registration. Organizations do not need to solve the registration problem to have rights. Rebuttal: While true, registration is required to bring an infringement lawsuit in federal court and to claim statutory damages. Without registration, copyright protection is significantly weakened in practice, especially for commercial content.

## Recommended Post Structure
- Opening: The Supreme Court's March 2 denial in Thaler v. Perlmutter was widely reported as settling the AI authorship question. It did not. It settled the easy question - whether a machine with zero human involvement can be an author. The hard question, which affects every organization using AI to produce content, remains open: how much human involvement makes an AI-assisted work copyrightable?
- Section 1 (The Gap Thaler Left Open): Walk through what the ruling actually decided versus what it did not. Thaler explicitly disclaimed human involvement - a fact the courts noted repeatedly. The ruling says nothing about the spectrum of human-AI collaboration that defines modern content production. Cite the Holland & Knight and Morgan Lewis analyses.
- Section 2 (624 Prompts and Counting): Use Allen v. Perlmutter and Zarya of the Dawn as case studies showing how the Copyright Office has drawn (and redrawn) the line in practice. Allen used 624 prompts and still failed. Zarya received partial protection - text and arrangement, but not the AI-generated images. The pattern: the Copyright Office is looking for evidence of human creative decisions, but has not defined what that evidence should look like.
- Section 3 (The Scale Problem): Steelman the counterargument that case-by-case review has always worked for copyright. Then show why AI breaks this: volume (thousands of works per day), ambiguity (the human-AI boundary is continuous, not binary), and the paradox identified by Copyright Lately - the same work can be too machine-made to protect and close enough to existing expression to infringe. The Copyright Office's own Part 2 Report confirms no bright-line test exists.
- Section 4 (Content Provenance as the Documentation Layer): This is where machine-readable provenance metadata enters the argument. C2PA Content Credentials can record the creation chain - which AI tools were used, what human edits were made, the sequence of creative decisions. This does not solve the legal question of how much human involvement is enough, but it solves the evidentiary question of proving what human involvement existed. For organizations producing AI-assisted content at scale, this is the difference between being able to demonstrate human authorship and having no record at all.
- Closing: The Thaler decision closed a door that was already closed - pure AI output was never going to be copyrightable. The door that matters is the one the courts left open: what documentation of human contribution will be sufficient. Organizations that embed provenance metadata now will have that documentation when courts and regulators define the threshold. Those that do not will be left reconstructing creative processes after the fact, one work at a time. Allen v. Perlmutter, pending in Colorado, may be the next marker. The infrastructure question will not wait for the courts to catch up.
