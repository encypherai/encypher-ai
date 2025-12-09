# CoalitionApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getCoalitionDashboardApiV1CoalitionDashboardGet**](CoalitionApi.md#getcoalitiondashboardapiv1coalitiondashboardget) | **GET** /api/v1/coalition/dashboard | Get Coalition Dashboard |
| [**getCoalitionDashboardApiV1CoalitionDashboardGet_0**](CoalitionApi.md#getcoalitiondashboardapiv1coalitiondashboardget_0) | **GET** /api/v1/coalition/dashboard | Get Coalition Dashboard |
| [**getContentStatsApiV1CoalitionContentStatsGet**](CoalitionApi.md#getcontentstatsapiv1coalitioncontentstatsget) | **GET** /api/v1/coalition/content-stats | Get Content Stats |
| [**getContentStatsApiV1CoalitionContentStatsGet_0**](CoalitionApi.md#getcontentstatsapiv1coalitioncontentstatsget_0) | **GET** /api/v1/coalition/content-stats | Get Content Stats |
| [**getEarningsHistoryApiV1CoalitionEarningsGet**](CoalitionApi.md#getearningshistoryapiv1coalitionearningsget) | **GET** /api/v1/coalition/earnings | Get Earnings History |
| [**getEarningsHistoryApiV1CoalitionEarningsGet_0**](CoalitionApi.md#getearningshistoryapiv1coalitionearningsget_0) | **GET** /api/v1/coalition/earnings | Get Earnings History |
| [**optInToCoalitionApiV1CoalitionOptInPost**](CoalitionApi.md#optintocoalitionapiv1coalitionoptinpost) | **POST** /api/v1/coalition/opt-in | Opt In To Coalition |
| [**optInToCoalitionApiV1CoalitionOptInPost_0**](CoalitionApi.md#optintocoalitionapiv1coalitionoptinpost_0) | **POST** /api/v1/coalition/opt-in | Opt In To Coalition |
| [**optOutOfCoalitionApiV1CoalitionOptOutPost**](CoalitionApi.md#optoutofcoalitionapiv1coalitionoptoutpost) | **POST** /api/v1/coalition/opt-out | Opt Out Of Coalition |
| [**optOutOfCoalitionApiV1CoalitionOptOutPost_0**](CoalitionApi.md#optoutofcoalitionapiv1coalitionoptoutpost_0) | **POST** /api/v1/coalition/opt-out | Opt Out Of Coalition |



## getCoalitionDashboardApiV1CoalitionDashboardGet

> CoalitionDashboardResponse getCoalitionDashboardApiV1CoalitionDashboardGet()

Get Coalition Dashboard

Get coalition dashboard data for the organization.  Returns content stats, earnings, and payout information.

### Example

```ts
import {
  Configuration,
  CoalitionApi,
} from '@encypher/sdk';
import type { GetCoalitionDashboardApiV1CoalitionDashboardGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CoalitionApi(config);

  try {
    const data = await api.getCoalitionDashboardApiV1CoalitionDashboardGet();
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

[**CoalitionDashboardResponse**](CoalitionDashboardResponse.md)

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


## getCoalitionDashboardApiV1CoalitionDashboardGet_0

> CoalitionDashboardResponse getCoalitionDashboardApiV1CoalitionDashboardGet_0()

Get Coalition Dashboard

Get coalition dashboard data for the organization.  Returns content stats, earnings, and payout information.

### Example

```ts
import {
  Configuration,
  CoalitionApi,
} from '@encypher/sdk';
import type { GetCoalitionDashboardApiV1CoalitionDashboardGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CoalitionApi(config);

  try {
    const data = await api.getCoalitionDashboardApiV1CoalitionDashboardGet_0();
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

[**CoalitionDashboardResponse**](CoalitionDashboardResponse.md)

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


## getContentStatsApiV1CoalitionContentStatsGet

> any getContentStatsApiV1CoalitionContentStatsGet(months)

Get Content Stats

Get historical content corpus statistics.

### Example

```ts
import {
  Configuration,
  CoalitionApi,
} from '@encypher/sdk';
import type { GetContentStatsApiV1CoalitionContentStatsGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CoalitionApi(config);

  const body = {
    // number (optional)
    months: 56,
  } satisfies GetContentStatsApiV1CoalitionContentStatsGetRequest;

  try {
    const data = await api.getContentStatsApiV1CoalitionContentStatsGet(body);
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
| **months** | `number` |  | [Optional] [Defaults to `12`] |

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


## getContentStatsApiV1CoalitionContentStatsGet_0

> any getContentStatsApiV1CoalitionContentStatsGet_0(months)

Get Content Stats

Get historical content corpus statistics.

### Example

```ts
import {
  Configuration,
  CoalitionApi,
} from '@encypher/sdk';
import type { GetContentStatsApiV1CoalitionContentStatsGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CoalitionApi(config);

  const body = {
    // number (optional)
    months: 56,
  } satisfies GetContentStatsApiV1CoalitionContentStatsGet0Request;

  try {
    const data = await api.getContentStatsApiV1CoalitionContentStatsGet_0(body);
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
| **months** | `number` |  | [Optional] [Defaults to `12`] |

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


## getEarningsHistoryApiV1CoalitionEarningsGet

> any getEarningsHistoryApiV1CoalitionEarningsGet(months)

Get Earnings History

Get detailed earnings history.

### Example

```ts
import {
  Configuration,
  CoalitionApi,
} from '@encypher/sdk';
import type { GetEarningsHistoryApiV1CoalitionEarningsGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CoalitionApi(config);

  const body = {
    // number (optional)
    months: 56,
  } satisfies GetEarningsHistoryApiV1CoalitionEarningsGetRequest;

  try {
    const data = await api.getEarningsHistoryApiV1CoalitionEarningsGet(body);
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
| **months** | `number` |  | [Optional] [Defaults to `12`] |

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


## getEarningsHistoryApiV1CoalitionEarningsGet_0

> any getEarningsHistoryApiV1CoalitionEarningsGet_0(months)

Get Earnings History

Get detailed earnings history.

### Example

```ts
import {
  Configuration,
  CoalitionApi,
} from '@encypher/sdk';
import type { GetEarningsHistoryApiV1CoalitionEarningsGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CoalitionApi(config);

  const body = {
    // number (optional)
    months: 56,
  } satisfies GetEarningsHistoryApiV1CoalitionEarningsGet0Request;

  try {
    const data = await api.getEarningsHistoryApiV1CoalitionEarningsGet_0(body);
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
| **months** | `number` |  | [Optional] [Defaults to `12`] |

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


## optInToCoalitionApiV1CoalitionOptInPost

> any optInToCoalitionApiV1CoalitionOptInPost()

Opt In To Coalition

Opt back into the coalition revenue sharing program.

### Example

```ts
import {
  Configuration,
  CoalitionApi,
} from '@encypher/sdk';
import type { OptInToCoalitionApiV1CoalitionOptInPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CoalitionApi(config);

  try {
    const data = await api.optInToCoalitionApiV1CoalitionOptInPost();
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


## optInToCoalitionApiV1CoalitionOptInPost_0

> any optInToCoalitionApiV1CoalitionOptInPost_0()

Opt In To Coalition

Opt back into the coalition revenue sharing program.

### Example

```ts
import {
  Configuration,
  CoalitionApi,
} from '@encypher/sdk';
import type { OptInToCoalitionApiV1CoalitionOptInPost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CoalitionApi(config);

  try {
    const data = await api.optInToCoalitionApiV1CoalitionOptInPost_0();
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


## optOutOfCoalitionApiV1CoalitionOptOutPost

> any optOutOfCoalitionApiV1CoalitionOptOutPost()

Opt Out Of Coalition

Opt out of the coalition revenue sharing program.  Note: This will stop future earnings but won\&#39;t affect pending payouts.

### Example

```ts
import {
  Configuration,
  CoalitionApi,
} from '@encypher/sdk';
import type { OptOutOfCoalitionApiV1CoalitionOptOutPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CoalitionApi(config);

  try {
    const data = await api.optOutOfCoalitionApiV1CoalitionOptOutPost();
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


## optOutOfCoalitionApiV1CoalitionOptOutPost_0

> any optOutOfCoalitionApiV1CoalitionOptOutPost_0()

Opt Out Of Coalition

Opt out of the coalition revenue sharing program.  Note: This will stop future earnings but won\&#39;t affect pending payouts.

### Example

```ts
import {
  Configuration,
  CoalitionApi,
} from '@encypher/sdk';
import type { OptOutOfCoalitionApiV1CoalitionOptOutPost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CoalitionApi(config);

  try {
    const data = await api.optOutOfCoalitionApiV1CoalitionOptOutPost_0();
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

