# \SigningAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**SignAdvancedApiV1SignAdvancedPost**](SigningAPI.md#SignAdvancedApiV1SignAdvancedPost) | **Post** /api/v1/sign/advanced | Sign with advanced embedding controls
[**SignContentApiV1SignPost**](SigningAPI.md#SignContentApiV1SignPost) | **Post** /api/v1/sign | Sign Content



## SignAdvancedApiV1SignAdvancedPost

> EncodeWithEmbeddingsResponse SignAdvancedApiV1SignAdvancedPost(ctx).EncodeWithEmbeddingsRequest(encodeWithEmbeddingsRequest).Execute()

Sign with advanced embedding controls



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
	encodeWithEmbeddingsRequest := *openapiclient.NewEncodeWithEmbeddingsRequest("DocumentId_example", "Text_example") // EncodeWithEmbeddingsRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.SigningAPI.SignAdvancedApiV1SignAdvancedPost(context.Background()).EncodeWithEmbeddingsRequest(encodeWithEmbeddingsRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `SigningAPI.SignAdvancedApiV1SignAdvancedPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SignAdvancedApiV1SignAdvancedPost`: EncodeWithEmbeddingsResponse
	fmt.Fprintf(os.Stdout, "Response from `SigningAPI.SignAdvancedApiV1SignAdvancedPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiSignAdvancedApiV1SignAdvancedPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **encodeWithEmbeddingsRequest** | [**EncodeWithEmbeddingsRequest**](EncodeWithEmbeddingsRequest.md) |  | 

### Return type

[**EncodeWithEmbeddingsResponse**](EncodeWithEmbeddingsResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SignContentApiV1SignPost

> SignResponse SignContentApiV1SignPost(ctx).SignRequest(signRequest).Execute()

Sign Content



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
	signRequest := *openapiclient.NewSignRequest("Text_example") // SignRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.SigningAPI.SignContentApiV1SignPost(context.Background()).SignRequest(signRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `SigningAPI.SignContentApiV1SignPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SignContentApiV1SignPost`: SignResponse
	fmt.Fprintf(os.Stdout, "Response from `SigningAPI.SignContentApiV1SignPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiSignContentApiV1SignPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **signRequest** | [**SignRequest**](SignRequest.md) |  | 

### Return type

[**SignResponse**](SignResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

