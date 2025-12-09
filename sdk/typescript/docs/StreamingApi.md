# StreamingApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**closeStreamingSessionApiV1StreamSessionSessionIdClosePost**](StreamingApi.md#closestreamingsessionapiv1streamsessionsessionidclosepost) | **POST** /api/v1/stream/session/{session_id}/close | Close Streaming Session |
| [**createStreamingSessionApiV1StreamSessionCreatePost**](StreamingApi.md#createstreamingsessionapiv1streamsessioncreatepost) | **POST** /api/v1/stream/session/create | Create Streaming Session |
| [**getStreamRunApiV1StreamRunsRunIdGet**](StreamingApi.md#getstreamrunapiv1streamrunsrunidget) | **GET** /api/v1/stream/runs/{run_id} | Get Stream Run |
| [**getStreamingStatsApiV1StreamStatsGet**](StreamingApi.md#getstreamingstatsapiv1streamstatsget) | **GET** /api/v1/stream/stats | Get Streaming Stats |
| [**sseEventsEndpointApiV1StreamEventsGet**](StreamingApi.md#sseeventsendpointapiv1streameventsget) | **GET** /api/v1/stream/events | Sse Events Endpoint |
| [**streamSigningApiV1StreamSignPost**](StreamingApi.md#streamsigningapiv1streamsignpost) | **POST** /api/v1/stream/sign | Stream Signing |
| [**streamingHealthCheckApiV1StreamHealthGet**](StreamingApi.md#streaminghealthcheckapiv1streamhealthget) | **GET** /api/v1/stream/health | Streaming Health Check |



## closeStreamingSessionApiV1StreamSessionSessionIdClosePost

> any closeStreamingSessionApiV1StreamSessionSessionIdClosePost(sessionId)

Close Streaming Session

Close a streaming session.  Args:     session_id: Session identifier     organization: Authenticated organization     db: Database session      Returns:     Session closure result with stats

### Example

```ts
import {
  Configuration,
  StreamingApi,
} from '@encypher/sdk';
import type { CloseStreamingSessionApiV1StreamSessionSessionIdClosePostRequest } from '@encypher/sdk';

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
  } satisfies CloseStreamingSessionApiV1StreamSessionSessionIdClosePostRequest;

  try {
    const data = await api.closeStreamingSessionApiV1StreamSessionSessionIdClosePost(body);
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


## createStreamingSessionApiV1StreamSessionCreatePost

> any createStreamingSessionApiV1StreamSessionCreatePost(sessionType, bodyCreateStreamingSessionApiV1StreamSessionCreatePost)

Create Streaming Session

Create a new streaming session.  Args:     session_type: Type of session (websocket, sse, kafka)     metadata: Optional session metadata     signing_options: Optional signing configuration     organization: Authenticated organization     db: Database session      Returns:     Session creation result with session_id

### Example

```ts
import {
  Configuration,
  StreamingApi,
} from '@encypher/sdk';
import type { CreateStreamingSessionApiV1StreamSessionCreatePostRequest } from '@encypher/sdk';

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
    // BodyCreateStreamingSessionApiV1StreamSessionCreatePost (optional)
    bodyCreateStreamingSessionApiV1StreamSessionCreatePost: ...,
  } satisfies CreateStreamingSessionApiV1StreamSessionCreatePostRequest;

  try {
    const data = await api.createStreamingSessionApiV1StreamSessionCreatePost(body);
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
| **bodyCreateStreamingSessionApiV1StreamSessionCreatePost** | [BodyCreateStreamingSessionApiV1StreamSessionCreatePost](BodyCreateStreamingSessionApiV1StreamSessionCreatePost.md) |  | [Optional] |

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


## getStreamRunApiV1StreamRunsRunIdGet

> any getStreamRunApiV1StreamRunsRunIdGet(runId)

Get Stream Run

Return persisted streaming run state.

### Example

```ts
import {
  Configuration,
  StreamingApi,
} from '@encypher/sdk';
import type { GetStreamRunApiV1StreamRunsRunIdGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new StreamingApi();

  const body = {
    // string
    runId: runId_example,
  } satisfies GetStreamRunApiV1StreamRunsRunIdGetRequest;

  try {
    const data = await api.getStreamRunApiV1StreamRunsRunIdGet(body);
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

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getStreamingStatsApiV1StreamStatsGet

> any getStreamingStatsApiV1StreamStatsGet()

Get Streaming Stats

Get streaming statistics for organization.  Args:     organization: Authenticated organization      Returns:     Streaming statistics

### Example

```ts
import {
  Configuration,
  StreamingApi,
} from '@encypher/sdk';
import type { GetStreamingStatsApiV1StreamStatsGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StreamingApi(config);

  try {
    const data = await api.getStreamingStatsApiV1StreamStatsGet();
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


## sseEventsEndpointApiV1StreamEventsGet

> any sseEventsEndpointApiV1StreamEventsGet(sessionId, apiKey)

Sse Events Endpoint

Server-Sent Events (SSE) endpoint for unidirectional streaming.  Args:     session_id: Session identifier     api_key: API key for authentication      Returns:     StreamingResponse with SSE events

### Example

```ts
import {
  Configuration,
  StreamingApi,
} from '@encypher/sdk';
import type { SseEventsEndpointApiV1StreamEventsGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new StreamingApi();

  const body = {
    // string
    sessionId: sessionId_example,
    // string (optional)
    apiKey: apiKey_example,
  } satisfies SseEventsEndpointApiV1StreamEventsGetRequest;

  try {
    const data = await api.sseEventsEndpointApiV1StreamEventsGet(body);
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

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## streamSigningApiV1StreamSignPost

> streamSigningApiV1StreamSignPost(streamSignRequest)

Stream Signing

Stream signing progress via SSE.

### Example

```ts
import {
  Configuration,
  StreamingApi,
} from '@encypher/sdk';
import type { StreamSigningApiV1StreamSignPostRequest } from '@encypher/sdk';

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
  } satisfies StreamSigningApiV1StreamSignPostRequest;

  try {
    const data = await api.streamSigningApiV1StreamSignPost(body);
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


## streamingHealthCheckApiV1StreamHealthGet

> any streamingHealthCheckApiV1StreamHealthGet()

Streaming Health Check

Health check endpoint for streaming service.  Returns:     Health status of streaming components

### Example

```ts
import {
  Configuration,
  StreamingApi,
} from '@encypher/sdk';
import type { StreamingHealthCheckApiV1StreamHealthGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new StreamingApi();

  try {
    const data = await api.streamingHealthCheckApiV1StreamHealthGet();
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

