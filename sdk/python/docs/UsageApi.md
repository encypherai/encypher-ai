# encypher.UsageApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_usage_history_api_v1_usage_history_get**](UsageApi.md#get_usage_history_api_v1_usage_history_get) | **GET** /api/v1/usage/history | Get Usage History
[**get_usage_stats_api_v1_usage_get**](UsageApi.md#get_usage_stats_api_v1_usage_get) | **GET** /api/v1/usage | Get Usage Stats


# **get_usage_history_api_v1_usage_history_get**
> object get_usage_history_api_v1_usage_history_get(months=months)

Get Usage History

Get historical usage data for the organization.

Returns monthly usage summaries for the specified number of months.

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
    api_instance = encypher.UsageApi(api_client)
    months = 6 # int |  (optional) (default to 6)

    try:
        # Get Usage History
        api_response = api_instance.get_usage_history_api_v1_usage_history_get(months=months)
        print("The response of UsageApi->get_usage_history_api_v1_usage_history_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsageApi->get_usage_history_api_v1_usage_history_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **months** | **int**|  | [optional] [default to 6]

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_usage_stats_api_v1_usage_get**
> UsageResponse get_usage_stats_api_v1_usage_get()

Get Usage Stats

Get current period usage statistics for the organization.

Returns usage metrics including:
- C2PA signatures (documents signed)
- Sentences tracked
- Batch operations
- API calls

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.usage_response import UsageResponse
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
    api_instance = encypher.UsageApi(api_client)

    try:
        # Get Usage Stats
        api_response = api_instance.get_usage_stats_api_v1_usage_get()
        print("The response of UsageApi->get_usage_stats_api_v1_usage_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsageApi->get_usage_stats_api_v1_usage_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**UsageResponse**](UsageResponse.md)

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

