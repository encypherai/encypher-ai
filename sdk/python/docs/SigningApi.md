# encypher.SigningApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**sign_advanced_api_v1_sign_advanced_post**](SigningApi.md#sign_advanced_api_v1_sign_advanced_post) | **POST** /api/v1/sign/advanced | REMOVED - Use POST /sign with options instead
[**sign_content_api_v1_sign_post**](SigningApi.md#sign_content_api_v1_sign_post) | **POST** /api/v1/sign | Sign content with C2PA manifest


# **sign_advanced_api_v1_sign_advanced_post**
> object sign_advanced_api_v1_sign_advanced_post()

REMOVED - Use POST /sign with options instead

**⚠️ REMOVED: This endpoint has been removed.**

Please use `POST /sign` with options instead.

Migration example:
```json
// Old /sign/advanced request
{
    "document_id": "doc1",
    "text": "...",
    "segmentation_level": "sentence"
}

// New /sign request
{
    "text": "...",
    "document_id": "doc1",
    "options": {
        "segmentation_level": "sentence"
    }
}
```

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.SigningApi(api_client)

    try:
        # REMOVED - Use POST /sign with options instead
        api_response = api_instance.sign_advanced_api_v1_sign_advanced_post()
        print("The response of SigningApi->sign_advanced_api_v1_sign_advanced_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SigningApi->sign_advanced_api_v1_sign_advanced_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**410** | Endpoint removed |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sign_content_api_v1_sign_post**
> object sign_content_api_v1_sign_post(unified_sign_request)

Sign content with C2PA manifest

Sign content with C2PA manifest. Features are gated by tier.

---

## Tier Feature Matrix

| Feature | Free | Enterprise |
|---------|------|------------|
| Basic C2PA signing | ✅ | ✅ |
| Sentence / paragraph / section segmentation | ✅ | ✅ |
| Advanced manifest modes | ✅ | ✅ |
| Attribution indexing | ✅ | ✅ |
| Custom assertions | ✅ | ✅ |
| Rights metadata | ✅ | ✅ |
| Batch signing | up to 10 | up to 100 |
| Word-level segmentation | ❌ | ✅ |
| Dual binding | ❌ | ✅ |
| Fingerprinting | ❌ | ✅ |

---

## Request Body

Provide **either** `text` (single document) **or** `documents` (batch), plus an `options` object.

### Top-level fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | one of `text` / `documents` | Content to sign (single document, max 1 MB). |
| `document_id` | string | no | Custom document identifier (1-255 chars). Auto-generated if omitted. |
| `document_title` | string | no | Human-readable title (max 500 chars). |
| `document_url` | string | no | Canonical URL of the document (max 1000 chars). |
| `metadata` | object | no | Arbitrary key-value metadata attached to the document. |
| `documents` | array | one of `text` / `documents` | List of `{text, document_id?, document_title?, document_url?, metadata?}` objects for batch signing. |
| `options` | object | no | Signing options (see below). All fields have sensible defaults. |

---

## Options Reference

### Segmentation & Structure

| Option | Type | Default | Values | Tier | Description |
|--------|------|---------|--------|------|-------------|
| `segmentation_level` | string | `"document"` | `document`, `sentence`, `paragraph`, `section`, `word` | `word` requires Enterprise | Granularity at which text is split and individually signed. Higher granularity enables per-segment tamper detection. |
| `segmentation_levels` | string[] | *null* | subset of `sentence`, `paragraph`, `section` | Free | Build Merkle trees at multiple levels simultaneously for multi-resolution verification. |

### Manifest & Embedding

| Option | Type | Default | Values | Tier | Description |
|--------|------|---------|--------|------|-------------|
| `manifest_mode` | string | `"full"` | `full`, `micro` | Free | Controls how the C2PA manifest and per-segment markers are embedded. `full` = standard C2PA wrapper. `micro` = ultra-compact per-segment markers controlled by `ecc`, `embed_c2pa`, and `legacy_safe` flags. A C2PA manifest is always generated; `embed_c2pa` controls whether it's embedded in content; `store_c2pa_manifest` controls DB persistence. |
| `ecc` | bool | `true` | | Free | Enable Reed-Solomon error correction for micro mode (44 chars/segment vs 36). Ignored for non-micro modes. |
| `embed_c2pa` | bool | `true` | | Free | Embed full C2PA document manifest into signed content for micro mode. When false, per-sentence markers only; C2PA manifest is still generated and stored in DB. Ignored for non-micro modes. |
| `embedding_strategy` | string | `"single_point"` | `single_point`, `distributed`, `distributed_redundant` | `distributed_redundant` requires Enterprise | How the invisible signature is placed within each segment. `single_point` = one location. `distributed` = spread across the segment. `distributed_redundant` = distributed with ECC for resilience. |
| `distribution_target` | string | *null* | `whitespace`, `punctuation`, `all_chars` | Free | Which character positions are used when `embedding_strategy` is `distributed` or `distributed_redundant`. |

### C2PA Provenance

| Option | Type | Default | Values | Tier | Description |
|--------|------|---------|--------|------|-------------|
| `action` | string | `"c2pa.created"` | `c2pa.created`, `c2pa.edited` | Free | C2PA action type. Use `c2pa.created` for new content, `c2pa.edited` for modifications. |
| `previous_instance_id` | string | *null* | any | Free | The `instance_id` from a previous signing response. Required when `action` is `c2pa.edited` to form a provenance chain. |
| `document_type` | string | `"article"` | `article`, `legal_brief`, `contract`, `ai_output` | Free | Semantic document type included in the manifest. |
| `claim_generator` | string | *null* | any | Free | Optional claim generator identifier for C2PA manifests (e.g. your application name). |
| `digital_source_type` | string | *null* | IPTC URI | Free | IPTC digital source type URI, e.g. for AI-generated content. |

### Advanced Features

| Option | Type | Default | Tier | Description |
|--------|------|---------|------|-------------|
| `index_for_attribution` | bool | `false` | Free | Index content segments for later attribution and plagiarism detection via `/verify/advanced`. |
| `add_dual_binding` | bool | `false` | Enterprise | Enable an additional integrity binding layer for enhanced tamper resistance. |
| `include_fingerprint` | bool | `false` | Enterprise | Generate a robust content fingerprint that can survive minor text modifications. |
| `disable_c2pa` | bool | `false` | Enterprise | Opt out of C2PA manifest embedding for non-micro modes; only basic metadata is attached. For micro mode, use `embed_c2pa` instead. |
| `store_c2pa_manifest` | bool | `true` | Free | Persist generated C2PA manifest in content DB for DB-backed verification. Applies to all modes that generate a manifest. |
| `enable_print_fingerprint` | bool | `false` | Enterprise | Print Leak Detection - embed imperceptible spacing patterns (U+2009 THIN SPACE vs U+0020) that survive printing and scanning, enabling source identification from leaked physical or PDF copies. |

### Custom Assertions & Rights (Business+)

| Option | Type | Default | Tier | Description |
|--------|------|---------|------|-------------|
| `custom_assertions` | array | *null* | Free | List of `{label, data}` objects to include as custom C2PA assertions. |
| `template_id` | string | *null* | Free | ID of a pre-registered assertion template to apply. |
| `validate_assertions` | bool | `true` | Free | Whether to validate custom assertions against registered JSON schemas. |
| `rights` | object | *null* | Free | Rights metadata: `{copyright_holder, license_url, usage_terms, syndication_allowed, embargo_until, contact_email}`. |
| `license` | object | *null* | Free | License info: `{type, url, contact_email}`. |
| `actions` | array | *null* | Free | List of C2PA action assertion objects. |

### Output Options

| Option | Type | Default | Values | Description |
|--------|------|---------|--------|-------------|
| `embedding_options.format` | string | `"plain"` | `plain`, `html`, `markdown`, `json` | Output format for the signed text. |
| `embedding_options.method` | string | `"invisible"` | `invisible`, `data-attribute`, `span`, `comment` | How the embedding is represented. `invisible` uses zero-width Unicode characters. |
| `embedding_options.include_text` | bool | `true` | | Whether to include the embedded text in the response. |
| `return_embedding_plan` | bool | `false` | | When `true`, includes `document.embedding_plan` with codepoint-based marker insertion operations for formatting-preserving clients. |
| `expires_at` | datetime | *null* | ISO 8601 | Optional expiration timestamp for the embeddings. |

---

## Examples

**Single document (minimal):**
```json
{
    "text": "The Senate passed a landmark bill today.",
    "document_title": "Senate Bill"
}
```

**Single document (with options):**
```json
{
    "text": "The Senate passed a landmark bill today. The vote was 67-33.",
    "document_title": "Senate Bill",
    "options": {
        "segmentation_level": "sentence",
        "manifest_mode": "micro",
        "index_for_attribution": true,
        "action": "c2pa.created"
    }
}
```

**Batch:**
```json
{
    "documents": [
        {"text": "First article...", "document_title": "Article 1"},
        {"text": "Second article...", "document_title": "Article 2"}
    ],
    "options": {
        "segmentation_level": "sentence",
        "embedding_strategy": "distributed"
    }
}
```

**Edit provenance chain:**
```json
{
    "text": "Updated article content...",
    "options": {
        "action": "c2pa.edited",
        "previous_instance_id": "urn:uuid:abc123..."
    }
}
```

The response includes `meta.features_gated` showing features available at higher tiers.

When `options.return_embedding_plan=true`, each signed document may also include:

```json
"embedding_plan": {
  "index_unit": "codepoint",
  "operations": [
    {"insert_after_index": 128, "marker": "..."}
  ]
}
```

This allows clients (e.g. Office add-ins) to insert only invisible markers at indexed positions while preserving native formatting.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.unified_sign_request import UnifiedSignRequest
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = encypher.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.SigningApi(api_client)
    unified_sign_request = encypher.UnifiedSignRequest() # UnifiedSignRequest |

    try:
        # Sign content with C2PA manifest
        api_response = api_instance.sign_content_api_v1_sign_post(unified_sign_request)
        print("The response of SigningApi->sign_content_api_v1_sign_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SigningApi->sign_content_api_v1_sign_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **unified_sign_request** | [**UnifiedSignRequest**](UnifiedSignRequest.md)|  |

### Return type

**object**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Content signed successfully |  -  |
**400** | Invalid request |  -  |
**403** | Feature requires higher tier |  -  |
**429** | Rate limit exceeded |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
