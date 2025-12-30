# StatusRevocationApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getDocumentStatusApiV1StatusDocumentsDocumentIdGet**](StatusRevocationApi.md#getdocumentstatusapiv1statusdocumentsdocumentidget) | **GET** /api/v1/status/documents/{document_id} | Get Document Status |
| [**getDocumentStatusApiV1StatusDocumentsDocumentIdGet_0**](StatusRevocationApi.md#getdocumentstatusapiv1statusdocumentsdocumentidget_0) | **GET** /api/v1/status/documents/{document_id} | Get Document Status |
| [**getStatusListApiV1StatusListOrganizationIdListIndexGet**](StatusRevocationApi.md#getstatuslistapiv1statuslistorganizationidlistindexget) | **GET** /api/v1/status/list/{organization_id}/{list_index} | Get Status List |
| [**getStatusListApiV1StatusListOrganizationIdListIndexGet_0**](StatusRevocationApi.md#getstatuslistapiv1statuslistorganizationidlistindexget_0) | **GET** /api/v1/status/list/{organization_id}/{list_index} | Get Status List |
| [**getStatusStatsApiV1StatusStatsGet**](StatusRevocationApi.md#getstatusstatsapiv1statusstatsget) | **GET** /api/v1/status/stats | Get Status Stats |
| [**getStatusStatsApiV1StatusStatsGet_0**](StatusRevocationApi.md#getstatusstatsapiv1statusstatsget_0) | **GET** /api/v1/status/stats | Get Status Stats |
| [**reinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost**](StatusRevocationApi.md#reinstatedocumentapiv1statusdocumentsdocumentidreinstatepost) | **POST** /api/v1/status/documents/{document_id}/reinstate | Reinstate Document |
| [**reinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost_0**](StatusRevocationApi.md#reinstatedocumentapiv1statusdocumentsdocumentidreinstatepost_0) | **POST** /api/v1/status/documents/{document_id}/reinstate | Reinstate Document |
| [**revokeDocumentApiV1StatusDocumentsDocumentIdRevokePost**](StatusRevocationApi.md#revokedocumentapiv1statusdocumentsdocumentidrevokepost) | **POST** /api/v1/status/documents/{document_id}/revoke | Revoke Document |
| [**revokeDocumentApiV1StatusDocumentsDocumentIdRevokePost_0**](StatusRevocationApi.md#revokedocumentapiv1statusdocumentsdocumentidrevokepost_0) | **POST** /api/v1/status/documents/{document_id}/revoke | Revoke Document |



## getDocumentStatusApiV1StatusDocumentsDocumentIdGet

> DocumentStatusResponse getDocumentStatusApiV1StatusDocumentsDocumentIdGet(documentId)

Get Document Status

Get the revocation status of a document.

### Example

```ts
import {
  Configuration,
  StatusRevocationApi,
} from '@encypher/sdk';
import type { GetDocumentStatusApiV1StatusDocumentsDocumentIdGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StatusRevocationApi(config);

  const body = {
    // string
    documentId: documentId_example,
  } satisfies GetDocumentStatusApiV1StatusDocumentsDocumentIdGetRequest;

  try {
    const data = await api.getDocumentStatusApiV1StatusDocumentsDocumentIdGet(body);
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

[**DocumentStatusResponse**](DocumentStatusResponse.md)

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


## getDocumentStatusApiV1StatusDocumentsDocumentIdGet_0

> DocumentStatusResponse getDocumentStatusApiV1StatusDocumentsDocumentIdGet_0(documentId)

Get Document Status

Get the revocation status of a document.

### Example

```ts
import {
  Configuration,
  StatusRevocationApi,
} from '@encypher/sdk';
import type { GetDocumentStatusApiV1StatusDocumentsDocumentIdGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StatusRevocationApi(config);

  const body = {
    // string
    documentId: documentId_example,
  } satisfies GetDocumentStatusApiV1StatusDocumentsDocumentIdGet0Request;

  try {
    const data = await api.getDocumentStatusApiV1StatusDocumentsDocumentIdGet_0(body);
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

[**DocumentStatusResponse**](DocumentStatusResponse.md)

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


## getStatusListApiV1StatusListOrganizationIdListIndexGet

> any getStatusListApiV1StatusListOrganizationIdListIndexGet(organizationId, listIndex)

Get Status List

Get a status list credential (public, no auth required).  This endpoint serves W3C StatusList2021 credentials for verification. Responses are designed to be cached by CDN with 5-minute TTL.  **Response Format:** W3C StatusList2021Credential (JSON-LD)

### Example

```ts
import {
  Configuration,
  StatusRevocationApi,
} from '@encypher/sdk';
import type { GetStatusListApiV1StatusListOrganizationIdListIndexGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new StatusRevocationApi();

  const body = {
    // string
    organizationId: organizationId_example,
    // number
    listIndex: 56,
  } satisfies GetStatusListApiV1StatusListOrganizationIdListIndexGetRequest;

  try {
    const data = await api.getStatusListApiV1StatusListOrganizationIdListIndexGet(body);
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
| **organizationId** | `string` |  | [Defaults to `undefined`] |
| **listIndex** | `number` |  | [Defaults to `undefined`] |

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


## getStatusListApiV1StatusListOrganizationIdListIndexGet_0

> any getStatusListApiV1StatusListOrganizationIdListIndexGet_0(organizationId, listIndex)

Get Status List

Get a status list credential (public, no auth required).  This endpoint serves W3C StatusList2021 credentials for verification. Responses are designed to be cached by CDN with 5-minute TTL.  **Response Format:** W3C StatusList2021Credential (JSON-LD)

### Example

```ts
import {
  Configuration,
  StatusRevocationApi,
} from '@encypher/sdk';
import type { GetStatusListApiV1StatusListOrganizationIdListIndexGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new StatusRevocationApi();

  const body = {
    // string
    organizationId: organizationId_example,
    // number
    listIndex: 56,
  } satisfies GetStatusListApiV1StatusListOrganizationIdListIndexGet0Request;

  try {
    const data = await api.getStatusListApiV1StatusListOrganizationIdListIndexGet_0(body);
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
| **organizationId** | `string` |  | [Defaults to `undefined`] |
| **listIndex** | `number` |  | [Defaults to `undefined`] |

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


## getStatusStatsApiV1StatusStatsGet

> any getStatusStatsApiV1StatusStatsGet()

Get Status Stats

Get status list statistics for the organization.

### Example

```ts
import {
  Configuration,
  StatusRevocationApi,
} from '@encypher/sdk';
import type { GetStatusStatsApiV1StatusStatsGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StatusRevocationApi(config);

  try {
    const data = await api.getStatusStatsApiV1StatusStatsGet();
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

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getStatusStatsApiV1StatusStatsGet_0

> any getStatusStatsApiV1StatusStatsGet_0()

Get Status Stats

Get status list statistics for the organization.

### Example

```ts
import {
  Configuration,
  StatusRevocationApi,
} from '@encypher/sdk';
import type { GetStatusStatsApiV1StatusStatsGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StatusRevocationApi(config);

  try {
    const data = await api.getStatusStatsApiV1StatusStatsGet_0();
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

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## reinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost

> RevocationResponse reinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost(documentId)

Reinstate Document

Reinstate a previously revoked document.  The document will pass verification again within 5 minutes (CDN cache TTL).

### Example

```ts
import {
  Configuration,
  StatusRevocationApi,
} from '@encypher/sdk';
import type { ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StatusRevocationApi(config);

  const body = {
    // string
    documentId: documentId_example,
  } satisfies ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePostRequest;

  try {
    const data = await api.reinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost(body);
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

[**RevocationResponse**](RevocationResponse.md)

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


## reinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost_0

> RevocationResponse reinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost_0(documentId)

Reinstate Document

Reinstate a previously revoked document.  The document will pass verification again within 5 minutes (CDN cache TTL).

### Example

```ts
import {
  Configuration,
  StatusRevocationApi,
} from '@encypher/sdk';
import type { ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StatusRevocationApi(config);

  const body = {
    // string
    documentId: documentId_example,
  } satisfies ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost0Request;

  try {
    const data = await api.reinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost_0(body);
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

[**RevocationResponse**](RevocationResponse.md)

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


## revokeDocumentApiV1StatusDocumentsDocumentIdRevokePost

> RevocationResponse revokeDocumentApiV1StatusDocumentsDocumentIdRevokePost(documentId, revokeRequest)

Revoke Document

Revoke a document\&#39;s authenticity.  The document will fail verification within 5 minutes (CDN cache TTL). This action is reversible via the reinstate endpoint.  **Revocation Reasons:** - &#x60;factual_error&#x60;: Content contains factual errors - &#x60;legal_takedown&#x60;: Legal request (DMCA, court order) - &#x60;copyright_claim&#x60;: Copyright infringement claim - &#x60;privacy_request&#x60;: Privacy/GDPR request - &#x60;publisher_request&#x60;: Publisher-initiated takedown - &#x60;security_concern&#x60;: Security vulnerability in content - &#x60;content_policy&#x60;: Violates content policy - &#x60;other&#x60;: Other reason (specify in reason_detail)

### Example

```ts
import {
  Configuration,
  StatusRevocationApi,
} from '@encypher/sdk';
import type { RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StatusRevocationApi(config);

  const body = {
    // string
    documentId: documentId_example,
    // RevokeRequest
    revokeRequest: ...,
  } satisfies RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePostRequest;

  try {
    const data = await api.revokeDocumentApiV1StatusDocumentsDocumentIdRevokePost(body);
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
| **revokeRequest** | [RevokeRequest](RevokeRequest.md) |  | |

### Return type

[**RevocationResponse**](RevocationResponse.md)

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


## revokeDocumentApiV1StatusDocumentsDocumentIdRevokePost_0

> RevocationResponse revokeDocumentApiV1StatusDocumentsDocumentIdRevokePost_0(documentId, revokeRequest)

Revoke Document

Revoke a document\&#39;s authenticity.  The document will fail verification within 5 minutes (CDN cache TTL). This action is reversible via the reinstate endpoint.  **Revocation Reasons:** - &#x60;factual_error&#x60;: Content contains factual errors - &#x60;legal_takedown&#x60;: Legal request (DMCA, court order) - &#x60;copyright_claim&#x60;: Copyright infringement claim - &#x60;privacy_request&#x60;: Privacy/GDPR request - &#x60;publisher_request&#x60;: Publisher-initiated takedown - &#x60;security_concern&#x60;: Security vulnerability in content - &#x60;content_policy&#x60;: Violates content policy - &#x60;other&#x60;: Other reason (specify in reason_detail)

### Example

```ts
import {
  Configuration,
  StatusRevocationApi,
} from '@encypher/sdk';
import type { RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new StatusRevocationApi(config);

  const body = {
    // string
    documentId: documentId_example,
    // RevokeRequest
    revokeRequest: ...,
  } satisfies RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost0Request;

  try {
    const data = await api.revokeDocumentApiV1StatusDocumentsDocumentIdRevokePost_0(body);
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
| **revokeRequest** | [RevokeRequest](RevokeRequest.md) |  | |

### Return type

[**RevocationResponse**](RevocationResponse.md)

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

