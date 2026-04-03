# StreamingMerkleApi

All URIs are relative to *https://api.encypher.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**addSegmentToSessionApiV1EnterpriseStreamMerkleSegmentPost**](StreamingMerkleApi.md#addsegmenttosessionapiv1enterprisestreammerklesegmentpost) | **POST** /api/v1/enterprise/stream/merkle/segment | Add Segment To Session |
| [**finalizeStreamingSessionApiV1EnterpriseStreamMerkleFinalizePost**](StreamingMerkleApi.md#finalizestreamingsessionapiv1enterprisestreammerklefinalizepost) | **POST** /api/v1/enterprise/stream/merkle/finalize | Finalize Streaming Session |
| [**getSessionStatusApiV1EnterpriseStreamMerkleStatusPost**](StreamingMerkleApi.md#getsessionstatusapiv1enterprisestreammerklestatuspost) | **POST** /api/v1/enterprise/stream/merkle/status | Get Session Status |
| [**startStreamingMerkleSessionApiV1EnterpriseStreamMerkleStartPost**](StreamingMerkleApi.md#startstreamingmerklesessionapiv1enterprisestreammerklestartpost) | **POST** /api/v1/enterprise/stream/merkle/start | Start Streaming Merkle Session |



## addSegmentToSessionApiV1EnterpriseStreamMerkleSegmentPost

> StreamMerkleSegmentResponse addSegmentToSessionApiV1EnterpriseStreamMerkleSegmentPost(streamMerkleSegmentRequest)

Add Segment To Session

Add a segment to an active streaming Merkle session.  Segments are buffered and combined into the Merkle tree incrementally. The tree is constructed using a bounded buffer approach for memory efficiency.  Set &#x60;is_final&#x3D;true&#x60; to finalize the session after adding this segment.

### Example

```ts
import {
  Configuration,
  StreamingMerkleApi,
} from '@encypher/sdk';
import type { AddSegmentToSessionApiV1EnterpriseStreamMerkleSegmentPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StreamingMerkleApi(config);

  const body = {
    // StreamMerkleSegmentRequest
    streamMerkleSegmentRequest: ...,
  } satisfies AddSegmentToSessionApiV1EnterpriseStreamMerkleSegmentPostRequest;

  try {
    const data = await api.addSegmentToSessionApiV1EnterpriseStreamMerkleSegmentPost(body);
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
| **streamMerkleSegmentRequest** | [StreamMerkleSegmentRequest](StreamMerkleSegmentRequest.md) |  | |

### Return type

[**StreamMerkleSegmentResponse**](StreamMerkleSegmentResponse.md)

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


## finalizeStreamingSessionApiV1EnterpriseStreamMerkleFinalizePost

> StreamMerkleFinalizeResponse finalizeStreamingSessionApiV1EnterpriseStreamMerkleFinalizePost(streamMerkleFinalizeRequest)

Finalize Streaming Session

Finalize a streaming Merkle session and compute the final root.  This completes the tree construction, computes the final root hash, and optionally embeds a C2PA manifest into the full document.

### Example

```ts
import {
  Configuration,
  StreamingMerkleApi,
} from '@encypher/sdk';
import type { FinalizeStreamingSessionApiV1EnterpriseStreamMerkleFinalizePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StreamingMerkleApi(config);

  const body = {
    // StreamMerkleFinalizeRequest
    streamMerkleFinalizeRequest: ...,
  } satisfies FinalizeStreamingSessionApiV1EnterpriseStreamMerkleFinalizePostRequest;

  try {
    const data = await api.finalizeStreamingSessionApiV1EnterpriseStreamMerkleFinalizePost(body);
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
| **streamMerkleFinalizeRequest** | [StreamMerkleFinalizeRequest](StreamMerkleFinalizeRequest.md) |  | |

### Return type

[**StreamMerkleFinalizeResponse**](StreamMerkleFinalizeResponse.md)

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


## getSessionStatusApiV1EnterpriseStreamMerkleStatusPost

> StreamMerkleStatusResponse getSessionStatusApiV1EnterpriseStreamMerkleStatusPost(streamMerkleStatusRequest)

Get Session Status

Check the status of a streaming Merkle session.

### Example

```ts
import {
  Configuration,
  StreamingMerkleApi,
} from '@encypher/sdk';
import type { GetSessionStatusApiV1EnterpriseStreamMerkleStatusPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StreamingMerkleApi(config);

  const body = {
    // StreamMerkleStatusRequest
    streamMerkleStatusRequest: ...,
  } satisfies GetSessionStatusApiV1EnterpriseStreamMerkleStatusPostRequest;

  try {
    const data = await api.getSessionStatusApiV1EnterpriseStreamMerkleStatusPost(body);
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
| **streamMerkleStatusRequest** | [StreamMerkleStatusRequest](StreamMerkleStatusRequest.md) |  | |

### Return type

[**StreamMerkleStatusResponse**](StreamMerkleStatusResponse.md)

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


## startStreamingMerkleSessionApiV1EnterpriseStreamMerkleStartPost

> StreamMerkleStartResponse startStreamingMerkleSessionApiV1EnterpriseStreamMerkleStartPost(streamMerkleStartRequest)

Start Streaming Merkle Session

Start a new streaming Merkle tree construction session.  This initiates a session that allows segments to be added incrementally, ideal for real-time LLM output signing where content is generated token-by-token.  **Tier Requirement:** Professional+  Patent Reference: FIG. 5 - Streaming Merkle Tree Construction

### Example

```ts
import {
  Configuration,
  StreamingMerkleApi,
} from '@encypher/sdk';
import type { StartStreamingMerkleSessionApiV1EnterpriseStreamMerkleStartPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StreamingMerkleApi(config);

  const body = {
    // StreamMerkleStartRequest
    streamMerkleStartRequest: ...,
  } satisfies StartStreamingMerkleSessionApiV1EnterpriseStreamMerkleStartPostRequest;

  try {
    const data = await api.startStreamingMerkleSessionApiV1EnterpriseStreamMerkleStartPost(body);
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
| **streamMerkleStartRequest** | [StreamMerkleStartRequest](StreamMerkleStartRequest.md) |  | |

### Return type

[**StreamMerkleStartResponse**](StreamMerkleStartResponse.md)

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
