# encypher.DiscoveryApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**api_discovery_api_v1_get**](DiscoveryApi.md#api_discovery_api_v1_get) | **GET** /api/v1/ | API Discovery
[**api_discovery_api_v1_get_0**](DiscoveryApi.md#api_discovery_api_v1_get_0) | **GET** /api/v1/ | API Discovery


# **api_discovery_api_v1_get**
> object api_discovery_api_v1_get()

API Discovery

Returns an index of all available API endpoints with summaries.

### Example


```python
import encypher
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
    api_instance = encypher.DiscoveryApi(api_client)

    try:
        # API Discovery
        api_response = api_instance.api_discovery_api_v1_get()
        print("The response of DiscoveryApi->api_discovery_api_v1_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DiscoveryApi->api_discovery_api_v1_get: %s\n" % e)
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

# **api_discovery_api_v1_get_0**
> object api_discovery_api_v1_get_0()

API Discovery

Returns an index of all available API endpoints with summaries.

### Example


```python
import encypher
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
    api_instance = encypher.DiscoveryApi(api_client)

    try:
        # API Discovery
        api_response = api_instance.api_discovery_api_v1_get_0()
        print("The response of DiscoveryApi->api_discovery_api_v1_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DiscoveryApi->api_discovery_api_v1_get_0: %s\n" % e)
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
