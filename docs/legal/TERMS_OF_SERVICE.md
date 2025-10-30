# Encypher Enterprise API - Terms of Service

**Last Updated:** October 28, 2025  
**Effective Date:** October 28, 2025

## 1. Acceptance of Terms

By accessing or using the Encypher Enterprise API (the "Service"), you ("Customer", "you", or "your") agree to be bound by these Terms of Service ("Terms"). If you are entering into these Terms on behalf of an organization, you represent that you have the authority to bind that organization to these Terms.

If you do not agree to these Terms, do not access or use the Service.

## 2. Service Description

Encypher provides a content authentication and verification platform that enables organizations to:

- **Sign Content**: Generate C2PA 2.2 compliant digital signatures for text-based content (articles, legal documents, contracts, AI-generated content)
- **Sentence-Level Tracking**: Create cryptographic proofs for individual sentences within documents
- **Verification Services**: Verify the authenticity and integrity of signed content
- **Certificate Management**: Automated SSL.com certificate lifecycle management for Ed25519 signatures
- **Merkle Tree Evidence**: Generate court-admissible evidence packages for content attribution and plagiarism detection

## 3. Account Registration and API Keys

### 3.1 Account Creation
To use the Service, you must:
- Provide accurate and complete registration information
- Maintain the security of your account credentials
- Promptly update any changes to your account information
- Accept responsibility for all activities under your account

### 3.2 API Keys
- API keys are confidential and must not be shared
- You are responsible for all usage of your API keys
- Lost or compromised keys must be reported immediately to legal@encypherai.com
- We reserve the right to revoke API keys at any time for violation of these Terms

### 3.3 Organization Types
The Service supports multiple organization types:
- **Publishers**: News organizations, media companies, content creators
- **Legal/Finance**: Law firms, financial institutions, compliance departments
- **AI Labs**: AI research organizations, LLM providers
- **Enterprise**: Corporations, government agencies, educational institutions

## 4. Service Tiers and Usage Limits

### 4.1 Service Tiers

**Free Tier:**
- 1,000 API calls per month
- 100 requests per hour
- Community support
- Basic features only

**Business Tier:**
- 50,000 API calls per month
- 1,000 requests per hour
- Email support (48-hour response time)
- All features included

**Enterprise Tier:**
- Custom API call limits
- Custom rate limits
- Priority support (4-hour response time)
- Dedicated account manager
- Custom SLA available
- White-label options available

### 4.2 Rate Limits
- Rate limits are enforced per API key
- Exceeding rate limits results in HTTP 429 (Too Many Requests) responses
- Systematic circumvention of rate limits may result in account suspension

### 4.3 Quota Management
- Monthly quotas reset on the first day of each calendar month
- Unused quota does not roll over to the next month
- Quota overages may be purchased for Business and Enterprise tiers
- Free tier accounts cannot purchase additional quota

## 5. Acceptable Use Policy

### 5.1 Permitted Uses
You may use the Service to:
- Sign and verify authentic content you own or have rights to
- Track provenance of your published content
- Generate evidence for legal proceedings
- Comply with regulatory requirements
- Prevent plagiarism and content theft

### 5.2 Prohibited Uses
You may NOT use the Service to:
- Sign false, misleading, or fraudulent content
- Impersonate other publishers or organizations
- Sign content you do not own or have rights to
- Circumvent rate limits or quota restrictions
- Reverse engineer or attempt to extract cryptographic keys
- Interfere with the Service's operation or security
- Sign illegal content (defamatory, obscene, infringing, etc.)
- Resell or redistribute the Service without authorization
- Use automated tools to abuse the Service

### 5.3 Content Responsibility
- You are solely responsible for all content you sign using the Service
- We do not review, approve, or endorse any content signed through the Service
- We are not liable for any content signed by you or your organization
- You represent and warrant that you have all necessary rights to sign the content

## 6. Data Ownership and Usage

### 6.1 Your Data
- You retain all ownership rights to content you sign using the Service
- We do not claim any ownership of your content
- You grant us a limited license to store and process your content solely to provide the Service

### 6.2 Metadata Storage
We store the following metadata for verification purposes:
- Document titles, URLs, and publication dates
- Sentence-level hashes and signatures
- C2PA manifests and certificates
- API usage logs and timestamps
- Organization information

### 6.3 Data Retention
- **Active Accounts**: Metadata retained indefinitely for verification purposes
- **Deleted Accounts**: Metadata retained for 90 days, then permanently deleted
- **Verification Records**: Retained for 7 years to support legal proceedings
- **Audit Logs**: Retained for 2 years for security and compliance

### 6.4 Data Export
- You may request a complete export of your data at any time
- Data exports provided in JSON format within 30 days
- No charge for data exports

## 7. Intellectual Property

### 7.1 Service Ownership
- Encypher retains all rights, title, and interest in the Service
- These Terms do not grant you any intellectual property rights in the Service
- "Encypher", logos, and trademarks are owned by Encypher

### 7.2 Feedback
- Any feedback, suggestions, or ideas you provide become our property
- We may use feedback without compensation or attribution
- You waive any rights to feedback you provide

## 8. Payment Terms (Business and Enterprise Tiers)

### 8.1 Fees
- Fees are based on your selected service tier
- All fees are in U.S. Dollars (USD)
- Fees are non-refundable except as required by law

### 8.2 Billing
- Business tier: Monthly billing in advance
- Enterprise tier: Annual billing or custom terms
- Payment due within 30 days of invoice date
- Late payments subject to 1.5% monthly interest

### 8.3 Price Changes
- We may change prices with 30 days' notice
- Price changes apply to subsequent billing periods
- You may cancel before price increase takes effect

### 8.4 Taxes
- Fees do not include applicable taxes
- You are responsible for all taxes except those based on our income
- We will invoice taxes separately where required

## 9. Warranties and Disclaimers

### 9.1 Service Warranty
We warrant that the Service will:
- Conform to the documentation provided
- Be provided in a professional manner
- Use industry-standard security practices

### 9.2 DISCLAIMER OF WARRANTIES
EXCEPT AS EXPRESSLY PROVIDED IN SECTION 9.1, THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO:

- IMPLIED WARRANTIES OF MERCHANTABILITY
- FITNESS FOR A PARTICULAR PURPOSE
- NON-INFRINGEMENT
- UNINTERRUPTED OR ERROR-FREE OPERATION
- ACCURACY OR RELIABILITY OF RESULTS
- SECURITY OF DATA

### 9.3 Cryptographic Limitations
- Digital signatures are tamper-evident, not tamper-proof
- Signatures depend on the security of cryptographic keys
- We are not liable for compromised keys or certificates
- Verification depends on the integrity of the verification process

## 10. Limitation of Liability

### 10.1 Liability Cap
TO THE MAXIMUM EXTENT PERMITTED BY LAW, OUR TOTAL LIABILITY ARISING OUT OF OR RELATED TO THESE TERMS SHALL NOT EXCEED THE GREATER OF:
- (A) THE FEES YOU PAID IN THE 12 MONTHS PRECEDING THE CLAIM, OR
- (B) $1,000 USD

### 10.2 Exclusion of Damages
WE SHALL NOT BE LIABLE FOR:
- INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES
- LOSS OF PROFITS, REVENUE, DATA, OR BUSINESS OPPORTUNITIES
- COST OF SUBSTITUTE SERVICES
- DAMAGES ARISING FROM YOUR USE OR INABILITY TO USE THE SERVICE

### 10.3 Exceptions
The limitations in this section do not apply to:
- Our indemnification obligations
- Violations of intellectual property rights
- Fraud or willful misconduct
- Liability that cannot be excluded by law

## 11. Indemnification

You agree to indemnify, defend, and hold harmless Encypher, its affiliates, and their respective officers, directors, employees, and agents from any claims, damages, losses, liabilities, and expenses (including reasonable attorneys' fees) arising out of or related to:

- Your use of the Service
- Content you sign using the Service
- Your violation of these Terms
- Your violation of any third-party rights
- Your violation of applicable laws or regulations

## 12. Term and Termination

### 12.1 Term
These Terms commence when you first access the Service and continue until terminated.

### 12.2 Termination by You
- You may terminate at any time by closing your account
- No refunds for prepaid fees
- Data export available for 90 days after termination

### 12.3 Termination by Us
We may suspend or terminate your account immediately if:
- You violate these Terms
- You fail to pay fees when due
- Your use poses a security risk
- Required by law or court order

### 12.4 Effect of Termination
Upon termination:
- Your access to the Service immediately ceases
- All outstanding fees become immediately due
- We may delete your data after the retention period
- Verification records remain available per Section 6.3
- Sections 6, 7, 9, 10, 11, 13, and 14 survive termination

## 13. Service Level Agreement (Enterprise Tier Only)

### 13.1 Uptime Commitment
- We commit to 99.9% uptime for Enterprise tier customers
- Uptime measured monthly, excluding scheduled maintenance
- Scheduled maintenance announced 7 days in advance

### 13.2 Service Credits
If uptime falls below 99.9%:
- 99.0% - 99.9%: 10% service credit
- 95.0% - 99.0%: 25% service credit
- Below 95.0%: 50% service credit

### 13.3 Credit Claims
- Must be claimed within 30 days of the incident
- Maximum credit: 50% of monthly fees
- Credits applied to future invoices only

### 13.4 Exclusions
Uptime commitment excludes downtime caused by:
- Scheduled maintenance
- Your actions or omissions
- Third-party services (SSL.com, hosting providers)
- Force majeure events
- DDoS attacks or security incidents

## 14. General Provisions

### 14.1 Governing Law
These Terms are governed by the laws of the State of Delaware, United States, without regard to conflict of law principles.

### 14.2 Dispute Resolution
- **Informal Resolution**: Contact legal@encypherai.com to resolve disputes informally
- **Arbitration**: Unresolved disputes shall be settled by binding arbitration under the American Arbitration Association (AAA) Commercial Arbitration Rules
- **Location**: Arbitration held in Wilmington, Delaware
- **Class Action Waiver**: You waive any right to bring claims as a class action

### 14.3 Exceptions to Arbitration
Either party may bring claims in court for:
- Intellectual property infringement
- Violation of the Acceptable Use Policy
- Injunctive relief

### 14.4 Modifications
- We may modify these Terms at any time
- Material changes require 30 days' notice
- Continued use after changes constitutes acceptance
- If you disagree, you must stop using the Service

### 14.5 Assignment
- You may not assign these Terms without our written consent
- We may assign these Terms to any affiliate or successor
- Assignment does not relieve either party of obligations

### 14.6 Entire Agreement
- These Terms constitute the entire agreement between you and Encypher
- Supersedes all prior agreements and understandings
- May only be modified in writing signed by both parties

### 14.7 Severability
If any provision is found unenforceable, the remaining provisions continue in full force and effect.

### 14.8 Waiver
Failure to enforce any provision does not waive our right to enforce it later.

### 14.9 Force Majeure
We are not liable for delays or failures caused by circumstances beyond our reasonable control, including natural disasters, war, terrorism, labor disputes, or internet outages.

### 14.10 Export Compliance
You agree to comply with all applicable export control laws and regulations.

### 14.11 U.S. Government Rights
The Service is a "commercial item" as defined in FAR 2.101, provided with "restricted rights" as defined in FAR 52.227-19.

## 15. Contact Information

For questions about these Terms, contact us at:

**Encypher**  
Email: legal@encypherai.com  
Website: https://encypherai.com

For technical support:  
Email: support@encypherai.com

For privacy inquiries:  
Email: privacy@encypherai.com

For abuse reports:  
Email: abuse@encypherai.com

---

**By using the Encypher Enterprise API, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.**
