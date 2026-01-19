# ChatApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**chatHealthCheckApiV1ChatHealthGet**](ChatApi.md#chathealthcheckapiv1chathealthget) | **GET** /api/v1/chat/health | Chat Health Check |
| [**openaiCompatibleChatApiV1ChatCompletionsPost**](ChatApi.md#openaicompatiblechatapiv1chatcompletionspost) | **POST** /api/v1/chat/completions | Openai Compatible Chat |



## chatHealthCheckApiV1ChatHealthGet

> any chatHealthCheckApiV1ChatHealthGet()

Chat Health Check

Health check for chat streaming endpoint.  Returns:     Health status

### Example

```ts
import {
  Configuration,
  ChatApi,
} from '@encypher/sdk';
import type { ChatHealthCheckApiV1ChatHealthGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new ChatApi();

  try {
    const data = await api.chatHealthCheckApiV1ChatHealthGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## openaiCompatibleChatApiV1ChatCompletionsPost

> any openaiCompatibleChatApiV1ChatCompletionsPost(chatCompletionRequest)

Openai Compatible Chat

OpenAI-compatible chat completion endpoint with signing.  This endpoint mimics the OpenAI Chat Completions API but adds C2PA signing to the response content.  Args:     request: Chat completion request     organization: Authenticated organization     db: Database session  Returns:     Chat completion response (streaming or non-streaming)

### Example

```ts
import {
  Configuration,
  ChatApi,
} from '@encypher/sdk';
import type { OpenaiCompatibleChatApiV1ChatCompletionsPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ChatApi(config);

  const body = {
    // ChatCompletionRequest
    chatCompletionRequest: ...,
  } satisfies OpenaiCompatibleChatApiV1ChatCompletionsPostRequest;

  try {
    const data = await api.openaiCompatibleChatApiV1ChatCompletionsPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **chatCompletionRequest** | [ChatCompletionRequest](ChatCompletionRequest.md) |  | |

### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

