# SigningApi

All URIs are relative to *https://api.encypher.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**signAdvancedApiV1SignAdvancedPost**](SigningApi.md#signadvancedapiv1signadvancedpost) | **POST** /api/v1/sign/advanced | REMOVED - Use POST /sign with options instead |
| [**signContentApiV1SignPost**](SigningApi.md#signcontentapiv1signpost) | **POST** /api/v1/sign | Sign content with C2PA manifest |



## signAdvancedApiV1SignAdvancedPost

> any signAdvancedApiV1SignAdvancedPost()

REMOVED - Use POST /sign with options instead

**⚠️ REMOVED: This endpoint has been removed.**  Please use &#x60;POST /sign&#x60; with options instead.  Migration example: &#x60;&#x60;&#x60;json // Old /sign/advanced request {     \&quot;document_id\&quot;: \&quot;doc1\&quot;,     \&quot;text\&quot;: \&quot;...\&quot;,     \&quot;segmentation_level\&quot;: \&quot;sentence\&quot; }  // New /sign request {     \&quot;text\&quot;: \&quot;...\&quot;,     \&quot;document_id\&quot;: \&quot;doc1\&quot;,     \&quot;options\&quot;: {         \&quot;segmentation_level\&quot;: \&quot;sentence\&quot;     } } &#x60;&#x60;&#x60;

### Example

```ts
import {
  Configuration,
  SigningApi,
} from '@encypher/sdk';
import type { SignAdvancedApiV1SignAdvancedPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new SigningApi();

  try {
    const data = await api.signAdvancedApiV1SignAdvancedPost();
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
| **410** | Endpoint removed |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## signContentApiV1SignPost

> any signContentApiV1SignPost(unifiedSignRequest)

Sign content with C2PA manifest

Sign content with C2PA manifest. Features are gated by tier.  **Tier Feature Matrix:**  | Feature | Free/Starter | Professional | Business | Enterprise | |---------|--------------|--------------|----------|------------| | Basic C2PA signing | ✅ | ✅ | ✅ | ✅ | | Sentence segmentation | ❌ | ✅ | ✅ | ✅ | | Advanced manifest modes | ❌ | ✅ | ✅ | ✅ | | Attribution indexing | ❌ | ✅ | ✅ | ✅ | | Custom assertions | ❌ | ❌ | ✅ | ✅ | | Rights metadata | ❌ | ❌ | ✅ | ✅ | | Dual binding | ❌ | ❌ | ❌ | ✅ | | Fingerprinting | ❌ | ❌ | ❌ | ✅ | | Batch size | 1 | 10 | 50 | 100 |  **Single Document:** &#x60;&#x60;&#x60;json {     \&quot;text\&quot;: \&quot;Content to sign...\&quot;,     \&quot;document_title\&quot;: \&quot;My Article\&quot;,     \&quot;options\&quot;: {         \&quot;segmentation_level\&quot;: \&quot;sentence\&quot;     } } &#x60;&#x60;&#x60;  **Batch (Professional+):** &#x60;&#x60;&#x60;json {     \&quot;documents\&quot;: [         {\&quot;text\&quot;: \&quot;First doc...\&quot;, \&quot;document_title\&quot;: \&quot;Doc 1\&quot;},         {\&quot;text\&quot;: \&quot;Second doc...\&quot;, \&quot;document_title\&quot;: \&quot;Doc 2\&quot;}     ],     \&quot;options\&quot;: {         \&quot;segmentation_level\&quot;: \&quot;sentence\&quot;     } } &#x60;&#x60;&#x60;  The response includes &#x60;meta.features_gated&#x60; showing features available at higher tiers.

### Example

```ts
import {
  Configuration,
  SigningApi,
} from '@encypher/sdk';
import type { SignContentApiV1SignPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new SigningApi(config);

  const body = {
    // UnifiedSignRequest
    unifiedSignRequest: ...,
  } satisfies SignContentApiV1SignPostRequest;

  try {
    const data = await api.signContentApiV1SignPost(body);
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
| **unifiedSignRequest** | [UnifiedSignRequest](UnifiedSignRequest.md) |  | |

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
| **201** | Content signed successfully |  -  |
| **400** | Invalid request |  -  |
| **403** | Feature requires higher tier |  -  |
| **429** | Rate limit exceeded |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
