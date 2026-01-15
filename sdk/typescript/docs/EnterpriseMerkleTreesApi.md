# EnterpriseMerkleTreesApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**encodeDocumentApiV1EnterpriseMerkleEncodePost**](EnterpriseMerkleTreesApi.md#encodedocumentapiv1enterprisemerkleencodepost) | **POST** /api/v1/enterprise/merkle/encode | Encode Document into Merkle Trees |



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

