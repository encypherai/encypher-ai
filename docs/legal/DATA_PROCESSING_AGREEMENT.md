# Data Processing Agreement (DPA)

**Effective Date:** October 28, 2025

This Data Processing Agreement ("DPA") forms part of the Terms of Service between Encypher ("Processor", "we", "us") and the customer ("Controller", "you", "your") for the provision of the Encypher Enterprise API (the "Service").

This DPA applies to the extent that Encypher processes Personal Data on behalf of the Controller in the course of providing the Service.

## 1. Definitions

**"Affiliate"** means any entity that directly or indirectly controls, is controlled by, or is under common control with a party.

**"Controller"** means the entity that determines the purposes and means of the processing of Personal Data.

**"Data Subject"** means an identified or identifiable natural person whose Personal Data is processed.

**"GDPR"** means Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 on the protection of natural persons with regard to the processing of personal data and on the free movement of such data.

**"Personal Data"** means any information relating to an identified or identifiable natural person that is processed by Encypher on behalf of the Controller.

**"Processing"** means any operation or set of operations performed on Personal Data, including collection, recording, organization, structuring, storage, adaptation, retrieval, consultation, use, disclosure, erasure, or destruction.

**"Processor"** means Encypher, the entity that processes Personal Data on behalf of the Controller.

**"Security Incident"** means any accidental or unlawful destruction, loss, alteration, unauthorized disclosure of, or access to Personal Data.

**"Standard Contractual Clauses" or "SCCs"** means the standard contractual clauses for the transfer of personal data to third countries approved by the European Commission.

**"Sub-processor"** means any third party engaged by Encypher to process Personal Data on behalf of the Controller.

## 2. Scope and Roles

### 2.1 Scope of Processing

This DPA applies to the processing of Personal Data by Encypher in the course of providing the Service, including:

- Content signing and verification services
- Sentence-level tracking and metadata storage
- Certificate management
- API usage logging and analytics

### 2.2 Controller and Processor Roles

- **Controller**: You determine the purposes and means of processing Personal Data
- **Processor**: We process Personal Data only on your documented instructions
- **Independent Controllers**: For certain activities (e.g., billing, security monitoring), we may act as an independent controller

### 2.3 Instructions

We will process Personal Data only:
- As documented in this DPA
- As necessary to provide the Service
- As instructed by you through the Service interface
- As required by applicable law

If we believe an instruction violates applicable law, we will inform you immediately.

## 3. Details of Processing

### 3.1 Subject Matter

Processing of Personal Data necessary to provide content authentication and verification services.

### 3.2 Duration

Processing will continue for the duration of the Service agreement and the applicable retention periods specified in our Privacy Policy.

### 3.3 Nature and Purpose

- **Signing Services**: Generate cryptographic signatures for content
- **Verification Services**: Verify authenticity and integrity of signed content
- **Tracking Services**: Maintain sentence-level provenance records
- **Certificate Management**: Manage SSL.com certificates for digital signatures

### 3.4 Types of Personal Data

- **Content Data**: Text content, document metadata, author information
- **Account Data**: Organization name, email addresses, contact information
- **Usage Data**: API logs, timestamps, IP addresses
- **Technical Data**: User agents, device identifiers

### 3.5 Categories of Data Subjects

- Employees and representatives of the Controller
- End users who view or interact with signed content
- Authors and content creators

## 4. Controller Obligations

### 4.1 Lawful Processing

You represent and warrant that:
- You have a lawful basis for processing Personal Data
- You have provided all necessary notices to Data Subjects
- You have obtained all necessary consents
- Your instructions comply with applicable data protection laws

### 4.2 Controller Instructions

You are responsible for:
- Ensuring your instructions are lawful
- Determining the purposes and means of processing
- Responding to Data Subject requests
- Maintaining records of processing activities

### 4.3 Data Subject Rights

You are responsible for:
- Receiving and responding to Data Subject requests
- Verifying the identity of Data Subjects
- Determining whether to grant or deny requests

We will assist you in responding to Data Subject requests as described in Section 7.

## 5. Processor Obligations

### 5.1 Processing Instructions

We will:
- Process Personal Data only on your documented instructions
- Inform you if we believe an instruction violates applicable law
- Not process Personal Data for our own purposes (except as permitted by law)

### 5.2 Confidentiality

We will:
- Ensure that persons authorized to process Personal Data are bound by confidentiality obligations
- Maintain confidentiality of Personal Data
- Not disclose Personal Data to third parties except as permitted by this DPA

### 5.3 Security Measures

We implement appropriate technical and organizational measures to protect Personal Data, as described in Section 6.

### 5.4 Sub-processors

We may engage Sub-processors as described in Section 8.

### 5.5 Data Subject Rights

We will assist you in responding to Data Subject requests as described in Section 7.

### 5.6 Security Incidents

We will notify you of Security Incidents as described in Section 9.

### 5.7 Deletion and Return

We will delete or return Personal Data as described in Section 10.

### 5.8 Audits

We will make available information necessary to demonstrate compliance and allow for audits as described in Section 11.

## 6. Security Measures

### 6.1 Technical Measures

**Encryption:**
- TLS 1.3 for data in transit
- AES-256 encryption for data at rest
- Encrypted backup storage
- Encrypted private key storage (AES-256-GCM)

**Access Controls:**
- API key authentication
- Role-based access control (RBAC)
- Multi-factor authentication for administrative access
- Principle of least privilege
- Regular access reviews

**Network Security:**
- Firewall protection
- Intrusion detection and prevention systems (IDS/IPS)
- DDoS mitigation
- Network segmentation
- VPN for administrative access

**Application Security:**
- Input validation and sanitization
- SQL injection prevention
- Cross-site scripting (XSS) prevention
- Cross-site request forgery (CSRF) protection
- Regular security updates and patches

### 6.2 Organizational Measures

**Policies and Procedures:**
- Information security policy
- Incident response plan
- Business continuity plan
- Disaster recovery plan
- Data retention and deletion policy

**Personnel Security:**
- Background checks for employees with access to Personal Data
- Confidentiality agreements
- Security awareness training
- Regular security training updates

**Physical Security:**
- Secure data centers (Railway infrastructure)
- Physical access controls
- Video surveillance
- Environmental controls (fire suppression, climate control)

**Monitoring and Logging:**
- 24/7 security monitoring
- Centralized logging
- Audit trail of access to Personal Data
- Automated alerting for suspicious activity

**Vulnerability Management:**
- Regular vulnerability scanning
- Penetration testing (annual)
- Security patch management
- Secure software development lifecycle

**Backup and Recovery:**
- Automated daily backups
- Point-in-time recovery capability
- Backup encryption
- Regular backup testing
- Geographically distributed backups

### 6.3 Certifications and Compliance

We maintain compliance with:
- SOC 2 Type II (in progress)
- ISO 27001 (planned)
- GDPR requirements
- CCPA requirements

### 6.4 Security Reviews

We conduct:
- Annual third-party security audits
- Quarterly internal security reviews
- Continuous security monitoring
- Regular penetration testing

## 7. Data Subject Rights

### 7.1 Assistance Obligation

We will provide reasonable assistance to enable you to respond to Data Subject requests, including:

- **Right of Access**: Provide information about Personal Data we process
- **Right to Rectification**: Correct inaccurate Personal Data
- **Right to Erasure**: Delete Personal Data (subject to legal retention requirements)
- **Right to Restriction**: Restrict processing of Personal Data
- **Right to Data Portability**: Export Personal Data in machine-readable format
- **Right to Object**: Cease processing for certain purposes

### 7.2 Response Time

We will respond to your requests for assistance within:
- **Urgent requests**: 24 hours
- **Standard requests**: 5 business days

### 7.3 Fees

Assistance with Data Subject requests is included in the Service at no additional charge, except for:
- Manifestly unfounded or excessive requests
- Requests requiring significant custom development

We will notify you of any fees before performing work.

### 7.4 Direct Requests

If we receive a Data Subject request directly, we will:
- Promptly notify you
- Not respond to the Data Subject without your authorization
- Redirect the Data Subject to contact you

## 8. Sub-processors

### 8.1 Authorized Sub-processors

You authorize us to engage the following Sub-processors:

| Sub-processor | Service | Location | Purpose |
|---------------|---------|----------|---------|
| **Railway** | Infrastructure Hosting | United States | Database, application hosting |
| **SSL.com** | Certificate Authority | United States | SSL/TLS certificate issuance |
| **Stripe** | Payment Processing | United States | Billing and payment processing |
| **SendGrid** | Email Delivery | United States | Transactional email delivery |
| **Sentry** | Error Monitoring | United States | Application error tracking |

### 8.2 Sub-processor Obligations

We ensure that Sub-processors:
- Are bound by data protection obligations equivalent to this DPA
- Implement appropriate security measures
- Process Personal Data only for authorized purposes
- Comply with applicable data protection laws

### 8.3 Sub-processor Changes

We will:
- Notify you at least 30 days before adding or replacing a Sub-processor
- Provide information about the Sub-processor
- Allow you to object to the change

If you object to a Sub-processor change:
- You must notify us within 30 days
- We will work with you to find a solution
- If no solution is found, you may terminate the Service

### 8.4 Sub-processor List

An up-to-date list of Sub-processors is available at:  
https://encypherai.com/legal/subprocessors

### 8.5 Liability

We remain fully liable for the acts and omissions of our Sub-processors.

## 9. Security Incidents

### 9.1 Notification

We will notify you without undue delay after becoming aware of a Security Incident, and in any event within 72 hours.

### 9.2 Notification Contents

Our notification will include:
- Description of the Security Incident
- Categories and approximate number of Data Subjects affected
- Categories and approximate number of Personal Data records affected
- Likely consequences of the Security Incident
- Measures taken or proposed to address the Security Incident
- Contact point for more information

### 9.3 Investigation and Remediation

We will:
- Investigate the Security Incident
- Take reasonable steps to mitigate the effects
- Implement measures to prevent recurrence
- Provide updates as the investigation progresses

### 9.4 Cooperation

We will cooperate with you and regulatory authorities in investigating and responding to the Security Incident.

### 9.5 Documentation

We will document all Security Incidents and make documentation available to you upon request.

### 9.6 No Acknowledgment of Fault

Notification of a Security Incident does not constitute an acknowledgment of fault or liability.

## 10. Deletion and Return of Personal Data

### 10.1 Upon Termination

Upon termination of the Service, we will, at your choice:
- Delete all Personal Data, or
- Return all Personal Data to you in a commonly used format

### 10.2 Retention Period

After termination, we will:
- Delete Personal Data within 90 days, except as required by law
- Retain verification records for 7 years (legal compliance requirement)
- Retain audit logs for 2 years (security and compliance requirement)

### 10.3 Certification

Upon request, we will provide written certification that Personal Data has been deleted or returned.

### 10.4 Exceptions

We may retain Personal Data to the extent required by:
- Applicable law
- Court order or legal process
- Legitimate business purposes (e.g., dispute resolution, fraud prevention)

Retained Personal Data will continue to be protected in accordance with this DPA.

## 11. Audits and Inspections

### 11.1 Audit Rights

You have the right to audit our compliance with this DPA, subject to the following conditions:

- **Frequency**: Once per year, unless required by law or following a Security Incident
- **Notice**: At least 30 days' advance written notice
- **Scope**: Limited to information necessary to verify compliance
- **Timing**: During normal business hours
- **Disruption**: Must not unreasonably interfere with our operations

### 11.2 Audit Methods

Audits may be conducted through:
- Review of our SOC 2 Type II report (when available)
- Review of security documentation and policies
- On-site inspection (with advance notice)
- Third-party audit (at your expense)

### 11.3 Confidentiality

You agree to:
- Keep all audit findings confidential
- Use findings only to verify compliance
- Not disclose findings to third parties (except as required by law)

### 11.4 Costs

- **Standard Audits**: No charge for one audit per year
- **Additional Audits**: You bear the costs of additional audits
- **On-site Audits**: You bear travel and accommodation costs

### 11.5 Remediation

If an audit reveals non-compliance, we will:
- Promptly notify you of the findings
- Develop a remediation plan within 30 days
- Implement remediation measures
- Provide updates on remediation progress

## 12. International Data Transfers

### 12.1 Data Transfer Mechanisms

For transfers of Personal Data from the EEA, UK, or Switzerland to the United States, we rely on:

- **Standard Contractual Clauses (SCCs)**: Approved by the European Commission
- **Additional Safeguards**: As required by applicable law

### 12.2 Standard Contractual Clauses

The Standard Contractual Clauses (Module Two: Controller to Processor) are incorporated into this DPA by reference and form an integral part of this agreement.

In the event of any conflict between this DPA and the SCCs, the SCCs shall prevail.

### 12.3 UK and Swiss Transfers

For transfers from the UK or Switzerland, we comply with the UK GDPR and Swiss Federal Act on Data Protection, respectively, and use appropriate transfer mechanisms.

### 12.4 Multi-Region Options

Enterprise customers may request data storage in specific regions:
- **EU Region**: Frankfurt, Germany (GDPR compliant)
- **Asia-Pacific Region**: Singapore

Contact sales@encypherai.com for multi-region deployment options.

### 12.5 Onward Transfers

Sub-processors located outside the EEA, UK, or Switzerland are bound by equivalent data protection obligations, including Standard Contractual Clauses where applicable.

## 13. Liability and Indemnification

### 13.1 Liability Allocation

Each party's liability under this DPA is subject to the limitation of liability provisions in the Terms of Service.

### 13.2 Processor Liability

We are liable for damages caused by our processing of Personal Data only if:
- We have not complied with obligations specifically directed to processors under applicable law, or
- We have acted outside or contrary to your lawful instructions

### 13.3 Controller Liability

You are liable for damages caused by your processing of Personal Data, including:
- Unlawful instructions to us
- Failure to comply with controller obligations
- Failure to respond to Data Subject requests

### 13.4 Indemnification

We will indemnify you against fines and penalties imposed by data protection authorities resulting from our breach of this DPA, except to the extent caused by your actions or instructions.

## 14. Term and Termination

### 14.1 Term

This DPA takes effect on the Effective Date and continues for the duration of the Service agreement.

### 14.2 Termination

This DPA terminates automatically upon termination of the Service agreement.

### 14.3 Survival

The following provisions survive termination:
- Section 5.2 (Confidentiality)
- Section 9 (Security Incidents)
- Section 10 (Deletion and Return)
- Section 13 (Liability and Indemnification)

## 15. General Provisions

### 15.1 Amendments

We may amend this DPA to:
- Comply with changes in applicable law
- Reflect changes in our processing activities
- Incorporate new security measures

We will notify you of material amendments at least 30 days in advance.

### 15.2 Governing Law

This DPA is governed by the same law as the Terms of Service.

### 15.3 Severability

If any provision of this DPA is found invalid or unenforceable, the remaining provisions continue in full force and effect.

### 15.4 Entire Agreement

This DPA, together with the Terms of Service and Privacy Policy, constitutes the entire agreement regarding data processing.

### 15.5 Order of Precedence

In the event of conflict:
1. Standard Contractual Clauses (for EEA, UK, Swiss transfers)
2. This DPA
3. Terms of Service
4. Privacy Policy

## 16. Contact Information

For questions or concerns regarding this DPA:

**Data Protection Officer:**  
Email: dpo@encypherai.com

**Legal Department:**  
Email: legal@encypherai.com

**Security Incidents:**  
Email: security@encypherai.com  
Phone: [Emergency Security Hotline]

**General Inquiries:**  
Website: https://encypherai.com  
Email: support@encypherai.com

---

## Appendix 1: Standard Contractual Clauses

The Standard Contractual Clauses (Module Two: Controller to Processor) approved by the European Commission Decision 2021/914 of 4 June 2021 are incorporated into this DPA by reference.

**Clause 7 (Docking Clause):** Not applicable

**Clause 9 (Use of Sub-processors):**
- Option 2 (General written authorization) applies
- Sub-processors listed in Section 8.1
- Notification period: 30 days

**Clause 11 (Redress):**
- Independent dispute resolution body: [To be specified]

**Clause 17 (Governing Law):**
- Law of Delaware, United States (for non-EEA parties)
- Law of the EU Member State where the Controller is established (for EEA parties)

**Clause 18 (Choice of Forum and Jurisdiction):**
- Courts of Delaware, United States (for non-EEA parties)
- Courts of the EU Member State where the Controller is established (for EEA parties)

---

**By using the Encypher Service, you acknowledge that you have read, understood, and agree to this Data Processing Agreement.**
