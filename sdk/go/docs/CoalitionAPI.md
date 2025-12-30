# \CoalitionAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GetCoalitionDashboardApiV1CoalitionDashboardGet**](CoalitionAPI.md#GetCoalitionDashboardApiV1CoalitionDashboardGet) | **Get** /api/v1/coalition/dashboard | Get Coalition Dashboard
[**GetCoalitionDashboardApiV1CoalitionDashboardGet_0**](CoalitionAPI.md#GetCoalitionDashboardApiV1CoalitionDashboardGet_0) | **Get** /api/v1/coalition/dashboard | Get Coalition Dashboard
[**GetContentStatsApiV1CoalitionContentStatsGet**](CoalitionAPI.md#GetContentStatsApiV1CoalitionContentStatsGet) | **Get** /api/v1/coalition/content-stats | Get Content Stats
[**GetContentStatsApiV1CoalitionContentStatsGet_0**](CoalitionAPI.md#GetContentStatsApiV1CoalitionContentStatsGet_0) | **Get** /api/v1/coalition/content-stats | Get Content Stats
[**GetEarningsHistoryApiV1CoalitionEarningsGet**](CoalitionAPI.md#GetEarningsHistoryApiV1CoalitionEarningsGet) | **Get** /api/v1/coalition/earnings | Get Earnings History
[**GetEarningsHistoryApiV1CoalitionEarningsGet_0**](CoalitionAPI.md#GetEarningsHistoryApiV1CoalitionEarningsGet_0) | **Get** /api/v1/coalition/earnings | Get Earnings History
[**OptInToCoalitionApiV1CoalitionOptInPost**](CoalitionAPI.md#OptInToCoalitionApiV1CoalitionOptInPost) | **Post** /api/v1/coalition/opt-in | Opt In To Coalition
[**OptInToCoalitionApiV1CoalitionOptInPost_0**](CoalitionAPI.md#OptInToCoalitionApiV1CoalitionOptInPost_0) | **Post** /api/v1/coalition/opt-in | Opt In To Coalition
[**OptOutOfCoalitionApiV1CoalitionOptOutPost**](CoalitionAPI.md#OptOutOfCoalitionApiV1CoalitionOptOutPost) | **Post** /api/v1/coalition/opt-out | Opt Out Of Coalition
[**OptOutOfCoalitionApiV1CoalitionOptOutPost_0**](CoalitionAPI.md#OptOutOfCoalitionApiV1CoalitionOptOutPost_0) | **Post** /api/v1/coalition/opt-out | Opt Out Of Coalition



## GetCoalitionDashboardApiV1CoalitionDashboardGet

> CoalitionDashboardResponse GetCoalitionDashboardApiV1CoalitionDashboardGet(ctx).Execute()

Get Coalition Dashboard



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
	resp, r, err := apiClient.CoalitionAPI.GetCoalitionDashboardApiV1CoalitionDashboardGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CoalitionAPI.GetCoalitionDashboardApiV1CoalitionDashboardGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetCoalitionDashboardApiV1CoalitionDashboardGet`: CoalitionDashboardResponse
	fmt.Fprintf(os.Stdout, "Response from `CoalitionAPI.GetCoalitionDashboardApiV1CoalitionDashboardGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetCoalitionDashboardApiV1CoalitionDashboardGetRequest struct via the builder pattern


### Return type

[**CoalitionDashboardResponse**](CoalitionDashboardResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetCoalitionDashboardApiV1CoalitionDashboardGet_0

> CoalitionDashboardResponse GetCoalitionDashboardApiV1CoalitionDashboardGet_0(ctx).Execute()

Get Coalition Dashboard



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
	resp, r, err := apiClient.CoalitionAPI.GetCoalitionDashboardApiV1CoalitionDashboardGet_0(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CoalitionAPI.GetCoalitionDashboardApiV1CoalitionDashboardGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetCoalitionDashboardApiV1CoalitionDashboardGet_0`: CoalitionDashboardResponse
	fmt.Fprintf(os.Stdout, "Response from `CoalitionAPI.GetCoalitionDashboardApiV1CoalitionDashboardGet_0`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetCoalitionDashboardApiV1CoalitionDashboardGet_1Request struct via the builder pattern


### Return type

[**CoalitionDashboardResponse**](CoalitionDashboardResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetContentStatsApiV1CoalitionContentStatsGet

> interface{} GetContentStatsApiV1CoalitionContentStatsGet(ctx).Months(months).Execute()

Get Content Stats



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
	months := int32(56) // int32 |  (optional) (default to 12)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.CoalitionAPI.GetContentStatsApiV1CoalitionContentStatsGet(context.Background()).Months(months).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CoalitionAPI.GetContentStatsApiV1CoalitionContentStatsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetContentStatsApiV1CoalitionContentStatsGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `CoalitionAPI.GetContentStatsApiV1CoalitionContentStatsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetContentStatsApiV1CoalitionContentStatsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **months** | **int32** |  | [default to 12]

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


## GetContentStatsApiV1CoalitionContentStatsGet_0

> interface{} GetContentStatsApiV1CoalitionContentStatsGet_0(ctx).Months(months).Execute()

Get Content Stats



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
	months := int32(56) // int32 |  (optional) (default to 12)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.CoalitionAPI.GetContentStatsApiV1CoalitionContentStatsGet_0(context.Background()).Months(months).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CoalitionAPI.GetContentStatsApiV1CoalitionContentStatsGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetContentStatsApiV1CoalitionContentStatsGet_0`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `CoalitionAPI.GetContentStatsApiV1CoalitionContentStatsGet_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetContentStatsApiV1CoalitionContentStatsGet_2Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **months** | **int32** |  | [default to 12]

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


## GetEarningsHistoryApiV1CoalitionEarningsGet

> interface{} GetEarningsHistoryApiV1CoalitionEarningsGet(ctx).Months(months).Execute()

Get Earnings History



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
	months := int32(56) // int32 |  (optional) (default to 12)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.CoalitionAPI.GetEarningsHistoryApiV1CoalitionEarningsGet(context.Background()).Months(months).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CoalitionAPI.GetEarningsHistoryApiV1CoalitionEarningsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetEarningsHistoryApiV1CoalitionEarningsGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `CoalitionAPI.GetEarningsHistoryApiV1CoalitionEarningsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetEarningsHistoryApiV1CoalitionEarningsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **months** | **int32** |  | [default to 12]

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


## GetEarningsHistoryApiV1CoalitionEarningsGet_0

> interface{} GetEarningsHistoryApiV1CoalitionEarningsGet_0(ctx).Months(months).Execute()

Get Earnings History



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
	months := int32(56) // int32 |  (optional) (default to 12)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.CoalitionAPI.GetEarningsHistoryApiV1CoalitionEarningsGet_0(context.Background()).Months(months).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CoalitionAPI.GetEarningsHistoryApiV1CoalitionEarningsGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetEarningsHistoryApiV1CoalitionEarningsGet_0`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `CoalitionAPI.GetEarningsHistoryApiV1CoalitionEarningsGet_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetEarningsHistoryApiV1CoalitionEarningsGet_3Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **months** | **int32** |  | [default to 12]

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


## OptInToCoalitionApiV1CoalitionOptInPost

> interface{} OptInToCoalitionApiV1CoalitionOptInPost(ctx).Execute()

Opt In To Coalition



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
	resp, r, err := apiClient.CoalitionAPI.OptInToCoalitionApiV1CoalitionOptInPost(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CoalitionAPI.OptInToCoalitionApiV1CoalitionOptInPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `OptInToCoalitionApiV1CoalitionOptInPost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `CoalitionAPI.OptInToCoalitionApiV1CoalitionOptInPost`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiOptInToCoalitionApiV1CoalitionOptInPostRequest struct via the builder pattern


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


## OptInToCoalitionApiV1CoalitionOptInPost_0

> interface{} OptInToCoalitionApiV1CoalitionOptInPost_0(ctx).Execute()

Opt In To Coalition



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
	resp, r, err := apiClient.CoalitionAPI.OptInToCoalitionApiV1CoalitionOptInPost_0(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CoalitionAPI.OptInToCoalitionApiV1CoalitionOptInPost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `OptInToCoalitionApiV1CoalitionOptInPost_0`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `CoalitionAPI.OptInToCoalitionApiV1CoalitionOptInPost_0`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiOptInToCoalitionApiV1CoalitionOptInPost_4Request struct via the builder pattern


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


## OptOutOfCoalitionApiV1CoalitionOptOutPost

> interface{} OptOutOfCoalitionApiV1CoalitionOptOutPost(ctx).Execute()

Opt Out Of Coalition



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
	resp, r, err := apiClient.CoalitionAPI.OptOutOfCoalitionApiV1CoalitionOptOutPost(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CoalitionAPI.OptOutOfCoalitionApiV1CoalitionOptOutPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `OptOutOfCoalitionApiV1CoalitionOptOutPost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `CoalitionAPI.OptOutOfCoalitionApiV1CoalitionOptOutPost`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiOptOutOfCoalitionApiV1CoalitionOptOutPostRequest struct via the builder pattern


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


## OptOutOfCoalitionApiV1CoalitionOptOutPost_0

> interface{} OptOutOfCoalitionApiV1CoalitionOptOutPost_0(ctx).Execute()

Opt Out Of Coalition



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
	resp, r, err := apiClient.CoalitionAPI.OptOutOfCoalitionApiV1CoalitionOptOutPost_0(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CoalitionAPI.OptOutOfCoalitionApiV1CoalitionOptOutPost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `OptOutOfCoalitionApiV1CoalitionOptOutPost_0`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `CoalitionAPI.OptOutOfCoalitionApiV1CoalitionOptOutPost_0`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiOptOutOfCoalitionApiV1CoalitionOptOutPost_5Request struct via the builder pattern


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

