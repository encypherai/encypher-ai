# \DocumentsAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**DeleteDocumentApiV1DocumentsDocumentIdDelete**](DocumentsAPI.md#DeleteDocumentApiV1DocumentsDocumentIdDelete) | **Delete** /api/v1/documents/{document_id} | Delete Document
[**DeleteDocumentApiV1DocumentsDocumentIdDelete_0**](DocumentsAPI.md#DeleteDocumentApiV1DocumentsDocumentIdDelete_0) | **Delete** /api/v1/documents/{document_id} | Delete Document
[**GetDocumentApiV1DocumentsDocumentIdGet**](DocumentsAPI.md#GetDocumentApiV1DocumentsDocumentIdGet) | **Get** /api/v1/documents/{document_id} | Get Document
[**GetDocumentApiV1DocumentsDocumentIdGet_0**](DocumentsAPI.md#GetDocumentApiV1DocumentsDocumentIdGet_0) | **Get** /api/v1/documents/{document_id} | Get Document
[**GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet**](DocumentsAPI.md#GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet) | **Get** /api/v1/documents/{document_id}/history | Get Document History
[**GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet_0**](DocumentsAPI.md#GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet_0) | **Get** /api/v1/documents/{document_id}/history | Get Document History
[**ListDocumentsApiV1DocumentsGet**](DocumentsAPI.md#ListDocumentsApiV1DocumentsGet) | **Get** /api/v1/documents | List Documents
[**ListDocumentsApiV1DocumentsGet_0**](DocumentsAPI.md#ListDocumentsApiV1DocumentsGet_0) | **Get** /api/v1/documents | List Documents



## DeleteDocumentApiV1DocumentsDocumentIdDelete

> DocumentDeleteResponse DeleteDocumentApiV1DocumentsDocumentIdDelete(ctx, documentId).Revoke(revoke).Reason(reason).Execute()

Delete Document



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
	documentId := "documentId_example" // string | 
	revoke := true // bool | Also revoke the document (optional) (default to true)
	reason := "reason_example" // string | Reason for deletion (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DocumentsAPI.DeleteDocumentApiV1DocumentsDocumentIdDelete(context.Background(), documentId).Revoke(revoke).Reason(reason).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DocumentsAPI.DeleteDocumentApiV1DocumentsDocumentIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteDocumentApiV1DocumentsDocumentIdDelete`: DocumentDeleteResponse
	fmt.Fprintf(os.Stdout, "Response from `DocumentsAPI.DeleteDocumentApiV1DocumentsDocumentIdDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**documentId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteDocumentApiV1DocumentsDocumentIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **revoke** | **bool** | Also revoke the document | [default to true]
 **reason** | **string** | Reason for deletion | 

### Return type

[**DocumentDeleteResponse**](DocumentDeleteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteDocumentApiV1DocumentsDocumentIdDelete_0

> DocumentDeleteResponse DeleteDocumentApiV1DocumentsDocumentIdDelete_0(ctx, documentId).Revoke(revoke).Reason(reason).Execute()

Delete Document



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
	documentId := "documentId_example" // string | 
	revoke := true // bool | Also revoke the document (optional) (default to true)
	reason := "reason_example" // string | Reason for deletion (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DocumentsAPI.DeleteDocumentApiV1DocumentsDocumentIdDelete_0(context.Background(), documentId).Revoke(revoke).Reason(reason).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DocumentsAPI.DeleteDocumentApiV1DocumentsDocumentIdDelete_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteDocumentApiV1DocumentsDocumentIdDelete_0`: DocumentDeleteResponse
	fmt.Fprintf(os.Stdout, "Response from `DocumentsAPI.DeleteDocumentApiV1DocumentsDocumentIdDelete_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**documentId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteDocumentApiV1DocumentsDocumentIdDelete_1Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **revoke** | **bool** | Also revoke the document | [default to true]
 **reason** | **string** | Reason for deletion | 

### Return type

[**DocumentDeleteResponse**](DocumentDeleteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetDocumentApiV1DocumentsDocumentIdGet

> DocumentDetailResponse GetDocumentApiV1DocumentsDocumentIdGet(ctx, documentId).Execute()

Get Document



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
	documentId := "documentId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DocumentsAPI.GetDocumentApiV1DocumentsDocumentIdGet(context.Background(), documentId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DocumentsAPI.GetDocumentApiV1DocumentsDocumentIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetDocumentApiV1DocumentsDocumentIdGet`: DocumentDetailResponse
	fmt.Fprintf(os.Stdout, "Response from `DocumentsAPI.GetDocumentApiV1DocumentsDocumentIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**documentId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetDocumentApiV1DocumentsDocumentIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**DocumentDetailResponse**](DocumentDetailResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetDocumentApiV1DocumentsDocumentIdGet_0

> DocumentDetailResponse GetDocumentApiV1DocumentsDocumentIdGet_0(ctx, documentId).Execute()

Get Document



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
	documentId := "documentId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DocumentsAPI.GetDocumentApiV1DocumentsDocumentIdGet_0(context.Background(), documentId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DocumentsAPI.GetDocumentApiV1DocumentsDocumentIdGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetDocumentApiV1DocumentsDocumentIdGet_0`: DocumentDetailResponse
	fmt.Fprintf(os.Stdout, "Response from `DocumentsAPI.GetDocumentApiV1DocumentsDocumentIdGet_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**documentId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetDocumentApiV1DocumentsDocumentIdGet_2Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**DocumentDetailResponse**](DocumentDetailResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet

> DocumentHistoryResponse GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet(ctx, documentId).Execute()

Get Document History



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
	documentId := "documentId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DocumentsAPI.GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet(context.Background(), documentId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DocumentsAPI.GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet`: DocumentHistoryResponse
	fmt.Fprintf(os.Stdout, "Response from `DocumentsAPI.GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**documentId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetDocumentHistoryApiV1DocumentsDocumentIdHistoryGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**DocumentHistoryResponse**](DocumentHistoryResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet_0

> DocumentHistoryResponse GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet_0(ctx, documentId).Execute()

Get Document History



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
	documentId := "documentId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DocumentsAPI.GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet_0(context.Background(), documentId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DocumentsAPI.GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet_0`: DocumentHistoryResponse
	fmt.Fprintf(os.Stdout, "Response from `DocumentsAPI.GetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**documentId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetDocumentHistoryApiV1DocumentsDocumentIdHistoryGet_3Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**DocumentHistoryResponse**](DocumentHistoryResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListDocumentsApiV1DocumentsGet

> DocumentListResponse ListDocumentsApiV1DocumentsGet(ctx).Page(page).PageSize(pageSize).Search(search).Status(status).FromDate(fromDate).ToDate(toDate).Execute()

List Documents



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
	page := int32(56) // int32 | Page number (optional) (default to 1)
	pageSize := int32(56) // int32 | Items per page (optional) (default to 50)
	search := "search_example" // string | Search in title (optional)
	status := "status_example" // string | Filter by status (active/revoked) (optional)
	fromDate := "fromDate_example" // string | Filter from date (ISO format) (optional)
	toDate := "toDate_example" // string | Filter to date (ISO format) (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DocumentsAPI.ListDocumentsApiV1DocumentsGet(context.Background()).Page(page).PageSize(pageSize).Search(search).Status(status).FromDate(fromDate).ToDate(toDate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DocumentsAPI.ListDocumentsApiV1DocumentsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListDocumentsApiV1DocumentsGet`: DocumentListResponse
	fmt.Fprintf(os.Stdout, "Response from `DocumentsAPI.ListDocumentsApiV1DocumentsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListDocumentsApiV1DocumentsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int32** | Page number | [default to 1]
 **pageSize** | **int32** | Items per page | [default to 50]
 **search** | **string** | Search in title | 
 **status** | **string** | Filter by status (active/revoked) | 
 **fromDate** | **string** | Filter from date (ISO format) | 
 **toDate** | **string** | Filter to date (ISO format) | 

### Return type

[**DocumentListResponse**](DocumentListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListDocumentsApiV1DocumentsGet_0

> DocumentListResponse ListDocumentsApiV1DocumentsGet_0(ctx).Page(page).PageSize(pageSize).Search(search).Status(status).FromDate(fromDate).ToDate(toDate).Execute()

List Documents



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
	page := int32(56) // int32 | Page number (optional) (default to 1)
	pageSize := int32(56) // int32 | Items per page (optional) (default to 50)
	search := "search_example" // string | Search in title (optional)
	status := "status_example" // string | Filter by status (active/revoked) (optional)
	fromDate := "fromDate_example" // string | Filter from date (ISO format) (optional)
	toDate := "toDate_example" // string | Filter to date (ISO format) (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DocumentsAPI.ListDocumentsApiV1DocumentsGet_0(context.Background()).Page(page).PageSize(pageSize).Search(search).Status(status).FromDate(fromDate).ToDate(toDate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DocumentsAPI.ListDocumentsApiV1DocumentsGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListDocumentsApiV1DocumentsGet_0`: DocumentListResponse
	fmt.Fprintf(os.Stdout, "Response from `DocumentsAPI.ListDocumentsApiV1DocumentsGet_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListDocumentsApiV1DocumentsGet_4Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int32** | Page number | [default to 1]
 **pageSize** | **int32** | Items per page | [default to 50]
 **search** | **string** | Search in title | 
 **status** | **string** | Filter by status (active/revoked) | 
 **fromDate** | **string** | Filter from date (ISO format) | 
 **toDate** | **string** | Filter to date (ISO format) | 

### Return type

[**DocumentListResponse**](DocumentListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

