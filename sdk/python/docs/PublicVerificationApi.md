# encypher.PublicVerificationApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**batch_verify_embeddings_api_v1_public_verify_batch_post**](PublicVerificationApi.md#batch_verify_embeddings_api_v1_public_verify_batch_post) | **POST** /api/v1/public/verify/batch | Batch Verify Embeddings (Public - No Auth Required)
[**extract_and_verify_embedding_api_v1_public_extract_and_verify_post**](PublicVerificationApi.md#extract_and_verify_embedding_api_v1_public_extract_and_verify_post) | **POST** /api/v1/public/extract-and-verify | DEPRECATED - Use POST /api/v1/verify instead
[**verify_embedding_api_v1_public_verify_ref_id_get**](PublicVerificationApi.md#verify_embedding_api_v1_public_verify_ref_id_get) | **GET** /api/v1/public/verify/{ref_id} | Verify Embedding (Public - No Auth Required)


# **batch_verify_embeddings_api_v1_public_verify_batch_post**
> BatchVerifyResponse batch_verify_embeddings_api_v1_public_verify_batch_post(app_schemas_embeddings_batch_verify_request, authorization=authorization)

Batch Verify Embeddings (Public - No Auth Required)

Verify multiple embeddings in a single request.

    **This endpoint is PUBLIC and does NOT require authentication.**

    Useful for:
    - Verifying all embeddings on a page at once
    - Bulk verification by web scrapers
    - Browser extensions checking multiple paragraphs

    **Rate Limiting:**
    - 100 requests/hour per IP address
    - Maximum 50 embeddings per request

### Example


```python
import encypher
from encypher.models.app_schemas_embeddings_batch_verify_request import AppSchemasEmbeddingsBatchVerifyRequest
from encypher.models.batch_verify_response import BatchVerifyResponse
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
    api_instance = encypher.PublicVerificationApi(api_client)
    app_schemas_embeddings_batch_verify_request = encypher.AppSchemasEmbeddingsBatchVerifyRequest() # AppSchemasEmbeddingsBatchVerifyRequest |
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Batch Verify Embeddings (Public - No Auth Required)
        api_response = api_instance.batch_verify_embeddings_api_v1_public_verify_batch_post(app_schemas_embeddings_batch_verify_request, authorization=authorization)
        print("The response of PublicVerificationApi->batch_verify_embeddings_api_v1_public_verify_batch_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicVerificationApi->batch_verify_embeddings_api_v1_public_verify_batch_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_schemas_embeddings_batch_verify_request** | [**AppSchemasEmbeddingsBatchVerifyRequest**](AppSchemasEmbeddingsBatchVerifyRequest.md)|  |
 **authorization** | **str**|  | [optional]

### Return type

[**BatchVerifyResponse**](BatchVerifyResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Batch verification completed |  -  |
**400** | Invalid request |  -  |
**429** | Rate limit exceeded |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **extract_and_verify_embedding_api_v1_public_extract_and_verify_post**
> object extract_and_verify_embedding_api_v1_public_extract_and_verify_post(extract_and_verify_request)

DEPRECATED - Use POST /api/v1/verify instead

**⚠️ DEPRECATED: This endpoint is deprecated and will be removed.**

    Please use `POST /api/v1/verify` instead, which provides:
    - Full C2PA trust chain validation
    - Document info, licensing, and C2PA details (all free)
    - Merkle proof (with API key)
    - Better performance via verification-service

### Example


```python
import encypher
from encypher.models.extract_and_verify_request import ExtractAndVerifyRequest
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
    api_instance = encypher.PublicVerificationApi(api_client)
    extract_and_verify_request = encypher.ExtractAndVerifyRequest() # ExtractAndVerifyRequest |

    try:
        # DEPRECATED - Use POST /api/v1/verify instead
        api_response = api_instance.extract_and_verify_embedding_api_v1_public_extract_and_verify_post(extract_and_verify_request)
        print("The response of PublicVerificationApi->extract_and_verify_embedding_api_v1_public_extract_and_verify_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicVerificationApi->extract_and_verify_embedding_api_v1_public_extract_and_verify_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **extract_and_verify_request** | [**ExtractAndVerifyRequest**](ExtractAndVerifyRequest.md)|  |

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
**301** | Redirect to /api/v1/verify |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **verify_embedding_api_v1_public_verify_ref_id_get**
> VerifyEmbeddingResponse verify_embedding_api_v1_public_verify_ref_id_get(ref_id, signature, authorization=authorization)

Verify Embedding (Public - No Auth Required)

Verify a minimal signed embedding and retrieve associated metadata.

    **This endpoint is PUBLIC and does NOT require authentication.**

    Third parties can use this endpoint to:
    - Verify authenticity of content with embedded markers
    - Retrieve document metadata (title, author, organization)
    - Access C2PA manifest information
    - View licensing terms
    - Get Merkle proof for cryptographic verification

    **Rate Limiting:**
    - 1000 requests/hour per IP address
    - CAPTCHA required after repeated failures

    **Privacy:**
    - Does not return DB-stored text
    - Full text content is NOT exposed
    - Internal document IDs are mapped to public IDs

    **Example Usage:**
    ```
    GET /api/v1/public/verify/a3f9c2e1?signature=8k3mP9xQ
    ```

### Example


```python
import encypher
from encypher.models.verify_embedding_response import VerifyEmbeddingResponse
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
    api_instance = encypher.PublicVerificationApi(api_client)
    ref_id = 'ref_id_example' # str |
    signature = 'signature_example' # str | HMAC signature (8+ hex characters)
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Verify Embedding (Public - No Auth Required)
        api_response = api_instance.verify_embedding_api_v1_public_verify_ref_id_get(ref_id, signature, authorization=authorization)
        print("The response of PublicVerificationApi->verify_embedding_api_v1_public_verify_ref_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicVerificationApi->verify_embedding_api_v1_public_verify_ref_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ref_id** | **str**|  |
 **signature** | **str**| HMAC signature (8+ hex characters) |
 **authorization** | **str**|  | [optional]

### Return type

[**VerifyEmbeddingResponse**](VerifyEmbeddingResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Embedding verified successfully |  -  |
**400** | Invalid request |  -  |
**404** | Embedding not found |  -  |
**429** | Rate limit exceeded |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
