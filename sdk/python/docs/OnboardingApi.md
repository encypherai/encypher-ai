# encypher.OnboardingApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_certificate_status_api_v1_onboarding_certificate_status_get**](OnboardingApi.md#get_certificate_status_api_v1_onboarding_certificate_status_get) | **GET** /api/v1/onboarding/certificate-status | Get Certificate Status
[**request_certificate_api_v1_onboarding_request_certificate_post**](OnboardingApi.md#request_certificate_api_v1_onboarding_request_certificate_post) | **POST** /api/v1/onboarding/request-certificate | Request Certificate


# **get_certificate_status_api_v1_onboarding_certificate_status_get**
> object get_certificate_status_api_v1_onboarding_certificate_status_get()

Get Certificate Status

Get current certificate status for organization.

Args:
    organization: Organization details from authentication
    db: Database session

Returns:
    dict: Current certificate status

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
    api_instance = encypher.OnboardingApi(api_client)

    try:
        # Get Certificate Status
        api_response = api_instance.get_certificate_status_api_v1_onboarding_certificate_status_get()
        print("The response of OnboardingApi->get_certificate_status_api_v1_onboarding_certificate_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->get_certificate_status_api_v1_onboarding_certificate_status_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **request_certificate_api_v1_onboarding_request_certificate_post**
> object request_certificate_api_v1_onboarding_request_certificate_post()

Request Certificate

Initiate SSL.com certificate request for organization.

This endpoint:
1. Checks if organization already has a pending/active certificate
2. Creates SSL.com order via API
3. Stores order tracking in certificate_lifecycle table
4. Returns validation URL to organization

Args:
    organization: Organization details from authentication
    db: Database session

Returns:
    dict: Certificate request details including validation URL

Raises:
    HTTPException: If organization already has certificate or SSL.com API fails

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
    api_instance = encypher.OnboardingApi(api_client)

    try:
        # Request Certificate
        api_response = api_instance.request_certificate_api_v1_onboarding_request_certificate_post()
        print("The response of OnboardingApi->request_certificate_api_v1_onboarding_request_certificate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->request_certificate_api_v1_onboarding_request_certificate_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

