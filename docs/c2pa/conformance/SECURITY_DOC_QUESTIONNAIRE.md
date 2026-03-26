# Security Architecture Document -- Questionnaire

Fill in the answers below. I will update the Security Architecture Document with your responses.

---

## P0 -- Submission-blocking

**1. Compliance contact** (C.1.1)
Who should Scott contact for conformance questions?
- Name:
- Email:
- Title:

**2. Hosting platform** (C.2.1, C.2.2, C.2.6)
What platform runs the production Enterprise API?
- [ ] Railway
- [ ] AWS (which services?)
- [ ] Other:

**3. Key generation location** (C.2.2)
Where was the ECC P-256 signing key generated?
- [ ] Operations engineer's local machine (then uploaded to hosting env)
- [ ] In the hosting environment directly
- [ ] Via SSL.com's portal/API
- [ ] Other:

**4. MFA on SSL.com account** (C.2.1)
Is MFA enabled on the SSL.com account used for certificate enrollment?
- [ ] Yes
- [ ] No
- [ ] Not sure

**5. Personnel with production access** (C.2.1, C.2.6)
How many people have access to production secrets/environment?
- Count:
- Roles (e.g., "2 founders, 1 DevOps"):

---

## P1 -- Important for credibility

**6. At-rest encryption for environment variables** (C.2.2)
How does the hosting platform encrypt env vars at rest?
- Mechanism (e.g., AES-256-GCM):
- Or: "Platform default, details unknown"

**7. Key rotation frequency** (C.2.2)
What is the target rotation frequency for the signing key?
- [ ] Annually
- [ ] Aligned with certificate validity period
- [ ] Other:

**8. SSL.com enrollment method** (C.2.1)
How was the certificate obtained from SSL.com?
- [ ] Web portal (manual)
- [ ] ACME protocol
- [ ] API
- [ ] Other:

**9. Secrets management** (C.2.1)
Where are signing keys and secrets stored?
- [ ] Railway encrypted environment variables
- [ ] AWS Secrets Manager
- [ ] Other:

**10. Traefik TLS configuration** (C.2.5)
What TLS settings does the production Traefik reverse proxy use?
- Minimum TLS version (e.g., 1.2):
- Cipher suites (or "Traefik defaults"):

---

## P2 -- Good to have

**11. Dependabot** (C.2.3)
Are Dependabot alerts and/or automated security PRs enabled on the repo?
- [ ] Yes, alerts + auto PRs
- [ ] Yes, alerts only
- [ ] No
- [ ] Not sure

**12. TSA endpoint** (C.2.5)
The current TSA URL is `http://ts.ssl.com` (plain HTTP). Should we switch to an HTTPS endpoint?
- [ ] Keep http://ts.ssl.com (timestamp token is independently signed)
- [ ] Switch to https:// variant if available
- [ ] Other:

---

Once you answer these, I can fill in all 15 TO_BE_CONFIRMED items and the document is submission-ready.
