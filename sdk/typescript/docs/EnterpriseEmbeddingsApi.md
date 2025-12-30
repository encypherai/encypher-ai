# EnterpriseEmbeddingsApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**encodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPost**](EnterpriseEmbeddingsApi.md#encodewithembeddingsapiv1enterpriseembeddingsencodewithembeddingspost) | **POST** /api/v1/enterprise/embeddings/encode-with-embeddings | Encode With Embeddings |
| [**signAdvancedApiV1EnterpriseEmbeddingsSignAdvancedPost**](EnterpriseEmbeddingsApi.md#signadvancedapiv1enterpriseembeddingssignadvancedpost) | **POST** /api/v1/enterprise/embeddings/sign/advanced | Sign Advanced |



## encodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPost

> EncodeWithEmbeddingsResponse encodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPost(encodeWithEmbeddingsRequest, authorization)

Encode With Embeddings

Encode a document with invisible embeddings.  **Alias:** POST /enterprise/sign/advanced

### Example

```ts
import {
  Configuration,
  EnterpriseEmbeddingsApi,
} from '@encypher/sdk';
import type { EncodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new EnterpriseEmbeddingsApi();

  const body = {
    // EncodeWithEmbeddingsRequest
    encodeWithEmbeddingsRequest: ...,
    // string (optional)
    authorization: authorization_example,
  } satisfies EncodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPostRequest;

  try {
    const data = await api.encodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPost(body);
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
| **encodeWithEmbeddingsRequest** | [EncodeWithEmbeddingsRequest](EncodeWithEmbeddingsRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**EncodeWithEmbeddingsResponse**](EncodeWithEmbeddingsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## signAdvancedApiV1EnterpriseEmbeddingsSignAdvancedPost

> EncodeWithEmbeddingsResponse signAdvancedApiV1EnterpriseEmbeddingsSignAdvancedPost(encodeWithEmbeddingsRequest, authorization)

Sign Advanced

Sign a document with advanced invisible embeddings.  This is an alias for POST /enterprise/embeddings/encode-with-embeddings with a clearer name. Creates C2PA-compliant invisible signatures.  Requires Professional or Enterprise tier.

### Example

```ts
import {
  Configuration,
  EnterpriseEmbeddingsApi,
} from '@encypher/sdk';
import type { SignAdvancedApiV1EnterpriseEmbeddingsSignAdvancedPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new EnterpriseEmbeddingsApi();

  const body = {
    // EncodeWithEmbeddingsRequest
    encodeWithEmbeddingsRequest: ...,
    // string (optional)
    authorization: authorization_example,
  } satisfies SignAdvancedApiV1EnterpriseEmbeddingsSignAdvancedPostRequest;

  try {
    const data = await api.signAdvancedApiV1EnterpriseEmbeddingsSignAdvancedPost(body);
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
| **encodeWithEmbeddingsRequest** | [EncodeWithEmbeddingsRequest](EncodeWithEmbeddingsRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**EncodeWithEmbeddingsResponse**](EncodeWithEmbeddingsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

