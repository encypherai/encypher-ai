# \EnterpriseMerkleTreesAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**DetectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPost**](EnterpriseMerkleTreesAPI.md#DetectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPost) | **Post** /api/v1/enterprise/merkle/detect-plagiarism | Detect Plagiarism
[**EncodeDocumentApiV1EnterpriseMerkleEncodePost**](EnterpriseMerkleTreesAPI.md#EncodeDocumentApiV1EnterpriseMerkleEncodePost) | **Post** /api/v1/enterprise/merkle/encode | Encode Document into Merkle Trees
[**FindSourcesApiV1EnterpriseMerkleAttributePost**](EnterpriseMerkleTreesAPI.md#FindSourcesApiV1EnterpriseMerkleAttributePost) | **Post** /api/v1/enterprise/merkle/attribute | Find Source Documents



## DetectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPost

> PlagiarismDetectionResponse DetectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPost(ctx).PlagiarismDetectionRequest(plagiarismDetectionRequest).Execute()

Detect Plagiarism



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
	plagiarismDetectionRequest := *openapiclient.NewPlagiarismDetectionRequest("TargetText_example") // PlagiarismDetectionRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.EnterpriseMerkleTreesAPI.DetectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPost(context.Background()).PlagiarismDetectionRequest(plagiarismDetectionRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `EnterpriseMerkleTreesAPI.DetectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DetectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPost`: PlagiarismDetectionResponse
	fmt.Fprintf(os.Stdout, "Response from `EnterpriseMerkleTreesAPI.DetectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiDetectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plagiarismDetectionRequest** | [**PlagiarismDetectionRequest**](PlagiarismDetectionRequest.md) |  | 

### Return type

[**PlagiarismDetectionResponse**](PlagiarismDetectionResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


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


## FindSourcesApiV1EnterpriseMerkleAttributePost

> SourceAttributionResponse FindSourcesApiV1EnterpriseMerkleAttributePost(ctx).SourceAttributionRequest(sourceAttributionRequest).Execute()

Find Source Documents



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
	sourceAttributionRequest := *openapiclient.NewSourceAttributionRequest("This is a sentence to find.") // SourceAttributionRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.EnterpriseMerkleTreesAPI.FindSourcesApiV1EnterpriseMerkleAttributePost(context.Background()).SourceAttributionRequest(sourceAttributionRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `EnterpriseMerkleTreesAPI.FindSourcesApiV1EnterpriseMerkleAttributePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `FindSourcesApiV1EnterpriseMerkleAttributePost`: SourceAttributionResponse
	fmt.Fprintf(os.Stdout, "Response from `EnterpriseMerkleTreesAPI.FindSourcesApiV1EnterpriseMerkleAttributePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiFindSourcesApiV1EnterpriseMerkleAttributePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sourceAttributionRequest** | [**SourceAttributionRequest**](SourceAttributionRequest.md) |  | 

### Return type

[**SourceAttributionResponse**](SourceAttributionResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

