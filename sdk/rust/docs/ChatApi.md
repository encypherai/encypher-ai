# \ChatApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**chat_health_check_api_v1_chat_health_get**](ChatApi.md#chat_health_check_api_v1_chat_health_get) | **GET** /api/v1/chat/health | Chat Health Check
[**openai_compatible_chat_api_v1_chat_completions_post**](ChatApi.md#openai_compatible_chat_api_v1_chat_completions_post) | **POST** /api/v1/chat/completions | Openai Compatible Chat



## chat_health_check_api_v1_chat_health_get

> serde_json::Value chat_health_check_api_v1_chat_health_get()
Chat Health Check

Health check for chat streaming endpoint.  Returns:     Health status

### Parameters

This endpoint does not need any parameter.

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## openai_compatible_chat_api_v1_chat_completions_post

> serde_json::Value openai_compatible_chat_api_v1_chat_completions_post(chat_completion_request)
Openai Compatible Chat

OpenAI-compatible chat completion endpoint with signing.  This endpoint mimics the OpenAI Chat Completions API but adds C2PA signing to the response content.  Args:     request: Chat completion request     organization: Authenticated organization     db: Database session  Returns:     Chat completion response (streaming or non-streaming)

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**chat_completion_request** | [**ChatCompletionRequest**](ChatCompletionRequest.md) |  | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

