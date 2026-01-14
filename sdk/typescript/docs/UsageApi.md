# UsageApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getUsageHistoryApiV1UsageHistoryGet**](UsageApi.md#getusagehistoryapiv1usagehistoryget) | **GET** /api/v1/usage/history | Get Usage History |
| [**getUsageStatsApiV1UsageGet**](UsageApi.md#getusagestatsapiv1usageget) | **GET** /api/v1/usage | Get Usage Stats |



## getUsageHistoryApiV1UsageHistoryGet

> any getUsageHistoryApiV1UsageHistoryGet(months)

Get Usage History

Get historical usage data for the organization.  Returns monthly usage summaries for the specified number of months.

### Example

```ts
import {
  Configuration,
  UsageApi,
} from '@encypher/sdk';
import type { GetUsageHistoryApiV1UsageHistoryGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new UsageApi(config);

  const body = {
    // number (optional)
    months: 56,
  } satisfies GetUsageHistoryApiV1UsageHistoryGetRequest;

  try {
    const data = await api.getUsageHistoryApiV1UsageHistoryGet(body);
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
| **months** | `number` |  | [Optional] [Defaults to `6`] |

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
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getUsageStatsApiV1UsageGet

> UsageResponse getUsageStatsApiV1UsageGet()

Get Usage Stats

Get current period usage statistics for the organization.  Returns usage metrics including: - C2PA signatures (documents signed) - Sentences tracked - Batch operations - API calls

### Example

```ts
import {
  Configuration,
  UsageApi,
} from '@encypher/sdk';
import type { GetUsageStatsApiV1UsageGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new UsageApi(config);

  try {
    const data = await api.getUsageStatsApiV1UsageGet();
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

[**UsageResponse**](UsageResponse.md)

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

