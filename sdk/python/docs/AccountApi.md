# encypher.AccountApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_account_info_api_v1_account_get**](AccountApi.md#get_account_info_api_v1_account_get) | **GET** /api/v1/account | Get Account Info
[**get_account_info_api_v1_account_get_0**](AccountApi.md#get_account_info_api_v1_account_get_0) | **GET** /api/v1/account | Get Account Info
[**get_account_quota_api_v1_account_quota_get**](AccountApi.md#get_account_quota_api_v1_account_quota_get) | **GET** /api/v1/account/quota | Get Account Quota
[**get_account_quota_api_v1_account_quota_get_0**](AccountApi.md#get_account_quota_api_v1_account_quota_get_0) | **GET** /api/v1/account/quota | Get Account Quota


# **get_account_info_api_v1_account_get**
> AccountResponse get_account_info_api_v1_account_get()

Get Account Info

Get current organization account information.

Returns organization details including:
- Organization ID and name
- Current subscription tier
- Enabled feature flags
- Account creation date

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.account_response import AccountResponse
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
    api_instance = encypher.AccountApi(api_client)

    try:
        # Get Account Info
        api_response = api_instance.get_account_info_api_v1_account_get()
        print("The response of AccountApi->get_account_info_api_v1_account_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountApi->get_account_info_api_v1_account_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**AccountResponse**](AccountResponse.md)

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

# **get_account_info_api_v1_account_get_0**
> AccountResponse get_account_info_api_v1_account_get_0()

Get Account Info

Get current organization account information.

Returns organization details including:
- Organization ID and name
- Current subscription tier
- Enabled feature flags
- Account creation date

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.account_response import AccountResponse
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
    api_instance = encypher.AccountApi(api_client)

    try:
        # Get Account Info
        api_response = api_instance.get_account_info_api_v1_account_get_0()
        print("The response of AccountApi->get_account_info_api_v1_account_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountApi->get_account_info_api_v1_account_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**AccountResponse**](AccountResponse.md)

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

# **get_account_quota_api_v1_account_quota_get**
> QuotaResponse get_account_quota_api_v1_account_quota_get()

Get Account Quota

Get detailed quota information for the organization.

Returns current usage and limits for:
- C2PA signatures
- Sentences tracked
- Batch operations
- API calls

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.quota_response import QuotaResponse
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
    api_instance = encypher.AccountApi(api_client)

    try:
        # Get Account Quota
        api_response = api_instance.get_account_quota_api_v1_account_quota_get()
        print("The response of AccountApi->get_account_quota_api_v1_account_quota_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountApi->get_account_quota_api_v1_account_quota_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**QuotaResponse**](QuotaResponse.md)

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

# **get_account_quota_api_v1_account_quota_get_0**
> QuotaResponse get_account_quota_api_v1_account_quota_get_0()

Get Account Quota

Get detailed quota information for the organization.

Returns current usage and limits for:
- C2PA signatures
- Sentences tracked
- Batch operations
- API calls

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.quota_response import QuotaResponse
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
    api_instance = encypher.AccountApi(api_client)

    try:
        # Get Account Quota
        api_response = api_instance.get_account_quota_api_v1_account_quota_get_0()
        print("The response of AccountApi->get_account_quota_api_v1_account_quota_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountApi->get_account_quota_api_v1_account_quota_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**QuotaResponse**](QuotaResponse.md)

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
