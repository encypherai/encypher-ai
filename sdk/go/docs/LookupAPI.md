# \LookupAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**LookupSentenceApiV1LookupPost**](LookupAPI.md#LookupSentenceApiV1LookupPost) | **Post** /api/v1/lookup | Lookup Sentence



## LookupSentenceApiV1LookupPost

> LookupResponse LookupSentenceApiV1LookupPost(ctx).LookupRequest(lookupRequest).Execute()

Lookup Sentence



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
	lookupRequest := *openapiclient.NewLookupRequest("SentenceText_example") // LookupRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LookupAPI.LookupSentenceApiV1LookupPost(context.Background()).LookupRequest(lookupRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LookupAPI.LookupSentenceApiV1LookupPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `LookupSentenceApiV1LookupPost`: LookupResponse
	fmt.Fprintf(os.Stdout, "Response from `LookupAPI.LookupSentenceApiV1LookupPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiLookupSentenceApiV1LookupPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lookupRequest** | [**LookupRequest**](LookupRequest.md) |  | 

### Return type

[**LookupResponse**](LookupResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

