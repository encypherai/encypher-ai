# encypher.WebhooksApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_webhook_api_v1_webhooks_post**](WebhooksApi.md#create_webhook_api_v1_webhooks_post) | **POST** /api/v1/webhooks | Create Webhook
[**create_webhook_api_v1_webhooks_post_0**](WebhooksApi.md#create_webhook_api_v1_webhooks_post_0) | **POST** /api/v1/webhooks | Create Webhook
[**delete_webhook_api_v1_webhooks_webhook_id_delete**](WebhooksApi.md#delete_webhook_api_v1_webhooks_webhook_id_delete) | **DELETE** /api/v1/webhooks/{webhook_id} | Delete Webhook
[**delete_webhook_api_v1_webhooks_webhook_id_delete_0**](WebhooksApi.md#delete_webhook_api_v1_webhooks_webhook_id_delete_0) | **DELETE** /api/v1/webhooks/{webhook_id} | Delete Webhook
[**get_webhook_api_v1_webhooks_webhook_id_get**](WebhooksApi.md#get_webhook_api_v1_webhooks_webhook_id_get) | **GET** /api/v1/webhooks/{webhook_id} | Get Webhook
[**get_webhook_api_v1_webhooks_webhook_id_get_0**](WebhooksApi.md#get_webhook_api_v1_webhooks_webhook_id_get_0) | **GET** /api/v1/webhooks/{webhook_id} | Get Webhook
[**get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get**](WebhooksApi.md#get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get) | **GET** /api/v1/webhooks/{webhook_id}/deliveries | Get Webhook Deliveries
[**get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get_0**](WebhooksApi.md#get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get_0) | **GET** /api/v1/webhooks/{webhook_id}/deliveries | Get Webhook Deliveries
[**list_webhooks_api_v1_webhooks_get**](WebhooksApi.md#list_webhooks_api_v1_webhooks_get) | **GET** /api/v1/webhooks | List Webhooks
[**list_webhooks_api_v1_webhooks_get_0**](WebhooksApi.md#list_webhooks_api_v1_webhooks_get_0) | **GET** /api/v1/webhooks | List Webhooks
[**test_webhook_api_v1_webhooks_webhook_id_test_post**](WebhooksApi.md#test_webhook_api_v1_webhooks_webhook_id_test_post) | **POST** /api/v1/webhooks/{webhook_id}/test | Test Webhook
[**test_webhook_api_v1_webhooks_webhook_id_test_post_0**](WebhooksApi.md#test_webhook_api_v1_webhooks_webhook_id_test_post_0) | **POST** /api/v1/webhooks/{webhook_id}/test | Test Webhook
[**update_webhook_api_v1_webhooks_webhook_id_patch**](WebhooksApi.md#update_webhook_api_v1_webhooks_webhook_id_patch) | **PATCH** /api/v1/webhooks/{webhook_id} | Update Webhook
[**update_webhook_api_v1_webhooks_webhook_id_patch_0**](WebhooksApi.md#update_webhook_api_v1_webhooks_webhook_id_patch_0) | **PATCH** /api/v1/webhooks/{webhook_id} | Update Webhook


# **create_webhook_api_v1_webhooks_post**
> WebhookCreateResponse create_webhook_api_v1_webhooks_post(webhook_create_request)

Create Webhook

Register a new webhook.

The webhook URL must be HTTPS. You can optionally provide a shared secret
for HMAC signature verification of webhook payloads.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.webhook_create_request import WebhookCreateRequest
from encypher.models.webhook_create_response import WebhookCreateResponse
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
    api_instance = encypher.WebhooksApi(api_client)
    webhook_create_request = encypher.WebhookCreateRequest() # WebhookCreateRequest |

    try:
        # Create Webhook
        api_response = api_instance.create_webhook_api_v1_webhooks_post(webhook_create_request)
        print("The response of WebhooksApi->create_webhook_api_v1_webhooks_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->create_webhook_api_v1_webhooks_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_create_request** | [**WebhookCreateRequest**](WebhookCreateRequest.md)|  |

### Return type

[**WebhookCreateResponse**](WebhookCreateResponse.md)

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

# **create_webhook_api_v1_webhooks_post_0**
> WebhookCreateResponse create_webhook_api_v1_webhooks_post_0(webhook_create_request)

Create Webhook

Register a new webhook.

The webhook URL must be HTTPS. You can optionally provide a shared secret
for HMAC signature verification of webhook payloads.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.webhook_create_request import WebhookCreateRequest
from encypher.models.webhook_create_response import WebhookCreateResponse
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
    api_instance = encypher.WebhooksApi(api_client)
    webhook_create_request = encypher.WebhookCreateRequest() # WebhookCreateRequest |

    try:
        # Create Webhook
        api_response = api_instance.create_webhook_api_v1_webhooks_post_0(webhook_create_request)
        print("The response of WebhooksApi->create_webhook_api_v1_webhooks_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->create_webhook_api_v1_webhooks_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_create_request** | [**WebhookCreateRequest**](WebhookCreateRequest.md)|  |

### Return type

[**WebhookCreateResponse**](WebhookCreateResponse.md)

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

# **delete_webhook_api_v1_webhooks_webhook_id_delete**
> WebhookDeleteResponse delete_webhook_api_v1_webhooks_webhook_id_delete(webhook_id)

Delete Webhook

Delete a webhook.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.webhook_delete_response import WebhookDeleteResponse
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
    api_instance = encypher.WebhooksApi(api_client)
    webhook_id = 'webhook_id_example' # str |

    try:
        # Delete Webhook
        api_response = api_instance.delete_webhook_api_v1_webhooks_webhook_id_delete(webhook_id)
        print("The response of WebhooksApi->delete_webhook_api_v1_webhooks_webhook_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->delete_webhook_api_v1_webhooks_webhook_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_id** | **str**|  |

### Return type

[**WebhookDeleteResponse**](WebhookDeleteResponse.md)

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

# **delete_webhook_api_v1_webhooks_webhook_id_delete_0**
> WebhookDeleteResponse delete_webhook_api_v1_webhooks_webhook_id_delete_0(webhook_id)

Delete Webhook

Delete a webhook.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.webhook_delete_response import WebhookDeleteResponse
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
    api_instance = encypher.WebhooksApi(api_client)
    webhook_id = 'webhook_id_example' # str |

    try:
        # Delete Webhook
        api_response = api_instance.delete_webhook_api_v1_webhooks_webhook_id_delete_0(webhook_id)
        print("The response of WebhooksApi->delete_webhook_api_v1_webhooks_webhook_id_delete_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->delete_webhook_api_v1_webhooks_webhook_id_delete_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_id** | **str**|  |

### Return type

[**WebhookDeleteResponse**](WebhookDeleteResponse.md)

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

# **get_webhook_api_v1_webhooks_webhook_id_get**
> WebhookListResponse get_webhook_api_v1_webhooks_webhook_id_get(webhook_id)

Get Webhook

Get details of a specific webhook.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.webhook_list_response import WebhookListResponse
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
    api_instance = encypher.WebhooksApi(api_client)
    webhook_id = 'webhook_id_example' # str |

    try:
        # Get Webhook
        api_response = api_instance.get_webhook_api_v1_webhooks_webhook_id_get(webhook_id)
        print("The response of WebhooksApi->get_webhook_api_v1_webhooks_webhook_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->get_webhook_api_v1_webhooks_webhook_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_id** | **str**|  |

### Return type

[**WebhookListResponse**](WebhookListResponse.md)

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

# **get_webhook_api_v1_webhooks_webhook_id_get_0**
> WebhookListResponse get_webhook_api_v1_webhooks_webhook_id_get_0(webhook_id)

Get Webhook

Get details of a specific webhook.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.webhook_list_response import WebhookListResponse
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
    api_instance = encypher.WebhooksApi(api_client)
    webhook_id = 'webhook_id_example' # str |

    try:
        # Get Webhook
        api_response = api_instance.get_webhook_api_v1_webhooks_webhook_id_get_0(webhook_id)
        print("The response of WebhooksApi->get_webhook_api_v1_webhooks_webhook_id_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->get_webhook_api_v1_webhooks_webhook_id_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_id** | **str**|  |

### Return type

[**WebhookListResponse**](WebhookListResponse.md)

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

# **get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get**
> WebhookDeliveriesResponse get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get(webhook_id, page=page, page_size=page_size)

Get Webhook Deliveries

Get delivery history for a webhook.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.webhook_deliveries_response import WebhookDeliveriesResponse
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
    api_instance = encypher.WebhooksApi(api_client)
    webhook_id = 'webhook_id_example' # str |
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)

    try:
        # Get Webhook Deliveries
        api_response = api_instance.get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get(webhook_id, page=page, page_size=page_size)
        print("The response of WebhooksApi->get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_id** | **str**|  |
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]

### Return type

[**WebhookDeliveriesResponse**](WebhookDeliveriesResponse.md)

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

# **get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get_0**
> WebhookDeliveriesResponse get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get_0(webhook_id, page=page, page_size=page_size)

Get Webhook Deliveries

Get delivery history for a webhook.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.webhook_deliveries_response import WebhookDeliveriesResponse
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
    api_instance = encypher.WebhooksApi(api_client)
    webhook_id = 'webhook_id_example' # str |
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)

    try:
        # Get Webhook Deliveries
        api_response = api_instance.get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get_0(webhook_id, page=page, page_size=page_size)
        print("The response of WebhooksApi->get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_id** | **str**|  |
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]

### Return type

[**WebhookDeliveriesResponse**](WebhookDeliveriesResponse.md)

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

# **list_webhooks_api_v1_webhooks_get**
> WebhookListResponse list_webhooks_api_v1_webhooks_get()

List Webhooks

List all webhooks for the organization.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.webhook_list_response import WebhookListResponse
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
    api_instance = encypher.WebhooksApi(api_client)

    try:
        # List Webhooks
        api_response = api_instance.list_webhooks_api_v1_webhooks_get()
        print("The response of WebhooksApi->list_webhooks_api_v1_webhooks_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->list_webhooks_api_v1_webhooks_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**WebhookListResponse**](WebhookListResponse.md)

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

# **list_webhooks_api_v1_webhooks_get_0**
> WebhookListResponse list_webhooks_api_v1_webhooks_get_0()

List Webhooks

List all webhooks for the organization.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.webhook_list_response import WebhookListResponse
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
    api_instance = encypher.WebhooksApi(api_client)

    try:
        # List Webhooks
        api_response = api_instance.list_webhooks_api_v1_webhooks_get_0()
        print("The response of WebhooksApi->list_webhooks_api_v1_webhooks_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->list_webhooks_api_v1_webhooks_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**WebhookListResponse**](WebhookListResponse.md)

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

# **test_webhook_api_v1_webhooks_webhook_id_test_post**
> WebhookTestResponse test_webhook_api_v1_webhooks_webhook_id_test_post(webhook_id)

Test Webhook

Send a test event to the webhook.

This sends a test payload to verify the webhook is configured correctly.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.webhook_test_response import WebhookTestResponse
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
    api_instance = encypher.WebhooksApi(api_client)
    webhook_id = 'webhook_id_example' # str |

    try:
        # Test Webhook
        api_response = api_instance.test_webhook_api_v1_webhooks_webhook_id_test_post(webhook_id)
        print("The response of WebhooksApi->test_webhook_api_v1_webhooks_webhook_id_test_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->test_webhook_api_v1_webhooks_webhook_id_test_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_id** | **str**|  |

### Return type

[**WebhookTestResponse**](WebhookTestResponse.md)

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

# **test_webhook_api_v1_webhooks_webhook_id_test_post_0**
> WebhookTestResponse test_webhook_api_v1_webhooks_webhook_id_test_post_0(webhook_id)

Test Webhook

Send a test event to the webhook.

This sends a test payload to verify the webhook is configured correctly.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.webhook_test_response import WebhookTestResponse
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
    api_instance = encypher.WebhooksApi(api_client)
    webhook_id = 'webhook_id_example' # str |

    try:
        # Test Webhook
        api_response = api_instance.test_webhook_api_v1_webhooks_webhook_id_test_post_0(webhook_id)
        print("The response of WebhooksApi->test_webhook_api_v1_webhooks_webhook_id_test_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->test_webhook_api_v1_webhooks_webhook_id_test_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_id** | **str**|  |

### Return type

[**WebhookTestResponse**](WebhookTestResponse.md)

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

# **update_webhook_api_v1_webhooks_webhook_id_patch**
> WebhookUpdateResponse update_webhook_api_v1_webhooks_webhook_id_patch(webhook_id, webhook_update_request)

Update Webhook

Update a webhook's URL, events, or active status.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.webhook_update_request import WebhookUpdateRequest
from encypher.models.webhook_update_response import WebhookUpdateResponse
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
    api_instance = encypher.WebhooksApi(api_client)
    webhook_id = 'webhook_id_example' # str |
    webhook_update_request = encypher.WebhookUpdateRequest() # WebhookUpdateRequest |

    try:
        # Update Webhook
        api_response = api_instance.update_webhook_api_v1_webhooks_webhook_id_patch(webhook_id, webhook_update_request)
        print("The response of WebhooksApi->update_webhook_api_v1_webhooks_webhook_id_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->update_webhook_api_v1_webhooks_webhook_id_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_id** | **str**|  |
 **webhook_update_request** | [**WebhookUpdateRequest**](WebhookUpdateRequest.md)|  |

### Return type

[**WebhookUpdateResponse**](WebhookUpdateResponse.md)

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

# **update_webhook_api_v1_webhooks_webhook_id_patch_0**
> WebhookUpdateResponse update_webhook_api_v1_webhooks_webhook_id_patch_0(webhook_id, webhook_update_request)

Update Webhook

Update a webhook's URL, events, or active status.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.webhook_update_request import WebhookUpdateRequest
from encypher.models.webhook_update_response import WebhookUpdateResponse
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
    api_instance = encypher.WebhooksApi(api_client)
    webhook_id = 'webhook_id_example' # str |
    webhook_update_request = encypher.WebhookUpdateRequest() # WebhookUpdateRequest |

    try:
        # Update Webhook
        api_response = api_instance.update_webhook_api_v1_webhooks_webhook_id_patch_0(webhook_id, webhook_update_request)
        print("The response of WebhooksApi->update_webhook_api_v1_webhooks_webhook_id_patch_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->update_webhook_api_v1_webhooks_webhook_id_patch_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_id** | **str**|  |
 **webhook_update_request** | [**WebhookUpdateRequest**](WebhookUpdateRequest.md)|  |

### Return type

[**WebhookUpdateResponse**](WebhookUpdateResponse.md)

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
