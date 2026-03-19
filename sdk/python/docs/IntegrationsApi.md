# encypher.IntegrationsApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ack_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_action_id_ack_post**](IntegrationsApi.md#ack_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_action_id_ack_post) | **POST** /api/v1/integrations/wordpress/{install_id}/actions/{action_id}/ack | Acknowledge a WordPress remote action result
[**ack_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_action_id_ack_post_0**](IntegrationsApi.md#ack_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_action_id_ack_post_0) | **POST** /api/v1/integrations/wordpress/{install_id}/actions/{action_id}/ack | Acknowledge a WordPress remote action result
[**complete_wordpress_connect_session_api_v1_integrations_wordpress_connect_complete_post**](IntegrationsApi.md#complete_wordpress_connect_session_api_v1_integrations_wordpress_connect_complete_post) | **POST** /api/v1/integrations/wordpress/connect/complete | Complete a WordPress magic-link connect session
[**complete_wordpress_connect_session_api_v1_integrations_wordpress_connect_complete_post_0**](IntegrationsApi.md#complete_wordpress_connect_session_api_v1_integrations_wordpress_connect_complete_post_0) | **POST** /api/v1/integrations/wordpress/connect/complete | Complete a WordPress magic-link connect session
[**create_ghost_integration_api_v1_integrations_ghost_post**](IntegrationsApi.md#create_ghost_integration_api_v1_integrations_ghost_post) | **POST** /api/v1/integrations/ghost | Configure Ghost integration
[**create_ghost_integration_api_v1_integrations_ghost_post_0**](IntegrationsApi.md#create_ghost_integration_api_v1_integrations_ghost_post_0) | **POST** /api/v1/integrations/ghost | Configure Ghost integration
[**delete_ghost_integration_api_v1_integrations_ghost_delete**](IntegrationsApi.md#delete_ghost_integration_api_v1_integrations_ghost_delete) | **DELETE** /api/v1/integrations/ghost | Remove Ghost integration
[**delete_ghost_integration_api_v1_integrations_ghost_delete_0**](IntegrationsApi.md#delete_ghost_integration_api_v1_integrations_ghost_delete_0) | **DELETE** /api/v1/integrations/ghost | Remove Ghost integration
[**get_ghost_integration_api_v1_integrations_ghost_get**](IntegrationsApi.md#get_ghost_integration_api_v1_integrations_ghost_get) | **GET** /api/v1/integrations/ghost | Get Ghost integration config
[**get_ghost_integration_api_v1_integrations_ghost_get_0**](IntegrationsApi.md#get_ghost_integration_api_v1_integrations_ghost_get_0) | **GET** /api/v1/integrations/ghost | Get Ghost integration config
[**get_wordpress_integration_status_api_v1_integrations_wordpress_status_get**](IntegrationsApi.md#get_wordpress_integration_status_api_v1_integrations_wordpress_status_get) | **GET** /api/v1/integrations/wordpress/status | Get WordPress integration status
[**get_wordpress_integration_status_api_v1_integrations_wordpress_status_get_0**](IntegrationsApi.md#get_wordpress_integration_status_api_v1_integrations_wordpress_status_get_0) | **GET** /api/v1/integrations/wordpress/status | Get WordPress integration status
[**ghost_webhook_api_v1_integrations_ghost_webhook_post**](IntegrationsApi.md#ghost_webhook_api_v1_integrations_ghost_webhook_post) | **POST** /api/v1/integrations/ghost/webhook | Receive Ghost CMS webhooks
[**ghost_webhook_api_v1_integrations_ghost_webhook_post_0**](IntegrationsApi.md#ghost_webhook_api_v1_integrations_ghost_webhook_post_0) | **POST** /api/v1/integrations/ghost/webhook | Receive Ghost CMS webhooks
[**manual_sign_ghost_post_api_v1_integrations_ghost_sign_post_id_post**](IntegrationsApi.md#manual_sign_ghost_post_api_v1_integrations_ghost_sign_post_id_post) | **POST** /api/v1/integrations/ghost/sign/{post_id} | Manually sign a Ghost post
[**manual_sign_ghost_post_api_v1_integrations_ghost_sign_post_id_post_0**](IntegrationsApi.md#manual_sign_ghost_post_api_v1_integrations_ghost_sign_post_id_post_0) | **POST** /api/v1/integrations/ghost/sign/{post_id} | Manually sign a Ghost post
[**poll_wordpress_connect_session_api_v1_integrations_wordpress_connect_session_session_id_get**](IntegrationsApi.md#poll_wordpress_connect_session_api_v1_integrations_wordpress_connect_session_session_id_get) | **GET** /api/v1/integrations/wordpress/connect/session/{session_id} | Poll a WordPress magic-link connect session
[**poll_wordpress_connect_session_api_v1_integrations_wordpress_connect_session_session_id_get_0**](IntegrationsApi.md#poll_wordpress_connect_session_api_v1_integrations_wordpress_connect_session_session_id_get_0) | **GET** /api/v1/integrations/wordpress/connect/session/{session_id} | Poll a WordPress magic-link connect session
[**pull_wordpress_install_actions_api_v1_integrations_wordpress_install_id_actions_pull_post**](IntegrationsApi.md#pull_wordpress_install_actions_api_v1_integrations_wordpress_install_id_actions_pull_post) | **POST** /api/v1/integrations/wordpress/{install_id}/actions/pull | Pull queued remote actions for a WordPress install
[**pull_wordpress_install_actions_api_v1_integrations_wordpress_install_id_actions_pull_post_0**](IntegrationsApi.md#pull_wordpress_install_actions_api_v1_integrations_wordpress_install_id_actions_pull_post_0) | **POST** /api/v1/integrations/wordpress/{install_id}/actions/pull | Pull queued remote actions for a WordPress install
[**queue_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_post**](IntegrationsApi.md#queue_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_post) | **POST** /api/v1/integrations/wordpress/{install_id}/actions | Queue a remote action for a WordPress install
[**queue_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_post_0**](IntegrationsApi.md#queue_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_post_0) | **POST** /api/v1/integrations/wordpress/{install_id}/actions | Queue a remote action for a WordPress install
[**record_wordpress_verification_event_api_v1_integrations_wordpress_verification_event_post**](IntegrationsApi.md#record_wordpress_verification_event_api_v1_integrations_wordpress_verification_event_post) | **POST** /api/v1/integrations/wordpress/verification-event | Record a WordPress verification event
[**record_wordpress_verification_event_api_v1_integrations_wordpress_verification_event_post_0**](IntegrationsApi.md#record_wordpress_verification_event_api_v1_integrations_wordpress_verification_event_post_0) | **POST** /api/v1/integrations/wordpress/verification-event | Record a WordPress verification event
[**regenerate_ghost_token_api_v1_integrations_ghost_regenerate_token_post**](IntegrationsApi.md#regenerate_ghost_token_api_v1_integrations_ghost_regenerate_token_post) | **POST** /api/v1/integrations/ghost/regenerate-token | Regenerate webhook token
[**regenerate_ghost_token_api_v1_integrations_ghost_regenerate_token_post_0**](IntegrationsApi.md#regenerate_ghost_token_api_v1_integrations_ghost_regenerate_token_post_0) | **POST** /api/v1/integrations/ghost/regenerate-token | Regenerate webhook token
[**register_wordpress_install_api_v1_integrations_wordpress_register_install_post**](IntegrationsApi.md#register_wordpress_install_api_v1_integrations_wordpress_register_install_post) | **POST** /api/v1/integrations/wordpress/register-install | Register or update a WordPress install
[**register_wordpress_install_api_v1_integrations_wordpress_register_install_post_0**](IntegrationsApi.md#register_wordpress_install_api_v1_integrations_wordpress_register_install_post_0) | **POST** /api/v1/integrations/wordpress/register-install | Register or update a WordPress install
[**start_wordpress_connect_session_api_v1_integrations_wordpress_connect_start_post**](IntegrationsApi.md#start_wordpress_connect_session_api_v1_integrations_wordpress_connect_start_post) | **POST** /api/v1/integrations/wordpress/connect/start | Start a WordPress magic-link connect session
[**start_wordpress_connect_session_api_v1_integrations_wordpress_connect_start_post_0**](IntegrationsApi.md#start_wordpress_connect_session_api_v1_integrations_wordpress_connect_start_post_0) | **POST** /api/v1/integrations/wordpress/connect/start | Start a WordPress magic-link connect session
[**sync_wordpress_integration_status_api_v1_integrations_wordpress_status_sync_post**](IntegrationsApi.md#sync_wordpress_integration_status_api_v1_integrations_wordpress_status_sync_post) | **POST** /api/v1/integrations/wordpress/status-sync | Sync WordPress integration status
[**sync_wordpress_integration_status_api_v1_integrations_wordpress_status_sync_post_0**](IntegrationsApi.md#sync_wordpress_integration_status_api_v1_integrations_wordpress_status_sync_post_0) | **POST** /api/v1/integrations/wordpress/status-sync | Sync WordPress integration status


# **ack_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_action_id_ack_post**
> WordPressIntegrationStatusResponse ack_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_action_id_ack_post(install_id, action_id, word_press_action_ack_payload)

Acknowledge a WordPress remote action result

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.word_press_action_ack_payload import WordPressActionAckPayload
from encypher.models.word_press_integration_status_response import WordPressIntegrationStatusResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    install_id = 'install_id_example' # str |
    action_id = 'action_id_example' # str |
    word_press_action_ack_payload = encypher.WordPressActionAckPayload() # WordPressActionAckPayload |

    try:
        # Acknowledge a WordPress remote action result
        api_response = api_instance.ack_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_action_id_ack_post(install_id, action_id, word_press_action_ack_payload)
        print("The response of IntegrationsApi->ack_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_action_id_ack_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->ack_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_action_id_ack_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **install_id** | **str**|  |
 **action_id** | **str**|  |
 **word_press_action_ack_payload** | [**WordPressActionAckPayload**](WordPressActionAckPayload.md)|  |

### Return type

[**WordPressIntegrationStatusResponse**](WordPressIntegrationStatusResponse.md)

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

# **ack_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_action_id_ack_post_0**
> WordPressIntegrationStatusResponse ack_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_action_id_ack_post_0(install_id, action_id, word_press_action_ack_payload)

Acknowledge a WordPress remote action result

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.word_press_action_ack_payload import WordPressActionAckPayload
from encypher.models.word_press_integration_status_response import WordPressIntegrationStatusResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    install_id = 'install_id_example' # str |
    action_id = 'action_id_example' # str |
    word_press_action_ack_payload = encypher.WordPressActionAckPayload() # WordPressActionAckPayload |

    try:
        # Acknowledge a WordPress remote action result
        api_response = api_instance.ack_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_action_id_ack_post_0(install_id, action_id, word_press_action_ack_payload)
        print("The response of IntegrationsApi->ack_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_action_id_ack_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->ack_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_action_id_ack_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **install_id** | **str**|  |
 **action_id** | **str**|  |
 **word_press_action_ack_payload** | [**WordPressActionAckPayload**](WordPressActionAckPayload.md)|  |

### Return type

[**WordPressIntegrationStatusResponse**](WordPressIntegrationStatusResponse.md)

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

# **complete_wordpress_connect_session_api_v1_integrations_wordpress_connect_complete_post**
> WordPressConnectPollResponse complete_wordpress_connect_session_api_v1_integrations_wordpress_connect_complete_post(word_press_connect_complete_payload)

Complete a WordPress magic-link connect session

### Example


```python
import encypher
from encypher.models.word_press_connect_complete_payload import WordPressConnectCompletePayload
from encypher.models.word_press_connect_poll_response import WordPressConnectPollResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.IntegrationsApi(api_client)
    word_press_connect_complete_payload = encypher.WordPressConnectCompletePayload() # WordPressConnectCompletePayload |

    try:
        # Complete a WordPress magic-link connect session
        api_response = api_instance.complete_wordpress_connect_session_api_v1_integrations_wordpress_connect_complete_post(word_press_connect_complete_payload)
        print("The response of IntegrationsApi->complete_wordpress_connect_session_api_v1_integrations_wordpress_connect_complete_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->complete_wordpress_connect_session_api_v1_integrations_wordpress_connect_complete_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **word_press_connect_complete_payload** | [**WordPressConnectCompletePayload**](WordPressConnectCompletePayload.md)|  |

### Return type

[**WordPressConnectPollResponse**](WordPressConnectPollResponse.md)

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

# **complete_wordpress_connect_session_api_v1_integrations_wordpress_connect_complete_post_0**
> WordPressConnectPollResponse complete_wordpress_connect_session_api_v1_integrations_wordpress_connect_complete_post_0(word_press_connect_complete_payload)

Complete a WordPress magic-link connect session

### Example


```python
import encypher
from encypher.models.word_press_connect_complete_payload import WordPressConnectCompletePayload
from encypher.models.word_press_connect_poll_response import WordPressConnectPollResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.IntegrationsApi(api_client)
    word_press_connect_complete_payload = encypher.WordPressConnectCompletePayload() # WordPressConnectCompletePayload |

    try:
        # Complete a WordPress magic-link connect session
        api_response = api_instance.complete_wordpress_connect_session_api_v1_integrations_wordpress_connect_complete_post_0(word_press_connect_complete_payload)
        print("The response of IntegrationsApi->complete_wordpress_connect_session_api_v1_integrations_wordpress_connect_complete_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->complete_wordpress_connect_session_api_v1_integrations_wordpress_connect_complete_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **word_press_connect_complete_payload** | [**WordPressConnectCompletePayload**](WordPressConnectCompletePayload.md)|  |

### Return type

[**WordPressConnectPollResponse**](WordPressConnectPollResponse.md)

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

# **create_ghost_integration_api_v1_integrations_ghost_post**
> GhostIntegrationResponse create_ghost_integration_api_v1_integrations_ghost_post(ghost_integration_create)

Configure Ghost integration

Save your Ghost instance URL and Admin API key to enable automatic signing via webhooks. Returns a webhook URL containing a scoped token — copy it into Ghost.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.ghost_integration_create import GhostIntegrationCreate
from encypher.models.ghost_integration_response import GhostIntegrationResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    ghost_integration_create = encypher.GhostIntegrationCreate() # GhostIntegrationCreate |

    try:
        # Configure Ghost integration
        api_response = api_instance.create_ghost_integration_api_v1_integrations_ghost_post(ghost_integration_create)
        print("The response of IntegrationsApi->create_ghost_integration_api_v1_integrations_ghost_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->create_ghost_integration_api_v1_integrations_ghost_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ghost_integration_create** | [**GhostIntegrationCreate**](GhostIntegrationCreate.md)|  |

### Return type

[**GhostIntegrationResponse**](GhostIntegrationResponse.md)

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

# **create_ghost_integration_api_v1_integrations_ghost_post_0**
> GhostIntegrationResponse create_ghost_integration_api_v1_integrations_ghost_post_0(ghost_integration_create)

Configure Ghost integration

Save your Ghost instance URL and Admin API key to enable automatic signing via webhooks. Returns a webhook URL containing a scoped token — copy it into Ghost.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.ghost_integration_create import GhostIntegrationCreate
from encypher.models.ghost_integration_response import GhostIntegrationResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    ghost_integration_create = encypher.GhostIntegrationCreate() # GhostIntegrationCreate |

    try:
        # Configure Ghost integration
        api_response = api_instance.create_ghost_integration_api_v1_integrations_ghost_post_0(ghost_integration_create)
        print("The response of IntegrationsApi->create_ghost_integration_api_v1_integrations_ghost_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->create_ghost_integration_api_v1_integrations_ghost_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ghost_integration_create** | [**GhostIntegrationCreate**](GhostIntegrationCreate.md)|  |

### Return type

[**GhostIntegrationResponse**](GhostIntegrationResponse.md)

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

# **delete_ghost_integration_api_v1_integrations_ghost_delete**
> delete_ghost_integration_api_v1_integrations_ghost_delete()

Remove Ghost integration

Deactivate the Ghost integration for this organization.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)

    try:
        # Remove Ghost integration
        api_instance.delete_ghost_integration_api_v1_integrations_ghost_delete()
    except Exception as e:
        print("Exception when calling IntegrationsApi->delete_ghost_integration_api_v1_integrations_ghost_delete: %s\n" % e)
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

# **delete_ghost_integration_api_v1_integrations_ghost_delete_0**
> delete_ghost_integration_api_v1_integrations_ghost_delete_0()

Remove Ghost integration

Deactivate the Ghost integration for this organization.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)

    try:
        # Remove Ghost integration
        api_instance.delete_ghost_integration_api_v1_integrations_ghost_delete_0()
    except Exception as e:
        print("Exception when calling IntegrationsApi->delete_ghost_integration_api_v1_integrations_ghost_delete_0: %s\n" % e)
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

# **get_ghost_integration_api_v1_integrations_ghost_get**
> GhostIntegrationResponse get_ghost_integration_api_v1_integrations_ghost_get()

Get Ghost integration config

Returns the current Ghost integration configuration with the API key masked.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.ghost_integration_response import GhostIntegrationResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)

    try:
        # Get Ghost integration config
        api_response = api_instance.get_ghost_integration_api_v1_integrations_ghost_get()
        print("The response of IntegrationsApi->get_ghost_integration_api_v1_integrations_ghost_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->get_ghost_integration_api_v1_integrations_ghost_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GhostIntegrationResponse**](GhostIntegrationResponse.md)

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

# **get_ghost_integration_api_v1_integrations_ghost_get_0**
> GhostIntegrationResponse get_ghost_integration_api_v1_integrations_ghost_get_0()

Get Ghost integration config

Returns the current Ghost integration configuration with the API key masked.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.ghost_integration_response import GhostIntegrationResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)

    try:
        # Get Ghost integration config
        api_response = api_instance.get_ghost_integration_api_v1_integrations_ghost_get_0()
        print("The response of IntegrationsApi->get_ghost_integration_api_v1_integrations_ghost_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->get_ghost_integration_api_v1_integrations_ghost_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GhostIntegrationResponse**](GhostIntegrationResponse.md)

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

# **get_wordpress_integration_status_api_v1_integrations_wordpress_status_get**
> WordPressIntegrationStatusResponse get_wordpress_integration_status_api_v1_integrations_wordpress_status_get()

Get WordPress integration status

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.word_press_integration_status_response import WordPressIntegrationStatusResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)

    try:
        # Get WordPress integration status
        api_response = api_instance.get_wordpress_integration_status_api_v1_integrations_wordpress_status_get()
        print("The response of IntegrationsApi->get_wordpress_integration_status_api_v1_integrations_wordpress_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->get_wordpress_integration_status_api_v1_integrations_wordpress_status_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**WordPressIntegrationStatusResponse**](WordPressIntegrationStatusResponse.md)

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

# **get_wordpress_integration_status_api_v1_integrations_wordpress_status_get_0**
> WordPressIntegrationStatusResponse get_wordpress_integration_status_api_v1_integrations_wordpress_status_get_0()

Get WordPress integration status

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.word_press_integration_status_response import WordPressIntegrationStatusResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)

    try:
        # Get WordPress integration status
        api_response = api_instance.get_wordpress_integration_status_api_v1_integrations_wordpress_status_get_0()
        print("The response of IntegrationsApi->get_wordpress_integration_status_api_v1_integrations_wordpress_status_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->get_wordpress_integration_status_api_v1_integrations_wordpress_status_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**WordPressIntegrationStatusResponse**](WordPressIntegrationStatusResponse.md)

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

# **ghost_webhook_api_v1_integrations_ghost_webhook_post**
> object ghost_webhook_api_v1_integrations_ghost_webhook_post(token)

Receive Ghost CMS webhooks

Webhook endpoint for Ghost CMS. Configure in Ghost Admin → Integrations → Webhooks.

Use the `webhook_url` returned when you created the integration — it contains a scoped token.

Supported events: `post.published`, `post.published.edited`, `page.published`, `page.published.edited`

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.IntegrationsApi(api_client)
    token = 'token_example' # str | Webhook token (ghwh_...) from integration setup

    try:
        # Receive Ghost CMS webhooks
        api_response = api_instance.ghost_webhook_api_v1_integrations_ghost_webhook_post(token)
        print("The response of IntegrationsApi->ghost_webhook_api_v1_integrations_ghost_webhook_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->ghost_webhook_api_v1_integrations_ghost_webhook_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| Webhook token (ghwh_...) from integration setup |

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

# **ghost_webhook_api_v1_integrations_ghost_webhook_post_0**
> object ghost_webhook_api_v1_integrations_ghost_webhook_post_0(token)

Receive Ghost CMS webhooks

Webhook endpoint for Ghost CMS. Configure in Ghost Admin → Integrations → Webhooks.

Use the `webhook_url` returned when you created the integration — it contains a scoped token.

Supported events: `post.published`, `post.published.edited`, `page.published`, `page.published.edited`

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.IntegrationsApi(api_client)
    token = 'token_example' # str | Webhook token (ghwh_...) from integration setup

    try:
        # Receive Ghost CMS webhooks
        api_response = api_instance.ghost_webhook_api_v1_integrations_ghost_webhook_post_0(token)
        print("The response of IntegrationsApi->ghost_webhook_api_v1_integrations_ghost_webhook_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->ghost_webhook_api_v1_integrations_ghost_webhook_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| Webhook token (ghwh_...) from integration setup |

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

# **manual_sign_ghost_post_api_v1_integrations_ghost_sign_post_id_post**
> object manual_sign_ghost_post_api_v1_integrations_ghost_sign_post_id_post(post_id, ghost_manual_sign_request=ghost_manual_sign_request)

Manually sign a Ghost post

Trigger signing for a specific Ghost post or page.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.ghost_manual_sign_request import GhostManualSignRequest
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    post_id = 'post_id_example' # str |
    ghost_manual_sign_request = encypher.GhostManualSignRequest() # GhostManualSignRequest |  (optional)

    try:
        # Manually sign a Ghost post
        api_response = api_instance.manual_sign_ghost_post_api_v1_integrations_ghost_sign_post_id_post(post_id, ghost_manual_sign_request=ghost_manual_sign_request)
        print("The response of IntegrationsApi->manual_sign_ghost_post_api_v1_integrations_ghost_sign_post_id_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->manual_sign_ghost_post_api_v1_integrations_ghost_sign_post_id_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **post_id** | **str**|  |
 **ghost_manual_sign_request** | [**GhostManualSignRequest**](GhostManualSignRequest.md)|  | [optional]

### Return type

**object**

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

# **manual_sign_ghost_post_api_v1_integrations_ghost_sign_post_id_post_0**
> object manual_sign_ghost_post_api_v1_integrations_ghost_sign_post_id_post_0(post_id, ghost_manual_sign_request=ghost_manual_sign_request)

Manually sign a Ghost post

Trigger signing for a specific Ghost post or page.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.ghost_manual_sign_request import GhostManualSignRequest
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    post_id = 'post_id_example' # str |
    ghost_manual_sign_request = encypher.GhostManualSignRequest() # GhostManualSignRequest |  (optional)

    try:
        # Manually sign a Ghost post
        api_response = api_instance.manual_sign_ghost_post_api_v1_integrations_ghost_sign_post_id_post_0(post_id, ghost_manual_sign_request=ghost_manual_sign_request)
        print("The response of IntegrationsApi->manual_sign_ghost_post_api_v1_integrations_ghost_sign_post_id_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->manual_sign_ghost_post_api_v1_integrations_ghost_sign_post_id_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **post_id** | **str**|  |
 **ghost_manual_sign_request** | [**GhostManualSignRequest**](GhostManualSignRequest.md)|  | [optional]

### Return type

**object**

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

# **poll_wordpress_connect_session_api_v1_integrations_wordpress_connect_session_session_id_get**
> WordPressConnectPollResponse poll_wordpress_connect_session_api_v1_integrations_wordpress_connect_session_session_id_get(session_id)

Poll a WordPress magic-link connect session

### Example


```python
import encypher
from encypher.models.word_press_connect_poll_response import WordPressConnectPollResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.IntegrationsApi(api_client)
    session_id = 'session_id_example' # str |

    try:
        # Poll a WordPress magic-link connect session
        api_response = api_instance.poll_wordpress_connect_session_api_v1_integrations_wordpress_connect_session_session_id_get(session_id)
        print("The response of IntegrationsApi->poll_wordpress_connect_session_api_v1_integrations_wordpress_connect_session_session_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->poll_wordpress_connect_session_api_v1_integrations_wordpress_connect_session_session_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  |

### Return type

[**WordPressConnectPollResponse**](WordPressConnectPollResponse.md)

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

# **poll_wordpress_connect_session_api_v1_integrations_wordpress_connect_session_session_id_get_0**
> WordPressConnectPollResponse poll_wordpress_connect_session_api_v1_integrations_wordpress_connect_session_session_id_get_0(session_id)

Poll a WordPress magic-link connect session

### Example


```python
import encypher
from encypher.models.word_press_connect_poll_response import WordPressConnectPollResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.IntegrationsApi(api_client)
    session_id = 'session_id_example' # str |

    try:
        # Poll a WordPress magic-link connect session
        api_response = api_instance.poll_wordpress_connect_session_api_v1_integrations_wordpress_connect_session_session_id_get_0(session_id)
        print("The response of IntegrationsApi->poll_wordpress_connect_session_api_v1_integrations_wordpress_connect_session_session_id_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->poll_wordpress_connect_session_api_v1_integrations_wordpress_connect_session_session_id_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  |

### Return type

[**WordPressConnectPollResponse**](WordPressConnectPollResponse.md)

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

# **pull_wordpress_install_actions_api_v1_integrations_wordpress_install_id_actions_pull_post**
> WordPressIntegrationStatusResponse pull_wordpress_install_actions_api_v1_integrations_wordpress_install_id_actions_pull_post(install_id)

Pull queued remote actions for a WordPress install

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.word_press_integration_status_response import WordPressIntegrationStatusResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    install_id = 'install_id_example' # str |

    try:
        # Pull queued remote actions for a WordPress install
        api_response = api_instance.pull_wordpress_install_actions_api_v1_integrations_wordpress_install_id_actions_pull_post(install_id)
        print("The response of IntegrationsApi->pull_wordpress_install_actions_api_v1_integrations_wordpress_install_id_actions_pull_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->pull_wordpress_install_actions_api_v1_integrations_wordpress_install_id_actions_pull_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **install_id** | **str**|  |

### Return type

[**WordPressIntegrationStatusResponse**](WordPressIntegrationStatusResponse.md)

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

# **pull_wordpress_install_actions_api_v1_integrations_wordpress_install_id_actions_pull_post_0**
> WordPressIntegrationStatusResponse pull_wordpress_install_actions_api_v1_integrations_wordpress_install_id_actions_pull_post_0(install_id)

Pull queued remote actions for a WordPress install

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.word_press_integration_status_response import WordPressIntegrationStatusResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    install_id = 'install_id_example' # str |

    try:
        # Pull queued remote actions for a WordPress install
        api_response = api_instance.pull_wordpress_install_actions_api_v1_integrations_wordpress_install_id_actions_pull_post_0(install_id)
        print("The response of IntegrationsApi->pull_wordpress_install_actions_api_v1_integrations_wordpress_install_id_actions_pull_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->pull_wordpress_install_actions_api_v1_integrations_wordpress_install_id_actions_pull_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **install_id** | **str**|  |

### Return type

[**WordPressIntegrationStatusResponse**](WordPressIntegrationStatusResponse.md)

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

# **queue_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_post**
> WordPressIntegrationStatusResponse queue_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_post(install_id, word_press_action_queue_payload)

Queue a remote action for a WordPress install

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.word_press_action_queue_payload import WordPressActionQueuePayload
from encypher.models.word_press_integration_status_response import WordPressIntegrationStatusResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    install_id = 'install_id_example' # str |
    word_press_action_queue_payload = encypher.WordPressActionQueuePayload() # WordPressActionQueuePayload |

    try:
        # Queue a remote action for a WordPress install
        api_response = api_instance.queue_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_post(install_id, word_press_action_queue_payload)
        print("The response of IntegrationsApi->queue_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->queue_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **install_id** | **str**|  |
 **word_press_action_queue_payload** | [**WordPressActionQueuePayload**](WordPressActionQueuePayload.md)|  |

### Return type

[**WordPressIntegrationStatusResponse**](WordPressIntegrationStatusResponse.md)

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

# **queue_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_post_0**
> WordPressIntegrationStatusResponse queue_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_post_0(install_id, word_press_action_queue_payload)

Queue a remote action for a WordPress install

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.word_press_action_queue_payload import WordPressActionQueuePayload
from encypher.models.word_press_integration_status_response import WordPressIntegrationStatusResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    install_id = 'install_id_example' # str |
    word_press_action_queue_payload = encypher.WordPressActionQueuePayload() # WordPressActionQueuePayload |

    try:
        # Queue a remote action for a WordPress install
        api_response = api_instance.queue_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_post_0(install_id, word_press_action_queue_payload)
        print("The response of IntegrationsApi->queue_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->queue_wordpress_install_action_api_v1_integrations_wordpress_install_id_actions_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **install_id** | **str**|  |
 **word_press_action_queue_payload** | [**WordPressActionQueuePayload**](WordPressActionQueuePayload.md)|  |

### Return type

[**WordPressIntegrationStatusResponse**](WordPressIntegrationStatusResponse.md)

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

# **record_wordpress_verification_event_api_v1_integrations_wordpress_verification_event_post**
> WordPressIntegrationStatusResponse record_wordpress_verification_event_api_v1_integrations_wordpress_verification_event_post(word_press_verification_event_payload)

Record a WordPress verification event

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.word_press_integration_status_response import WordPressIntegrationStatusResponse
from encypher.models.word_press_verification_event_payload import WordPressVerificationEventPayload
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    word_press_verification_event_payload = encypher.WordPressVerificationEventPayload() # WordPressVerificationEventPayload |

    try:
        # Record a WordPress verification event
        api_response = api_instance.record_wordpress_verification_event_api_v1_integrations_wordpress_verification_event_post(word_press_verification_event_payload)
        print("The response of IntegrationsApi->record_wordpress_verification_event_api_v1_integrations_wordpress_verification_event_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->record_wordpress_verification_event_api_v1_integrations_wordpress_verification_event_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **word_press_verification_event_payload** | [**WordPressVerificationEventPayload**](WordPressVerificationEventPayload.md)|  |

### Return type

[**WordPressIntegrationStatusResponse**](WordPressIntegrationStatusResponse.md)

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

# **record_wordpress_verification_event_api_v1_integrations_wordpress_verification_event_post_0**
> WordPressIntegrationStatusResponse record_wordpress_verification_event_api_v1_integrations_wordpress_verification_event_post_0(word_press_verification_event_payload)

Record a WordPress verification event

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.word_press_integration_status_response import WordPressIntegrationStatusResponse
from encypher.models.word_press_verification_event_payload import WordPressVerificationEventPayload
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    word_press_verification_event_payload = encypher.WordPressVerificationEventPayload() # WordPressVerificationEventPayload |

    try:
        # Record a WordPress verification event
        api_response = api_instance.record_wordpress_verification_event_api_v1_integrations_wordpress_verification_event_post_0(word_press_verification_event_payload)
        print("The response of IntegrationsApi->record_wordpress_verification_event_api_v1_integrations_wordpress_verification_event_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->record_wordpress_verification_event_api_v1_integrations_wordpress_verification_event_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **word_press_verification_event_payload** | [**WordPressVerificationEventPayload**](WordPressVerificationEventPayload.md)|  |

### Return type

[**WordPressIntegrationStatusResponse**](WordPressIntegrationStatusResponse.md)

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

# **regenerate_ghost_token_api_v1_integrations_ghost_regenerate_token_post**
> GhostTokenRegenerateResponse regenerate_ghost_token_api_v1_integrations_ghost_regenerate_token_post()

Regenerate webhook token

Invalidate the current webhook token and generate a new one. You must update the webhook URL in Ghost after regenerating.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.ghost_token_regenerate_response import GhostTokenRegenerateResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)

    try:
        # Regenerate webhook token
        api_response = api_instance.regenerate_ghost_token_api_v1_integrations_ghost_regenerate_token_post()
        print("The response of IntegrationsApi->regenerate_ghost_token_api_v1_integrations_ghost_regenerate_token_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->regenerate_ghost_token_api_v1_integrations_ghost_regenerate_token_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GhostTokenRegenerateResponse**](GhostTokenRegenerateResponse.md)

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

# **regenerate_ghost_token_api_v1_integrations_ghost_regenerate_token_post_0**
> GhostTokenRegenerateResponse regenerate_ghost_token_api_v1_integrations_ghost_regenerate_token_post_0()

Regenerate webhook token

Invalidate the current webhook token and generate a new one. You must update the webhook URL in Ghost after regenerating.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.ghost_token_regenerate_response import GhostTokenRegenerateResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)

    try:
        # Regenerate webhook token
        api_response = api_instance.regenerate_ghost_token_api_v1_integrations_ghost_regenerate_token_post_0()
        print("The response of IntegrationsApi->regenerate_ghost_token_api_v1_integrations_ghost_regenerate_token_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->regenerate_ghost_token_api_v1_integrations_ghost_regenerate_token_post_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GhostTokenRegenerateResponse**](GhostTokenRegenerateResponse.md)

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

# **register_wordpress_install_api_v1_integrations_wordpress_register_install_post**
> WordPressIntegrationStatusResponse register_wordpress_install_api_v1_integrations_wordpress_register_install_post(word_press_install_registration_payload)

Register or update a WordPress install

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.word_press_install_registration_payload import WordPressInstallRegistrationPayload
from encypher.models.word_press_integration_status_response import WordPressIntegrationStatusResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    word_press_install_registration_payload = encypher.WordPressInstallRegistrationPayload() # WordPressInstallRegistrationPayload |

    try:
        # Register or update a WordPress install
        api_response = api_instance.register_wordpress_install_api_v1_integrations_wordpress_register_install_post(word_press_install_registration_payload)
        print("The response of IntegrationsApi->register_wordpress_install_api_v1_integrations_wordpress_register_install_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->register_wordpress_install_api_v1_integrations_wordpress_register_install_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **word_press_install_registration_payload** | [**WordPressInstallRegistrationPayload**](WordPressInstallRegistrationPayload.md)|  |

### Return type

[**WordPressIntegrationStatusResponse**](WordPressIntegrationStatusResponse.md)

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

# **register_wordpress_install_api_v1_integrations_wordpress_register_install_post_0**
> WordPressIntegrationStatusResponse register_wordpress_install_api_v1_integrations_wordpress_register_install_post_0(word_press_install_registration_payload)

Register or update a WordPress install

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.word_press_install_registration_payload import WordPressInstallRegistrationPayload
from encypher.models.word_press_integration_status_response import WordPressIntegrationStatusResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    word_press_install_registration_payload = encypher.WordPressInstallRegistrationPayload() # WordPressInstallRegistrationPayload |

    try:
        # Register or update a WordPress install
        api_response = api_instance.register_wordpress_install_api_v1_integrations_wordpress_register_install_post_0(word_press_install_registration_payload)
        print("The response of IntegrationsApi->register_wordpress_install_api_v1_integrations_wordpress_register_install_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->register_wordpress_install_api_v1_integrations_wordpress_register_install_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **word_press_install_registration_payload** | [**WordPressInstallRegistrationPayload**](WordPressInstallRegistrationPayload.md)|  |

### Return type

[**WordPressIntegrationStatusResponse**](WordPressIntegrationStatusResponse.md)

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

# **start_wordpress_connect_session_api_v1_integrations_wordpress_connect_start_post**
> WordPressConnectPollResponse start_wordpress_connect_session_api_v1_integrations_wordpress_connect_start_post(word_press_connect_start_payload)

Start a WordPress magic-link connect session

### Example


```python
import encypher
from encypher.models.word_press_connect_poll_response import WordPressConnectPollResponse
from encypher.models.word_press_connect_start_payload import WordPressConnectStartPayload
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.IntegrationsApi(api_client)
    word_press_connect_start_payload = encypher.WordPressConnectStartPayload() # WordPressConnectStartPayload |

    try:
        # Start a WordPress magic-link connect session
        api_response = api_instance.start_wordpress_connect_session_api_v1_integrations_wordpress_connect_start_post(word_press_connect_start_payload)
        print("The response of IntegrationsApi->start_wordpress_connect_session_api_v1_integrations_wordpress_connect_start_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->start_wordpress_connect_session_api_v1_integrations_wordpress_connect_start_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **word_press_connect_start_payload** | [**WordPressConnectStartPayload**](WordPressConnectStartPayload.md)|  |

### Return type

[**WordPressConnectPollResponse**](WordPressConnectPollResponse.md)

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

# **start_wordpress_connect_session_api_v1_integrations_wordpress_connect_start_post_0**
> WordPressConnectPollResponse start_wordpress_connect_session_api_v1_integrations_wordpress_connect_start_post_0(word_press_connect_start_payload)

Start a WordPress magic-link connect session

### Example


```python
import encypher
from encypher.models.word_press_connect_poll_response import WordPressConnectPollResponse
from encypher.models.word_press_connect_start_payload import WordPressConnectStartPayload
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.IntegrationsApi(api_client)
    word_press_connect_start_payload = encypher.WordPressConnectStartPayload() # WordPressConnectStartPayload |

    try:
        # Start a WordPress magic-link connect session
        api_response = api_instance.start_wordpress_connect_session_api_v1_integrations_wordpress_connect_start_post_0(word_press_connect_start_payload)
        print("The response of IntegrationsApi->start_wordpress_connect_session_api_v1_integrations_wordpress_connect_start_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->start_wordpress_connect_session_api_v1_integrations_wordpress_connect_start_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **word_press_connect_start_payload** | [**WordPressConnectStartPayload**](WordPressConnectStartPayload.md)|  |

### Return type

[**WordPressConnectPollResponse**](WordPressConnectPollResponse.md)

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

# **sync_wordpress_integration_status_api_v1_integrations_wordpress_status_sync_post**
> WordPressIntegrationStatusResponse sync_wordpress_integration_status_api_v1_integrations_wordpress_status_sync_post(word_press_integration_status_payload)

Sync WordPress integration status

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.word_press_integration_status_payload import WordPressIntegrationStatusPayload
from encypher.models.word_press_integration_status_response import WordPressIntegrationStatusResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    word_press_integration_status_payload = encypher.WordPressIntegrationStatusPayload() # WordPressIntegrationStatusPayload |

    try:
        # Sync WordPress integration status
        api_response = api_instance.sync_wordpress_integration_status_api_v1_integrations_wordpress_status_sync_post(word_press_integration_status_payload)
        print("The response of IntegrationsApi->sync_wordpress_integration_status_api_v1_integrations_wordpress_status_sync_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->sync_wordpress_integration_status_api_v1_integrations_wordpress_status_sync_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **word_press_integration_status_payload** | [**WordPressIntegrationStatusPayload**](WordPressIntegrationStatusPayload.md)|  |

### Return type

[**WordPressIntegrationStatusResponse**](WordPressIntegrationStatusResponse.md)

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

# **sync_wordpress_integration_status_api_v1_integrations_wordpress_status_sync_post_0**
> WordPressIntegrationStatusResponse sync_wordpress_integration_status_api_v1_integrations_wordpress_status_sync_post_0(word_press_integration_status_payload)

Sync WordPress integration status

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.word_press_integration_status_payload import WordPressIntegrationStatusPayload
from encypher.models.word_press_integration_status_response import WordPressIntegrationStatusResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
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
    api_instance = encypher.IntegrationsApi(api_client)
    word_press_integration_status_payload = encypher.WordPressIntegrationStatusPayload() # WordPressIntegrationStatusPayload |

    try:
        # Sync WordPress integration status
        api_response = api_instance.sync_wordpress_integration_status_api_v1_integrations_wordpress_status_sync_post_0(word_press_integration_status_payload)
        print("The response of IntegrationsApi->sync_wordpress_integration_status_api_v1_integrations_wordpress_status_sync_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntegrationsApi->sync_wordpress_integration_status_api_v1_integrations_wordpress_status_sync_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **word_press_integration_status_payload** | [**WordPressIntegrationStatusPayload**](WordPressIntegrationStatusPayload.md)|  |

### Return type

[**WordPressIntegrationStatusResponse**](WordPressIntegrationStatusResponse.md)

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
