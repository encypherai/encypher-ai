# encypher.ComplianceApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_compliance_readiness_api_v1_compliance_readiness_get**](ComplianceApi.md#get_compliance_readiness_api_v1_compliance_readiness_get) | **GET** /api/v1/compliance/readiness | Get Compliance Readiness
[**get_compliance_readiness_api_v1_compliance_readiness_get_0**](ComplianceApi.md#get_compliance_readiness_api_v1_compliance_readiness_get_0) | **GET** /api/v1/compliance/readiness | Get Compliance Readiness


# **get_compliance_readiness_api_v1_compliance_readiness_get**
> Dict[str, object] get_compliance_readiness_api_v1_compliance_readiness_get()

Get Compliance Readiness

Return EU AI Act compliance readiness checklist for the organization.

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
    api_instance = encypher.ComplianceApi(api_client)

    try:
        # Get Compliance Readiness
        api_response = api_instance.get_compliance_readiness_api_v1_compliance_readiness_get()
        print("The response of ComplianceApi->get_compliance_readiness_api_v1_compliance_readiness_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ComplianceApi->get_compliance_readiness_api_v1_compliance_readiness_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_compliance_readiness_api_v1_compliance_readiness_get_0**
> Dict[str, object] get_compliance_readiness_api_v1_compliance_readiness_get_0()

Get Compliance Readiness

Return EU AI Act compliance readiness checklist for the organization.

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
    api_instance = encypher.ComplianceApi(api_client)

    try:
        # Get Compliance Readiness
        api_response = api_instance.get_compliance_readiness_api_v1_compliance_readiness_get_0()
        print("The response of ComplianceApi->get_compliance_readiness_api_v1_compliance_readiness_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ComplianceApi->get_compliance_readiness_api_v1_compliance_readiness_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
