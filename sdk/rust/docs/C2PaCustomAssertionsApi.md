# \C2PaCustomAssertionsApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_schema_api_v1_enterprise_c2pa_schemas_post**](C2PaCustomAssertionsApi.md#create_schema_api_v1_enterprise_c2pa_schemas_post) | **POST** /api/v1/enterprise/c2pa/schemas | Create Schema
[**create_template_api_v1_enterprise_c2pa_templates_post**](C2PaCustomAssertionsApi.md#create_template_api_v1_enterprise_c2pa_templates_post) | **POST** /api/v1/enterprise/c2pa/templates | Create Template
[**delete_schema_api_v1_enterprise_c2pa_schemas_schema_id_delete**](C2PaCustomAssertionsApi.md#delete_schema_api_v1_enterprise_c2pa_schemas_schema_id_delete) | **DELETE** /api/v1/enterprise/c2pa/schemas/{schema_id} | Delete Schema
[**delete_template_api_v1_enterprise_c2pa_templates_template_id_delete**](C2PaCustomAssertionsApi.md#delete_template_api_v1_enterprise_c2pa_templates_template_id_delete) | **DELETE** /api/v1/enterprise/c2pa/templates/{template_id} | Delete Template
[**get_schema_api_v1_enterprise_c2pa_schemas_schema_id_get**](C2PaCustomAssertionsApi.md#get_schema_api_v1_enterprise_c2pa_schemas_schema_id_get) | **GET** /api/v1/enterprise/c2pa/schemas/{schema_id} | Get Schema
[**get_template_api_v1_enterprise_c2pa_templates_template_id_get**](C2PaCustomAssertionsApi.md#get_template_api_v1_enterprise_c2pa_templates_template_id_get) | **GET** /api/v1/enterprise/c2pa/templates/{template_id} | Get Template
[**list_schemas_api_v1_enterprise_c2pa_schemas_get**](C2PaCustomAssertionsApi.md#list_schemas_api_v1_enterprise_c2pa_schemas_get) | **GET** /api/v1/enterprise/c2pa/schemas | List Schemas
[**list_templates_api_v1_enterprise_c2pa_templates_get**](C2PaCustomAssertionsApi.md#list_templates_api_v1_enterprise_c2pa_templates_get) | **GET** /api/v1/enterprise/c2pa/templates | List Templates
[**update_schema_api_v1_enterprise_c2pa_schemas_schema_id_put**](C2PaCustomAssertionsApi.md#update_schema_api_v1_enterprise_c2pa_schemas_schema_id_put) | **PUT** /api/v1/enterprise/c2pa/schemas/{schema_id} | Update Schema
[**update_template_api_v1_enterprise_c2pa_templates_template_id_put**](C2PaCustomAssertionsApi.md#update_template_api_v1_enterprise_c2pa_templates_template_id_put) | **PUT** /api/v1/enterprise/c2pa/templates/{template_id} | Update Template
[**validate_assertion_api_v1_enterprise_c2pa_validate_post**](C2PaCustomAssertionsApi.md#validate_assertion_api_v1_enterprise_c2pa_validate_post) | **POST** /api/v1/enterprise/c2pa/validate | Validate Assertion



## create_schema_api_v1_enterprise_c2pa_schemas_post

> models::C2PaSchemaResponse create_schema_api_v1_enterprise_c2pa_schemas_post(c2_pa_schema_create)
Create Schema

Register a custom C2PA assertion schema.  Allows organizations to define custom assertion types with JSON Schema validation rules.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**c2_pa_schema_create** | [**C2PaSchemaCreate**](C2PaSchemaCreate.md) |  | [required] |

### Return type

[**models::C2PaSchemaResponse**](C2PASchemaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## create_template_api_v1_enterprise_c2pa_templates_post

> models::C2PaTemplateResponse create_template_api_v1_enterprise_c2pa_templates_post(c2_pa_template_create)
Create Template

Create a new assertion template.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**c2_pa_template_create** | [**C2PaTemplateCreate**](C2PaTemplateCreate.md) |  | [required] |

### Return type

[**models::C2PaTemplateResponse**](C2PATemplateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## delete_schema_api_v1_enterprise_c2pa_schemas_schema_id_delete

> delete_schema_api_v1_enterprise_c2pa_schemas_schema_id_delete(schema_id)
Delete Schema

Delete a C2PA assertion schema.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**schema_id** | **String** |  | [required] |

### Return type

 (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## delete_template_api_v1_enterprise_c2pa_templates_template_id_delete

> delete_template_api_v1_enterprise_c2pa_templates_template_id_delete(template_id)
Delete Template

Delete an assertion template.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**template_id** | **String** |  | [required] |

### Return type

 (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_schema_api_v1_enterprise_c2pa_schemas_schema_id_get

> models::C2PaSchemaResponse get_schema_api_v1_enterprise_c2pa_schemas_schema_id_get(schema_id)
Get Schema

Get a specific C2PA assertion schema.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**schema_id** | **String** |  | [required] |

### Return type

[**models::C2PaSchemaResponse**](C2PASchemaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_template_api_v1_enterprise_c2pa_templates_template_id_get

> models::C2PaTemplateResponse get_template_api_v1_enterprise_c2pa_templates_template_id_get(template_id)
Get Template

Get a specific assertion template.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**template_id** | **String** |  | [required] |

### Return type

[**models::C2PaTemplateResponse**](C2PATemplateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_schemas_api_v1_enterprise_c2pa_schemas_get

> models::C2PaSchemaListResponse list_schemas_api_v1_enterprise_c2pa_schemas_get(page, page_size, is_public)
List Schemas

List available C2PA assertion schemas.  Returns schemas owned by the organization or public schemas.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**page** | Option<**i32**> |  |  |[default to 1]
**page_size** | Option<**i32**> |  |  |[default to 50]
**is_public** | Option<**bool**> |  |  |

### Return type

[**models::C2PaSchemaListResponse**](C2PASchemaListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_templates_api_v1_enterprise_c2pa_templates_get

> models::C2PaTemplateListResponse list_templates_api_v1_enterprise_c2pa_templates_get(page, page_size, category)
List Templates

List available assertion templates.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**page** | Option<**i32**> |  |  |[default to 1]
**page_size** | Option<**i32**> |  |  |[default to 50]
**category** | Option<**String**> |  |  |

### Return type

[**models::C2PaTemplateListResponse**](C2PATemplateListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## update_schema_api_v1_enterprise_c2pa_schemas_schema_id_put

> models::C2PaSchemaResponse update_schema_api_v1_enterprise_c2pa_schemas_schema_id_put(schema_id, c2_pa_schema_update)
Update Schema

Update a C2PA assertion schema.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**schema_id** | **String** |  | [required] |
**c2_pa_schema_update** | [**C2PaSchemaUpdate**](C2PaSchemaUpdate.md) |  | [required] |

### Return type

[**models::C2PaSchemaResponse**](C2PASchemaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## update_template_api_v1_enterprise_c2pa_templates_template_id_put

> models::C2PaTemplateResponse update_template_api_v1_enterprise_c2pa_templates_template_id_put(template_id, c2_pa_template_update)
Update Template

Update an assertion template.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**template_id** | **String** |  | [required] |
**c2_pa_template_update** | [**C2PaTemplateUpdate**](C2PaTemplateUpdate.md) |  | [required] |

### Return type

[**models::C2PaTemplateResponse**](C2PATemplateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## validate_assertion_api_v1_enterprise_c2pa_validate_post

> models::C2PaAssertionValidateResponse validate_assertion_api_v1_enterprise_c2pa_validate_post(c2_pa_assertion_validate_request)
Validate Assertion

Validate a C2PA assertion before embedding.  Checks the assertion data against its registered schema.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**c2_pa_assertion_validate_request** | [**C2PaAssertionValidateRequest**](C2PaAssertionValidateRequest.md) |  | [required] |

### Return type

[**models::C2PaAssertionValidateResponse**](C2PAAssertionValidateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
