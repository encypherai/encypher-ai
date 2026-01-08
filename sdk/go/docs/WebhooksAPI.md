# \WebhooksAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateWebhookApiV1WebhooksPost**](WebhooksAPI.md#CreateWebhookApiV1WebhooksPost) | **Post** /api/v1/webhooks | Create Webhook
[**CreateWebhookApiV1WebhooksPost_0**](WebhooksAPI.md#CreateWebhookApiV1WebhooksPost_0) | **Post** /api/v1/webhooks | Create Webhook
[**DeleteWebhookApiV1WebhooksWebhookIdDelete**](WebhooksAPI.md#DeleteWebhookApiV1WebhooksWebhookIdDelete) | **Delete** /api/v1/webhooks/{webhook_id} | Delete Webhook
[**DeleteWebhookApiV1WebhooksWebhookIdDelete_0**](WebhooksAPI.md#DeleteWebhookApiV1WebhooksWebhookIdDelete_0) | **Delete** /api/v1/webhooks/{webhook_id} | Delete Webhook
[**GetWebhookApiV1WebhooksWebhookIdGet**](WebhooksAPI.md#GetWebhookApiV1WebhooksWebhookIdGet) | **Get** /api/v1/webhooks/{webhook_id} | Get Webhook
[**GetWebhookApiV1WebhooksWebhookIdGet_0**](WebhooksAPI.md#GetWebhookApiV1WebhooksWebhookIdGet_0) | **Get** /api/v1/webhooks/{webhook_id} | Get Webhook
[**GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet**](WebhooksAPI.md#GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet) | **Get** /api/v1/webhooks/{webhook_id}/deliveries | Get Webhook Deliveries
[**GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet_0**](WebhooksAPI.md#GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet_0) | **Get** /api/v1/webhooks/{webhook_id}/deliveries | Get Webhook Deliveries
[**ListWebhooksApiV1WebhooksGet**](WebhooksAPI.md#ListWebhooksApiV1WebhooksGet) | **Get** /api/v1/webhooks | List Webhooks
[**ListWebhooksApiV1WebhooksGet_0**](WebhooksAPI.md#ListWebhooksApiV1WebhooksGet_0) | **Get** /api/v1/webhooks | List Webhooks
[**TestWebhookApiV1WebhooksWebhookIdTestPost**](WebhooksAPI.md#TestWebhookApiV1WebhooksWebhookIdTestPost) | **Post** /api/v1/webhooks/{webhook_id}/test | Test Webhook
[**TestWebhookApiV1WebhooksWebhookIdTestPost_0**](WebhooksAPI.md#TestWebhookApiV1WebhooksWebhookIdTestPost_0) | **Post** /api/v1/webhooks/{webhook_id}/test | Test Webhook
[**UpdateWebhookApiV1WebhooksWebhookIdPatch**](WebhooksAPI.md#UpdateWebhookApiV1WebhooksWebhookIdPatch) | **Patch** /api/v1/webhooks/{webhook_id} | Update Webhook
[**UpdateWebhookApiV1WebhooksWebhookIdPatch_0**](WebhooksAPI.md#UpdateWebhookApiV1WebhooksWebhookIdPatch_0) | **Patch** /api/v1/webhooks/{webhook_id} | Update Webhook



## CreateWebhookApiV1WebhooksPost

> WebhookCreateResponse CreateWebhookApiV1WebhooksPost(ctx).WebhookCreateRequest(webhookCreateRequest).Execute()

Create Webhook



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
	webhookCreateRequest := *openapiclient.NewWebhookCreateRequest("Url_example", []string{"Events_example"}) // WebhookCreateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.WebhooksAPI.CreateWebhookApiV1WebhooksPost(context.Background()).WebhookCreateRequest(webhookCreateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WebhooksAPI.CreateWebhookApiV1WebhooksPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateWebhookApiV1WebhooksPost`: WebhookCreateResponse
	fmt.Fprintf(os.Stdout, "Response from `WebhooksAPI.CreateWebhookApiV1WebhooksPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateWebhookApiV1WebhooksPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhookCreateRequest** | [**WebhookCreateRequest**](WebhookCreateRequest.md) |  | 

### Return type

[**WebhookCreateResponse**](WebhookCreateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateWebhookApiV1WebhooksPost_0

> WebhookCreateResponse CreateWebhookApiV1WebhooksPost_0(ctx).WebhookCreateRequest(webhookCreateRequest).Execute()

Create Webhook



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
	webhookCreateRequest := *openapiclient.NewWebhookCreateRequest("Url_example", []string{"Events_example"}) // WebhookCreateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.WebhooksAPI.CreateWebhookApiV1WebhooksPost_0(context.Background()).WebhookCreateRequest(webhookCreateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WebhooksAPI.CreateWebhookApiV1WebhooksPost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateWebhookApiV1WebhooksPost_0`: WebhookCreateResponse
	fmt.Fprintf(os.Stdout, "Response from `WebhooksAPI.CreateWebhookApiV1WebhooksPost_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateWebhookApiV1WebhooksPost_1Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhookCreateRequest** | [**WebhookCreateRequest**](WebhookCreateRequest.md) |  | 

### Return type

[**WebhookCreateResponse**](WebhookCreateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteWebhookApiV1WebhooksWebhookIdDelete

> WebhookDeleteResponse DeleteWebhookApiV1WebhooksWebhookIdDelete(ctx, webhookId).Execute()

Delete Webhook



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
	webhookId := "webhookId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.WebhooksAPI.DeleteWebhookApiV1WebhooksWebhookIdDelete(context.Background(), webhookId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WebhooksAPI.DeleteWebhookApiV1WebhooksWebhookIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteWebhookApiV1WebhooksWebhookIdDelete`: WebhookDeleteResponse
	fmt.Fprintf(os.Stdout, "Response from `WebhooksAPI.DeleteWebhookApiV1WebhooksWebhookIdDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**webhookId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteWebhookApiV1WebhooksWebhookIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**WebhookDeleteResponse**](WebhookDeleteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteWebhookApiV1WebhooksWebhookIdDelete_0

> WebhookDeleteResponse DeleteWebhookApiV1WebhooksWebhookIdDelete_0(ctx, webhookId).Execute()

Delete Webhook



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
	webhookId := "webhookId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.WebhooksAPI.DeleteWebhookApiV1WebhooksWebhookIdDelete_0(context.Background(), webhookId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WebhooksAPI.DeleteWebhookApiV1WebhooksWebhookIdDelete_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteWebhookApiV1WebhooksWebhookIdDelete_0`: WebhookDeleteResponse
	fmt.Fprintf(os.Stdout, "Response from `WebhooksAPI.DeleteWebhookApiV1WebhooksWebhookIdDelete_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**webhookId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteWebhookApiV1WebhooksWebhookIdDelete_2Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**WebhookDeleteResponse**](WebhookDeleteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetWebhookApiV1WebhooksWebhookIdGet

> WebhookListResponse GetWebhookApiV1WebhooksWebhookIdGet(ctx, webhookId).Execute()

Get Webhook



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
	webhookId := "webhookId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.WebhooksAPI.GetWebhookApiV1WebhooksWebhookIdGet(context.Background(), webhookId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WebhooksAPI.GetWebhookApiV1WebhooksWebhookIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetWebhookApiV1WebhooksWebhookIdGet`: WebhookListResponse
	fmt.Fprintf(os.Stdout, "Response from `WebhooksAPI.GetWebhookApiV1WebhooksWebhookIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**webhookId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetWebhookApiV1WebhooksWebhookIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**WebhookListResponse**](WebhookListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetWebhookApiV1WebhooksWebhookIdGet_0

> WebhookListResponse GetWebhookApiV1WebhooksWebhookIdGet_0(ctx, webhookId).Execute()

Get Webhook



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
	webhookId := "webhookId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.WebhooksAPI.GetWebhookApiV1WebhooksWebhookIdGet_0(context.Background(), webhookId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WebhooksAPI.GetWebhookApiV1WebhooksWebhookIdGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetWebhookApiV1WebhooksWebhookIdGet_0`: WebhookListResponse
	fmt.Fprintf(os.Stdout, "Response from `WebhooksAPI.GetWebhookApiV1WebhooksWebhookIdGet_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**webhookId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetWebhookApiV1WebhooksWebhookIdGet_3Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**WebhookListResponse**](WebhookListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet

> WebhookDeliveriesResponse GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet(ctx, webhookId).Page(page).PageSize(pageSize).Execute()

Get Webhook Deliveries



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
	webhookId := "webhookId_example" // string | 
	page := int32(56) // int32 |  (optional) (default to 1)
	pageSize := int32(56) // int32 |  (optional) (default to 50)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.WebhooksAPI.GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet(context.Background(), webhookId).Page(page).PageSize(pageSize).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WebhooksAPI.GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet`: WebhookDeliveriesResponse
	fmt.Fprintf(os.Stdout, "Response from `WebhooksAPI.GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**webhookId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **page** | **int32** |  | [default to 1]
 **pageSize** | **int32** |  | [default to 50]

### Return type

[**WebhookDeliveriesResponse**](WebhookDeliveriesResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet_0

> WebhookDeliveriesResponse GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet_0(ctx, webhookId).Page(page).PageSize(pageSize).Execute()

Get Webhook Deliveries



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
	webhookId := "webhookId_example" // string | 
	page := int32(56) // int32 |  (optional) (default to 1)
	pageSize := int32(56) // int32 |  (optional) (default to 50)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.WebhooksAPI.GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet_0(context.Background(), webhookId).Page(page).PageSize(pageSize).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WebhooksAPI.GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet_0`: WebhookDeliveriesResponse
	fmt.Fprintf(os.Stdout, "Response from `WebhooksAPI.GetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**webhookId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet_4Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **page** | **int32** |  | [default to 1]
 **pageSize** | **int32** |  | [default to 50]

### Return type

[**WebhookDeliveriesResponse**](WebhookDeliveriesResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListWebhooksApiV1WebhooksGet

> WebhookListResponse ListWebhooksApiV1WebhooksGet(ctx).Execute()

List Webhooks



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
	resp, r, err := apiClient.WebhooksAPI.ListWebhooksApiV1WebhooksGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WebhooksAPI.ListWebhooksApiV1WebhooksGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListWebhooksApiV1WebhooksGet`: WebhookListResponse
	fmt.Fprintf(os.Stdout, "Response from `WebhooksAPI.ListWebhooksApiV1WebhooksGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiListWebhooksApiV1WebhooksGetRequest struct via the builder pattern


### Return type

[**WebhookListResponse**](WebhookListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListWebhooksApiV1WebhooksGet_0

> WebhookListResponse ListWebhooksApiV1WebhooksGet_0(ctx).Execute()

List Webhooks



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
	resp, r, err := apiClient.WebhooksAPI.ListWebhooksApiV1WebhooksGet_0(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WebhooksAPI.ListWebhooksApiV1WebhooksGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListWebhooksApiV1WebhooksGet_0`: WebhookListResponse
	fmt.Fprintf(os.Stdout, "Response from `WebhooksAPI.ListWebhooksApiV1WebhooksGet_0`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiListWebhooksApiV1WebhooksGet_5Request struct via the builder pattern


### Return type

[**WebhookListResponse**](WebhookListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## TestWebhookApiV1WebhooksWebhookIdTestPost

> WebhookTestResponse TestWebhookApiV1WebhooksWebhookIdTestPost(ctx, webhookId).Execute()

Test Webhook



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
	webhookId := "webhookId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.WebhooksAPI.TestWebhookApiV1WebhooksWebhookIdTestPost(context.Background(), webhookId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WebhooksAPI.TestWebhookApiV1WebhooksWebhookIdTestPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `TestWebhookApiV1WebhooksWebhookIdTestPost`: WebhookTestResponse
	fmt.Fprintf(os.Stdout, "Response from `WebhooksAPI.TestWebhookApiV1WebhooksWebhookIdTestPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**webhookId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiTestWebhookApiV1WebhooksWebhookIdTestPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**WebhookTestResponse**](WebhookTestResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## TestWebhookApiV1WebhooksWebhookIdTestPost_0

> WebhookTestResponse TestWebhookApiV1WebhooksWebhookIdTestPost_0(ctx, webhookId).Execute()

Test Webhook



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
	webhookId := "webhookId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.WebhooksAPI.TestWebhookApiV1WebhooksWebhookIdTestPost_0(context.Background(), webhookId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WebhooksAPI.TestWebhookApiV1WebhooksWebhookIdTestPost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `TestWebhookApiV1WebhooksWebhookIdTestPost_0`: WebhookTestResponse
	fmt.Fprintf(os.Stdout, "Response from `WebhooksAPI.TestWebhookApiV1WebhooksWebhookIdTestPost_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**webhookId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiTestWebhookApiV1WebhooksWebhookIdTestPost_6Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**WebhookTestResponse**](WebhookTestResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateWebhookApiV1WebhooksWebhookIdPatch

> WebhookUpdateResponse UpdateWebhookApiV1WebhooksWebhookIdPatch(ctx, webhookId).WebhookUpdateRequest(webhookUpdateRequest).Execute()

Update Webhook



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
	webhookId := "webhookId_example" // string | 
	webhookUpdateRequest := *openapiclient.NewWebhookUpdateRequest() // WebhookUpdateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.WebhooksAPI.UpdateWebhookApiV1WebhooksWebhookIdPatch(context.Background(), webhookId).WebhookUpdateRequest(webhookUpdateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WebhooksAPI.UpdateWebhookApiV1WebhooksWebhookIdPatch``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateWebhookApiV1WebhooksWebhookIdPatch`: WebhookUpdateResponse
	fmt.Fprintf(os.Stdout, "Response from `WebhooksAPI.UpdateWebhookApiV1WebhooksWebhookIdPatch`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**webhookId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateWebhookApiV1WebhooksWebhookIdPatchRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **webhookUpdateRequest** | [**WebhookUpdateRequest**](WebhookUpdateRequest.md) |  | 

### Return type

[**WebhookUpdateResponse**](WebhookUpdateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateWebhookApiV1WebhooksWebhookIdPatch_0

> WebhookUpdateResponse UpdateWebhookApiV1WebhooksWebhookIdPatch_0(ctx, webhookId).WebhookUpdateRequest(webhookUpdateRequest).Execute()

Update Webhook



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
	webhookId := "webhookId_example" // string | 
	webhookUpdateRequest := *openapiclient.NewWebhookUpdateRequest() // WebhookUpdateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.WebhooksAPI.UpdateWebhookApiV1WebhooksWebhookIdPatch_0(context.Background(), webhookId).WebhookUpdateRequest(webhookUpdateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WebhooksAPI.UpdateWebhookApiV1WebhooksWebhookIdPatch_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateWebhookApiV1WebhooksWebhookIdPatch_0`: WebhookUpdateResponse
	fmt.Fprintf(os.Stdout, "Response from `WebhooksAPI.UpdateWebhookApiV1WebhooksWebhookIdPatch_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**webhookId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateWebhookApiV1WebhooksWebhookIdPatch_7Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **webhookUpdateRequest** | [**WebhookUpdateRequest**](WebhookUpdateRequest.md) |  | 

### Return type

[**WebhookUpdateResponse**](WebhookUpdateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

