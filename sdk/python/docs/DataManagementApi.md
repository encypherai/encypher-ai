# encypher.DataManagementApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**admin_purge_user_api_v1_data_admin_purge_user_post**](DataManagementApi.md#admin_purge_user_api_v1_data_admin_purge_user_post) | **POST** /api/v1/data/admin/purge-user | Admin: purge a user&#39;s data
[**admin_purge_user_api_v1_data_admin_purge_user_post_0**](DataManagementApi.md#admin_purge_user_api_v1_data_admin_purge_user_post_0) | **POST** /api/v1/data/admin/purge-user | Admin: purge a user&#39;s data
[**cancel_deletion_request_api_v1_data_deletion_request_request_id_cancel_post**](DataManagementApi.md#cancel_deletion_request_api_v1_data_deletion_request_request_id_cancel_post) | **POST** /api/v1/data/deletion-request/{request_id}/cancel | Cancel a pending deletion request
[**cancel_deletion_request_api_v1_data_deletion_request_request_id_cancel_post_0**](DataManagementApi.md#cancel_deletion_request_api_v1_data_deletion_request_request_id_cancel_post_0) | **POST** /api/v1/data/deletion-request/{request_id}/cancel | Cancel a pending deletion request
[**confirm_deletion_request_api_v1_data_deletion_request_request_id_confirm_delete**](DataManagementApi.md#confirm_deletion_request_api_v1_data_deletion_request_request_id_confirm_delete) | **DELETE** /api/v1/data/deletion-request/{request_id}/confirm | Confirm and execute a deletion request
[**confirm_deletion_request_api_v1_data_deletion_request_request_id_confirm_delete_0**](DataManagementApi.md#confirm_deletion_request_api_v1_data_deletion_request_request_id_confirm_delete_0) | **DELETE** /api/v1/data/deletion-request/{request_id}/confirm | Confirm and execute a deletion request
[**create_deletion_request_api_v1_data_deletion_request_post**](DataManagementApi.md#create_deletion_request_api_v1_data_deletion_request_post) | **POST** /api/v1/data/deletion-request | Request data deletion (GDPR Art. 17)
[**create_deletion_request_api_v1_data_deletion_request_post_0**](DataManagementApi.md#create_deletion_request_api_v1_data_deletion_request_post_0) | **POST** /api/v1/data/deletion-request | Request data deletion (GDPR Art. 17)
[**get_deletion_receipt_api_v1_data_deletion_request_request_id_receipt_get**](DataManagementApi.md#get_deletion_receipt_api_v1_data_deletion_request_request_id_receipt_get) | **GET** /api/v1/data/deletion-request/{request_id}/receipt | Get deletion receipt
[**get_deletion_receipt_api_v1_data_deletion_request_request_id_receipt_get_0**](DataManagementApi.md#get_deletion_receipt_api_v1_data_deletion_request_request_id_receipt_get_0) | **GET** /api/v1/data/deletion-request/{request_id}/receipt | Get deletion receipt
[**list_deletion_requests_api_v1_data_deletion_requests_get**](DataManagementApi.md#list_deletion_requests_api_v1_data_deletion_requests_get) | **GET** /api/v1/data/deletion-requests | List deletion requests
[**list_deletion_requests_api_v1_data_deletion_requests_get_0**](DataManagementApi.md#list_deletion_requests_api_v1_data_deletion_requests_get_0) | **GET** /api/v1/data/deletion-requests | List deletion requests


# **admin_purge_user_api_v1_data_admin_purge_user_post**
> AdminPurgeResponse admin_purge_user_api_v1_data_admin_purge_user_post(admin_purge_request)

Admin: purge a user's data

Organization admin endpoint to initiate deletion of a specific user's data. Requires admin/owner role. The purge follows the same 90-day window.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.admin_purge_request import AdminPurgeRequest
from encypher.models.admin_purge_response import AdminPurgeResponse
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
    api_instance = encypher.DataManagementApi(api_client)
    admin_purge_request = encypher.AdminPurgeRequest() # AdminPurgeRequest |

    try:
        # Admin: purge a user's data
        api_response = api_instance.admin_purge_user_api_v1_data_admin_purge_user_post(admin_purge_request)
        print("The response of DataManagementApi->admin_purge_user_api_v1_data_admin_purge_user_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->admin_purge_user_api_v1_data_admin_purge_user_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **admin_purge_request** | [**AdminPurgeRequest**](AdminPurgeRequest.md)|  |

### Return type

[**AdminPurgeResponse**](AdminPurgeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **admin_purge_user_api_v1_data_admin_purge_user_post_0**
> AdminPurgeResponse admin_purge_user_api_v1_data_admin_purge_user_post_0(admin_purge_request)

Admin: purge a user's data

Organization admin endpoint to initiate deletion of a specific user's data. Requires admin/owner role. The purge follows the same 90-day window.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.admin_purge_request import AdminPurgeRequest
from encypher.models.admin_purge_response import AdminPurgeResponse
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
    api_instance = encypher.DataManagementApi(api_client)
    admin_purge_request = encypher.AdminPurgeRequest() # AdminPurgeRequest |

    try:
        # Admin: purge a user's data
        api_response = api_instance.admin_purge_user_api_v1_data_admin_purge_user_post_0(admin_purge_request)
        print("The response of DataManagementApi->admin_purge_user_api_v1_data_admin_purge_user_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->admin_purge_user_api_v1_data_admin_purge_user_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **admin_purge_request** | [**AdminPurgeRequest**](AdminPurgeRequest.md)|  |

### Return type

[**AdminPurgeResponse**](AdminPurgeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cancel_deletion_request_api_v1_data_deletion_request_request_id_cancel_post**
> DeletionConfirmResponse cancel_deletion_request_api_v1_data_deletion_request_request_id_cancel_post(request_id)

Cancel a pending deletion request

Cancel a deletion request that has not yet been purged.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.deletion_confirm_response import DeletionConfirmResponse
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
    api_instance = encypher.DataManagementApi(api_client)
    request_id = 'request_id_example' # str |

    try:
        # Cancel a pending deletion request
        api_response = api_instance.cancel_deletion_request_api_v1_data_deletion_request_request_id_cancel_post(request_id)
        print("The response of DataManagementApi->cancel_deletion_request_api_v1_data_deletion_request_request_id_cancel_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->cancel_deletion_request_api_v1_data_deletion_request_request_id_cancel_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_id** | **str**|  |

### Return type

[**DeletionConfirmResponse**](DeletionConfirmResponse.md)

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

# **cancel_deletion_request_api_v1_data_deletion_request_request_id_cancel_post_0**
> DeletionConfirmResponse cancel_deletion_request_api_v1_data_deletion_request_request_id_cancel_post_0(request_id)

Cancel a pending deletion request

Cancel a deletion request that has not yet been purged.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.deletion_confirm_response import DeletionConfirmResponse
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
    api_instance = encypher.DataManagementApi(api_client)
    request_id = 'request_id_example' # str |

    try:
        # Cancel a pending deletion request
        api_response = api_instance.cancel_deletion_request_api_v1_data_deletion_request_request_id_cancel_post_0(request_id)
        print("The response of DataManagementApi->cancel_deletion_request_api_v1_data_deletion_request_request_id_cancel_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->cancel_deletion_request_api_v1_data_deletion_request_request_id_cancel_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_id** | **str**|  |

### Return type

[**DeletionConfirmResponse**](DeletionConfirmResponse.md)

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

# **confirm_deletion_request_api_v1_data_deletion_request_request_id_confirm_delete**
> DeletionConfirmResponse confirm_deletion_request_api_v1_data_deletion_request_request_id_confirm_delete(request_id)

Confirm and execute a deletion request

Confirm a pending deletion request. This begins the data purge process. Account data is soft-deleted immediately and permanently purged after 90 days. Verification records are retained for 7 years.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.deletion_confirm_response import DeletionConfirmResponse
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
    api_instance = encypher.DataManagementApi(api_client)
    request_id = 'request_id_example' # str |

    try:
        # Confirm and execute a deletion request
        api_response = api_instance.confirm_deletion_request_api_v1_data_deletion_request_request_id_confirm_delete(request_id)
        print("The response of DataManagementApi->confirm_deletion_request_api_v1_data_deletion_request_request_id_confirm_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->confirm_deletion_request_api_v1_data_deletion_request_request_id_confirm_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_id** | **str**|  |

### Return type

[**DeletionConfirmResponse**](DeletionConfirmResponse.md)

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

# **confirm_deletion_request_api_v1_data_deletion_request_request_id_confirm_delete_0**
> DeletionConfirmResponse confirm_deletion_request_api_v1_data_deletion_request_request_id_confirm_delete_0(request_id)

Confirm and execute a deletion request

Confirm a pending deletion request. This begins the data purge process. Account data is soft-deleted immediately and permanently purged after 90 days. Verification records are retained for 7 years.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.deletion_confirm_response import DeletionConfirmResponse
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
    api_instance = encypher.DataManagementApi(api_client)
    request_id = 'request_id_example' # str |

    try:
        # Confirm and execute a deletion request
        api_response = api_instance.confirm_deletion_request_api_v1_data_deletion_request_request_id_confirm_delete_0(request_id)
        print("The response of DataManagementApi->confirm_deletion_request_api_v1_data_deletion_request_request_id_confirm_delete_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->confirm_deletion_request_api_v1_data_deletion_request_request_id_confirm_delete_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_id** | **str**|  |

### Return type

[**DeletionConfirmResponse**](DeletionConfirmResponse.md)

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

# **create_deletion_request_api_v1_data_deletion_request_post**
> DeletionRequestResponse create_deletion_request_api_v1_data_deletion_request_post(deletion_request_create)

Request data deletion (GDPR Art. 17)

Submit a request to delete your account or personal data. A 90-day soft-delete window begins immediately. Verification records are retained for 7 years per legal compliance requirements.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.deletion_request_create import DeletionRequestCreate
from encypher.models.deletion_request_response import DeletionRequestResponse
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
    api_instance = encypher.DataManagementApi(api_client)
    deletion_request_create = encypher.DeletionRequestCreate() # DeletionRequestCreate |

    try:
        # Request data deletion (GDPR Art. 17)
        api_response = api_instance.create_deletion_request_api_v1_data_deletion_request_post(deletion_request_create)
        print("The response of DataManagementApi->create_deletion_request_api_v1_data_deletion_request_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->create_deletion_request_api_v1_data_deletion_request_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **deletion_request_create** | [**DeletionRequestCreate**](DeletionRequestCreate.md)|  |

### Return type

[**DeletionRequestResponse**](DeletionRequestResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_deletion_request_api_v1_data_deletion_request_post_0**
> DeletionRequestResponse create_deletion_request_api_v1_data_deletion_request_post_0(deletion_request_create)

Request data deletion (GDPR Art. 17)

Submit a request to delete your account or personal data. A 90-day soft-delete window begins immediately. Verification records are retained for 7 years per legal compliance requirements.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.deletion_request_create import DeletionRequestCreate
from encypher.models.deletion_request_response import DeletionRequestResponse
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
    api_instance = encypher.DataManagementApi(api_client)
    deletion_request_create = encypher.DeletionRequestCreate() # DeletionRequestCreate |

    try:
        # Request data deletion (GDPR Art. 17)
        api_response = api_instance.create_deletion_request_api_v1_data_deletion_request_post_0(deletion_request_create)
        print("The response of DataManagementApi->create_deletion_request_api_v1_data_deletion_request_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->create_deletion_request_api_v1_data_deletion_request_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **deletion_request_create** | [**DeletionRequestCreate**](DeletionRequestCreate.md)|  |

### Return type

[**DeletionRequestResponse**](DeletionRequestResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_deletion_receipt_api_v1_data_deletion_request_request_id_receipt_get**
> DeletionReceiptResponse get_deletion_receipt_api_v1_data_deletion_request_request_id_receipt_get(request_id)

Get deletion receipt

Get a compliance receipt for a deletion request documenting what was deleted and what was retained.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.deletion_receipt_response import DeletionReceiptResponse
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
    api_instance = encypher.DataManagementApi(api_client)
    request_id = 'request_id_example' # str |

    try:
        # Get deletion receipt
        api_response = api_instance.get_deletion_receipt_api_v1_data_deletion_request_request_id_receipt_get(request_id)
        print("The response of DataManagementApi->get_deletion_receipt_api_v1_data_deletion_request_request_id_receipt_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->get_deletion_receipt_api_v1_data_deletion_request_request_id_receipt_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_id** | **str**|  |

### Return type

[**DeletionReceiptResponse**](DeletionReceiptResponse.md)

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

# **get_deletion_receipt_api_v1_data_deletion_request_request_id_receipt_get_0**
> DeletionReceiptResponse get_deletion_receipt_api_v1_data_deletion_request_request_id_receipt_get_0(request_id)

Get deletion receipt

Get a compliance receipt for a deletion request documenting what was deleted and what was retained.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.deletion_receipt_response import DeletionReceiptResponse
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
    api_instance = encypher.DataManagementApi(api_client)
    request_id = 'request_id_example' # str |

    try:
        # Get deletion receipt
        api_response = api_instance.get_deletion_receipt_api_v1_data_deletion_request_request_id_receipt_get_0(request_id)
        print("The response of DataManagementApi->get_deletion_receipt_api_v1_data_deletion_request_request_id_receipt_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->get_deletion_receipt_api_v1_data_deletion_request_request_id_receipt_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_id** | **str**|  |

### Return type

[**DeletionReceiptResponse**](DeletionReceiptResponse.md)

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

# **list_deletion_requests_api_v1_data_deletion_requests_get**
> DeletionRequestListResponse list_deletion_requests_api_v1_data_deletion_requests_get(status=status)

List deletion requests

List all deletion requests for the current organization.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.deletion_request_list_response import DeletionRequestListResponse
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
    api_instance = encypher.DataManagementApi(api_client)
    status = 'status_example' # str | Filter by status: pending, confirmed, completed, cancelled (optional)

    try:
        # List deletion requests
        api_response = api_instance.list_deletion_requests_api_v1_data_deletion_requests_get(status=status)
        print("The response of DataManagementApi->list_deletion_requests_api_v1_data_deletion_requests_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->list_deletion_requests_api_v1_data_deletion_requests_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | **str**| Filter by status: pending, confirmed, completed, cancelled | [optional]

### Return type

[**DeletionRequestListResponse**](DeletionRequestListResponse.md)

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

# **list_deletion_requests_api_v1_data_deletion_requests_get_0**
> DeletionRequestListResponse list_deletion_requests_api_v1_data_deletion_requests_get_0(status=status)

List deletion requests

List all deletion requests for the current organization.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.deletion_request_list_response import DeletionRequestListResponse
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
    api_instance = encypher.DataManagementApi(api_client)
    status = 'status_example' # str | Filter by status: pending, confirmed, completed, cancelled (optional)

    try:
        # List deletion requests
        api_response = api_instance.list_deletion_requests_api_v1_data_deletion_requests_get_0(status=status)
        print("The response of DataManagementApi->list_deletion_requests_api_v1_data_deletion_requests_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->list_deletion_requests_api_v1_data_deletion_requests_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | **str**| Filter by status: pending, confirmed, completed, cancelled | [optional]

### Return type

[**DeletionRequestListResponse**](DeletionRequestListResponse.md)

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
