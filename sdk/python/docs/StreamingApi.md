# encypher.StreamingApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**close_streaming_session_api_v1_sign_stream_sessions_session_id_close_post**](StreamingApi.md#close_streaming_session_api_v1_sign_stream_sessions_session_id_close_post) | **POST** /api/v1/sign/stream/sessions/{session_id}/close | Close Streaming Session
[**create_streaming_session_api_v1_sign_stream_sessions_post**](StreamingApi.md#create_streaming_session_api_v1_sign_stream_sessions_post) | **POST** /api/v1/sign/stream/sessions | Create Streaming Session
[**get_stream_run_api_v1_sign_stream_runs_run_id_get**](StreamingApi.md#get_stream_run_api_v1_sign_stream_runs_run_id_get) | **GET** /api/v1/sign/stream/runs/{run_id} | Get Stream Run
[**get_streaming_stats_api_v1_sign_stream_stats_get**](StreamingApi.md#get_streaming_stats_api_v1_sign_stream_stats_get) | **GET** /api/v1/sign/stream/stats | Get Streaming Stats
[**sse_events_endpoint_api_v1_sign_stream_sessions_session_id_events_get**](StreamingApi.md#sse_events_endpoint_api_v1_sign_stream_sessions_session_id_events_get) | **GET** /api/v1/sign/stream/sessions/{session_id}/events | Sse Events Endpoint
[**stream_signing_api_v1_sign_stream_post**](StreamingApi.md#stream_signing_api_v1_sign_stream_post) | **POST** /api/v1/sign/stream | Stream Signing


# **close_streaming_session_api_v1_sign_stream_sessions_session_id_close_post**
> object close_streaming_session_api_v1_sign_stream_sessions_session_id_close_post(session_id)

Close Streaming Session

Close a streaming session.

Args:
    session_id: Session identifier
    organization: Authenticated organization
    db: Database session

Returns:
    Session closure result with stats

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.StreamingApi(api_client)
    session_id = 'session_id_example' # str | 

    try:
        # Close Streaming Session
        api_response = api_instance.close_streaming_session_api_v1_sign_stream_sessions_session_id_close_post(session_id)
        print("The response of StreamingApi->close_streaming_session_api_v1_sign_stream_sessions_session_id_close_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StreamingApi->close_streaming_session_api_v1_sign_stream_sessions_session_id_close_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 

### Return type

**object**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_streaming_session_api_v1_sign_stream_sessions_post**
> object create_streaming_session_api_v1_sign_stream_sessions_post(session_type=session_type, body_create_streaming_session_api_v1_sign_stream_sessions_post=body_create_streaming_session_api_v1_sign_stream_sessions_post)

Create Streaming Session

Create a new streaming session.

Args:
    session_type: Type of session (websocket, sse, kafka)
    metadata: Optional session metadata
    signing_options: Optional signing configuration
    organization: Authenticated organization
    db: Database session

Returns:
    Session creation result with session_id

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.body_create_streaming_session_api_v1_sign_stream_sessions_post import BodyCreateStreamingSessionApiV1SignStreamSessionsPost
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
    api_instance = encypher.StreamingApi(api_client)
    session_type = 'websocket' # str |  (optional) (default to 'websocket')
    body_create_streaming_session_api_v1_sign_stream_sessions_post = encypher.BodyCreateStreamingSessionApiV1SignStreamSessionsPost() # BodyCreateStreamingSessionApiV1SignStreamSessionsPost |  (optional)

    try:
        # Create Streaming Session
        api_response = api_instance.create_streaming_session_api_v1_sign_stream_sessions_post(session_type=session_type, body_create_streaming_session_api_v1_sign_stream_sessions_post=body_create_streaming_session_api_v1_sign_stream_sessions_post)
        print("The response of StreamingApi->create_streaming_session_api_v1_sign_stream_sessions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StreamingApi->create_streaming_session_api_v1_sign_stream_sessions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_type** | **str**|  | [optional] [default to &#39;websocket&#39;]
 **body_create_streaming_session_api_v1_sign_stream_sessions_post** | [**BodyCreateStreamingSessionApiV1SignStreamSessionsPost**](BodyCreateStreamingSessionApiV1SignStreamSessionsPost.md)|  | [optional] 

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

# **get_stream_run_api_v1_sign_stream_runs_run_id_get**
> object get_stream_run_api_v1_sign_stream_runs_run_id_get(run_id)

Get Stream Run

Return persisted streaming run state.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.StreamingApi(api_client)
    run_id = 'run_id_example' # str | 

    try:
        # Get Stream Run
        api_response = api_instance.get_stream_run_api_v1_sign_stream_runs_run_id_get(run_id)
        print("The response of StreamingApi->get_stream_run_api_v1_sign_stream_runs_run_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StreamingApi->get_stream_run_api_v1_sign_stream_runs_run_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **run_id** | **str**|  | 

### Return type

**object**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_streaming_stats_api_v1_sign_stream_stats_get**
> object get_streaming_stats_api_v1_sign_stream_stats_get()

Get Streaming Stats

Get streaming statistics for organization.

Args:
    organization: Authenticated organization

Returns:
    Streaming statistics

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.StreamingApi(api_client)

    try:
        # Get Streaming Stats
        api_response = api_instance.get_streaming_stats_api_v1_sign_stream_stats_get()
        print("The response of StreamingApi->get_streaming_stats_api_v1_sign_stream_stats_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StreamingApi->get_streaming_stats_api_v1_sign_stream_stats_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sse_events_endpoint_api_v1_sign_stream_sessions_session_id_events_get**
> object sse_events_endpoint_api_v1_sign_stream_sessions_session_id_events_get(session_id, api_key=api_key)

Sse Events Endpoint

Server-Sent Events (SSE) endpoint for unidirectional streaming (session scoped).

Args:
    session_id: Session identifier
    api_key: API key for authentication

Returns:
    StreamingResponse with SSE events

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.StreamingApi(api_client)
    session_id = 'session_id_example' # str | 
    api_key = 'api_key_example' # str |  (optional)

    try:
        # Sse Events Endpoint
        api_response = api_instance.sse_events_endpoint_api_v1_sign_stream_sessions_session_id_events_get(session_id, api_key=api_key)
        print("The response of StreamingApi->sse_events_endpoint_api_v1_sign_stream_sessions_session_id_events_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StreamingApi->sse_events_endpoint_api_v1_sign_stream_sessions_session_id_events_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **api_key** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stream_signing_api_v1_sign_stream_post**
> stream_signing_api_v1_sign_stream_post(stream_sign_request)

Stream Signing

Stream signing progress via SSE.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.stream_sign_request import StreamSignRequest
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
    api_instance = encypher.StreamingApi(api_client)
    stream_sign_request = encypher.StreamSignRequest() # StreamSignRequest | 

    try:
        # Stream Signing
        api_instance.stream_signing_api_v1_sign_stream_post(stream_sign_request)
    except Exception as e:
        print("Exception when calling StreamingApi->stream_signing_api_v1_sign_stream_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stream_sign_request** | [**StreamSignRequest**](StreamSignRequest.md)|  | 

### Return type

void (empty response body)

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

