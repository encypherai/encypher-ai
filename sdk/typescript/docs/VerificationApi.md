# VerificationApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getStatsApiV1VerifyStatsGet**](VerificationApi.md#getstatsapiv1verifystatsget) | **GET** /api/v1/verify/stats | Get Stats |
| [**getVerificationHistoryApiV1VerifyHistoryDocumentIdGet**](VerificationApi.md#getverificationhistoryapiv1verifyhistorydocumentidget) | **GET** /api/v1/verify/history/{document_id} | Get Verification History |
| [**healthCheckApiV1VerifyHealthGet**](VerificationApi.md#healthcheckapiv1verifyhealthget) | **GET** /api/v1/verify/health | Health Check |
| [**verifyAdvancedApiV1VerifyAdvancedPost**](VerificationApi.md#verifyadvancedapiv1verifyadvancedpost) | **POST** /api/v1/verify/advanced | Advanced verification |
| [**verifyByDocumentIdApiV1VerifyDocumentIdGet**](VerificationApi.md#verifybydocumentidapiv1verifydocumentidget) | **GET** /api/v1/verify/{document_id} | Verify By Document Id |
| [**verifyDocumentApiV1VerifyDocumentPost**](VerificationApi.md#verifydocumentapiv1verifydocumentpost) | **POST** /api/v1/verify/document | Verify Document |
| [**verifySignatureApiV1VerifySignaturePost**](VerificationApi.md#verifysignatureapiv1verifysignaturepost) | **POST** /api/v1/verify/signature | Verify Signature |
| [**verifyTextApiV1VerifyPost**](VerificationApi.md#verifytextapiv1verifypost) | **POST** /api/v1/verify | Verify Text |



## getStatsApiV1VerifyStatsGet

> VerificationStats getStatsApiV1VerifyStatsGet(authorization)

Get Stats

Get verification statistics

### Example

```ts
import {
  Configuration,
  VerificationApi,
} from '@encypher/sdk';
import type { GetStatsApiV1VerifyStatsGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new VerificationApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
  } satisfies GetStatsApiV1VerifyStatsGetRequest;

  try {
    const data = await api.getStatsApiV1VerifyStatsGet(body);
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
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**VerificationStats**](VerificationStats.md)

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


## getVerificationHistoryApiV1VerifyHistoryDocumentIdGet

> Array&lt;VerificationHistory&gt; getVerificationHistoryApiV1VerifyHistoryDocumentIdGet(documentId, limit)

Get Verification History

Get verification history for a document (public endpoint)  - **document_id**: Document ID - **limit**: Maximum number of results

### Example

```ts
import {
  Configuration,
  VerificationApi,
} from '@encypher/sdk';
import type { GetVerificationHistoryApiV1VerifyHistoryDocumentIdGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new VerificationApi();

  const body = {
    // string
    documentId: documentId_example,
    // number (optional)
    limit: 56,
  } satisfies GetVerificationHistoryApiV1VerifyHistoryDocumentIdGetRequest;

  try {
    const data = await api.getVerificationHistoryApiV1VerifyHistoryDocumentIdGet(body);
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
| **limit** | `number` |  | [Optional] [Defaults to `100`] |

### Return type

[**Array&lt;VerificationHistory&gt;**](VerificationHistory.md)

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


## healthCheckApiV1VerifyHealthGet

> any healthCheckApiV1VerifyHealthGet()

Health Check

Health check endpoint

### Example

```ts
import {
  Configuration,
  VerificationApi,
} from '@encypher/sdk';
import type { HealthCheckApiV1VerifyHealthGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new VerificationApi();

  try {
    const data = await api.healthCheckApiV1VerifyHealthGet();
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

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## verifyAdvancedApiV1VerifyAdvancedPost

> any verifyAdvancedApiV1VerifyAdvancedPost(verifyAdvancedRequest)

Advanced verification

Verify signed content and optionally run attribution/plagiarism analysis.

### Example

```ts
import {
  Configuration,
  VerificationApi,
} from '@encypher/sdk';
import type { VerifyAdvancedApiV1VerifyAdvancedPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new VerificationApi(config);

  const body = {
    // VerifyAdvancedRequest
    verifyAdvancedRequest: ...,
  } satisfies VerifyAdvancedApiV1VerifyAdvancedPostRequest;

  try {
    const data = await api.verifyAdvancedApiV1VerifyAdvancedPost(body);
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
| **verifyAdvancedRequest** | [VerifyAdvancedRequest](VerifyAdvancedRequest.md) |  | |

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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## verifyByDocumentIdApiV1VerifyDocumentIdGet

> any verifyByDocumentIdApiV1VerifyDocumentIdGet(documentId)

Verify By Document Id

Verify a document by its ID (for clickable verification links).  Returns an HTML page so users can preview verification state in a browser. This endpoint queries the content database for the signed document.

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


## verifyDocumentApiV1VerifyDocumentPost

> VerificationResponse verifyDocumentApiV1VerifyDocumentPost(documentVerify, xForwardedFor, userAgent, authorization)

Verify Document

Complete document verification (public endpoint)  - **document_id**: Document ID from encoding service - **content**: Current content to verify

### Example

```ts
import {
  Configuration,
  VerificationApi,
} from '@encypher/sdk';
import type { VerifyDocumentApiV1VerifyDocumentPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new VerificationApi();

  const body = {
    // DocumentVerify
    documentVerify: ...,
    // string (optional)
    xForwardedFor: xForwardedFor_example,
    // string (optional)
    userAgent: userAgent_example,
    // string (optional)
    authorization: authorization_example,
  } satisfies VerifyDocumentApiV1VerifyDocumentPostRequest;

  try {
    const data = await api.verifyDocumentApiV1VerifyDocumentPost(body);
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
| **documentVerify** | [DocumentVerify](DocumentVerify.md) |  | |
| **xForwardedFor** | `string` |  | [Optional] [Defaults to `undefined`] |
| **userAgent** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**VerificationResponse**](VerificationResponse.md)

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


## verifySignatureApiV1VerifySignaturePost

> VerificationResponse verifySignatureApiV1VerifySignaturePost(signatureVerify, xForwardedFor, userAgent, authorization)

Verify Signature

Verify a signature (public endpoint)  - **content**: Original content - **signature**: Hex-encoded signature - **public_key_pem**: PEM-encoded public key

### Example

```ts
import {
  Configuration,
  VerificationApi,
} from '@encypher/sdk';
import type { VerifySignatureApiV1VerifySignaturePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new VerificationApi();

  const body = {
    // SignatureVerify
    signatureVerify: ...,
    // string (optional)
    xForwardedFor: xForwardedFor_example,
    // string (optional)
    userAgent: userAgent_example,
    // string (optional)
    authorization: authorization_example,
  } satisfies VerifySignatureApiV1VerifySignaturePostRequest;

  try {
    const data = await api.verifySignatureApiV1VerifySignaturePost(body);
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
| **signatureVerify** | [SignatureVerify](SignatureVerify.md) |  | |
| **xForwardedFor** | `string` |  | [Optional] [Defaults to `undefined`] |
| **userAgent** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**VerificationResponse**](VerificationResponse.md)

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


## verifyTextApiV1VerifyPost

> VerifyResponse verifyTextApiV1VerifyPost(verifyRequest, authorization)

Verify Text

Verify signed content and return a structured verdict.

### Example

```ts
import {
  Configuration,
  VerificationApi,
} from '@encypher/sdk';
import type { VerifyTextApiV1VerifyPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new VerificationApi();

  const body = {
    // VerifyRequest
    verifyRequest: ...,
    // string (optional)
    authorization: authorization_example,
  } satisfies VerifyTextApiV1VerifyPostRequest;

  try {
    const data = await api.verifyTextApiV1VerifyPost(body);
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
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

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

