# encypher.EnterpriseEmbeddingsApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post**](EnterpriseEmbeddingsApi.md#encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post) | **POST** /api/v1/enterprise/embeddings/encode-with-embeddings | Encode With Embeddings
[**sign_advanced_api_v1_enterprise_embeddings_sign_advanced_post**](EnterpriseEmbeddingsApi.md#sign_advanced_api_v1_enterprise_embeddings_sign_advanced_post) | **POST** /api/v1/enterprise/embeddings/sign/advanced | Sign Advanced


# **encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post**
> EncodeWithEmbeddingsResponse encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post(encode_with_embeddings_request, authorization=authorization)

Encode With Embeddings

Encode a document with invisible embeddings.

**Alias:** POST /enterprise/sign/advanced

### Example


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


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.EnterpriseEmbeddingsApi(api_client)
    encode_with_embeddings_request = encypher.EncodeWithEmbeddingsRequest() # EncodeWithEmbeddingsRequest | 
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Encode With Embeddings
        api_response = api_instance.encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post(encode_with_embeddings_request, authorization=authorization)
        print("The response of EnterpriseEmbeddingsApi->encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EnterpriseEmbeddingsApi->encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **encode_with_embeddings_request** | [**EncodeWithEmbeddingsRequest**](EncodeWithEmbeddingsRequest.md)|  | 
 **authorization** | **str**|  | [optional] 

### Return type

[**EncodeWithEmbeddingsResponse**](EncodeWithEmbeddingsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sign_advanced_api_v1_enterprise_embeddings_sign_advanced_post**
> EncodeWithEmbeddingsResponse sign_advanced_api_v1_enterprise_embeddings_sign_advanced_post(encode_with_embeddings_request, authorization=authorization)

Sign Advanced

Sign a document with advanced invisible embeddings.

This is an alias for POST /enterprise/embeddings/encode-with-embeddings
with a clearer name. Creates C2PA-compliant invisible signatures.

Requires Professional or Enterprise tier.

### Example


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


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.EnterpriseEmbeddingsApi(api_client)
    encode_with_embeddings_request = encypher.EncodeWithEmbeddingsRequest() # EncodeWithEmbeddingsRequest | 
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Sign Advanced
        api_response = api_instance.sign_advanced_api_v1_enterprise_embeddings_sign_advanced_post(encode_with_embeddings_request, authorization=authorization)
        print("The response of EnterpriseEmbeddingsApi->sign_advanced_api_v1_enterprise_embeddings_sign_advanced_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EnterpriseEmbeddingsApi->sign_advanced_api_v1_enterprise_embeddings_sign_advanced_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **encode_with_embeddings_request** | [**EncodeWithEmbeddingsRequest**](EncodeWithEmbeddingsRequest.md)|  | 
 **authorization** | **str**|  | [optional] 

### Return type

[**EncodeWithEmbeddingsResponse**](EncodeWithEmbeddingsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

