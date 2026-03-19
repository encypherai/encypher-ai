# encypher.CDNProvenanceApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_manifest_api_v1_cdn_manifests_record_id_get**](CDNProvenanceApi.md#get_manifest_api_v1_cdn_manifests_record_id_get) | **GET** /api/v1/cdn/manifests/{record_id} | Fetch C2PA manifest for a CDN image record
[**get_manifest_api_v1_cdn_manifests_record_id_get_0**](CDNProvenanceApi.md#get_manifest_api_v1_cdn_manifests_record_id_get_0) | **GET** /api/v1/cdn/manifests/{record_id} | Fetch C2PA manifest for a CDN image record
[**lookup_manifest_by_url_api_v1_cdn_manifests_lookup_get**](CDNProvenanceApi.md#lookup_manifest_by_url_api_v1_cdn_manifests_lookup_get) | **GET** /api/v1/cdn/manifests/lookup | Lookup manifest by canonical URL
[**lookup_manifest_by_url_api_v1_cdn_manifests_lookup_get_0**](CDNProvenanceApi.md#lookup_manifest_by_url_api_v1_cdn_manifests_lookup_get_0) | **GET** /api/v1/cdn/manifests/lookup | Lookup manifest by canonical URL
[**pre_register_variants_api_v1_cdn_images_record_id_variants_post**](CDNProvenanceApi.md#pre_register_variants_api_v1_cdn_images_record_id_variants_post) | **POST** /api/v1/cdn/images/{record_id}/variants | Pre-register expected CDN derivative variants
[**pre_register_variants_api_v1_cdn_images_record_id_variants_post_0**](CDNProvenanceApi.md#pre_register_variants_api_v1_cdn_images_record_id_variants_post_0) | **POST** /api/v1/cdn/images/{record_id}/variants | Pre-register expected CDN derivative variants
[**register_image_endpoint_api_v1_cdn_images_register_post**](CDNProvenanceApi.md#register_image_endpoint_api_v1_cdn_images_register_post) | **POST** /api/v1/cdn/images/register | Register a pre-signed image for CDN tracking
[**register_image_endpoint_api_v1_cdn_images_register_post_0**](CDNProvenanceApi.md#register_image_endpoint_api_v1_cdn_images_register_post_0) | **POST** /api/v1/cdn/images/register | Register a pre-signed image for CDN tracking
[**sign_image_endpoint_api_v1_cdn_images_sign_post**](CDNProvenanceApi.md#sign_image_endpoint_api_v1_cdn_images_sign_post) | **POST** /api/v1/cdn/images/sign | Sign image and store provenance manifest
[**sign_image_endpoint_api_v1_cdn_images_sign_post_0**](CDNProvenanceApi.md#sign_image_endpoint_api_v1_cdn_images_sign_post_0) | **POST** /api/v1/cdn/images/sign | Sign image and store provenance manifest
[**verify_image_api_v1_cdn_verify_post**](CDNProvenanceApi.md#verify_image_api_v1_cdn_verify_post) | **POST** /api/v1/cdn/verify | Verify image provenance by upload
[**verify_image_api_v1_cdn_verify_post_0**](CDNProvenanceApi.md#verify_image_api_v1_cdn_verify_post_0) | **POST** /api/v1/cdn/verify | Verify image provenance by upload
[**verify_image_url_api_v1_cdn_verify_url_post**](CDNProvenanceApi.md#verify_image_url_api_v1_cdn_verify_url_post) | **POST** /api/v1/cdn/verify/url | Verify image provenance by URL
[**verify_image_url_api_v1_cdn_verify_url_post_0**](CDNProvenanceApi.md#verify_image_url_api_v1_cdn_verify_url_post_0) | **POST** /api/v1/cdn/verify/url | Verify image provenance by URL
[**well_known_manifest_well_known_c2pa_manifests_record_id_get**](CDNProvenanceApi.md#well_known_manifest_well_known_c2pa_manifests_record_id_get) | **GET** /.well-known/c2pa/manifests/{record_id} | Well-known C2PA manifest discovery
[**well_known_manifest_well_known_c2pa_manifests_record_id_get_0**](CDNProvenanceApi.md#well_known_manifest_well_known_c2pa_manifests_record_id_get_0) | **GET** /.well-known/c2pa/manifests/{record_id} | Well-known C2PA manifest discovery


# **get_manifest_api_v1_cdn_manifests_record_id_get**
> object get_manifest_api_v1_cdn_manifests_record_id_get(record_id)

Fetch C2PA manifest for a CDN image record

Public endpoint to retrieve the stored C2PA manifest for a registered image.

Supports `Accept: application/cbor` for CBOR-encoded manifest response.

No authentication required. IP-based rate limiting recommended in production.

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
    api_instance = encypher.CDNProvenanceApi(api_client)
    record_id = 'record_id_example' # str |

    try:
        # Fetch C2PA manifest for a CDN image record
        api_response = api_instance.get_manifest_api_v1_cdn_manifests_record_id_get(record_id)
        print("The response of CDNProvenanceApi->get_manifest_api_v1_cdn_manifests_record_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->get_manifest_api_v1_cdn_manifests_record_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **record_id** | **str**|  |

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_manifest_api_v1_cdn_manifests_record_id_get_0**
> object get_manifest_api_v1_cdn_manifests_record_id_get_0(record_id)

Fetch C2PA manifest for a CDN image record

Public endpoint to retrieve the stored C2PA manifest for a registered image.

Supports `Accept: application/cbor` for CBOR-encoded manifest response.

No authentication required. IP-based rate limiting recommended in production.

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
    api_instance = encypher.CDNProvenanceApi(api_client)
    record_id = 'record_id_example' # str |

    try:
        # Fetch C2PA manifest for a CDN image record
        api_response = api_instance.get_manifest_api_v1_cdn_manifests_record_id_get_0(record_id)
        print("The response of CDNProvenanceApi->get_manifest_api_v1_cdn_manifests_record_id_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->get_manifest_api_v1_cdn_manifests_record_id_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **record_id** | **str**|  |

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **lookup_manifest_by_url_api_v1_cdn_manifests_lookup_get**
> CdnManifestLookupResponse lookup_manifest_by_url_api_v1_cdn_manifests_lookup_get(url)

Lookup manifest by canonical URL

Find a CDN image record by its canonical original URL.

No authentication required. IP-based rate limiting recommended in production.

### Example


```python
import encypher
from encypher.models.cdn_manifest_lookup_response import CdnManifestLookupResponse
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
    api_instance = encypher.CDNProvenanceApi(api_client)
    url = 'url_example' # str |

    try:
        # Lookup manifest by canonical URL
        api_response = api_instance.lookup_manifest_by_url_api_v1_cdn_manifests_lookup_get(url)
        print("The response of CDNProvenanceApi->lookup_manifest_by_url_api_v1_cdn_manifests_lookup_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->lookup_manifest_by_url_api_v1_cdn_manifests_lookup_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **url** | **str**|  |

### Return type

[**CdnManifestLookupResponse**](CdnManifestLookupResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **lookup_manifest_by_url_api_v1_cdn_manifests_lookup_get_0**
> CdnManifestLookupResponse lookup_manifest_by_url_api_v1_cdn_manifests_lookup_get_0(url)

Lookup manifest by canonical URL

Find a CDN image record by its canonical original URL.

No authentication required. IP-based rate limiting recommended in production.

### Example


```python
import encypher
from encypher.models.cdn_manifest_lookup_response import CdnManifestLookupResponse
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
    api_instance = encypher.CDNProvenanceApi(api_client)
    url = 'url_example' # str |

    try:
        # Lookup manifest by canonical URL
        api_response = api_instance.lookup_manifest_by_url_api_v1_cdn_manifests_lookup_get_0(url)
        print("The response of CDNProvenanceApi->lookup_manifest_by_url_api_v1_cdn_manifests_lookup_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->lookup_manifest_by_url_api_v1_cdn_manifests_lookup_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **url** | **str**|  |

### Return type

[**CdnManifestLookupResponse**](CdnManifestLookupResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **pre_register_variants_api_v1_cdn_images_record_id_variants_post**
> CdnVariantsResponse pre_register_variants_api_v1_cdn_images_record_id_variants_post(record_id, cdn_variants_request)

Pre-register expected CDN derivative variants

Pre-register the expected CDN derivative transforms (resize, reformat, quality
compression, etc.) for a registered image so they can be matched on re-upload.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_variants_request import CdnVariantsRequest
from encypher.models.cdn_variants_response import CdnVariantsResponse
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
    api_instance = encypher.CDNProvenanceApi(api_client)
    record_id = 'record_id_example' # str |
    cdn_variants_request = encypher.CdnVariantsRequest() # CdnVariantsRequest |

    try:
        # Pre-register expected CDN derivative variants
        api_response = api_instance.pre_register_variants_api_v1_cdn_images_record_id_variants_post(record_id, cdn_variants_request)
        print("The response of CDNProvenanceApi->pre_register_variants_api_v1_cdn_images_record_id_variants_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->pre_register_variants_api_v1_cdn_images_record_id_variants_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **record_id** | **str**|  |
 **cdn_variants_request** | [**CdnVariantsRequest**](CdnVariantsRequest.md)|  |

### Return type

[**CdnVariantsResponse**](CdnVariantsResponse.md)

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

# **pre_register_variants_api_v1_cdn_images_record_id_variants_post_0**
> CdnVariantsResponse pre_register_variants_api_v1_cdn_images_record_id_variants_post_0(record_id, cdn_variants_request)

Pre-register expected CDN derivative variants

Pre-register the expected CDN derivative transforms (resize, reformat, quality
compression, etc.) for a registered image so they can be matched on re-upload.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_variants_request import CdnVariantsRequest
from encypher.models.cdn_variants_response import CdnVariantsResponse
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
    api_instance = encypher.CDNProvenanceApi(api_client)
    record_id = 'record_id_example' # str |
    cdn_variants_request = encypher.CdnVariantsRequest() # CdnVariantsRequest |

    try:
        # Pre-register expected CDN derivative variants
        api_response = api_instance.pre_register_variants_api_v1_cdn_images_record_id_variants_post_0(record_id, cdn_variants_request)
        print("The response of CDNProvenanceApi->pre_register_variants_api_v1_cdn_images_record_id_variants_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->pre_register_variants_api_v1_cdn_images_record_id_variants_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **record_id** | **str**|  |
 **cdn_variants_request** | [**CdnVariantsRequest**](CdnVariantsRequest.md)|  |

### Return type

[**CdnVariantsResponse**](CdnVariantsResponse.md)

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

# **register_image_endpoint_api_v1_cdn_images_register_post**
> CdnImageRegisterResponse register_image_endpoint_api_v1_cdn_images_register_post(file, original_url=original_url, manifest_data=manifest_data)

Register a pre-signed image for CDN tracking

Register an already-signed image for CDN provenance tracking without re-signing.
Computes pHash and SHA-256, stores record.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_image_register_response import CdnImageRegisterResponse
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
    api_instance = encypher.CDNProvenanceApi(api_client)
    file = None # bytearray | Image file to register
    original_url = 'original_url_example' # str |  (optional)
    manifest_data = 'manifest_data_example' # str |  (optional)

    try:
        # Register a pre-signed image for CDN tracking
        api_response = api_instance.register_image_endpoint_api_v1_cdn_images_register_post(file, original_url=original_url, manifest_data=manifest_data)
        print("The response of CDNProvenanceApi->register_image_endpoint_api_v1_cdn_images_register_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->register_image_endpoint_api_v1_cdn_images_register_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **bytearray**| Image file to register |
 **original_url** | **str**|  | [optional]
 **manifest_data** | **str**|  | [optional]

### Return type

[**CdnImageRegisterResponse**](CdnImageRegisterResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **register_image_endpoint_api_v1_cdn_images_register_post_0**
> CdnImageRegisterResponse register_image_endpoint_api_v1_cdn_images_register_post_0(file, original_url=original_url, manifest_data=manifest_data)

Register a pre-signed image for CDN tracking

Register an already-signed image for CDN provenance tracking without re-signing.
Computes pHash and SHA-256, stores record.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_image_register_response import CdnImageRegisterResponse
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
    api_instance = encypher.CDNProvenanceApi(api_client)
    file = None # bytearray | Image file to register
    original_url = 'original_url_example' # str |  (optional)
    manifest_data = 'manifest_data_example' # str |  (optional)

    try:
        # Register a pre-signed image for CDN tracking
        api_response = api_instance.register_image_endpoint_api_v1_cdn_images_register_post_0(file, original_url=original_url, manifest_data=manifest_data)
        print("The response of CDNProvenanceApi->register_image_endpoint_api_v1_cdn_images_register_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->register_image_endpoint_api_v1_cdn_images_register_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **bytearray**| Image file to register |
 **original_url** | **str**|  | [optional]
 **manifest_data** | **str**|  | [optional]

### Return type

[**CdnImageRegisterResponse**](CdnImageRegisterResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sign_image_endpoint_api_v1_cdn_images_sign_post**
> CdnImageSignResponse sign_image_endpoint_api_v1_cdn_images_sign_post(file, title=title, original_url=original_url)

Sign image and store provenance manifest

Sign an image with a C2PA manifest and register it in the CDN provenance store.
Returns the signed image bytes (base64), pHash, and SHA-256 for downstream
CDN tracking.

**Enterprise tier only.**

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_image_sign_response import CdnImageSignResponse
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
    api_instance = encypher.CDNProvenanceApi(api_client)
    file = None # bytearray | Image file to sign
    title = 'Untitled Image' # str | Image title for C2PA manifest (optional) (default to 'Untitled Image')
    original_url = 'original_url_example' # str |  (optional)

    try:
        # Sign image and store provenance manifest
        api_response = api_instance.sign_image_endpoint_api_v1_cdn_images_sign_post(file, title=title, original_url=original_url)
        print("The response of CDNProvenanceApi->sign_image_endpoint_api_v1_cdn_images_sign_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->sign_image_endpoint_api_v1_cdn_images_sign_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **bytearray**| Image file to sign |
 **title** | **str**| Image title for C2PA manifest | [optional] [default to &#39;Untitled Image&#39;]
 **original_url** | **str**|  | [optional]

### Return type

[**CdnImageSignResponse**](CdnImageSignResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sign_image_endpoint_api_v1_cdn_images_sign_post_0**
> CdnImageSignResponse sign_image_endpoint_api_v1_cdn_images_sign_post_0(file, title=title, original_url=original_url)

Sign image and store provenance manifest

Sign an image with a C2PA manifest and register it in the CDN provenance store.
Returns the signed image bytes (base64), pHash, and SHA-256 for downstream
CDN tracking.

**Enterprise tier only.**

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_image_sign_response import CdnImageSignResponse
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
    api_instance = encypher.CDNProvenanceApi(api_client)
    file = None # bytearray | Image file to sign
    title = 'Untitled Image' # str | Image title for C2PA manifest (optional) (default to 'Untitled Image')
    original_url = 'original_url_example' # str |  (optional)

    try:
        # Sign image and store provenance manifest
        api_response = api_instance.sign_image_endpoint_api_v1_cdn_images_sign_post_0(file, title=title, original_url=original_url)
        print("The response of CDNProvenanceApi->sign_image_endpoint_api_v1_cdn_images_sign_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->sign_image_endpoint_api_v1_cdn_images_sign_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **bytearray**| Image file to sign |
 **title** | **str**| Image title for C2PA manifest | [optional] [default to &#39;Untitled Image&#39;]
 **original_url** | **str**|  | [optional]

### Return type

[**CdnImageSignResponse**](CdnImageSignResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **verify_image_api_v1_cdn_verify_post**
> CdnVerifyResponse verify_image_api_v1_cdn_verify_post(file)

Verify image provenance by upload

Upload an image to verify its provenance. Attempts (in order):

1. Extract embedded Encypher XMP provenance data.
2. Exact SHA-256 match across all orgs.
3. pHash fuzzy lookup across all orgs (picks lowest Hamming distance).

Returns a verdict: ORIGINAL_SIGNED | VERIFIED_DERIVATIVE | PROVENANCE_LOST.

No authentication required. IP-based rate limiting recommended in production.

### Example


```python
import encypher
from encypher.models.cdn_verify_response import CdnVerifyResponse
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
    api_instance = encypher.CDNProvenanceApi(api_client)
    file = None # bytearray | Image to verify

    try:
        # Verify image provenance by upload
        api_response = api_instance.verify_image_api_v1_cdn_verify_post(file)
        print("The response of CDNProvenanceApi->verify_image_api_v1_cdn_verify_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->verify_image_api_v1_cdn_verify_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **bytearray**| Image to verify |

### Return type

[**CdnVerifyResponse**](CdnVerifyResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **verify_image_api_v1_cdn_verify_post_0**
> CdnVerifyResponse verify_image_api_v1_cdn_verify_post_0(file)

Verify image provenance by upload

Upload an image to verify its provenance. Attempts (in order):

1. Extract embedded Encypher XMP provenance data.
2. Exact SHA-256 match across all orgs.
3. pHash fuzzy lookup across all orgs (picks lowest Hamming distance).

Returns a verdict: ORIGINAL_SIGNED | VERIFIED_DERIVATIVE | PROVENANCE_LOST.

No authentication required. IP-based rate limiting recommended in production.

### Example


```python
import encypher
from encypher.models.cdn_verify_response import CdnVerifyResponse
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
    api_instance = encypher.CDNProvenanceApi(api_client)
    file = None # bytearray | Image to verify

    try:
        # Verify image provenance by upload
        api_response = api_instance.verify_image_api_v1_cdn_verify_post_0(file)
        print("The response of CDNProvenanceApi->verify_image_api_v1_cdn_verify_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->verify_image_api_v1_cdn_verify_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **bytearray**| Image to verify |

### Return type

[**CdnVerifyResponse**](CdnVerifyResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **verify_image_url_api_v1_cdn_verify_url_post**
> CdnVerifyResponse verify_image_url_api_v1_cdn_verify_url_post(url)

Verify image provenance by URL

Fetch an image from a URL then run the same provenance verification as
POST /cdn/verify.

No authentication required. IP-based rate limiting recommended in production.

### Example


```python
import encypher
from encypher.models.cdn_verify_response import CdnVerifyResponse
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
    api_instance = encypher.CDNProvenanceApi(api_client)
    url = 'url_example' # str |

    try:
        # Verify image provenance by URL
        api_response = api_instance.verify_image_url_api_v1_cdn_verify_url_post(url)
        print("The response of CDNProvenanceApi->verify_image_url_api_v1_cdn_verify_url_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->verify_image_url_api_v1_cdn_verify_url_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **url** | **str**|  |

### Return type

[**CdnVerifyResponse**](CdnVerifyResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **verify_image_url_api_v1_cdn_verify_url_post_0**
> CdnVerifyResponse verify_image_url_api_v1_cdn_verify_url_post_0(url)

Verify image provenance by URL

Fetch an image from a URL then run the same provenance verification as
POST /cdn/verify.

No authentication required. IP-based rate limiting recommended in production.

### Example


```python
import encypher
from encypher.models.cdn_verify_response import CdnVerifyResponse
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
    api_instance = encypher.CDNProvenanceApi(api_client)
    url = 'url_example' # str |

    try:
        # Verify image provenance by URL
        api_response = api_instance.verify_image_url_api_v1_cdn_verify_url_post_0(url)
        print("The response of CDNProvenanceApi->verify_image_url_api_v1_cdn_verify_url_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->verify_image_url_api_v1_cdn_verify_url_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **url** | **str**|  |

### Return type

[**CdnVerifyResponse**](CdnVerifyResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **well_known_manifest_well_known_c2pa_manifests_record_id_get**
> object well_known_manifest_well_known_c2pa_manifests_record_id_get(record_id)

Well-known C2PA manifest discovery

Standards-aligned discovery alias. Redirects to the canonical manifest endpoint.

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
    api_instance = encypher.CDNProvenanceApi(api_client)
    record_id = 'record_id_example' # str |

    try:
        # Well-known C2PA manifest discovery
        api_response = api_instance.well_known_manifest_well_known_c2pa_manifests_record_id_get(record_id)
        print("The response of CDNProvenanceApi->well_known_manifest_well_known_c2pa_manifests_record_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->well_known_manifest_well_known_c2pa_manifests_record_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **record_id** | **str**|  |

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **well_known_manifest_well_known_c2pa_manifests_record_id_get_0**
> object well_known_manifest_well_known_c2pa_manifests_record_id_get_0(record_id)

Well-known C2PA manifest discovery

Standards-aligned discovery alias. Redirects to the canonical manifest endpoint.

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
    api_instance = encypher.CDNProvenanceApi(api_client)
    record_id = 'record_id_example' # str |

    try:
        # Well-known C2PA manifest discovery
        api_response = api_instance.well_known_manifest_well_known_c2pa_manifests_record_id_get_0(record_id)
        print("The response of CDNProvenanceApi->well_known_manifest_well_known_c2pa_manifests_record_id_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNProvenanceApi->well_known_manifest_well_known_c2pa_manifests_record_id_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **record_id** | **str**|  |

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
