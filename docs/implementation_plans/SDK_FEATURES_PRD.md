# SDK & API Features - Product Requirements Document

**Version:** 1.0  
**Date:** October 29, 2025  
**Status:** Phase 1 Complete ✅

## Executive Summary

This PRD defines essential features for the Encypher Enterprise SDK and API to support publishers, news organizations, and content creators. All features align with our WordPress plugin integration and provide comprehensive content signing capabilities.

## Work Breakdown Structure

### 1.0 Incremental Signing

**Priority:** P0 (Essential for V1)  
**Effort:** 2 weeks  
**Dependencies:** None

#### 1.1 State Management
- [x] 1.1.1 Create state file format (`.encypher-state.json`)
- [x] 1.1.2 Implement file hash tracking (SHA-256)
- [x] 1.1.3 Add state persistence and loading
- [x] 1.1.4 Handle state file corruption/recovery

#### 1.2 Change Detection
- [x] 1.2.1 Compare current file hash with stored hash
- [x] 1.2.2 Detect new files (not in state)
- [x] 1.2.3 Detect modified files (hash mismatch)
- [x] 1.2.4 Detect deleted files (in state but not on disk)

#### 1.3 SDK Implementation
- [x] 1.3.1 Add `sign_directory_incremental()` method to `RepositorySigner`
- [x] 1.3.2 Add `--incremental` flag to CLI
- [x] 1.3.3 Add `--force-resign` option to override incremental
- [x] 1.3.4 Update documentation and examples

#### 1.4 API Support
- [x] 1.4.1 No API changes needed (uses existing `/sign` endpoint)
- [x] 1.4.2 Document best practices for incremental signing

**Success Criteria:**
- Only changed files are signed on subsequent runs
- State file correctly tracks all signed files
- 10x faster for large repos with few changes

---

### 2.0 Git Integration

**Priority:** P0 (Essential for V1)  
**Effort:** 1.5 weeks  
**Dependencies:** None

#### 2.1 Git Metadata Extraction
- [x] 2.1.1 Extract author from git commit history
- [x] 2.1.2 Extract creation date from first commit
- [x] 2.1.3 Extract last modified date from latest commit
- [x] 2.1.4 Extract contributors list
- [x] 2.1.5 Extract current branch name
- [x] 2.1.6 Extract commit SHA

#### 2.2 SDK Implementation
- [x] 2.2.1 Create `GitMetadataProvider` class
- [x] 2.2.2 Add `gitpython` as optional dependency
- [x] 2.2.3 Add `--use-git-metadata` CLI flag
- [x] 2.2.4 Handle non-git repositories gracefully

#### 2.3 API Support
- [x] 2.3.1 Accept git metadata in `custom` field of sign request
- [x] 2.3.2 Store git metadata in database
- [x] 2.3.3 Return git metadata in verification response

**Success Criteria:**
- Automatically extracts author/date from git
- Works with both local and remote repositories
- Gracefully handles non-git directories

---

### 3.0 Frontmatter Parsing

**Priority:** P0 (Essential for V1)  
**Effort:** 1 week  
**Dependencies:** None

#### 3.1 Parser Implementation
- [x] 3.1.1 YAML frontmatter parser
- [x] 3.1.2 TOML frontmatter parser
- [x] 3.1.3 JSON frontmatter parser
- [x] 3.1.4 Auto-detect frontmatter format

#### 3.2 Metadata Mapping
- [x] 3.2.1 Map frontmatter fields to `FileMetadata`
- [x] 3.2.2 Support custom field mappings
- [x] 3.2.3 Handle missing/invalid frontmatter

#### 3.3 SDK Implementation
- [x] 3.3.1 Create `FrontmatterMetadataProvider` class
- [x] 3.3.2 Add `pyyaml` and `toml` as optional dependencies
- [x] 3.3.3 Add `--use-frontmatter` CLI flag
- [x] 3.3.4 Support custom field mapping config

#### 3.4 API Support
- [x] 3.4.1 No API changes needed
- [x] 3.4.2 Document frontmatter best practices

**Success Criteria:**
- Parses YAML, TOML, and JSON frontmatter
- Maps common fields (title, author, date, tags)
- Works with Hugo, Jekyll, Next.js, Astro

---

### 4.0 Verification Report Generation

**Priority:** P0 (Essential for V1)  
**Effort:** 1 week  
**Dependencies:** None

#### 4.1 HTML Report Generator
- [x] 4.1.1 Create HTML template for verification report
- [x] 4.1.2 Include verification badges
- [x] 4.1.3 Add metadata display
- [x] 4.1.4 Make mobile-responsive

#### 4.2 Report Formats
- [x] 4.2.1 HTML report
- [x] 4.2.2 Markdown report
- [x] 4.2.3 JSON report (already exists)
- [x] 4.2.4 CSV export

#### 4.3 SDK Implementation
- [x] 4.3.1 Add `generate_verification_report()` function
- [x] 4.3.2 Add `--report-format` CLI option
- [x] 4.3.3 Add templates directory to SDK

#### 4.4 API Support
- [x] 4.4.1 No API changes needed
- [x] 4.4.2 Provide public verification page template

**Success Criteria:**
- Generates shareable HTML reports
- Reports include all verification details
- Reports are SEO-friendly

---

### 5.0 CI/CD Integration

**Priority:** P0 (Essential for V1)  
**Effort:** 1 week  
**Dependencies:** 1.0 (Incremental Signing)

#### 5.1 GitHub Actions
- [x] 5.1.1 Create reusable workflow template
- [x] 5.1.2 Support incremental signing
- [x] 5.1.3 Auto-commit signed files
- [x] 5.1.4 Post verification report as comment

#### 5.2 GitLab CI
- [x] 5.2.1 Create `.gitlab-ci.yml` template
- [x] 5.2.2 Support incremental signing
- [x] 5.2.3 Artifact signed files

#### 5.3 Other CI Systems
- [ ] 5.3.1 Jenkins pipeline example
- [ ] 5.3.2 CircleCI config example
- [ ] 5.3.3 Azure Pipelines example

#### 5.4 SDK Implementation
- [x] 5.4.1 Add `--ci` mode (non-interactive)
- [x] 5.4.2 Add exit codes for CI
- [x] 5.4.3 Add machine-readable output

#### 5.5 API Support
- [x] 5.5.1 Rate limit exemption for CI
- [x] 5.5.2 Batch signing endpoint optimization

**Success Criteria:**
- One-click setup for GitHub Actions
- Automatic signing on every commit
- No manual intervention required

---

### 6.0 Batch Verification

**Priority:** P1 (Should-Have for V1)  
**Effort:** 1 week  
**Dependencies:** None

#### 6.1 Verifier Implementation
- [x] 6.1.1 Create `RepositoryVerifier` class
- [x] 6.1.2 Batch verify all signed files
- [x] 6.1.3 Detect tampered files
- [x] 6.1.4 Generate verification report

#### 6.2 SDK Implementation
- [x] 6.2.1 Add `verify-repo` CLI command
- [x] 6.2.2 Support concurrent verification
- [x] 6.2.3 Add `--fail-on-tampered` option

#### 6.3 API Support
- [x] 6.3.1 Batch verification endpoint (uses existing `/verify`)
- [x] 6.3.2 Accept array of signed texts
- [x] 6.3.3 Return array of verification results
- [x] 6.3.4 Optimize for performance

**Success Criteria:**
- Verify 1000+ files in <30 seconds
- Detect all tampered files
- Generate audit report

---

### 7.0 Content Diff Tracking

**Priority:** P1 (Should-Have for V1.5)  
**Effort:** 1.5 weeks  
**Dependencies:** 1.0 (Incremental Signing)

#### 7.1 Diff Generation
- [x] 7.1.1 Generate unified diff between versions
- [x] 7.1.2 Calculate change statistics
- [x] 7.1.3 Identify added/removed/modified sections

#### 7.2 Version History
- [x] 7.2.1 Track version numbers
- [x] 7.2.2 Link to previous versions
- [x] 7.2.3 Store diff in metadata

#### 7.3 SDK Implementation
- [x] 7.3.1 Add `--track-changes` option
- [x] 7.3.2 Store previous version in state file
- [x] 7.3.3 Include diff in C2PA manifest

#### 7.4 API Support
- [x] 7.4.1 Accept `previous_version` in sign request (SDK ready)
- [x] 7.4.2 Store version history in database (SDK ready)
- [x] 7.4.3 Return version history in verification (SDK ready)

**Success Criteria:**
- Track what changed between versions
- Display edit history to readers
- Maintain version lineage

---

### 8.0 Multi-Language Support

**Priority:** P1 (Should-Have for V1.5)  
**Effort:** 1 week  
**Dependencies:** None

#### 8.1 Language Detection
- [x] 8.1.1 Auto-detect content language
- [x] 8.1.2 Support manual language specification
- [x] 8.1.3 Handle multi-language documents

#### 8.2 Translation Linking
- [x] 8.2.1 Link translated versions
- [x] 8.2.2 Track translation metadata
- [x] 8.2.3 Verify translation authenticity

#### 8.3 SDK Implementation
- [x] 8.3.1 Add `--language` CLI option
- [x] 8.3.2 Add `--detect-language` option
- [x] 8.3.3 Auto-detect from frontmatter

#### 8.4 API Support
- [x] 8.4.1 Accept `language` in sign request (SDK ready)
- [x] 8.4.2 Accept `translations` array (SDK ready)
- [x] 8.4.3 Return language in verification (SDK ready)

**Success Criteria:**
- Support 50+ languages
- Link translated versions
- Maintain provenance across translations

---

### 9.0 Bulk Metadata Updates

**Priority:** P2 (Nice-to-Have for V2)  
**Effort:** 1 week  
**Dependencies:** None

#### 9.1 Update Operations
- [x] 9.1.1 Update metadata without re-signing
- [x] 9.1.2 Batch update multiple documents
- [x] 9.1.3 Validate metadata changes

#### 9.2 SDK Implementation
- [x] 9.2.1 Add `update-metadata` CLI command (SDK ready)
- [x] 9.2.2 Support bulk updates from CSV/JSON
- [x] 9.2.3 Preview changes before applying

#### 9.3 API Support
- [x] 9.3.1 Create `PATCH /api/v1/documents/{id}/metadata` endpoint (SDK ready)
- [x] 9.3.2 Create `POST /api/v1/documents/metadata/batch` endpoint (SDK ready)
- [x] 9.3.3 Validate metadata schema
- [x] 9.3.4 Audit metadata changes

**Success Criteria:**
- Update metadata without re-signing
- Batch update 1000+ documents
- Maintain audit trail

---

### 10.0 Signature Expiration & Renewal

**Priority:** P2 (Nice-to-Have for V2)  
**Effort:** 2 weeks  
**Dependencies:** None

#### 10.1 Expiration Tracking
- [x] 10.1.1 Track certificate expiration dates
- [x] 10.1.2 Detect expiring signatures
- [x] 10.1.3 Send expiration warnings

#### 10.2 Auto-Renewal
- [x] 10.2.1 Auto-renew before expiration
- [x] 10.2.2 Batch renewal for repositories
- [x] 10.2.3 Handle renewal failures

#### 10.3 SDK Implementation
- [x] 10.3.1 Add `check-expiring` CLI command (SDK ready)
- [x] 10.3.2 Add `renew-signatures` CLI command (SDK ready)
- [x] 10.3.3 Add `--auto-renew` option

#### 10.4 API Support
- [x] 10.4.1 Return expiration date in verification (SDK ready)
- [x] 10.4.2 Create renewal endpoint (SDK ready)
- [x] 10.4.3 Send expiration notifications

**Success Criteria:**
- Detect signatures expiring in 30 days
- Auto-renew without manual intervention
- Zero downtime during renewal

---

### 11.0 Analytics & Metrics

**Priority:** P2 (Nice-to-Have for V2)  
**Effort:** 1.5 weeks  
**Dependencies:** None

#### 11.1 Metrics Collection
- [x] 11.1.1 Track signing activity
- [x] 11.1.2 Track verification requests
- [x] 11.1.3 Track API usage
- [x] 11.1.4 Track error rates

#### 11.2 Dashboard Integration
- [x] 11.2.1 Send metrics to analytics service
- [x] 11.2.2 Create dashboard views (Prometheus/Grafana support)
- [x] 11.2.3 Generate usage reports

#### 11.3 SDK Implementation
- [x] 11.3.1 Add `--analytics` option (SDK ready)
- [x] 11.3.2 Track local metrics
- [x] 11.3.3 Export metrics to dashboard

#### 11.4 API Support
- [x] 11.4.1 Create analytics endpoints (SDK ready)
- [x] 11.4.2 Aggregate usage data
- [x] 11.4.3 Generate reports

**Success Criteria:**
- Track all signing/verification activity
- Real-time dashboard updates
- Monthly usage reports

---

### 12.0 Binary File Support

**Priority:** P2 (Nice-to-Have for V2)  
**Effort:** 2 weeks  
**Dependencies:** None

#### 12.1 File Type Support
- [x] 12.1.1 PDF signing
- [x] 12.1.2 DOCX signing
- [x] 12.1.3 Image signing (JPEG, PNG)
- [x] 12.1.4 Video signing (MP4)

#### 12.2 Text Extraction
- [x] 12.2.1 Extract text from PDF
- [x] 12.2.2 Extract text from DOCX
- [x] 12.2.3 Use file hash for images/video

#### 12.3 SDK Implementation
- [x] 12.3.1 Add binary file support to `RepositorySigner` (SDK ready)
- [x] 12.3.2 Add text extraction utilities
- [x] 12.3.3 Support mixed file types

#### 12.4 API Support
- [x] 12.4.1 Accept binary file hashes (SDK ready)
- [x] 12.4.2 Store binary file metadata (SDK ready)
- [x] 12.4.3 Verify binary files (SDK ready)

**Success Criteria:**
- Sign PDF, DOCX, images, video
- Extract text when possible
- Maintain C2PA compliance

---

## API Endpoints Required

### New Endpoints

| Endpoint | Method | Purpose | Priority |
|----------|--------|---------|----------|
| `/api/v1/verify/batch` | POST | Batch verification | P1 |
| `/api/v1/documents/{id}/metadata` | PATCH | Update metadata | P2 |
| `/api/v1/documents/metadata/batch` | POST | Bulk metadata update | P2 |
| `/api/v1/documents/{id}/renew` | POST | Renew signature | P2 |
| `/api/v1/analytics/usage` | GET | Usage metrics | P2 |

### Enhanced Endpoints

| Endpoint | Enhancement | Priority |
|----------|-------------|----------|
| `POST /api/v1/sign` | Accept git metadata, previous version | P0 |
| `POST /api/v1/verify` | Return expiration date, version history | P1 |

---

## SDK Enhancements Required

### New Classes

- `GitMetadataProvider` - Extract metadata from git
- `FrontmatterMetadataProvider` - Parse frontmatter
- `RepositoryVerifier` - Batch verification
- `AnalyticsTracker` - Track metrics

### New CLI Commands

- `encypher verify-repo` - Verify all signed files
- `encypher check-expiring` - Find expiring signatures
- `encypher renew-signatures` - Renew signatures
- `encypher update-metadata` - Update metadata

### New Options

- `--incremental` - Incremental signing
- `--use-git-metadata` - Extract from git
- `--use-frontmatter` - Parse frontmatter
- `--track-changes` - Track version diffs
- `--auto-renew` - Auto-renew signatures

---

## WordPress Plugin Alignment

The WordPress plugin already exists and uses:
- ✅ `POST /api/v1/sign` - Sign posts
- ✅ `POST /api/v1/verify` - Verify posts
- ✅ Settings page for API key configuration
- ✅ Gutenberg sidebar integration
- ✅ Classic Editor meta box

**Plugin Enhancements Needed:**
- Auto-sign on publish (currently manual)
- Bulk sign existing posts
- Display verification badge on frontend
- Show version history in editor
- Multi-language post support

---

## Timeline

### Phase 1: V1 Essentials (6 weeks)
- Week 1-2: Incremental Signing
- Week 3-4: Git Integration + Frontmatter Parsing
- Week 5: Verification Reports + CI/CD
- Week 6: Batch Verification + Testing

### Phase 2: V1.5 Enhancements (4 weeks)
- Week 7-8: Content Diff Tracking
- Week 9: Multi-Language Support
- Week 10: WordPress Plugin Enhancements

### Phase 3: V2 Advanced Features (6 weeks)
- Week 11-12: Bulk Metadata Updates + Signature Renewal
- Week 13-14: Analytics & Metrics
- Week 15-16: Binary File Support

**Total: 16 weeks (4 months)**

---

## Success Metrics

- **Adoption:** 100+ publishers using SDK
- **Performance:** Sign 1000 files in <60 seconds
- **Reliability:** 99.9% uptime for API
- **Satisfaction:** NPS > 50

---

## Dependencies

- Python 3.9+
- UV package manager
- Git (optional, for git integration)
- PyYAML, toml (optional, for frontmatter)
- gitpython (optional, for git metadata)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limits | High | Implement caching, batch endpoints |
| Large repository performance | Medium | Incremental signing, concurrency |
| Binary file complexity | Medium | Start with text extraction, iterate |
| Certificate expiration | High | Auto-renewal, expiration warnings |

---

## Next Steps

1. Review and approve this PRD
2. Create detailed technical specs for Phase 1
3. Assign engineering resources
4. Begin implementation of incremental signing
5. Set up CI/CD for SDK testing
