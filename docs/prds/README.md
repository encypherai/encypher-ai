# Product Requirements Documents (PRDs)

This directory contains PRDs for implementing the coalition and licensing vision for Encypher's commercial platform.

---

## Vision

Enable small publishers to monetize their content through collective licensing. Free tier users are automatically onboarded into a coalition where their C2PA-signed content is pooled and licensed in bulk to AI companies. Revenue is distributed to members based on usage (70% to publishers, 30% to Encypher).

---

## PRD Index

### Master Roadmap
- **[PRD-MASTER-Coalition-Roadmap.md](./PRD-MASTER-Coalition-Roadmap.md)** - Complete vision, timeline, and success metrics

### Core Infrastructure (P0 - Critical)
1. **[PRD-001: Coalition Infrastructure & Auto-Onboarding](./PRD-001-Coalition-Infrastructure.md)**
   - **Effort**: 4-6 weeks
   - **Status**: Draft
   - **Key Features**: Auto-enrollment, content indexing, coalition stats API
   - **Dependencies**: None

2. **[PRD-002: Licensing Agreement Management](./PRD-002-Licensing-Agreement-Management.md)**
   - **Effort**: 3-4 weeks
   - **Status**: Draft
   - **Key Features**: Agreement CRUD, content access tracking, revenue distribution
   - **Dependencies**: PRD-001

### User Experience (P1 - High)
3. **[PRD-003: WordPress Coalition Integration](./PRD-003-WordPress-Coalition-Integration.md)**
   - **Effort**: 1-2 weeks
   - **Status**: Draft
   - **Key Features**: Coalition widget, revenue display, settings integration
   - **Dependencies**: PRD-001

4. **[PRD-004: Dashboard Coalition Features](./PRD-004-Dashboard-Coalition-Features.md)**
   - **Effort**: 2-3 weeks
   - **Status**: Draft
   - **Key Features**: Coalition dashboard, revenue charts, admin management
   - **Dependencies**: PRD-001

---

## Implementation Timeline

### Phase 1: Foundation (Weeks 1-6)
Build core coalition infrastructure and licensing system
- PRD-001: Coalition Service
- PRD-002: Licensing agreements and revenue engine

### Phase 2: User Experience (Weeks 7-10)
Member-facing features in WordPress and dashboard
- PRD-003: WordPress integration
- PRD-004: Dashboard features

### Phase 3: Launch (Weeks 11-12)
Testing, security audit, and production launch

**Total Estimated Time**: 12-14 weeks

---

## Key Metrics

### Launch Success (30 Days)
- 100% free tier coalition enrollment
- 10K+ signed documents in pool
- 1 AI company agreement signed
- 99.9% system uptime

### Growth Success (90 Days)
- 1,000+ coalition members
- 100K+ documents in pool
- 3 AI company agreements
- $10K+ revenue distributed
- 5% free → Pro conversion rate

---

## Technical Architecture

### New Components
- **Coalition Service** (Port 8009) - Membership, content indexing, licensing
- **Revenue Distribution Engine** - Automated calculation and payouts
- **AI Company API** - Content access for licensed companies

### Integrations
- **Auth Service** - Auto-enrollment on signup
- **Enterprise API** - Content indexing from signed documents
- **Dashboard App** - Coalition UI for members and admins
- **WordPress Plugin** - Coalition stats widget
- **Stripe** - Payment processing

---

## Business Model

### Revenue Split
- **70%** to coalition members (content creators)
- **30%** to Encypher (platform fee)

### Distribution Method
**Usage-Based**: Revenue distributed proportionally based on:
- Number of documents accessed
- Frequency of access
- Content quality metrics (future)

### Minimum Payout
- **$10 USD** threshold
- Monthly payout cycle
- Stripe direct deposit

---

## Customer Journey Alignment

### Small Publisher (Sarah - TechCurrent)
**Before**: Free tier, no monetization, no upgrade incentive  
**After**: Auto-enrolled, earns $14K/year, upgrades to Pro for better split

### Large Publisher (Jennifer - MetroDaily)
**Before**: Reactive legal approach, no licensing infrastructure  
**After**: Proactive formal notices, bulk licensing deals, $30.5M benefit

---

## Dependencies

### Technical
- PostgreSQL database
- Redis caching
- Stripe payment processing
- SendGrid email service

### Business
- At least 1 AI company pilot partner
- Legal review of coalition terms
- Marketing campaign for launch

### External
- Stripe account setup
- Legal counsel review
- AI company partnerships

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| No AI company interest | Proactive outreach, pilot deals, competitive pricing |
| Low content quality | Quality filters, minimum word count requirements |
| Revenue disputes | Transparent tracking, clear terms, audit trail |
| Scalability issues | Design for 100K+ members, load testing |
| Payment failures | Stripe reliability, retry logic, error handling |

---

## Next Steps

1. **Engineering Review** - Review PRDs with engineering team
2. **Legal Review** - Coalition terms and licensing agreements
3. **AI Company Outreach** - Secure 1 pilot partner
4. **Resource Allocation** - Assign engineers to PRD-001
5. **Kickoff Meeting** - Schedule project kickoff

---

## Questions & Feedback

For questions or feedback on these PRDs, please contact:
- **Product**: [Product Manager]
- **Engineering**: [Engineering Lead]
- **Business Development**: [BD Lead]

---

## Document History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-01-04 | 1.0 | Initial PRDs created | Cascade AI |

---

## Related Documentation

- [Enterprise API Documentation](../../enterprise_api/README.md)
- [Services Architecture](../../services/README.md)
- [Dashboard App Documentation](../../dashboard_app/README.md)
- [WordPress Plugin Documentation](../../integrations/wordpress-provenance-plugin/README.md)
- [Feature Gap Analysis](../FEATURE_GAP_ANALYSIS.md)
