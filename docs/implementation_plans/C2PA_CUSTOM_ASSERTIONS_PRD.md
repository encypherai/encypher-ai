# C2PA Custom Assertions & Complete Actions Support - PRD

**Product Requirements Document**  
**Project Code:** C2PA-CUSTOM-2024  
**Version:** 1.0  
**Date:** November 3, 2025  
**Status:** Planning → Implementation

---

## Executive Summary

Extend the Enterprise API to support all C2PA 2.2 standard actions and enable custom assertions with validation, making it the most comprehensive C2PA implementation for text content. This positions Encypher as the enterprise-grade solution for news organizations, legal firms, publishers, and academic institutions requiring advanced content provenance.

---

## Business Value

### Target Customers & Use Cases

#### 1. News Organizations
**Pain Points:**
- Need to embed fact-checking results
- Track editorial workflows
- Prevent AI training on copyrighted content
- Attribute sources properly

**Value Delivered:**
- `c2pa.claim_review.v1` for fact-checking integration
- `c2pa.training-mining.v1` for AI permissions
- Custom editorial assertions
- Complete action tracking (published, edited, redacted)

**Revenue Impact:** $50K-200K ARR per major news org

#### 2. Legal Firms
**Pain Points:**
- Need tamper-evident legal documents
- Track document lifecycle
- Custom metadata for case management
- Multi-party signing workflows

**Value Delivered:**
- Custom legal assertions (case numbers, jurisdictions)
- Complete audit trail with all C2PA actions
- Multi-signature support
- Court-admissible provenance

**Revenue Impact:** $100K-500K ARR per large firm

#### 3. Publishers
**Pain Points:**
- Copyright management
- License tracking
- Translation provenance
- AI training permissions

**Value Delivered:**
- `c2pa.translated` action tracking
- `c2pa.training-mining.v1` assertions
- Schema.org metadata integration
- Rich content metadata

**Revenue Impact:** $30K-150K ARR per publisher

#### 4. Academic Institutions
**Pain Points:**
- Research data provenance
- Citation tracking
- Peer review metadata
- Collaboration attribution

**Value Delivered:**
- Custom academic assertions
- Complete research workflow tracking
- Multi-author signing
- Data lineage tracking

**Revenue Impact:** $20K-100K ARR per institution

---

## Task List

### 1.0 Foundation & Architecture
- [ ] 1.1 Design C2PA validation service architecture
- [ ] 1.2 Create database schema for custom schemas and templates
- [ ] 1.3 Set up schema registry infrastructure
- [ ] 1.4 Design API endpoints for custom assertions

### 2.0 Complete C2PA Actions Support
- [ ] 2.1 Implement all standard C2PA actions
  - [ ] 2.1.1 `c2pa.opened` - Document opened/viewed
  - [ ] 2.1.2 `c2pa.placed` - Asset placed into another
  - [ ] 2.1.3 `c2pa.published` - Content published
  - [ ] 2.1.4 `c2pa.redacted` - Content redacted
  - [ ] 2.1.5 `c2pa.transcoded` - Format conversion
  - [ ] 2.1.6 `c2pa.translated` - Language translation
  - [ ] 2.1.7 `c2pa.cropped` - Cropping operation
  - [ ] 2.1.8 `c2pa.filtered` - Filter/effect applied
  - [ ] 2.1.9 `c2pa.resized` - Dimension changes
  - [ ] 2.1.10 `c2pa.orientation` - Rotation/flip
  - [ ] 2.1.11 `c2pa.color_adjustments` - Color correction
  - [ ] 2.1.12 `c2pa.drawing` - Drawing/annotation
  - [ ] 2.1.13 `c2pa.repackaged` - Container format change
- [ ] 2.2 Add action metadata support
- [ ] 2.3 Update API schema to accept any C2PA action
- [ ] 2.4 Add action validation

### 3.0 Standard C2PA Assertions
- [ ] 3.1 Location assertion (`c2pa.location.v1`)
  - [ ] 3.1.1 GPS coordinates support
  - [ ] 3.1.2 Location name and address
  - [ ] 3.1.3 Altitude support
- [ ] 3.2 AI Training/Mining assertion (`c2pa.training-mining.v1`)
  - [ ] 3.2.1 Training permission flag
  - [ ] 3.2.2 Inference permission flag
  - [ ] 3.2.3 Mining permission flag
  - [ ] 3.2.4 License constraints
- [ ] 3.3 Claim Review assertion (`c2pa.claim_review.v1`)
  - [ ] 3.3.1 Claim reviewed field
  - [ ] 3.3.2 Rating/verdict
  - [ ] 3.3.3 Reviewer information
  - [ ] 3.3.4 Review URL
- [ ] 3.4 Thumbnail assertion (`c2pa.thumbnail.v1`)
  - [ ] 3.4.1 Base64 image support
  - [ ] 3.4.2 Format validation
  - [ ] 3.4.3 Size limits
- [ ] 3.5 Schema.org Creative Work (`c2pa.schema-org.CreativeWork.v1`)
  - [ ] 3.5.1 NewsArticle type
  - [ ] 3.5.2 Author metadata
  - [ ] 3.5.3 Publisher metadata
  - [ ] 3.5.4 Date fields

### 4.0 Custom Assertion Framework
- [ ] 4.1 Schema validation service
  - [ ] 4.1.1 JSON Schema validator
  - [ ] 4.1.2 Required field checking
  - [ ] 4.1.3 Type validation
  - [ ] 4.1.4 Format validation (dates, URIs, etc.)
- [ ] 4.2 Schema registry
  - [ ] 4.2.1 Database models for schemas
  - [ ] 4.2.2 CRUD operations for schemas
  - [ ] 4.2.3 Version management
  - [ ] 4.2.4 Namespace ownership
- [ ] 4.3 Custom namespace support
  - [ ] 4.3.1 Namespace registration
  - [ ] 4.3.2 Namespace validation
  - [ ] 4.3.3 Organization-specific namespaces
- [ ] 4.4 API endpoints
  - [ ] 4.4.1 `POST /api/v1/enterprise/c2pa/schemas` - Register schema
  - [ ] 4.4.2 `GET /api/v1/enterprise/c2pa/schemas` - List schemas
  - [ ] 4.4.3 `GET /api/v1/enterprise/c2pa/schemas/{id}` - Get schema
  - [ ] 4.4.4 `PUT /api/v1/enterprise/c2pa/schemas/{id}` - Update schema
  - [ ] 4.4.5 `DELETE /api/v1/enterprise/c2pa/schemas/{id}` - Delete schema
  - [ ] 4.4.6 `POST /api/v1/enterprise/c2pa/validate` - Validate assertion

### 5.0 Assertion Templates
- [ ] 5.1 Template system design
- [ ] 5.2 Pre-built templates
  - [ ] 5.2.1 News article template
  - [ ] 5.2.2 Legal document template
  - [ ] 5.2.3 Academic paper template
  - [ ] 5.2.4 Publisher content template
- [ ] 5.3 Custom template creation
- [ ] 5.4 Template API endpoints
  - [ ] 5.4.1 `GET /api/v1/enterprise/c2pa/templates` - List templates
  - [ ] 5.4.2 `GET /api/v1/enterprise/c2pa/templates/{name}` - Get template
  - [ ] 5.4.3 `POST /api/v1/enterprise/c2pa/templates` - Create template
  - [ ] 5.4.4 `PUT /api/v1/enterprise/c2pa/templates/{id}` - Update template
  - [ ] 5.4.5 `DELETE /api/v1/enterprise/c2pa/templates/{id}` - Delete template

### 6.0 Enhanced Ingredient Support
- [ ] 6.1 Multiple relationship types
  - [ ] 6.1.1 `componentOf` relationship
  - [ ] 6.1.2 `derivedFrom` relationship
  - [ ] 6.1.3 `alternateOf` relationship
  - [ ] 6.1.4 `supplementOf` relationship
- [ ] 6.2 Ingredient metadata
  - [ ] 6.2.1 Thumbnail support
  - [ ] 6.2.2 Format information
  - [ ] 6.2.3 Size information
- [ ] 6.3 Update embedding service to support new relationships

### 7.0 Integration with Existing Systems
- [ ] 7.1 Update `encode-with-embeddings` endpoint
  - [ ] 7.1.1 Accept `custom_assertions` parameter
  - [ ] 7.1.2 Validate custom assertions
  - [ ] 7.1.3 Embed validated assertions
- [ ] 7.2 Update encypher-ai library
  - [ ] 7.2.1 Support custom assertions in manifest builder
  - [ ] 7.2.2 Maintain C2PA 2.2 compliance
- [ ] 7.3 Update verification endpoint
  - [ ] 7.3.1 Extract custom assertions
  - [ ] 7.3.2 Validate against registered schemas
  - [ ] 7.3.3 Return validation results

### 8.0 Database & Migrations
- [ ] 8.1 Create `c2pa_schemas` table
- [ ] 8.2 Create `c2pa_assertion_templates` table
- [ ] 8.3 Add indexes for performance
- [ ] 8.4 Create Alembic migrations
- [ ] 8.5 Add foreign key constraints

### 9.0 API Documentation
- [ ] 9.1 OpenAPI/Swagger specs for new endpoints
- [ ] 9.2 Example requests/responses
- [ ] 9.3 Schema registration guide
- [ ] 9.4 Custom assertion guide
- [ ] 9.5 Template usage guide

### 10.0 Testing
- [ ] 10.1 Unit tests for validation service
- [ ] 10.2 Integration tests for schema registry
- [ ] 10.3 End-to-end tests for custom assertions
- [ ] 10.4 C2PA compliance validation
- [ ] 10.5 Performance testing
- [ ] 10.6 Security testing (namespace ownership)

### 11.0 WordPress Plugin Integration
- [ ] 11.1 UI for selecting C2PA actions
- [ ] 11.2 UI for adding custom assertions
- [ ] 11.3 Template selector
- [ ] 11.4 Assertion preview
- [ ] 11.5 Validation feedback

### 12.0 Documentation & Examples
- [ ] 12.1 Update Enterprise API README
- [ ] 12.2 Create custom assertions guide
- [ ] 12.3 Industry-specific examples
  - [ ] 12.3.1 News organization example
  - [ ] 12.3.2 Legal firm example
  - [ ] 12.3.3 Publisher example
  - [ ] 12.3.4 Academic example
- [ ] 12.4 Video tutorials
- [ ] 12.5 Migration guide for existing customers

---

## Notes

### Technical Considerations

**Schema Validation:**
- Use `jsonschema` library for Python validation
- Cache compiled schemas for performance
- Support JSON Schema Draft 7 or later

**Security:**
- Namespace ownership verification
- Rate limiting on schema registration
- Validation of malicious schemas
- Size limits on custom data

**Performance:**
- Index on namespace and label
- Cache frequently used schemas
- Lazy load schema validation
- Batch validation for multiple assertions

**Backwards Compatibility:**
- Existing endpoints continue to work
- Custom assertions are optional
- Default to standard C2PA behavior

### C2PA Compliance

All implementations must:
- Follow C2PA 2.2 specification exactly
- Use official JSON-LD contexts
- Maintain signature integrity
- Support standard assertion formats
- Validate against C2PA schemas

### Pricing Strategy

**Professional Tier:**
- Standard C2PA actions (all 13 actions)
- Standard assertions (location, AI permissions)
- 5 custom schemas per organization

**Enterprise Tier:**
- All Professional features
- Unlimited custom schemas
- Custom namespaces
- Assertion templates
- Multi-signature support
- Priority validation service

---

## Current Goal

**Start with:** 2.0 Complete C2PA Actions Support - Implement all standard actions and action metadata

---

## Success Metrics

### Technical Metrics
- ✅ All 13 C2PA actions supported
- ✅ 100% C2PA 2.2 compliance
- ✅ <50ms validation time for custom assertions
- ✅ Support 1000+ custom schemas per organization

### Business Metrics
- 🎯 5 enterprise customers using custom assertions (Q1 2026)
- 🎯 $500K ARR from advanced C2PA features (Q2 2026)
- 🎯 50% of enterprise customers using AI permissions (Q2 2026)
- 🎯 Industry recognition as most complete C2PA implementation

### Customer Satisfaction
- 🎯 NPS score >50 for enterprise features
- 🎯 <24hr response time for custom schema validation issues
- 🎯  90% customer retention for enterprise tier

---

## Dependencies

- C2PA 2.2 specification
- jsonschema library
- PostgreSQL JSONB support
- encypher-ai library updates
- WordPress plugin updates (optional)

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| C2PA spec changes | High | Low | Monitor C2PA working group, version schemas |
| Performance issues with validation | Medium | Medium | Caching, lazy loading, optimization |
| Customer misuse of custom schemas | Medium | Medium | Validation, rate limiting, review process |
| Complexity for users | High | High | Templates, examples, excellent documentation |
| Security vulnerabilities | High | Low | Security review, penetration testing |

---

## Timeline

**Phase 1 (Weeks 1-2):** Foundation & Standard Actions  
**Phase 2 (Weeks 3-4):** Standard Assertions  
**Phase 3 (Weeks 5-6):** Custom Assertion Framework  
**Phase 4 (Weeks 7-8):** Templates & Integration  
**Phase 5 (Weeks 9-10):** Testing & Documentation  

**Total Duration:** 10 weeks  
**Target Completion:** January 15, 2026

---

## Stakeholders

**Engineering:** Full-stack implementation  
**Product:** Feature prioritization, customer feedback  
**Sales:** Enterprise customer outreach  
**Marketing:** Positioning as most complete C2PA solution  
**Support:** Documentation, customer onboarding  

---

## Approval

**Product Manager:** ___________________ Date: ___________  
**Engineering Lead:** ___________________ Date: ___________  
**CTO:** ___________________ Date: ___________
