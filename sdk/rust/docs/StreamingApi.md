# \StreamingApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**close_streaming_session_api_v1_stream_session_session_id_close_post**](StreamingApi.md#close_streaming_session_api_v1_stream_session_session_id_close_post) | **POST** /api/v1/stream/session/{session_id}/close | Close Streaming Session
[**create_streaming_session_api_v1_stream_session_create_post**](StreamingApi.md#create_streaming_session_api_v1_stream_session_create_post) | **POST** /api/v1/stream/session/create | Create Streaming Session
[**get_stream_run_api_v1_stream_runs_run_id_get**](StreamingApi.md#get_stream_run_api_v1_stream_runs_run_id_get) | **GET** /api/v1/stream/runs/{run_id} | Get Stream Run
[**get_streaming_stats_api_v1_stream_stats_get**](StreamingApi.md#get_streaming_stats_api_v1_stream_stats_get) | **GET** /api/v1/stream/stats | Get Streaming Stats
[**sse_events_endpoint_api_v1_stream_events_get**](StreamingApi.md#sse_events_endpoint_api_v1_stream_events_get) | **GET** /api/v1/stream/events | Sse Events Endpoint
[**stream_signing_api_v1_stream_sign_post**](StreamingApi.md#stream_signing_api_v1_stream_sign_post) | **POST** /api/v1/stream/sign | Stream Signing



## close_streaming_session_api_v1_stream_session_session_id_close_post

> serde_json::Value close_streaming_session_api_v1_stream_session_session_id_close_post(session_id)
Close Streaming Session

Close a streaming session.  Args:     session_id: Session identifier     organization: Authenticated organization     db: Database session      Returns:     Session closure result with stats

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**session_id** | **String** |  | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## create_streaming_session_api_v1_stream_session_create_post

> serde_json::Value create_streaming_session_api_v1_stream_session_create_post(session_type, body_create_streaming_session_api_v1_stream_session_create_post)
Create Streaming Session

Create a new streaming session.  Args:     session_type: Type of session (websocket, sse, kafka)     metadata: Optional session metadata     signing_options: Optional signing configuration     organization: Authenticated organization     db: Database session      Returns:     Session creation result with session_id

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**session_type** | Option<**String**> |  |  |[default to websocket]
**body_create_streaming_session_api_v1_stream_session_create_post** | Option<[**BodyCreateStreamingSessionApiV1StreamSessionCreatePost**](BodyCreateStreamingSessionApiV1StreamSessionCreatePost.md)> |  |  |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_stream_run_api_v1_stream_runs_run_id_get

> serde_json::Value get_stream_run_api_v1_stream_runs_run_id_get(run_id)
Get Stream Run

Return persisted streaming run state.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**run_id** | **String** |  | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_streaming_stats_api_v1_stream_stats_get

> serde_json::Value get_streaming_stats_api_v1_stream_stats_get()
Get Streaming Stats

Get streaming statistics for organization.  Args:     organization: Authenticated organization      Returns:     Streaming statistics

### Parameters

This endpoint does not need any parameter.

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## sse_events_endpoint_api_v1_stream_events_get

> serde_json::Value sse_events_endpoint_api_v1_stream_events_get(session_id, api_key)
Sse Events Endpoint

Server-Sent Events (SSE) endpoint for unidirectional streaming.  Args:     session_id: Session identifier     api_key: API key for authentication      Returns:     StreamingResponse with SSE events

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**session_id** | **String** |  | [required] |
**api_key** | Option<**String**> |  |  |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## stream_signing_api_v1_stream_sign_post

> stream_signing_api_v1_stream_sign_post(stream_sign_request)
Stream Signing

Stream signing progress via SSE.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**stream_sign_request** | [**StreamSignRequest**](StreamSignRequest.md) |  | [required] |

### Return type

 (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

