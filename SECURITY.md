# Security Policy

Encypher takes the security of the C2PA Text Standard and its reference implementations seriously.

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please do **not** open a public issue.

Instead, please email **security@encypherai.com**.

We will acknowledge your report within 48 hours and provide an estimated timeline for a fix.

## Scope

This policy applies to:
- The C2PA Text Embedding Specification (`Manifests_Text.adoc`) logic.
- The reference implementations in this repository (Python, TypeScript, Rust, Go).
- The parsing and verification logic associated with the wrapper.

## Non-Scope

- Issues related to the underlying cryptographic primitives (Ed25519, SHA-256) should be reported to the respective library maintainers unless the issue is in our usage of them.
- Issues with the C2PA specification itself should be reported to the [C2PA Working Group](https://c2pa.org).
