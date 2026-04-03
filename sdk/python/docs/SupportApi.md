# encypher.SupportApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**submit_support_contact_api_v1_support_contact_post**](SupportApi.md#submit_support_contact_api_v1_support_contact_post) | **POST** /api/v1/support/contact | Submit Support Contact
[**submit_support_contact_api_v1_support_contact_post_0**](SupportApi.md#submit_support_contact_api_v1_support_contact_post_0) | **POST** /api/v1/support/contact | Submit Support Contact


# **submit_support_contact_api_v1_support_contact_post**
> SupportContactResponse submit_support_contact_api_v1_support_contact_post(support_contact_request)

Submit Support Contact

Submit a support contact request. Sends email to support team.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.support_contact_request import SupportContactRequest
from encypher.models.support_contact_response import SupportContactResponse
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
    api_instance = encypher.SupportApi(api_client)
    support_contact_request = encypher.SupportContactRequest() # SupportContactRequest |

    try:
        # Submit Support Contact
        api_response = api_instance.submit_support_contact_api_v1_support_contact_post(support_contact_request)
        print("The response of SupportApi->submit_support_contact_api_v1_support_contact_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SupportApi->submit_support_contact_api_v1_support_contact_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **support_contact_request** | [**SupportContactRequest**](SupportContactRequest.md)|  |

### Return type

[**SupportContactResponse**](SupportContactResponse.md)

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

# **submit_support_contact_api_v1_support_contact_post_0**
> SupportContactResponse submit_support_contact_api_v1_support_contact_post_0(support_contact_request)

Submit Support Contact

Submit a support contact request. Sends email to support team.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.support_contact_request import SupportContactRequest
from encypher.models.support_contact_response import SupportContactResponse
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
    api_instance = encypher.SupportApi(api_client)
    support_contact_request = encypher.SupportContactRequest() # SupportContactRequest |

    try:
        # Submit Support Contact
        api_response = api_instance.submit_support_contact_api_v1_support_contact_post_0(support_contact_request)
        print("The response of SupportApi->submit_support_contact_api_v1_support_contact_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SupportApi->submit_support_contact_api_v1_support_contact_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **support_contact_request** | [**SupportContactRequest**](SupportContactRequest.md)|  |

### Return type

[**SupportContactResponse**](SupportContactResponse.md)

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
