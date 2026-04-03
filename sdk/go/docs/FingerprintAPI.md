# \FingerprintAPI

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**DetectFingerprintApiV1EnterpriseFingerprintDetectPost**](FingerprintAPI.md#DetectFingerprintApiV1EnterpriseFingerprintDetectPost) | **Post** /api/v1/enterprise/fingerprint/detect | Detect Fingerprint
[**EncodeFingerprintApiV1EnterpriseFingerprintEncodePost**](FingerprintAPI.md#EncodeFingerprintApiV1EnterpriseFingerprintEncodePost) | **Post** /api/v1/enterprise/fingerprint/encode | Encode Fingerprint



## DetectFingerprintApiV1EnterpriseFingerprintDetectPost

> FingerprintDetectResponse DetectFingerprintApiV1EnterpriseFingerprintDetectPost(ctx).FingerprintDetectRequest(fingerprintDetectRequest).Execute()

Detect Fingerprint



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
	fingerprintDetectRequest := *openapiclient.NewFingerprintDetectRequest("Text_example") // FingerprintDetectRequest |

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FingerprintAPI.DetectFingerprintApiV1EnterpriseFingerprintDetectPost(context.Background()).FingerprintDetectRequest(fingerprintDetectRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FingerprintAPI.DetectFingerprintApiV1EnterpriseFingerprintDetectPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DetectFingerprintApiV1EnterpriseFingerprintDetectPost`: FingerprintDetectResponse
	fmt.Fprintf(os.Stdout, "Response from `FingerprintAPI.DetectFingerprintApiV1EnterpriseFingerprintDetectPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiDetectFingerprintApiV1EnterpriseFingerprintDetectPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **fingerprintDetectRequest** | [**FingerprintDetectRequest**](FingerprintDetectRequest.md) |  |

### Return type

[**FingerprintDetectResponse**](FingerprintDetectResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## EncodeFingerprintApiV1EnterpriseFingerprintEncodePost

> FingerprintEncodeResponse EncodeFingerprintApiV1EnterpriseFingerprintEncodePost(ctx).FingerprintEncodeRequest(fingerprintEncodeRequest).Execute()

Encode Fingerprint



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
	fingerprintEncodeRequest := *openapiclient.NewFingerprintEncodeRequest("DocumentId_example", "Text_example") // FingerprintEncodeRequest |

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FingerprintAPI.EncodeFingerprintApiV1EnterpriseFingerprintEncodePost(context.Background()).FingerprintEncodeRequest(fingerprintEncodeRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FingerprintAPI.EncodeFingerprintApiV1EnterpriseFingerprintEncodePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `EncodeFingerprintApiV1EnterpriseFingerprintEncodePost`: FingerprintEncodeResponse
	fmt.Fprintf(os.Stdout, "Response from `FingerprintAPI.EncodeFingerprintApiV1EnterpriseFingerprintEncodePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiEncodeFingerprintApiV1EnterpriseFingerprintEncodePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **fingerprintEncodeRequest** | [**FingerprintEncodeRequest**](FingerprintEncodeRequest.md) |  |

### Return type

[**FingerprintEncodeResponse**](FingerprintEncodeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
