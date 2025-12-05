# \PublicToolsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**DecodeTextApiV1ToolsDecodePost**](PublicToolsAPI.md#DecodeTextApiV1ToolsDecodePost) | **Post** /api/v1/tools/decode | Decode Text
[**DecodeTextApiV1ToolsDecodePost_0**](PublicToolsAPI.md#DecodeTextApiV1ToolsDecodePost_0) | **Post** /api/v1/tools/decode | Decode Text
[**EncodeTextApiV1ToolsEncodePost**](PublicToolsAPI.md#EncodeTextApiV1ToolsEncodePost) | **Post** /api/v1/tools/encode | Encode Text
[**EncodeTextApiV1ToolsEncodePost_0**](PublicToolsAPI.md#EncodeTextApiV1ToolsEncodePost_0) | **Post** /api/v1/tools/encode | Encode Text



## DecodeTextApiV1ToolsDecodePost

> DecodeToolResponse DecodeTextApiV1ToolsDecodePost(ctx).DecodeToolRequest(decodeToolRequest).Execute()

Decode Text



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
	decodeToolRequest := *openapiclient.NewDecodeToolRequest("EncodedText_example") // DecodeToolRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PublicToolsAPI.DecodeTextApiV1ToolsDecodePost(context.Background()).DecodeToolRequest(decodeToolRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PublicToolsAPI.DecodeTextApiV1ToolsDecodePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DecodeTextApiV1ToolsDecodePost`: DecodeToolResponse
	fmt.Fprintf(os.Stdout, "Response from `PublicToolsAPI.DecodeTextApiV1ToolsDecodePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiDecodeTextApiV1ToolsDecodePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **decodeToolRequest** | [**DecodeToolRequest**](DecodeToolRequest.md) |  | 

### Return type

[**DecodeToolResponse**](DecodeToolResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DecodeTextApiV1ToolsDecodePost_0

> DecodeToolResponse DecodeTextApiV1ToolsDecodePost_0(ctx).DecodeToolRequest(decodeToolRequest).Execute()

Decode Text



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
	decodeToolRequest := *openapiclient.NewDecodeToolRequest("EncodedText_example") // DecodeToolRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PublicToolsAPI.DecodeTextApiV1ToolsDecodePost_0(context.Background()).DecodeToolRequest(decodeToolRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PublicToolsAPI.DecodeTextApiV1ToolsDecodePost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DecodeTextApiV1ToolsDecodePost_0`: DecodeToolResponse
	fmt.Fprintf(os.Stdout, "Response from `PublicToolsAPI.DecodeTextApiV1ToolsDecodePost_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiDecodeTextApiV1ToolsDecodePost_1Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **decodeToolRequest** | [**DecodeToolRequest**](DecodeToolRequest.md) |  | 

### Return type

[**DecodeToolResponse**](DecodeToolResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## EncodeTextApiV1ToolsEncodePost

> EncodeToolResponse EncodeTextApiV1ToolsEncodePost(ctx).EncodeToolRequest(encodeToolRequest).Execute()

Encode Text



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
	encodeToolRequest := *openapiclient.NewEncodeToolRequest("OriginalText_example") // EncodeToolRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PublicToolsAPI.EncodeTextApiV1ToolsEncodePost(context.Background()).EncodeToolRequest(encodeToolRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PublicToolsAPI.EncodeTextApiV1ToolsEncodePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `EncodeTextApiV1ToolsEncodePost`: EncodeToolResponse
	fmt.Fprintf(os.Stdout, "Response from `PublicToolsAPI.EncodeTextApiV1ToolsEncodePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiEncodeTextApiV1ToolsEncodePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **encodeToolRequest** | [**EncodeToolRequest**](EncodeToolRequest.md) |  | 

### Return type

[**EncodeToolResponse**](EncodeToolResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## EncodeTextApiV1ToolsEncodePost_0

> EncodeToolResponse EncodeTextApiV1ToolsEncodePost_0(ctx).EncodeToolRequest(encodeToolRequest).Execute()

Encode Text



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
	encodeToolRequest := *openapiclient.NewEncodeToolRequest("OriginalText_example") // EncodeToolRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PublicToolsAPI.EncodeTextApiV1ToolsEncodePost_0(context.Background()).EncodeToolRequest(encodeToolRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PublicToolsAPI.EncodeTextApiV1ToolsEncodePost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `EncodeTextApiV1ToolsEncodePost_0`: EncodeToolResponse
	fmt.Fprintf(os.Stdout, "Response from `PublicToolsAPI.EncodeTextApiV1ToolsEncodePost_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiEncodeTextApiV1ToolsEncodePost_2Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **encodeToolRequest** | [**EncodeToolRequest**](EncodeToolRequest.md) |  | 

### Return type

[**EncodeToolResponse**](EncodeToolResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

