# encypher.InfoApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**root_get**](InfoApi.md#root_get) | **GET** / | Root


# **root_get**
> object root_get()

Root

API root endpoint with basic information.

Returns:
    dict: API information

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
    api_instance = encypher.InfoApi(api_client)

    try:
        # Root
        api_response = api_instance.root_get()
        print("The response of InfoApi->root_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InfoApi->root_get: %s\n" % e)
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

