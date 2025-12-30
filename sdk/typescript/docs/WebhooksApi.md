# WebhooksApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createWebhookApiV1WebhooksPost**](WebhooksApi.md#createwebhookapiv1webhookspost) | **POST** /api/v1/webhooks | Create Webhook |
| [**createWebhookApiV1WebhooksPost_0**](WebhooksApi.md#createwebhookapiv1webhookspost_0) | **POST** /api/v1/webhooks | Create Webhook |
| [**deleteWebhookApiV1WebhooksWebhookIdDelete**](WebhooksApi.md#deletewebhookapiv1webhookswebhookiddelete) | **DELETE** /api/v1/webhooks/{webhook_id} | Delete Webhook |
| [**deleteWebhookApiV1WebhooksWebhookIdDelete_0**](WebhooksApi.md#deletewebhookapiv1webhookswebhookiddelete_0) | **DELETE** /api/v1/webhooks/{webhook_id} | Delete Webhook |
| [**getWebhookApiV1WebhooksWebhookIdGet**](WebhooksApi.md#getwebhookapiv1webhookswebhookidget) | **GET** /api/v1/webhooks/{webhook_id} | Get Webhook |
| [**getWebhookApiV1WebhooksWebhookIdGet_0**](WebhooksApi.md#getwebhookapiv1webhookswebhookidget_0) | **GET** /api/v1/webhooks/{webhook_id} | Get Webhook |
| [**getWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet**](WebhooksApi.md#getwebhookdeliveriesapiv1webhookswebhookiddeliveriesget) | **GET** /api/v1/webhooks/{webhook_id}/deliveries | Get Webhook Deliveries |
| [**getWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet_0**](WebhooksApi.md#getwebhookdeliveriesapiv1webhookswebhookiddeliveriesget_0) | **GET** /api/v1/webhooks/{webhook_id}/deliveries | Get Webhook Deliveries |
| [**listWebhooksApiV1WebhooksGet**](WebhooksApi.md#listwebhooksapiv1webhooksget) | **GET** /api/v1/webhooks | List Webhooks |
| [**listWebhooksApiV1WebhooksGet_0**](WebhooksApi.md#listwebhooksapiv1webhooksget_0) | **GET** /api/v1/webhooks | List Webhooks |
| [**testWebhookApiV1WebhooksWebhookIdTestPost**](WebhooksApi.md#testwebhookapiv1webhookswebhookidtestpost) | **POST** /api/v1/webhooks/{webhook_id}/test | Test Webhook |
| [**testWebhookApiV1WebhooksWebhookIdTestPost_0**](WebhooksApi.md#testwebhookapiv1webhookswebhookidtestpost_0) | **POST** /api/v1/webhooks/{webhook_id}/test | Test Webhook |
| [**updateWebhookApiV1WebhooksWebhookIdPatch**](WebhooksApi.md#updatewebhookapiv1webhookswebhookidpatch) | **PATCH** /api/v1/webhooks/{webhook_id} | Update Webhook |
| [**updateWebhookApiV1WebhooksWebhookIdPatch_0**](WebhooksApi.md#updatewebhookapiv1webhookswebhookidpatch_0) | **PATCH** /api/v1/webhooks/{webhook_id} | Update Webhook |



## createWebhookApiV1WebhooksPost

> WebhookCreateResponse createWebhookApiV1WebhooksPost(webhookCreateRequest)

Create Webhook

Register a new webhook.  The webhook URL must be HTTPS. You can optionally provide a shared secret for HMAC signature verification of webhook payloads.

### Example

```ts
import {
  Configuration,
  WebhooksApi,
} from '@encypher/sdk';
import type { CreateWebhookApiV1WebhooksPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WebhooksApi(config);

  const body = {
    // WebhookCreateRequest
    webhookCreateRequest: ...,
  } satisfies CreateWebhookApiV1WebhooksPostRequest;

  try {
    const data = await api.createWebhookApiV1WebhooksPost(body);
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
| **webhookCreateRequest** | [WebhookCreateRequest](WebhookCreateRequest.md) |  | |

### Return type

[**WebhookCreateResponse**](WebhookCreateResponse.md)

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


## createWebhookApiV1WebhooksPost_0

> WebhookCreateResponse createWebhookApiV1WebhooksPost_0(webhookCreateRequest)

Create Webhook

Register a new webhook.  The webhook URL must be HTTPS. You can optionally provide a shared secret for HMAC signature verification of webhook payloads.

### Example

```ts
import {
  Configuration,
  WebhooksApi,
} from '@encypher/sdk';
import type { CreateWebhookApiV1WebhooksPost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WebhooksApi(config);

  const body = {
    // WebhookCreateRequest
    webhookCreateRequest: ...,
  } satisfies CreateWebhookApiV1WebhooksPost0Request;

  try {
    const data = await api.createWebhookApiV1WebhooksPost_0(body);
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
| **webhookCreateRequest** | [WebhookCreateRequest](WebhookCreateRequest.md) |  | |

### Return type

[**WebhookCreateResponse**](WebhookCreateResponse.md)

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


## deleteWebhookApiV1WebhooksWebhookIdDelete

> WebhookDeleteResponse deleteWebhookApiV1WebhooksWebhookIdDelete(webhookId)

Delete Webhook

Delete a webhook.

### Example

```ts
import {
  Configuration,
  WebhooksApi,
} from '@encypher/sdk';
import type { DeleteWebhookApiV1WebhooksWebhookIdDeleteRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WebhooksApi(config);

  const body = {
    // string
    webhookId: webhookId_example,
  } satisfies DeleteWebhookApiV1WebhooksWebhookIdDeleteRequest;

  try {
    const data = await api.deleteWebhookApiV1WebhooksWebhookIdDelete(body);
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
| **webhookId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**WebhookDeleteResponse**](WebhookDeleteResponse.md)

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


## deleteWebhookApiV1WebhooksWebhookIdDelete_0

> WebhookDeleteResponse deleteWebhookApiV1WebhooksWebhookIdDelete_0(webhookId)

Delete Webhook

Delete a webhook.

### Example

```ts
import {
  Configuration,
  WebhooksApi,
} from '@encypher/sdk';
import type { DeleteWebhookApiV1WebhooksWebhookIdDelete0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WebhooksApi(config);

  const body = {
    // string
    webhookId: webhookId_example,
  } satisfies DeleteWebhookApiV1WebhooksWebhookIdDelete0Request;

  try {
    const data = await api.deleteWebhookApiV1WebhooksWebhookIdDelete_0(body);
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
| **webhookId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**WebhookDeleteResponse**](WebhookDeleteResponse.md)

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


## getWebhookApiV1WebhooksWebhookIdGet

> WebhookListResponse getWebhookApiV1WebhooksWebhookIdGet(webhookId)

Get Webhook

Get details of a specific webhook.

### Example

```ts
import {
  Configuration,
  WebhooksApi,
} from '@encypher/sdk';
import type { GetWebhookApiV1WebhooksWebhookIdGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WebhooksApi(config);

  const body = {
    // string
    webhookId: webhookId_example,
  } satisfies GetWebhookApiV1WebhooksWebhookIdGetRequest;

  try {
    const data = await api.getWebhookApiV1WebhooksWebhookIdGet(body);
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
| **webhookId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**WebhookListResponse**](WebhookListResponse.md)

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


## getWebhookApiV1WebhooksWebhookIdGet_0

> WebhookListResponse getWebhookApiV1WebhooksWebhookIdGet_0(webhookId)

Get Webhook

Get details of a specific webhook.

### Example

```ts
import {
  Configuration,
  WebhooksApi,
} from '@encypher/sdk';
import type { GetWebhookApiV1WebhooksWebhookIdGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WebhooksApi(config);

  const body = {
    // string
    webhookId: webhookId_example,
  } satisfies GetWebhookApiV1WebhooksWebhookIdGet0Request;

  try {
    const data = await api.getWebhookApiV1WebhooksWebhookIdGet_0(body);
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
| **webhookId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**WebhookListResponse**](WebhookListResponse.md)

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


## getWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet

> WebhookDeliveriesResponse getWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet(webhookId, page, pageSize)

Get Webhook Deliveries

Get delivery history for a webhook.

### Example

```ts
import {
  Configuration,
  WebhooksApi,
} from '@encypher/sdk';
import type { GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WebhooksApi(config);

  const body = {
    // string
    webhookId: webhookId_example,
    // number (optional)
    page: 56,
    // number (optional)
    pageSize: 56,
  } satisfies GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGetRequest;

  try {
    const data = await api.getWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet(body);
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
| **webhookId** | `string` |  | [Defaults to `undefined`] |
| **page** | `number` |  | [Optional] [Defaults to `1`] |
| **pageSize** | `number` |  | [Optional] [Defaults to `50`] |

### Return type

[**WebhookDeliveriesResponse**](WebhookDeliveriesResponse.md)

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


## getWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet_0

> WebhookDeliveriesResponse getWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet_0(webhookId, page, pageSize)

Get Webhook Deliveries

Get delivery history for a webhook.

### Example

```ts
import {
  Configuration,
  WebhooksApi,
} from '@encypher/sdk';
import type { GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WebhooksApi(config);

  const body = {
    // string
    webhookId: webhookId_example,
    // number (optional)
    page: 56,
    // number (optional)
    pageSize: 56,
  } satisfies GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet0Request;

  try {
    const data = await api.getWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet_0(body);
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
| **webhookId** | `string` |  | [Defaults to `undefined`] |
| **page** | `number` |  | [Optional] [Defaults to `1`] |
| **pageSize** | `number` |  | [Optional] [Defaults to `50`] |

### Return type

[**WebhookDeliveriesResponse**](WebhookDeliveriesResponse.md)

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


## listWebhooksApiV1WebhooksGet

> WebhookListResponse listWebhooksApiV1WebhooksGet()

List Webhooks

List all webhooks for the organization.

### Example

```ts
import {
  Configuration,
  WebhooksApi,
} from '@encypher/sdk';
import type { ListWebhooksApiV1WebhooksGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WebhooksApi(config);

  try {
    const data = await api.listWebhooksApiV1WebhooksGet();
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

[**WebhookListResponse**](WebhookListResponse.md)

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


## listWebhooksApiV1WebhooksGet_0

> WebhookListResponse listWebhooksApiV1WebhooksGet_0()

List Webhooks

List all webhooks for the organization.

### Example

```ts
import {
  Configuration,
  WebhooksApi,
} from '@encypher/sdk';
import type { ListWebhooksApiV1WebhooksGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WebhooksApi(config);

  try {
    const data = await api.listWebhooksApiV1WebhooksGet_0();
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

[**WebhookListResponse**](WebhookListResponse.md)

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


## testWebhookApiV1WebhooksWebhookIdTestPost

> WebhookTestResponse testWebhookApiV1WebhooksWebhookIdTestPost(webhookId)

Test Webhook

Send a test event to the webhook.  This sends a test payload to verify the webhook is configured correctly.

### Example

```ts
import {
  Configuration,
  WebhooksApi,
} from '@encypher/sdk';
import type { TestWebhookApiV1WebhooksWebhookIdTestPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WebhooksApi(config);

  const body = {
    // string
    webhookId: webhookId_example,
  } satisfies TestWebhookApiV1WebhooksWebhookIdTestPostRequest;

  try {
    const data = await api.testWebhookApiV1WebhooksWebhookIdTestPost(body);
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
| **webhookId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**WebhookTestResponse**](WebhookTestResponse.md)

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


## testWebhookApiV1WebhooksWebhookIdTestPost_0

> WebhookTestResponse testWebhookApiV1WebhooksWebhookIdTestPost_0(webhookId)

Test Webhook

Send a test event to the webhook.  This sends a test payload to verify the webhook is configured correctly.

### Example

```ts
import {
  Configuration,
  WebhooksApi,
} from '@encypher/sdk';
import type { TestWebhookApiV1WebhooksWebhookIdTestPost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WebhooksApi(config);

  const body = {
    // string
    webhookId: webhookId_example,
  } satisfies TestWebhookApiV1WebhooksWebhookIdTestPost0Request;

  try {
    const data = await api.testWebhookApiV1WebhooksWebhookIdTestPost_0(body);
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
| **webhookId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**WebhookTestResponse**](WebhookTestResponse.md)

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


## updateWebhookApiV1WebhooksWebhookIdPatch

> WebhookUpdateResponse updateWebhookApiV1WebhooksWebhookIdPatch(webhookId, webhookUpdateRequest)

Update Webhook

Update a webhook\&#39;s URL, events, or active status.

### Example

```ts
import {
  Configuration,
  WebhooksApi,
} from '@encypher/sdk';
import type { UpdateWebhookApiV1WebhooksWebhookIdPatchRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WebhooksApi(config);

  const body = {
    // string
    webhookId: webhookId_example,
    // WebhookUpdateRequest
    webhookUpdateRequest: ...,
  } satisfies UpdateWebhookApiV1WebhooksWebhookIdPatchRequest;

  try {
    const data = await api.updateWebhookApiV1WebhooksWebhookIdPatch(body);
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
| **webhookId** | `string` |  | [Defaults to `undefined`] |
| **webhookUpdateRequest** | [WebhookUpdateRequest](WebhookUpdateRequest.md) |  | |

### Return type

[**WebhookUpdateResponse**](WebhookUpdateResponse.md)

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


## updateWebhookApiV1WebhooksWebhookIdPatch_0

> WebhookUpdateResponse updateWebhookApiV1WebhooksWebhookIdPatch_0(webhookId, webhookUpdateRequest)

Update Webhook

Update a webhook\&#39;s URL, events, or active status.

### Example

```ts
import {
  Configuration,
  WebhooksApi,
} from '@encypher/sdk';
import type { UpdateWebhookApiV1WebhooksWebhookIdPatch0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new WebhooksApi(config);

  const body = {
    // string
    webhookId: webhookId_example,
    // WebhookUpdateRequest
    webhookUpdateRequest: ...,
  } satisfies UpdateWebhookApiV1WebhooksWebhookIdPatch0Request;

  try {
    const data = await api.updateWebhookApiV1WebhooksWebhookIdPatch_0(body);
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
| **webhookId** | `string` |  | [Defaults to `undefined`] |
| **webhookUpdateRequest** | [WebhookUpdateRequest](WebhookUpdateRequest.md) |  | |

### Return type

[**WebhookUpdateResponse**](WebhookUpdateResponse.md)

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

