# encypher.SigningApi

All URIs are relative to *https://api.encypherai.com*

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

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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

**Tier Feature Matrix:**

| Feature | Free/Starter | Professional | Business | Enterprise |
|---------|--------------|--------------|----------|------------|
| Basic C2PA signing | ✅ | ✅ | ✅ | ✅ |
| Sentence segmentation | ❌ | ✅ | ✅ | ✅ |
| Advanced manifest modes | ❌ | ✅ | ✅ | ✅ |
| Attribution indexing | ❌ | ✅ | ✅ | ✅ |
| Custom assertions | ❌ | ❌ | ✅ | ✅ |
| Rights metadata | ❌ | ❌ | ✅ | ✅ |
| Dual binding | ❌ | ❌ | ❌ | ✅ |
| Fingerprinting | ❌ | ❌ | ❌ | ✅ |
| Batch size | 1 | 10 | 50 | 100 |

**Single Document:**
```json
{
    "text": "Content to sign...",
    "document_title": "My Article",
    "options": {
        "segmentation_level": "sentence"
    }
}
```

**Batch (Professional+):**
```json
{
    "documents": [
        {"text": "First doc...", "document_title": "Doc 1"},
        {"text": "Second doc...", "document_title": "Doc 2"}
    ],
    "options": {
        "segmentation_level": "sentence"
    }
}
```

The response includes `meta.features_gated` showing features available at higher tiers.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.unified_sign_request import UnifiedSignRequest
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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

