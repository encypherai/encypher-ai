# Phase 2 & 3 Implementation Plan

**Date:** October 29, 2025  
**Status:** Planning → Implementation  
**Estimated Time:** 8 weeks total

---

## Executive Summary

This plan outlines the implementation of Phase 2 (P1 features) and Phase 3 (P2 features) for the Encypher Enterprise SDK and API. These features enhance the core functionality with advanced capabilities for version tracking, multi-language support, metadata management, signature lifecycle, analytics, and binary file support.

---

## Phase 2 (P1 - Should-Have for V1.5)

**Total Effort:** 2.5 weeks  
**Priority:** High (enhances core value proposition)

### 7.0 Content Diff Tracking ✅ PLANNED

**Effort:** 1.5 weeks  
**Value:** Track content changes over time, show edit history

#### Implementation Steps:

1. **State File Enhancement** (Day 1-2)
   - Extend `.encypher-state.json` to store previous content hash
   - Add version number tracking
   - Store previous document ID for linking

2. **Diff Generation** (Day 3-4)
   - Implement unified diff generation (Python `difflib`)
   - Calculate change statistics (lines added/removed/modified)
   - Identify changed sections (paragraphs/sentences)

3. **Version Linking** (Day 5-6)
   - Link current version to previous version in metadata
   - Store diff in C2PA custom assertions
   - Track version lineage (v1 → v2 → v3)

4. **SDK Implementation** (Day 7-8)
   - Add `--track-changes` CLI flag
   - Modify `StateManager` to store previous versions
   - Include diff in signing metadata

5. **API Enhancement** (Day 9-10)
   - Accept `previous_version_id` in sign request
   - Store version history in database
   - Return version history in verification response

**Deliverables:**
- `encypher_enterprise/diff.py` - Diff generation utilities
- Enhanced `StateManager` with version tracking
- `--track-changes` CLI option
- Database schema for version history
- API endpoints for version retrieval

---

### 8.0 Multi-Language Support ✅ PLANNED

**Effort:** 1 week  
**Value:** Support international publishers, link translations

#### Implementation Steps:

1. **Language Detection** (Day 1-2)
   - Integrate `langdetect` library for auto-detection
   - Support manual language specification
   - Handle multi-language documents (detect primary language)

2. **Translation Linking** (Day 3-4)
   - Add `translations` field to metadata
   - Link translated versions by document ID
   - Track translation metadata (translator, date)

3. **SDK Implementation** (Day 5-6)
   - Add `--language` CLI option
   - Add `--translations` option (JSON array)
   - Auto-detect from frontmatter `lang` field

4. **API Enhancement** (Day 7)
   - Accept `language` and `translations` in sign request
   - Store in database with indexes
   - Return in verification response

**Deliverables:**
- `encypher_enterprise/language.py` - Language detection
- `--language` and `--translations` CLI options
- Database schema for translations
- API endpoints for translation queries

---

## Phase 3 (P2 - Nice-to-Have for V2)

**Total Effort:** 6.5 weeks  
**Priority:** Medium (advanced features for power users)

### 9.0 Bulk Metadata Updates ✅ PLANNED

**Effort:** 1 week  
**Value:** Update metadata without re-signing, batch operations

#### Implementation Steps:

1. **Metadata Update Logic** (Day 1-2)
   - Implement metadata-only updates (no re-signing)
   - Validate metadata schema
   - Audit trail for changes

2. **Batch Operations** (Day 3-4)
   - Support CSV/JSON input for bulk updates
   - Preview changes before applying
   - Progress tracking for large batches

3. **SDK Implementation** (Day 5-6)
   - Add `update-metadata` CLI command
   - Support `--from-csv` and `--from-json` options
   - Add `--preview` flag

4. **API Implementation** (Day 7)
   - `PATCH /api/v1/documents/{id}/metadata`
   - `POST /api/v1/documents/metadata/batch`
   - Validation and audit logging

**Deliverables:**
- `encypher_enterprise/metadata_updater.py`
- `update-metadata` CLI command
- API endpoints for metadata updates
- Audit logging system

---

### 10.0 Signature Expiration & Renewal ✅ PLANNED

**Effort:** 2 weeks  
**Value:** Automated signature lifecycle management

#### Implementation Steps:

1. **Expiration Tracking** (Day 1-3)
   - Track certificate expiration dates
   - Query expiring signatures (30/60/90 days)
   - Send email notifications

2. **Renewal Logic** (Day 4-6)
   - Implement signature renewal (re-sign with new cert)
   - Maintain document ID and metadata
   - Link to previous signature

3. **Auto-Renewal** (Day 7-9)
   - Scheduled task for auto-renewal
   - Batch renewal for repositories
   - Handle failures gracefully

4. **SDK Implementation** (Day 10-12)
   - Add `check-expiring` CLI command
   - Add `renew-signatures` CLI command
   - Add `--auto-renew` option

5. **API Implementation** (Day 13-14)
   - Return expiration date in verification
   - `POST /api/v1/documents/{id}/renew`
   - Notification system

**Deliverables:**
- `encypher_enterprise/renewal.py`
- `check-expiring` and `renew-signatures` CLI commands
- API renewal endpoint
- Email notification system
- Scheduled renewal task

---

### 11.0 Analytics & Metrics ✅ PLANNED

**Effort:** 1.5 weeks  
**Value:** Usage insights, performance monitoring

#### Implementation Steps:

1. **Metrics Collection** (Day 1-3)
   - Track signing activity (count, size, time)
   - Track verification requests
   - Track API usage and errors
   - Local metrics storage

2. **Dashboard Integration** (Day 4-6)
   - Send metrics to analytics service (optional)
   - Create dashboard views (if building UI)
   - Generate usage reports (CSV/JSON)

3. **SDK Implementation** (Day 7-9)
   - Add `--analytics` option (opt-in)
   - Track local metrics in `.encypher-metrics.json`
   - Add `stats` CLI command

4. **API Implementation** (Day 10-11)
   - `GET /api/v1/analytics/usage`
   - Aggregate usage data
   - Generate monthly reports

**Deliverables:**
- `encypher_enterprise/analytics.py`
- `--analytics` CLI option
- `stats` CLI command (enhanced)
- API analytics endpoints
- Usage report generator

---

### 12.0 Binary File Support ✅ PLANNED

**Effort:** 2 weeks  
**Value:** Sign PDFs, DOCX, images, video

#### Implementation Steps:

1. **File Type Detection** (Day 1-2)
   - Detect file types (MIME types)
   - Support PDF, DOCX, JPEG, PNG, MP4
   - Validate file formats

2. **Text Extraction** (Day 3-5)
   - Extract text from PDF (`PyPDF2` or `pdfplumber`)
   - Extract text from DOCX (`python-docx`)
   - Use file hash for images/video (no text)

3. **Binary Signing** (Day 6-8)
   - Sign extracted text (for PDF/DOCX)
   - Sign file hash (for images/video)
   - Store binary metadata

4. **SDK Implementation** (Day 9-12)
   - Extend `RepositorySigner` for binary files
   - Add text extraction utilities
   - Support mixed file types in repositories

5. **API Implementation** (Day 13-14)
   - Accept binary file hashes in sign request
   - Store binary file metadata
   - Verify binary files

**Deliverables:**
- `encypher_enterprise/binary.py` - Binary file handling
- Text extraction utilities
- Extended `RepositorySigner`
- API support for binary files
- Dependencies: `PyPDF2`, `python-docx`, `Pillow`

---

## Implementation Order

### Week 1-2: Phase 2 Features
1. **Week 1**: Content Diff Tracking (7.0)
2. **Week 2**: Multi-Language Support (8.0)

### Week 3-8: Phase 3 Features
3. **Week 3**: Bulk Metadata Updates (9.0)
4. **Week 4-5**: Signature Expiration & Renewal (10.0)
5. **Week 6-7**: Analytics & Metrics (11.0)
6. **Week 8**: Binary File Support (12.0)

---

## Technical Architecture

### New Modules

```
encypher_enterprise/
├── diff.py                 # Content diff generation
├── language.py             # Language detection
├── metadata_updater.py     # Bulk metadata updates
├── renewal.py              # Signature renewal
├── analytics.py            # Metrics tracking
└── binary.py               # Binary file support
```

### Database Schema Changes

```sql
-- Version history
CREATE TABLE document_versions (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    version_number INTEGER NOT NULL,
    previous_version_id VARCHAR(255),
    diff_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Translations
CREATE TABLE document_translations (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    language VARCHAR(10) NOT NULL,
    translation_of VARCHAR(255),
    translator VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Expiration tracking
ALTER TABLE documents ADD COLUMN expires_at TIMESTAMP;
ALTER TABLE documents ADD COLUMN renewed_from VARCHAR(255);

-- Analytics
CREATE TABLE analytics_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    document_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### New Dependencies

```toml
# Phase 2
langdetect = "^1.0.9"      # Language detection

# Phase 3
PyPDF2 = "^3.0.0"          # PDF text extraction
python-docx = "^1.1.0"     # DOCX text extraction
Pillow = "^10.0.0"         # Image handling
schedule = "^1.2.0"        # Scheduled tasks (renewal)
```

---

## Testing Strategy

### Unit Tests
- Diff generation accuracy
- Language detection accuracy
- Metadata validation
- Renewal logic
- Analytics tracking
- Binary file handling

### Integration Tests
- End-to-end version tracking
- Translation linking
- Bulk metadata updates
- Auto-renewal workflow
- Binary file signing

### Performance Tests
- Diff generation for large files
- Bulk update performance (1000+ docs)
- Binary file processing speed

**Target Coverage:** 80%+ for all new modules

---

## API Endpoints Summary

### New Endpoints

| Endpoint | Method | Feature | Priority |
|----------|--------|---------|----------|
| `/api/v1/documents/{id}/versions` | GET | Version history | P1 |
| `/api/v1/documents/{id}/translations` | GET | Get translations | P1 |
| `/api/v1/documents/metadata/batch` | PATCH | Bulk metadata update | P2 |
| `/api/v1/documents/{id}/renew` | POST | Renew signature | P2 |
| `/api/v1/documents/expiring` | GET | List expiring docs | P2 |
| `/api/v1/analytics/usage` | GET | Usage metrics | P2 |

### Enhanced Endpoints

| Endpoint | Enhancement | Priority |
|----------|-------------|----------|
| `POST /api/v1/sign` | Accept language, previous_version, binary hash | P1/P2 |
| `POST /api/v1/verify` | Return expiration, versions, translations | P1/P2 |

---

## CLI Commands Summary

### New Commands

```bash
# Version tracking
encypher diff <file1> <file2>
encypher versions <document-id>

# Translations
encypher link-translation <doc-id> <translation-doc-id> --language es

# Metadata updates
encypher update-metadata <doc-id> --author "New Author"
encypher update-metadata --from-csv updates.csv

# Renewal
encypher check-expiring --days 30
encypher renew-signatures <directory>
encypher renew-signatures <doc-id>

# Analytics
encypher stats --detailed
encypher export-metrics --format json

# Binary files
encypher sign-binary <file.pdf>
encypher sign-repo ./docs --include-binary
```

---

## Success Criteria

### Phase 2
- ✅ Track version history for all signed documents
- ✅ Support 50+ languages with auto-detection
- ✅ Link translated versions bidirectionally

### Phase 3
- ✅ Update metadata for 1000+ documents in <10 seconds
- ✅ Auto-renew signatures before expiration
- ✅ Track all signing/verification activity
- ✅ Sign PDF, DOCX, images, and video files

---

## Risk Mitigation

### Technical Risks
- **Diff generation performance**: Use streaming for large files
- **Language detection accuracy**: Fallback to manual specification
- **Binary file size**: Implement chunked processing
- **Renewal failures**: Retry logic with exponential backoff

### Compatibility Risks
- **Database migrations**: Use Alembic for versioned migrations
- **API versioning**: Maintain v1 compatibility, add v2 if needed
- **SDK backwards compatibility**: All new features are opt-in

---

## Documentation Updates

### SDK Documentation
- Version tracking guide
- Multi-language setup
- Metadata update examples
- Renewal configuration
- Analytics setup
- Binary file signing guide

### API Documentation
- New endpoint specifications
- Request/response examples
- Error codes
- Migration guide

---

## Timeline

```
Week 1: Content Diff Tracking
├── Mon-Tue: State file enhancement, diff generation
├── Wed-Thu: Version linking, SDK implementation
└── Fri: API enhancement, testing

Week 2: Multi-Language Support
├── Mon-Tue: Language detection
├── Wed-Thu: Translation linking
├── Fri: SDK/API implementation, testing

Week 3: Bulk Metadata Updates
├── Mon-Tue: Update logic, validation
├── Wed-Thu: Batch operations
└── Fri: SDK/API implementation, testing

Week 4-5: Signature Expiration & Renewal
├── Week 4: Expiration tracking, renewal logic
└── Week 5: Auto-renewal, SDK/API implementation

Week 6-7: Analytics & Metrics
├── Week 6: Metrics collection, storage
└── Week 7: Dashboard integration, SDK/API

Week 8: Binary File Support
├── Mon-Wed: File detection, text extraction
├── Thu-Fri: Binary signing, SDK/API implementation
```

---

## Next Steps

1. ✅ Review and approve plan
2. ✅ Set up development environment
3. ✅ Create feature branches
4. ✅ Begin Week 1: Content Diff Tracking
5. ✅ Continuous testing and documentation

---

**Ready to implement!** 🚀
