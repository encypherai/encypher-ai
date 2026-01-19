# BatchApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**batchSignApiV1BatchSignPost**](BatchApi.md#batchsignapiv1batchsignpost) | **POST** /api/v1/batch/sign | Batch Sign |
| [**batchVerifyApiV1BatchVerifyPost**](BatchApi.md#batchverifyapiv1batchverifypost) | **POST** /api/v1/batch/verify | Batch Verify |



## batchSignApiV1BatchSignPost

> BatchResponseEnvelope batchSignApiV1BatchSignPost(batchSignRequest)

Batch Sign

Sign multiple documents in a single request.

### Example

```ts
import {
  Configuration,
  BatchApi,
} from '@encypher/sdk';
import type { BatchSignApiV1BatchSignPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new BatchApi(config);

  const body = {
    // BatchSignRequest
    batchSignRequest: ...,
  } satisfies BatchSignApiV1BatchSignPostRequest;

  try {
    const data = await api.batchSignApiV1BatchSignPost(body);
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
| **batchSignRequest** | [BatchSignRequest](BatchSignRequest.md) |  | |

### Return type

[**BatchResponseEnvelope**](BatchResponseEnvelope.md)

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


## batchVerifyApiV1BatchVerifyPost

> BatchResponseEnvelope batchVerifyApiV1BatchVerifyPost(appSchemasBatchBatchVerifyRequest)

Batch Verify

Verify multiple documents in a single request.

### Example

```ts
import {
  Configuration,
  BatchApi,
} from '@encypher/sdk';
import type { BatchVerifyApiV1BatchVerifyPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new BatchApi(config);

  const body = {
    // AppSchemasBatchBatchVerifyRequest
    appSchemasBatchBatchVerifyRequest: ...,
  } satisfies BatchVerifyApiV1BatchVerifyPostRequest;

  try {
    const data = await api.batchVerifyApiV1BatchVerifyPost(body);
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
| **appSchemasBatchBatchVerifyRequest** | [AppSchemasBatchBatchVerifyRequest](AppSchemasBatchBatchVerifyRequest.md) |  | |

### Return type

[**BatchResponseEnvelope**](BatchResponseEnvelope.md)

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

