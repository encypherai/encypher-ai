# AuditApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**exportAuditLogsApiV1AuditLogsExportGet**](AuditApi.md#exportauditlogsapiv1auditlogsexportget) | **GET** /api/v1/audit-logs/export | Export Audit Logs |
| [**getAuditLogsApiV1AuditLogsGet**](AuditApi.md#getauditlogsapiv1auditlogsget) | **GET** /api/v1/audit-logs | Get Audit Logs |



## exportAuditLogsApiV1AuditLogsExportGet

> any exportAuditLogsApiV1AuditLogsExportGet(format, startDate, endDate)

Export Audit Logs

Export audit logs in JSON or CSV format.  Returns all logs within the specified date range. Default is last 30 days if no dates specified.

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@encypher/sdk';
import type { ExportAuditLogsApiV1AuditLogsExportGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AuditApi(config);

  const body = {
    // string (optional)
    format: format_example,
    // string (optional)
    startDate: startDate_example,
    // string (optional)
    endDate: endDate_example,
  } satisfies ExportAuditLogsApiV1AuditLogsExportGetRequest;

  try {
    const data = await api.exportAuditLogsApiV1AuditLogsExportGet(body);
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
| **format** | `string` |  | [Optional] [Defaults to `&#39;json&#39;`] |
| **startDate** | `string` |  | [Optional] [Defaults to `undefined`] |
| **endDate** | `string` |  | [Optional] [Defaults to `undefined`] |

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


## getAuditLogsApiV1AuditLogsGet

> AuditLogResponse getAuditLogsApiV1AuditLogsGet(page, pageSize, action, actorId, resourceType, startDate, endDate)

Get Audit Logs

Get audit logs for the organization.  Supports filtering by: - action: Type of action (e.g., \&quot;document.signed\&quot;) - actor_id: ID of the user or API key that performed the action - resource_type: Type of resource affected - start_date/end_date: Date range  Results are paginated and sorted by timestamp (newest first).

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@encypher/sdk';
import type { GetAuditLogsApiV1AuditLogsGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AuditApi(config);

  const body = {
    // number (optional)
    page: 56,
    // number (optional)
    pageSize: 56,
    // string | Filter by action type (optional)
    action: action_example,
    // string | Filter by actor ID (optional)
    actorId: actorId_example,
    // string | Filter by resource type (optional)
    resourceType: resourceType_example,
    // string | Start date (ISO format) (optional)
    startDate: startDate_example,
    // string | End date (ISO format) (optional)
    endDate: endDate_example,
  } satisfies GetAuditLogsApiV1AuditLogsGetRequest;

  try {
    const data = await api.getAuditLogsApiV1AuditLogsGet(body);
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
| **page** | `number` |  | [Optional] [Defaults to `1`] |
| **pageSize** | `number` |  | [Optional] [Defaults to `50`] |
| **action** | `string` | Filter by action type | [Optional] [Defaults to `undefined`] |
| **actorId** | `string` | Filter by actor ID | [Optional] [Defaults to `undefined`] |
| **resourceType** | `string` | Filter by resource type | [Optional] [Defaults to `undefined`] |
| **startDate** | `string` | Start date (ISO format) | [Optional] [Defaults to `undefined`] |
| **endDate** | `string` | End date (ISO format) | [Optional] [Defaults to `undefined`] |

### Return type

[**AuditLogResponse**](AuditLogResponse.md)

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

