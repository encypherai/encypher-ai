# \BYOKAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ListPublicKeysApiV1ByokPublicKeysGet**](BYOKAPI.md#ListPublicKeysApiV1ByokPublicKeysGet) | **Get** /api/v1/byok/public-keys | List public keys
[**ListPublicKeysApiV1ByokPublicKeysGet_0**](BYOKAPI.md#ListPublicKeysApiV1ByokPublicKeysGet_0) | **Get** /api/v1/byok/public-keys | List public keys
[**ListTrustedCasApiV1ByokTrustedCasGet**](BYOKAPI.md#ListTrustedCasApiV1ByokTrustedCasGet) | **Get** /api/v1/byok/trusted-cas | List trusted Certificate Authorities
[**ListTrustedCasApiV1ByokTrustedCasGet_0**](BYOKAPI.md#ListTrustedCasApiV1ByokTrustedCasGet_0) | **Get** /api/v1/byok/trusted-cas | List trusted Certificate Authorities
[**RegisterPublicKeyApiV1ByokPublicKeysPost**](BYOKAPI.md#RegisterPublicKeyApiV1ByokPublicKeysPost) | **Post** /api/v1/byok/public-keys | Register a public key
[**RegisterPublicKeyApiV1ByokPublicKeysPost_0**](BYOKAPI.md#RegisterPublicKeyApiV1ByokPublicKeysPost_0) | **Post** /api/v1/byok/public-keys | Register a public key
[**RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete**](BYOKAPI.md#RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete) | **Delete** /api/v1/byok/public-keys/{key_id} | Revoke a public key
[**RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete_0**](BYOKAPI.md#RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete_0) | **Delete** /api/v1/byok/public-keys/{key_id} | Revoke a public key
[**UploadCertificateApiV1ByokCertificatesPost**](BYOKAPI.md#UploadCertificateApiV1ByokCertificatesPost) | **Post** /api/v1/byok/certificates | Upload a CA-signed certificate
[**UploadCertificateApiV1ByokCertificatesPost_0**](BYOKAPI.md#UploadCertificateApiV1ByokCertificatesPost_0) | **Post** /api/v1/byok/certificates | Upload a CA-signed certificate



## ListPublicKeysApiV1ByokPublicKeysGet

> PublicKeyListResponse ListPublicKeysApiV1ByokPublicKeysGet(ctx).IncludeRevoked(includeRevoked).Execute()

List public keys



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
	resp, r, err := apiClient.BYOKAPI.ListPublicKeysApiV1ByokPublicKeysGet(context.Background()).IncludeRevoked(includeRevoked).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BYOKAPI.ListPublicKeysApiV1ByokPublicKeysGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListPublicKeysApiV1ByokPublicKeysGet`: PublicKeyListResponse
	fmt.Fprintf(os.Stdout, "Response from `BYOKAPI.ListPublicKeysApiV1ByokPublicKeysGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListPublicKeysApiV1ByokPublicKeysGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **includeRevoked** | **bool** | Include revoked keys | [default to false]

### Return type

[**PublicKeyListResponse**](PublicKeyListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListPublicKeysApiV1ByokPublicKeysGet_0

> PublicKeyListResponse ListPublicKeysApiV1ByokPublicKeysGet_0(ctx).IncludeRevoked(includeRevoked).Execute()

List public keys



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
	resp, r, err := apiClient.BYOKAPI.ListPublicKeysApiV1ByokPublicKeysGet_0(context.Background()).IncludeRevoked(includeRevoked).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BYOKAPI.ListPublicKeysApiV1ByokPublicKeysGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListPublicKeysApiV1ByokPublicKeysGet_0`: PublicKeyListResponse
	fmt.Fprintf(os.Stdout, "Response from `BYOKAPI.ListPublicKeysApiV1ByokPublicKeysGet_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListPublicKeysApiV1ByokPublicKeysGet_1Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **includeRevoked** | **bool** | Include revoked keys | [default to false]

### Return type

[**PublicKeyListResponse**](PublicKeyListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListTrustedCasApiV1ByokTrustedCasGet

> TrustListResponse ListTrustedCasApiV1ByokTrustedCasGet(ctx).Execute()

List trusted Certificate Authorities



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
	resp, r, err := apiClient.BYOKAPI.ListTrustedCasApiV1ByokTrustedCasGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BYOKAPI.ListTrustedCasApiV1ByokTrustedCasGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListTrustedCasApiV1ByokTrustedCasGet`: TrustListResponse
	fmt.Fprintf(os.Stdout, "Response from `BYOKAPI.ListTrustedCasApiV1ByokTrustedCasGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiListTrustedCasApiV1ByokTrustedCasGetRequest struct via the builder pattern


### Return type

[**TrustListResponse**](TrustListResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListTrustedCasApiV1ByokTrustedCasGet_0

> TrustListResponse ListTrustedCasApiV1ByokTrustedCasGet_0(ctx).Execute()

List trusted Certificate Authorities



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
	resp, r, err := apiClient.BYOKAPI.ListTrustedCasApiV1ByokTrustedCasGet_0(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BYOKAPI.ListTrustedCasApiV1ByokTrustedCasGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListTrustedCasApiV1ByokTrustedCasGet_0`: TrustListResponse
	fmt.Fprintf(os.Stdout, "Response from `BYOKAPI.ListTrustedCasApiV1ByokTrustedCasGet_0`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiListTrustedCasApiV1ByokTrustedCasGet_2Request struct via the builder pattern


### Return type

[**TrustListResponse**](TrustListResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RegisterPublicKeyApiV1ByokPublicKeysPost

> PublicKeyRegisterResponse RegisterPublicKeyApiV1ByokPublicKeysPost(ctx).PublicKeyRegisterRequest(publicKeyRegisterRequest).Execute()

Register a public key



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
	publicKeyRegisterRequest := *openapiclient.NewPublicKeyRegisterRequest("PublicKeyPem_example") // PublicKeyRegisterRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BYOKAPI.RegisterPublicKeyApiV1ByokPublicKeysPost(context.Background()).PublicKeyRegisterRequest(publicKeyRegisterRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BYOKAPI.RegisterPublicKeyApiV1ByokPublicKeysPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RegisterPublicKeyApiV1ByokPublicKeysPost`: PublicKeyRegisterResponse
	fmt.Fprintf(os.Stdout, "Response from `BYOKAPI.RegisterPublicKeyApiV1ByokPublicKeysPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiRegisterPublicKeyApiV1ByokPublicKeysPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **publicKeyRegisterRequest** | [**PublicKeyRegisterRequest**](PublicKeyRegisterRequest.md) |  | 

### Return type

[**PublicKeyRegisterResponse**](PublicKeyRegisterResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RegisterPublicKeyApiV1ByokPublicKeysPost_0

> PublicKeyRegisterResponse RegisterPublicKeyApiV1ByokPublicKeysPost_0(ctx).PublicKeyRegisterRequest(publicKeyRegisterRequest).Execute()

Register a public key



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
	publicKeyRegisterRequest := *openapiclient.NewPublicKeyRegisterRequest("PublicKeyPem_example") // PublicKeyRegisterRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BYOKAPI.RegisterPublicKeyApiV1ByokPublicKeysPost_0(context.Background()).PublicKeyRegisterRequest(publicKeyRegisterRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BYOKAPI.RegisterPublicKeyApiV1ByokPublicKeysPost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RegisterPublicKeyApiV1ByokPublicKeysPost_0`: PublicKeyRegisterResponse
	fmt.Fprintf(os.Stdout, "Response from `BYOKAPI.RegisterPublicKeyApiV1ByokPublicKeysPost_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiRegisterPublicKeyApiV1ByokPublicKeysPost_3Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **publicKeyRegisterRequest** | [**PublicKeyRegisterRequest**](PublicKeyRegisterRequest.md) |  | 

### Return type

[**PublicKeyRegisterResponse**](PublicKeyRegisterResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete

> map[string]interface{} RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete(ctx, keyId).Reason(reason).Execute()

Revoke a public key



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
	reason := "reason_example" // string | Reason for revocation (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BYOKAPI.RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete(context.Background(), keyId).Reason(reason).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BYOKAPI.RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete`: map[string]interface{}
	fmt.Fprintf(os.Stdout, "Response from `BYOKAPI.RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**keyId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiRevokePublicKeyApiV1ByokPublicKeysKeyIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **reason** | **string** | Reason for revocation | 

### Return type

**map[string]interface{}**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete_0

> map[string]interface{} RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete_0(ctx, keyId).Reason(reason).Execute()

Revoke a public key



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
	reason := "reason_example" // string | Reason for revocation (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BYOKAPI.RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete_0(context.Background(), keyId).Reason(reason).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BYOKAPI.RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete_0`: map[string]interface{}
	fmt.Fprintf(os.Stdout, "Response from `BYOKAPI.RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**keyId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiRevokePublicKeyApiV1ByokPublicKeysKeyIdDelete_4Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **reason** | **string** | Reason for revocation | 

### Return type

**map[string]interface{}**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UploadCertificateApiV1ByokCertificatesPost

> CertificateUploadResponse UploadCertificateApiV1ByokCertificatesPost(ctx).CertificateUploadRequest(certificateUploadRequest).Execute()

Upload a CA-signed certificate



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
	certificateUploadRequest := *openapiclient.NewCertificateUploadRequest("CertificatePem_example") // CertificateUploadRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BYOKAPI.UploadCertificateApiV1ByokCertificatesPost(context.Background()).CertificateUploadRequest(certificateUploadRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BYOKAPI.UploadCertificateApiV1ByokCertificatesPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UploadCertificateApiV1ByokCertificatesPost`: CertificateUploadResponse
	fmt.Fprintf(os.Stdout, "Response from `BYOKAPI.UploadCertificateApiV1ByokCertificatesPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiUploadCertificateApiV1ByokCertificatesPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **certificateUploadRequest** | [**CertificateUploadRequest**](CertificateUploadRequest.md) |  | 

### Return type

[**CertificateUploadResponse**](CertificateUploadResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UploadCertificateApiV1ByokCertificatesPost_0

> CertificateUploadResponse UploadCertificateApiV1ByokCertificatesPost_0(ctx).CertificateUploadRequest(certificateUploadRequest).Execute()

Upload a CA-signed certificate



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
	certificateUploadRequest := *openapiclient.NewCertificateUploadRequest("CertificatePem_example") // CertificateUploadRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BYOKAPI.UploadCertificateApiV1ByokCertificatesPost_0(context.Background()).CertificateUploadRequest(certificateUploadRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BYOKAPI.UploadCertificateApiV1ByokCertificatesPost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UploadCertificateApiV1ByokCertificatesPost_0`: CertificateUploadResponse
	fmt.Fprintf(os.Stdout, "Response from `BYOKAPI.UploadCertificateApiV1ByokCertificatesPost_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiUploadCertificateApiV1ByokCertificatesPost_5Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **certificateUploadRequest** | [**CertificateUploadRequest**](CertificateUploadRequest.md) |  | 

### Return type

[**CertificateUploadResponse**](CertificateUploadResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

