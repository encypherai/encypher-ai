# \C2PACustomAssertionsAPI

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateSchemaApiV1EnterpriseC2paSchemasPost**](C2PACustomAssertionsAPI.md#CreateSchemaApiV1EnterpriseC2paSchemasPost) | **Post** /api/v1/enterprise/c2pa/schemas | Create Schema
[**CreateTemplateApiV1EnterpriseC2paTemplatesPost**](C2PACustomAssertionsAPI.md#CreateTemplateApiV1EnterpriseC2paTemplatesPost) | **Post** /api/v1/enterprise/c2pa/templates | Create Template
[**DeleteSchemaApiV1EnterpriseC2paSchemasSchemaIdDelete**](C2PACustomAssertionsAPI.md#DeleteSchemaApiV1EnterpriseC2paSchemasSchemaIdDelete) | **Delete** /api/v1/enterprise/c2pa/schemas/{schema_id} | Delete Schema
[**DeleteTemplateApiV1EnterpriseC2paTemplatesTemplateIdDelete**](C2PACustomAssertionsAPI.md#DeleteTemplateApiV1EnterpriseC2paTemplatesTemplateIdDelete) | **Delete** /api/v1/enterprise/c2pa/templates/{template_id} | Delete Template
[**GetSchemaApiV1EnterpriseC2paSchemasSchemaIdGet**](C2PACustomAssertionsAPI.md#GetSchemaApiV1EnterpriseC2paSchemasSchemaIdGet) | **Get** /api/v1/enterprise/c2pa/schemas/{schema_id} | Get Schema
[**GetTemplateApiV1EnterpriseC2paTemplatesTemplateIdGet**](C2PACustomAssertionsAPI.md#GetTemplateApiV1EnterpriseC2paTemplatesTemplateIdGet) | **Get** /api/v1/enterprise/c2pa/templates/{template_id} | Get Template
[**ListSchemasApiV1EnterpriseC2paSchemasGet**](C2PACustomAssertionsAPI.md#ListSchemasApiV1EnterpriseC2paSchemasGet) | **Get** /api/v1/enterprise/c2pa/schemas | List Schemas
[**ListTemplatesApiV1EnterpriseC2paTemplatesGet**](C2PACustomAssertionsAPI.md#ListTemplatesApiV1EnterpriseC2paTemplatesGet) | **Get** /api/v1/enterprise/c2pa/templates | List Templates
[**UpdateSchemaApiV1EnterpriseC2paSchemasSchemaIdPut**](C2PACustomAssertionsAPI.md#UpdateSchemaApiV1EnterpriseC2paSchemasSchemaIdPut) | **Put** /api/v1/enterprise/c2pa/schemas/{schema_id} | Update Schema
[**UpdateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPut**](C2PACustomAssertionsAPI.md#UpdateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPut) | **Put** /api/v1/enterprise/c2pa/templates/{template_id} | Update Template
[**ValidateAssertionApiV1EnterpriseC2paValidatePost**](C2PACustomAssertionsAPI.md#ValidateAssertionApiV1EnterpriseC2paValidatePost) | **Post** /api/v1/enterprise/c2pa/validate | Validate Assertion



## CreateSchemaApiV1EnterpriseC2paSchemasPost

> C2PASchemaResponse CreateSchemaApiV1EnterpriseC2paSchemasPost(ctx).C2PASchemaCreate(c2PASchemaCreate).Execute()

Create Schema



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
	c2PASchemaCreate := *openapiclient.NewC2PASchemaCreate("Name_example", "Label_example", map[string]interface{}{"key": interface{}(123)}) // C2PASchemaCreate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.C2PACustomAssertionsAPI.CreateSchemaApiV1EnterpriseC2paSchemasPost(context.Background()).C2PASchemaCreate(c2PASchemaCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `C2PACustomAssertionsAPI.CreateSchemaApiV1EnterpriseC2paSchemasPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateSchemaApiV1EnterpriseC2paSchemasPost`: C2PASchemaResponse
	fmt.Fprintf(os.Stdout, "Response from `C2PACustomAssertionsAPI.CreateSchemaApiV1EnterpriseC2paSchemasPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateSchemaApiV1EnterpriseC2paSchemasPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **c2PASchemaCreate** | [**C2PASchemaCreate**](C2PASchemaCreate.md) |  | 

### Return type

[**C2PASchemaResponse**](C2PASchemaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateTemplateApiV1EnterpriseC2paTemplatesPost

> C2PATemplateResponse CreateTemplateApiV1EnterpriseC2paTemplatesPost(ctx).C2PATemplateCreate(c2PATemplateCreate).Execute()

Create Template



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
	c2PATemplateCreate := *openapiclient.NewC2PATemplateCreate("Name_example", "SchemaId_example", map[string]interface{}{"key": interface{}(123)}) // C2PATemplateCreate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.C2PACustomAssertionsAPI.CreateTemplateApiV1EnterpriseC2paTemplatesPost(context.Background()).C2PATemplateCreate(c2PATemplateCreate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `C2PACustomAssertionsAPI.CreateTemplateApiV1EnterpriseC2paTemplatesPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateTemplateApiV1EnterpriseC2paTemplatesPost`: C2PATemplateResponse
	fmt.Fprintf(os.Stdout, "Response from `C2PACustomAssertionsAPI.CreateTemplateApiV1EnterpriseC2paTemplatesPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateTemplateApiV1EnterpriseC2paTemplatesPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **c2PATemplateCreate** | [**C2PATemplateCreate**](C2PATemplateCreate.md) |  | 

### Return type

[**C2PATemplateResponse**](C2PATemplateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteSchemaApiV1EnterpriseC2paSchemasSchemaIdDelete

> DeleteSchemaApiV1EnterpriseC2paSchemasSchemaIdDelete(ctx, schemaId).Execute()

Delete Schema



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
	schemaId := "schemaId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.C2PACustomAssertionsAPI.DeleteSchemaApiV1EnterpriseC2paSchemasSchemaIdDelete(context.Background(), schemaId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `C2PACustomAssertionsAPI.DeleteSchemaApiV1EnterpriseC2paSchemasSchemaIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**schemaId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteSchemaApiV1EnterpriseC2paSchemasSchemaIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

 (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteTemplateApiV1EnterpriseC2paTemplatesTemplateIdDelete

> DeleteTemplateApiV1EnterpriseC2paTemplatesTemplateIdDelete(ctx, templateId).Execute()

Delete Template



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
	templateId := "templateId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.C2PACustomAssertionsAPI.DeleteTemplateApiV1EnterpriseC2paTemplatesTemplateIdDelete(context.Background(), templateId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `C2PACustomAssertionsAPI.DeleteTemplateApiV1EnterpriseC2paTemplatesTemplateIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**templateId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteTemplateApiV1EnterpriseC2paTemplatesTemplateIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

 (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetSchemaApiV1EnterpriseC2paSchemasSchemaIdGet

> C2PASchemaResponse GetSchemaApiV1EnterpriseC2paSchemasSchemaIdGet(ctx, schemaId).Execute()

Get Schema



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
	schemaId := "schemaId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.C2PACustomAssertionsAPI.GetSchemaApiV1EnterpriseC2paSchemasSchemaIdGet(context.Background(), schemaId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `C2PACustomAssertionsAPI.GetSchemaApiV1EnterpriseC2paSchemasSchemaIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetSchemaApiV1EnterpriseC2paSchemasSchemaIdGet`: C2PASchemaResponse
	fmt.Fprintf(os.Stdout, "Response from `C2PACustomAssertionsAPI.GetSchemaApiV1EnterpriseC2paSchemasSchemaIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**schemaId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetSchemaApiV1EnterpriseC2paSchemasSchemaIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**C2PASchemaResponse**](C2PASchemaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetTemplateApiV1EnterpriseC2paTemplatesTemplateIdGet

> C2PATemplateResponse GetTemplateApiV1EnterpriseC2paTemplatesTemplateIdGet(ctx, templateId).Execute()

Get Template



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
	templateId := "templateId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.C2PACustomAssertionsAPI.GetTemplateApiV1EnterpriseC2paTemplatesTemplateIdGet(context.Background(), templateId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `C2PACustomAssertionsAPI.GetTemplateApiV1EnterpriseC2paTemplatesTemplateIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetTemplateApiV1EnterpriseC2paTemplatesTemplateIdGet`: C2PATemplateResponse
	fmt.Fprintf(os.Stdout, "Response from `C2PACustomAssertionsAPI.GetTemplateApiV1EnterpriseC2paTemplatesTemplateIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**templateId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetTemplateApiV1EnterpriseC2paTemplatesTemplateIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**C2PATemplateResponse**](C2PATemplateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListSchemasApiV1EnterpriseC2paSchemasGet

> C2PASchemaListResponse ListSchemasApiV1EnterpriseC2paSchemasGet(ctx).Page(page).PageSize(pageSize).IsPublic(isPublic).Execute()

List Schemas



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
	page := int32(56) // int32 |  (optional) (default to 1)
	pageSize := int32(56) // int32 |  (optional) (default to 50)
	isPublic := true // bool |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.C2PACustomAssertionsAPI.ListSchemasApiV1EnterpriseC2paSchemasGet(context.Background()).Page(page).PageSize(pageSize).IsPublic(isPublic).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `C2PACustomAssertionsAPI.ListSchemasApiV1EnterpriseC2paSchemasGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListSchemasApiV1EnterpriseC2paSchemasGet`: C2PASchemaListResponse
	fmt.Fprintf(os.Stdout, "Response from `C2PACustomAssertionsAPI.ListSchemasApiV1EnterpriseC2paSchemasGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListSchemasApiV1EnterpriseC2paSchemasGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int32** |  | [default to 1]
 **pageSize** | **int32** |  | [default to 50]
 **isPublic** | **bool** |  | 

### Return type

[**C2PASchemaListResponse**](C2PASchemaListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListTemplatesApiV1EnterpriseC2paTemplatesGet

> C2PATemplateListResponse ListTemplatesApiV1EnterpriseC2paTemplatesGet(ctx).Page(page).PageSize(pageSize).Category(category).Execute()

List Templates



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
	page := int32(56) // int32 |  (optional) (default to 1)
	pageSize := int32(56) // int32 |  (optional) (default to 50)
	category := "category_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.C2PACustomAssertionsAPI.ListTemplatesApiV1EnterpriseC2paTemplatesGet(context.Background()).Page(page).PageSize(pageSize).Category(category).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `C2PACustomAssertionsAPI.ListTemplatesApiV1EnterpriseC2paTemplatesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListTemplatesApiV1EnterpriseC2paTemplatesGet`: C2PATemplateListResponse
	fmt.Fprintf(os.Stdout, "Response from `C2PACustomAssertionsAPI.ListTemplatesApiV1EnterpriseC2paTemplatesGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListTemplatesApiV1EnterpriseC2paTemplatesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int32** |  | [default to 1]
 **pageSize** | **int32** |  | [default to 50]
 **category** | **string** |  | 

### Return type

[**C2PATemplateListResponse**](C2PATemplateListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateSchemaApiV1EnterpriseC2paSchemasSchemaIdPut

> C2PASchemaResponse UpdateSchemaApiV1EnterpriseC2paSchemasSchemaIdPut(ctx, schemaId).C2PASchemaUpdate(c2PASchemaUpdate).Execute()

Update Schema



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
	schemaId := "schemaId_example" // string | 
	c2PASchemaUpdate := *openapiclient.NewC2PASchemaUpdate() // C2PASchemaUpdate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.C2PACustomAssertionsAPI.UpdateSchemaApiV1EnterpriseC2paSchemasSchemaIdPut(context.Background(), schemaId).C2PASchemaUpdate(c2PASchemaUpdate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `C2PACustomAssertionsAPI.UpdateSchemaApiV1EnterpriseC2paSchemasSchemaIdPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateSchemaApiV1EnterpriseC2paSchemasSchemaIdPut`: C2PASchemaResponse
	fmt.Fprintf(os.Stdout, "Response from `C2PACustomAssertionsAPI.UpdateSchemaApiV1EnterpriseC2paSchemasSchemaIdPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**schemaId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateSchemaApiV1EnterpriseC2paSchemasSchemaIdPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **c2PASchemaUpdate** | [**C2PASchemaUpdate**](C2PASchemaUpdate.md) |  | 

### Return type

[**C2PASchemaResponse**](C2PASchemaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPut

> C2PATemplateResponse UpdateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPut(ctx, templateId).C2PATemplateUpdate(c2PATemplateUpdate).Execute()

Update Template



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
	templateId := "templateId_example" // string | 
	c2PATemplateUpdate := *openapiclient.NewC2PATemplateUpdate() // C2PATemplateUpdate | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.C2PACustomAssertionsAPI.UpdateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPut(context.Background(), templateId).C2PATemplateUpdate(c2PATemplateUpdate).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `C2PACustomAssertionsAPI.UpdateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPut`: C2PATemplateResponse
	fmt.Fprintf(os.Stdout, "Response from `C2PACustomAssertionsAPI.UpdateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**templateId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **c2PATemplateUpdate** | [**C2PATemplateUpdate**](C2PATemplateUpdate.md) |  | 

### Return type

[**C2PATemplateResponse**](C2PATemplateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ValidateAssertionApiV1EnterpriseC2paValidatePost

> C2PAAssertionValidateResponse ValidateAssertionApiV1EnterpriseC2paValidatePost(ctx).C2PAAssertionValidateRequest(c2PAAssertionValidateRequest).Execute()

Validate Assertion



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
	c2PAAssertionValidateRequest := *openapiclient.NewC2PAAssertionValidateRequest("Label_example", map[string]interface{}{"key": interface{}(123)}) // C2PAAssertionValidateRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.C2PACustomAssertionsAPI.ValidateAssertionApiV1EnterpriseC2paValidatePost(context.Background()).C2PAAssertionValidateRequest(c2PAAssertionValidateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `C2PACustomAssertionsAPI.ValidateAssertionApiV1EnterpriseC2paValidatePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ValidateAssertionApiV1EnterpriseC2paValidatePost`: C2PAAssertionValidateResponse
	fmt.Fprintf(os.Stdout, "Response from `C2PACustomAssertionsAPI.ValidateAssertionApiV1EnterpriseC2paValidatePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiValidateAssertionApiV1EnterpriseC2paValidatePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **c2PAAssertionValidateRequest** | [**C2PAAssertionValidateRequest**](C2PAAssertionValidateRequest.md) |  | 

### Return type

[**C2PAAssertionValidateResponse**](C2PAAssertionValidateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

