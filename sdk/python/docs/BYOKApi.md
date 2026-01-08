# encypher.BYOKApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_public_keys_api_v1_byok_public_keys_get**](BYOKApi.md#list_public_keys_api_v1_byok_public_keys_get) | **GET** /api/v1/byok/public-keys | List public keys
[**list_public_keys_api_v1_byok_public_keys_get_0**](BYOKApi.md#list_public_keys_api_v1_byok_public_keys_get_0) | **GET** /api/v1/byok/public-keys | List public keys
[**register_public_key_api_v1_byok_public_keys_post**](BYOKApi.md#register_public_key_api_v1_byok_public_keys_post) | **POST** /api/v1/byok/public-keys | Register a public key
[**register_public_key_api_v1_byok_public_keys_post_0**](BYOKApi.md#register_public_key_api_v1_byok_public_keys_post_0) | **POST** /api/v1/byok/public-keys | Register a public key
[**revoke_public_key_api_v1_byok_public_keys_key_id_delete**](BYOKApi.md#revoke_public_key_api_v1_byok_public_keys_key_id_delete) | **DELETE** /api/v1/byok/public-keys/{key_id} | Revoke a public key
[**revoke_public_key_api_v1_byok_public_keys_key_id_delete_0**](BYOKApi.md#revoke_public_key_api_v1_byok_public_keys_key_id_delete_0) | **DELETE** /api/v1/byok/public-keys/{key_id} | Revoke a public key


# **list_public_keys_api_v1_byok_public_keys_get**
> PublicKeyListResponse list_public_keys_api_v1_byok_public_keys_get(include_revoked=include_revoked)

List public keys

List all registered public keys for the organization.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.public_key_list_response import PublicKeyListResponse
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
    api_instance = encypher.BYOKApi(api_client)
    include_revoked = False # bool | Include revoked keys (optional) (default to False)

    try:
        # List public keys
        api_response = api_instance.list_public_keys_api_v1_byok_public_keys_get(include_revoked=include_revoked)
        print("The response of BYOKApi->list_public_keys_api_v1_byok_public_keys_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BYOKApi->list_public_keys_api_v1_byok_public_keys_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **include_revoked** | **bool**| Include revoked keys | [optional] [default to False]

### Return type

[**PublicKeyListResponse**](PublicKeyListResponse.md)

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

# **list_public_keys_api_v1_byok_public_keys_get_0**
> PublicKeyListResponse list_public_keys_api_v1_byok_public_keys_get_0(include_revoked=include_revoked)

List public keys

List all registered public keys for the organization.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.public_key_list_response import PublicKeyListResponse
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
    api_instance = encypher.BYOKApi(api_client)
    include_revoked = False # bool | Include revoked keys (optional) (default to False)

    try:
        # List public keys
        api_response = api_instance.list_public_keys_api_v1_byok_public_keys_get_0(include_revoked=include_revoked)
        print("The response of BYOKApi->list_public_keys_api_v1_byok_public_keys_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BYOKApi->list_public_keys_api_v1_byok_public_keys_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **include_revoked** | **bool**| Include revoked keys | [optional] [default to False]

### Return type

[**PublicKeyListResponse**](PublicKeyListResponse.md)

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

# **register_public_key_api_v1_byok_public_keys_post**
> PublicKeyRegisterResponse register_public_key_api_v1_byok_public_keys_post(public_key_register_request)

Register a public key

Register a BYOK public key for signature verification.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.public_key_register_request import PublicKeyRegisterRequest
from encypher.models.public_key_register_response import PublicKeyRegisterResponse
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
    api_instance = encypher.BYOKApi(api_client)
    public_key_register_request = encypher.PublicKeyRegisterRequest() # PublicKeyRegisterRequest | 

    try:
        # Register a public key
        api_response = api_instance.register_public_key_api_v1_byok_public_keys_post(public_key_register_request)
        print("The response of BYOKApi->register_public_key_api_v1_byok_public_keys_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BYOKApi->register_public_key_api_v1_byok_public_keys_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **public_key_register_request** | [**PublicKeyRegisterRequest**](PublicKeyRegisterRequest.md)|  | 

### Return type

[**PublicKeyRegisterResponse**](PublicKeyRegisterResponse.md)

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

# **register_public_key_api_v1_byok_public_keys_post_0**
> PublicKeyRegisterResponse register_public_key_api_v1_byok_public_keys_post_0(public_key_register_request)

Register a public key

Register a BYOK public key for signature verification.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.public_key_register_request import PublicKeyRegisterRequest
from encypher.models.public_key_register_response import PublicKeyRegisterResponse
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
    api_instance = encypher.BYOKApi(api_client)
    public_key_register_request = encypher.PublicKeyRegisterRequest() # PublicKeyRegisterRequest | 

    try:
        # Register a public key
        api_response = api_instance.register_public_key_api_v1_byok_public_keys_post_0(public_key_register_request)
        print("The response of BYOKApi->register_public_key_api_v1_byok_public_keys_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BYOKApi->register_public_key_api_v1_byok_public_keys_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **public_key_register_request** | [**PublicKeyRegisterRequest**](PublicKeyRegisterRequest.md)|  | 

### Return type

[**PublicKeyRegisterResponse**](PublicKeyRegisterResponse.md)

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

# **revoke_public_key_api_v1_byok_public_keys_key_id_delete**
> Dict[str, object] revoke_public_key_api_v1_byok_public_keys_key_id_delete(key_id, reason=reason)

Revoke a public key

Revoke a registered public key. Revoked keys cannot be used for verification.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.BYOKApi(api_client)
    key_id = 'key_id_example' # str | 
    reason = 'reason_example' # str | Reason for revocation (optional)

    try:
        # Revoke a public key
        api_response = api_instance.revoke_public_key_api_v1_byok_public_keys_key_id_delete(key_id, reason=reason)
        print("The response of BYOKApi->revoke_public_key_api_v1_byok_public_keys_key_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BYOKApi->revoke_public_key_api_v1_byok_public_keys_key_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key_id** | **str**|  | 
 **reason** | **str**| Reason for revocation | [optional] 

### Return type

**Dict[str, object]**

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

# **revoke_public_key_api_v1_byok_public_keys_key_id_delete_0**
> Dict[str, object] revoke_public_key_api_v1_byok_public_keys_key_id_delete_0(key_id, reason=reason)

Revoke a public key

Revoke a registered public key. Revoked keys cannot be used for verification.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.BYOKApi(api_client)
    key_id = 'key_id_example' # str | 
    reason = 'reason_example' # str | Reason for revocation (optional)

    try:
        # Revoke a public key
        api_response = api_instance.revoke_public_key_api_v1_byok_public_keys_key_id_delete_0(key_id, reason=reason)
        print("The response of BYOKApi->revoke_public_key_api_v1_byok_public_keys_key_id_delete_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BYOKApi->revoke_public_key_api_v1_byok_public_keys_key_id_delete_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key_id** | **str**|  | 
 **reason** | **str**| Reason for revocation | [optional] 

### Return type

**Dict[str, object]**

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

