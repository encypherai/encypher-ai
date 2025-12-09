# \ProvisioningAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**AutoProvisionApiV1ProvisioningAutoProvisionPost**](ProvisioningAPI.md#AutoProvisionApiV1ProvisioningAutoProvisionPost) | **Post** /api/v1/provisioning/auto-provision | Auto-provision Organization and API Key
[**CreateApiKeyApiV1ProvisioningApiKeysPost**](ProvisioningAPI.md#CreateApiKeyApiV1ProvisioningApiKeysPost) | **Post** /api/v1/provisioning/api-keys | Create API Key
[**CreateUserAccountApiV1ProvisioningUsersPost**](ProvisioningAPI.md#CreateUserAccountApiV1ProvisioningUsersPost) | **Post** /api/v1/provisioning/users | Create User Account
[**ListApiKeysApiV1ProvisioningApiKeysGet**](ProvisioningAPI.md#ListApiKeysApiV1ProvisioningApiKeysGet) | **Get** /api/v1/provisioning/api-keys | List API Keys
[**ProvisioningHealthApiV1ProvisioningHealthGet**](ProvisioningAPI.md#ProvisioningHealthApiV1ProvisioningHealthGet) | **Get** /api/v1/provisioning/health | Provisioning Service Health
[**RevokeApiKeyApiV1ProvisioningApiKeysKeyIdDelete**](ProvisioningAPI.md#RevokeApiKeyApiV1ProvisioningApiKeysKeyIdDelete) | **Delete** /api/v1/provisioning/api-keys/{key_id} | Revoke API Key



## AutoProvisionApiV1ProvisioningAutoProvisionPost

> AutoProvisionResponse AutoProvisionApiV1ProvisioningAutoProvisionPost(ctx).AutoProvisionRequest(autoProvisionRequest).XProvisioningToken(xProvisioningToken).Execute()

Auto-provision Organization and API Key



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
	autoProvisionRequest := *openapiclient.NewAutoProvisionRequest("user@example.com", "wordpress") // AutoProvisionRequest | 
	xProvisioningToken := "xProvisioningToken_example" // string | Provisioning token (optional) (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ProvisioningAPI.AutoProvisionApiV1ProvisioningAutoProvisionPost(context.Background()).AutoProvisionRequest(autoProvisionRequest).XProvisioningToken(xProvisioningToken).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ProvisioningAPI.AutoProvisionApiV1ProvisioningAutoProvisionPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `AutoProvisionApiV1ProvisioningAutoProvisionPost`: AutoProvisionResponse
	fmt.Fprintf(os.Stdout, "Response from `ProvisioningAPI.AutoProvisionApiV1ProvisioningAutoProvisionPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiAutoProvisionApiV1ProvisioningAutoProvisionPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **autoProvisionRequest** | [**AutoProvisionRequest**](AutoProvisionRequest.md) |  | 
 **xProvisioningToken** | **string** | Provisioning token (optional) | 

### Return type

[**AutoProvisionResponse**](AutoProvisionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateApiKeyApiV1ProvisioningApiKeysPost

> APIKeyResponse CreateApiKeyApiV1ProvisioningApiKeysPost(ctx).APIKeyCreateRequest(aPIKeyCreateRequest).Execute()

Create API Key



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
	aPIKeyCreateRequest := *openapiclient.NewAPIKeyCreateRequest() // APIKeyCreateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ProvisioningAPI.CreateApiKeyApiV1ProvisioningApiKeysPost(context.Background()).APIKeyCreateRequest(aPIKeyCreateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ProvisioningAPI.CreateApiKeyApiV1ProvisioningApiKeysPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateApiKeyApiV1ProvisioningApiKeysPost`: APIKeyResponse
	fmt.Fprintf(os.Stdout, "Response from `ProvisioningAPI.CreateApiKeyApiV1ProvisioningApiKeysPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateApiKeyApiV1ProvisioningApiKeysPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **aPIKeyCreateRequest** | [**APIKeyCreateRequest**](APIKeyCreateRequest.md) |  | 

### Return type

[**APIKeyResponse**](APIKeyResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateUserAccountApiV1ProvisioningUsersPost

> UserAccountResponse CreateUserAccountApiV1ProvisioningUsersPost(ctx).UserAccountCreateRequest(userAccountCreateRequest).Execute()

Create User Account



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
	userAccountCreateRequest := *openapiclient.NewUserAccountCreateRequest("Email_example") // UserAccountCreateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ProvisioningAPI.CreateUserAccountApiV1ProvisioningUsersPost(context.Background()).UserAccountCreateRequest(userAccountCreateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ProvisioningAPI.CreateUserAccountApiV1ProvisioningUsersPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateUserAccountApiV1ProvisioningUsersPost`: UserAccountResponse
	fmt.Fprintf(os.Stdout, "Response from `ProvisioningAPI.CreateUserAccountApiV1ProvisioningUsersPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateUserAccountApiV1ProvisioningUsersPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **userAccountCreateRequest** | [**UserAccountCreateRequest**](UserAccountCreateRequest.md) |  | 

### Return type

[**UserAccountResponse**](UserAccountResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListApiKeysApiV1ProvisioningApiKeysGet

> APIKeyListResponse ListApiKeysApiV1ProvisioningApiKeysGet(ctx).Execute()

List API Keys



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
	resp, r, err := apiClient.ProvisioningAPI.ListApiKeysApiV1ProvisioningApiKeysGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ProvisioningAPI.ListApiKeysApiV1ProvisioningApiKeysGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListApiKeysApiV1ProvisioningApiKeysGet`: APIKeyListResponse
	fmt.Fprintf(os.Stdout, "Response from `ProvisioningAPI.ListApiKeysApiV1ProvisioningApiKeysGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiListApiKeysApiV1ProvisioningApiKeysGetRequest struct via the builder pattern


### Return type

[**APIKeyListResponse**](APIKeyListResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ProvisioningHealthApiV1ProvisioningHealthGet

> interface{} ProvisioningHealthApiV1ProvisioningHealthGet(ctx).Execute()

Provisioning Service Health



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
	resp, r, err := apiClient.ProvisioningAPI.ProvisioningHealthApiV1ProvisioningHealthGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ProvisioningAPI.ProvisioningHealthApiV1ProvisioningHealthGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ProvisioningHealthApiV1ProvisioningHealthGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `ProvisioningAPI.ProvisioningHealthApiV1ProvisioningHealthGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiProvisioningHealthApiV1ProvisioningHealthGetRequest struct via the builder pattern


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


## RevokeApiKeyApiV1ProvisioningApiKeysKeyIdDelete

> RevokeApiKeyApiV1ProvisioningApiKeysKeyIdDelete(ctx, keyId).APIKeyRevokeRequest(aPIKeyRevokeRequest).Execute()

Revoke API Key



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
	keyId := "keyId_example" // string | 
	aPIKeyRevokeRequest := *openapiclient.NewAPIKeyRevokeRequest("KeyId_example") // APIKeyRevokeRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.ProvisioningAPI.RevokeApiKeyApiV1ProvisioningApiKeysKeyIdDelete(context.Background(), keyId).APIKeyRevokeRequest(aPIKeyRevokeRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ProvisioningAPI.RevokeApiKeyApiV1ProvisioningApiKeysKeyIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**keyId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiRevokeApiKeyApiV1ProvisioningApiKeysKeyIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **aPIKeyRevokeRequest** | [**APIKeyRevokeRequest**](APIKeyRevokeRequest.md) |  | 

### Return type

 (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

