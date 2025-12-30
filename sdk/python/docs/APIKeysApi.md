# encypher.APIKeysApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_key_api_v1_keys_post**](APIKeysApi.md#create_key_api_v1_keys_post) | **POST** /api/v1/keys | Create Key
[**create_key_api_v1_keys_post_0**](APIKeysApi.md#create_key_api_v1_keys_post_0) | **POST** /api/v1/keys | Create Key
[**list_keys_api_v1_keys_get**](APIKeysApi.md#list_keys_api_v1_keys_get) | **GET** /api/v1/keys | List Keys
[**list_keys_api_v1_keys_get_0**](APIKeysApi.md#list_keys_api_v1_keys_get_0) | **GET** /api/v1/keys | List Keys
[**revoke_key_api_v1_keys_key_id_delete**](APIKeysApi.md#revoke_key_api_v1_keys_key_id_delete) | **DELETE** /api/v1/keys/{key_id} | Revoke Key
[**revoke_key_api_v1_keys_key_id_delete_0**](APIKeysApi.md#revoke_key_api_v1_keys_key_id_delete_0) | **DELETE** /api/v1/keys/{key_id} | Revoke Key
[**rotate_key_api_v1_keys_key_id_rotate_post**](APIKeysApi.md#rotate_key_api_v1_keys_key_id_rotate_post) | **POST** /api/v1/keys/{key_id}/rotate | Rotate Key
[**rotate_key_api_v1_keys_key_id_rotate_post_0**](APIKeysApi.md#rotate_key_api_v1_keys_key_id_rotate_post_0) | **POST** /api/v1/keys/{key_id}/rotate | Rotate Key
[**update_key_api_v1_keys_key_id_patch**](APIKeysApi.md#update_key_api_v1_keys_key_id_patch) | **PATCH** /api/v1/keys/{key_id} | Update Key
[**update_key_api_v1_keys_key_id_patch_0**](APIKeysApi.md#update_key_api_v1_keys_key_id_patch_0) | **PATCH** /api/v1/keys/{key_id} | Update Key


# **create_key_api_v1_keys_post**
> KeyCreateResponse create_key_api_v1_keys_post(key_create_request)

Create Key

Create a new API key.

The full key is only returned once - store it securely.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.key_create_request import KeyCreateRequest
from encypher.models.key_create_response import KeyCreateResponse
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
    api_instance = encypher.APIKeysApi(api_client)
    key_create_request = encypher.KeyCreateRequest() # KeyCreateRequest | 

    try:
        # Create Key
        api_response = api_instance.create_key_api_v1_keys_post(key_create_request)
        print("The response of APIKeysApi->create_key_api_v1_keys_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIKeysApi->create_key_api_v1_keys_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key_create_request** | [**KeyCreateRequest**](KeyCreateRequest.md)|  | 

### Return type

[**KeyCreateResponse**](KeyCreateResponse.md)

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

# **create_key_api_v1_keys_post_0**
> KeyCreateResponse create_key_api_v1_keys_post_0(key_create_request)

Create Key

Create a new API key.

The full key is only returned once - store it securely.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.key_create_request import KeyCreateRequest
from encypher.models.key_create_response import KeyCreateResponse
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
    api_instance = encypher.APIKeysApi(api_client)
    key_create_request = encypher.KeyCreateRequest() # KeyCreateRequest | 

    try:
        # Create Key
        api_response = api_instance.create_key_api_v1_keys_post_0(key_create_request)
        print("The response of APIKeysApi->create_key_api_v1_keys_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIKeysApi->create_key_api_v1_keys_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key_create_request** | [**KeyCreateRequest**](KeyCreateRequest.md)|  | 

### Return type

[**KeyCreateResponse**](KeyCreateResponse.md)

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

# **list_keys_api_v1_keys_get**
> KeyListResponse list_keys_api_v1_keys_get(include_revoked=include_revoked)

List Keys

List API keys for the organization.

Keys are masked - only the prefix is shown for security.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.key_list_response import KeyListResponse
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
    api_instance = encypher.APIKeysApi(api_client)
    include_revoked = False # bool | Include revoked keys (optional) (default to False)

    try:
        # List Keys
        api_response = api_instance.list_keys_api_v1_keys_get(include_revoked=include_revoked)
        print("The response of APIKeysApi->list_keys_api_v1_keys_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIKeysApi->list_keys_api_v1_keys_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **include_revoked** | **bool**| Include revoked keys | [optional] [default to False]

### Return type

[**KeyListResponse**](KeyListResponse.md)

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

# **list_keys_api_v1_keys_get_0**
> KeyListResponse list_keys_api_v1_keys_get_0(include_revoked=include_revoked)

List Keys

List API keys for the organization.

Keys are masked - only the prefix is shown for security.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.key_list_response import KeyListResponse
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
    api_instance = encypher.APIKeysApi(api_client)
    include_revoked = False # bool | Include revoked keys (optional) (default to False)

    try:
        # List Keys
        api_response = api_instance.list_keys_api_v1_keys_get_0(include_revoked=include_revoked)
        print("The response of APIKeysApi->list_keys_api_v1_keys_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIKeysApi->list_keys_api_v1_keys_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **include_revoked** | **bool**| Include revoked keys | [optional] [default to False]

### Return type

[**KeyListResponse**](KeyListResponse.md)

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

# **revoke_key_api_v1_keys_key_id_delete**
> KeyRevokeResponse revoke_key_api_v1_keys_key_id_delete(key_id)

Revoke Key

Revoke an API key.

The key will immediately stop working. This action cannot be undone.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.key_revoke_response import KeyRevokeResponse
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
    api_instance = encypher.APIKeysApi(api_client)
    key_id = 'key_id_example' # str | 

    try:
        # Revoke Key
        api_response = api_instance.revoke_key_api_v1_keys_key_id_delete(key_id)
        print("The response of APIKeysApi->revoke_key_api_v1_keys_key_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIKeysApi->revoke_key_api_v1_keys_key_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key_id** | **str**|  | 

### Return type

[**KeyRevokeResponse**](KeyRevokeResponse.md)

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

# **revoke_key_api_v1_keys_key_id_delete_0**
> KeyRevokeResponse revoke_key_api_v1_keys_key_id_delete_0(key_id)

Revoke Key

Revoke an API key.

The key will immediately stop working. This action cannot be undone.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.key_revoke_response import KeyRevokeResponse
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
    api_instance = encypher.APIKeysApi(api_client)
    key_id = 'key_id_example' # str | 

    try:
        # Revoke Key
        api_response = api_instance.revoke_key_api_v1_keys_key_id_delete_0(key_id)
        print("The response of APIKeysApi->revoke_key_api_v1_keys_key_id_delete_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIKeysApi->revoke_key_api_v1_keys_key_id_delete_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key_id** | **str**|  | 

### Return type

[**KeyRevokeResponse**](KeyRevokeResponse.md)

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

# **rotate_key_api_v1_keys_key_id_rotate_post**
> KeyRotateResponse rotate_key_api_v1_keys_key_id_rotate_post(key_id)

Rotate Key

Rotate an API key.

Creates a new key with the same permissions and revokes the old one.
The new key is only returned once - store it securely.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.key_rotate_response import KeyRotateResponse
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
    api_instance = encypher.APIKeysApi(api_client)
    key_id = 'key_id_example' # str | 

    try:
        # Rotate Key
        api_response = api_instance.rotate_key_api_v1_keys_key_id_rotate_post(key_id)
        print("The response of APIKeysApi->rotate_key_api_v1_keys_key_id_rotate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIKeysApi->rotate_key_api_v1_keys_key_id_rotate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key_id** | **str**|  | 

### Return type

[**KeyRotateResponse**](KeyRotateResponse.md)

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

# **rotate_key_api_v1_keys_key_id_rotate_post_0**
> KeyRotateResponse rotate_key_api_v1_keys_key_id_rotate_post_0(key_id)

Rotate Key

Rotate an API key.

Creates a new key with the same permissions and revokes the old one.
The new key is only returned once - store it securely.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.key_rotate_response import KeyRotateResponse
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
    api_instance = encypher.APIKeysApi(api_client)
    key_id = 'key_id_example' # str | 

    try:
        # Rotate Key
        api_response = api_instance.rotate_key_api_v1_keys_key_id_rotate_post_0(key_id)
        print("The response of APIKeysApi->rotate_key_api_v1_keys_key_id_rotate_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIKeysApi->rotate_key_api_v1_keys_key_id_rotate_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key_id** | **str**|  | 

### Return type

[**KeyRotateResponse**](KeyRotateResponse.md)

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

# **update_key_api_v1_keys_key_id_patch**
> KeyUpdateResponse update_key_api_v1_keys_key_id_patch(key_id, key_update_request)

Update Key

Update an API key's name or permissions.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.key_update_request import KeyUpdateRequest
from encypher.models.key_update_response import KeyUpdateResponse
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
    api_instance = encypher.APIKeysApi(api_client)
    key_id = 'key_id_example' # str | 
    key_update_request = encypher.KeyUpdateRequest() # KeyUpdateRequest | 

    try:
        # Update Key
        api_response = api_instance.update_key_api_v1_keys_key_id_patch(key_id, key_update_request)
        print("The response of APIKeysApi->update_key_api_v1_keys_key_id_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIKeysApi->update_key_api_v1_keys_key_id_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key_id** | **str**|  | 
 **key_update_request** | [**KeyUpdateRequest**](KeyUpdateRequest.md)|  | 

### Return type

[**KeyUpdateResponse**](KeyUpdateResponse.md)

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

# **update_key_api_v1_keys_key_id_patch_0**
> KeyUpdateResponse update_key_api_v1_keys_key_id_patch_0(key_id, key_update_request)

Update Key

Update an API key's name or permissions.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.key_update_request import KeyUpdateRequest
from encypher.models.key_update_response import KeyUpdateResponse
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
    api_instance = encypher.APIKeysApi(api_client)
    key_id = 'key_id_example' # str | 
    key_update_request = encypher.KeyUpdateRequest() # KeyUpdateRequest | 

    try:
        # Update Key
        api_response = api_instance.update_key_api_v1_keys_key_id_patch_0(key_id, key_update_request)
        print("The response of APIKeysApi->update_key_api_v1_keys_key_id_patch_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIKeysApi->update_key_api_v1_keys_key_id_patch_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key_id** | **str**|  | 
 **key_update_request** | [**KeyUpdateRequest**](KeyUpdateRequest.md)|  | 

### Return type

[**KeyUpdateResponse**](KeyUpdateResponse.md)

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

