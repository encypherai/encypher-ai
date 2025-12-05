# encypher.StatusRevocationApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_document_status_api_v1_status_documents_document_id_get**](StatusRevocationApi.md#get_document_status_api_v1_status_documents_document_id_get) | **GET** /api/v1/status/documents/{document_id} | Get Document Status
[**get_document_status_api_v1_status_documents_document_id_get_0**](StatusRevocationApi.md#get_document_status_api_v1_status_documents_document_id_get_0) | **GET** /api/v1/status/documents/{document_id} | Get Document Status
[**get_status_list_api_v1_status_list_organization_id_list_index_get**](StatusRevocationApi.md#get_status_list_api_v1_status_list_organization_id_list_index_get) | **GET** /api/v1/status/list/{organization_id}/{list_index} | Get Status List
[**get_status_list_api_v1_status_list_organization_id_list_index_get_0**](StatusRevocationApi.md#get_status_list_api_v1_status_list_organization_id_list_index_get_0) | **GET** /api/v1/status/list/{organization_id}/{list_index} | Get Status List
[**get_status_stats_api_v1_status_stats_get**](StatusRevocationApi.md#get_status_stats_api_v1_status_stats_get) | **GET** /api/v1/status/stats | Get Status Stats
[**get_status_stats_api_v1_status_stats_get_0**](StatusRevocationApi.md#get_status_stats_api_v1_status_stats_get_0) | **GET** /api/v1/status/stats | Get Status Stats
[**reinstate_document_api_v1_status_documents_document_id_reinstate_post**](StatusRevocationApi.md#reinstate_document_api_v1_status_documents_document_id_reinstate_post) | **POST** /api/v1/status/documents/{document_id}/reinstate | Reinstate Document
[**reinstate_document_api_v1_status_documents_document_id_reinstate_post_0**](StatusRevocationApi.md#reinstate_document_api_v1_status_documents_document_id_reinstate_post_0) | **POST** /api/v1/status/documents/{document_id}/reinstate | Reinstate Document
[**revoke_document_api_v1_status_documents_document_id_revoke_post**](StatusRevocationApi.md#revoke_document_api_v1_status_documents_document_id_revoke_post) | **POST** /api/v1/status/documents/{document_id}/revoke | Revoke Document
[**revoke_document_api_v1_status_documents_document_id_revoke_post_0**](StatusRevocationApi.md#revoke_document_api_v1_status_documents_document_id_revoke_post_0) | **POST** /api/v1/status/documents/{document_id}/revoke | Revoke Document


# **get_document_status_api_v1_status_documents_document_id_get**
> DocumentStatusResponse get_document_status_api_v1_status_documents_document_id_get(document_id)

Get Document Status

Get the revocation status of a document.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.document_status_response import DocumentStatusResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
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
    api_instance = encypher.StatusRevocationApi(api_client)
    document_id = 'document_id_example' # str | 

    try:
        # Get Document Status
        api_response = api_instance.get_document_status_api_v1_status_documents_document_id_get(document_id)
        print("The response of StatusRevocationApi->get_document_status_api_v1_status_documents_document_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusRevocationApi->get_document_status_api_v1_status_documents_document_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | 

### Return type

[**DocumentStatusResponse**](DocumentStatusResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_document_status_api_v1_status_documents_document_id_get_0**
> DocumentStatusResponse get_document_status_api_v1_status_documents_document_id_get_0(document_id)

Get Document Status

Get the revocation status of a document.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.document_status_response import DocumentStatusResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
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
    api_instance = encypher.StatusRevocationApi(api_client)
    document_id = 'document_id_example' # str | 

    try:
        # Get Document Status
        api_response = api_instance.get_document_status_api_v1_status_documents_document_id_get_0(document_id)
        print("The response of StatusRevocationApi->get_document_status_api_v1_status_documents_document_id_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusRevocationApi->get_document_status_api_v1_status_documents_document_id_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | 

### Return type

[**DocumentStatusResponse**](DocumentStatusResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_status_list_api_v1_status_list_organization_id_list_index_get**
> object get_status_list_api_v1_status_list_organization_id_list_index_get(organization_id, list_index)

Get Status List

Get a status list credential (public, no auth required).

This endpoint serves W3C StatusList2021 credentials for verification.
Responses are designed to be cached by CDN with 5-minute TTL.

**Response Format:** W3C StatusList2021Credential (JSON-LD)

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.StatusRevocationApi(api_client)
    organization_id = 'organization_id_example' # str | 
    list_index = 56 # int | 

    try:
        # Get Status List
        api_response = api_instance.get_status_list_api_v1_status_list_organization_id_list_index_get(organization_id, list_index)
        print("The response of StatusRevocationApi->get_status_list_api_v1_status_list_organization_id_list_index_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusRevocationApi->get_status_list_api_v1_status_list_organization_id_list_index_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_id** | **str**|  | 
 **list_index** | **int**|  | 

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

# **get_status_list_api_v1_status_list_organization_id_list_index_get_0**
> object get_status_list_api_v1_status_list_organization_id_list_index_get_0(organization_id, list_index)

Get Status List

Get a status list credential (public, no auth required).

This endpoint serves W3C StatusList2021 credentials for verification.
Responses are designed to be cached by CDN with 5-minute TTL.

**Response Format:** W3C StatusList2021Credential (JSON-LD)

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.StatusRevocationApi(api_client)
    organization_id = 'organization_id_example' # str | 
    list_index = 56 # int | 

    try:
        # Get Status List
        api_response = api_instance.get_status_list_api_v1_status_list_organization_id_list_index_get_0(organization_id, list_index)
        print("The response of StatusRevocationApi->get_status_list_api_v1_status_list_organization_id_list_index_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusRevocationApi->get_status_list_api_v1_status_list_organization_id_list_index_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization_id** | **str**|  | 
 **list_index** | **int**|  | 

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

# **get_status_stats_api_v1_status_stats_get**
> object get_status_stats_api_v1_status_stats_get()

Get Status Stats

Get status list statistics for the organization.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
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
    api_instance = encypher.StatusRevocationApi(api_client)

    try:
        # Get Status Stats
        api_response = api_instance.get_status_stats_api_v1_status_stats_get()
        print("The response of StatusRevocationApi->get_status_stats_api_v1_status_stats_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusRevocationApi->get_status_stats_api_v1_status_stats_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_status_stats_api_v1_status_stats_get_0**
> object get_status_stats_api_v1_status_stats_get_0()

Get Status Stats

Get status list statistics for the organization.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
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
    api_instance = encypher.StatusRevocationApi(api_client)

    try:
        # Get Status Stats
        api_response = api_instance.get_status_stats_api_v1_status_stats_get_0()
        print("The response of StatusRevocationApi->get_status_stats_api_v1_status_stats_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusRevocationApi->get_status_stats_api_v1_status_stats_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reinstate_document_api_v1_status_documents_document_id_reinstate_post**
> RevocationResponse reinstate_document_api_v1_status_documents_document_id_reinstate_post(document_id)

Reinstate Document

Reinstate a previously revoked document.

The document will pass verification again within 5 minutes (CDN cache TTL).

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.revocation_response import RevocationResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
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
    api_instance = encypher.StatusRevocationApi(api_client)
    document_id = 'document_id_example' # str | 

    try:
        # Reinstate Document
        api_response = api_instance.reinstate_document_api_v1_status_documents_document_id_reinstate_post(document_id)
        print("The response of StatusRevocationApi->reinstate_document_api_v1_status_documents_document_id_reinstate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusRevocationApi->reinstate_document_api_v1_status_documents_document_id_reinstate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | 

### Return type

[**RevocationResponse**](RevocationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reinstate_document_api_v1_status_documents_document_id_reinstate_post_0**
> RevocationResponse reinstate_document_api_v1_status_documents_document_id_reinstate_post_0(document_id)

Reinstate Document

Reinstate a previously revoked document.

The document will pass verification again within 5 minutes (CDN cache TTL).

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.revocation_response import RevocationResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
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
    api_instance = encypher.StatusRevocationApi(api_client)
    document_id = 'document_id_example' # str | 

    try:
        # Reinstate Document
        api_response = api_instance.reinstate_document_api_v1_status_documents_document_id_reinstate_post_0(document_id)
        print("The response of StatusRevocationApi->reinstate_document_api_v1_status_documents_document_id_reinstate_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusRevocationApi->reinstate_document_api_v1_status_documents_document_id_reinstate_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | 

### Return type

[**RevocationResponse**](RevocationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revoke_document_api_v1_status_documents_document_id_revoke_post**
> RevocationResponse revoke_document_api_v1_status_documents_document_id_revoke_post(document_id, revoke_request)

Revoke Document

Revoke a document's authenticity.

The document will fail verification within 5 minutes (CDN cache TTL).
This action is reversible via the reinstate endpoint.

**Revocation Reasons:**
- `factual_error`: Content contains factual errors
- `legal_takedown`: Legal request (DMCA, court order)
- `copyright_claim`: Copyright infringement claim
- `privacy_request`: Privacy/GDPR request
- `publisher_request`: Publisher-initiated takedown
- `security_concern`: Security vulnerability in content
- `content_policy`: Violates content policy
- `other`: Other reason (specify in reason_detail)

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.revocation_response import RevocationResponse
from encypher.models.revoke_request import RevokeRequest
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
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
    api_instance = encypher.StatusRevocationApi(api_client)
    document_id = 'document_id_example' # str | 
    revoke_request = encypher.RevokeRequest() # RevokeRequest | 

    try:
        # Revoke Document
        api_response = api_instance.revoke_document_api_v1_status_documents_document_id_revoke_post(document_id, revoke_request)
        print("The response of StatusRevocationApi->revoke_document_api_v1_status_documents_document_id_revoke_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusRevocationApi->revoke_document_api_v1_status_documents_document_id_revoke_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | 
 **revoke_request** | [**RevokeRequest**](RevokeRequest.md)|  | 

### Return type

[**RevocationResponse**](RevocationResponse.md)

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

# **revoke_document_api_v1_status_documents_document_id_revoke_post_0**
> RevocationResponse revoke_document_api_v1_status_documents_document_id_revoke_post_0(document_id, revoke_request)

Revoke Document

Revoke a document's authenticity.

The document will fail verification within 5 minutes (CDN cache TTL).
This action is reversible via the reinstate endpoint.

**Revocation Reasons:**
- `factual_error`: Content contains factual errors
- `legal_takedown`: Legal request (DMCA, court order)
- `copyright_claim`: Copyright infringement claim
- `privacy_request`: Privacy/GDPR request
- `publisher_request`: Publisher-initiated takedown
- `security_concern`: Security vulnerability in content
- `content_policy`: Violates content policy
- `other`: Other reason (specify in reason_detail)

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.revocation_response import RevocationResponse
from encypher.models.revoke_request import RevokeRequest
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
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
    api_instance = encypher.StatusRevocationApi(api_client)
    document_id = 'document_id_example' # str | 
    revoke_request = encypher.RevokeRequest() # RevokeRequest | 

    try:
        # Revoke Document
        api_response = api_instance.revoke_document_api_v1_status_documents_document_id_revoke_post_0(document_id, revoke_request)
        print("The response of StatusRevocationApi->revoke_document_api_v1_status_documents_document_id_revoke_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StatusRevocationApi->revoke_document_api_v1_status_documents_document_id_revoke_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | 
 **revoke_request** | [**RevokeRequest**](RevokeRequest.md)|  | 

### Return type

[**RevocationResponse**](RevocationResponse.md)

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

