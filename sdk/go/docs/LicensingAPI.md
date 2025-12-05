# \LicensingAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateAgreementApiV1LicensingAgreementsPost**](LicensingAPI.md#CreateAgreementApiV1LicensingAgreementsPost) | **Post** /api/v1/licensing/agreements | Create Agreement
[**CreateAgreementApiV1LicensingAgreementsPost_0**](LicensingAPI.md#CreateAgreementApiV1LicensingAgreementsPost_0) | **Post** /api/v1/licensing/agreements | Create Agreement
[**CreateRevenueDistributionApiV1LicensingDistributionsPost**](LicensingAPI.md#CreateRevenueDistributionApiV1LicensingDistributionsPost) | **Post** /api/v1/licensing/distributions | Create Revenue Distribution
[**CreateRevenueDistributionApiV1LicensingDistributionsPost_0**](LicensingAPI.md#CreateRevenueDistributionApiV1LicensingDistributionsPost_0) | **Post** /api/v1/licensing/distributions | Create Revenue Distribution
[**GetAgreementApiV1LicensingAgreementsAgreementIdGet**](LicensingAPI.md#GetAgreementApiV1LicensingAgreementsAgreementIdGet) | **Get** /api/v1/licensing/agreements/{agreement_id} | Get Agreement
[**GetAgreementApiV1LicensingAgreementsAgreementIdGet_0**](LicensingAPI.md#GetAgreementApiV1LicensingAgreementsAgreementIdGet_0) | **Get** /api/v1/licensing/agreements/{agreement_id} | Get Agreement
[**GetDistributionApiV1LicensingDistributionsDistributionIdGet**](LicensingAPI.md#GetDistributionApiV1LicensingDistributionsDistributionIdGet) | **Get** /api/v1/licensing/distributions/{distribution_id} | Get Distribution
[**GetDistributionApiV1LicensingDistributionsDistributionIdGet_0**](LicensingAPI.md#GetDistributionApiV1LicensingDistributionsDistributionIdGet_0) | **Get** /api/v1/licensing/distributions/{distribution_id} | Get Distribution
[**ListAgreementsApiV1LicensingAgreementsGet**](LicensingAPI.md#ListAgreementsApiV1LicensingAgreementsGet) | **Get** /api/v1/licensing/agreements | List Agreements
[**ListAgreementsApiV1LicensingAgreementsGet_0**](LicensingAPI.md#ListAgreementsApiV1LicensingAgreementsGet_0) | **Get** /api/v1/licensing/agreements | List Agreements
[**ListAvailableContentApiV1LicensingContentGet**](LicensingAPI.md#ListAvailableContentApiV1LicensingContentGet) | **Get** /api/v1/licensing/content | List Available Content
[**ListAvailableContentApiV1LicensingContentGet_0**](LicensingAPI.md#ListAvailableContentApiV1LicensingContentGet_0) | **Get** /api/v1/licensing/content | List Available Content
[**ListDistributionsApiV1LicensingDistributionsGet**](LicensingAPI.md#ListDistributionsApiV1LicensingDistributionsGet) | **Get** /api/v1/licensing/distributions | List Distributions
[**ListDistributionsApiV1LicensingDistributionsGet_0**](LicensingAPI.md#ListDistributionsApiV1LicensingDistributionsGet_0) | **Get** /api/v1/licensing/distributions | List Distributions
[**ProcessPayoutsApiV1LicensingPayoutsPost**](LicensingAPI.md#ProcessPayoutsApiV1LicensingPayoutsPost) | **Post** /api/v1/licensing/payouts | Process Payouts
[**ProcessPayoutsApiV1LicensingPayoutsPost_0**](LicensingAPI.md#ProcessPayoutsApiV1LicensingPayoutsPost_0) | **Post** /api/v1/licensing/payouts | Process Payouts
[**TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete**](LicensingAPI.md#TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete) | **Delete** /api/v1/licensing/agreements/{agreement_id} | Terminate Agreement
[**TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete_0**](LicensingAPI.md#TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete_0) | **Delete** /api/v1/licensing/agreements/{agreement_id} | Terminate Agreement
[**TrackContentAccessApiV1LicensingTrackAccessPost**](LicensingAPI.md#TrackContentAccessApiV1LicensingTrackAccessPost) | **Post** /api/v1/licensing/track-access | Track Content Access
[**TrackContentAccessApiV1LicensingTrackAccessPost_0**](LicensingAPI.md#TrackContentAccessApiV1LicensingTrackAccessPost_0) | **Post** /api/v1/licensing/track-access | Track Content Access
[**UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch**](LicensingAPI.md#UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch) | **Patch** /api/v1/licensing/agreements/{agreement_id} | Update Agreement
[**UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch_0**](LicensingAPI.md#UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch_0) | **Patch** /api/v1/licensing/agreements/{agreement_id} | Update Agreement



## CreateAgreementApiV1LicensingAgreementsPost

> LicensingAgreementCreateResponse CreateAgreementApiV1LicensingAgreementsPost(ctx).LicensingAgreementCreate(licensingAgreementCreate).Execute()

Create Agreement



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
    "time"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	licensingAgreementCreate := *openapiclient.NewLicensingAgreementCreate("AgreementName_example", "AiCompanyName_example", "AiCompanyEmail_example", *openapiclient.NewTotalValue(), time.Now(), time.Now()) // LicensingAgreementCreate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.CreateAgreementApiV1LicensingAgreementsPost(context.Background()).LicensingAgreementCreate(licensingAgreementCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.CreateAgreementApiV1LicensingAgreementsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateAgreementApiV1LicensingAgreementsPost`: LicensingAgreementCreateResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.CreateAgreementApiV1LicensingAgreementsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateAgreementApiV1LicensingAgreementsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **licensingAgreementCreate** | [**LicensingAgreementCreate**](LicensingAgreementCreate.md) |  | 

### Return type

[**LicensingAgreementCreateResponse**](LicensingAgreementCreateResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateAgreementApiV1LicensingAgreementsPost_0

> LicensingAgreementCreateResponse CreateAgreementApiV1LicensingAgreementsPost_0(ctx).LicensingAgreementCreate(licensingAgreementCreate).Execute()

Create Agreement



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
    "time"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	licensingAgreementCreate := *openapiclient.NewLicensingAgreementCreate("AgreementName_example", "AiCompanyName_example", "AiCompanyEmail_example", *openapiclient.NewTotalValue(), time.Now(), time.Now()) // LicensingAgreementCreate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.CreateAgreementApiV1LicensingAgreementsPost_0(context.Background()).LicensingAgreementCreate(licensingAgreementCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.CreateAgreementApiV1LicensingAgreementsPost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateAgreementApiV1LicensingAgreementsPost_0`: LicensingAgreementCreateResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.CreateAgreementApiV1LicensingAgreementsPost_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateAgreementApiV1LicensingAgreementsPost_1Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **licensingAgreementCreate** | [**LicensingAgreementCreate**](LicensingAgreementCreate.md) |  | 

### Return type

[**LicensingAgreementCreateResponse**](LicensingAgreementCreateResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateRevenueDistributionApiV1LicensingDistributionsPost

> RevenueDistributionResponse CreateRevenueDistributionApiV1LicensingDistributionsPost(ctx).RevenueDistributionCreate(revenueDistributionCreate).Execute()

Create Revenue Distribution



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
    "time"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	revenueDistributionCreate := *openapiclient.NewRevenueDistributionCreate("AgreementId_example", time.Now(), time.Now()) // RevenueDistributionCreate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.CreateRevenueDistributionApiV1LicensingDistributionsPost(context.Background()).RevenueDistributionCreate(revenueDistributionCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.CreateRevenueDistributionApiV1LicensingDistributionsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateRevenueDistributionApiV1LicensingDistributionsPost`: RevenueDistributionResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.CreateRevenueDistributionApiV1LicensingDistributionsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateRevenueDistributionApiV1LicensingDistributionsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **revenueDistributionCreate** | [**RevenueDistributionCreate**](RevenueDistributionCreate.md) |  | 

### Return type

[**RevenueDistributionResponse**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateRevenueDistributionApiV1LicensingDistributionsPost_0

> RevenueDistributionResponse CreateRevenueDistributionApiV1LicensingDistributionsPost_0(ctx).RevenueDistributionCreate(revenueDistributionCreate).Execute()

Create Revenue Distribution



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
    "time"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	revenueDistributionCreate := *openapiclient.NewRevenueDistributionCreate("AgreementId_example", time.Now(), time.Now()) // RevenueDistributionCreate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.CreateRevenueDistributionApiV1LicensingDistributionsPost_0(context.Background()).RevenueDistributionCreate(revenueDistributionCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.CreateRevenueDistributionApiV1LicensingDistributionsPost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateRevenueDistributionApiV1LicensingDistributionsPost_0`: RevenueDistributionResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.CreateRevenueDistributionApiV1LicensingDistributionsPost_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateRevenueDistributionApiV1LicensingDistributionsPost_2Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **revenueDistributionCreate** | [**RevenueDistributionCreate**](RevenueDistributionCreate.md) |  | 

### Return type

[**RevenueDistributionResponse**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAgreementApiV1LicensingAgreementsAgreementIdGet

> LicensingAgreementResponse GetAgreementApiV1LicensingAgreementsAgreementIdGet(ctx, agreementId).Execute()

Get Agreement



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
	agreementId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.GetAgreementApiV1LicensingAgreementsAgreementIdGet(context.Background(), agreementId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.GetAgreementApiV1LicensingAgreementsAgreementIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAgreementApiV1LicensingAgreementsAgreementIdGet`: LicensingAgreementResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.GetAgreementApiV1LicensingAgreementsAgreementIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**agreementId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetAgreementApiV1LicensingAgreementsAgreementIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**LicensingAgreementResponse**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAgreementApiV1LicensingAgreementsAgreementIdGet_0

> LicensingAgreementResponse GetAgreementApiV1LicensingAgreementsAgreementIdGet_0(ctx, agreementId).Execute()

Get Agreement



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
	agreementId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.GetAgreementApiV1LicensingAgreementsAgreementIdGet_0(context.Background(), agreementId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.GetAgreementApiV1LicensingAgreementsAgreementIdGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAgreementApiV1LicensingAgreementsAgreementIdGet_0`: LicensingAgreementResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.GetAgreementApiV1LicensingAgreementsAgreementIdGet_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**agreementId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetAgreementApiV1LicensingAgreementsAgreementIdGet_3Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**LicensingAgreementResponse**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetDistributionApiV1LicensingDistributionsDistributionIdGet

> RevenueDistributionResponse GetDistributionApiV1LicensingDistributionsDistributionIdGet(ctx, distributionId).Execute()

Get Distribution



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
	distributionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.GetDistributionApiV1LicensingDistributionsDistributionIdGet(context.Background(), distributionId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.GetDistributionApiV1LicensingDistributionsDistributionIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetDistributionApiV1LicensingDistributionsDistributionIdGet`: RevenueDistributionResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.GetDistributionApiV1LicensingDistributionsDistributionIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**distributionId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetDistributionApiV1LicensingDistributionsDistributionIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**RevenueDistributionResponse**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetDistributionApiV1LicensingDistributionsDistributionIdGet_0

> RevenueDistributionResponse GetDistributionApiV1LicensingDistributionsDistributionIdGet_0(ctx, distributionId).Execute()

Get Distribution



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
	distributionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.GetDistributionApiV1LicensingDistributionsDistributionIdGet_0(context.Background(), distributionId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.GetDistributionApiV1LicensingDistributionsDistributionIdGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetDistributionApiV1LicensingDistributionsDistributionIdGet_0`: RevenueDistributionResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.GetDistributionApiV1LicensingDistributionsDistributionIdGet_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**distributionId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetDistributionApiV1LicensingDistributionsDistributionIdGet_4Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**RevenueDistributionResponse**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAgreementsApiV1LicensingAgreementsGet

> []LicensingAgreementResponse ListAgreementsApiV1LicensingAgreementsGet(ctx).Status(status).Limit(limit).Offset(offset).Execute()

List Agreements



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
	status := openapiclient.AgreementStatus("active") // AgreementStatus | Filter by status (optional)
	limit := int32(56) // int32 | Results per page (optional) (default to 100)
	offset := int32(56) // int32 | Pagination offset (optional) (default to 0)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.ListAgreementsApiV1LicensingAgreementsGet(context.Background()).Status(status).Limit(limit).Offset(offset).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.ListAgreementsApiV1LicensingAgreementsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAgreementsApiV1LicensingAgreementsGet`: []LicensingAgreementResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.ListAgreementsApiV1LicensingAgreementsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAgreementsApiV1LicensingAgreementsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | [**AgreementStatus**](AgreementStatus.md) | Filter by status | 
 **limit** | **int32** | Results per page | [default to 100]
 **offset** | **int32** | Pagination offset | [default to 0]

### Return type

[**[]LicensingAgreementResponse**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAgreementsApiV1LicensingAgreementsGet_0

> []LicensingAgreementResponse ListAgreementsApiV1LicensingAgreementsGet_0(ctx).Status(status).Limit(limit).Offset(offset).Execute()

List Agreements



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
	status := openapiclient.AgreementStatus("active") // AgreementStatus | Filter by status (optional)
	limit := int32(56) // int32 | Results per page (optional) (default to 100)
	offset := int32(56) // int32 | Pagination offset (optional) (default to 0)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.ListAgreementsApiV1LicensingAgreementsGet_0(context.Background()).Status(status).Limit(limit).Offset(offset).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.ListAgreementsApiV1LicensingAgreementsGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAgreementsApiV1LicensingAgreementsGet_0`: []LicensingAgreementResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.ListAgreementsApiV1LicensingAgreementsGet_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAgreementsApiV1LicensingAgreementsGet_5Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | [**AgreementStatus**](AgreementStatus.md) | Filter by status | 
 **limit** | **int32** | Results per page | [default to 100]
 **offset** | **int32** | Pagination offset | [default to 0]

### Return type

[**[]LicensingAgreementResponse**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAvailableContentApiV1LicensingContentGet

> ContentListResponse ListAvailableContentApiV1LicensingContentGet(ctx).ContentType(contentType).MinWordCount(minWordCount).Limit(limit).Offset(offset).Execute()

List Available Content



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
	contentType := "contentType_example" // string | Filter by content type (optional)
	minWordCount := int32(56) // int32 | Minimum word count (optional)
	limit := int32(56) // int32 | Results per page (optional) (default to 100)
	offset := int32(56) // int32 | Pagination offset (optional) (default to 0)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.ListAvailableContentApiV1LicensingContentGet(context.Background()).ContentType(contentType).MinWordCount(minWordCount).Limit(limit).Offset(offset).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.ListAvailableContentApiV1LicensingContentGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAvailableContentApiV1LicensingContentGet`: ContentListResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.ListAvailableContentApiV1LicensingContentGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAvailableContentApiV1LicensingContentGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **contentType** | **string** | Filter by content type | 
 **minWordCount** | **int32** | Minimum word count | 
 **limit** | **int32** | Results per page | [default to 100]
 **offset** | **int32** | Pagination offset | [default to 0]

### Return type

[**ContentListResponse**](ContentListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAvailableContentApiV1LicensingContentGet_0

> ContentListResponse ListAvailableContentApiV1LicensingContentGet_0(ctx).ContentType(contentType).MinWordCount(minWordCount).Limit(limit).Offset(offset).Execute()

List Available Content



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
	contentType := "contentType_example" // string | Filter by content type (optional)
	minWordCount := int32(56) // int32 | Minimum word count (optional)
	limit := int32(56) // int32 | Results per page (optional) (default to 100)
	offset := int32(56) // int32 | Pagination offset (optional) (default to 0)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.ListAvailableContentApiV1LicensingContentGet_0(context.Background()).ContentType(contentType).MinWordCount(minWordCount).Limit(limit).Offset(offset).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.ListAvailableContentApiV1LicensingContentGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAvailableContentApiV1LicensingContentGet_0`: ContentListResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.ListAvailableContentApiV1LicensingContentGet_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAvailableContentApiV1LicensingContentGet_6Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **contentType** | **string** | Filter by content type | 
 **minWordCount** | **int32** | Minimum word count | 
 **limit** | **int32** | Results per page | [default to 100]
 **offset** | **int32** | Pagination offset | [default to 0]

### Return type

[**ContentListResponse**](ContentListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListDistributionsApiV1LicensingDistributionsGet

> []RevenueDistributionResponse ListDistributionsApiV1LicensingDistributionsGet(ctx).AgreementId(agreementId).Status(status).Limit(limit).Offset(offset).Execute()

List Distributions



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
	agreementId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string | Filter by agreement (optional)
	status := openapiclient.DistributionStatus("pending") // DistributionStatus | Filter by status (optional)
	limit := int32(56) // int32 | Results per page (optional) (default to 100)
	offset := int32(56) // int32 | Pagination offset (optional) (default to 0)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.ListDistributionsApiV1LicensingDistributionsGet(context.Background()).AgreementId(agreementId).Status(status).Limit(limit).Offset(offset).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.ListDistributionsApiV1LicensingDistributionsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListDistributionsApiV1LicensingDistributionsGet`: []RevenueDistributionResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.ListDistributionsApiV1LicensingDistributionsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListDistributionsApiV1LicensingDistributionsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agreementId** | **string** | Filter by agreement | 
 **status** | [**DistributionStatus**](DistributionStatus.md) | Filter by status | 
 **limit** | **int32** | Results per page | [default to 100]
 **offset** | **int32** | Pagination offset | [default to 0]

### Return type

[**[]RevenueDistributionResponse**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListDistributionsApiV1LicensingDistributionsGet_0

> []RevenueDistributionResponse ListDistributionsApiV1LicensingDistributionsGet_0(ctx).AgreementId(agreementId).Status(status).Limit(limit).Offset(offset).Execute()

List Distributions



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
	agreementId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string | Filter by agreement (optional)
	status := openapiclient.DistributionStatus("pending") // DistributionStatus | Filter by status (optional)
	limit := int32(56) // int32 | Results per page (optional) (default to 100)
	offset := int32(56) // int32 | Pagination offset (optional) (default to 0)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.ListDistributionsApiV1LicensingDistributionsGet_0(context.Background()).AgreementId(agreementId).Status(status).Limit(limit).Offset(offset).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.ListDistributionsApiV1LicensingDistributionsGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListDistributionsApiV1LicensingDistributionsGet_0`: []RevenueDistributionResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.ListDistributionsApiV1LicensingDistributionsGet_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListDistributionsApiV1LicensingDistributionsGet_7Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agreementId** | **string** | Filter by agreement | 
 **status** | [**DistributionStatus**](DistributionStatus.md) | Filter by status | 
 **limit** | **int32** | Results per page | [default to 100]
 **offset** | **int32** | Pagination offset | [default to 0]

### Return type

[**[]RevenueDistributionResponse**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ProcessPayoutsApiV1LicensingPayoutsPost

> PayoutResponse ProcessPayoutsApiV1LicensingPayoutsPost(ctx).PayoutCreate(payoutCreate).Execute()

Process Payouts



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
	payoutCreate := *openapiclient.NewPayoutCreate("DistributionId_example") // PayoutCreate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.ProcessPayoutsApiV1LicensingPayoutsPost(context.Background()).PayoutCreate(payoutCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.ProcessPayoutsApiV1LicensingPayoutsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ProcessPayoutsApiV1LicensingPayoutsPost`: PayoutResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.ProcessPayoutsApiV1LicensingPayoutsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiProcessPayoutsApiV1LicensingPayoutsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **payoutCreate** | [**PayoutCreate**](PayoutCreate.md) |  | 

### Return type

[**PayoutResponse**](PayoutResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ProcessPayoutsApiV1LicensingPayoutsPost_0

> PayoutResponse ProcessPayoutsApiV1LicensingPayoutsPost_0(ctx).PayoutCreate(payoutCreate).Execute()

Process Payouts



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
	payoutCreate := *openapiclient.NewPayoutCreate("DistributionId_example") // PayoutCreate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.ProcessPayoutsApiV1LicensingPayoutsPost_0(context.Background()).PayoutCreate(payoutCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.ProcessPayoutsApiV1LicensingPayoutsPost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ProcessPayoutsApiV1LicensingPayoutsPost_0`: PayoutResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.ProcessPayoutsApiV1LicensingPayoutsPost_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiProcessPayoutsApiV1LicensingPayoutsPost_8Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **payoutCreate** | [**PayoutCreate**](PayoutCreate.md) |  | 

### Return type

[**PayoutResponse**](PayoutResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete

> SuccessResponse TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete(ctx, agreementId).Execute()

Terminate Agreement



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
	agreementId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete(context.Background(), agreementId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete`: SuccessResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**agreementId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiTerminateAgreementApiV1LicensingAgreementsAgreementIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**SuccessResponse**](SuccessResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete_0

> SuccessResponse TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete_0(ctx, agreementId).Execute()

Terminate Agreement



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
	agreementId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete_0(context.Background(), agreementId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete_0`: SuccessResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.TerminateAgreementApiV1LicensingAgreementsAgreementIdDelete_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**agreementId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiTerminateAgreementApiV1LicensingAgreementsAgreementIdDelete_9Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**SuccessResponse**](SuccessResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## TrackContentAccessApiV1LicensingTrackAccessPost

> ContentAccessLogResponse TrackContentAccessApiV1LicensingTrackAccessPost(ctx).ContentAccessTrack(contentAccessTrack).Execute()

Track Content Access



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
	contentAccessTrack := *openapiclient.NewContentAccessTrack(int32(123)) // ContentAccessTrack | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.TrackContentAccessApiV1LicensingTrackAccessPost(context.Background()).ContentAccessTrack(contentAccessTrack).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.TrackContentAccessApiV1LicensingTrackAccessPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `TrackContentAccessApiV1LicensingTrackAccessPost`: ContentAccessLogResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.TrackContentAccessApiV1LicensingTrackAccessPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiTrackContentAccessApiV1LicensingTrackAccessPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **contentAccessTrack** | [**ContentAccessTrack**](ContentAccessTrack.md) |  | 

### Return type

[**ContentAccessLogResponse**](ContentAccessLogResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## TrackContentAccessApiV1LicensingTrackAccessPost_0

> ContentAccessLogResponse TrackContentAccessApiV1LicensingTrackAccessPost_0(ctx).ContentAccessTrack(contentAccessTrack).Execute()

Track Content Access



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
	contentAccessTrack := *openapiclient.NewContentAccessTrack(int32(123)) // ContentAccessTrack | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.TrackContentAccessApiV1LicensingTrackAccessPost_0(context.Background()).ContentAccessTrack(contentAccessTrack).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.TrackContentAccessApiV1LicensingTrackAccessPost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `TrackContentAccessApiV1LicensingTrackAccessPost_0`: ContentAccessLogResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.TrackContentAccessApiV1LicensingTrackAccessPost_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiTrackContentAccessApiV1LicensingTrackAccessPost_10Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **contentAccessTrack** | [**ContentAccessTrack**](ContentAccessTrack.md) |  | 

### Return type

[**ContentAccessLogResponse**](ContentAccessLogResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch

> LicensingAgreementResponse UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch(ctx, agreementId).LicensingAgreementUpdate(licensingAgreementUpdate).Execute()

Update Agreement



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
	agreementId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string | 
	licensingAgreementUpdate := *openapiclient.NewLicensingAgreementUpdate() // LicensingAgreementUpdate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch(context.Background(), agreementId).LicensingAgreementUpdate(licensingAgreementUpdate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch`: LicensingAgreementResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**agreementId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateAgreementApiV1LicensingAgreementsAgreementIdPatchRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **licensingAgreementUpdate** | [**LicensingAgreementUpdate**](LicensingAgreementUpdate.md) |  | 

### Return type

[**LicensingAgreementResponse**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch_0

> LicensingAgreementResponse UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch_0(ctx, agreementId).LicensingAgreementUpdate(licensingAgreementUpdate).Execute()

Update Agreement



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
	agreementId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string | 
	licensingAgreementUpdate := *openapiclient.NewLicensingAgreementUpdate() // LicensingAgreementUpdate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LicensingAPI.UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch_0(context.Background(), agreementId).LicensingAgreementUpdate(licensingAgreementUpdate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LicensingAPI.UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch_0`: LicensingAgreementResponse
	fmt.Fprintf(os.Stdout, "Response from `LicensingAPI.UpdateAgreementApiV1LicensingAgreementsAgreementIdPatch_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**agreementId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateAgreementApiV1LicensingAgreementsAgreementIdPatch_11Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **licensingAgreementUpdate** | [**LicensingAgreementUpdate**](LicensingAgreementUpdate.md) |  | 

### Return type

[**LicensingAgreementResponse**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

