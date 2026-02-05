# \PublicVerificationAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**BatchVerifyEmbeddingsApiV1PublicVerifyBatchPost**](PublicVerificationAPI.md#BatchVerifyEmbeddingsApiV1PublicVerifyBatchPost) | **Post** /api/v1/public/verify/batch | Batch Verify Embeddings (Public - No Auth Required)
[**ExtractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPost**](PublicVerificationAPI.md#ExtractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPost) | **Post** /api/v1/public/extract-and-verify | DEPRECATED - Use POST /api/v1/verify instead
[**VerifyEmbeddingApiV1PublicVerifyRefIdGet**](PublicVerificationAPI.md#VerifyEmbeddingApiV1PublicVerifyRefIdGet) | **Get** /api/v1/public/verify/{ref_id} | Verify Embedding (Public - No Auth Required)



## BatchVerifyEmbeddingsApiV1PublicVerifyBatchPost

> BatchVerifyResponse BatchVerifyEmbeddingsApiV1PublicVerifyBatchPost(ctx).BatchVerifyRequest(batchVerifyRequest).Authorization(authorization).Execute()

Batch Verify Embeddings (Public - No Auth Required)



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
	batchVerifyRequest := *openapiclient.NewBatchVerifyRequest([]openapiclient.VerifyEmbeddingRequest{*openapiclient.NewVerifyEmbeddingRequest("RefId_example", "Signature_example")}) // BatchVerifyRequest | 
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PublicVerificationAPI.BatchVerifyEmbeddingsApiV1PublicVerifyBatchPost(context.Background()).BatchVerifyRequest(batchVerifyRequest).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PublicVerificationAPI.BatchVerifyEmbeddingsApiV1PublicVerifyBatchPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `BatchVerifyEmbeddingsApiV1PublicVerifyBatchPost`: BatchVerifyResponse
	fmt.Fprintf(os.Stdout, "Response from `PublicVerificationAPI.BatchVerifyEmbeddingsApiV1PublicVerifyBatchPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiBatchVerifyEmbeddingsApiV1PublicVerifyBatchPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batchVerifyRequest** | [**BatchVerifyRequest**](BatchVerifyRequest.md) |  | 
 **authorization** | **string** |  | 

### Return type

[**BatchVerifyResponse**](BatchVerifyResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ExtractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPost

> interface{} ExtractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPost(ctx).ExtractAndVerifyRequest(extractAndVerifyRequest).Execute()

DEPRECATED - Use POST /api/v1/verify instead



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
	extractAndVerifyRequest := *openapiclient.NewExtractAndVerifyRequest("Text_example") // ExtractAndVerifyRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PublicVerificationAPI.ExtractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPost(context.Background()).ExtractAndVerifyRequest(extractAndVerifyRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PublicVerificationAPI.ExtractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ExtractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `PublicVerificationAPI.ExtractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiExtractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **extractAndVerifyRequest** | [**ExtractAndVerifyRequest**](ExtractAndVerifyRequest.md) |  | 

### Return type

**interface{}**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## VerifyEmbeddingApiV1PublicVerifyRefIdGet

> VerifyEmbeddingResponse VerifyEmbeddingApiV1PublicVerifyRefIdGet(ctx, refId).Signature(signature).Authorization(authorization).Execute()

Verify Embedding (Public - No Auth Required)



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
	refId := "refId_example" // string | 
	signature := "signature_example" // string | HMAC signature (8+ hex characters)
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PublicVerificationAPI.VerifyEmbeddingApiV1PublicVerifyRefIdGet(context.Background(), refId).Signature(signature).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PublicVerificationAPI.VerifyEmbeddingApiV1PublicVerifyRefIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `VerifyEmbeddingApiV1PublicVerifyRefIdGet`: VerifyEmbeddingResponse
	fmt.Fprintf(os.Stdout, "Response from `PublicVerificationAPI.VerifyEmbeddingApiV1PublicVerifyRefIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**refId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiVerifyEmbeddingApiV1PublicVerifyRefIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **signature** | **string** | HMAC signature (8+ hex characters) | 
 **authorization** | **string** |  | 

### Return type

[**VerifyEmbeddingResponse**](VerifyEmbeddingResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

