# \OnboardingAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GetCertificateStatusApiV1OnboardingCertificateStatusGet**](OnboardingAPI.md#GetCertificateStatusApiV1OnboardingCertificateStatusGet) | **Get** /api/v1/onboarding/certificate-status | Get Certificate Status
[**RequestCertificateApiV1OnboardingRequestCertificatePost**](OnboardingAPI.md#RequestCertificateApiV1OnboardingRequestCertificatePost) | **Post** /api/v1/onboarding/request-certificate | Request Certificate



## GetCertificateStatusApiV1OnboardingCertificateStatusGet

> interface{} GetCertificateStatusApiV1OnboardingCertificateStatusGet(ctx).Execute()

Get Certificate Status



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

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.OnboardingAPI.GetCertificateStatusApiV1OnboardingCertificateStatusGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `OnboardingAPI.GetCertificateStatusApiV1OnboardingCertificateStatusGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetCertificateStatusApiV1OnboardingCertificateStatusGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `OnboardingAPI.GetCertificateStatusApiV1OnboardingCertificateStatusGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetCertificateStatusApiV1OnboardingCertificateStatusGetRequest struct via the builder pattern


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


## RequestCertificateApiV1OnboardingRequestCertificatePost

> interface{} RequestCertificateApiV1OnboardingRequestCertificatePost(ctx).Execute()

Request Certificate



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

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.OnboardingAPI.RequestCertificateApiV1OnboardingRequestCertificatePost(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `OnboardingAPI.RequestCertificateApiV1OnboardingRequestCertificatePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RequestCertificateApiV1OnboardingRequestCertificatePost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `OnboardingAPI.RequestCertificateApiV1OnboardingRequestCertificatePost`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiRequestCertificateApiV1OnboardingRequestCertificatePostRequest struct via the builder pattern


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

