# \EnterpriseMerkleTreesAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**EncodeDocumentApiV1EnterpriseMerkleEncodePost**](EnterpriseMerkleTreesAPI.md#EncodeDocumentApiV1EnterpriseMerkleEncodePost) | **Post** /api/v1/enterprise/merkle/encode | Encode Document into Merkle Trees



## EncodeDocumentApiV1EnterpriseMerkleEncodePost

> DocumentEncodeResponse EncodeDocumentApiV1EnterpriseMerkleEncodePost(ctx).DocumentEncodeRequest(documentEncodeRequest).Execute()

Encode Document into Merkle Trees



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
	documentEncodeRequest := *openapiclient.NewDocumentEncodeRequest("doc_2024_article_001", "This is the first sentence. This is the second sentence.") // DocumentEncodeRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.EnterpriseMerkleTreesAPI.EncodeDocumentApiV1EnterpriseMerkleEncodePost(context.Background()).DocumentEncodeRequest(documentEncodeRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `EnterpriseMerkleTreesAPI.EncodeDocumentApiV1EnterpriseMerkleEncodePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `EncodeDocumentApiV1EnterpriseMerkleEncodePost`: DocumentEncodeResponse
	fmt.Fprintf(os.Stdout, "Response from `EnterpriseMerkleTreesAPI.EncodeDocumentApiV1EnterpriseMerkleEncodePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiEncodeDocumentApiV1EnterpriseMerkleEncodePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **documentEncodeRequest** | [**DocumentEncodeRequest**](DocumentEncodeRequest.md) |  | 

### Return type

[**DocumentEncodeResponse**](DocumentEncodeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

