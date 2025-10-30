# Architecture Decision: Microservices vs Enterprise API

**Decision Date:** October 30, 2025  
**Status:** ✅ Implemented  
**Impact:** High - Affects all customer tiers

---

## 📋 Decision Summary

We maintain **two separate architectural systems** for different customer tiers and use cases:

1. **Core Microservices** - Foundation platform for all tiers
2. **Enterprise API** - Advanced features for enterprise customers only

---

## 🎯 Context

After completing the microservices migration, we needed to decide:
- Should Merkle tree features be integrated into Encoding Service?
- Should Enterprise API remain separate?
- How do we balance user experience vs. licensing control?

---

## ✅ Decision

**Keep separate architectures with clear boundaries:**

### Core Microservices (All Tiers)
**8 Production Services:**
- Auth Service (8001)
- User Service (8002)
- Key Service (8003)
- Encoding Service (8004) - **Basic signing only**
- Verification Service (8005) - **Standard verification only**
- Analytics Service (8006)
- Billing Service (8007)
- Notification Service (8008)

**Features:**
- Basic Ed25519 document signing
- Standard C2PA manifests
- Signature verification
- Tampering detection
- User/team management
- API key management
- Usage analytics
- Billing & subscriptions

### Enterprise API (Enterprise Tier Only)
**Advanced Features:**
- 🔒 Merkle tree encoding
- 🔒 Source attribution
- 🔒 Plagiarism detection
- 🔒 Batch operations
- 🔒 Advanced analytics
- 🔒 Custom integrations

---

## 🤔 Alternatives Considered

### Option 1: Integrate Everything into Encoding Service
**Rejected because:**
- ❌ Harder to enforce enterprise licensing
- ❌ Enterprise code visible in basic deployments
- ❌ Service becomes too complex
- ❌ Can't scale basic and advanced features independently
- ❌ Security risk (proprietary algorithms exposed)

### Option 2: Hybrid Approach (Future Consideration)
**Deferred because:**
- ⏸️ Just completed major migration
- ⏸️ Adds complexity too soon
- ⏸️ Can migrate later if needed
- ⏸️ Current approach is working

---

## ✅ Benefits of Chosen Approach

### Business Benefits
1. **Clear Licensing Enforcement** - Enterprise features protected
2. **Revenue Protection** - Premium features can't leak to lower tiers
3. **Flexible Pricing** - Can price tiers independently
4. **Market Segmentation** - Clear value proposition per tier

### Technical Benefits
1. **Independent Scaling** - Scale basic and advanced separately
2. **Simpler Services** - Each service has single responsibility
3. **Better Security** - Enterprise algorithms isolated
4. **Easier Maintenance** - Separate codebases for different complexity levels
5. **Deployment Flexibility** - Deploy services independently

### Operational Benefits
1. **Clear Boundaries** - Teams know what goes where
2. **Reduced Risk** - Changes to basic features don't affect enterprise
3. **Better Testing** - Can test tiers independently
4. **Monitoring** - Separate metrics for each tier

---

## ⚠️ Trade-offs Accepted

### User Experience
- **Trade-off:** Users need to integrate with two APIs (if using enterprise)
- **Mitigation:** Clear documentation, unified SDK in future

### Code Duplication
- **Trade-off:** Some signing logic exists in both systems
- **Mitigation:** Plan to extract shared library (Phase 2)

### Operational Complexity
- **Trade-off:** More services to maintain
- **Mitigation:** Docker, monitoring, clear documentation

---

## 📊 Feature Breakdown

### Microservices Features

| Feature | Service | Available To |
|---------|---------|--------------|
| Basic Document Signing | Encoding | All tiers |
| Ed25519 Signatures | Encoding | All tiers |
| C2PA Manifests | Encoding | All tiers |
| Signature Verification | Verification | All tiers |
| Tampering Detection | Verification | All tiers |
| JWT Authentication | Auth | All tiers |
| OAuth (Google/GitHub) | Auth | All tiers |
| API Key Management | Key | All tiers |
| User Profiles | User | All tiers |
| Team Management | User | Pro & Enterprise |
| Usage Analytics | Analytics | Pro & Enterprise |
| Subscriptions | Billing | All tiers |
| Email Notifications | Notification | All tiers |

### Enterprise API Features

| Feature | Available To |
|---------|--------------|
| Merkle Tree Encoding | Enterprise only |
| Source Attribution | Enterprise only |
| Plagiarism Detection | Enterprise only |
| Batch Operations | Enterprise only |
| Advanced Analytics | Enterprise only |
| Forensic Analysis | Enterprise only |
| Custom Integrations | Enterprise only |

---

## 🔄 Integration Pattern

```
┌─────────────────────────────────────┐
│         Client Applications         │
└────────────┬────────────────────────┘
             │
        ┌────┴─────┐
        │          │
┌───────▼──┐  ┌────▼──────────┐
│   Core   │  │   Enterprise  │
│Microsvcs │  │      API      │
│          │  │               │
│ • Auth   │  │ • Merkle Tree │
│ • Keys   │  │ • Attribution │
│ • Encode │  │ • Plagiarism  │
│ • Verify │  │ • Batch Ops   │
│ • etc.   │  │               │
└──────────┘  └───────────────┘
     │              │
     └──────┬───────┘
            │
    ┌───────▼────────┐
    │   PostgreSQL   │
    │   + Redis      │
    └────────────────┘
```

**Customer Usage:**
- **Free Tier:** → Core Microservices only
- **Pro Tier:** → Core Microservices only (higher limits)
- **Enterprise Tier:** → Core Microservices + Enterprise API

---

## 🚀 Future Migration Path

### Phase 1 (Current) ✅
- Separate microservices and Enterprise API
- Clear boundaries
- Production ready

### Phase 2 (Planned)
- Extract shared crypto library
- Both systems use shared library
- Reduce code duplication

### Phase 3 (Future)
- Consider hybrid approach if needed
- Enterprise service extends base
- Single API endpoint option

---

## 📚 Related Documentation

- [Main README](../../README.md#️-architecture-decision-microservices-vs-enterprise-api)
- [Microservices Progress](./MICROSERVICES_PROGRESS.md)
- [Migration Complete](./MIGRATION_COMPLETE.md)
- [Enterprise API README](../../enterprise_api/README.md)

---

## 🎯 Success Metrics

**Licensing Control:**
- ✅ Enterprise features cannot be accessed without license
- ✅ Clear tier boundaries enforced

**Performance:**
- ✅ Basic services remain fast and lightweight
- ✅ Enterprise features can scale independently

**Security:**
- ✅ Enterprise algorithms protected
- ✅ No proprietary code in basic tier

**Maintainability:**
- ✅ Clear separation of concerns
- ✅ Easy to understand which features go where

---

## 👥 Decision Makers

- **Architecture Team:** Approved separation approach
- **Product Team:** Confirmed tier requirements
- **Engineering Team:** Validated technical feasibility
- **Business Team:** Approved licensing model

---

<div align="center">

**Decision Status: ✅ IMPLEMENTED**

**Last Updated:** October 30, 2025

[Main README](../../README.md) • [Architecture Docs](./README.md)

</div>
