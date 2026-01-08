# \StreamingAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CloseStreamingSessionApiV1StreamSessionSessionIdClosePost**](StreamingAPI.md#CloseStreamingSessionApiV1StreamSessionSessionIdClosePost) | **Post** /api/v1/stream/session/{session_id}/close | Close Streaming Session
[**CreateStreamingSessionApiV1StreamSessionCreatePost**](StreamingAPI.md#CreateStreamingSessionApiV1StreamSessionCreatePost) | **Post** /api/v1/stream/session/create | Create Streaming Session
[**GetStreamRunApiV1StreamRunsRunIdGet**](StreamingAPI.md#GetStreamRunApiV1StreamRunsRunIdGet) | **Get** /api/v1/stream/runs/{run_id} | Get Stream Run
[**GetStreamingStatsApiV1StreamStatsGet**](StreamingAPI.md#GetStreamingStatsApiV1StreamStatsGet) | **Get** /api/v1/stream/stats | Get Streaming Stats
[**SseEventsEndpointApiV1StreamEventsGet**](StreamingAPI.md#SseEventsEndpointApiV1StreamEventsGet) | **Get** /api/v1/stream/events | Sse Events Endpoint
[**StreamSigningApiV1StreamSignPost**](StreamingAPI.md#StreamSigningApiV1StreamSignPost) | **Post** /api/v1/stream/sign | Stream Signing
[**StreamingHealthCheckApiV1StreamHealthGet**](StreamingAPI.md#StreamingHealthCheckApiV1StreamHealthGet) | **Get** /api/v1/stream/health | Streaming Health Check



## CloseStreamingSessionApiV1StreamSessionSessionIdClosePost

> interface{} CloseStreamingSessionApiV1StreamSessionSessionIdClosePost(ctx, sessionId).Execute()

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
	resp, r, err := apiClient.StreamingAPI.CloseStreamingSessionApiV1StreamSessionSessionIdClosePost(context.Background(), sessionId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingAPI.CloseStreamingSessionApiV1StreamSessionSessionIdClosePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CloseStreamingSessionApiV1StreamSessionSessionIdClosePost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StreamingAPI.CloseStreamingSessionApiV1StreamSessionSessionIdClosePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**sessionId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiCloseStreamingSessionApiV1StreamSessionSessionIdClosePostRequest struct via the builder pattern


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


## CreateStreamingSessionApiV1StreamSessionCreatePost

> interface{} CreateStreamingSessionApiV1StreamSessionCreatePost(ctx).SessionType(sessionType).BodyCreateStreamingSessionApiV1StreamSessionCreatePost(bodyCreateStreamingSessionApiV1StreamSessionCreatePost).Execute()

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
	bodyCreateStreamingSessionApiV1StreamSessionCreatePost := *openapiclient.NewBodyCreateStreamingSessionApiV1StreamSessionCreatePost() // BodyCreateStreamingSessionApiV1StreamSessionCreatePost |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StreamingAPI.CreateStreamingSessionApiV1StreamSessionCreatePost(context.Background()).SessionType(sessionType).BodyCreateStreamingSessionApiV1StreamSessionCreatePost(bodyCreateStreamingSessionApiV1StreamSessionCreatePost).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingAPI.CreateStreamingSessionApiV1StreamSessionCreatePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateStreamingSessionApiV1StreamSessionCreatePost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StreamingAPI.CreateStreamingSessionApiV1StreamSessionCreatePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateStreamingSessionApiV1StreamSessionCreatePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sessionType** | **string** |  | [default to &quot;websocket&quot;]
 **bodyCreateStreamingSessionApiV1StreamSessionCreatePost** | [**BodyCreateStreamingSessionApiV1StreamSessionCreatePost**](BodyCreateStreamingSessionApiV1StreamSessionCreatePost.md) |  | 

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


## GetStreamRunApiV1StreamRunsRunIdGet

> interface{} GetStreamRunApiV1StreamRunsRunIdGet(ctx, runId).Execute()

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
	resp, r, err := apiClient.StreamingAPI.GetStreamRunApiV1StreamRunsRunIdGet(context.Background(), runId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingAPI.GetStreamRunApiV1StreamRunsRunIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetStreamRunApiV1StreamRunsRunIdGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StreamingAPI.GetStreamRunApiV1StreamRunsRunIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**runId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetStreamRunApiV1StreamRunsRunIdGetRequest struct via the builder pattern


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


## GetStreamingStatsApiV1StreamStatsGet

> interface{} GetStreamingStatsApiV1StreamStatsGet(ctx).Execute()

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
	resp, r, err := apiClient.StreamingAPI.GetStreamingStatsApiV1StreamStatsGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingAPI.GetStreamingStatsApiV1StreamStatsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetStreamingStatsApiV1StreamStatsGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StreamingAPI.GetStreamingStatsApiV1StreamStatsGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetStreamingStatsApiV1StreamStatsGetRequest struct via the builder pattern


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


## SseEventsEndpointApiV1StreamEventsGet

> interface{} SseEventsEndpointApiV1StreamEventsGet(ctx).SessionId(sessionId).ApiKey(apiKey).Execute()

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
	resp, r, err := apiClient.StreamingAPI.SseEventsEndpointApiV1StreamEventsGet(context.Background()).SessionId(sessionId).ApiKey(apiKey).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingAPI.SseEventsEndpointApiV1StreamEventsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SseEventsEndpointApiV1StreamEventsGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StreamingAPI.SseEventsEndpointApiV1StreamEventsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiSseEventsEndpointApiV1StreamEventsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sessionId** | **string** |  | 
 **apiKey** | **string** |  | 

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


## StreamSigningApiV1StreamSignPost

> StreamSigningApiV1StreamSignPost(ctx).StreamSignRequest(streamSignRequest).Execute()

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
	r, err := apiClient.StreamingAPI.StreamSigningApiV1StreamSignPost(context.Background()).StreamSignRequest(streamSignRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingAPI.StreamSigningApiV1StreamSignPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiStreamSigningApiV1StreamSignPostRequest struct via the builder pattern


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


## StreamingHealthCheckApiV1StreamHealthGet

> interface{} StreamingHealthCheckApiV1StreamHealthGet(ctx).Execute()

Streaming Health Check



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
	resp, r, err := apiClient.StreamingAPI.StreamingHealthCheckApiV1StreamHealthGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingAPI.StreamingHealthCheckApiV1StreamHealthGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `StreamingHealthCheckApiV1StreamHealthGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `StreamingAPI.StreamingHealthCheckApiV1StreamHealthGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiStreamingHealthCheckApiV1StreamHealthGetRequest struct via the builder pattern


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

