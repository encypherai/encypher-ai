# \APIKeysAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateKeyApiV1KeysPost**](APIKeysAPI.md#CreateKeyApiV1KeysPost) | **Post** /api/v1/keys | Create Key
[**CreateKeyApiV1KeysPost_0**](APIKeysAPI.md#CreateKeyApiV1KeysPost_0) | **Post** /api/v1/keys | Create Key
[**ListKeysApiV1KeysGet**](APIKeysAPI.md#ListKeysApiV1KeysGet) | **Get** /api/v1/keys | List Keys
[**ListKeysApiV1KeysGet_0**](APIKeysAPI.md#ListKeysApiV1KeysGet_0) | **Get** /api/v1/keys | List Keys
[**RevokeKeyApiV1KeysKeyIdDelete**](APIKeysAPI.md#RevokeKeyApiV1KeysKeyIdDelete) | **Delete** /api/v1/keys/{key_id} | Revoke Key
[**RevokeKeyApiV1KeysKeyIdDelete_0**](APIKeysAPI.md#RevokeKeyApiV1KeysKeyIdDelete_0) | **Delete** /api/v1/keys/{key_id} | Revoke Key
[**RotateKeyApiV1KeysKeyIdRotatePost**](APIKeysAPI.md#RotateKeyApiV1KeysKeyIdRotatePost) | **Post** /api/v1/keys/{key_id}/rotate | Rotate Key
[**RotateKeyApiV1KeysKeyIdRotatePost_0**](APIKeysAPI.md#RotateKeyApiV1KeysKeyIdRotatePost_0) | **Post** /api/v1/keys/{key_id}/rotate | Rotate Key
[**UpdateKeyApiV1KeysKeyIdPatch**](APIKeysAPI.md#UpdateKeyApiV1KeysKeyIdPatch) | **Patch** /api/v1/keys/{key_id} | Update Key
[**UpdateKeyApiV1KeysKeyIdPatch_0**](APIKeysAPI.md#UpdateKeyApiV1KeysKeyIdPatch_0) | **Patch** /api/v1/keys/{key_id} | Update Key



## CreateKeyApiV1KeysPost

> KeyCreateResponse CreateKeyApiV1KeysPost(ctx).KeyCreateRequest(keyCreateRequest).Execute()

Create Key



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
	keyCreateRequest := *openapiclient.NewKeyCreateRequest() // KeyCreateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.APIKeysAPI.CreateKeyApiV1KeysPost(context.Background()).KeyCreateRequest(keyCreateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `APIKeysAPI.CreateKeyApiV1KeysPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateKeyApiV1KeysPost`: KeyCreateResponse
	fmt.Fprintf(os.Stdout, "Response from `APIKeysAPI.CreateKeyApiV1KeysPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateKeyApiV1KeysPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **keyCreateRequest** | [**KeyCreateRequest**](KeyCreateRequest.md) |  | 

### Return type

[**KeyCreateResponse**](KeyCreateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateKeyApiV1KeysPost_0

> KeyCreateResponse CreateKeyApiV1KeysPost_0(ctx).KeyCreateRequest(keyCreateRequest).Execute()

Create Key



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
	keyCreateRequest := *openapiclient.NewKeyCreateRequest() // KeyCreateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.APIKeysAPI.CreateKeyApiV1KeysPost_0(context.Background()).KeyCreateRequest(keyCreateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `APIKeysAPI.CreateKeyApiV1KeysPost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateKeyApiV1KeysPost_0`: KeyCreateResponse
	fmt.Fprintf(os.Stdout, "Response from `APIKeysAPI.CreateKeyApiV1KeysPost_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateKeyApiV1KeysPost_1Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **keyCreateRequest** | [**KeyCreateRequest**](KeyCreateRequest.md) |  | 

### Return type

[**KeyCreateResponse**](KeyCreateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListKeysApiV1KeysGet

> KeyListResponse ListKeysApiV1KeysGet(ctx).IncludeRevoked(includeRevoked).Execute()

List Keys



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
	includeRevoked := true // bool | Include revoked keys (optional) (default to false)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.APIKeysAPI.ListKeysApiV1KeysGet(context.Background()).IncludeRevoked(includeRevoked).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `APIKeysAPI.ListKeysApiV1KeysGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListKeysApiV1KeysGet`: KeyListResponse
	fmt.Fprintf(os.Stdout, "Response from `APIKeysAPI.ListKeysApiV1KeysGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListKeysApiV1KeysGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **includeRevoked** | **bool** | Include revoked keys | [default to false]

### Return type

[**KeyListResponse**](KeyListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListKeysApiV1KeysGet_0

> KeyListResponse ListKeysApiV1KeysGet_0(ctx).IncludeRevoked(includeRevoked).Execute()

List Keys



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
	includeRevoked := true // bool | Include revoked keys (optional) (default to false)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.APIKeysAPI.ListKeysApiV1KeysGet_0(context.Background()).IncludeRevoked(includeRevoked).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `APIKeysAPI.ListKeysApiV1KeysGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListKeysApiV1KeysGet_0`: KeyListResponse
	fmt.Fprintf(os.Stdout, "Response from `APIKeysAPI.ListKeysApiV1KeysGet_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListKeysApiV1KeysGet_2Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **includeRevoked** | **bool** | Include revoked keys | [default to false]

### Return type

[**KeyListResponse**](KeyListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RevokeKeyApiV1KeysKeyIdDelete

> KeyRevokeResponse RevokeKeyApiV1KeysKeyIdDelete(ctx, keyId).Execute()

Revoke Key



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
	keyId := "keyId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.APIKeysAPI.RevokeKeyApiV1KeysKeyIdDelete(context.Background(), keyId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `APIKeysAPI.RevokeKeyApiV1KeysKeyIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RevokeKeyApiV1KeysKeyIdDelete`: KeyRevokeResponse
	fmt.Fprintf(os.Stdout, "Response from `APIKeysAPI.RevokeKeyApiV1KeysKeyIdDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**keyId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiRevokeKeyApiV1KeysKeyIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**KeyRevokeResponse**](KeyRevokeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RevokeKeyApiV1KeysKeyIdDelete_0

> KeyRevokeResponse RevokeKeyApiV1KeysKeyIdDelete_0(ctx, keyId).Execute()

Revoke Key



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
	keyId := "keyId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.APIKeysAPI.RevokeKeyApiV1KeysKeyIdDelete_0(context.Background(), keyId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `APIKeysAPI.RevokeKeyApiV1KeysKeyIdDelete_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RevokeKeyApiV1KeysKeyIdDelete_0`: KeyRevokeResponse
	fmt.Fprintf(os.Stdout, "Response from `APIKeysAPI.RevokeKeyApiV1KeysKeyIdDelete_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**keyId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiRevokeKeyApiV1KeysKeyIdDelete_3Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**KeyRevokeResponse**](KeyRevokeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RotateKeyApiV1KeysKeyIdRotatePost

> KeyRotateResponse RotateKeyApiV1KeysKeyIdRotatePost(ctx, keyId).Execute()

Rotate Key



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
	keyId := "keyId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.APIKeysAPI.RotateKeyApiV1KeysKeyIdRotatePost(context.Background(), keyId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `APIKeysAPI.RotateKeyApiV1KeysKeyIdRotatePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RotateKeyApiV1KeysKeyIdRotatePost`: KeyRotateResponse
	fmt.Fprintf(os.Stdout, "Response from `APIKeysAPI.RotateKeyApiV1KeysKeyIdRotatePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**keyId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiRotateKeyApiV1KeysKeyIdRotatePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**KeyRotateResponse**](KeyRotateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RotateKeyApiV1KeysKeyIdRotatePost_0

> KeyRotateResponse RotateKeyApiV1KeysKeyIdRotatePost_0(ctx, keyId).Execute()

Rotate Key



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
	keyId := "keyId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.APIKeysAPI.RotateKeyApiV1KeysKeyIdRotatePost_0(context.Background(), keyId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `APIKeysAPI.RotateKeyApiV1KeysKeyIdRotatePost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RotateKeyApiV1KeysKeyIdRotatePost_0`: KeyRotateResponse
	fmt.Fprintf(os.Stdout, "Response from `APIKeysAPI.RotateKeyApiV1KeysKeyIdRotatePost_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**keyId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiRotateKeyApiV1KeysKeyIdRotatePost_4Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**KeyRotateResponse**](KeyRotateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateKeyApiV1KeysKeyIdPatch

> KeyUpdateResponse UpdateKeyApiV1KeysKeyIdPatch(ctx, keyId).KeyUpdateRequest(keyUpdateRequest).Execute()

Update Key



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
	keyId := "keyId_example" // string | 
	keyUpdateRequest := *openapiclient.NewKeyUpdateRequest() // KeyUpdateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.APIKeysAPI.UpdateKeyApiV1KeysKeyIdPatch(context.Background(), keyId).KeyUpdateRequest(keyUpdateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `APIKeysAPI.UpdateKeyApiV1KeysKeyIdPatch``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateKeyApiV1KeysKeyIdPatch`: KeyUpdateResponse
	fmt.Fprintf(os.Stdout, "Response from `APIKeysAPI.UpdateKeyApiV1KeysKeyIdPatch`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**keyId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateKeyApiV1KeysKeyIdPatchRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **keyUpdateRequest** | [**KeyUpdateRequest**](KeyUpdateRequest.md) |  | 

### Return type

[**KeyUpdateResponse**](KeyUpdateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateKeyApiV1KeysKeyIdPatch_0

> KeyUpdateResponse UpdateKeyApiV1KeysKeyIdPatch_0(ctx, keyId).KeyUpdateRequest(keyUpdateRequest).Execute()

Update Key



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
	keyId := "keyId_example" // string | 
	keyUpdateRequest := *openapiclient.NewKeyUpdateRequest() // KeyUpdateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.APIKeysAPI.UpdateKeyApiV1KeysKeyIdPatch_0(context.Background(), keyId).KeyUpdateRequest(keyUpdateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `APIKeysAPI.UpdateKeyApiV1KeysKeyIdPatch_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateKeyApiV1KeysKeyIdPatch_0`: KeyUpdateResponse
	fmt.Fprintf(os.Stdout, "Response from `APIKeysAPI.UpdateKeyApiV1KeysKeyIdPatch_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**keyId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateKeyApiV1KeysKeyIdPatch_5Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **keyUpdateRequest** | [**KeyUpdateRequest**](KeyUpdateRequest.md) |  | 

### Return type

[**KeyUpdateResponse**](KeyUpdateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

