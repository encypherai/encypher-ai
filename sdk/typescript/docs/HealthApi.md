# HealthApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**healthCheckHealthGet**](HealthApi.md#healthcheckhealthget) | **GET** /health | Health Check |
| [**readinessCheckReadyzGet**](HealthApi.md#readinesscheckreadyzget) | **GET** /readyz | Readiness Check |



## healthCheckHealthGet

> any healthCheckHealthGet()

Health Check

Health check endpoint for monitoring.  Returns:     dict: Status and environment information

### Example

```ts
import {
  Configuration,
  HealthApi,
} from '@encypher/sdk';
import type { HealthCheckHealthGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new HealthApi();

  try {
    const data = await api.healthCheckHealthGet();
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


## readinessCheckReadyzGet

> any readinessCheckReadyzGet()

Readiness Check

Lightweight readiness probe.

### Example

```ts
import {
  Configuration,
  HealthApi,
} from '@encypher/sdk';
import type { ReadinessCheckReadyzGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new HealthApi();

  try {
    const data = await api.readinessCheckReadyzGet();
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

