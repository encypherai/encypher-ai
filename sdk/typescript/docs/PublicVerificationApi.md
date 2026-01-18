# PublicVerificationApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**batchVerifyEmbeddingsApiV1PublicVerifyBatchPost**](PublicVerificationApi.md#batchverifyembeddingsapiv1publicverifybatchpost) | **POST** /api/v1/public/verify/batch | Batch Verify Embeddings (Public - No Auth Required) |
| [**extractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPost**](PublicVerificationApi.md#extractandverifyembeddingapiv1publicextractandverifypost) | **POST** /api/v1/public/extract-and-verify | Extract and Verify Invisible Embedding (Public - No Auth Required) |
| [**verifyEmbeddingApiV1PublicVerifyRefIdGet**](PublicVerificationApi.md#verifyembeddingapiv1publicverifyrefidget) | **GET** /api/v1/public/verify/{ref_id} | Verify Embedding (Public - No Auth Required) |



## batchVerifyEmbeddingsApiV1PublicVerifyBatchPost

> BatchVerifyResponse batchVerifyEmbeddingsApiV1PublicVerifyBatchPost(batchVerifyRequest, authorization)

Batch Verify Embeddings (Public - No Auth Required)

Verify multiple embeddings in a single request.          **This endpoint is PUBLIC and does NOT require authentication.**          Useful for:     - Verifying all embeddings on a page at once     - Bulk verification by web scrapers     - Browser extensions checking multiple paragraphs          **Rate Limiting:**     - 100 requests/hour per IP address     - Maximum 50 embeddings per request

### Example

```ts
import {
  Configuration,
  PublicVerificationApi,
} from '@encypher/sdk';
import type { BatchVerifyEmbeddingsApiV1PublicVerifyBatchPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new PublicVerificationApi();

  const body = {
    // BatchVerifyRequest
    batchVerifyRequest: ...,
    // string (optional)
    authorization: authorization_example,
  } satisfies BatchVerifyEmbeddingsApiV1PublicVerifyBatchPostRequest;

  try {
    const data = await api.batchVerifyEmbeddingsApiV1PublicVerifyBatchPost(body);
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
| **batchVerifyRequest** | [BatchVerifyRequest](BatchVerifyRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**BatchVerifyResponse**](BatchVerifyResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Batch verification completed |  -  |
| **400** | Invalid request |  -  |
| **429** | Rate limit exceeded |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## extractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPost

> ExtractAndVerifyResponse extractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPost(extractAndVerifyRequest, authorization)

Extract and Verify Invisible Embedding (Public - No Auth Required)

Extract and verify invisible Unicode embedding from text using encypher-ai.          **This endpoint is PUBLIC and does NOT require authentication.**          This is the NEW verification method for invisible embeddings:     - Extracts invisible Unicode variation selector embeddings     - Verifies cryptographic signature using encypher-ai     - Returns enterprise metadata (Merkle tree, document info, etc.)          **How it works:**     1. Text contains invisible Unicode variation selectors     2. encypher-ai extracts and verifies the embedded metadata     3. Enterprise API looks up Merkle tree and document info     4. Returns full verification result with all metadata          **Rate Limiting:**     - 1000 requests/hour per IP address          **Example Usage:**     &#x60;&#x60;&#x60;json     POST /api/v1/public/extract-and-verify     {       \&quot;text\&quot;: \&quot;Content with invisible embedding...\&quot;     }     &#x60;&#x60;&#x60;

### Example

```ts
import {
  Configuration,
  PublicVerificationApi,
} from '@encypher/sdk';
import type { ExtractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new PublicVerificationApi();

  const body = {
    // ExtractAndVerifyRequest
    extractAndVerifyRequest: ...,
    // string (optional)
    authorization: authorization_example,
  } satisfies ExtractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPostRequest;

  try {
    const data = await api.extractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPost(body);
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
| **extractAndVerifyRequest** | [ExtractAndVerifyRequest](ExtractAndVerifyRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ExtractAndVerifyResponse**](ExtractAndVerifyResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Embedding extracted and verified |  -  |
| **400** | Invalid request |  -  |
| **404** | No embedding found |  -  |
| **429** | Rate limit exceeded |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## verifyEmbeddingApiV1PublicVerifyRefIdGet

> VerifyEmbeddingResponse verifyEmbeddingApiV1PublicVerifyRefIdGet(refId, signature, authorization)

Verify Embedding (Public - No Auth Required)

Verify a minimal signed embedding and retrieve associated metadata.          **This endpoint is PUBLIC and does NOT require authentication.**          Third parties can use this endpoint to:     - Verify authenticity of content with embedded markers     - Retrieve document metadata (title, author, organization)     - Access C2PA manifest information     - View licensing terms     - Get Merkle proof for cryptographic verification          **Rate Limiting:**     - 1000 requests/hour per IP address     - CAPTCHA required after repeated failures          **Privacy:**     - Only returns text preview (first 200 characters)     - Full text content is NOT exposed     - Internal document IDs are mapped to public IDs          **Example Usage:**     &#x60;&#x60;&#x60;     GET /api/v1/public/verify/a3f9c2e1?signature&#x3D;8k3mP9xQ     &#x60;&#x60;&#x60;

### Example

```ts
import {
  Configuration,
  PublicVerificationApi,
} from '@encypher/sdk';
import type { VerifyEmbeddingApiV1PublicVerifyRefIdGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new PublicVerificationApi();

  const body = {
    // string
    refId: refId_example,
    // string | HMAC signature (8+ hex characters)
    signature: signature_example,
    // string (optional)
    authorization: authorization_example,
  } satisfies VerifyEmbeddingApiV1PublicVerifyRefIdGetRequest;

  try {
    const data = await api.verifyEmbeddingApiV1PublicVerifyRefIdGet(body);
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
| **refId** | `string` |  | [Defaults to `undefined`] |
| **signature** | `string` | HMAC signature (8+ hex characters) | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**VerifyEmbeddingResponse**](VerifyEmbeddingResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Embedding verified successfully |  -  |
| **400** | Invalid request |  -  |
| **404** | Embedding not found |  -  |
| **429** | Rate limit exceeded |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

