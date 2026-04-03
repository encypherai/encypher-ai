# \PublicC2PAAPI

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateManifestApiV1PublicC2paCreateManifestPost**](PublicC2PAAPI.md#CreateManifestApiV1PublicC2paCreateManifestPost) | **Post** /api/v1/public/c2pa/create-manifest | Create C2PA-like manifest JSON from plaintext (Public - Non-Cryptographic)
[**GetTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGet**](PublicC2PAAPI.md#GetTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGet) | **Get** /api/v1/public/c2pa/trust-anchors/{signer_id} | Lookup trust anchor for C2PA verification (Public)
[**ValidateManifestApiV1PublicC2paValidateManifestPost**](PublicC2PAAPI.md#ValidateManifestApiV1PublicC2paValidateManifestPost) | **Post** /api/v1/public/c2pa/validate-manifest | Validate C2PA-like manifest JSON (Public - Non-Cryptographic)



## CreateManifestApiV1PublicC2paCreateManifestPost

> CreateManifestResponse CreateManifestApiV1PublicC2paCreateManifestPost(ctx).CreateManifestRequest(createManifestRequest).Authorization(authorization).Execute()

Create C2PA-like manifest JSON from plaintext (Public - Non-Cryptographic)



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
	createManifestRequest := *openapiclient.NewCreateManifestRequest("Text_example") // CreateManifestRequest |
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PublicC2PAAPI.CreateManifestApiV1PublicC2paCreateManifestPost(context.Background()).CreateManifestRequest(createManifestRequest).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PublicC2PAAPI.CreateManifestApiV1PublicC2paCreateManifestPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateManifestApiV1PublicC2paCreateManifestPost`: CreateManifestResponse
	fmt.Fprintf(os.Stdout, "Response from `PublicC2PAAPI.CreateManifestApiV1PublicC2paCreateManifestPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateManifestApiV1PublicC2paCreateManifestPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **createManifestRequest** | [**CreateManifestRequest**](CreateManifestRequest.md) |  |
 **authorization** | **string** |  |

### Return type

[**CreateManifestResponse**](CreateManifestResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGet

> TrustAnchorResponse GetTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGet(ctx, signerId).Execute()

Lookup trust anchor for C2PA verification (Public)



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
	signerId := "signerId_example" // string | Signer identifier from manifest

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PublicC2PAAPI.GetTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGet(context.Background(), signerId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PublicC2PAAPI.GetTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGet`: TrustAnchorResponse
	fmt.Fprintf(os.Stdout, "Response from `PublicC2PAAPI.GetTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**signerId** | **string** | Signer identifier from manifest |

### Other Parameters

Other parameters are passed through a pointer to a apiGetTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**TrustAnchorResponse**](TrustAnchorResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ValidateManifestApiV1PublicC2paValidateManifestPost

> ValidateManifestResponse ValidateManifestApiV1PublicC2paValidateManifestPost(ctx).ValidateManifestRequest(validateManifestRequest).Authorization(authorization).Execute()

Validate C2PA-like manifest JSON (Public - Non-Cryptographic)



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
	validateManifestRequest := *openapiclient.NewValidateManifestRequest(map[string]interface{}{"key": interface{}(123)}) // ValidateManifestRequest |
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PublicC2PAAPI.ValidateManifestApiV1PublicC2paValidateManifestPost(context.Background()).ValidateManifestRequest(validateManifestRequest).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PublicC2PAAPI.ValidateManifestApiV1PublicC2paValidateManifestPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ValidateManifestApiV1PublicC2paValidateManifestPost`: ValidateManifestResponse
	fmt.Fprintf(os.Stdout, "Response from `PublicC2PAAPI.ValidateManifestApiV1PublicC2paValidateManifestPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiValidateManifestApiV1PublicC2paValidateManifestPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **validateManifestRequest** | [**ValidateManifestRequest**](ValidateManifestRequest.md) |  |
 **authorization** | **string** |  |

### Return type

[**ValidateManifestResponse**](ValidateManifestResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
