# AccountApi

All URIs are relative to *https://api.encypher.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getAccountInfoApiV1AccountGet**](AccountApi.md#getaccountinfoapiv1accountget) | **GET** /api/v1/account | Get Account Info |
| [**getAccountInfoApiV1AccountGet_0**](AccountApi.md#getaccountinfoapiv1accountget_0) | **GET** /api/v1/account | Get Account Info |
| [**getAccountQuotaApiV1AccountQuotaGet**](AccountApi.md#getaccountquotaapiv1accountquotaget) | **GET** /api/v1/account/quota | Get Account Quota |
| [**getAccountQuotaApiV1AccountQuotaGet_0**](AccountApi.md#getaccountquotaapiv1accountquotaget_0) | **GET** /api/v1/account/quota | Get Account Quota |



## getAccountInfoApiV1AccountGet

> AccountResponse getAccountInfoApiV1AccountGet()

Get Account Info

Get current organization account information.  Returns organization details including: - Organization ID and name - Current subscription tier - Enabled feature flags - Account creation date

### Example

```ts
import {
  Configuration,
  AccountApi,
} from '@encypher/sdk';
import type { GetAccountInfoApiV1AccountGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountApi(config);

  try {
    const data = await api.getAccountInfoApiV1AccountGet();
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

[**AccountResponse**](AccountResponse.md)

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


## getAccountInfoApiV1AccountGet_0

> AccountResponse getAccountInfoApiV1AccountGet_0()

Get Account Info

Get current organization account information.  Returns organization details including: - Organization ID and name - Current subscription tier - Enabled feature flags - Account creation date

### Example

```ts
import {
  Configuration,
  AccountApi,
} from '@encypher/sdk';
import type { GetAccountInfoApiV1AccountGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountApi(config);

  try {
    const data = await api.getAccountInfoApiV1AccountGet_0();
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

[**AccountResponse**](AccountResponse.md)

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


## getAccountQuotaApiV1AccountQuotaGet

> QuotaResponse getAccountQuotaApiV1AccountQuotaGet()

Get Account Quota

Get detailed quota information for the organization.  Returns current usage and limits for: - C2PA signatures - Sentences tracked - Batch operations - API calls

### Example

```ts
import {
  Configuration,
  AccountApi,
} from '@encypher/sdk';
import type { GetAccountQuotaApiV1AccountQuotaGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountApi(config);

  try {
    const data = await api.getAccountQuotaApiV1AccountQuotaGet();
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

[**QuotaResponse**](QuotaResponse.md)

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


## getAccountQuotaApiV1AccountQuotaGet_0

> QuotaResponse getAccountQuotaApiV1AccountQuotaGet_0()

Get Account Quota

Get detailed quota information for the organization.  Returns current usage and limits for: - C2PA signatures - Sentences tracked - Batch operations - API calls

### Example

```ts
import {
  Configuration,
  AccountApi,
} from '@encypher/sdk';
import type { GetAccountQuotaApiV1AccountQuotaGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountApi(config);

  try {
    const data = await api.getAccountQuotaApiV1AccountQuotaGet_0();
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

[**QuotaResponse**](QuotaResponse.md)

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
