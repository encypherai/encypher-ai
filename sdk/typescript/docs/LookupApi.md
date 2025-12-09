# LookupApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**lookupSentenceApiV1LookupPost**](LookupApi.md#lookupsentenceapiv1lookuppost) | **POST** /api/v1/lookup | Lookup Sentence |



## lookupSentenceApiV1LookupPost

> LookupResponse lookupSentenceApiV1LookupPost(lookupRequest)

Lookup Sentence

Look up sentence provenance by hash.  This endpoint allows anyone to paste a sentence and find which document it originally came from, along with metadata about the publisher.  Use case: User pastes a sentence, we find which document it came from.  Note: This endpoint does NOT require authentication (public lookup).  Args:     request: LookupRequest containing sentence text     db: Database session  Returns:     LookupResponse with document and organization details if found

### Example

```ts
import {
  Configuration,
  LookupApi,
} from '@encypher/sdk';
import type { LookupSentenceApiV1LookupPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LookupApi();

  const body = {
    // LookupRequest
    lookupRequest: ...,
  } satisfies LookupSentenceApiV1LookupPostRequest;

  try {
    const data = await api.lookupSentenceApiV1LookupPost(body);
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
| **lookupRequest** | [LookupRequest](LookupRequest.md) |  | |

### Return type

[**LookupResponse**](LookupResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

