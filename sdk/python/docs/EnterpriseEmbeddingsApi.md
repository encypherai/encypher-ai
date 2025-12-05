# encypher.EnterpriseEmbeddingsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post**](EnterpriseEmbeddingsApi.md#encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post) | **POST** /api/v1/enterprise/embeddings/encode-with-embeddings | Encode With Embeddings


# **encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post**
> EncodeWithEmbeddingsResponse encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post(encode_with_embeddings_request, authorization=authorization)

Encode With Embeddings

Encode a document with invisible embeddings.

### Example


```python
import encypher
from encypher.models.encode_with_embeddings_request import EncodeWithEmbeddingsRequest
from encypher.models.encode_with_embeddings_response import EncodeWithEmbeddingsResponse
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

