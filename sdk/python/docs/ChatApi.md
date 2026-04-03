# encypher.ChatApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**chat_health_check_api_v1_chat_health_get**](ChatApi.md#chat_health_check_api_v1_chat_health_get) | **GET** /api/v1/chat/health | Chat Health Check
[**openai_compatible_chat_api_v1_chat_completions_post**](ChatApi.md#openai_compatible_chat_api_v1_chat_completions_post) | **POST** /api/v1/chat/completions | Openai Compatible Chat


# **chat_health_check_api_v1_chat_health_get**
> object chat_health_check_api_v1_chat_health_get()

Chat Health Check

Health check for chat streaming endpoint.

Returns:
    Health status

### Example


```python
import encypher
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
    api_instance = encypher.ChatApi(api_client)

    try:
        # Chat Health Check
        api_response = api_instance.chat_health_check_api_v1_chat_health_get()
        print("The response of ChatApi->chat_health_check_api_v1_chat_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->chat_health_check_api_v1_chat_health_get: %s\n" % e)
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

# **openai_compatible_chat_api_v1_chat_completions_post**
> object openai_compatible_chat_api_v1_chat_completions_post(chat_completion_request)

Openai Compatible Chat

OpenAI-compatible chat completion endpoint with signing.

This endpoint mimics the OpenAI Chat Completions API but adds
C2PA signing to the response content.

Args:
    request: Chat completion request
    organization: Authenticated organization
    db: Database session

Returns:
    Chat completion response (streaming or non-streaming)

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.chat_completion_request import ChatCompletionRequest
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
    api_instance = encypher.ChatApi(api_client)
    chat_completion_request = encypher.ChatCompletionRequest() # ChatCompletionRequest |

    try:
        # Openai Compatible Chat
        api_response = api_instance.openai_compatible_chat_api_v1_chat_completions_post(chat_completion_request)
        print("The response of ChatApi->openai_compatible_chat_api_v1_chat_completions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->openai_compatible_chat_api_v1_chat_completions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **chat_completion_request** | [**ChatCompletionRequest**](ChatCompletionRequest.md)|  |

### Return type

**object**

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
