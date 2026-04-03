# encypher.ImageVerificationApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**verify_image_api_v1_verify_image_post**](ImageVerificationApi.md#verify_image_api_v1_verify_image_post) | **POST** /api/v1/verify/image | Verify a C2PA-signed image
[**verify_rich_api_v1_verify_rich_post**](ImageVerificationApi.md#verify_rich_api_v1_verify_rich_post) | **POST** /api/v1/verify/rich | Verify a signed rich article (text + images)


# **verify_image_api_v1_verify_image_post**
> ImageVerifyResponse verify_image_api_v1_verify_image_post(image_verify_request)

Verify a C2PA-signed image

Public endpoint. Accepts a base64-encoded image, extracts and verifies the embedded JUMBF C2PA manifest.

### Example


```python
import encypher
from encypher.models.image_verify_request import ImageVerifyRequest
from encypher.models.image_verify_response import ImageVerifyResponse
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
    api_instance = encypher.ImageVerificationApi(api_client)
    image_verify_request = encypher.ImageVerifyRequest() # ImageVerifyRequest |

    try:
        # Verify a C2PA-signed image
        api_response = api_instance.verify_image_api_v1_verify_image_post(image_verify_request)
        print("The response of ImageVerificationApi->verify_image_api_v1_verify_image_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ImageVerificationApi->verify_image_api_v1_verify_image_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_verify_request** | [**ImageVerifyRequest**](ImageVerifyRequest.md)|  |

### Return type

[**ImageVerifyResponse**](ImageVerifyResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **verify_rich_api_v1_verify_rich_post**
> RichVerifyResponse verify_rich_api_v1_verify_rich_post(rich_verify_request)

Verify a signed rich article (text + images)

Public endpoint. Looks up a signed article by document_id and verifies all components: text signature, each image C2PA manifest, and the composite manifest integrity.

### Example


```python
import encypher
from encypher.models.rich_verify_request import RichVerifyRequest
from encypher.models.rich_verify_response import RichVerifyResponse
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
    api_instance = encypher.ImageVerificationApi(api_client)
    rich_verify_request = encypher.RichVerifyRequest() # RichVerifyRequest |

    try:
        # Verify a signed rich article (text + images)
        api_response = api_instance.verify_rich_api_v1_verify_rich_post(rich_verify_request)
        print("The response of ImageVerificationApi->verify_rich_api_v1_verify_rich_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ImageVerificationApi->verify_rich_api_v1_verify_rich_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rich_verify_request** | [**RichVerifyRequest**](RichVerifyRequest.md)|  |

### Return type

[**RichVerifyResponse**](RichVerifyResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
