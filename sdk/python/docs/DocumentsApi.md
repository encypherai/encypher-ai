# encypher.DocumentsApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_document_api_v1_documents_document_id_delete**](DocumentsApi.md#delete_document_api_v1_documents_document_id_delete) | **DELETE** /api/v1/documents/{document_id} | Delete Document
[**delete_document_api_v1_documents_document_id_delete_0**](DocumentsApi.md#delete_document_api_v1_documents_document_id_delete_0) | **DELETE** /api/v1/documents/{document_id} | Delete Document
[**get_document_api_v1_documents_document_id_get**](DocumentsApi.md#get_document_api_v1_documents_document_id_get) | **GET** /api/v1/documents/{document_id} | Get Document
[**get_document_api_v1_documents_document_id_get_0**](DocumentsApi.md#get_document_api_v1_documents_document_id_get_0) | **GET** /api/v1/documents/{document_id} | Get Document
[**get_document_history_api_v1_documents_document_id_history_get**](DocumentsApi.md#get_document_history_api_v1_documents_document_id_history_get) | **GET** /api/v1/documents/{document_id}/history | Get Document History
[**get_document_history_api_v1_documents_document_id_history_get_0**](DocumentsApi.md#get_document_history_api_v1_documents_document_id_history_get_0) | **GET** /api/v1/documents/{document_id}/history | Get Document History
[**list_documents_api_v1_documents_get**](DocumentsApi.md#list_documents_api_v1_documents_get) | **GET** /api/v1/documents | List Documents
[**list_documents_api_v1_documents_get_0**](DocumentsApi.md#list_documents_api_v1_documents_get_0) | **GET** /api/v1/documents | List Documents


# **delete_document_api_v1_documents_document_id_delete**
> DocumentDeleteResponse delete_document_api_v1_documents_document_id_delete(document_id, revoke=revoke, reason=reason)

Delete Document

Soft delete a document.

By default, this also revokes the document so it will fail verification.
The document is not permanently deleted but marked as deleted.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.document_delete_response import DocumentDeleteResponse
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
    api_instance = encypher.DocumentsApi(api_client)
    document_id = 'document_id_example' # str |
    revoke = True # bool | Also revoke the document (optional) (default to True)
    reason = 'reason_example' # str | Reason for deletion (optional)

    try:
        # Delete Document
        api_response = api_instance.delete_document_api_v1_documents_document_id_delete(document_id, revoke=revoke, reason=reason)
        print("The response of DocumentsApi->delete_document_api_v1_documents_document_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->delete_document_api_v1_documents_document_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  |
 **revoke** | **bool**| Also revoke the document | [optional] [default to True]
 **reason** | **str**| Reason for deletion | [optional]

### Return type

[**DocumentDeleteResponse**](DocumentDeleteResponse.md)

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

# **delete_document_api_v1_documents_document_id_delete_0**
> DocumentDeleteResponse delete_document_api_v1_documents_document_id_delete_0(document_id, revoke=revoke, reason=reason)

Delete Document

Soft delete a document.

By default, this also revokes the document so it will fail verification.
The document is not permanently deleted but marked as deleted.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.document_delete_response import DocumentDeleteResponse
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
    api_instance = encypher.DocumentsApi(api_client)
    document_id = 'document_id_example' # str |
    revoke = True # bool | Also revoke the document (optional) (default to True)
    reason = 'reason_example' # str | Reason for deletion (optional)

    try:
        # Delete Document
        api_response = api_instance.delete_document_api_v1_documents_document_id_delete_0(document_id, revoke=revoke, reason=reason)
        print("The response of DocumentsApi->delete_document_api_v1_documents_document_id_delete_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->delete_document_api_v1_documents_document_id_delete_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  |
 **revoke** | **bool**| Also revoke the document | [optional] [default to True]
 **reason** | **str**| Reason for deletion | [optional]

### Return type

[**DocumentDeleteResponse**](DocumentDeleteResponse.md)

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

# **get_document_api_v1_documents_document_id_get**
> DocumentDetailResponse get_document_api_v1_documents_document_id_get(document_id)

Get Document

Get detailed information about a specific document.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.document_detail_response import DocumentDetailResponse
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
    api_instance = encypher.DocumentsApi(api_client)
    document_id = 'document_id_example' # str |

    try:
        # Get Document
        api_response = api_instance.get_document_api_v1_documents_document_id_get(document_id)
        print("The response of DocumentsApi->get_document_api_v1_documents_document_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->get_document_api_v1_documents_document_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  |

### Return type

[**DocumentDetailResponse**](DocumentDetailResponse.md)

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

# **get_document_api_v1_documents_document_id_get_0**
> DocumentDetailResponse get_document_api_v1_documents_document_id_get_0(document_id)

Get Document

Get detailed information about a specific document.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.document_detail_response import DocumentDetailResponse
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
    api_instance = encypher.DocumentsApi(api_client)
    document_id = 'document_id_example' # str |

    try:
        # Get Document
        api_response = api_instance.get_document_api_v1_documents_document_id_get_0(document_id)
        print("The response of DocumentsApi->get_document_api_v1_documents_document_id_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->get_document_api_v1_documents_document_id_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  |

### Return type

[**DocumentDetailResponse**](DocumentDetailResponse.md)

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

# **get_document_history_api_v1_documents_document_id_history_get**
> DocumentHistoryResponse get_document_history_api_v1_documents_document_id_history_get(document_id)

Get Document History

Get the audit trail/history for a document.

Shows all actions taken on the document including signing, verification, and revocation.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.document_history_response import DocumentHistoryResponse
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
    api_instance = encypher.DocumentsApi(api_client)
    document_id = 'document_id_example' # str |

    try:
        # Get Document History
        api_response = api_instance.get_document_history_api_v1_documents_document_id_history_get(document_id)
        print("The response of DocumentsApi->get_document_history_api_v1_documents_document_id_history_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->get_document_history_api_v1_documents_document_id_history_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  |

### Return type

[**DocumentHistoryResponse**](DocumentHistoryResponse.md)

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

# **get_document_history_api_v1_documents_document_id_history_get_0**
> DocumentHistoryResponse get_document_history_api_v1_documents_document_id_history_get_0(document_id)

Get Document History

Get the audit trail/history for a document.

Shows all actions taken on the document including signing, verification, and revocation.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.document_history_response import DocumentHistoryResponse
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
    api_instance = encypher.DocumentsApi(api_client)
    document_id = 'document_id_example' # str |

    try:
        # Get Document History
        api_response = api_instance.get_document_history_api_v1_documents_document_id_history_get_0(document_id)
        print("The response of DocumentsApi->get_document_history_api_v1_documents_document_id_history_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->get_document_history_api_v1_documents_document_id_history_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  |

### Return type

[**DocumentHistoryResponse**](DocumentHistoryResponse.md)

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

# **list_documents_api_v1_documents_get**
> DocumentListResponse list_documents_api_v1_documents_get(page=page, page_size=page_size, search=search, status=status, from_date=from_date, to_date=to_date)

List Documents

List signed documents for the organization.

Supports pagination, search, and filtering by status and date range.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.document_list_response import DocumentListResponse
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
    api_instance = encypher.DocumentsApi(api_client)
    page = 1 # int | Page number (optional) (default to 1)
    page_size = 50 # int | Items per page (optional) (default to 50)
    search = 'search_example' # str | Search in title (optional)
    status = 'status_example' # str | Filter by status (active/revoked) (optional)
    from_date = 'from_date_example' # str | Filter from date (ISO format) (optional)
    to_date = 'to_date_example' # str | Filter to date (ISO format) (optional)

    try:
        # List Documents
        api_response = api_instance.list_documents_api_v1_documents_get(page=page, page_size=page_size, search=search, status=status, from_date=from_date, to_date=to_date)
        print("The response of DocumentsApi->list_documents_api_v1_documents_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->list_documents_api_v1_documents_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**| Page number | [optional] [default to 1]
 **page_size** | **int**| Items per page | [optional] [default to 50]
 **search** | **str**| Search in title | [optional]
 **status** | **str**| Filter by status (active/revoked) | [optional]
 **from_date** | **str**| Filter from date (ISO format) | [optional]
 **to_date** | **str**| Filter to date (ISO format) | [optional]

### Return type

[**DocumentListResponse**](DocumentListResponse.md)

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

# **list_documents_api_v1_documents_get_0**
> DocumentListResponse list_documents_api_v1_documents_get_0(page=page, page_size=page_size, search=search, status=status, from_date=from_date, to_date=to_date)

List Documents

List signed documents for the organization.

Supports pagination, search, and filtering by status and date range.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.document_list_response import DocumentListResponse
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
    api_instance = encypher.DocumentsApi(api_client)
    page = 1 # int | Page number (optional) (default to 1)
    page_size = 50 # int | Items per page (optional) (default to 50)
    search = 'search_example' # str | Search in title (optional)
    status = 'status_example' # str | Filter by status (active/revoked) (optional)
    from_date = 'from_date_example' # str | Filter from date (ISO format) (optional)
    to_date = 'to_date_example' # str | Filter to date (ISO format) (optional)

    try:
        # List Documents
        api_response = api_instance.list_documents_api_v1_documents_get_0(page=page, page_size=page_size, search=search, status=status, from_date=from_date, to_date=to_date)
        print("The response of DocumentsApi->list_documents_api_v1_documents_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->list_documents_api_v1_documents_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**| Page number | [optional] [default to 1]
 **page_size** | **int**| Items per page | [optional] [default to 50]
 **search** | **str**| Search in title | [optional]
 **status** | **str**| Filter by status (active/revoked) | [optional]
 **from_date** | **str**| Filter from date (ISO format) | [optional]
 **to_date** | **str**| Filter to date (ISO format) | [optional]

### Return type

[**DocumentListResponse**](DocumentListResponse.md)

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
