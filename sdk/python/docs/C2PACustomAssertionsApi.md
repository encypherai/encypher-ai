# encypher.C2PACustomAssertionsApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_schema_api_v1_enterprise_c2pa_schemas_post**](C2PACustomAssertionsApi.md#create_schema_api_v1_enterprise_c2pa_schemas_post) | **POST** /api/v1/enterprise/c2pa/schemas | Create Schema
[**create_template_api_v1_enterprise_c2pa_templates_post**](C2PACustomAssertionsApi.md#create_template_api_v1_enterprise_c2pa_templates_post) | **POST** /api/v1/enterprise/c2pa/templates | Create Template
[**delete_schema_api_v1_enterprise_c2pa_schemas_schema_id_delete**](C2PACustomAssertionsApi.md#delete_schema_api_v1_enterprise_c2pa_schemas_schema_id_delete) | **DELETE** /api/v1/enterprise/c2pa/schemas/{schema_id} | Delete Schema
[**delete_template_api_v1_enterprise_c2pa_templates_template_id_delete**](C2PACustomAssertionsApi.md#delete_template_api_v1_enterprise_c2pa_templates_template_id_delete) | **DELETE** /api/v1/enterprise/c2pa/templates/{template_id} | Delete Template
[**get_schema_api_v1_enterprise_c2pa_schemas_schema_id_get**](C2PACustomAssertionsApi.md#get_schema_api_v1_enterprise_c2pa_schemas_schema_id_get) | **GET** /api/v1/enterprise/c2pa/schemas/{schema_id} | Get Schema
[**get_template_api_v1_enterprise_c2pa_templates_template_id_get**](C2PACustomAssertionsApi.md#get_template_api_v1_enterprise_c2pa_templates_template_id_get) | **GET** /api/v1/enterprise/c2pa/templates/{template_id} | Get Template
[**list_schemas_api_v1_enterprise_c2pa_schemas_get**](C2PACustomAssertionsApi.md#list_schemas_api_v1_enterprise_c2pa_schemas_get) | **GET** /api/v1/enterprise/c2pa/schemas | List Schemas
[**list_templates_api_v1_enterprise_c2pa_templates_get**](C2PACustomAssertionsApi.md#list_templates_api_v1_enterprise_c2pa_templates_get) | **GET** /api/v1/enterprise/c2pa/templates | List Templates
[**update_schema_api_v1_enterprise_c2pa_schemas_schema_id_put**](C2PACustomAssertionsApi.md#update_schema_api_v1_enterprise_c2pa_schemas_schema_id_put) | **PUT** /api/v1/enterprise/c2pa/schemas/{schema_id} | Update Schema
[**update_template_api_v1_enterprise_c2pa_templates_template_id_put**](C2PACustomAssertionsApi.md#update_template_api_v1_enterprise_c2pa_templates_template_id_put) | **PUT** /api/v1/enterprise/c2pa/templates/{template_id} | Update Template
[**validate_assertion_api_v1_enterprise_c2pa_validate_post**](C2PACustomAssertionsApi.md#validate_assertion_api_v1_enterprise_c2pa_validate_post) | **POST** /api/v1/enterprise/c2pa/validate | Validate Assertion


# **create_schema_api_v1_enterprise_c2pa_schemas_post**
> C2PASchemaResponse create_schema_api_v1_enterprise_c2pa_schemas_post(c2_pa_schema_create)

Create Schema

Register a custom C2PA assertion schema.

Allows organizations to define custom assertion types with
JSON Schema validation rules.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.c2_pa_schema_create import C2PASchemaCreate
from encypher.models.c2_pa_schema_response import C2PASchemaResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = encypher.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.C2PACustomAssertionsApi(api_client)
    c2_pa_schema_create = encypher.C2PASchemaCreate() # C2PASchemaCreate |

    try:
        # Create Schema
        api_response = api_instance.create_schema_api_v1_enterprise_c2pa_schemas_post(c2_pa_schema_create)
        print("The response of C2PACustomAssertionsApi->create_schema_api_v1_enterprise_c2pa_schemas_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling C2PACustomAssertionsApi->create_schema_api_v1_enterprise_c2pa_schemas_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **c2_pa_schema_create** | [**C2PASchemaCreate**](C2PASchemaCreate.md)|  |

### Return type

[**C2PASchemaResponse**](C2PASchemaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_template_api_v1_enterprise_c2pa_templates_post**
> C2PATemplateResponse create_template_api_v1_enterprise_c2pa_templates_post(c2_pa_template_create)

Create Template

Create a new assertion template.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.c2_pa_template_create import C2PATemplateCreate
from encypher.models.c2_pa_template_response import C2PATemplateResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = encypher.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.C2PACustomAssertionsApi(api_client)
    c2_pa_template_create = encypher.C2PATemplateCreate() # C2PATemplateCreate |

    try:
        # Create Template
        api_response = api_instance.create_template_api_v1_enterprise_c2pa_templates_post(c2_pa_template_create)
        print("The response of C2PACustomAssertionsApi->create_template_api_v1_enterprise_c2pa_templates_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling C2PACustomAssertionsApi->create_template_api_v1_enterprise_c2pa_templates_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **c2_pa_template_create** | [**C2PATemplateCreate**](C2PATemplateCreate.md)|  |

### Return type

[**C2PATemplateResponse**](C2PATemplateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_schema_api_v1_enterprise_c2pa_schemas_schema_id_delete**
> delete_schema_api_v1_enterprise_c2pa_schemas_schema_id_delete(schema_id)

Delete Schema

Delete a C2PA assertion schema.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = encypher.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.C2PACustomAssertionsApi(api_client)
    schema_id = 'schema_id_example' # str |

    try:
        # Delete Schema
        api_instance.delete_schema_api_v1_enterprise_c2pa_schemas_schema_id_delete(schema_id)
    except Exception as e:
        print("Exception when calling C2PACustomAssertionsApi->delete_schema_api_v1_enterprise_c2pa_schemas_schema_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **schema_id** | **str**|  |

### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_template_api_v1_enterprise_c2pa_templates_template_id_delete**
> delete_template_api_v1_enterprise_c2pa_templates_template_id_delete(template_id)

Delete Template

Delete an assertion template.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = encypher.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.C2PACustomAssertionsApi(api_client)
    template_id = 'template_id_example' # str |

    try:
        # Delete Template
        api_instance.delete_template_api_v1_enterprise_c2pa_templates_template_id_delete(template_id)
    except Exception as e:
        print("Exception when calling C2PACustomAssertionsApi->delete_template_api_v1_enterprise_c2pa_templates_template_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **template_id** | **str**|  |

### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_schema_api_v1_enterprise_c2pa_schemas_schema_id_get**
> C2PASchemaResponse get_schema_api_v1_enterprise_c2pa_schemas_schema_id_get(schema_id)

Get Schema

Get a specific C2PA assertion schema.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.c2_pa_schema_response import C2PASchemaResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = encypher.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.C2PACustomAssertionsApi(api_client)
    schema_id = 'schema_id_example' # str |

    try:
        # Get Schema
        api_response = api_instance.get_schema_api_v1_enterprise_c2pa_schemas_schema_id_get(schema_id)
        print("The response of C2PACustomAssertionsApi->get_schema_api_v1_enterprise_c2pa_schemas_schema_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling C2PACustomAssertionsApi->get_schema_api_v1_enterprise_c2pa_schemas_schema_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **schema_id** | **str**|  |

### Return type

[**C2PASchemaResponse**](C2PASchemaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_template_api_v1_enterprise_c2pa_templates_template_id_get**
> C2PATemplateResponse get_template_api_v1_enterprise_c2pa_templates_template_id_get(template_id)

Get Template

Get a specific assertion template.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.c2_pa_template_response import C2PATemplateResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = encypher.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.C2PACustomAssertionsApi(api_client)
    template_id = 'template_id_example' # str |

    try:
        # Get Template
        api_response = api_instance.get_template_api_v1_enterprise_c2pa_templates_template_id_get(template_id)
        print("The response of C2PACustomAssertionsApi->get_template_api_v1_enterprise_c2pa_templates_template_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling C2PACustomAssertionsApi->get_template_api_v1_enterprise_c2pa_templates_template_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **template_id** | **str**|  |

### Return type

[**C2PATemplateResponse**](C2PATemplateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_schemas_api_v1_enterprise_c2pa_schemas_get**
> C2PASchemaListResponse list_schemas_api_v1_enterprise_c2pa_schemas_get(page=page, page_size=page_size, is_public=is_public)

List Schemas

List available C2PA assertion schemas.

Returns schemas owned by the organization or public schemas.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.c2_pa_schema_list_response import C2PASchemaListResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = encypher.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.C2PACustomAssertionsApi(api_client)
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    is_public = True # bool |  (optional)

    try:
        # List Schemas
        api_response = api_instance.list_schemas_api_v1_enterprise_c2pa_schemas_get(page=page, page_size=page_size, is_public=is_public)
        print("The response of C2PACustomAssertionsApi->list_schemas_api_v1_enterprise_c2pa_schemas_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling C2PACustomAssertionsApi->list_schemas_api_v1_enterprise_c2pa_schemas_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]
 **is_public** | **bool**|  | [optional]

### Return type

[**C2PASchemaListResponse**](C2PASchemaListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_templates_api_v1_enterprise_c2pa_templates_get**
> C2PATemplateListResponse list_templates_api_v1_enterprise_c2pa_templates_get(page=page, page_size=page_size, category=category)

List Templates

List available assertion templates.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.c2_pa_template_list_response import C2PATemplateListResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = encypher.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.C2PACustomAssertionsApi(api_client)
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    category = 'category_example' # str |  (optional)

    try:
        # List Templates
        api_response = api_instance.list_templates_api_v1_enterprise_c2pa_templates_get(page=page, page_size=page_size, category=category)
        print("The response of C2PACustomAssertionsApi->list_templates_api_v1_enterprise_c2pa_templates_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling C2PACustomAssertionsApi->list_templates_api_v1_enterprise_c2pa_templates_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]
 **category** | **str**|  | [optional]

### Return type

[**C2PATemplateListResponse**](C2PATemplateListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_schema_api_v1_enterprise_c2pa_schemas_schema_id_put**
> C2PASchemaResponse update_schema_api_v1_enterprise_c2pa_schemas_schema_id_put(schema_id, c2_pa_schema_update)

Update Schema

Update a C2PA assertion schema.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.c2_pa_schema_response import C2PASchemaResponse
from encypher.models.c2_pa_schema_update import C2PASchemaUpdate
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = encypher.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.C2PACustomAssertionsApi(api_client)
    schema_id = 'schema_id_example' # str |
    c2_pa_schema_update = encypher.C2PASchemaUpdate() # C2PASchemaUpdate |

    try:
        # Update Schema
        api_response = api_instance.update_schema_api_v1_enterprise_c2pa_schemas_schema_id_put(schema_id, c2_pa_schema_update)
        print("The response of C2PACustomAssertionsApi->update_schema_api_v1_enterprise_c2pa_schemas_schema_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling C2PACustomAssertionsApi->update_schema_api_v1_enterprise_c2pa_schemas_schema_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **schema_id** | **str**|  |
 **c2_pa_schema_update** | [**C2PASchemaUpdate**](C2PASchemaUpdate.md)|  |

### Return type

[**C2PASchemaResponse**](C2PASchemaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_template_api_v1_enterprise_c2pa_templates_template_id_put**
> C2PATemplateResponse update_template_api_v1_enterprise_c2pa_templates_template_id_put(template_id, c2_pa_template_update)

Update Template

Update an assertion template.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.c2_pa_template_response import C2PATemplateResponse
from encypher.models.c2_pa_template_update import C2PATemplateUpdate
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = encypher.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.C2PACustomAssertionsApi(api_client)
    template_id = 'template_id_example' # str |
    c2_pa_template_update = encypher.C2PATemplateUpdate() # C2PATemplateUpdate |

    try:
        # Update Template
        api_response = api_instance.update_template_api_v1_enterprise_c2pa_templates_template_id_put(template_id, c2_pa_template_update)
        print("The response of C2PACustomAssertionsApi->update_template_api_v1_enterprise_c2pa_templates_template_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling C2PACustomAssertionsApi->update_template_api_v1_enterprise_c2pa_templates_template_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **template_id** | **str**|  |
 **c2_pa_template_update** | [**C2PATemplateUpdate**](C2PATemplateUpdate.md)|  |

### Return type

[**C2PATemplateResponse**](C2PATemplateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validate_assertion_api_v1_enterprise_c2pa_validate_post**
> C2PAAssertionValidateResponse validate_assertion_api_v1_enterprise_c2pa_validate_post(c2_pa_assertion_validate_request)

Validate Assertion

Validate a C2PA assertion before embedding.

Checks the assertion data against its registered schema.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.c2_pa_assertion_validate_request import C2PAAssertionValidateRequest
from encypher.models.c2_pa_assertion_validate_response import C2PAAssertionValidateResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = encypher.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.C2PACustomAssertionsApi(api_client)
    c2_pa_assertion_validate_request = encypher.C2PAAssertionValidateRequest() # C2PAAssertionValidateRequest |

    try:
        # Validate Assertion
        api_response = api_instance.validate_assertion_api_v1_enterprise_c2pa_validate_post(c2_pa_assertion_validate_request)
        print("The response of C2PACustomAssertionsApi->validate_assertion_api_v1_enterprise_c2pa_validate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling C2PACustomAssertionsApi->validate_assertion_api_v1_enterprise_c2pa_validate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **c2_pa_assertion_validate_request** | [**C2PAAssertionValidateRequest**](C2PAAssertionValidateRequest.md)|  |

### Return type

[**C2PAAssertionValidateResponse**](C2PAAssertionValidateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
