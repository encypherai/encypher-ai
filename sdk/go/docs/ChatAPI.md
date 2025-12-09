# \ChatAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ChatHealthCheckApiV1StreamChatHealthGet**](ChatAPI.md#ChatHealthCheckApiV1StreamChatHealthGet) | **Get** /api/v1/stream/chat/health | Chat Health Check
[**OpenaiCompatibleChatApiV1StreamChatOpenaiCompatiblePost**](ChatAPI.md#OpenaiCompatibleChatApiV1StreamChatOpenaiCompatiblePost) | **Post** /api/v1/stream/chat/openai-compatible | Openai Compatible Chat



## ChatHealthCheckApiV1StreamChatHealthGet

> interface{} ChatHealthCheckApiV1StreamChatHealthGet(ctx).Execute()

Chat Health Check



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

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ChatAPI.ChatHealthCheckApiV1StreamChatHealthGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ChatAPI.ChatHealthCheckApiV1StreamChatHealthGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ChatHealthCheckApiV1StreamChatHealthGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `ChatAPI.ChatHealthCheckApiV1StreamChatHealthGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiChatHealthCheckApiV1StreamChatHealthGetRequest struct via the builder pattern


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


## OpenaiCompatibleChatApiV1StreamChatOpenaiCompatiblePost

> interface{} OpenaiCompatibleChatApiV1StreamChatOpenaiCompatiblePost(ctx).ChatCompletionRequest(chatCompletionRequest).Execute()

Openai Compatible Chat



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
	chatCompletionRequest := *openapiclient.NewChatCompletionRequest([]openapiclient.ChatMessage{*openapiclient.NewChatMessage("Role_example", "Content_example")}) // ChatCompletionRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ChatAPI.OpenaiCompatibleChatApiV1StreamChatOpenaiCompatiblePost(context.Background()).ChatCompletionRequest(chatCompletionRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ChatAPI.OpenaiCompatibleChatApiV1StreamChatOpenaiCompatiblePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `OpenaiCompatibleChatApiV1StreamChatOpenaiCompatiblePost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `ChatAPI.OpenaiCompatibleChatApiV1StreamChatOpenaiCompatiblePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiOpenaiCompatibleChatApiV1StreamChatOpenaiCompatiblePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **chatCompletionRequest** | [**ChatCompletionRequest**](ChatCompletionRequest.md) |  | 

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

