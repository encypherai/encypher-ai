# \AuditAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ExportAuditLogsApiV1AuditLogsExportGet**](AuditAPI.md#ExportAuditLogsApiV1AuditLogsExportGet) | **Get** /api/v1/audit-logs/export | Export Audit Logs
[**GetAuditLogsApiV1AuditLogsGet**](AuditAPI.md#GetAuditLogsApiV1AuditLogsGet) | **Get** /api/v1/audit-logs | Get Audit Logs



## ExportAuditLogsApiV1AuditLogsExportGet

> interface{} ExportAuditLogsApiV1AuditLogsExportGet(ctx).Format(format).StartDate(startDate).EndDate(endDate).Execute()

Export Audit Logs



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	format := "format_example" // string |  (optional) (default to "json")
	startDate := "startDate_example" // string |  (optional)
	endDate := "endDate_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuditAPI.ExportAuditLogsApiV1AuditLogsExportGet(context.Background()).Format(format).StartDate(startDate).EndDate(endDate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.ExportAuditLogsApiV1AuditLogsExportGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ExportAuditLogsApiV1AuditLogsExportGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.ExportAuditLogsApiV1AuditLogsExportGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiExportAuditLogsApiV1AuditLogsExportGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **format** | **string** |  | [default to &quot;json&quot;]
 **startDate** | **string** |  | 
 **endDate** | **string** |  | 

### Return type

**interface{}**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAuditLogsApiV1AuditLogsGet

> AuditLogResponse GetAuditLogsApiV1AuditLogsGet(ctx).Page(page).PageSize(pageSize).Action(action).ActorId(actorId).ResourceType(resourceType).StartDate(startDate).EndDate(endDate).Execute()

Get Audit Logs



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	page := int32(56) // int32 |  (optional) (default to 1)
	pageSize := int32(56) // int32 |  (optional) (default to 50)
	action := "action_example" // string | Filter by action type (optional)
	actorId := "actorId_example" // string | Filter by actor ID (optional)
	resourceType := "resourceType_example" // string | Filter by resource type (optional)
	startDate := "startDate_example" // string | Start date (ISO format) (optional)
	endDate := "endDate_example" // string | End date (ISO format) (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuditAPI.GetAuditLogsApiV1AuditLogsGet(context.Background()).Page(page).PageSize(pageSize).Action(action).ActorId(actorId).ResourceType(resourceType).StartDate(startDate).EndDate(endDate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.GetAuditLogsApiV1AuditLogsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAuditLogsApiV1AuditLogsGet`: AuditLogResponse
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.GetAuditLogsApiV1AuditLogsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetAuditLogsApiV1AuditLogsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int32** |  | [default to 1]
 **pageSize** | **int32** |  | [default to 50]
 **action** | **string** | Filter by action type | 
 **actorId** | **string** | Filter by actor ID | 
 **resourceType** | **string** | Filter by resource type | 
 **startDate** | **string** | Start date (ISO format) | 
 **endDate** | **string** | End date (ISO format) | 

### Return type

[**AuditLogResponse**](AuditLogResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

