# \SigningAPI

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**SignAdvancedApiV1SignAdvancedPost**](SigningAPI.md#SignAdvancedApiV1SignAdvancedPost) | **Post** /api/v1/sign/advanced | REMOVED - Use POST /sign with options instead
[**SignContentApiV1SignPost**](SigningAPI.md#SignContentApiV1SignPost) | **Post** /api/v1/sign | Sign content with C2PA manifest



## SignAdvancedApiV1SignAdvancedPost

> interface{} SignAdvancedApiV1SignAdvancedPost(ctx).Execute()

REMOVED - Use POST /sign with options instead



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
	resp, r, err := apiClient.SigningAPI.SignAdvancedApiV1SignAdvancedPost(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `SigningAPI.SignAdvancedApiV1SignAdvancedPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SignAdvancedApiV1SignAdvancedPost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `SigningAPI.SignAdvancedApiV1SignAdvancedPost`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiSignAdvancedApiV1SignAdvancedPostRequest struct via the builder pattern


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


## SignContentApiV1SignPost

> interface{} SignContentApiV1SignPost(ctx).UnifiedSignRequest(unifiedSignRequest).Execute()

Sign content with C2PA manifest



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
	unifiedSignRequest := *openapiclient.NewUnifiedSignRequest() // UnifiedSignRequest |

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.SigningAPI.SignContentApiV1SignPost(context.Background()).UnifiedSignRequest(unifiedSignRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `SigningAPI.SignContentApiV1SignPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SignContentApiV1SignPost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `SigningAPI.SignContentApiV1SignPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiSignContentApiV1SignPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **unifiedSignRequest** | [**UnifiedSignRequest**](UnifiedSignRequest.md) |  |

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
