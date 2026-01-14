# MultiSourceAttributionApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**multiSourceLookupApiV1EnterpriseAttributionMultiSourcePost**](MultiSourceAttributionApi.md#multisourcelookupapiv1enterpriseattributionmultisourcepost) | **POST** /api/v1/enterprise/attribution/multi-source | Multi Source Lookup |



## multiSourceLookupApiV1EnterpriseAttributionMultiSourcePost

> MultiSourceLookupResponse multiSourceLookupApiV1EnterpriseAttributionMultiSourcePost(multiSourceLookupRequest)

Multi Source Lookup

Look up content across multiple sources.  Returns all matching sources with linked-list tracking, chronological ordering, and optional authority ranking.  **Tier Requirement:** Business+ (Authority ranking requires Enterprise)  Patent Reference: FIG. 8 - Multi-Source Hash Table Lookup

### Example

```ts
import {
  Configuration,
  MultiSourceAttributionApi,
} from '@encypher/sdk';
import type { MultiSourceLookupApiV1EnterpriseAttributionMultiSourcePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MultiSourceAttributionApi(config);

  const body = {
    // MultiSourceLookupRequest
    multiSourceLookupRequest: ...,
  } satisfies MultiSourceLookupApiV1EnterpriseAttributionMultiSourcePostRequest;

  try {
    const data = await api.multiSourceLookupApiV1EnterpriseAttributionMultiSourcePost(body);
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
| **multiSourceLookupRequest** | [MultiSourceLookupRequest](MultiSourceLookupRequest.md) |  | |

### Return type

[**MultiSourceLookupResponse**](MultiSourceLookupResponse.md)

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

