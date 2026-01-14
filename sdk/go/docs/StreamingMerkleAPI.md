# \StreamingMerkleAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**AddSegmentToSessionApiV1EnterpriseStreamMerkleSegmentPost**](StreamingMerkleAPI.md#AddSegmentToSessionApiV1EnterpriseStreamMerkleSegmentPost) | **Post** /api/v1/enterprise/stream/merkle/segment | Add Segment To Session
[**FinalizeStreamingSessionApiV1EnterpriseStreamMerkleFinalizePost**](StreamingMerkleAPI.md#FinalizeStreamingSessionApiV1EnterpriseStreamMerkleFinalizePost) | **Post** /api/v1/enterprise/stream/merkle/finalize | Finalize Streaming Session
[**GetSessionStatusApiV1EnterpriseStreamMerkleStatusPost**](StreamingMerkleAPI.md#GetSessionStatusApiV1EnterpriseStreamMerkleStatusPost) | **Post** /api/v1/enterprise/stream/merkle/status | Get Session Status
[**StartStreamingMerkleSessionApiV1EnterpriseStreamMerkleStartPost**](StreamingMerkleAPI.md#StartStreamingMerkleSessionApiV1EnterpriseStreamMerkleStartPost) | **Post** /api/v1/enterprise/stream/merkle/start | Start Streaming Merkle Session



## AddSegmentToSessionApiV1EnterpriseStreamMerkleSegmentPost

> StreamMerkleSegmentResponse AddSegmentToSessionApiV1EnterpriseStreamMerkleSegmentPost(ctx).StreamMerkleSegmentRequest(streamMerkleSegmentRequest).Execute()

Add Segment To Session



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
	streamMerkleSegmentRequest := *openapiclient.NewStreamMerkleSegmentRequest("SessionId_example", "SegmentText_example") // StreamMerkleSegmentRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StreamingMerkleAPI.AddSegmentToSessionApiV1EnterpriseStreamMerkleSegmentPost(context.Background()).StreamMerkleSegmentRequest(streamMerkleSegmentRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingMerkleAPI.AddSegmentToSessionApiV1EnterpriseStreamMerkleSegmentPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `AddSegmentToSessionApiV1EnterpriseStreamMerkleSegmentPost`: StreamMerkleSegmentResponse
	fmt.Fprintf(os.Stdout, "Response from `StreamingMerkleAPI.AddSegmentToSessionApiV1EnterpriseStreamMerkleSegmentPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiAddSegmentToSessionApiV1EnterpriseStreamMerkleSegmentPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **streamMerkleSegmentRequest** | [**StreamMerkleSegmentRequest**](StreamMerkleSegmentRequest.md) |  | 

### Return type

[**StreamMerkleSegmentResponse**](StreamMerkleSegmentResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## FinalizeStreamingSessionApiV1EnterpriseStreamMerkleFinalizePost

> StreamMerkleFinalizeResponse FinalizeStreamingSessionApiV1EnterpriseStreamMerkleFinalizePost(ctx).StreamMerkleFinalizeRequest(streamMerkleFinalizeRequest).Execute()

Finalize Streaming Session



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
	streamMerkleFinalizeRequest := *openapiclient.NewStreamMerkleFinalizeRequest("SessionId_example") // StreamMerkleFinalizeRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StreamingMerkleAPI.FinalizeStreamingSessionApiV1EnterpriseStreamMerkleFinalizePost(context.Background()).StreamMerkleFinalizeRequest(streamMerkleFinalizeRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingMerkleAPI.FinalizeStreamingSessionApiV1EnterpriseStreamMerkleFinalizePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `FinalizeStreamingSessionApiV1EnterpriseStreamMerkleFinalizePost`: StreamMerkleFinalizeResponse
	fmt.Fprintf(os.Stdout, "Response from `StreamingMerkleAPI.FinalizeStreamingSessionApiV1EnterpriseStreamMerkleFinalizePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiFinalizeStreamingSessionApiV1EnterpriseStreamMerkleFinalizePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **streamMerkleFinalizeRequest** | [**StreamMerkleFinalizeRequest**](StreamMerkleFinalizeRequest.md) |  | 

### Return type

[**StreamMerkleFinalizeResponse**](StreamMerkleFinalizeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetSessionStatusApiV1EnterpriseStreamMerkleStatusPost

> StreamMerkleStatusResponse GetSessionStatusApiV1EnterpriseStreamMerkleStatusPost(ctx).StreamMerkleStatusRequest(streamMerkleStatusRequest).Execute()

Get Session Status



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
	streamMerkleStatusRequest := *openapiclient.NewStreamMerkleStatusRequest("SessionId_example") // StreamMerkleStatusRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StreamingMerkleAPI.GetSessionStatusApiV1EnterpriseStreamMerkleStatusPost(context.Background()).StreamMerkleStatusRequest(streamMerkleStatusRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingMerkleAPI.GetSessionStatusApiV1EnterpriseStreamMerkleStatusPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetSessionStatusApiV1EnterpriseStreamMerkleStatusPost`: StreamMerkleStatusResponse
	fmt.Fprintf(os.Stdout, "Response from `StreamingMerkleAPI.GetSessionStatusApiV1EnterpriseStreamMerkleStatusPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetSessionStatusApiV1EnterpriseStreamMerkleStatusPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **streamMerkleStatusRequest** | [**StreamMerkleStatusRequest**](StreamMerkleStatusRequest.md) |  | 

### Return type

[**StreamMerkleStatusResponse**](StreamMerkleStatusResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## StartStreamingMerkleSessionApiV1EnterpriseStreamMerkleStartPost

> StreamMerkleStartResponse StartStreamingMerkleSessionApiV1EnterpriseStreamMerkleStartPost(ctx).StreamMerkleStartRequest(streamMerkleStartRequest).Execute()

Start Streaming Merkle Session



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
	streamMerkleStartRequest := *openapiclient.NewStreamMerkleStartRequest("DocumentId_example") // StreamMerkleStartRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StreamingMerkleAPI.StartStreamingMerkleSessionApiV1EnterpriseStreamMerkleStartPost(context.Background()).StreamMerkleStartRequest(streamMerkleStartRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StreamingMerkleAPI.StartStreamingMerkleSessionApiV1EnterpriseStreamMerkleStartPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `StartStreamingMerkleSessionApiV1EnterpriseStreamMerkleStartPost`: StreamMerkleStartResponse
	fmt.Fprintf(os.Stdout, "Response from `StreamingMerkleAPI.StartStreamingMerkleSessionApiV1EnterpriseStreamMerkleStartPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiStartStreamingMerkleSessionApiV1EnterpriseStreamMerkleStartPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **streamMerkleStartRequest** | [**StreamMerkleStartRequest**](StreamMerkleStartRequest.md) |  | 

### Return type

[**StreamMerkleStartResponse**](StreamMerkleStartResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

