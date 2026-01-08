# SigningApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**signAdvancedApiV1SignAdvancedPost**](SigningApi.md#signadvancedapiv1signadvancedpost) | **POST** /api/v1/sign/advanced | Sign Advanced |
| [**signContentApiV1SignPost**](SigningApi.md#signcontentapiv1signpost) | **POST** /api/v1/sign | Sign Content |



## signAdvancedApiV1SignAdvancedPost

> EncodeWithEmbeddingsResponse signAdvancedApiV1SignAdvancedPost(encodeWithEmbeddingsRequest)

Sign Advanced

### Example

```ts
import {
  Configuration,
  SigningApi,
} from '@encypher/sdk';
import type { SignAdvancedApiV1SignAdvancedPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new SigningApi(config);

  const body = {
    // EncodeWithEmbeddingsRequest
    encodeWithEmbeddingsRequest: ...,
  } satisfies SignAdvancedApiV1SignAdvancedPostRequest;

  try {
    const data = await api.signAdvancedApiV1SignAdvancedPost(body);
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

### Return type

[**EncodeWithEmbeddingsResponse**](EncodeWithEmbeddingsResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## signContentApiV1SignPost

> SignResponse signContentApiV1SignPost(signRequest)

Sign Content

Sign content with a C2PA manifest.

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
    // SignRequest
    signRequest: ...,
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
| **signRequest** | [SignRequest](SignRequest.md) |  | |

### Return type

[**SignResponse**](SignResponse.md)

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

