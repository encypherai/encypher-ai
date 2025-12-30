# C2PACustomAssertionsApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createSchemaApiV1EnterpriseC2paSchemasPost**](C2PACustomAssertionsApi.md#createschemaapiv1enterprisec2paschemaspost) | **POST** /api/v1/enterprise/c2pa/schemas | Create Schema |
| [**createTemplateApiV1EnterpriseC2paTemplatesPost**](C2PACustomAssertionsApi.md#createtemplateapiv1enterprisec2patemplatespost) | **POST** /api/v1/enterprise/c2pa/templates | Create Template |
| [**deleteSchemaApiV1EnterpriseC2paSchemasSchemaIdDelete**](C2PACustomAssertionsApi.md#deleteschemaapiv1enterprisec2paschemasschemaiddelete) | **DELETE** /api/v1/enterprise/c2pa/schemas/{schema_id} | Delete Schema |
| [**deleteTemplateApiV1EnterpriseC2paTemplatesTemplateIdDelete**](C2PACustomAssertionsApi.md#deletetemplateapiv1enterprisec2patemplatestemplateiddelete) | **DELETE** /api/v1/enterprise/c2pa/templates/{template_id} | Delete Template |
| [**getSchemaApiV1EnterpriseC2paSchemasSchemaIdGet**](C2PACustomAssertionsApi.md#getschemaapiv1enterprisec2paschemasschemaidget) | **GET** /api/v1/enterprise/c2pa/schemas/{schema_id} | Get Schema |
| [**getTemplateApiV1EnterpriseC2paTemplatesTemplateIdGet**](C2PACustomAssertionsApi.md#gettemplateapiv1enterprisec2patemplatestemplateidget) | **GET** /api/v1/enterprise/c2pa/templates/{template_id} | Get Template |
| [**listSchemasApiV1EnterpriseC2paSchemasGet**](C2PACustomAssertionsApi.md#listschemasapiv1enterprisec2paschemasget) | **GET** /api/v1/enterprise/c2pa/schemas | List Schemas |
| [**listTemplatesApiV1EnterpriseC2paTemplatesGet**](C2PACustomAssertionsApi.md#listtemplatesapiv1enterprisec2patemplatesget) | **GET** /api/v1/enterprise/c2pa/templates | List Templates |
| [**updateSchemaApiV1EnterpriseC2paSchemasSchemaIdPut**](C2PACustomAssertionsApi.md#updateschemaapiv1enterprisec2paschemasschemaidput) | **PUT** /api/v1/enterprise/c2pa/schemas/{schema_id} | Update Schema |
| [**updateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPut**](C2PACustomAssertionsApi.md#updatetemplateapiv1enterprisec2patemplatestemplateidput) | **PUT** /api/v1/enterprise/c2pa/templates/{template_id} | Update Template |
| [**validateAssertionApiV1EnterpriseC2paValidatePost**](C2PACustomAssertionsApi.md#validateassertionapiv1enterprisec2pavalidatepost) | **POST** /api/v1/enterprise/c2pa/validate | Validate Assertion |



## createSchemaApiV1EnterpriseC2paSchemasPost

> C2PASchemaResponse createSchemaApiV1EnterpriseC2paSchemasPost(c2PASchemaCreate)

Create Schema

Register a custom C2PA assertion schema.  Allows organizations to define custom assertion types with JSON Schema validation rules.

### Example

```ts
import {
  Configuration,
  C2PACustomAssertionsApi,
} from '@encypher/sdk';
import type { CreateSchemaApiV1EnterpriseC2paSchemasPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new C2PACustomAssertionsApi(config);

  const body = {
    // C2PASchemaCreate
    c2PASchemaCreate: ...,
  } satisfies CreateSchemaApiV1EnterpriseC2paSchemasPostRequest;

  try {
    const data = await api.createSchemaApiV1EnterpriseC2paSchemasPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **c2PASchemaCreate** | [C2PASchemaCreate](C2PASchemaCreate.md) |  | |

### Return type

[**C2PASchemaResponse**](C2PASchemaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## createTemplateApiV1EnterpriseC2paTemplatesPost

> C2PATemplateResponse createTemplateApiV1EnterpriseC2paTemplatesPost(c2PATemplateCreate)

Create Template

Create a new assertion template.

### Example

```ts
import {
  Configuration,
  C2PACustomAssertionsApi,
} from '@encypher/sdk';
import type { CreateTemplateApiV1EnterpriseC2paTemplatesPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new C2PACustomAssertionsApi(config);

  const body = {
    // C2PATemplateCreate
    c2PATemplateCreate: ...,
  } satisfies CreateTemplateApiV1EnterpriseC2paTemplatesPostRequest;

  try {
    const data = await api.createTemplateApiV1EnterpriseC2paTemplatesPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **c2PATemplateCreate** | [C2PATemplateCreate](C2PATemplateCreate.md) |  | |

### Return type

[**C2PATemplateResponse**](C2PATemplateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## deleteSchemaApiV1EnterpriseC2paSchemasSchemaIdDelete

> deleteSchemaApiV1EnterpriseC2paSchemasSchemaIdDelete(schemaId)

Delete Schema

Delete a C2PA assertion schema.

### Example

```ts
import {
  Configuration,
  C2PACustomAssertionsApi,
} from '@encypher/sdk';
import type { DeleteSchemaApiV1EnterpriseC2paSchemasSchemaIdDeleteRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new C2PACustomAssertionsApi(config);

  const body = {
    // string
    schemaId: schemaId_example,
  } satisfies DeleteSchemaApiV1EnterpriseC2paSchemasSchemaIdDeleteRequest;

  try {
    const data = await api.deleteSchemaApiV1EnterpriseC2paSchemasSchemaIdDelete(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **schemaId** | `string` |  | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## deleteTemplateApiV1EnterpriseC2paTemplatesTemplateIdDelete

> deleteTemplateApiV1EnterpriseC2paTemplatesTemplateIdDelete(templateId)

Delete Template

Delete an assertion template.

### Example

```ts
import {
  Configuration,
  C2PACustomAssertionsApi,
} from '@encypher/sdk';
import type { DeleteTemplateApiV1EnterpriseC2paTemplatesTemplateIdDeleteRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new C2PACustomAssertionsApi(config);

  const body = {
    // string
    templateId: templateId_example,
  } satisfies DeleteTemplateApiV1EnterpriseC2paTemplatesTemplateIdDeleteRequest;

  try {
    const data = await api.deleteTemplateApiV1EnterpriseC2paTemplatesTemplateIdDelete(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **templateId** | `string` |  | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getSchemaApiV1EnterpriseC2paSchemasSchemaIdGet

> C2PASchemaResponse getSchemaApiV1EnterpriseC2paSchemasSchemaIdGet(schemaId)

Get Schema

Get a specific C2PA assertion schema.

### Example

```ts
import {
  Configuration,
  C2PACustomAssertionsApi,
} from '@encypher/sdk';
import type { GetSchemaApiV1EnterpriseC2paSchemasSchemaIdGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new C2PACustomAssertionsApi(config);

  const body = {
    // string
    schemaId: schemaId_example,
  } satisfies GetSchemaApiV1EnterpriseC2paSchemasSchemaIdGetRequest;

  try {
    const data = await api.getSchemaApiV1EnterpriseC2paSchemasSchemaIdGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **schemaId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**C2PASchemaResponse**](C2PASchemaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getTemplateApiV1EnterpriseC2paTemplatesTemplateIdGet

> C2PATemplateResponse getTemplateApiV1EnterpriseC2paTemplatesTemplateIdGet(templateId)

Get Template

Get a specific assertion template.

### Example

```ts
import {
  Configuration,
  C2PACustomAssertionsApi,
} from '@encypher/sdk';
import type { GetTemplateApiV1EnterpriseC2paTemplatesTemplateIdGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new C2PACustomAssertionsApi(config);

  const body = {
    // string
    templateId: templateId_example,
  } satisfies GetTemplateApiV1EnterpriseC2paTemplatesTemplateIdGetRequest;

  try {
    const data = await api.getTemplateApiV1EnterpriseC2paTemplatesTemplateIdGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **templateId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**C2PATemplateResponse**](C2PATemplateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listSchemasApiV1EnterpriseC2paSchemasGet

> C2PASchemaListResponse listSchemasApiV1EnterpriseC2paSchemasGet(page, pageSize, isPublic)

List Schemas

List available C2PA assertion schemas.  Returns schemas owned by the organization or public schemas.

### Example

```ts
import {
  Configuration,
  C2PACustomAssertionsApi,
} from '@encypher/sdk';
import type { ListSchemasApiV1EnterpriseC2paSchemasGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new C2PACustomAssertionsApi(config);

  const body = {
    // number (optional)
    page: 56,
    // number (optional)
    pageSize: 56,
    // boolean (optional)
    isPublic: true,
  } satisfies ListSchemasApiV1EnterpriseC2paSchemasGetRequest;

  try {
    const data = await api.listSchemasApiV1EnterpriseC2paSchemasGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **page** | `number` |  | [Optional] [Defaults to `1`] |
| **pageSize** | `number` |  | [Optional] [Defaults to `50`] |
| **isPublic** | `boolean` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**C2PASchemaListResponse**](C2PASchemaListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listTemplatesApiV1EnterpriseC2paTemplatesGet

> C2PATemplateListResponse listTemplatesApiV1EnterpriseC2paTemplatesGet(page, pageSize, category)

List Templates

List available assertion templates.

### Example

```ts
import {
  Configuration,
  C2PACustomAssertionsApi,
} from '@encypher/sdk';
import type { ListTemplatesApiV1EnterpriseC2paTemplatesGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new C2PACustomAssertionsApi(config);

  const body = {
    // number (optional)
    page: 56,
    // number (optional)
    pageSize: 56,
    // string (optional)
    category: category_example,
  } satisfies ListTemplatesApiV1EnterpriseC2paTemplatesGetRequest;

  try {
    const data = await api.listTemplatesApiV1EnterpriseC2paTemplatesGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **page** | `number` |  | [Optional] [Defaults to `1`] |
| **pageSize** | `number` |  | [Optional] [Defaults to `50`] |
| **category** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**C2PATemplateListResponse**](C2PATemplateListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## updateSchemaApiV1EnterpriseC2paSchemasSchemaIdPut

> C2PASchemaResponse updateSchemaApiV1EnterpriseC2paSchemasSchemaIdPut(schemaId, c2PASchemaUpdate)

Update Schema

Update a C2PA assertion schema.

### Example

```ts
import {
  Configuration,
  C2PACustomAssertionsApi,
} from '@encypher/sdk';
import type { UpdateSchemaApiV1EnterpriseC2paSchemasSchemaIdPutRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new C2PACustomAssertionsApi(config);

  const body = {
    // string
    schemaId: schemaId_example,
    // C2PASchemaUpdate
    c2PASchemaUpdate: ...,
  } satisfies UpdateSchemaApiV1EnterpriseC2paSchemasSchemaIdPutRequest;

  try {
    const data = await api.updateSchemaApiV1EnterpriseC2paSchemasSchemaIdPut(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **schemaId** | `string` |  | [Defaults to `undefined`] |
| **c2PASchemaUpdate** | [C2PASchemaUpdate](C2PASchemaUpdate.md) |  | |

### Return type

[**C2PASchemaResponse**](C2PASchemaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## updateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPut

> C2PATemplateResponse updateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPut(templateId, c2PATemplateUpdate)

Update Template

Update an assertion template.

### Example

```ts
import {
  Configuration,
  C2PACustomAssertionsApi,
} from '@encypher/sdk';
import type { UpdateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPutRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new C2PACustomAssertionsApi(config);

  const body = {
    // string
    templateId: templateId_example,
    // C2PATemplateUpdate
    c2PATemplateUpdate: ...,
  } satisfies UpdateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPutRequest;

  try {
    const data = await api.updateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPut(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **templateId** | `string` |  | [Defaults to `undefined`] |
| **c2PATemplateUpdate** | [C2PATemplateUpdate](C2PATemplateUpdate.md) |  | |

### Return type

[**C2PATemplateResponse**](C2PATemplateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## validateAssertionApiV1EnterpriseC2paValidatePost

> C2PAAssertionValidateResponse validateAssertionApiV1EnterpriseC2paValidatePost(c2PAAssertionValidateRequest)

Validate Assertion

Validate a C2PA assertion before embedding.  Checks the assertion data against its registered schema.

### Example

```ts
import {
  Configuration,
  C2PACustomAssertionsApi,
} from '@encypher/sdk';
import type { ValidateAssertionApiV1EnterpriseC2paValidatePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new C2PACustomAssertionsApi(config);

  const body = {
    // C2PAAssertionValidateRequest
    c2PAAssertionValidateRequest: ...,
  } satisfies ValidateAssertionApiV1EnterpriseC2paValidatePostRequest;

  try {
    const data = await api.validateAssertionApiV1EnterpriseC2paValidatePost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **c2PAAssertionValidateRequest** | [C2PAAssertionValidateRequest](C2PAAssertionValidateRequest.md) |  | |

### Return type

[**C2PAAssertionValidateResponse**](C2PAAssertionValidateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

