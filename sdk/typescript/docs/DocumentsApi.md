# DocumentsApi

All URIs are relative to *https://api.encypher.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**deleteDocumentApiV1DocumentsDocumentIdDelete**](DocumentsApi.md#deletedocumentapiv1documentsdocumentiddelete) | **DELETE** /api/v1/documents/{document_id} | Delete Document |
| [**deleteDocumentApiV1DocumentsDocumentIdDelete_0**](DocumentsApi.md#deletedocumentapiv1documentsdocumentiddelete_0) | **DELETE** /api/v1/documents/{document_id} | Delete Document |
| [**getDocumentApiV1DocumentsDocumentIdGet**](DocumentsApi.md#getdocumentapiv1documentsdocumentidget) | **GET** /api/v1/documents/{document_id} | Get Document |
| [**getDocumentApiV1DocumentsDocumentIdGet_0**](DocumentsApi.md#getdocumentapiv1documentsdocumentidget_0) | **GET** /api/v1/documents/{document_id} | Get Document |
| [**getDocumentHistoryApiV1DocumentsDocumentIdHistoryGet**](DocumentsApi.md#getdocumenthistoryapiv1documentsdocumentidhistoryget) | **GET** /api/v1/documents/{document_id}/history | Get Document History |
| [**getDocumentHistoryApiV1DocumentsDocumentIdHistoryGet_0**](DocumentsApi.md#getdocumenthistoryapiv1documentsdocumentidhistoryget_0) | **GET** /api/v1/documents/{document_id}/history | Get Document History |
| [**listDocumentsApiV1DocumentsGet**](DocumentsApi.md#listdocumentsapiv1documentsget) | **GET** /api/v1/documents | List Documents |
| [**listDocumentsApiV1DocumentsGet_0**](DocumentsApi.md#listdocumentsapiv1documentsget_0) | **GET** /api/v1/documents | List Documents |



## deleteDocumentApiV1DocumentsDocumentIdDelete

> DocumentDeleteResponse deleteDocumentApiV1DocumentsDocumentIdDelete(documentId, revoke, reason)

Delete Document

Soft delete a document.  By default, this also revokes the document so it will fail verification. The document is not permanently deleted but marked as deleted.

### Example

```ts
import {
  Configuration,
  DocumentsApi,
} from '@encypher/sdk';
import type { DeleteDocumentApiV1DocumentsDocumentIdDeleteRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new DocumentsApi(config);

  const body = {
    // string
    documentId: documentId_example,
    // boolean | Also revoke the document (optional)
    revoke: true,
    // string | Reason for deletion (optional)
    reason: reason_example,
  } satisfies DeleteDocumentApiV1DocumentsDocumentIdDeleteRequest;

  try {
    const data = await api.deleteDocumentApiV1DocumentsDocumentIdDelete(body);
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
| **revoke** | `boolean` | Also revoke the document | [Optional] [Defaults to `true`] |
| **reason** | `string` | Reason for deletion | [Optional] [Defaults to `undefined`] |

### Return type

[**DocumentDeleteResponse**](DocumentDeleteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## deleteDocumentApiV1DocumentsDocumentIdDelete_0

> DocumentDeleteResponse deleteDocumentApiV1DocumentsDocumentIdDelete_0(documentId, revoke, reason)

Delete Document

Soft delete a document.  By default, this also revokes the document so it will fail verification. The document is not permanently deleted but marked as deleted.

### Example

```ts
import {
  Configuration,
  DocumentsApi,
} from '@encypher/sdk';
import type { DeleteDocumentApiV1DocumentsDocumentIdDelete0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new DocumentsApi(config);

  const body = {
    // string
    documentId: documentId_example,
    // boolean | Also revoke the document (optional)
    revoke: true,
    // string | Reason for deletion (optional)
    reason: reason_example,
  } satisfies DeleteDocumentApiV1DocumentsDocumentIdDelete0Request;

  try {
    const data = await api.deleteDocumentApiV1DocumentsDocumentIdDelete_0(body);
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
| **revoke** | `boolean` | Also revoke the document | [Optional] [Defaults to `true`] |
| **reason** | `string` | Reason for deletion | [Optional] [Defaults to `undefined`] |

### Return type

[**DocumentDeleteResponse**](DocumentDeleteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getDocumentApiV1DocumentsDocumentIdGet

> DocumentDetailResponse getDocumentApiV1DocumentsDocumentIdGet(documentId)

Get Document

Get detailed information about a specific document.

### Example

```ts
import {
  Configuration,
  DocumentsApi,
} from '@encypher/sdk';
import type { GetDocumentApiV1DocumentsDocumentIdGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new DocumentsApi(config);

  const body = {
    // string
    documentId: documentId_example,
  } satisfies GetDocumentApiV1DocumentsDocumentIdGetRequest;

  try {
    const data = await api.getDocumentApiV1DocumentsDocumentIdGet(body);
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

[**DocumentDetailResponse**](DocumentDetailResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getDocumentApiV1DocumentsDocumentIdGet_0

> DocumentDetailResponse getDocumentApiV1DocumentsDocumentIdGet_0(documentId)

Get Document

Get detailed information about a specific document.

### Example

```ts
import {
  Configuration,
  DocumentsApi,
} from '@encypher/sdk';
import type { GetDocumentApiV1DocumentsDocumentIdGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new DocumentsApi(config);

  const body = {
    // string
    documentId: documentId_example,
  } satisfies GetDocumentApiV1DocumentsDocumentIdGet0Request;

  try {
    const data = await api.getDocumentApiV1DocumentsDocumentIdGet_0(body);
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

[**DocumentDetailResponse**](DocumentDetailResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getDocumentHistoryApiV1DocumentsDocumentIdHistoryGet

> DocumentHistoryResponse getDocumentHistoryApiV1DocumentsDocumentIdHistoryGet(documentId)

Get Document History

Get the audit trail/history for a document.  Shows all actions taken on the document including signing, verification, and revocation.

### Example

```ts
import {
  Configuration,
  DocumentsApi,
} from '@encypher/sdk';
import type { GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new DocumentsApi(config);

  const body = {
    // string
    documentId: documentId_example,
  } satisfies GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGetRequest;

  try {
    const data = await api.getDocumentHistoryApiV1DocumentsDocumentIdHistoryGet(body);
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

[**DocumentHistoryResponse**](DocumentHistoryResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getDocumentHistoryApiV1DocumentsDocumentIdHistoryGet_0

> DocumentHistoryResponse getDocumentHistoryApiV1DocumentsDocumentIdHistoryGet_0(documentId)

Get Document History

Get the audit trail/history for a document.  Shows all actions taken on the document including signing, verification, and revocation.

### Example

```ts
import {
  Configuration,
  DocumentsApi,
} from '@encypher/sdk';
import type { GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new DocumentsApi(config);

  const body = {
    // string
    documentId: documentId_example,
  } satisfies GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet0Request;

  try {
    const data = await api.getDocumentHistoryApiV1DocumentsDocumentIdHistoryGet_0(body);
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

[**DocumentHistoryResponse**](DocumentHistoryResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listDocumentsApiV1DocumentsGet

> DocumentListResponse listDocumentsApiV1DocumentsGet(page, pageSize, search, status, fromDate, toDate)

List Documents

List signed documents for the organization.  Supports pagination, search, and filtering by status and date range.

### Example

```ts
import {
  Configuration,
  DocumentsApi,
} from '@encypher/sdk';
import type { ListDocumentsApiV1DocumentsGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new DocumentsApi(config);

  const body = {
    // number | Page number (optional)
    page: 56,
    // number | Items per page (optional)
    pageSize: 56,
    // string | Search in title (optional)
    search: search_example,
    // string | Filter by status (active/revoked) (optional)
    status: status_example,
    // string | Filter from date (ISO format) (optional)
    fromDate: fromDate_example,
    // string | Filter to date (ISO format) (optional)
    toDate: toDate_example,
  } satisfies ListDocumentsApiV1DocumentsGetRequest;

  try {
    const data = await api.listDocumentsApiV1DocumentsGet(body);
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
| **page** | `number` | Page number | [Optional] [Defaults to `1`] |
| **pageSize** | `number` | Items per page | [Optional] [Defaults to `50`] |
| **search** | `string` | Search in title | [Optional] [Defaults to `undefined`] |
| **status** | `string` | Filter by status (active/revoked) | [Optional] [Defaults to `undefined`] |
| **fromDate** | `string` | Filter from date (ISO format) | [Optional] [Defaults to `undefined`] |
| **toDate** | `string` | Filter to date (ISO format) | [Optional] [Defaults to `undefined`] |

### Return type

[**DocumentListResponse**](DocumentListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listDocumentsApiV1DocumentsGet_0

> DocumentListResponse listDocumentsApiV1DocumentsGet_0(page, pageSize, search, status, fromDate, toDate)

List Documents

List signed documents for the organization.  Supports pagination, search, and filtering by status and date range.

### Example

```ts
import {
  Configuration,
  DocumentsApi,
} from '@encypher/sdk';
import type { ListDocumentsApiV1DocumentsGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new DocumentsApi(config);

  const body = {
    // number | Page number (optional)
    page: 56,
    // number | Items per page (optional)
    pageSize: 56,
    // string | Search in title (optional)
    search: search_example,
    // string | Filter by status (active/revoked) (optional)
    status: status_example,
    // string | Filter from date (ISO format) (optional)
    fromDate: fromDate_example,
    // string | Filter to date (ISO format) (optional)
    toDate: toDate_example,
  } satisfies ListDocumentsApiV1DocumentsGet0Request;

  try {
    const data = await api.listDocumentsApiV1DocumentsGet_0(body);
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
| **page** | `number` | Page number | [Optional] [Defaults to `1`] |
| **pageSize** | `number` | Items per page | [Optional] [Defaults to `50`] |
| **search** | `string` | Search in title | [Optional] [Defaults to `undefined`] |
| **status** | `string` | Filter by status (active/revoked) | [Optional] [Defaults to `undefined`] |
| **fromDate** | `string` | Filter from date (ISO format) | [Optional] [Defaults to `undefined`] |
| **toDate** | `string` | Filter to date (ISO format) | [Optional] [Defaults to `undefined`] |

### Return type

[**DocumentListResponse**](DocumentListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
