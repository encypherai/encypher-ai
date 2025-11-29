# EncypherAI Feature Matrix by Tier

**Last Updated**: November 28, 2025  
**Version**: 1.0

This document provides a comprehensive breakdown of all EncypherAI features organized by subscription tier.

---

## 📊 Tier Overview

| Tier | Price | Target Audience | Key Value Proposition |
|------|-------|-----------------|----------------------|
| **Free** | $0/month | Developers, hobbyists | Basic content authentication |
| **Professional** | $49/month | Small teams, startups | Advanced policies, team features |
| **Business** | $199/month | Growing companies | Multi-org, webhooks, priority support |
| **Enterprise** | Custom | Large organizations | Full platform, custom integrations |

---

## 🔐 Authentication & Access

| Feature | Free | Pro | Business | Enterprise |
|---------|:----:|:---:|:--------:|:----------:|
| Email/Password Login | ✅ | ✅ | ✅ | ✅ |
| OAuth (Google) | ✅ | ✅ | ✅ | ✅ |
| OAuth (GitHub) | ✅ | ✅ | ✅ | ✅ |
| Password Reset Flow | ✅ | ✅ | ✅ | ✅ |
| Session Management | ✅ | ✅ | ✅ | ✅ |
| Two-Factor Authentication (2FA) | ❌ | ✅ | ✅ | ✅ |
| SSO (SAML/OIDC) | ❌ | ❌ | ❌ | ✅ |
| Custom Identity Provider | ❌ | ❌ | ❌ | ✅ |

---

## 🔑 API Key Management

| Feature | Free | Pro | Business | Enterprise |
|---------|:----:|:---:|:--------:|:----------:|
| Generate API Keys | ✅ (1) | ✅ (5) | ✅ (25) | ✅ (Unlimited) |
| View/Revoke Keys | ✅ | ✅ | ✅ | ✅ |
| Key Permissions (Scopes) | Basic | ✅ | ✅ | ✅ |
| Key Rotation | ❌ | ✅ | ✅ | ✅ |
| Key Expiration Settings | ❌ | ✅ | ✅ | ✅ |
| Usage Tracking per Key | ❌ | ✅ | ✅ | ✅ |
| Export Keys (CSV) | ❌ | ✅ | ✅ | ✅ |

---

## ✍️ Content Signing

| Feature | Free | Pro | Business | Enterprise |
|---------|:----:|:---:|:--------:|:----------:|
| Ed25519 Signatures | ✅ | ✅ | ✅ | ✅ |
| C2PA-Compliant Manifests | ✅ | ✅ | ✅ | ✅ |
| Unicode Metadata Embedding | ✅ | ✅ | ✅ | ✅ |
| Batch Signing | ❌ | ✅ (100/batch) | ✅ (1000/batch) | ✅ (Unlimited) |
| Streaming Support | ❌ | ✅ | ✅ | ✅ |
| Custom Metadata Fields | ❌ | ✅ | ✅ | ✅ |
| Merkle Tree Encoding | ❌ | ❌ | ❌ | ✅ |
| Minimal Signed Embeddings | ❌ | ❌ | ❌ | ✅ |

---

## ✔️ Verification

| Feature | Free | Pro | Business | Enterprise |
|---------|:----:|:---:|:--------:|:----------:|
| Signature Verification | ✅ | ✅ | ✅ | ✅ |
| Tampering Detection | ✅ | ✅ | ✅ | ✅ |
| Metadata Extraction | ✅ | ✅ | ✅ | ✅ |
| Batch Verification | ❌ | ✅ | ✅ | ✅ |
| Public Verification Page | ❌ | ✅ | ✅ | ✅ |
| Verification API | ✅ | ✅ | ✅ | ✅ |
| Source Attribution | ❌ | ❌ | ❌ | ✅ |
| Plagiarism Detection | ❌ | ❌ | ❌ | ✅ |

---

## 📊 Dashboard Features

| Feature | Free | Pro | Business | Enterprise |
|---------|:----:|:---:|:--------:|:----------:|
| Usage Overview | ✅ | ✅ | ✅ | ✅ |
| API Call Statistics | ✅ | ✅ | ✅ | ✅ |
| Documents Signed Counter | ✅ | ✅ | ✅ | ✅ |
| Verifications Counter | ✅ | ✅ | ✅ | ✅ |
| Success Rate Metrics | ✅ | ✅ | ✅ | ✅ |
| Time Range Filtering | 7 days | 30 days | 90 days | Custom |
| Export Analytics (CSV) | ❌ | ✅ | ✅ | ✅ |
| Activity Feed | ❌ | ✅ | ✅ | ✅ |
| Audit Logs | ❌ | ❌ | ✅ | ✅ |

---

## 👥 Team & Organization

| Feature | Free | Pro | Business | Enterprise |
|---------|:----:|:---:|:--------:|:----------:|
| Single User | ✅ | ✅ | ✅ | ✅ |
| Team Members | ❌ | ✅ (5) | ✅ (25) | ✅ (Unlimited) |
| Role-Based Access Control | ❌ | Basic | ✅ | ✅ |
| Team Invitations | ❌ | ✅ | ✅ | ✅ |
| Multiple Organizations | ❌ | ❌ | ✅ | ✅ |
| Organization Switcher | ❌ | ❌ | ✅ | ✅ |
| Custom Roles | ❌ | ❌ | ❌ | ✅ |
| Directory Integration (LDAP/AD) | ❌ | ❌ | ❌ | ✅ |

---

## 🔔 Notifications & Webhooks

| Feature | Free | Pro | Business | Enterprise |
|---------|:----:|:---:|:--------:|:----------:|
| Email Notifications | ✅ | ✅ | ✅ | ✅ |
| In-App Notifications | ✅ | ✅ | ✅ | ✅ |
| Notification Center | ✅ | ✅ | ✅ | ✅ |
| Webhooks | ❌ | ❌ | ✅ | ✅ |
| Webhook Event Types | - | - | 5 | Unlimited |
| SMS Notifications | ❌ | ❌ | ❌ | ✅ |
| Slack Integration | ❌ | ❌ | ✅ | ✅ |
| Custom Webhook Headers | ❌ | ❌ | ❌ | ✅ |

---

## 🎨 User Experience

| Feature | Free | Pro | Business | Enterprise |
|---------|:----:|:---:|:--------:|:----------:|
| Responsive Design | ✅ | ✅ | ✅ | ✅ |
| Mobile Navigation | ✅ | ✅ | ✅ | ✅ |
| Dark Mode | ✅ | ✅ | ✅ | ✅ |
| Command Palette (Cmd+K) | ✅ | ✅ | ✅ | ✅ |
| Onboarding Flow | ✅ | ✅ | ✅ | ✅ |
| Keyboard Shortcuts | ✅ | ✅ | ✅ | ✅ |
| Custom Branding | ❌ | ❌ | ❌ | ✅ |
| White-Label Dashboard | ❌ | ❌ | ❌ | ✅ |

---

## 💳 Billing & Subscriptions

| Feature | Free | Pro | Business | Enterprise |
|---------|:----:|:---:|:--------:|:----------:|
| Self-Service Billing | ✅ | ✅ | ✅ | ❌ |
| Credit Card Payments | ✅ | ✅ | ✅ | ✅ |
| Invoice Billing | ❌ | ❌ | ✅ | ✅ |
| Annual Discount | - | 20% | 20% | Custom |
| Usage-Based Billing | ❌ | ❌ | ✅ | ✅ |
| Custom Contracts | ❌ | ❌ | ❌ | ✅ |
| Volume Discounts | ❌ | ❌ | ❌ | ✅ |

---

## 🛠️ CLI Tools

| Feature | Free | Pro | Business | Enterprise |
|---------|:----:|:---:|:--------:|:----------:|
| Audit Log CLI | ✅ | ✅ | ✅ | ✅ |
| CSV Report Generation | ✅ | ✅ | ✅ | ✅ |
| Policy Validator CLI | ❌ | ✅ | ✅ | ✅ |
| Custom Policy Schemas | ❌ | ✅ | ✅ | ✅ |
| Trusted Signers Config | ❌ | ✅ | ✅ | ✅ |
| CI/CD Integration | ❌ | ❌ | ✅ | ✅ |

---

## 🔌 Integrations

| Feature | Free | Pro | Business | Enterprise |
|---------|:----:|:---:|:--------:|:----------:|
| REST API Access | ✅ | ✅ | ✅ | ✅ |
| Python SDK | ✅ | ✅ | ✅ | ✅ |
| WordPress Plugin | ❌ | ✅ | ✅ | ✅ |
| Framework Wrappers | ❌ | ❌ | ❌ | ✅ |
| Custom Integrations | ❌ | ❌ | ❌ | ✅ |
| Dedicated Support | ❌ | ❌ | ❌ | ✅ |

---

## 📈 API Rate Limits

| Metric | Free | Pro | Business | Enterprise |
|--------|:----:|:---:|:--------:|:----------:|
| API Calls/Month | 1,000 | 50,000 | 500,000 | Custom |
| Documents Signed/Month | 100 | 10,000 | 100,000 | Custom |
| Verifications/Month | 500 | 25,000 | 250,000 | Custom |
| Requests/Second | 1 | 10 | 50 | Custom |
| Batch Size | 1 | 100 | 1,000 | Custom |

---

## 🆘 Support

| Feature | Free | Pro | Business | Enterprise |
|---------|:----:|:---:|:--------:|:----------:|
| Documentation | ✅ | ✅ | ✅ | ✅ |
| Community Forum | ✅ | ✅ | ✅ | ✅ |
| Email Support | ❌ | ✅ | ✅ | ✅ |
| Priority Support | ❌ | ❌ | ✅ | ✅ |
| Dedicated Account Manager | ❌ | ❌ | ❌ | ✅ |
| SLA Guarantee | ❌ | ❌ | 99.9% | 99.99% |
| Phone Support | ❌ | ❌ | ❌ | ✅ |
| On-Site Training | ❌ | ❌ | ❌ | ✅ |

---

## 🔒 Security & Compliance

| Feature | Free | Pro | Business | Enterprise |
|---------|:----:|:---:|:--------:|:----------:|
| TLS Encryption | ✅ | ✅ | ✅ | ✅ |
| Data Encryption at Rest | ✅ | ✅ | ✅ | ✅ |
| SOC 2 Compliance | ❌ | ❌ | ✅ | ✅ |
| GDPR Compliance | ✅ | ✅ | ✅ | ✅ |
| HIPAA Compliance | ❌ | ❌ | ❌ | ✅ |
| Custom Data Retention | ❌ | ❌ | ✅ | ✅ |
| Audit Trail | ❌ | ❌ | ✅ | ✅ |
| Penetration Testing Reports | ❌ | ❌ | ❌ | ✅ |

---

## Legend

- ✅ = Included
- ❌ = Not Available
- Number = Limit (e.g., "5" means up to 5)
- "Custom" = Negotiable based on contract

---

## Related Documentation

- [README.md](./README.md) - Repository overview
- [MICROSERVICES_FEATURES.md](./MICROSERVICES_FEATURES.md) - Detailed microservice features
- [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) - Full documentation index
- [PRDs/dashboard_enhancements.md](./PRDs/dashboard_enhancements.md) - Dashboard feature PRD

---

**Document End**
