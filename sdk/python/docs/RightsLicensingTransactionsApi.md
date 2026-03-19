# encypher.RightsLicensingTransactionsApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_licensing_request_api_v1_rights_licensing_request_post**](RightsLicensingTransactionsApi.md#create_licensing_request_api_v1_rights_licensing_request_post) | **POST** /api/v1/rights-licensing/request | Submit a licensing request
[**create_licensing_request_api_v1_rights_licensing_request_post_0**](RightsLicensingTransactionsApi.md#create_licensing_request_api_v1_rights_licensing_request_post_0) | **POST** /api/v1/rights-licensing/request | Submit a licensing request
[**get_agreement_api_v1_rights_licensing_agreements_agreement_id_get**](RightsLicensingTransactionsApi.md#get_agreement_api_v1_rights_licensing_agreements_agreement_id_get) | **GET** /api/v1/rights-licensing/agreements/{agreement_id} | Get specific agreement details
[**get_agreement_api_v1_rights_licensing_agreements_agreement_id_get_0**](RightsLicensingTransactionsApi.md#get_agreement_api_v1_rights_licensing_agreements_agreement_id_get_0) | **GET** /api/v1/rights-licensing/agreements/{agreement_id} | Get specific agreement details
[**get_agreement_usage_api_v1_rights_licensing_agreements_agreement_id_usage_get**](RightsLicensingTransactionsApi.md#get_agreement_usage_api_v1_rights_licensing_agreements_agreement_id_usage_get) | **GET** /api/v1/rights-licensing/agreements/{agreement_id}/usage | Get usage metrics for an active agreement
[**get_agreement_usage_api_v1_rights_licensing_agreements_agreement_id_usage_get_0**](RightsLicensingTransactionsApi.md#get_agreement_usage_api_v1_rights_licensing_agreements_agreement_id_usage_get_0) | **GET** /api/v1/rights-licensing/agreements/{agreement_id}/usage | Get usage metrics for an active agreement
[**list_agreements_api_v1_rights_licensing_agreements_get**](RightsLicensingTransactionsApi.md#list_agreements_api_v1_rights_licensing_agreements_get) | **GET** /api/v1/rights-licensing/agreements | List active licensing agreements
[**list_agreements_api_v1_rights_licensing_agreements_get_0**](RightsLicensingTransactionsApi.md#list_agreements_api_v1_rights_licensing_agreements_get_0) | **GET** /api/v1/rights-licensing/agreements | List active licensing agreements
[**list_licensing_requests_api_v1_rights_licensing_requests_get**](RightsLicensingTransactionsApi.md#list_licensing_requests_api_v1_rights_licensing_requests_get) | **GET** /api/v1/rights-licensing/requests | List licensing requests
[**list_licensing_requests_api_v1_rights_licensing_requests_get_0**](RightsLicensingTransactionsApi.md#list_licensing_requests_api_v1_rights_licensing_requests_get_0) | **GET** /api/v1/rights-licensing/requests | List licensing requests
[**respond_to_licensing_request_api_v1_rights_licensing_requests_request_id_respond_put**](RightsLicensingTransactionsApi.md#respond_to_licensing_request_api_v1_rights_licensing_requests_request_id_respond_put) | **PUT** /api/v1/rights-licensing/requests/{request_id}/respond | Publisher responds to a licensing request
[**respond_to_licensing_request_api_v1_rights_licensing_requests_request_id_respond_put_0**](RightsLicensingTransactionsApi.md#respond_to_licensing_request_api_v1_rights_licensing_requests_request_id_respond_put_0) | **PUT** /api/v1/rights-licensing/requests/{request_id}/respond | Publisher responds to a licensing request


# **create_licensing_request_api_v1_rights_licensing_request_post**
> Dict[str, object] create_licensing_request_api_v1_rights_licensing_request_post(request_body)

Submit a licensing request

Submit a licensing request for publisher content.

**Requester** (AI company / consumer): Sends a request to a publisher for
rights to use their content at a specific tier (bronze, silver, or gold).

The publisher is notified and can approve, counter, or reject the request.

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
    api_instance = encypher.RightsLicensingTransactionsApi(api_client)
    request_body = None # Dict[str, object] |

    try:
        # Submit a licensing request
        api_response = api_instance.create_licensing_request_api_v1_rights_licensing_request_post(request_body)
        print("The response of RightsLicensingTransactionsApi->create_licensing_request_api_v1_rights_licensing_request_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RightsLicensingTransactionsApi->create_licensing_request_api_v1_rights_licensing_request_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**Dict[str, object]**](object.md)|  |

### Return type

**Dict[str, object]**

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

# **create_licensing_request_api_v1_rights_licensing_request_post_0**
> Dict[str, object] create_licensing_request_api_v1_rights_licensing_request_post_0(request_body)

Submit a licensing request

Submit a licensing request for publisher content.

**Requester** (AI company / consumer): Sends a request to a publisher for
rights to use their content at a specific tier (bronze, silver, or gold).

The publisher is notified and can approve, counter, or reject the request.

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
    api_instance = encypher.RightsLicensingTransactionsApi(api_client)
    request_body = None # Dict[str, object] |

    try:
        # Submit a licensing request
        api_response = api_instance.create_licensing_request_api_v1_rights_licensing_request_post_0(request_body)
        print("The response of RightsLicensingTransactionsApi->create_licensing_request_api_v1_rights_licensing_request_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RightsLicensingTransactionsApi->create_licensing_request_api_v1_rights_licensing_request_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**Dict[str, object]**](object.md)|  |

### Return type

**Dict[str, object]**

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

# **get_agreement_api_v1_rights_licensing_agreements_agreement_id_get**
> Dict[str, object] get_agreement_api_v1_rights_licensing_agreements_agreement_id_get(agreement_id)

Get specific agreement details

Retrieve the full terms, scope, and status for a specific licensing agreement. Only accessible to the publisher or licensee party to the agreement.

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
    api_instance = encypher.RightsLicensingTransactionsApi(api_client)
    agreement_id = 'agreement_id_example' # str | Agreement UUID

    try:
        # Get specific agreement details
        api_response = api_instance.get_agreement_api_v1_rights_licensing_agreements_agreement_id_get(agreement_id)
        print("The response of RightsLicensingTransactionsApi->get_agreement_api_v1_rights_licensing_agreements_agreement_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RightsLicensingTransactionsApi->get_agreement_api_v1_rights_licensing_agreements_agreement_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agreement_id** | **str**| Agreement UUID |

### Return type

**Dict[str, object]**

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

# **get_agreement_api_v1_rights_licensing_agreements_agreement_id_get_0**
> Dict[str, object] get_agreement_api_v1_rights_licensing_agreements_agreement_id_get_0(agreement_id)

Get specific agreement details

Retrieve the full terms, scope, and status for a specific licensing agreement. Only accessible to the publisher or licensee party to the agreement.

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
    api_instance = encypher.RightsLicensingTransactionsApi(api_client)
    agreement_id = 'agreement_id_example' # str | Agreement UUID

    try:
        # Get specific agreement details
        api_response = api_instance.get_agreement_api_v1_rights_licensing_agreements_agreement_id_get_0(agreement_id)
        print("The response of RightsLicensingTransactionsApi->get_agreement_api_v1_rights_licensing_agreements_agreement_id_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RightsLicensingTransactionsApi->get_agreement_api_v1_rights_licensing_agreements_agreement_id_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agreement_id** | **str**| Agreement UUID |

### Return type

**Dict[str, object]**

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

# **get_agreement_usage_api_v1_rights_licensing_agreements_agreement_id_usage_get**
> Dict[str, object] get_agreement_usage_api_v1_rights_licensing_agreements_agreement_id_usage_get(agreement_id)

Get usage metrics for an active agreement

Retrieve usage metrics (articles accessed, retrievals, ingestion events) for a specific licensing agreement. Useful for compliance monitoring and billing reconciliation.

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
    api_instance = encypher.RightsLicensingTransactionsApi(api_client)
    agreement_id = 'agreement_id_example' # str | Agreement UUID

    try:
        # Get usage metrics for an active agreement
        api_response = api_instance.get_agreement_usage_api_v1_rights_licensing_agreements_agreement_id_usage_get(agreement_id)
        print("The response of RightsLicensingTransactionsApi->get_agreement_usage_api_v1_rights_licensing_agreements_agreement_id_usage_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RightsLicensingTransactionsApi->get_agreement_usage_api_v1_rights_licensing_agreements_agreement_id_usage_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agreement_id** | **str**| Agreement UUID |

### Return type

**Dict[str, object]**

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

# **get_agreement_usage_api_v1_rights_licensing_agreements_agreement_id_usage_get_0**
> Dict[str, object] get_agreement_usage_api_v1_rights_licensing_agreements_agreement_id_usage_get_0(agreement_id)

Get usage metrics for an active agreement

Retrieve usage metrics (articles accessed, retrievals, ingestion events) for a specific licensing agreement. Useful for compliance monitoring and billing reconciliation.

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
    api_instance = encypher.RightsLicensingTransactionsApi(api_client)
    agreement_id = 'agreement_id_example' # str | Agreement UUID

    try:
        # Get usage metrics for an active agreement
        api_response = api_instance.get_agreement_usage_api_v1_rights_licensing_agreements_agreement_id_usage_get_0(agreement_id)
        print("The response of RightsLicensingTransactionsApi->get_agreement_usage_api_v1_rights_licensing_agreements_agreement_id_usage_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RightsLicensingTransactionsApi->get_agreement_usage_api_v1_rights_licensing_agreements_agreement_id_usage_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agreement_id** | **str**| Agreement UUID |

### Return type

**Dict[str, object]**

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

# **list_agreements_api_v1_rights_licensing_agreements_get**
> List[Optional[Dict[str, object]]] list_agreements_api_v1_rights_licensing_agreements_get()

List active licensing agreements

List all licensing agreements where the authenticated organization is either the publisher or the licensee, ordered by creation date.

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
    api_instance = encypher.RightsLicensingTransactionsApi(api_client)

    try:
        # List active licensing agreements
        api_response = api_instance.list_agreements_api_v1_rights_licensing_agreements_get()
        print("The response of RightsLicensingTransactionsApi->list_agreements_api_v1_rights_licensing_agreements_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RightsLicensingTransactionsApi->list_agreements_api_v1_rights_licensing_agreements_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**List[Optional[Dict[str, object]]]**

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

# **list_agreements_api_v1_rights_licensing_agreements_get_0**
> List[Optional[Dict[str, object]]] list_agreements_api_v1_rights_licensing_agreements_get_0()

List active licensing agreements

List all licensing agreements where the authenticated organization is either the publisher or the licensee, ordered by creation date.

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
    api_instance = encypher.RightsLicensingTransactionsApi(api_client)

    try:
        # List active licensing agreements
        api_response = api_instance.list_agreements_api_v1_rights_licensing_agreements_get_0()
        print("The response of RightsLicensingTransactionsApi->list_agreements_api_v1_rights_licensing_agreements_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RightsLicensingTransactionsApi->list_agreements_api_v1_rights_licensing_agreements_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**List[Optional[Dict[str, object]]]**

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

# **list_licensing_requests_api_v1_rights_licensing_requests_get**
> List[Optional[Dict[str, object]]] list_licensing_requests_api_v1_rights_licensing_requests_get(view=view, status=status)

List licensing requests

List licensing requests for the authenticated organization.

- **Publisher view**: incoming requests (where org is the publisher)
- **Consumer view**: outgoing requests (where org is the requester)

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
    api_instance = encypher.RightsLicensingTransactionsApi(api_client)
    view = 'incoming' # str | 'incoming' (publisher) or 'outgoing' (consumer) (optional) (default to 'incoming')
    status = 'status_example' # str | Filter by status: pending, approved, rejected, countered (optional)

    try:
        # List licensing requests
        api_response = api_instance.list_licensing_requests_api_v1_rights_licensing_requests_get(view=view, status=status)
        print("The response of RightsLicensingTransactionsApi->list_licensing_requests_api_v1_rights_licensing_requests_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RightsLicensingTransactionsApi->list_licensing_requests_api_v1_rights_licensing_requests_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **view** | **str**| &#39;incoming&#39; (publisher) or &#39;outgoing&#39; (consumer) | [optional] [default to &#39;incoming&#39;]
 **status** | **str**| Filter by status: pending, approved, rejected, countered | [optional]

### Return type

**List[Optional[Dict[str, object]]]**

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

# **list_licensing_requests_api_v1_rights_licensing_requests_get_0**
> List[Optional[Dict[str, object]]] list_licensing_requests_api_v1_rights_licensing_requests_get_0(view=view, status=status)

List licensing requests

List licensing requests for the authenticated organization.

- **Publisher view**: incoming requests (where org is the publisher)
- **Consumer view**: outgoing requests (where org is the requester)

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
    api_instance = encypher.RightsLicensingTransactionsApi(api_client)
    view = 'incoming' # str | 'incoming' (publisher) or 'outgoing' (consumer) (optional) (default to 'incoming')
    status = 'status_example' # str | Filter by status: pending, approved, rejected, countered (optional)

    try:
        # List licensing requests
        api_response = api_instance.list_licensing_requests_api_v1_rights_licensing_requests_get_0(view=view, status=status)
        print("The response of RightsLicensingTransactionsApi->list_licensing_requests_api_v1_rights_licensing_requests_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RightsLicensingTransactionsApi->list_licensing_requests_api_v1_rights_licensing_requests_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **view** | **str**| &#39;incoming&#39; (publisher) or &#39;outgoing&#39; (consumer) | [optional] [default to &#39;incoming&#39;]
 **status** | **str**| Filter by status: pending, approved, rejected, countered | [optional]

### Return type

**List[Optional[Dict[str, object]]]**

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

# **respond_to_licensing_request_api_v1_rights_licensing_requests_request_id_respond_put**
> Dict[str, object] respond_to_licensing_request_api_v1_rights_licensing_requests_request_id_respond_put(request_id, request_body)

Publisher responds to a licensing request

Publisher approves, counters, or rejects a licensing request.

- `approve`: Creates a licensing agreement and notifies requester
- `counter`: Returns counter-proposal for negotiation
- `reject`: Declines the request with optional reason

Requires: Publisher org admin.

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
    api_instance = encypher.RightsLicensingTransactionsApi(api_client)
    request_id = 'request_id_example' # str | Licensing request UUID
    request_body = None # Dict[str, object] |

    try:
        # Publisher responds to a licensing request
        api_response = api_instance.respond_to_licensing_request_api_v1_rights_licensing_requests_request_id_respond_put(request_id, request_body)
        print("The response of RightsLicensingTransactionsApi->respond_to_licensing_request_api_v1_rights_licensing_requests_request_id_respond_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RightsLicensingTransactionsApi->respond_to_licensing_request_api_v1_rights_licensing_requests_request_id_respond_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_id** | **str**| Licensing request UUID |
 **request_body** | [**Dict[str, object]**](object.md)|  |

### Return type

**Dict[str, object]**

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

# **respond_to_licensing_request_api_v1_rights_licensing_requests_request_id_respond_put_0**
> Dict[str, object] respond_to_licensing_request_api_v1_rights_licensing_requests_request_id_respond_put_0(request_id, request_body)

Publisher responds to a licensing request

Publisher approves, counters, or rejects a licensing request.

- `approve`: Creates a licensing agreement and notifies requester
- `counter`: Returns counter-proposal for negotiation
- `reject`: Declines the request with optional reason

Requires: Publisher org admin.

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
    api_instance = encypher.RightsLicensingTransactionsApi(api_client)
    request_id = 'request_id_example' # str | Licensing request UUID
    request_body = None # Dict[str, object] |

    try:
        # Publisher responds to a licensing request
        api_response = api_instance.respond_to_licensing_request_api_v1_rights_licensing_requests_request_id_respond_put_0(request_id, request_body)
        print("The response of RightsLicensingTransactionsApi->respond_to_licensing_request_api_v1_rights_licensing_requests_request_id_respond_put_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RightsLicensingTransactionsApi->respond_to_licensing_request_api_v1_rights_licensing_requests_request_id_respond_put_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_id** | **str**| Licensing request UUID |
 **request_body** | [**Dict[str, object]**](object.md)|  |

### Return type

**Dict[str, object]**

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
