# StreamingApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**closeStreamingSessionApiV1SignStreamSessionsSessionIdClosePost**](StreamingApi.md#closestreamingsessionapiv1signstreamsessionssessionidclosepost) | **POST** /api/v1/sign/stream/sessions/{session_id}/close | Close Streaming Session |
| [**createStreamingSessionApiV1SignStreamSessionsPost**](StreamingApi.md#createstreamingsessionapiv1signstreamsessionspost) | **POST** /api/v1/sign/stream/sessions | Create Streaming Session |
| [**getStreamRunApiV1SignStreamRunsRunIdGet**](StreamingApi.md#getstreamrunapiv1signstreamrunsrunidget) | **GET** /api/v1/sign/stream/runs/{run_id} | Get Stream Run |
| [**getStreamingStatsApiV1SignStreamStatsGet**](StreamingApi.md#getstreamingstatsapiv1signstreamstatsget) | **GET** /api/v1/sign/stream/stats | Get Streaming Stats |
| [**sseEventsEndpointApiV1SignStreamSessionsSessionIdEventsGet**](StreamingApi.md#sseeventsendpointapiv1signstreamsessionssessionideventsget) | **GET** /api/v1/sign/stream/sessions/{session_id}/events | Sse Events Endpoint |
| [**streamSigningApiV1SignStreamPost**](StreamingApi.md#streamsigningapiv1signstreampost) | **POST** /api/v1/sign/stream | Stream Signing |



## closeStreamingSessionApiV1SignStreamSessionsSessionIdClosePost

> any closeStreamingSessionApiV1SignStreamSessionsSessionIdClosePost(sessionId)

Close Streaming Session

Close a streaming session.  Args:     session_id: Session identifier     organization: Authenticated organization     db: Database session  Returns:     Session closure result with stats

### Example

```ts
import {
  Configuration,
  StreamingApi,
} from '@encypher/sdk';
import type { CloseStreamingSessionApiV1SignStreamSessionsSessionIdClosePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StreamingApi(config);

  const body = {
    // string
    sessionId: sessionId_example,
  } satisfies CloseStreamingSessionApiV1SignStreamSessionsSessionIdClosePostRequest;

  try {
    const data = await api.closeStreamingSessionApiV1SignStreamSessionsSessionIdClosePost(body);
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
| **sessionId** | `string` |  | [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## createStreamingSessionApiV1SignStreamSessionsPost

> any createStreamingSessionApiV1SignStreamSessionsPost(sessionType, bodyCreateStreamingSessionApiV1SignStreamSessionsPost)

Create Streaming Session

Create a new streaming session.  Args:     session_type: Type of session (websocket, sse, kafka)     metadata: Optional session metadata     signing_options: Optional signing configuration     organization: Authenticated organization     db: Database session  Returns:     Session creation result with session_id

### Example

```ts
import {
  Configuration,
  StreamingApi,
} from '@encypher/sdk';
import type { CreateStreamingSessionApiV1SignStreamSessionsPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StreamingApi(config);

  const body = {
    // string (optional)
    sessionType: sessionType_example,
    // BodyCreateStreamingSessionApiV1SignStreamSessionsPost (optional)
    bodyCreateStreamingSessionApiV1SignStreamSessionsPost: ...,
  } satisfies CreateStreamingSessionApiV1SignStreamSessionsPostRequest;

  try {
    const data = await api.createStreamingSessionApiV1SignStreamSessionsPost(body);
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
| **sessionType** | `string` |  | [Optional] [Defaults to `&#39;websocket&#39;`] |
| **bodyCreateStreamingSessionApiV1SignStreamSessionsPost** | [BodyCreateStreamingSessionApiV1SignStreamSessionsPost](BodyCreateStreamingSessionApiV1SignStreamSessionsPost.md) |  | [Optional] |

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


## getStreamRunApiV1SignStreamRunsRunIdGet

> any getStreamRunApiV1SignStreamRunsRunIdGet(runId)

Get Stream Run

Return persisted streaming run state.

### Example

```ts
import {
  Configuration,
  StreamingApi,
} from '@encypher/sdk';
import type { GetStreamRunApiV1SignStreamRunsRunIdGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StreamingApi(config);

  const body = {
    // string
    runId: runId_example,
  } satisfies GetStreamRunApiV1SignStreamRunsRunIdGetRequest;

  try {
    const data = await api.getStreamRunApiV1SignStreamRunsRunIdGet(body);
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
| **runId** | `string` |  | [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getStreamingStatsApiV1SignStreamStatsGet

> any getStreamingStatsApiV1SignStreamStatsGet()

Get Streaming Stats

Get streaming statistics for organization.  Args:     organization: Authenticated organization  Returns:     Streaming statistics

### Example

```ts
import {
  Configuration,
  StreamingApi,
} from '@encypher/sdk';
import type { GetStreamingStatsApiV1SignStreamStatsGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StreamingApi(config);

  try {
    const data = await api.getStreamingStatsApiV1SignStreamStatsGet();
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

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## sseEventsEndpointApiV1SignStreamSessionsSessionIdEventsGet

> any sseEventsEndpointApiV1SignStreamSessionsSessionIdEventsGet(sessionId, apiKey)

Sse Events Endpoint

Server-Sent Events (SSE) endpoint for unidirectional streaming (session scoped).  Args:     session_id: Session identifier     api_key: API key for authentication  Returns:     StreamingResponse with SSE events

### Example

```ts
import {
  Configuration,
  StreamingApi,
} from '@encypher/sdk';
import type { SseEventsEndpointApiV1SignStreamSessionsSessionIdEventsGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StreamingApi(config);

  const body = {
    // string
    sessionId: sessionId_example,
    // string (optional)
    apiKey: apiKey_example,
  } satisfies SseEventsEndpointApiV1SignStreamSessionsSessionIdEventsGetRequest;

  try {
    const data = await api.sseEventsEndpointApiV1SignStreamSessionsSessionIdEventsGet(body);
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
| **sessionId** | `string` |  | [Defaults to `undefined`] |
| **apiKey** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## streamSigningApiV1SignStreamPost

> streamSigningApiV1SignStreamPost(streamSignRequest)

Stream Signing

Stream signing progress via SSE.

### Example

```ts
import {
  Configuration,
  StreamingApi,
} from '@encypher/sdk';
import type { StreamSigningApiV1SignStreamPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StreamingApi(config);

  const body = {
    // StreamSignRequest
    streamSignRequest: ...,
  } satisfies StreamSigningApiV1SignStreamPostRequest;

  try {
    const data = await api.streamSigningApiV1SignStreamPost(body);
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
| **streamSignRequest** | [StreamSignRequest](StreamSignRequest.md) |  | |

### Return type

`void` (Empty response body)

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

