# VerificationApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**verifyByDocumentIdApiV1VerifyDocumentIdGet**](VerificationApi.md#verifybydocumentidapiv1verifydocumentidget) | **GET** /api/v1/verify/{document_id} | Verify By Document Id |
| [**verifyContentApiV1VerifyPost**](VerificationApi.md#verifycontentapiv1verifypost) | **POST** /api/v1/verify | Verify Content |



## verifyByDocumentIdApiV1VerifyDocumentIdGet

> any verifyByDocumentIdApiV1VerifyDocumentIdGet(documentId)

Verify By Document Id

Verify a document by its ID (for clickable verification links).  Returns an HTML page so users can preview verification state in a browser.

### Example

```ts
import {
  Configuration,
  VerificationApi,
} from '@encypher/sdk';
import type { VerifyByDocumentIdApiV1VerifyDocumentIdGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new VerificationApi();

  const body = {
    // string
    documentId: documentId_example,
  } satisfies VerifyByDocumentIdApiV1VerifyDocumentIdGetRequest;

  try {
    const data = await api.verifyByDocumentIdApiV1VerifyDocumentIdGet(body);
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
| **documentId** | `string` |  | [Defaults to `undefined`] |

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
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## verifyContentApiV1VerifyPost

> VerifyResponse verifyContentApiV1VerifyPost(verifyRequest)

Verify Content

Verify C2PA manifest in signed content using the encypher-ai library.  This endpoint is public, rate limited, and returns structured machine-friendly verdicts that SDKs consume.

### Example

```ts
import {
  Configuration,
  VerificationApi,
} from '@encypher/sdk';
import type { VerifyContentApiV1VerifyPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new VerificationApi();

  const body = {
    // VerifyRequest
    verifyRequest: ...,
  } satisfies VerifyContentApiV1VerifyPostRequest;

  try {
    const data = await api.verifyContentApiV1VerifyPost(body);
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
| **verifyRequest** | [VerifyRequest](VerifyRequest.md) |  | |

### Return type

[**VerifyResponse**](VerifyResponse.md)

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

