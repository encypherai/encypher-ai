# encypher.PublicC2PAApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_manifest_api_v1_public_c2pa_create_manifest_post**](PublicC2PAApi.md#create_manifest_api_v1_public_c2pa_create_manifest_post) | **POST** /api/v1/public/c2pa/create-manifest | Create C2PA-like manifest JSON from plaintext (Public - Non-Cryptographic)
[**get_trust_anchor_api_v1_public_c2pa_trust_anchors_signer_id_get**](PublicC2PAApi.md#get_trust_anchor_api_v1_public_c2pa_trust_anchors_signer_id_get) | **GET** /api/v1/public/c2pa/trust-anchors/{signer_id} | Lookup trust anchor for C2PA verification (Public)
[**validate_manifest_api_v1_public_c2pa_validate_manifest_post**](PublicC2PAApi.md#validate_manifest_api_v1_public_c2pa_validate_manifest_post) | **POST** /api/v1/public/c2pa/validate-manifest | Validate C2PA-like manifest JSON (Public - Non-Cryptographic)


# **create_manifest_api_v1_public_c2pa_create_manifest_post**
> CreateManifestResponse create_manifest_api_v1_public_c2pa_create_manifest_post(create_manifest_request, authorization=authorization)

Create C2PA-like manifest JSON from plaintext (Public - Non-Cryptographic)

### Example


```python
import encypher
from encypher.models.create_manifest_request import CreateManifestRequest
from encypher.models.create_manifest_response import CreateManifestResponse
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
    api_instance = encypher.PublicC2PAApi(api_client)
    create_manifest_request = encypher.CreateManifestRequest() # CreateManifestRequest | 
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Create C2PA-like manifest JSON from plaintext (Public - Non-Cryptographic)
        api_response = api_instance.create_manifest_api_v1_public_c2pa_create_manifest_post(create_manifest_request, authorization=authorization)
        print("The response of PublicC2PAApi->create_manifest_api_v1_public_c2pa_create_manifest_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicC2PAApi->create_manifest_api_v1_public_c2pa_create_manifest_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_manifest_request** | [**CreateManifestRequest**](CreateManifestRequest.md)|  | 
 **authorization** | **str**|  | [optional] 

### Return type

[**CreateManifestResponse**](CreateManifestResponse.md)

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

# **get_trust_anchor_api_v1_public_c2pa_trust_anchors_signer_id_get**
> TrustAnchorResponse get_trust_anchor_api_v1_public_c2pa_trust_anchors_signer_id_get(signer_id)

Lookup trust anchor for C2PA verification (Public)

Lookup a trust anchor (public key) for external C2PA validators.

This endpoint enables third-party validators to verify Encypher-signed
content by providing the signer's public key. This implements the
"Private Credential Store" model per C2PA spec §14.4.3.

**Special signer IDs:**
- `encypher.public` or `org_demo`: Returns Encypher's official demo/free-tier key
- `demo-*`: Returns demo/test keys (non-production)

**C2PA Spec Reference:**
https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_trust_lists

### Example


```python
import encypher
from encypher.models.trust_anchor_response import TrustAnchorResponse
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
    api_instance = encypher.PublicC2PAApi(api_client)
    signer_id = 'signer_id_example' # str | Signer identifier from manifest

    try:
        # Lookup trust anchor for C2PA verification (Public)
        api_response = api_instance.get_trust_anchor_api_v1_public_c2pa_trust_anchors_signer_id_get(signer_id)
        print("The response of PublicC2PAApi->get_trust_anchor_api_v1_public_c2pa_trust_anchors_signer_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicC2PAApi->get_trust_anchor_api_v1_public_c2pa_trust_anchors_signer_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **signer_id** | **str**| Signer identifier from manifest | 

### Return type

[**TrustAnchorResponse**](TrustAnchorResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Signer not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validate_manifest_api_v1_public_c2pa_validate_manifest_post**
> ValidateManifestResponse validate_manifest_api_v1_public_c2pa_validate_manifest_post(validate_manifest_request, authorization=authorization)

Validate C2PA-like manifest JSON (Public - Non-Cryptographic)

### Example


```python
import encypher
from encypher.models.validate_manifest_request import ValidateManifestRequest
from encypher.models.validate_manifest_response import ValidateManifestResponse
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
    api_instance = encypher.PublicC2PAApi(api_client)
    validate_manifest_request = encypher.ValidateManifestRequest() # ValidateManifestRequest | 
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Validate C2PA-like manifest JSON (Public - Non-Cryptographic)
        api_response = api_instance.validate_manifest_api_v1_public_c2pa_validate_manifest_post(validate_manifest_request, authorization=authorization)
        print("The response of PublicC2PAApi->validate_manifest_api_v1_public_c2pa_validate_manifest_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicC2PAApi->validate_manifest_api_v1_public_c2pa_validate_manifest_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **validate_manifest_request** | [**ValidateManifestRequest**](ValidateManifestRequest.md)|  | 
 **authorization** | **str**|  | [optional] 

### Return type

[**ValidateManifestResponse**](ValidateManifestResponse.md)

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

