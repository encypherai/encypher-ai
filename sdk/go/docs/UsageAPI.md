# \UsageAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GetUsageHistoryApiV1UsageHistoryGet**](UsageAPI.md#GetUsageHistoryApiV1UsageHistoryGet) | **Get** /api/v1/usage/history | Get Usage History
[**GetUsageStatsApiV1UsageGet**](UsageAPI.md#GetUsageStatsApiV1UsageGet) | **Get** /api/v1/usage | Get Usage Stats



## GetUsageHistoryApiV1UsageHistoryGet

> interface{} GetUsageHistoryApiV1UsageHistoryGet(ctx).Months(months).Execute()

Get Usage History



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/encypherai/encypherai-commercial/sdk/go"
)

func main() {
	months := int32(56) // int32 |  (optional) (default to 6)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.UsageAPI.GetUsageHistoryApiV1UsageHistoryGet(context.Background()).Months(months).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `UsageAPI.GetUsageHistoryApiV1UsageHistoryGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetUsageHistoryApiV1UsageHistoryGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `UsageAPI.GetUsageHistoryApiV1UsageHistoryGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetUsageHistoryApiV1UsageHistoryGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **months** | **int32** |  | [default to 6]

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


## GetUsageStatsApiV1UsageGet

> UsageResponse GetUsageStatsApiV1UsageGet(ctx).Execute()

Get Usage Stats



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/encypherai/encypherai-commercial/sdk/go"
)

func main() {

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.UsageAPI.GetUsageStatsApiV1UsageGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `UsageAPI.GetUsageStatsApiV1UsageGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetUsageStatsApiV1UsageGet`: UsageResponse
	fmt.Fprintf(os.Stdout, "Response from `UsageAPI.GetUsageStatsApiV1UsageGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetUsageStatsApiV1UsageGetRequest struct via the builder pattern


### Return type

[**UsageResponse**](UsageResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

