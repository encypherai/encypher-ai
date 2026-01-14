# encypher.MultiSourceAttributionApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**multi_source_lookup_api_v1_enterprise_attribution_multi_source_post**](MultiSourceAttributionApi.md#multi_source_lookup_api_v1_enterprise_attribution_multi_source_post) | **POST** /api/v1/enterprise/attribution/multi-source | Multi Source Lookup


# **multi_source_lookup_api_v1_enterprise_attribution_multi_source_post**
> MultiSourceLookupResponse multi_source_lookup_api_v1_enterprise_attribution_multi_source_post(multi_source_lookup_request)

Multi Source Lookup

Look up content across multiple sources.

Returns all matching sources with linked-list tracking,
chronological ordering, and optional authority ranking.

**Tier Requirement:** Business+ (Authority ranking requires Enterprise)

Patent Reference: FIG. 8 - Multi-Source Hash Table Lookup

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.multi_source_lookup_request import MultiSourceLookupRequest
from encypher.models.multi_source_lookup_response import MultiSourceLookupResponse
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
    api_instance = encypher.MultiSourceAttributionApi(api_client)
    multi_source_lookup_request = encypher.MultiSourceLookupRequest() # MultiSourceLookupRequest | 

    try:
        # Multi Source Lookup
        api_response = api_instance.multi_source_lookup_api_v1_enterprise_attribution_multi_source_post(multi_source_lookup_request)
        print("The response of MultiSourceAttributionApi->multi_source_lookup_api_v1_enterprise_attribution_multi_source_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MultiSourceAttributionApi->multi_source_lookup_api_v1_enterprise_attribution_multi_source_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **multi_source_lookup_request** | [**MultiSourceLookupRequest**](MultiSourceLookupRequest.md)|  | 

### Return type

[**MultiSourceLookupResponse**](MultiSourceLookupResponse.md)

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

