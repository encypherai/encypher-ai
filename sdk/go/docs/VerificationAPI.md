# \VerificationAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**VerifyByDocumentIdApiV1VerifyDocumentIdGet**](VerificationAPI.md#VerifyByDocumentIdApiV1VerifyDocumentIdGet) | **Get** /api/v1/verify/{document_id} | Verify By Document Id
[**VerifyContentApiV1VerifyPost**](VerificationAPI.md#VerifyContentApiV1VerifyPost) | **Post** /api/v1/verify | Verify Content



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


## VerifyContentApiV1VerifyPost

> VerifyResponse VerifyContentApiV1VerifyPost(ctx).VerifyRequest(verifyRequest).Execute()

Verify Content



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

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.VerificationAPI.VerifyContentApiV1VerifyPost(context.Background()).VerifyRequest(verifyRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `VerificationAPI.VerifyContentApiV1VerifyPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `VerifyContentApiV1VerifyPost`: VerifyResponse
	fmt.Fprintf(os.Stdout, "Response from `VerificationAPI.VerifyContentApiV1VerifyPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiVerifyContentApiV1VerifyPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verifyRequest** | [**VerifyRequest**](VerifyRequest.md) |  | 

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

