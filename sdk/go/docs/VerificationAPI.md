# \VerificationAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GetStatsApiV1VerifyStatsGet**](VerificationAPI.md#GetStatsApiV1VerifyStatsGet) | **Get** /api/v1/verify/stats | Get Stats
[**GetVerificationHistoryApiV1VerifyHistoryDocumentIdGet**](VerificationAPI.md#GetVerificationHistoryApiV1VerifyHistoryDocumentIdGet) | **Get** /api/v1/verify/history/{document_id} | Get Verification History
[**HealthCheckApiV1VerifyHealthGet**](VerificationAPI.md#HealthCheckApiV1VerifyHealthGet) | **Get** /api/v1/verify/health | Health Check
[**VerifyAdvancedApiV1VerifyAdvancedPost**](VerificationAPI.md#VerifyAdvancedApiV1VerifyAdvancedPost) | **Post** /api/v1/verify/advanced | Advanced verification
[**VerifyByDocumentIdApiV1VerifyDocumentIdGet**](VerificationAPI.md#VerifyByDocumentIdApiV1VerifyDocumentIdGet) | **Get** /api/v1/verify/{document_id} | Verify By Document Id
[**VerifyDocumentApiV1VerifyDocumentPost**](VerificationAPI.md#VerifyDocumentApiV1VerifyDocumentPost) | **Post** /api/v1/verify/document | Verify Document
[**VerifySignatureApiV1VerifySignaturePost**](VerificationAPI.md#VerifySignatureApiV1VerifySignaturePost) | **Post** /api/v1/verify/signature | Verify Signature
[**VerifyTextApiV1VerifyPost**](VerificationAPI.md#VerifyTextApiV1VerifyPost) | **Post** /api/v1/verify | Verify Text



## GetStatsApiV1VerifyStatsGet

> VerificationStats GetStatsApiV1VerifyStatsGet(ctx).Authorization(authorization).Execute()

Get Stats



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
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.VerificationAPI.GetStatsApiV1VerifyStatsGet(context.Background()).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VerificationAPI.GetStatsApiV1VerifyStatsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetStatsApiV1VerifyStatsGet`: VerificationStats
	fmt.Fprintf(os.Stdout, "Response from `VerificationAPI.GetStatsApiV1VerifyStatsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetStatsApiV1VerifyStatsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  | 

### Return type

[**VerificationStats**](VerificationStats.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetVerificationHistoryApiV1VerifyHistoryDocumentIdGet

> []VerificationHistory GetVerificationHistoryApiV1VerifyHistoryDocumentIdGet(ctx, documentId).Limit(limit).Execute()

Get Verification History



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
	limit := int32(56) // int32 |  (optional) (default to 100)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.VerificationAPI.GetVerificationHistoryApiV1VerifyHistoryDocumentIdGet(context.Background(), documentId).Limit(limit).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VerificationAPI.GetVerificationHistoryApiV1VerifyHistoryDocumentIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetVerificationHistoryApiV1VerifyHistoryDocumentIdGet`: []VerificationHistory
	fmt.Fprintf(os.Stdout, "Response from `VerificationAPI.GetVerificationHistoryApiV1VerifyHistoryDocumentIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**documentId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetVerificationHistoryApiV1VerifyHistoryDocumentIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **limit** | **int32** |  | [default to 100]

### Return type

[**[]VerificationHistory**](VerificationHistory.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## HealthCheckApiV1VerifyHealthGet

> interface{} HealthCheckApiV1VerifyHealthGet(ctx).Execute()

Health Check



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
	resp, r, err := apiClient.VerificationAPI.HealthCheckApiV1VerifyHealthGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VerificationAPI.HealthCheckApiV1VerifyHealthGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `HealthCheckApiV1VerifyHealthGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `VerificationAPI.HealthCheckApiV1VerifyHealthGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiHealthCheckApiV1VerifyHealthGetRequest struct via the builder pattern


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


## VerifyAdvancedApiV1VerifyAdvancedPost

> interface{} VerifyAdvancedApiV1VerifyAdvancedPost(ctx).VerifyAdvancedRequest(verifyAdvancedRequest).Execute()

Advanced verification



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
	verifyAdvancedRequest := *openapiclient.NewVerifyAdvancedRequest("Text_example") // VerifyAdvancedRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.VerificationAPI.VerifyAdvancedApiV1VerifyAdvancedPost(context.Background()).VerifyAdvancedRequest(verifyAdvancedRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VerificationAPI.VerifyAdvancedApiV1VerifyAdvancedPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `VerifyAdvancedApiV1VerifyAdvancedPost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `VerificationAPI.VerifyAdvancedApiV1VerifyAdvancedPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiVerifyAdvancedApiV1VerifyAdvancedPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verifyAdvancedRequest** | [**VerifyAdvancedRequest**](VerifyAdvancedRequest.md) |  | 

### Return type

**interface{}**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## VerifyByDocumentIdApiV1VerifyDocumentIdGet

> interface{} VerifyByDocumentIdApiV1VerifyDocumentIdGet(ctx, documentId).Execute()

Verify By Document Id



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
	resp, r, err := apiClient.VerificationAPI.VerifyByDocumentIdApiV1VerifyDocumentIdGet(context.Background(), documentId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VerificationAPI.VerifyByDocumentIdApiV1VerifyDocumentIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `VerifyByDocumentIdApiV1VerifyDocumentIdGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `VerificationAPI.VerifyByDocumentIdApiV1VerifyDocumentIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**documentId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiVerifyByDocumentIdApiV1VerifyDocumentIdGetRequest struct via the builder pattern


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


## VerifyDocumentApiV1VerifyDocumentPost

> VerificationResponse VerifyDocumentApiV1VerifyDocumentPost(ctx).DocumentVerify(documentVerify).XForwardedFor(xForwardedFor).UserAgent(userAgent).Authorization(authorization).Execute()

Verify Document



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
	documentVerify := *openapiclient.NewDocumentVerify("DocumentId_example", "Content_example") // DocumentVerify | 
	xForwardedFor := "xForwardedFor_example" // string |  (optional)
	userAgent := "userAgent_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.VerificationAPI.VerifyDocumentApiV1VerifyDocumentPost(context.Background()).DocumentVerify(documentVerify).XForwardedFor(xForwardedFor).UserAgent(userAgent).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VerificationAPI.VerifyDocumentApiV1VerifyDocumentPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `VerifyDocumentApiV1VerifyDocumentPost`: VerificationResponse
	fmt.Fprintf(os.Stdout, "Response from `VerificationAPI.VerifyDocumentApiV1VerifyDocumentPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiVerifyDocumentApiV1VerifyDocumentPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **documentVerify** | [**DocumentVerify**](DocumentVerify.md) |  | 
 **xForwardedFor** | **string** |  | 
 **userAgent** | **string** |  | 
 **authorization** | **string** |  | 

### Return type

[**VerificationResponse**](VerificationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## VerifySignatureApiV1VerifySignaturePost

> VerificationResponse VerifySignatureApiV1VerifySignaturePost(ctx).SignatureVerify(signatureVerify).XForwardedFor(xForwardedFor).UserAgent(userAgent).Authorization(authorization).Execute()

Verify Signature



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
	signatureVerify := *openapiclient.NewSignatureVerify("Content_example", "Signature_example", "PublicKeyPem_example") // SignatureVerify | 
	xForwardedFor := "xForwardedFor_example" // string |  (optional)
	userAgent := "userAgent_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.VerificationAPI.VerifySignatureApiV1VerifySignaturePost(context.Background()).SignatureVerify(signatureVerify).XForwardedFor(xForwardedFor).UserAgent(userAgent).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VerificationAPI.VerifySignatureApiV1VerifySignaturePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `VerifySignatureApiV1VerifySignaturePost`: VerificationResponse
	fmt.Fprintf(os.Stdout, "Response from `VerificationAPI.VerifySignatureApiV1VerifySignaturePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiVerifySignatureApiV1VerifySignaturePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **signatureVerify** | [**SignatureVerify**](SignatureVerify.md) |  | 
 **xForwardedFor** | **string** |  | 
 **userAgent** | **string** |  | 
 **authorization** | **string** |  | 

### Return type

[**VerificationResponse**](VerificationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## VerifyTextApiV1VerifyPost

> VerifyResponse VerifyTextApiV1VerifyPost(ctx).VerifyRequest(verifyRequest).Authorization(authorization).Execute()

Verify Text



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
	verifyRequest := *openapiclient.NewVerifyRequest("Text_example") // VerifyRequest | 
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.VerificationAPI.VerifyTextApiV1VerifyPost(context.Background()).VerifyRequest(verifyRequest).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VerificationAPI.VerifyTextApiV1VerifyPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `VerifyTextApiV1VerifyPost`: VerifyResponse
	fmt.Fprintf(os.Stdout, "Response from `VerificationAPI.VerifyTextApiV1VerifyPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiVerifyTextApiV1VerifyPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verifyRequest** | [**VerifyRequest**](VerifyRequest.md) |  | 
 **authorization** | **string** |  | 

### Return type

[**VerifyResponse**](VerifyResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

