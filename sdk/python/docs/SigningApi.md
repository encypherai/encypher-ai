# encypher.SigningApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**sign_advanced_api_v1_sign_advanced_post**](SigningApi.md#sign_advanced_api_v1_sign_advanced_post) | **POST** /api/v1/sign/advanced | Sign Advanced
[**sign_content_api_v1_sign_post**](SigningApi.md#sign_content_api_v1_sign_post) | **POST** /api/v1/sign | Sign Content


# **sign_advanced_api_v1_sign_advanced_post**
> EncodeWithEmbeddingsResponse sign_advanced_api_v1_sign_advanced_post(encode_with_embeddings_request)

Sign Advanced

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.encode_with_embeddings_request import EncodeWithEmbeddingsRequest
from encypher.models.encode_with_embeddings_response import EncodeWithEmbeddingsResponse
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
    api_instance = encypher.SigningApi(api_client)
    encode_with_embeddings_request = encypher.EncodeWithEmbeddingsRequest() # EncodeWithEmbeddingsRequest | 

    try:
        # Sign Advanced
        api_response = api_instance.sign_advanced_api_v1_sign_advanced_post(encode_with_embeddings_request)
        print("The response of SigningApi->sign_advanced_api_v1_sign_advanced_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SigningApi->sign_advanced_api_v1_sign_advanced_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **encode_with_embeddings_request** | [**EncodeWithEmbeddingsRequest**](EncodeWithEmbeddingsRequest.md)|  | 

### Return type

[**EncodeWithEmbeddingsResponse**](EncodeWithEmbeddingsResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sign_content_api_v1_sign_post**
> SignResponse sign_content_api_v1_sign_post(sign_request)

Sign Content

Sign content with a C2PA manifest.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.sign_request import SignRequest
from encypher.models.sign_response import SignResponse
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
    api_instance = encypher.SigningApi(api_client)
    sign_request = encypher.SignRequest() # SignRequest | 

    try:
        # Sign Content
        api_response = api_instance.sign_content_api_v1_sign_post(sign_request)
        print("The response of SigningApi->sign_content_api_v1_sign_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SigningApi->sign_content_api_v1_sign_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sign_request** | [**SignRequest**](SignRequest.md)|  | 

### Return type

[**SignResponse**](SignResponse.md)

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

