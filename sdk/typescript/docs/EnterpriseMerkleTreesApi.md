# EnterpriseMerkleTreesApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**detectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPost**](EnterpriseMerkleTreesApi.md#detectplagiarismapiv1enterprisemerkledetectplagiarismpost) | **POST** /api/v1/enterprise/merkle/detect-plagiarism | Detect Plagiarism |
| [**encodeDocumentApiV1EnterpriseMerkleEncodePost**](EnterpriseMerkleTreesApi.md#encodedocumentapiv1enterprisemerkleencodepost) | **POST** /api/v1/enterprise/merkle/encode | Encode Document into Merkle Trees |
| [**findSourcesApiV1EnterpriseMerkleAttributePost**](EnterpriseMerkleTreesApi.md#findsourcesapiv1enterprisemerkleattributepost) | **POST** /api/v1/enterprise/merkle/attribute | Find Source Documents |



## detectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPost

> PlagiarismDetectionResponse detectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPost(plagiarismDetectionRequest)

Detect Plagiarism

Analyze text for potential plagiarism by comparing against indexed documents.          This endpoint:     1. Segments the target text     2. Checks each segment against the Merkle tree index     3. Identifies matching source documents     4. Calculates match percentages and confidence scores     5. Generates a heat map showing which parts match          **Use Cases:**     - Academic plagiarism detection     - Content originality verification     - Copyright infringement detection     - Duplicate content identification          **Enterprise Tier Only**

### Example

```ts
import {
  Configuration,
  EnterpriseMerkleTreesApi,
} from '@encypher/sdk';
import type { DetectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new EnterpriseMerkleTreesApi(config);

  const body = {
    // PlagiarismDetectionRequest
    plagiarismDetectionRequest: ...,
  } satisfies DetectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPostRequest;

  try {
    const data = await api.detectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPost(body);
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
| **plagiarismDetectionRequest** | [PlagiarismDetectionRequest](PlagiarismDetectionRequest.md) |  | |

### Return type

[**PlagiarismDetectionResponse**](PlagiarismDetectionResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Analysis completed successfully |  -  |
| **400** | Invalid request |  -  |
| **401** | Unauthorized |  -  |
| **500** | Server error |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## encodeDocumentApiV1EnterpriseMerkleEncodePost

> DocumentEncodeResponse encodeDocumentApiV1EnterpriseMerkleEncodePost(documentEncodeRequest)

Encode Document into Merkle Trees

Encode a document into Merkle trees at specified segmentation levels.          This endpoint:     1. Segments the document text at multiple levels (word/sentence/paragraph/section)     2. Builds Merkle trees for each segmentation level     3. Stores all tree data in the database for future attribution queries     4. Returns root hashes and tree metadata          **Enterprise Tier Only** - Requires valid organization with Merkle features enabled.          **Rate Limits:**     - Free tier: Not available     - Enterprise tier: 1000 documents/month          **Processing Time:**     - Small documents (&lt;1000 words): ~100-200ms     - Medium documents (1000-10000 words): ~500ms-2s     - Large documents (&gt;10000 words): ~2-10s

### Example

```ts
import {
  Configuration,
  EnterpriseMerkleTreesApi,
} from '@encypher/sdk';
import type { EncodeDocumentApiV1EnterpriseMerkleEncodePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new EnterpriseMerkleTreesApi(config);

  const body = {
    // DocumentEncodeRequest
    documentEncodeRequest: ...,
  } satisfies EncodeDocumentApiV1EnterpriseMerkleEncodePostRequest;

  try {
    const data = await api.encodeDocumentApiV1EnterpriseMerkleEncodePost(body);
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
| **documentEncodeRequest** | [DocumentEncodeRequest](DocumentEncodeRequest.md) |  | |

### Return type

[**DocumentEncodeResponse**](DocumentEncodeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Document encoded successfully |  -  |
| **400** | Invalid request |  -  |
| **401** | Unauthorized |  -  |
| **403** | Quota exceeded or feature not enabled |  -  |
| **500** | Server error |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## findSourcesApiV1EnterpriseMerkleAttributePost

> SourceAttributionResponse findSourcesApiV1EnterpriseMerkleAttributePost(sourceAttributionRequest)

Find Source Documents

Find source documents that contain a specific text segment.          This endpoint searches the Merkle tree index to find which documents     contain the provided text segment.          **Use Cases:**     - Verify if a text segment appears in your document repository     - Find the original source of a quote or passage     - Check if content has been previously published          **Enterprise Tier Only**

### Example

```ts
import {
  Configuration,
  EnterpriseMerkleTreesApi,
} from '@encypher/sdk';
import type { FindSourcesApiV1EnterpriseMerkleAttributePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new EnterpriseMerkleTreesApi(config);

  const body = {
    // SourceAttributionRequest
    sourceAttributionRequest: ...,
  } satisfies FindSourcesApiV1EnterpriseMerkleAttributePostRequest;

  try {
    const data = await api.findSourcesApiV1EnterpriseMerkleAttributePost(body);
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
| **sourceAttributionRequest** | [SourceAttributionRequest](SourceAttributionRequest.md) |  | |

### Return type

[**SourceAttributionResponse**](SourceAttributionResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Search completed successfully |  -  |
| **400** | Invalid request |  -  |
| **401** | Unauthorized |  -  |
| **500** | Server error |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

