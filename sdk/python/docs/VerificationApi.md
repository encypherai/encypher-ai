# encypher.VerificationApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**verify_advanced_api_v1_verify_advanced_post**](VerificationApi.md#verify_advanced_api_v1_verify_advanced_post) | **POST** /api/v1/verify/advanced | Advanced verification
[**verify_quote_integrity_api_v1_verify_quote_integrity_post**](VerificationApi.md#verify_quote_integrity_api_v1_verify_quote_integrity_post) | **POST** /api/v1/verify/quote-integrity | Quote Integrity Verification


# **verify_advanced_api_v1_verify_advanced_post**
> object verify_advanced_api_v1_verify_advanced_post(verify_advanced_request)

Advanced verification

Verify signed content and optionally run attribution, plagiarism detection, and fuzzy fingerprint search.

Requires an authenticated API key with verify permission.

---

## Request Fields

| Field | Type | Default | Values | Tier | Description |
|-------|------|---------|--------|------|-------------|
| `text` | string | *(required)* | any (min 1 char) | Free | The text to verify. Should contain invisible C2PA embeddings from a prior `/sign` call. |
| `segmentation_level` | string | `"sentence"` | `document`, `sentence`, `paragraph`, `section` | Free | Granularity used for tamper detection. Should match the level used during signing. |
| `search_scope` | string | `"organization"` | `organization`, `public`, `all` | `all` requires Enterprise | Scope for attribution / plagiarism lookups. `organization` = only your org's documents. `public` = publicly indexed docs. `all` = cross-organization (Enterprise only). |
| `include_attribution` | bool | `false` | | Free | Run attribution analysis — find source documents that match segments of the submitted text. |
| `detect_plagiarism` | bool | `false` | | Free | Run plagiarism detection — generate a full plagiarism report with match percentages per source. |
| `include_heat_map` | bool | `false` | | Free | Include a segment-level heat map in the plagiarism report (only used when `detect_plagiarism` is `true`). |
| `min_match_percentage` | float | `0.0` | 0.0 – 100.0 | Free | Minimum match percentage to include a source in the plagiarism report. |
| `fuzzy_search` | object | *null* | see below | Enterprise | Optional fuzzy fingerprint search configuration. |

### `fuzzy_search` Object (Enterprise)

| Field | Type | Default | Values | Description |
|-------|------|---------|--------|-------------|
| `enabled` | bool | `false` | | Whether to run fuzzy fingerprint search. |
| `algorithm` | string | `"simhash"` | `simhash` | Fingerprint algorithm. |
| `levels` | string[] | `["sentence", "paragraph"]` | `sentence`, `paragraph`, `document` | Segmentation levels to search. |
| `similarity_threshold` | float | `0.82` | 0.0 – 1.0 | Minimum similarity score for a match. |
| `max_candidates` | int | `20` | 1 – 200 | Maximum number of candidate matches to return. |
| `include_merkle_proof` | bool | `true` | | Whether to include Merkle proofs for matches. |
| `fallback_when_no_binding` | bool | `true` | | Only run fuzzy search when no embeddings are found in the text. |

---

## Response

The response always includes:

- **`data`** — Verification verdict with `is_signed`, `reason_code`, `embeddings_found`, etc.
- **`tamper_detection`** — Merkle root comparison at the requested segmentation level.
- **`tamper_localization`** — Per-segment diff showing changed / inserted / deleted segments (when Merkle root exists).

Conditionally included based on request flags:

- **`attribution`** — List of source document matches with `document_id`, `organization_id`, `confidence`.
- **`plagiarism`** — Full plagiarism report with `overall_match_percentage`, `source_documents`, optional `heat_map_data`.
- **`fuzzy_search`** — Fuzzy fingerprint matches with similarity scores.

---

## Examples

**Basic verification:**
```json
{
    "text": "Signed content with invisible C2PA embeddings..."
}
```

**Verification with attribution and plagiarism:**
```json
{
    "text": "Content to check...",
    "segmentation_level": "sentence",
    "include_attribution": true,
    "detect_plagiarism": true,
    "include_heat_map": true,
    "min_match_percentage": 10.0
}
```

**Verification with fuzzy search (Enterprise):**
```json
{
    "text": "Content that may have been modified...",
    "fuzzy_search": {
        "enabled": true,
        "similarity_threshold": 0.75,
        "max_candidates": 50,
        "fallback_when_no_binding": false
    }
}
```

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.verify_advanced_request import VerifyAdvancedRequest
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
    api_instance = encypher.VerificationApi(api_client)
    verify_advanced_request = encypher.VerifyAdvancedRequest() # VerifyAdvancedRequest |

    try:
        # Advanced verification
        api_response = api_instance.verify_advanced_api_v1_verify_advanced_post(verify_advanced_request)
        print("The response of VerificationApi->verify_advanced_api_v1_verify_advanced_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VerificationApi->verify_advanced_api_v1_verify_advanced_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verify_advanced_request** | [**VerifyAdvancedRequest**](VerifyAdvancedRequest.md)|  |

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **verify_quote_integrity_api_v1_verify_quote_integrity_post**
> object verify_quote_integrity_api_v1_verify_quote_integrity_post(quote_integrity_request)

Quote Integrity Verification

Public endpoint for AI companies to verify quote accuracy against signed content.

Returns a verdict indicating whether the quoted text matches signed source content.

### Example


```python
import encypher
from encypher.models.quote_integrity_request import QuoteIntegrityRequest
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
    api_instance = encypher.VerificationApi(api_client)
    quote_integrity_request = encypher.QuoteIntegrityRequest() # QuoteIntegrityRequest |

    try:
        # Quote Integrity Verification
        api_response = api_instance.verify_quote_integrity_api_v1_verify_quote_integrity_post(quote_integrity_request)
        print("The response of VerificationApi->verify_quote_integrity_api_v1_verify_quote_integrity_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VerificationApi->verify_quote_integrity_api_v1_verify_quote_integrity_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **quote_integrity_request** | [**QuoteIntegrityRequest**](QuoteIntegrityRequest.md)|  |

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
