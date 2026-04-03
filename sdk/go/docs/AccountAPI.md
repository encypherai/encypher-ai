# \AccountAPI

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GetAccountInfoApiV1AccountGet**](AccountAPI.md#GetAccountInfoApiV1AccountGet) | **Get** /api/v1/account | Get Account Info
[**GetAccountInfoApiV1AccountGet_0**](AccountAPI.md#GetAccountInfoApiV1AccountGet_0) | **Get** /api/v1/account | Get Account Info
[**GetAccountQuotaApiV1AccountQuotaGet**](AccountAPI.md#GetAccountQuotaApiV1AccountQuotaGet) | **Get** /api/v1/account/quota | Get Account Quota
[**GetAccountQuotaApiV1AccountQuotaGet_0**](AccountAPI.md#GetAccountQuotaApiV1AccountQuotaGet_0) | **Get** /api/v1/account/quota | Get Account Quota



## GetAccountInfoApiV1AccountGet

> AccountResponse GetAccountInfoApiV1AccountGet(ctx).Execute()

Get Account Info



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
	resp, r, err := apiClient.AccountAPI.GetAccountInfoApiV1AccountGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AccountAPI.GetAccountInfoApiV1AccountGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAccountInfoApiV1AccountGet`: AccountResponse
	fmt.Fprintf(os.Stdout, "Response from `AccountAPI.GetAccountInfoApiV1AccountGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetAccountInfoApiV1AccountGetRequest struct via the builder pattern


### Return type

[**AccountResponse**](AccountResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAccountInfoApiV1AccountGet_0

> AccountResponse GetAccountInfoApiV1AccountGet_0(ctx).Execute()

Get Account Info



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
	resp, r, err := apiClient.AccountAPI.GetAccountInfoApiV1AccountGet_0(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AccountAPI.GetAccountInfoApiV1AccountGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAccountInfoApiV1AccountGet_0`: AccountResponse
	fmt.Fprintf(os.Stdout, "Response from `AccountAPI.GetAccountInfoApiV1AccountGet_0`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetAccountInfoApiV1AccountGet_1Request struct via the builder pattern


### Return type

[**AccountResponse**](AccountResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAccountQuotaApiV1AccountQuotaGet

> QuotaResponse GetAccountQuotaApiV1AccountQuotaGet(ctx).Execute()

Get Account Quota



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
	resp, r, err := apiClient.AccountAPI.GetAccountQuotaApiV1AccountQuotaGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AccountAPI.GetAccountQuotaApiV1AccountQuotaGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAccountQuotaApiV1AccountQuotaGet`: QuotaResponse
	fmt.Fprintf(os.Stdout, "Response from `AccountAPI.GetAccountQuotaApiV1AccountQuotaGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetAccountQuotaApiV1AccountQuotaGetRequest struct via the builder pattern


### Return type

[**QuotaResponse**](QuotaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAccountQuotaApiV1AccountQuotaGet_0

> QuotaResponse GetAccountQuotaApiV1AccountQuotaGet_0(ctx).Execute()

Get Account Quota



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
	resp, r, err := apiClient.AccountAPI.GetAccountQuotaApiV1AccountQuotaGet_0(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AccountAPI.GetAccountQuotaApiV1AccountQuotaGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAccountQuotaApiV1AccountQuotaGet_0`: QuotaResponse
	fmt.Fprintf(os.Stdout, "Response from `AccountAPI.GetAccountQuotaApiV1AccountQuotaGet_0`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetAccountQuotaApiV1AccountQuotaGet_2Request struct via the builder pattern


### Return type

[**QuotaResponse**](QuotaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
