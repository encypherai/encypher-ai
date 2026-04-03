# encypher.PublicC2PAApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulk_resolve_segment_uuids_api_v1_public_c2pa_zw_resolve_post**](PublicC2PAApi.md#bulk_resolve_segment_uuids_api_v1_public_c2pa_zw_resolve_post) | **POST** /api/v1/public/c2pa/zw/resolve | Bulk resolve segment UUIDs (Public, internal)
[**create_manifest_api_v1_public_c2pa_create_manifest_post**](PublicC2PAApi.md#create_manifest_api_v1_public_c2pa_create_manifest_post) | **POST** /api/v1/public/c2pa/create-manifest | Create C2PA-like manifest JSON from plaintext (Public - Non-Cryptographic)
[**get_trust_anchor_api_v1_public_c2pa_trust_anchors_signer_id_get**](PublicC2PAApi.md#get_trust_anchor_api_v1_public_c2pa_trust_anchors_signer_id_get) | **GET** /api/v1/public/c2pa/trust-anchors/{signer_id} | Lookup trust anchor for C2PA verification (Public)
[**resolve_zw_segment_uuid_api_v1_public_c2pa_zw_resolve_segment_uuid_get**](PublicC2PAApi.md#resolve_zw_segment_uuid_api_v1_public_c2pa_zw_resolve_segment_uuid_get) | **GET** /api/v1/public/c2pa/zw/resolve/{segment_uuid} | Resolve ZW segment UUID (Public, internal)
[**validate_manifest_api_v1_public_c2pa_validate_manifest_post**](PublicC2PAApi.md#validate_manifest_api_v1_public_c2pa_validate_manifest_post) | **POST** /api/v1/public/c2pa/validate-manifest | Validate C2PA-like manifest JSON (Public - Non-Cryptographic)


# **bulk_resolve_segment_uuids_api_v1_public_c2pa_zw_resolve_post**
> BulkResolveResponse bulk_resolve_segment_uuids_api_v1_public_c2pa_zw_resolve_post(bulk_resolve_request)

Bulk resolve segment UUIDs (Public, internal)

Resolve multiple segment UUIDs in a single call.

Used internally by the verification-service when verifying text that
contains multiple embedded signatures (e.g. a copied paragraph).

### Example


```python
import encypher
from encypher.models.bulk_resolve_request import BulkResolveRequest
from encypher.models.bulk_resolve_response import BulkResolveResponse
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
    api_instance = encypher.PublicC2PAApi(api_client)
    bulk_resolve_request = encypher.BulkResolveRequest() # BulkResolveRequest |

    try:
        # Bulk resolve segment UUIDs (Public, internal)
        api_response = api_instance.bulk_resolve_segment_uuids_api_v1_public_c2pa_zw_resolve_post(bulk_resolve_request)
        print("The response of PublicC2PAApi->bulk_resolve_segment_uuids_api_v1_public_c2pa_zw_resolve_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicC2PAApi->bulk_resolve_segment_uuids_api_v1_public_c2pa_zw_resolve_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bulk_resolve_request** | [**BulkResolveRequest**](BulkResolveRequest.md)|  |

### Return type

[**BulkResolveResponse**](BulkResolveResponse.md)

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

# **create_manifest_api_v1_public_c2pa_create_manifest_post**
> CreateManifestResponse create_manifest_api_v1_public_c2pa_create_manifest_post(create_manifest_request, authorization=authorization)

Create C2PA-like manifest JSON from plaintext (Public - Non-Cryptographic)

Create a C2PA-like manifest JSON payload from plaintext. This endpoint is intended for client-side workflows that want a server-generated starting point for a manifest before cryptographic signing.

Authentication is optional: unauthenticated requests are IP rate-limited; providing an API key may grant higher limits.

### Example


```python
import encypher
from encypher.models.create_manifest_request import CreateManifestRequest
from encypher.models.create_manifest_response import CreateManifestResponse
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

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
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

# **resolve_zw_segment_uuid_api_v1_public_c2pa_zw_resolve_segment_uuid_get**
> ZWResolveResponse resolve_zw_segment_uuid_api_v1_public_c2pa_zw_resolve_segment_uuid_get(segment_uuid)

Resolve ZW segment UUID (Public, internal)

Resolve a ZW (zero-width) embedding segment UUID to its organization.

Used internally by the verification-service to look up ZW embeddings
in the content database without needing direct DB access.

### Example


```python
import encypher
from encypher.models.zw_resolve_response import ZWResolveResponse
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
    api_instance = encypher.PublicC2PAApi(api_client)
    segment_uuid = 'segment_uuid_example' # str | Segment UUID from ZW embedding

    try:
        # Resolve ZW segment UUID (Public, internal)
        api_response = api_instance.resolve_zw_segment_uuid_api_v1_public_c2pa_zw_resolve_segment_uuid_get(segment_uuid)
        print("The response of PublicC2PAApi->resolve_zw_segment_uuid_api_v1_public_c2pa_zw_resolve_segment_uuid_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicC2PAApi->resolve_zw_segment_uuid_api_v1_public_c2pa_zw_resolve_segment_uuid_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **segment_uuid** | **str**| Segment UUID from ZW embedding |

### Return type

[**ZWResolveResponse**](ZWResolveResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Segment UUID not found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validate_manifest_api_v1_public_c2pa_validate_manifest_post**
> ValidateManifestResponse validate_manifest_api_v1_public_c2pa_validate_manifest_post(validate_manifest_request, authorization=authorization)

Validate C2PA-like manifest JSON (Public - Non-Cryptographic)

Validate a manifest JSON payload and (optionally) validate assertion payloads against provided JSON Schemas. This endpoint performs structural/schema validation only and does not verify cryptographic signatures.

Authentication is optional: unauthenticated requests are IP rate-limited; providing an API key may grant higher limits.

### Example


```python
import encypher
from encypher.models.validate_manifest_request import ValidateManifestRequest
from encypher.models.validate_manifest_response import ValidateManifestResponse
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
