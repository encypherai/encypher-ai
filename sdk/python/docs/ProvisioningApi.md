# encypher.ProvisioningApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**auto_provision_api_v1_provisioning_auto_provision_post**](ProvisioningApi.md#auto_provision_api_v1_provisioning_auto_provision_post) | **POST** /api/v1/provisioning/auto-provision | Auto-provision Organization and API Key
[**create_api_key_api_v1_provisioning_api_keys_post**](ProvisioningApi.md#create_api_key_api_v1_provisioning_api_keys_post) | **POST** /api/v1/provisioning/api-keys | Create API Key
[**create_user_account_api_v1_provisioning_users_post**](ProvisioningApi.md#create_user_account_api_v1_provisioning_users_post) | **POST** /api/v1/provisioning/users | Create User Account
[**list_api_keys_api_v1_provisioning_api_keys_get**](ProvisioningApi.md#list_api_keys_api_v1_provisioning_api_keys_get) | **GET** /api/v1/provisioning/api-keys | List API Keys
[**provisioning_health_api_v1_provisioning_health_get**](ProvisioningApi.md#provisioning_health_api_v1_provisioning_health_get) | **GET** /api/v1/provisioning/health | Provisioning Service Health
[**revoke_api_key_api_v1_provisioning_api_keys_key_id_delete**](ProvisioningApi.md#revoke_api_key_api_v1_provisioning_api_keys_key_id_delete) | **DELETE** /api/v1/provisioning/api-keys/{key_id} | Revoke API Key


# **auto_provision_api_v1_provisioning_auto_provision_post**
> AutoProvisionResponse auto_provision_api_v1_provisioning_auto_provision_post(auto_provision_request, x_provisioning_token=x_provisioning_token)

Auto-provision Organization and API Key

Automatically provision an organization, user account, and API key.
    
    This endpoint is designed for external services to automatically create
    accounts without manual intervention:
    
    **Use Cases:**
    - SDK initialization (auto-create account on first use)
    - WordPress plugin activation (auto-provision on install)
    - CLI tool setup (auto-create account on login)
    - Mobile app onboarding (auto-provision on signup)
    
    **What Gets Created:**
    1. Organization (with specified tier)
    2. User account (associated with email)
    3. API key (for authentication)
    
    **Idempotent:** If organization already exists for email, returns existing
    organization with a new API key.
    
    **Rate Limits:**
    - 10 requests per minute per IP
    - 100 requests per hour per email
    
    **Security:**
    - Requires valid provisioning token (for production)
    - Validates email format
    - Logs all provisioning events

### Example


```python
import encypher
from encypher.models.auto_provision_request import AutoProvisionRequest
from encypher.models.auto_provision_response import AutoProvisionResponse
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
    api_instance = encypher.ProvisioningApi(api_client)
    auto_provision_request = encypher.AutoProvisionRequest() # AutoProvisionRequest | 
    x_provisioning_token = 'x_provisioning_token_example' # str | Provisioning token (optional) (optional)

    try:
        # Auto-provision Organization and API Key
        api_response = api_instance.auto_provision_api_v1_provisioning_auto_provision_post(auto_provision_request, x_provisioning_token=x_provisioning_token)
        print("The response of ProvisioningApi->auto_provision_api_v1_provisioning_auto_provision_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProvisioningApi->auto_provision_api_v1_provisioning_auto_provision_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **auto_provision_request** | [**AutoProvisionRequest**](AutoProvisionRequest.md)|  | 
 **x_provisioning_token** | **str**| Provisioning token (optional) | [optional] 

### Return type

[**AutoProvisionResponse**](AutoProvisionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Organization and API key created successfully |  -  |
**400** | Invalid request |  -  |
**429** | Rate limit exceeded |  -  |
**500** | Server error |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_api_key_api_v1_provisioning_api_keys_post**
> APIKeyResponse create_api_key_api_v1_provisioning_api_keys_post(api_key_create_request)

Create API Key

Create a new API key for an organization

### Example


```python
import encypher
from encypher.models.api_key_create_request import APIKeyCreateRequest
from encypher.models.api_key_response import APIKeyResponse
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
    api_instance = encypher.ProvisioningApi(api_client)
    api_key_create_request = encypher.APIKeyCreateRequest() # APIKeyCreateRequest | 

    try:
        # Create API Key
        api_response = api_instance.create_api_key_api_v1_provisioning_api_keys_post(api_key_create_request)
        print("The response of ProvisioningApi->create_api_key_api_v1_provisioning_api_keys_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProvisioningApi->create_api_key_api_v1_provisioning_api_keys_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_key_create_request** | [**APIKeyCreateRequest**](APIKeyCreateRequest.md)|  | 

### Return type

[**APIKeyResponse**](APIKeyResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_user_account_api_v1_provisioning_users_post**
> UserAccountResponse create_user_account_api_v1_provisioning_users_post(user_account_create_request)

Create User Account

Create a new user account

### Example


```python
import encypher
from encypher.models.user_account_create_request import UserAccountCreateRequest
from encypher.models.user_account_response import UserAccountResponse
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
    api_instance = encypher.ProvisioningApi(api_client)
    user_account_create_request = encypher.UserAccountCreateRequest() # UserAccountCreateRequest | 

    try:
        # Create User Account
        api_response = api_instance.create_user_account_api_v1_provisioning_users_post(user_account_create_request)
        print("The response of ProvisioningApi->create_user_account_api_v1_provisioning_users_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProvisioningApi->create_user_account_api_v1_provisioning_users_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_account_create_request** | [**UserAccountCreateRequest**](UserAccountCreateRequest.md)|  | 

### Return type

[**UserAccountResponse**](UserAccountResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_api_keys_api_v1_provisioning_api_keys_get**
> APIKeyListResponse list_api_keys_api_v1_provisioning_api_keys_get()

List API Keys

List all API keys for an organization

### Example


```python
import encypher
from encypher.models.api_key_list_response import APIKeyListResponse
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
    api_instance = encypher.ProvisioningApi(api_client)

    try:
        # List API Keys
        api_response = api_instance.list_api_keys_api_v1_provisioning_api_keys_get()
        print("The response of ProvisioningApi->list_api_keys_api_v1_provisioning_api_keys_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProvisioningApi->list_api_keys_api_v1_provisioning_api_keys_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**APIKeyListResponse**](APIKeyListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **provisioning_health_api_v1_provisioning_health_get**
> object provisioning_health_api_v1_provisioning_health_get()

Provisioning Service Health

Check if provisioning service is available

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
    api_instance = encypher.ProvisioningApi(api_client)

    try:
        # Provisioning Service Health
        api_response = api_instance.provisioning_health_api_v1_provisioning_health_get()
        print("The response of ProvisioningApi->provisioning_health_api_v1_provisioning_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProvisioningApi->provisioning_health_api_v1_provisioning_health_get: %s\n" % e)
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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revoke_api_key_api_v1_provisioning_api_keys_key_id_delete**
> revoke_api_key_api_v1_provisioning_api_keys_key_id_delete(key_id, api_key_revoke_request)

Revoke API Key

Revoke an API key

### Example


```python
import encypher
from encypher.models.api_key_revoke_request import APIKeyRevokeRequest
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
    api_instance = encypher.ProvisioningApi(api_client)
    key_id = 'key_id_example' # str | 
    api_key_revoke_request = encypher.APIKeyRevokeRequest() # APIKeyRevokeRequest | 

    try:
        # Revoke API Key
        api_instance.revoke_api_key_api_v1_provisioning_api_keys_key_id_delete(key_id, api_key_revoke_request)
    except Exception as e:
        print("Exception when calling ProvisioningApi->revoke_api_key_api_v1_provisioning_api_keys_key_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key_id** | **str**|  | 
 **api_key_revoke_request** | [**APIKeyRevokeRequest**](APIKeyRevokeRequest.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

