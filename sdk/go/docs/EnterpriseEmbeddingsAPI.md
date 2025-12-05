# \EnterpriseEmbeddingsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**EncodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPost**](EnterpriseEmbeddingsAPI.md#EncodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPost) | **Post** /api/v1/enterprise/embeddings/encode-with-embeddings | Encode With Embeddings



## EncodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPost

> EncodeWithEmbeddingsResponse EncodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPost(ctx).EncodeWithEmbeddingsRequest(encodeWithEmbeddingsRequest).Authorization(authorization).Execute()

Encode With Embeddings



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
	encodeWithEmbeddingsRequest := *openapiclient.NewEncodeWithEmbeddingsRequest("DocumentId_example", "Text_example") // EncodeWithEmbeddingsRequest | 
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.EnterpriseEmbeddingsAPI.EncodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPost(context.Background()).EncodeWithEmbeddingsRequest(encodeWithEmbeddingsRequest).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `EnterpriseEmbeddingsAPI.EncodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `EncodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPost`: EncodeWithEmbeddingsResponse
	fmt.Fprintf(os.Stdout, "Response from `EnterpriseEmbeddingsAPI.EncodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiEncodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **encodeWithEmbeddingsRequest** | [**EncodeWithEmbeddingsRequest**](EncodeWithEmbeddingsRequest.md) |  | 
 **authorization** | **string** |  | 

### Return type

[**EncodeWithEmbeddingsResponse**](EncodeWithEmbeddingsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

