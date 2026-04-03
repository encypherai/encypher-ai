# encypher.PublicRightsApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_document_rights_api_v1_public_rights_document_id_get**](PublicRightsApi.md#get_document_rights_api_v1_public_rights_document_id_get) | **GET** /api/v1/public/rights/{document_id} | Resolve rights for a specific document
[**get_document_rights_json_ld_api_v1_public_rights_document_id_json_ld_get**](PublicRightsApi.md#get_document_rights_json_ld_api_v1_public_rights_document_id_json_ld_get) | **GET** /api/v1/public/rights/{document_id}/json-ld | Rights as JSON-LD (Schema.org compatible)
[**get_document_rights_odrl_api_v1_public_rights_document_id_odrl_get**](PublicRightsApi.md#get_document_rights_odrl_api_v1_public_rights_document_id_odrl_get) | **GET** /api/v1/public/rights/{document_id}/odrl | Rights as ODRL (W3C Open Digital Rights Language)
[**get_org_rights_profile_api_v1_public_rights_organization_org_id_get**](PublicRightsApi.md#get_org_rights_profile_api_v1_public_rights_organization_org_id_get) | **GET** /api/v1/public/rights/organization/{org_id} | Get default rights profile for a publisher organization
[**get_robots_meta_api_v1_public_rights_organization_org_id_robots_meta_get**](PublicRightsApi.md#get_robots_meta_api_v1_public_rights_organization_org_id_robots_meta_get) | **GET** /api/v1/public/rights/organization/{org_id}/robots-meta | Generate AI-specific robots meta directives
[**get_robots_txt_additions_api_v1_public_rights_organization_org_id_robots_txt_get**](PublicRightsApi.md#get_robots_txt_additions_api_v1_public_rights_organization_org_id_robots_txt_get) | **GET** /api/v1/public/rights/organization/{org_id}/robots-txt | Generate robots.txt additions with RSL directives
[**get_rsl_xml_api_v1_public_rights_organization_org_id_rsl_get**](PublicRightsApi.md#get_rsl_xml_api_v1_public_rights_organization_org_id_rsl_get) | **GET** /api/v1/public/rights/organization/{org_id}/rsl | Generate RSL 1.0 XML document
[**resolve_rights_from_text_api_v1_public_rights_resolve_post**](PublicRightsApi.md#resolve_rights_from_text_api_v1_public_rights_resolve_post) | **POST** /api/v1/public/rights/resolve | Resolve rights from raw text with embedded markers
[**rsl_olp_token_api_v1_public_rights_rsl_olp_token_post**](PublicRightsApi.md#rsl_olp_token_api_v1_public_rights_rsl_olp_token_post) | **POST** /api/v1/public/rights/rsl/olp/token | RSL Open License Protocol token endpoint
[**validate_olp_token_api_v1_public_rights_rsl_olp_validate_token_get**](PublicRightsApi.md#validate_olp_token_api_v1_public_rights_rsl_olp_validate_token_get) | **GET** /api/v1/public/rights/rsl/olp/validate/{token} | Validate an OLP token


# **get_document_rights_api_v1_public_rights_document_id_get**
> Dict[str, object] get_document_rights_api_v1_public_rights_document_id_get(document_id, endpoint_type=endpoint_type)

Resolve rights for a specific document

Resolve the full rights and licensing terms for a signed document.

This endpoint is public and rate-limited. Any entity — AI companies, developers,
researchers — can call this to discover the publisher's licensing terms for content
they have encountered.

Calling this endpoint constitutes **constructive notice** — the information was
available, accessible, and machine-readable.

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.PublicRightsApi(api_client)
    document_id = 'document_id_example' # str | Document ID from the signed content
    endpoint_type = 'default' # str |  (optional) (default to 'default')

    try:
        # Resolve rights for a specific document
        api_response = api_instance.get_document_rights_api_v1_public_rights_document_id_get(document_id, endpoint_type=endpoint_type)
        print("The response of PublicRightsApi->get_document_rights_api_v1_public_rights_document_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicRightsApi->get_document_rights_api_v1_public_rights_document_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**| Document ID from the signed content |
 **endpoint_type** | **str**|  | [optional] [default to &#39;default&#39;]

### Return type

**Dict[str, object]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_document_rights_json_ld_api_v1_public_rights_document_id_json_ld_get**
> Dict[str, object] get_document_rights_json_ld_api_v1_public_rights_document_id_json_ld_get(document_id, endpoint_type=endpoint_type)

Rights as JSON-LD (Schema.org compatible)

Returns the document's rights information in JSON-LD format for SEO and semantic web indexing.

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.PublicRightsApi(api_client)
    document_id = 'document_id_example' # str | Document ID
    endpoint_type = 'default' # str |  (optional) (default to 'default')

    try:
        # Rights as JSON-LD (Schema.org compatible)
        api_response = api_instance.get_document_rights_json_ld_api_v1_public_rights_document_id_json_ld_get(document_id, endpoint_type=endpoint_type)
        print("The response of PublicRightsApi->get_document_rights_json_ld_api_v1_public_rights_document_id_json_ld_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicRightsApi->get_document_rights_json_ld_api_v1_public_rights_document_id_json_ld_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**| Document ID |
 **endpoint_type** | **str**|  | [optional] [default to &#39;default&#39;]

### Return type

**Dict[str, object]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_document_rights_odrl_api_v1_public_rights_document_id_odrl_get**
> Dict[str, object] get_document_rights_odrl_api_v1_public_rights_document_id_odrl_get(document_id, endpoint_type=endpoint_type)

Rights as ODRL (W3C Open Digital Rights Language)

Returns the document's rights in W3C ODRL format — machine-readable by semantic web crawlers.

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.PublicRightsApi(api_client)
    document_id = 'document_id_example' # str | Document ID
    endpoint_type = 'default' # str |  (optional) (default to 'default')

    try:
        # Rights as ODRL (W3C Open Digital Rights Language)
        api_response = api_instance.get_document_rights_odrl_api_v1_public_rights_document_id_odrl_get(document_id, endpoint_type=endpoint_type)
        print("The response of PublicRightsApi->get_document_rights_odrl_api_v1_public_rights_document_id_odrl_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicRightsApi->get_document_rights_odrl_api_v1_public_rights_document_id_odrl_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**| Document ID |
 **endpoint_type** | **str**|  | [optional] [default to &#39;default&#39;]

### Return type

**Dict[str, object]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_org_rights_profile_api_v1_public_rights_organization_org_id_get**
> Dict[str, object] get_org_rights_profile_api_v1_public_rights_organization_org_id_get(org_id, endpoint_type=endpoint_type)

Get default rights profile for a publisher organization

Return the publisher's default rights profile (no document-specific overrides).
Useful for AI companies who want to know a publisher's standard terms before
processing their content at scale.

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.PublicRightsApi(api_client)
    org_id = 'org_id_example' # str | Organization ID
    endpoint_type = 'default' # str |  (optional) (default to 'default')

    try:
        # Get default rights profile for a publisher organization
        api_response = api_instance.get_org_rights_profile_api_v1_public_rights_organization_org_id_get(org_id, endpoint_type=endpoint_type)
        print("The response of PublicRightsApi->get_org_rights_profile_api_v1_public_rights_organization_org_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicRightsApi->get_org_rights_profile_api_v1_public_rights_organization_org_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organization ID |
 **endpoint_type** | **str**|  | [optional] [default to &#39;default&#39;]

### Return type

**Dict[str, object]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_robots_meta_api_v1_public_rights_organization_org_id_robots_meta_get**
> Dict[str, object] get_robots_meta_api_v1_public_rights_organization_org_id_robots_meta_get(org_id)

Generate AI-specific robots meta directives

Generate suggested meta tags and robots.txt additions that point AI crawlers
to the rights registry for this publisher.

WordPress plugin uses this to automatically add discovery paths.

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.PublicRightsApi(api_client)
    org_id = 'org_id_example' # str | Organization ID

    try:
        # Generate AI-specific robots meta directives
        api_response = api_instance.get_robots_meta_api_v1_public_rights_organization_org_id_robots_meta_get(org_id)
        print("The response of PublicRightsApi->get_robots_meta_api_v1_public_rights_organization_org_id_robots_meta_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicRightsApi->get_robots_meta_api_v1_public_rights_organization_org_id_robots_meta_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organization ID |

### Return type

**Dict[str, object]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_robots_txt_additions_api_v1_public_rights_organization_org_id_robots_txt_get**
> object get_robots_txt_additions_api_v1_public_rights_organization_org_id_robots_txt_get(org_id)

Generate robots.txt additions with RSL directives

Returns a text block to append to the publisher's robots.txt file.

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.PublicRightsApi(api_client)
    org_id = 'org_id_example' # str | Organization ID

    try:
        # Generate robots.txt additions with RSL directives
        api_response = api_instance.get_robots_txt_additions_api_v1_public_rights_organization_org_id_robots_txt_get(org_id)
        print("The response of PublicRightsApi->get_robots_txt_additions_api_v1_public_rights_organization_org_id_robots_txt_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicRightsApi->get_robots_txt_additions_api_v1_public_rights_organization_org_id_robots_txt_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organization ID |

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_rsl_xml_api_v1_public_rights_organization_org_id_rsl_get**
> object get_rsl_xml_api_v1_public_rights_organization_org_id_rsl_get(org_id)

Generate RSL 1.0 XML document

Generate an RSL 1.0 XML document from the publisher's rights profile.
Maps bronze/silver/gold tiers to RSL <license> elements.

Publishers can host this as rsl.txt or reference it from robots.txt.

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.PublicRightsApi(api_client)
    org_id = 'org_id_example' # str | Organization ID

    try:
        # Generate RSL 1.0 XML document
        api_response = api_instance.get_rsl_xml_api_v1_public_rights_organization_org_id_rsl_get(org_id)
        print("The response of PublicRightsApi->get_rsl_xml_api_v1_public_rights_organization_org_id_rsl_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicRightsApi->get_rsl_xml_api_v1_public_rights_organization_org_id_rsl_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organization ID |

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resolve_rights_from_text_api_v1_public_rights_resolve_post**
> Dict[str, object] resolve_rights_from_text_api_v1_public_rights_resolve_post(request_body, endpoint_type=endpoint_type)

Resolve rights from raw text with embedded markers

Extract embedded Unicode variation selector markers from text and resolve each
to the publisher's rights information.

Accepts raw text (with or without visible markers). Useful for AI pipelines
that want to check rights before processing content.

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.PublicRightsApi(api_client)
    request_body = None # Dict[str, object] |
    endpoint_type = 'default' # str |  (optional) (default to 'default')

    try:
        # Resolve rights from raw text with embedded markers
        api_response = api_instance.resolve_rights_from_text_api_v1_public_rights_resolve_post(request_body, endpoint_type=endpoint_type)
        print("The response of PublicRightsApi->resolve_rights_from_text_api_v1_public_rights_resolve_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicRightsApi->resolve_rights_from_text_api_v1_public_rights_resolve_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**Dict[str, object]**](object.md)|  |
 **endpoint_type** | **str**|  | [optional] [default to &#39;default&#39;]

### Return type

**Dict[str, object]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **rsl_olp_token_api_v1_public_rights_rsl_olp_token_post**
> Dict[str, object] rsl_olp_token_api_v1_public_rights_rsl_olp_token_post(request_body)

RSL Open License Protocol token endpoint

Implements RSL 1.0 Open License Protocol (OLP) with Encypher as the license
server backend. AI crawlers that comply with RSL send token requests here
before crawling publisher content.

Returns:
- 200 + token: Access granted (free bronze-tier crawling)
- 402: Payment required (paid bronze-tier)
- 401 + rights URL: Access blocked, rights resolution URL provided

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.PublicRightsApi(api_client)
    request_body = None # Dict[str, object] |

    try:
        # RSL Open License Protocol token endpoint
        api_response = api_instance.rsl_olp_token_api_v1_public_rights_rsl_olp_token_post(request_body)
        print("The response of PublicRightsApi->rsl_olp_token_api_v1_public_rights_rsl_olp_token_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicRightsApi->rsl_olp_token_api_v1_public_rights_rsl_olp_token_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**Dict[str, object]**](object.md)|  |

### Return type

**Dict[str, object]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validate_olp_token_api_v1_public_rights_rsl_olp_validate_token_get**
> Dict[str, object] validate_olp_token_api_v1_public_rights_rsl_olp_validate_token_get(token)

Validate an OLP token

Publisher web servers use this to verify crawler authorization.

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.PublicRightsApi(api_client)
    token = 'token_example' # str | OLP token to validate

    try:
        # Validate an OLP token
        api_response = api_instance.validate_olp_token_api_v1_public_rights_rsl_olp_validate_token_get(token)
        print("The response of PublicRightsApi->validate_olp_token_api_v1_public_rights_rsl_olp_validate_token_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicRightsApi->validate_olp_token_api_v1_public_rights_rsl_olp_validate_token_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| OLP token to validate |

### Return type

**Dict[str, object]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
