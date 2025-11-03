# C2PA Custom Assertions API Guide

Complete guide to using custom C2PA assertions in the EncypherAI Enterprise API.

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Schema Management](#schema-management)
4. [Assertion Validation](#assertion-validation)
5. [Template Management](#template-management)
6. [Embedding with Custom Assertions](#embedding-with-custom-assertions)
7. [Examples](#examples)
8. [Error Handling](#error-handling)

---

## Overview

The C2PA Custom Assertions API allows enterprise customers to:

- **Define custom assertion schemas** with JSON Schema validation
- **Validate assertions** before embedding
- **Create reusable templates** for common use cases
- **Embed custom assertions** in C2PA-compliant manifests
- **Maintain full C2PA 2.2 compliance**

### Base URL

```
Production: https://api.encypherai.com/api/v1
Development: http://localhost:8000/api/v1
```

---

## Authentication

All endpoints require API key authentication via the `X-API-Key` header.

```http
X-API-Key: your-api-key-here
```

---

## Schema Management

### Register a Custom Schema

Register a new C2PA assertion schema with JSON Schema validation rules.

**Endpoint:** `POST /enterprise/c2pa/schemas`

**Request Body:**

```json
{
  "namespace": "com.acme",
  "label": "com.acme.legal.case.v1",
  "version": "1.0",
  "description": "Legal case metadata for court documents",
  "is_public": false,
  "schema": {
    "type": "object",
    "properties": {
      "case_number": {
        "type": "string",
        "pattern": "^[0-9]{4}-[A-Z]{2}-[0-9]{5}$",
        "description": "Court case number"
      },
      "jurisdiction": {
        "type": "string",
        "description": "Legal jurisdiction"
      },
      "court": {
        "type": "string",
        "description": "Court name"
      },
      "filing_date": {
        "type": "string",
        "format": "date",
        "description": "Date of filing"
      }
    },
    "required": ["case_number", "jurisdiction"]
  }
}
```

**Response:** `201 Created`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "namespace": "com.acme",
  "label": "com.acme.legal.case.v1",
  "version": "1.0",
  "description": "Legal case metadata for court documents",
  "schema": { ... },
  "organization_id": "org_acme",
  "is_public": false,
  "created_at": "2025-11-03T14:00:00Z",
  "updated_at": "2025-11-03T14:00:00Z"
}
```

### List Schemas

List all schemas accessible to your organization.

**Endpoint:** `GET /enterprise/c2pa/schemas`

**Query Parameters:**

- `page` (integer, default: 1) - Page number
- `page_size` (integer, default: 50, max: 100) - Items per page
- `namespace` (string, optional) - Filter by namespace
- `is_public` (boolean, optional) - Filter by public/private

**Response:** `200 OK`

```json
{
  "schemas": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "namespace": "com.acme",
      "label": "com.acme.legal.case.v1",
      "version": "1.0",
      ...
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 50
}
```

### Get Schema

Get a specific schema by ID.

**Endpoint:** `GET /enterprise/c2pa/schemas/{schema_id}`

**Response:** `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "namespace": "com.acme",
  "label": "com.acme.legal.case.v1",
  ...
}
```

### Update Schema

Update an existing schema.

**Endpoint:** `PUT /enterprise/c2pa/schemas/{schema_id}`

**Request Body:**

```json
{
  "description": "Updated description",
  "schema": { ... },
  "is_public": true
}
```

**Response:** `200 OK`

### Delete Schema

Delete a schema.

**Endpoint:** `DELETE /enterprise/c2pa/schemas/{schema_id}`

**Response:** `204 No Content`

---

## Assertion Validation

### Validate Assertion

Validate an assertion against its registered schema before embedding.

**Endpoint:** `POST /enterprise/c2pa/validate`

**Request Body:**

```json
{
  "label": "c2pa.location.v1",
  "data": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "location_name": "San Francisco City Hall"
  }
}
```

**Response:** `200 OK`

```json
{
  "valid": true,
  "assertions": [
    {
      "label": "c2pa.location.v1",
      "valid": true,
      "errors": [],
      "warnings": []
    }
  ]
}
```

**Invalid Example Response:**

```json
{
  "valid": false,
  "assertions": [
    {
      "label": "c2pa.location.v1",
      "valid": false,
      "errors": [
        "latitude: 95.0 is greater than the maximum of 90"
      ],
      "warnings": []
    }
  ]
}
```

---

## Template Management

### Create Template

Create a reusable assertion template.

**Endpoint:** `POST /enterprise/c2pa/templates`

**Request Body:**

```json
{
  "name": "News Article with Fact-Checking",
  "description": "Template for news articles with fact-checking and AI permissions",
  "category": "news",
  "is_public": false,
  "assertions": [
    {
      "label": "c2pa.actions.v1",
      "description": "Track content lifecycle"
    },
    {
      "label": "c2pa.training-mining.v1",
      "description": "AI training permissions",
      "default_data": {
        "use": {
          "ai_training": false,
          "ai_inference": false,
          "data_mining": false
        }
      }
    },
    {
      "label": "c2pa.claim_review.v1",
      "description": "Fact-checking information",
      "optional": true
    },
    {
      "label": "c2pa.location.v1",
      "description": "Story location",
      "optional": true
    }
  ]
}
```

**Response:** `201 Created`

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "News Article with Fact-Checking",
  "description": "Template for news articles with fact-checking and AI permissions",
  "category": "news",
  "assertions": [ ... ],
  "organization_id": "org_acme",
  "is_public": false,
  "created_at": "2025-11-03T14:00:00Z",
  "updated_at": "2025-11-03T14:00:00Z"
}
```

### List Templates

List available templates.

**Endpoint:** `GET /enterprise/c2pa/templates`

**Query Parameters:**

- `page` (integer, default: 1)
- `page_size` (integer, default: 50, max: 100)
- `category` (string, optional) - Filter by category (news, legal, academic, publisher)

**Response:** `200 OK`

```json
{
  "templates": [ ... ],
  "total": 8,
  "page": 1,
  "page_size": 50
}
```

### Get Template

Get a specific template.

**Endpoint:** `GET /enterprise/c2pa/templates/{template_id}`

**Response:** `200 OK`

### Update Template

Update a template.

**Endpoint:** `PUT /enterprise/c2pa/templates/{template_id}`

**Request Body:**

```json
{
  "description": "Updated description",
  "category": "legal",
  "is_public": true
}
```

**Response:** `200 OK`

### Delete Template

Delete a template.

**Endpoint:** `DELETE /enterprise/c2pa/templates/{template_id}`

**Response:** `204 No Content`

---

## Embedding with Custom Assertions

### Encode Document with Custom Assertions

Embed a document with custom C2PA assertions.

**Endpoint:** `POST /enterprise/embeddings/encode-with-embeddings`

**Request Body:**

```json
{
  "document_id": "article_20251103_001",
  "text": "San Francisco City Hall announced new policies today...",
  "segmentation_level": "sentence",
  "action": "c2pa.created",
  "custom_assertions": [
    {
      "label": "c2pa.location.v1",
      "data": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "location_name": "San Francisco City Hall"
      }
    },
    {
      "label": "c2pa.training-mining.v1",
      "data": {
        "use": {
          "ai_training": false,
          "ai_inference": false,
          "data_mining": false
        },
        "constraint_info": {
          "license": "All Rights Reserved"
        }
      }
    },
    {
      "label": "com.acme.legal.case.v1",
      "data": {
        "case_number": "2024-CV-12345",
        "jurisdiction": "California",
        "court": "Superior Court of San Francisco"
      }
    }
  ],
  "validate_assertions": true
}
```

**Response:** `201 Created`

```json
{
  "document_id": "article_20251103_001",
  "merkle_tree": {
    "root_id": "770e8400-e29b-41d4-a716-446655440002",
    "root_hash": "abc123...",
    "leaf_count": 15
  },
  "embeddings": [
    {
      "leaf_index": 0,
      "text": "San Francisco City Hall announced new policies today...",
      ...
    }
  ],
  "c2pa_manifest": {
    "instance_id": "urn:uuid:880e8400-e29b-41d4-a716-446655440003",
    "assertions": [
      {
        "label": "c2pa.actions.v1",
        ...
      },
      {
        "label": "c2pa.location.v1",
        "data": {
          "latitude": 37.7749,
          "longitude": -122.4194,
          "location_name": "San Francisco City Hall"
        }
      },
      {
        "label": "c2pa.training-mining.v1",
        ...
      },
      {
        "label": "com.acme.legal.case.v1",
        ...
      }
    ]
  }
}
```

---

## Examples

### Example 1: News Article with Location and Fact-Checking

```bash
curl -X POST https://api.encypherai.com/api/v1/enterprise/embeddings/encode-with-embeddings \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "news_article_001",
    "text": "Breaking news from downtown...",
    "action": "c2pa.created",
    "custom_assertions": [
      {
        "label": "c2pa.location.v1",
        "data": {
          "latitude": 37.7749,
          "longitude": -122.4194
        }
      },
      {
        "label": "c2pa.claim_review.v1",
        "data": {
          "claim_reviewed": "Statement about policy change",
          "rating": "True",
          "author": {
            "name": "FactCheck.org"
          }
        }
      }
    ]
  }'
```

### Example 2: Legal Document with Custom Schema

```bash
# First, register custom schema
curl -X POST https://api.encypherai.com/api/v1/enterprise/c2pa/schemas \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "namespace": "com.lawfirm",
    "label": "com.lawfirm.brief.v1",
    "version": "1.0",
    "schema": {
      "type": "object",
      "properties": {
        "case_number": {"type": "string"},
        "attorney": {"type": "string"}
      },
      "required": ["case_number"]
    }
  }'

# Then, embed document with custom assertion
curl -X POST https://api.encypherai.com/api/v1/enterprise/embeddings/encode-with-embeddings \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "legal_brief_001",
    "text": "IN THE SUPERIOR COURT...",
    "action": "c2pa.created",
    "custom_assertions": [
      {
        "label": "com.lawfirm.brief.v1",
        "data": {
          "case_number": "2024-CV-12345",
          "attorney": "Jane Smith, Esq."
        }
      }
    ]
  }'
```

### Example 3: Using a Template

```bash
# Create template
curl -X POST https://api.encypherai.com/api/v1/enterprise/c2pa/templates \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Academic Paper",
    "category": "academic",
    "assertions": [
      {
        "label": "c2pa.training-mining.v1",
        "default_data": {
          "use": {
            "ai_training": true,
            "ai_inference": true,
            "data_mining": true
          },
          "constraint_info": {
            "license": "CC-BY-4.0"
          }
        }
      }
    ]
  }'
```

---

## Error Handling

### Common Error Codes

- `400 Bad Request` - Invalid request body or parameters
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate schema or template
- `422 Unprocessable Entity` - Validation failed

### Validation Error Response

```json
{
  "code": "INVALID_ASSERTIONS",
  "message": "One or more custom assertions failed validation",
  "validation_results": {
    "valid": false,
    "assertions": [
      {
        "label": "c2pa.location.v1",
        "valid": false,
        "errors": [
          "latitude: 95.0 is greater than the maximum of 90"
        ],
        "warnings": []
      }
    ]
  }
}
```

---

## Standard C2PA Assertions

The following standard C2PA assertions are pre-loaded and available without registration:

### c2pa.location.v1

Geographic location information.

**Schema:**
```json
{
  "latitude": 37.7749,
  "longitude": -122.4194,
  "altitude": 16.0,
  "location_name": "San Francisco City Hall"
}
```

### c2pa.training-mining.v1

AI training and data mining permissions.

**Schema:**
```json
{
  "use": {
    "ai_training": false,
    "ai_inference": false,
    "data_mining": false
  },
  "constraint_info": {
    "license": "CC-BY-NC-4.0",
    "license_url": "https://creativecommons.org/licenses/by-nc/4.0/"
  }
}
```

### c2pa.claim_review.v1

Fact-checking and claim review information.

**Schema:**
```json
{
  "claim_reviewed": "Statement being fact-checked",
  "rating": "True",
  "author": {
    "name": "FactCheck.org",
    "url": "https://factcheck.org"
  },
  "date_published": "2025-11-03T14:00:00Z",
  "url": "https://factcheck.org/review/12345"
}
```

### c2pa.thumbnail.v1

Thumbnail image for content preview.

**Schema:**
```json
{
  "format": "image/jpeg",
  "identifier": "thumb_123",
  "thumbnail": "base64_encoded_data_here"
}
```

---

## Best Practices

1. **Always validate assertions** before embedding to catch errors early
2. **Use templates** for common use cases to ensure consistency
3. **Namespace your custom schemas** (e.g., `com.yourcompany.type.v1`)
4. **Version your schemas** to allow for future updates
5. **Set appropriate permissions** (public vs. private) for schemas
6. **Test with validation endpoint** before production use
7. **Include descriptive metadata** in schemas and templates

---

## Support

For questions or issues:

- **Documentation**: https://docs.encypherai.com
- **API Status**: https://status.encypherai.com
- **Support Email**: support@encypherai.com
- **Enterprise Support**: enterprise@encypherai.com

---

## Changelog

### Version 1.0 (November 2025)

- Initial release of C2PA Custom Assertions API
- Schema management endpoints
- Assertion validation
- Template system
- Integration with embedding service
- Full C2PA 2.2 compliance
