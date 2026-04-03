# encypher.CDNIntegrationsApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_cdn_integration_api_v1_cdn_cloudflare_delete**](CDNIntegrationsApi.md#delete_cdn_integration_api_v1_cdn_cloudflare_delete) | **DELETE** /api/v1/cdn/cloudflare | Remove Cloudflare Logpush integration
[**delete_cdn_integration_api_v1_cdn_cloudflare_delete_0**](CDNIntegrationsApi.md#delete_cdn_integration_api_v1_cdn_cloudflare_delete_0) | **DELETE** /api/v1/cdn/cloudflare | Remove Cloudflare Logpush integration
[**generate_worker_config_api_v1_cdn_integrations_integration_id_generate_worker_config_post**](CDNIntegrationsApi.md#generate_worker_config_api_v1_cdn_integrations_integration_id_generate_worker_config_post) | **POST** /api/v1/cdn/integrations/{integration_id}/generate-worker-config | Generate Cloudflare Worker config for CDN provenance
[**generate_worker_config_api_v1_cdn_integrations_integration_id_generate_worker_config_post_0**](CDNIntegrationsApi.md#generate_worker_config_api_v1_cdn_integrations_integration_id_generate_worker_config_post_0) | **POST** /api/v1/cdn/integrations/{integration_id}/generate-worker-config | Generate Cloudflare Worker config for CDN provenance
[**get_cdn_integration_api_v1_cdn_cloudflare_get**](CDNIntegrationsApi.md#get_cdn_integration_api_v1_cdn_cloudflare_get) | **GET** /api/v1/cdn/cloudflare | Get current Cloudflare Logpush integration config
[**get_cdn_integration_api_v1_cdn_cloudflare_get_0**](CDNIntegrationsApi.md#get_cdn_integration_api_v1_cdn_cloudflare_get_0) | **GET** /api/v1/cdn/cloudflare | Get current Cloudflare Logpush integration config
[**save_cdn_integration_api_v1_cdn_cloudflare_post**](CDNIntegrationsApi.md#save_cdn_integration_api_v1_cdn_cloudflare_post) | **POST** /api/v1/cdn/cloudflare | Create or update Cloudflare Logpush integration
[**save_cdn_integration_api_v1_cdn_cloudflare_post_0**](CDNIntegrationsApi.md#save_cdn_integration_api_v1_cdn_cloudflare_post_0) | **POST** /api/v1/cdn/cloudflare | Create or update Cloudflare Logpush integration


# **delete_cdn_integration_api_v1_cdn_cloudflare_delete**
> delete_cdn_integration_api_v1_cdn_cloudflare_delete()

Remove Cloudflare Logpush integration

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
    api_instance = encypher.CDNIntegrationsApi(api_client)

    try:
        # Remove Cloudflare Logpush integration
        api_instance.delete_cdn_integration_api_v1_cdn_cloudflare_delete()
    except Exception as e:
        print("Exception when calling CDNIntegrationsApi->delete_cdn_integration_api_v1_cdn_cloudflare_delete: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_cdn_integration_api_v1_cdn_cloudflare_delete_0**
> delete_cdn_integration_api_v1_cdn_cloudflare_delete_0()

Remove Cloudflare Logpush integration

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
    api_instance = encypher.CDNIntegrationsApi(api_client)

    try:
        # Remove Cloudflare Logpush integration
        api_instance.delete_cdn_integration_api_v1_cdn_cloudflare_delete_0()
    except Exception as e:
        print("Exception when calling CDNIntegrationsApi->delete_cdn_integration_api_v1_cdn_cloudflare_delete_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **generate_worker_config_api_v1_cdn_integrations_integration_id_generate_worker_config_post**
> CdnWorkerConfigResponse generate_worker_config_api_v1_cdn_integrations_integration_id_generate_worker_config_post(integration_id)

Generate Cloudflare Worker config for CDN provenance

Generate a ready-to-deploy Cloudflare Worker script and wrangler.toml for the
specified CDN integration, with API URL, org ID, and integration ID
substituted.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_worker_config_response import CdnWorkerConfigResponse
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
    api_instance = encypher.CDNIntegrationsApi(api_client)
    integration_id = 'integration_id_example' # str | CDN integration UUID

    try:
        # Generate Cloudflare Worker config for CDN provenance
        api_response = api_instance.generate_worker_config_api_v1_cdn_integrations_integration_id_generate_worker_config_post(integration_id)
        print("The response of CDNIntegrationsApi->generate_worker_config_api_v1_cdn_integrations_integration_id_generate_worker_config_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNIntegrationsApi->generate_worker_config_api_v1_cdn_integrations_integration_id_generate_worker_config_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **integration_id** | **str**| CDN integration UUID |

### Return type

[**CdnWorkerConfigResponse**](CdnWorkerConfigResponse.md)

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

# **generate_worker_config_api_v1_cdn_integrations_integration_id_generate_worker_config_post_0**
> CdnWorkerConfigResponse generate_worker_config_api_v1_cdn_integrations_integration_id_generate_worker_config_post_0(integration_id)

Generate Cloudflare Worker config for CDN provenance

Generate a ready-to-deploy Cloudflare Worker script and wrangler.toml for the
specified CDN integration, with API URL, org ID, and integration ID
substituted.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_worker_config_response import CdnWorkerConfigResponse
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
    api_instance = encypher.CDNIntegrationsApi(api_client)
    integration_id = 'integration_id_example' # str | CDN integration UUID

    try:
        # Generate Cloudflare Worker config for CDN provenance
        api_response = api_instance.generate_worker_config_api_v1_cdn_integrations_integration_id_generate_worker_config_post_0(integration_id)
        print("The response of CDNIntegrationsApi->generate_worker_config_api_v1_cdn_integrations_integration_id_generate_worker_config_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNIntegrationsApi->generate_worker_config_api_v1_cdn_integrations_integration_id_generate_worker_config_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **integration_id** | **str**| CDN integration UUID |

### Return type

[**CdnWorkerConfigResponse**](CdnWorkerConfigResponse.md)

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

# **get_cdn_integration_api_v1_cdn_cloudflare_get**
> CdnIntegrationResponse get_cdn_integration_api_v1_cdn_cloudflare_get()

Get current Cloudflare Logpush integration config

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_integration_response import CdnIntegrationResponse
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
    api_instance = encypher.CDNIntegrationsApi(api_client)

    try:
        # Get current Cloudflare Logpush integration config
        api_response = api_instance.get_cdn_integration_api_v1_cdn_cloudflare_get()
        print("The response of CDNIntegrationsApi->get_cdn_integration_api_v1_cdn_cloudflare_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNIntegrationsApi->get_cdn_integration_api_v1_cdn_cloudflare_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**CdnIntegrationResponse**](CdnIntegrationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cdn_integration_api_v1_cdn_cloudflare_get_0**
> CdnIntegrationResponse get_cdn_integration_api_v1_cdn_cloudflare_get_0()

Get current Cloudflare Logpush integration config

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_integration_response import CdnIntegrationResponse
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
    api_instance = encypher.CDNIntegrationsApi(api_client)

    try:
        # Get current Cloudflare Logpush integration config
        api_response = api_instance.get_cdn_integration_api_v1_cdn_cloudflare_get_0()
        print("The response of CDNIntegrationsApi->get_cdn_integration_api_v1_cdn_cloudflare_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNIntegrationsApi->get_cdn_integration_api_v1_cdn_cloudflare_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**CdnIntegrationResponse**](CdnIntegrationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **save_cdn_integration_api_v1_cdn_cloudflare_post**
> CdnIntegrationResponse save_cdn_integration_api_v1_cdn_cloudflare_post(cdn_integration_create)

Create or update Cloudflare Logpush integration

Save (or replace) the Cloudflare Logpush configuration for the authenticated
organization. Returns the webhook URL to paste into the Cloudflare Logpush
job destination field and the truncated zone_id for confirmation.

The webhook_secret is stored hashed (bcrypt) and cannot be retrieved after
creation. Store it safely before submitting.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_integration_create import CdnIntegrationCreate
from encypher.models.cdn_integration_response import CdnIntegrationResponse
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
    api_instance = encypher.CDNIntegrationsApi(api_client)
    cdn_integration_create = encypher.CdnIntegrationCreate() # CdnIntegrationCreate |

    try:
        # Create or update Cloudflare Logpush integration
        api_response = api_instance.save_cdn_integration_api_v1_cdn_cloudflare_post(cdn_integration_create)
        print("The response of CDNIntegrationsApi->save_cdn_integration_api_v1_cdn_cloudflare_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNIntegrationsApi->save_cdn_integration_api_v1_cdn_cloudflare_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cdn_integration_create** | [**CdnIntegrationCreate**](CdnIntegrationCreate.md)|  |

### Return type

[**CdnIntegrationResponse**](CdnIntegrationResponse.md)

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

# **save_cdn_integration_api_v1_cdn_cloudflare_post_0**
> CdnIntegrationResponse save_cdn_integration_api_v1_cdn_cloudflare_post_0(cdn_integration_create)

Create or update Cloudflare Logpush integration

Save (or replace) the Cloudflare Logpush configuration for the authenticated
organization. Returns the webhook URL to paste into the Cloudflare Logpush
job destination field and the truncated zone_id for confirmation.

The webhook_secret is stored hashed (bcrypt) and cannot be retrieved after
creation. Store it safely before submitting.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_integration_create import CdnIntegrationCreate
from encypher.models.cdn_integration_response import CdnIntegrationResponse
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
    api_instance = encypher.CDNIntegrationsApi(api_client)
    cdn_integration_create = encypher.CdnIntegrationCreate() # CdnIntegrationCreate |

    try:
        # Create or update Cloudflare Logpush integration
        api_response = api_instance.save_cdn_integration_api_v1_cdn_cloudflare_post_0(cdn_integration_create)
        print("The response of CDNIntegrationsApi->save_cdn_integration_api_v1_cdn_cloudflare_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNIntegrationsApi->save_cdn_integration_api_v1_cdn_cloudflare_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cdn_integration_create** | [**CdnIntegrationCreate**](CdnIntegrationCreate.md)|  |

### Return type

[**CdnIntegrationResponse**](CdnIntegrationResponse.md)

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
