# \AuditApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**export_audit_logs_api_v1_audit_logs_export_get**](AuditApi.md#export_audit_logs_api_v1_audit_logs_export_get) | **GET** /api/v1/audit-logs/export | Export Audit Logs
[**get_audit_logs_api_v1_audit_logs_get**](AuditApi.md#get_audit_logs_api_v1_audit_logs_get) | **GET** /api/v1/audit-logs | Get Audit Logs



## export_audit_logs_api_v1_audit_logs_export_get

> serde_json::Value export_audit_logs_api_v1_audit_logs_export_get(format, start_date, end_date)
Export Audit Logs

Export audit logs in JSON or CSV format.  Returns all logs within the specified date range. Default is last 30 days if no dates specified.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**format** | Option<**String**> |  |  |[default to json]
**start_date** | Option<**String**> |  |  |
**end_date** | Option<**String**> |  |  |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_audit_logs_api_v1_audit_logs_get

> models::AuditLogResponse get_audit_logs_api_v1_audit_logs_get(page, page_size, action, actor_id, resource_type, start_date, end_date)
Get Audit Logs

Get audit logs for the organization.  Supports filtering by: - action: Type of action (e.g., \"document.signed\") - actor_id: ID of the user or API key that performed the action - resource_type: Type of resource affected - start_date/end_date: Date range  Results are paginated and sorted by timestamp (newest first).

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**page** | Option<**i32**> |  |  |[default to 1]
**page_size** | Option<**i32**> |  |  |[default to 50]
**action** | Option<**String**> | Filter by action type |  |
**actor_id** | Option<**String**> | Filter by actor ID |  |
**resource_type** | Option<**String**> | Filter by resource type |  |
**start_date** | Option<**String**> | Start date (ISO format) |  |
**end_date** | Option<**String**> | End date (ISO format) |  |

### Return type

[**models::AuditLogResponse**](AuditLogResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

