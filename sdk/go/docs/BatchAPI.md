# \BatchAPI

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**BatchSignApiV1BatchSignPost**](BatchAPI.md#BatchSignApiV1BatchSignPost) | **Post** /api/v1/batch/sign | Batch Sign
[**BatchVerifyApiV1BatchVerifyPost**](BatchAPI.md#BatchVerifyApiV1BatchVerifyPost) | **Post** /api/v1/batch/verify | Batch Verify



## BatchSignApiV1BatchSignPost

> BatchResponseEnvelope BatchSignApiV1BatchSignPost(ctx).BatchSignRequest(batchSignRequest).Execute()

Batch Sign



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
	batchSignRequest := *openapiclient.NewBatchSignRequest("Mode_example", "IdempotencyKey_example", []openapiclient.BatchItemPayload{*openapiclient.NewBatchItemPayload("DocumentId_example", "Text_example")}) // BatchSignRequest |

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BatchAPI.BatchSignApiV1BatchSignPost(context.Background()).BatchSignRequest(batchSignRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BatchAPI.BatchSignApiV1BatchSignPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `BatchSignApiV1BatchSignPost`: BatchResponseEnvelope
	fmt.Fprintf(os.Stdout, "Response from `BatchAPI.BatchSignApiV1BatchSignPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiBatchSignApiV1BatchSignPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batchSignRequest** | [**BatchSignRequest**](BatchSignRequest.md) |  |

### Return type

[**BatchResponseEnvelope**](BatchResponseEnvelope.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## BatchVerifyApiV1BatchVerifyPost

> BatchResponseEnvelope BatchVerifyApiV1BatchVerifyPost(ctx).AppSchemasBatchBatchVerifyRequest(appSchemasBatchBatchVerifyRequest).Execute()

Batch Verify



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
	appSchemasBatchBatchVerifyRequest := *openapiclient.NewAppSchemasBatchBatchVerifyRequest("Mode_example", "IdempotencyKey_example", []openapiclient.BatchItemPayload{*openapiclient.NewBatchItemPayload("DocumentId_example", "Text_example")}) // AppSchemasBatchBatchVerifyRequest |

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BatchAPI.BatchVerifyApiV1BatchVerifyPost(context.Background()).AppSchemasBatchBatchVerifyRequest(appSchemasBatchBatchVerifyRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BatchAPI.BatchVerifyApiV1BatchVerifyPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `BatchVerifyApiV1BatchVerifyPost`: BatchResponseEnvelope
	fmt.Fprintf(os.Stdout, "Response from `BatchAPI.BatchVerifyApiV1BatchVerifyPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiBatchVerifyApiV1BatchVerifyPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **appSchemasBatchBatchVerifyRequest** | [**AppSchemasBatchBatchVerifyRequest**](AppSchemasBatchBatchVerifyRequest.md) |  |

### Return type

[**BatchResponseEnvelope**](BatchResponseEnvelope.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
