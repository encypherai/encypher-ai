# \MultiSourceAttributionAPI

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**MultiSourceLookupApiV1EnterpriseAttributionMultiSourcePost**](MultiSourceAttributionAPI.md#MultiSourceLookupApiV1EnterpriseAttributionMultiSourcePost) | **Post** /api/v1/enterprise/attribution/multi-source | Multi Source Lookup



## MultiSourceLookupApiV1EnterpriseAttributionMultiSourcePost

> MultiSourceLookupResponse MultiSourceLookupApiV1EnterpriseAttributionMultiSourcePost(ctx).MultiSourceLookupRequest(multiSourceLookupRequest).Execute()

Multi Source Lookup



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
	multiSourceLookupRequest := *openapiclient.NewMultiSourceLookupRequest("TextSegment_example") // MultiSourceLookupRequest |

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.MultiSourceAttributionAPI.MultiSourceLookupApiV1EnterpriseAttributionMultiSourcePost(context.Background()).MultiSourceLookupRequest(multiSourceLookupRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `MultiSourceAttributionAPI.MultiSourceLookupApiV1EnterpriseAttributionMultiSourcePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `MultiSourceLookupApiV1EnterpriseAttributionMultiSourcePost`: MultiSourceLookupResponse
	fmt.Fprintf(os.Stdout, "Response from `MultiSourceAttributionAPI.MultiSourceLookupApiV1EnterpriseAttributionMultiSourcePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiMultiSourceLookupApiV1EnterpriseAttributionMultiSourcePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **multiSourceLookupRequest** | [**MultiSourceLookupRequest**](MultiSourceLookupRequest.md) |  |

### Return type

[**MultiSourceLookupResponse**](MultiSourceLookupResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
