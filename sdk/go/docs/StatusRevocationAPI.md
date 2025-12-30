# \StatusRevocationAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GetDocumentStatusApiV1StatusDocumentsDocumentIdGet**](StatusRevocationAPI.md#GetDocumentStatusApiV1StatusDocumentsDocumentIdGet) | **Get** /api/v1/status/documents/{document_id} | Get Document Status
[**GetDocumentStatusApiV1StatusDocumentsDocumentIdGet_0**](StatusRevocationAPI.md#GetDocumentStatusApiV1StatusDocumentsDocumentIdGet_0) | **Get** /api/v1/status/documents/{document_id} | Get Document Status
[**GetStatusListApiV1StatusListOrganizationIdListIndexGet**](StatusRevocationAPI.md#GetStatusListApiV1StatusListOrganizationIdListIndexGet) | **Get** /api/v1/status/list/{organization_id}/{list_index} | Get Status List
[**GetStatusListApiV1StatusListOrganizationIdListIndexGet_0**](StatusRevocationAPI.md#GetStatusListApiV1StatusListOrganizationIdListIndexGet_0) | **Get** /api/v1/status/list/{organization_id}/{list_index} | Get Status List
[**GetStatusStatsApiV1StatusStatsGet**](StatusRevocationAPI.md#GetStatusStatsApiV1StatusStatsGet) | **Get** /api/v1/status/stats | Get Status Stats
[**GetStatusStatsApiV1StatusStatsGet_0**](StatusRevocationAPI.md#GetStatusStatsApiV1StatusStatsGet_0) | **Get** /api/v1/status/stats | Get Status Stats
[**ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost**](StatusRevocationAPI.md#ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost) | **Post** /api/v1/status/documents/{document_id}/reinstate | Reinstate Document
[**ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost_0**](StatusRevocationAPI.md#ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost_0) | **Post** /api/v1/status/documents/{document_id}/reinstate | Reinstate Document
[**RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost**](StatusRevocationAPI.md#RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost) | **Post** /api/v1/status/documents/{document_id}/revoke | Revoke Document
[**RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost_0**](StatusRevocationAPI.md#RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost_0) | **Post** /api/v1/status/documents/{document_id}/revoke | Revoke Document



## GetDocumentStatusApiV1StatusDocumentsDocumentIdGet

> DocumentStatusResponse GetDocumentStatusApiV1StatusDocumentsDocumentIdGet(ctx, documentId).Execute()

Get Document Status



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
	resp, r, err := apiClient.StatusRevocationAPI.GetDocumentStatusApiV1StatusDocumentsDocumentIdGet(context.Background(), documentId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StatusRevocationAPI.GetDocumentStatusApiV1StatusDocumentsDocumentIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetDocumentStatusApiV1StatusDocumentsDocumentIdGet`: DocumentStatusResponse
	fmt.Fprintf(os.Stdout, "Response from `StatusRevocationAPI.GetDocumentStatusApiV1StatusDocumentsDocumentIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**documentId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetDocumentStatusApiV1StatusDocumentsDocumentIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**DocumentStatusResponse**](DocumentStatusResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetDocumentStatusApiV1StatusDocumentsDocumentIdGet_0

> DocumentStatusResponse GetDocumentStatusApiV1StatusDocumentsDocumentIdGet_0(ctx, documentId).Execute()

Get Document Status



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
	resp, r, err := apiClient.StatusRevocationAPI.GetDocumentStatusApiV1StatusDocumentsDocumentIdGet_0(context.Background(), documentId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StatusRevocationAPI.GetDocumentStatusApiV1StatusDocumentsDocumentIdGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetDocumentStatusApiV1StatusDocumentsDocumentIdGet_0`: DocumentStatusResponse
	fmt.Fprintf(os.Stdout, "Response from `StatusRevocationAPI.GetDocumentStatusApiV1StatusDocumentsDocumentIdGet_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**documentId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetDocumentStatusApiV1StatusDocumentsDocumentIdGet_1Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**DocumentStatusResponse**](DocumentStatusResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetStatusListApiV1StatusListOrganizationIdListIndexGet

> interface{} GetStatusListApiV1StatusListOrganizationIdListIndexGet(ctx, organizationId, listIndex).Execute()

Get Status List



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
	organizationId := "organizationId_example" // string | 
	listIndex := int32(56) // int32 | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StatusRevocationAPI.GetStatusListApiV1StatusListOrganizationIdListIndexGet(context.Background(), organizationId, listIndex).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StatusRevocationAPI.GetStatusListApiV1StatusListOrganizationIdListIndexGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetStatusListApiV1StatusListOrganizationIdListIndexGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StatusRevocationAPI.GetStatusListApiV1StatusListOrganizationIdListIndexGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**organizationId** | **string** |  | 
**listIndex** | **int32** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetStatusListApiV1StatusListOrganizationIdListIndexGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



### Return type

**interface{}**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetStatusListApiV1StatusListOrganizationIdListIndexGet_0

> interface{} GetStatusListApiV1StatusListOrganizationIdListIndexGet_0(ctx, organizationId, listIndex).Execute()

Get Status List



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
	organizationId := "organizationId_example" // string | 
	listIndex := int32(56) // int32 | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StatusRevocationAPI.GetStatusListApiV1StatusListOrganizationIdListIndexGet_0(context.Background(), organizationId, listIndex).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StatusRevocationAPI.GetStatusListApiV1StatusListOrganizationIdListIndexGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetStatusListApiV1StatusListOrganizationIdListIndexGet_0`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StatusRevocationAPI.GetStatusListApiV1StatusListOrganizationIdListIndexGet_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**organizationId** | **string** |  | 
**listIndex** | **int32** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetStatusListApiV1StatusListOrganizationIdListIndexGet_2Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



### Return type

**interface{}**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetStatusStatsApiV1StatusStatsGet

> interface{} GetStatusStatsApiV1StatusStatsGet(ctx).Execute()

Get Status Stats



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
	resp, r, err := apiClient.StatusRevocationAPI.GetStatusStatsApiV1StatusStatsGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StatusRevocationAPI.GetStatusStatsApiV1StatusStatsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetStatusStatsApiV1StatusStatsGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StatusRevocationAPI.GetStatusStatsApiV1StatusStatsGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetStatusStatsApiV1StatusStatsGetRequest struct via the builder pattern


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


## GetStatusStatsApiV1StatusStatsGet_0

> interface{} GetStatusStatsApiV1StatusStatsGet_0(ctx).Execute()

Get Status Stats



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
	resp, r, err := apiClient.StatusRevocationAPI.GetStatusStatsApiV1StatusStatsGet_0(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StatusRevocationAPI.GetStatusStatsApiV1StatusStatsGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetStatusStatsApiV1StatusStatsGet_0`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StatusRevocationAPI.GetStatusStatsApiV1StatusStatsGet_0`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetStatusStatsApiV1StatusStatsGet_3Request struct via the builder pattern


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


## ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost

> RevocationResponse ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost(ctx, documentId).Execute()

Reinstate Document



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
	resp, r, err := apiClient.StatusRevocationAPI.ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost(context.Background(), documentId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StatusRevocationAPI.ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost`: RevocationResponse
	fmt.Fprintf(os.Stdout, "Response from `StatusRevocationAPI.ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**documentId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**RevocationResponse**](RevocationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost_0

> RevocationResponse ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost_0(ctx, documentId).Execute()

Reinstate Document



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
	resp, r, err := apiClient.StatusRevocationAPI.ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost_0(context.Background(), documentId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StatusRevocationAPI.ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost_0`: RevocationResponse
	fmt.Fprintf(os.Stdout, "Response from `StatusRevocationAPI.ReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**documentId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiReinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost_4Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**RevocationResponse**](RevocationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost

> RevocationResponse RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost(ctx, documentId).RevokeRequest(revokeRequest).Execute()

Revoke Document



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
	revokeRequest := *openapiclient.NewRevokeRequest(openapiclient.RevocationReason("factual_error")) // RevokeRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StatusRevocationAPI.RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost(context.Background(), documentId).RevokeRequest(revokeRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StatusRevocationAPI.RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost`: RevocationResponse
	fmt.Fprintf(os.Stdout, "Response from `StatusRevocationAPI.RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**documentId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiRevokeDocumentApiV1StatusDocumentsDocumentIdRevokePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **revokeRequest** | [**RevokeRequest**](RevokeRequest.md) |  | 

### Return type

[**RevocationResponse**](RevocationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost_0

> RevocationResponse RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost_0(ctx, documentId).RevokeRequest(revokeRequest).Execute()

Revoke Document



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
	revokeRequest := *openapiclient.NewRevokeRequest(openapiclient.RevocationReason("factual_error")) // RevokeRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StatusRevocationAPI.RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost_0(context.Background(), documentId).RevokeRequest(revokeRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StatusRevocationAPI.RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost_0`: RevocationResponse
	fmt.Fprintf(os.Stdout, "Response from `StatusRevocationAPI.RevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**documentId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiRevokeDocumentApiV1StatusDocumentsDocumentIdRevokePost_5Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **revokeRequest** | [**RevokeRequest**](RevokeRequest.md) |  | 

### Return type

[**RevocationResponse**](RevocationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

