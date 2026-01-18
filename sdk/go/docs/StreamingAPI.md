# \StreamingAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CloseStreamingSessionApiV1SignStreamSessionsSessionIdClosePost**](StreamingAPI.md#CloseStreamingSessionApiV1SignStreamSessionsSessionIdClosePost) | **Post** /api/v1/sign/stream/sessions/{session_id}/close | Close Streaming Session
[**CreateStreamingSessionApiV1SignStreamSessionsPost**](StreamingAPI.md#CreateStreamingSessionApiV1SignStreamSessionsPost) | **Post** /api/v1/sign/stream/sessions | Create Streaming Session
[**GetStreamRunApiV1SignStreamRunsRunIdGet**](StreamingAPI.md#GetStreamRunApiV1SignStreamRunsRunIdGet) | **Get** /api/v1/sign/stream/runs/{run_id} | Get Stream Run
[**GetStreamingStatsApiV1SignStreamStatsGet**](StreamingAPI.md#GetStreamingStatsApiV1SignStreamStatsGet) | **Get** /api/v1/sign/stream/stats | Get Streaming Stats
[**SseEventsEndpointApiV1SignStreamSessionsSessionIdEventsGet**](StreamingAPI.md#SseEventsEndpointApiV1SignStreamSessionsSessionIdEventsGet) | **Get** /api/v1/sign/stream/sessions/{session_id}/events | Sse Events Endpoint
[**StreamSigningApiV1SignStreamPost**](StreamingAPI.md#StreamSigningApiV1SignStreamPost) | **Post** /api/v1/sign/stream | Stream Signing



## CloseStreamingSessionApiV1SignStreamSessionsSessionIdClosePost

> interface{} CloseStreamingSessionApiV1SignStreamSessionsSessionIdClosePost(ctx, sessionId).Execute()

Close Streaming Session



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
	sessionId := "sessionId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StreamingAPI.CloseStreamingSessionApiV1SignStreamSessionsSessionIdClosePost(context.Background(), sessionId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingAPI.CloseStreamingSessionApiV1SignStreamSessionsSessionIdClosePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CloseStreamingSessionApiV1SignStreamSessionsSessionIdClosePost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StreamingAPI.CloseStreamingSessionApiV1SignStreamSessionsSessionIdClosePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**sessionId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiCloseStreamingSessionApiV1SignStreamSessionsSessionIdClosePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

**interface{}**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateStreamingSessionApiV1SignStreamSessionsPost

> interface{} CreateStreamingSessionApiV1SignStreamSessionsPost(ctx).SessionType(sessionType).BodyCreateStreamingSessionApiV1SignStreamSessionsPost(bodyCreateStreamingSessionApiV1SignStreamSessionsPost).Execute()

Create Streaming Session



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
	sessionType := "sessionType_example" // string |  (optional) (default to "websocket")
	bodyCreateStreamingSessionApiV1SignStreamSessionsPost := *openapiclient.NewBodyCreateStreamingSessionApiV1SignStreamSessionsPost() // BodyCreateStreamingSessionApiV1SignStreamSessionsPost |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StreamingAPI.CreateStreamingSessionApiV1SignStreamSessionsPost(context.Background()).SessionType(sessionType).BodyCreateStreamingSessionApiV1SignStreamSessionsPost(bodyCreateStreamingSessionApiV1SignStreamSessionsPost).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingAPI.CreateStreamingSessionApiV1SignStreamSessionsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateStreamingSessionApiV1SignStreamSessionsPost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StreamingAPI.CreateStreamingSessionApiV1SignStreamSessionsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateStreamingSessionApiV1SignStreamSessionsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sessionType** | **string** |  | [default to &quot;websocket&quot;]
 **bodyCreateStreamingSessionApiV1SignStreamSessionsPost** | [**BodyCreateStreamingSessionApiV1SignStreamSessionsPost**](BodyCreateStreamingSessionApiV1SignStreamSessionsPost.md) |  | 

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


## GetStreamRunApiV1SignStreamRunsRunIdGet

> interface{} GetStreamRunApiV1SignStreamRunsRunIdGet(ctx, runId).Execute()

Get Stream Run



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
	runId := "runId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StreamingAPI.GetStreamRunApiV1SignStreamRunsRunIdGet(context.Background(), runId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingAPI.GetStreamRunApiV1SignStreamRunsRunIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetStreamRunApiV1SignStreamRunsRunIdGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StreamingAPI.GetStreamRunApiV1SignStreamRunsRunIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**runId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetStreamRunApiV1SignStreamRunsRunIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

**interface{}**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetStreamingStatsApiV1SignStreamStatsGet

> interface{} GetStreamingStatsApiV1SignStreamStatsGet(ctx).Execute()

Get Streaming Stats



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
	resp, r, err := apiClient.StreamingAPI.GetStreamingStatsApiV1SignStreamStatsGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingAPI.GetStreamingStatsApiV1SignStreamStatsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetStreamingStatsApiV1SignStreamStatsGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StreamingAPI.GetStreamingStatsApiV1SignStreamStatsGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetStreamingStatsApiV1SignStreamStatsGetRequest struct via the builder pattern


### Return type

**interface{}**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SseEventsEndpointApiV1SignStreamSessionsSessionIdEventsGet

> interface{} SseEventsEndpointApiV1SignStreamSessionsSessionIdEventsGet(ctx, sessionId).ApiKey(apiKey).Execute()

Sse Events Endpoint



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
	sessionId := "sessionId_example" // string | 
	apiKey := "apiKey_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StreamingAPI.SseEventsEndpointApiV1SignStreamSessionsSessionIdEventsGet(context.Background(), sessionId).ApiKey(apiKey).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingAPI.SseEventsEndpointApiV1SignStreamSessionsSessionIdEventsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SseEventsEndpointApiV1SignStreamSessionsSessionIdEventsGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StreamingAPI.SseEventsEndpointApiV1SignStreamSessionsSessionIdEventsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**sessionId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiSseEventsEndpointApiV1SignStreamSessionsSessionIdEventsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **apiKey** | **string** |  | 

### Return type

**interface{}**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## StreamSigningApiV1SignStreamPost

> StreamSigningApiV1SignStreamPost(ctx).StreamSignRequest(streamSignRequest).Execute()

Stream Signing



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
	streamSignRequest := *openapiclient.NewStreamSignRequest("Text_example") // StreamSignRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.StreamingAPI.StreamSigningApiV1SignStreamPost(context.Background()).StreamSignRequest(streamSignRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingAPI.StreamSigningApiV1SignStreamPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiStreamSigningApiV1SignStreamPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **streamSignRequest** | [**StreamSignRequest**](StreamSignRequest.md) |  | 

### Return type

 (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

