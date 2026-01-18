# \ChatAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ChatHealthCheckApiV1ChatHealthGet**](ChatAPI.md#ChatHealthCheckApiV1ChatHealthGet) | **Get** /api/v1/chat/health | Chat Health Check
[**OpenaiCompatibleChatApiV1ChatCompletionsPost**](ChatAPI.md#OpenaiCompatibleChatApiV1ChatCompletionsPost) | **Post** /api/v1/chat/completions | Openai Compatible Chat



## ChatHealthCheckApiV1ChatHealthGet

> interface{} ChatHealthCheckApiV1ChatHealthGet(ctx).Execute()

Chat Health Check



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
	resp, r, err := apiClient.ChatAPI.ChatHealthCheckApiV1ChatHealthGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ChatAPI.ChatHealthCheckApiV1ChatHealthGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ChatHealthCheckApiV1ChatHealthGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `ChatAPI.ChatHealthCheckApiV1ChatHealthGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiChatHealthCheckApiV1ChatHealthGetRequest struct via the builder pattern


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


## OpenaiCompatibleChatApiV1ChatCompletionsPost

> interface{} OpenaiCompatibleChatApiV1ChatCompletionsPost(ctx).ChatCompletionRequest(chatCompletionRequest).Execute()

Openai Compatible Chat



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
	chatCompletionRequest := *openapiclient.NewChatCompletionRequest([]openapiclient.ChatMessage{*openapiclient.NewChatMessage("Role_example", "Content_example")}) // ChatCompletionRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ChatAPI.OpenaiCompatibleChatApiV1ChatCompletionsPost(context.Background()).ChatCompletionRequest(chatCompletionRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ChatAPI.OpenaiCompatibleChatApiV1ChatCompletionsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `OpenaiCompatibleChatApiV1ChatCompletionsPost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `ChatAPI.OpenaiCompatibleChatApiV1ChatCompletionsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiOpenaiCompatibleChatApiV1ChatCompletionsPostRequest struct via the builder pattern


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

