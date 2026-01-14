# encypher.BatchApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**batch_sign_api_v1_batch_sign_post**](BatchApi.md#batch_sign_api_v1_batch_sign_post) | **POST** /api/v1/batch/sign | Batch Sign
[**batch_verify_api_v1_batch_verify_post**](BatchApi.md#batch_verify_api_v1_batch_verify_post) | **POST** /api/v1/batch/verify | Batch Verify


# **batch_sign_api_v1_batch_sign_post**
> BatchResponseEnvelope batch_sign_api_v1_batch_sign_post(batch_sign_request)

Batch Sign

Sign multiple documents in a single request.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.batch_response_envelope import BatchResponseEnvelope
from encypher.models.batch_sign_request import BatchSignRequest
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
    api_instance = encypher.BatchApi(api_client)
    batch_sign_request = encypher.BatchSignRequest() # BatchSignRequest | 

    try:
        # Batch Sign
        api_response = api_instance.batch_sign_api_v1_batch_sign_post(batch_sign_request)
        print("The response of BatchApi->batch_sign_api_v1_batch_sign_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BatchApi->batch_sign_api_v1_batch_sign_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batch_sign_request** | [**BatchSignRequest**](BatchSignRequest.md)|  | 

### Return type

[**BatchResponseEnvelope**](BatchResponseEnvelope.md)

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

# **batch_verify_api_v1_batch_verify_post**
> BatchResponseEnvelope batch_verify_api_v1_batch_verify_post(batch_verify_request)

Batch Verify

Verify multiple documents in a single request.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.batch_response_envelope import BatchResponseEnvelope
from encypher.models.batch_verify_request import BatchVerifyRequest
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
    api_instance = encypher.BatchApi(api_client)
    batch_verify_request = encypher.BatchVerifyRequest() # BatchVerifyRequest | 

    try:
        # Batch Verify
        api_response = api_instance.batch_verify_api_v1_batch_verify_post(batch_verify_request)
        print("The response of BatchApi->batch_verify_api_v1_batch_verify_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BatchApi->batch_verify_api_v1_batch_verify_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batch_verify_request** | [**BatchVerifyRequest**](BatchVerifyRequest.md)|  | 

### Return type

[**BatchResponseEnvelope**](BatchResponseEnvelope.md)

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

