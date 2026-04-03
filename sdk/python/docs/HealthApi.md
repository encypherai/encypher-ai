# encypher.HealthApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**health_check_health_get**](HealthApi.md#health_check_health_get) | **GET** /health | Health Check
[**readiness_check_readyz_get**](HealthApi.md#readiness_check_readyz_get) | **GET** /readyz | Readiness Check


# **health_check_health_get**
> object health_check_health_get()

Health Check

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
    api_instance = encypher.HealthApi(api_client)

    try:
        # Health Check
        api_response = api_instance.health_check_health_get()
        print("The response of HealthApi->health_check_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthApi->health_check_health_get: %s\n" % e)
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

# **readiness_check_readyz_get**
> object readiness_check_readyz_get()

Readiness Check

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
    api_instance = encypher.HealthApi(api_client)

    try:
        # Readiness Check
        api_response = api_instance.readiness_check_readyz_get()
        print("The response of HealthApi->readiness_check_readyz_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthApi->readiness_check_readyz_get: %s\n" % e)
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
