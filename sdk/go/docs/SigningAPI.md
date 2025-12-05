# \SigningAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**SignContentApiV1SignPost**](SigningAPI.md#SignContentApiV1SignPost) | **Post** /api/v1/sign | Sign Content



## SignContentApiV1SignPost

> SignResponse SignContentApiV1SignPost(ctx).SignRequest(signRequest).Execute()

Sign Content



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
	signRequest := *openapiclient.NewSignRequest("Text_example") // SignRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.SigningAPI.SignContentApiV1SignPost(context.Background()).SignRequest(signRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `SigningAPI.SignContentApiV1SignPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SignContentApiV1SignPost`: SignResponse
	fmt.Fprintf(os.Stdout, "Response from `SigningAPI.SignContentApiV1SignPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiSignContentApiV1SignPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **signRequest** | [**SignRequest**](SignRequest.md) |  | 

### Return type

[**SignResponse**](SignResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

