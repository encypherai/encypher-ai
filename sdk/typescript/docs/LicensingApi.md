# LicensingApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createAgreementApiV1LicensingAgreementsPost**](LicensingApi.md#createagreementapiv1licensingagreementspost) | **POST** /api/v1/licensing/agreements | Create Agreement |
| [**createAgreementApiV1LicensingAgreementsPost_0**](LicensingApi.md#createagreementapiv1licensingagreementspost_0) | **POST** /api/v1/licensing/agreements | Create Agreement |
| [**createRevenueDistributionApiV1LicensingDistributionsPost**](LicensingApi.md#createrevenuedistributionapiv1licensingdistributionspost) | **POST** /api/v1/licensing/distributions | Create Revenue Distribution |
| [**createRevenueDistributionApiV1LicensingDistributionsPost_0**](LicensingApi.md#createrevenuedistributionapiv1licensingdistributionspost_0) | **POST** /api/v1/licensing/distributions | Create Revenue Distribution |
| [**getAgreementApiV1LicensingAgreementsAgreementIdGet**](LicensingApi.md#getagreementapiv1licensingagreementsagreementidget) | **GET** /api/v1/licensing/agreements/{agreement_id} | Get Agreement |
| [**getAgreementApiV1LicensingAgreementsAgreementIdGet_0**](LicensingApi.md#getagreementapiv1licensingagreementsagreementidget_0) | **GET** /api/v1/licensing/agreements/{agreement_id} | Get Agreement |
| [**getDistributionApiV1LicensingDistributionsDistributionIdGet**](LicensingApi.md#getdistributionapiv1licensingdistributionsdistributionidget) | **GET** /api/v1/licensing/distributions/{distribution_id} | Get Distribution |
| [**getDistributionApiV1LicensingDistributionsDistributionIdGet_0**](LicensingApi.md#getdistributionapiv1licensingdistributionsdistributionidget_0) | **GET** /api/v1/licensing/distributions/{distribution_id} | Get Distribution |
| [**listAgreementsApiV1LicensingAgreementsGet**](LicensingApi.md#listagreementsapiv1licensingagreementsget) | **GET** /api/v1/licensing/agreements | List Agreements |
| [**listAgreementsApiV1LicensingAgreementsGet_0**](LicensingApi.md#listagreementsapiv1licensingagreementsget_0) | **GET** /api/v1/licensing/agreements | List Agreements |
| [**listAvailableContentApiV1LicensingContentGet**](LicensingApi.md#listavailablecontentapiv1licensingcontentget) | **GET** /api/v1/licensing/content | List Available Content |
| [**listAvailableContentApiV1LicensingContentGet_0**](LicensingApi.md#listavailablecontentapiv1licensingcontentget_0) | **GET** /api/v1/licensing/content | List Available Content |
| [**listDistributionsApiV1LicensingDistributionsGet**](LicensingApi.md#listdistributionsapiv1licensingdistributionsget) | **GET** /api/v1/licensing/distributions | List Distributions |
| [**listDistributionsApiV1LicensingDistributionsGet_0**](LicensingApi.md#listdistributionsapiv1licensingdistributionsget_0) | **GET** /api/v1/licensing/distributions | List Distributions |
| [**processPayoutsApiV1LicensingPayoutsPost**](LicensingApi.md#processpayoutsapiv1licensingpayoutspost) | **POST** /api/v1/licensing/payouts | Process Payouts |
| [**processPayoutsApiV1LicensingPayoutsPost_0**](LicensingApi.md#processpayoutsapiv1licensingpayoutspost_0) | **POST** /api/v1/licensing/payouts | Process Payouts |
| [**terminateAgreementApiV1LicensingAgreementsAgreementIdDelete**](LicensingApi.md#terminateagreementapiv1licensingagreementsagreementiddelete) | **DELETE** /api/v1/licensing/agreements/{agreement_id} | Terminate Agreement |
| [**terminateAgreementApiV1LicensingAgreementsAgreementIdDelete_0**](LicensingApi.md#terminateagreementapiv1licensingagreementsagreementiddelete_0) | **DELETE** /api/v1/licensing/agreements/{agreement_id} | Terminate Agreement |
| [**trackContentAccessApiV1LicensingTrackAccessPost**](LicensingApi.md#trackcontentaccessapiv1licensingtrackaccesspost) | **POST** /api/v1/licensing/track-access | Track Content Access |
| [**trackContentAccessApiV1LicensingTrackAccessPost_0**](LicensingApi.md#trackcontentaccessapiv1licensingtrackaccesspost_0) | **POST** /api/v1/licensing/track-access | Track Content Access |
| [**updateAgreementApiV1LicensingAgreementsAgreementIdPatch**](LicensingApi.md#updateagreementapiv1licensingagreementsagreementidpatch) | **PATCH** /api/v1/licensing/agreements/{agreement_id} | Update Agreement |
| [**updateAgreementApiV1LicensingAgreementsAgreementIdPatch_0**](LicensingApi.md#updateagreementapiv1licensingagreementsagreementidpatch_0) | **PATCH** /api/v1/licensing/agreements/{agreement_id} | Update Agreement |



## createAgreementApiV1LicensingAgreementsPost

> LicensingAgreementCreateResponse createAgreementApiV1LicensingAgreementsPost(licensingAgreementCreate)

Create Agreement

Create a new licensing agreement with an AI company.  **Admin only** - Creates agreement and generates API key for AI company.  Returns:     Agreement details including the API key (only shown once)

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { CreateAgreementApiV1LicensingAgreementsPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // LicensingAgreementCreate
    licensingAgreementCreate: ...,
  } satisfies CreateAgreementApiV1LicensingAgreementsPostRequest;

  try {
    const data = await api.createAgreementApiV1LicensingAgreementsPost(body);
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
| **licensingAgreementCreate** | [LicensingAgreementCreate](LicensingAgreementCreate.md) |  | |

### Return type

[**LicensingAgreementCreateResponse**](LicensingAgreementCreateResponse.md)

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


## createAgreementApiV1LicensingAgreementsPost_0

> LicensingAgreementCreateResponse createAgreementApiV1LicensingAgreementsPost_0(licensingAgreementCreate)

Create Agreement

Create a new licensing agreement with an AI company.  **Admin only** - Creates agreement and generates API key for AI company.  Returns:     Agreement details including the API key (only shown once)

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { CreateAgreementApiV1LicensingAgreementsPost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // LicensingAgreementCreate
    licensingAgreementCreate: ...,
  } satisfies CreateAgreementApiV1LicensingAgreementsPost0Request;

  try {
    const data = await api.createAgreementApiV1LicensingAgreementsPost_0(body);
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
| **licensingAgreementCreate** | [LicensingAgreementCreate](LicensingAgreementCreate.md) |  | |

### Return type

[**LicensingAgreementCreateResponse**](LicensingAgreementCreateResponse.md)

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


## createRevenueDistributionApiV1LicensingDistributionsPost

> RevenueDistributionResponse createRevenueDistributionApiV1LicensingDistributionsPost(revenueDistributionCreate)

Create Revenue Distribution

Create revenue distribution for a period.  **Admin only** - Calculates and creates revenue distribution based on content access during the specified period. Implements 70/30 split.

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { CreateRevenueDistributionApiV1LicensingDistributionsPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // RevenueDistributionCreate
    revenueDistributionCreate: ...,
  } satisfies CreateRevenueDistributionApiV1LicensingDistributionsPostRequest;

  try {
    const data = await api.createRevenueDistributionApiV1LicensingDistributionsPost(body);
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
| **revenueDistributionCreate** | [RevenueDistributionCreate](RevenueDistributionCreate.md) |  | |

### Return type

[**RevenueDistributionResponse**](RevenueDistributionResponse.md)

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


## createRevenueDistributionApiV1LicensingDistributionsPost_0

> RevenueDistributionResponse createRevenueDistributionApiV1LicensingDistributionsPost_0(revenueDistributionCreate)

Create Revenue Distribution

Create revenue distribution for a period.  **Admin only** - Calculates and creates revenue distribution based on content access during the specified period. Implements 70/30 split.

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { CreateRevenueDistributionApiV1LicensingDistributionsPost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // RevenueDistributionCreate
    revenueDistributionCreate: ...,
  } satisfies CreateRevenueDistributionApiV1LicensingDistributionsPost0Request;

  try {
    const data = await api.createRevenueDistributionApiV1LicensingDistributionsPost_0(body);
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
| **revenueDistributionCreate** | [RevenueDistributionCreate](RevenueDistributionCreate.md) |  | |

### Return type

[**RevenueDistributionResponse**](RevenueDistributionResponse.md)

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


## getAgreementApiV1LicensingAgreementsAgreementIdGet

> LicensingAgreementResponse getAgreementApiV1LicensingAgreementsAgreementIdGet(agreementId)

Get Agreement

Get details of a specific licensing agreement.  **Admin only**

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { GetAgreementApiV1LicensingAgreementsAgreementIdGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // string
    agreementId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
  } satisfies GetAgreementApiV1LicensingAgreementsAgreementIdGetRequest;

  try {
    const data = await api.getAgreementApiV1LicensingAgreementsAgreementIdGet(body);
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
| **agreementId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**LicensingAgreementResponse**](LicensingAgreementResponse.md)

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


## getAgreementApiV1LicensingAgreementsAgreementIdGet_0

> LicensingAgreementResponse getAgreementApiV1LicensingAgreementsAgreementIdGet_0(agreementId)

Get Agreement

Get details of a specific licensing agreement.  **Admin only**

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { GetAgreementApiV1LicensingAgreementsAgreementIdGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // string
    agreementId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
  } satisfies GetAgreementApiV1LicensingAgreementsAgreementIdGet0Request;

  try {
    const data = await api.getAgreementApiV1LicensingAgreementsAgreementIdGet_0(body);
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
| **agreementId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**LicensingAgreementResponse**](LicensingAgreementResponse.md)

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


## getDistributionApiV1LicensingDistributionsDistributionIdGet

> RevenueDistributionResponse getDistributionApiV1LicensingDistributionsDistributionIdGet(distributionId)

Get Distribution

Get details of a revenue distribution.  **Admin only** - Includes breakdown of member revenues.

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { GetDistributionApiV1LicensingDistributionsDistributionIdGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // string
    distributionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
  } satisfies GetDistributionApiV1LicensingDistributionsDistributionIdGetRequest;

  try {
    const data = await api.getDistributionApiV1LicensingDistributionsDistributionIdGet(body);
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
| **distributionId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**RevenueDistributionResponse**](RevenueDistributionResponse.md)

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


## getDistributionApiV1LicensingDistributionsDistributionIdGet_0

> RevenueDistributionResponse getDistributionApiV1LicensingDistributionsDistributionIdGet_0(distributionId)

Get Distribution

Get details of a revenue distribution.  **Admin only** - Includes breakdown of member revenues.

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { GetDistributionApiV1LicensingDistributionsDistributionIdGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // string
    distributionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
  } satisfies GetDistributionApiV1LicensingDistributionsDistributionIdGet0Request;

  try {
    const data = await api.getDistributionApiV1LicensingDistributionsDistributionIdGet_0(body);
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
| **distributionId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**RevenueDistributionResponse**](RevenueDistributionResponse.md)

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


## listAgreementsApiV1LicensingAgreementsGet

> Array&lt;LicensingAgreementResponse&gt; listAgreementsApiV1LicensingAgreementsGet(status, limit, offset)

List Agreements

List all licensing agreements.  **Admin only** - Returns all agreements with optional filtering.

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { ListAgreementsApiV1LicensingAgreementsGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // AgreementStatus | Filter by status (optional)
    status: ...,
    // number | Results per page (optional)
    limit: 56,
    // number | Pagination offset (optional)
    offset: 56,
  } satisfies ListAgreementsApiV1LicensingAgreementsGetRequest;

  try {
    const data = await api.listAgreementsApiV1LicensingAgreementsGet(body);
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
| **status** | `AgreementStatus` | Filter by status | [Optional] [Defaults to `undefined`] [Enum: active, suspended, terminated, expired] |
| **limit** | `number` | Results per page | [Optional] [Defaults to `100`] |
| **offset** | `number` | Pagination offset | [Optional] [Defaults to `0`] |

### Return type

[**Array&lt;LicensingAgreementResponse&gt;**](LicensingAgreementResponse.md)

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


## listAgreementsApiV1LicensingAgreementsGet_0

> Array&lt;LicensingAgreementResponse&gt; listAgreementsApiV1LicensingAgreementsGet_0(status, limit, offset)

List Agreements

List all licensing agreements.  **Admin only** - Returns all agreements with optional filtering.

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { ListAgreementsApiV1LicensingAgreementsGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // AgreementStatus | Filter by status (optional)
    status: ...,
    // number | Results per page (optional)
    limit: 56,
    // number | Pagination offset (optional)
    offset: 56,
  } satisfies ListAgreementsApiV1LicensingAgreementsGet0Request;

  try {
    const data = await api.listAgreementsApiV1LicensingAgreementsGet_0(body);
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
| **status** | `AgreementStatus` | Filter by status | [Optional] [Defaults to `undefined`] [Enum: active, suspended, terminated, expired] |
| **limit** | `number` | Results per page | [Optional] [Defaults to `100`] |
| **offset** | `number` | Pagination offset | [Optional] [Defaults to `0`] |

### Return type

[**Array&lt;LicensingAgreementResponse&gt;**](LicensingAgreementResponse.md)

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


## listAvailableContentApiV1LicensingContentGet

> ContentListResponse listAvailableContentApiV1LicensingContentGet(contentType, minWordCount, limit, offset)

List Available Content

List available content for licensed AI company.  **Requires AI company API key** - Returns content metadata that matches the terms of active licensing agreements.  Headers:     Authorization: Bearer lic_abc123...

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { ListAvailableContentApiV1LicensingContentGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new LicensingApi(config);

  const body = {
    // string | Filter by content type (optional)
    contentType: contentType_example,
    // number | Minimum word count (optional)
    minWordCount: 56,
    // number | Results per page (optional)
    limit: 56,
    // number | Pagination offset (optional)
    offset: 56,
  } satisfies ListAvailableContentApiV1LicensingContentGetRequest;

  try {
    const data = await api.listAvailableContentApiV1LicensingContentGet(body);
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
| **contentType** | `string` | Filter by content type | [Optional] [Defaults to `undefined`] |
| **minWordCount** | `number` | Minimum word count | [Optional] [Defaults to `undefined`] |
| **limit** | `number` | Results per page | [Optional] [Defaults to `100`] |
| **offset** | `number` | Pagination offset | [Optional] [Defaults to `0`] |

### Return type

[**ContentListResponse**](ContentListResponse.md)

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


## listAvailableContentApiV1LicensingContentGet_0

> ContentListResponse listAvailableContentApiV1LicensingContentGet_0(contentType, minWordCount, limit, offset)

List Available Content

List available content for licensed AI company.  **Requires AI company API key** - Returns content metadata that matches the terms of active licensing agreements.  Headers:     Authorization: Bearer lic_abc123...

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { ListAvailableContentApiV1LicensingContentGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new LicensingApi(config);

  const body = {
    // string | Filter by content type (optional)
    contentType: contentType_example,
    // number | Minimum word count (optional)
    minWordCount: 56,
    // number | Results per page (optional)
    limit: 56,
    // number | Pagination offset (optional)
    offset: 56,
  } satisfies ListAvailableContentApiV1LicensingContentGet0Request;

  try {
    const data = await api.listAvailableContentApiV1LicensingContentGet_0(body);
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
| **contentType** | `string` | Filter by content type | [Optional] [Defaults to `undefined`] |
| **minWordCount** | `number` | Minimum word count | [Optional] [Defaults to `undefined`] |
| **limit** | `number` | Results per page | [Optional] [Defaults to `100`] |
| **offset** | `number` | Pagination offset | [Optional] [Defaults to `0`] |

### Return type

[**ContentListResponse**](ContentListResponse.md)

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


## listDistributionsApiV1LicensingDistributionsGet

> Array&lt;RevenueDistributionResponse&gt; listDistributionsApiV1LicensingDistributionsGet(agreementId, status, limit, offset)

List Distributions

List revenue distributions.  **Admin only** - Returns all distributions with optional filtering.

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { ListDistributionsApiV1LicensingDistributionsGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // string | Filter by agreement (optional)
    agreementId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // DistributionStatus | Filter by status (optional)
    status: ...,
    // number | Results per page (optional)
    limit: 56,
    // number | Pagination offset (optional)
    offset: 56,
  } satisfies ListDistributionsApiV1LicensingDistributionsGetRequest;

  try {
    const data = await api.listDistributionsApiV1LicensingDistributionsGet(body);
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
| **agreementId** | `string` | Filter by agreement | [Optional] [Defaults to `undefined`] |
| **status** | `DistributionStatus` | Filter by status | [Optional] [Defaults to `undefined`] [Enum: pending, processing, completed, failed] |
| **limit** | `number` | Results per page | [Optional] [Defaults to `100`] |
| **offset** | `number` | Pagination offset | [Optional] [Defaults to `0`] |

### Return type

[**Array&lt;RevenueDistributionResponse&gt;**](RevenueDistributionResponse.md)

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


## listDistributionsApiV1LicensingDistributionsGet_0

> Array&lt;RevenueDistributionResponse&gt; listDistributionsApiV1LicensingDistributionsGet_0(agreementId, status, limit, offset)

List Distributions

List revenue distributions.  **Admin only** - Returns all distributions with optional filtering.

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { ListDistributionsApiV1LicensingDistributionsGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // string | Filter by agreement (optional)
    agreementId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // DistributionStatus | Filter by status (optional)
    status: ...,
    // number | Results per page (optional)
    limit: 56,
    // number | Pagination offset (optional)
    offset: 56,
  } satisfies ListDistributionsApiV1LicensingDistributionsGet0Request;

  try {
    const data = await api.listDistributionsApiV1LicensingDistributionsGet_0(body);
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
| **agreementId** | `string` | Filter by agreement | [Optional] [Defaults to `undefined`] |
| **status** | `DistributionStatus` | Filter by status | [Optional] [Defaults to `undefined`] [Enum: pending, processing, completed, failed] |
| **limit** | `number` | Results per page | [Optional] [Defaults to `100`] |
| **offset** | `number` | Pagination offset | [Optional] [Defaults to `0`] |

### Return type

[**Array&lt;RevenueDistributionResponse&gt;**](RevenueDistributionResponse.md)

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


## processPayoutsApiV1LicensingPayoutsPost

> PayoutResponse processPayoutsApiV1LicensingPayoutsPost(payoutCreate)

Process Payouts

Process payouts for a revenue distribution.  **Admin only** - Initiates payment processing for all members in a distribution.  Note: This is currently a simulation. In production, this would integrate with Stripe or other payment processors.

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { ProcessPayoutsApiV1LicensingPayoutsPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // PayoutCreate
    payoutCreate: ...,
  } satisfies ProcessPayoutsApiV1LicensingPayoutsPostRequest;

  try {
    const data = await api.processPayoutsApiV1LicensingPayoutsPost(body);
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
| **payoutCreate** | [PayoutCreate](PayoutCreate.md) |  | |

### Return type

[**PayoutResponse**](PayoutResponse.md)

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


## processPayoutsApiV1LicensingPayoutsPost_0

> PayoutResponse processPayoutsApiV1LicensingPayoutsPost_0(payoutCreate)

Process Payouts

Process payouts for a revenue distribution.  **Admin only** - Initiates payment processing for all members in a distribution.  Note: This is currently a simulation. In production, this would integrate with Stripe or other payment processors.

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { ProcessPayoutsApiV1LicensingPayoutsPost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // PayoutCreate
    payoutCreate: ...,
  } satisfies ProcessPayoutsApiV1LicensingPayoutsPost0Request;

  try {
    const data = await api.processPayoutsApiV1LicensingPayoutsPost_0(body);
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
| **payoutCreate** | [PayoutCreate](PayoutCreate.md) |  | |

### Return type

[**PayoutResponse**](PayoutResponse.md)

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


## terminateAgreementApiV1LicensingAgreementsAgreementIdDelete

> SuccessResponse terminateAgreementApiV1LicensingAgreementsAgreementIdDelete(agreementId)

Terminate Agreement

Terminate a licensing agreement.  **Admin only** - Sets agreement status to terminated.

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { TerminateAgreementApiV1LicensingAgreementsAgreementIdDeleteRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // string
    agreementId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
  } satisfies TerminateAgreementApiV1LicensingAgreementsAgreementIdDeleteRequest;

  try {
    const data = await api.terminateAgreementApiV1LicensingAgreementsAgreementIdDelete(body);
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
| **agreementId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**SuccessResponse**](SuccessResponse.md)

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


## terminateAgreementApiV1LicensingAgreementsAgreementIdDelete_0

> SuccessResponse terminateAgreementApiV1LicensingAgreementsAgreementIdDelete_0(agreementId)

Terminate Agreement

Terminate a licensing agreement.  **Admin only** - Sets agreement status to terminated.

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // string
    agreementId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
  } satisfies TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete0Request;

  try {
    const data = await api.terminateAgreementApiV1LicensingAgreementsAgreementIdDelete_0(body);
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
| **agreementId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**SuccessResponse**](SuccessResponse.md)

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


## trackContentAccessApiV1LicensingTrackAccessPost

> ContentAccessLogResponse trackContentAccessApiV1LicensingTrackAccessPost(contentAccessTrack)

Track Content Access

Track content access by AI company.  **Requires AI company API key** - Logs when content is accessed for revenue attribution.  Headers:     Authorization: Bearer lic_abc123...

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { TrackContentAccessApiV1LicensingTrackAccessPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new LicensingApi(config);

  const body = {
    // ContentAccessTrack
    contentAccessTrack: ...,
  } satisfies TrackContentAccessApiV1LicensingTrackAccessPostRequest;

  try {
    const data = await api.trackContentAccessApiV1LicensingTrackAccessPost(body);
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
| **contentAccessTrack** | [ContentAccessTrack](ContentAccessTrack.md) |  | |

### Return type

[**ContentAccessLogResponse**](ContentAccessLogResponse.md)

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


## trackContentAccessApiV1LicensingTrackAccessPost_0

> ContentAccessLogResponse trackContentAccessApiV1LicensingTrackAccessPost_0(contentAccessTrack)

Track Content Access

Track content access by AI company.  **Requires AI company API key** - Logs when content is accessed for revenue attribution.  Headers:     Authorization: Bearer lic_abc123...

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { TrackContentAccessApiV1LicensingTrackAccessPost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new LicensingApi(config);

  const body = {
    // ContentAccessTrack
    contentAccessTrack: ...,
  } satisfies TrackContentAccessApiV1LicensingTrackAccessPost0Request;

  try {
    const data = await api.trackContentAccessApiV1LicensingTrackAccessPost_0(body);
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
| **contentAccessTrack** | [ContentAccessTrack](ContentAccessTrack.md) |  | |

### Return type

[**ContentAccessLogResponse**](ContentAccessLogResponse.md)

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


## updateAgreementApiV1LicensingAgreementsAgreementIdPatch

> LicensingAgreementResponse updateAgreementApiV1LicensingAgreementsAgreementIdPatch(agreementId, licensingAgreementUpdate)

Update Agreement

Update a licensing agreement.  **Admin only** - Allows updating agreement terms and status.

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { UpdateAgreementApiV1LicensingAgreementsAgreementIdPatchRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // string
    agreementId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // LicensingAgreementUpdate
    licensingAgreementUpdate: ...,
  } satisfies UpdateAgreementApiV1LicensingAgreementsAgreementIdPatchRequest;

  try {
    const data = await api.updateAgreementApiV1LicensingAgreementsAgreementIdPatch(body);
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
| **agreementId** | `string` |  | [Defaults to `undefined`] |
| **licensingAgreementUpdate** | [LicensingAgreementUpdate](LicensingAgreementUpdate.md) |  | |

### Return type

[**LicensingAgreementResponse**](LicensingAgreementResponse.md)

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


## updateAgreementApiV1LicensingAgreementsAgreementIdPatch_0

> LicensingAgreementResponse updateAgreementApiV1LicensingAgreementsAgreementIdPatch_0(agreementId, licensingAgreementUpdate)

Update Agreement

Update a licensing agreement.  **Admin only** - Allows updating agreement terms and status.

### Example

```ts
import {
  Configuration,
  LicensingApi,
} from '@encypher/sdk';
import type { UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new LicensingApi();

  const body = {
    // string
    agreementId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // LicensingAgreementUpdate
    licensingAgreementUpdate: ...,
  } satisfies UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch0Request;

  try {
    const data = await api.updateAgreementApiV1LicensingAgreementsAgreementIdPatch_0(body);
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
| **agreementId** | `string` |  | [Defaults to `undefined`] |
| **licensingAgreementUpdate** | [LicensingAgreementUpdate](LicensingAgreementUpdate.md) |  | |

### Return type

[**LicensingAgreementResponse**](LicensingAgreementResponse.md)

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

