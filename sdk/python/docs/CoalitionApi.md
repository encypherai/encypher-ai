# encypher.CoalitionApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_coalition_dashboard_api_v1_coalition_dashboard_get**](CoalitionApi.md#get_coalition_dashboard_api_v1_coalition_dashboard_get) | **GET** /api/v1/coalition/dashboard | Get Coalition Dashboard
[**get_coalition_dashboard_api_v1_coalition_dashboard_get_0**](CoalitionApi.md#get_coalition_dashboard_api_v1_coalition_dashboard_get_0) | **GET** /api/v1/coalition/dashboard | Get Coalition Dashboard
[**get_content_stats_api_v1_coalition_content_stats_get**](CoalitionApi.md#get_content_stats_api_v1_coalition_content_stats_get) | **GET** /api/v1/coalition/content-stats | Get Content Stats
[**get_content_stats_api_v1_coalition_content_stats_get_0**](CoalitionApi.md#get_content_stats_api_v1_coalition_content_stats_get_0) | **GET** /api/v1/coalition/content-stats | Get Content Stats
[**get_earnings_history_api_v1_coalition_earnings_get**](CoalitionApi.md#get_earnings_history_api_v1_coalition_earnings_get) | **GET** /api/v1/coalition/earnings | Get Earnings History
[**get_earnings_history_api_v1_coalition_earnings_get_0**](CoalitionApi.md#get_earnings_history_api_v1_coalition_earnings_get_0) | **GET** /api/v1/coalition/earnings | Get Earnings History
[**get_public_coalition_stats_api_v1_coalition_public_stats_get**](CoalitionApi.md#get_public_coalition_stats_api_v1_coalition_public_stats_get) | **GET** /api/v1/coalition/public/stats | Public coalition aggregate statistics
[**get_public_coalition_stats_api_v1_coalition_public_stats_get_0**](CoalitionApi.md#get_public_coalition_stats_api_v1_coalition_public_stats_get_0) | **GET** /api/v1/coalition/public/stats | Public coalition aggregate statistics
[**opt_in_to_coalition_api_v1_coalition_opt_in_post**](CoalitionApi.md#opt_in_to_coalition_api_v1_coalition_opt_in_post) | **POST** /api/v1/coalition/opt-in | Opt In To Coalition
[**opt_in_to_coalition_api_v1_coalition_opt_in_post_0**](CoalitionApi.md#opt_in_to_coalition_api_v1_coalition_opt_in_post_0) | **POST** /api/v1/coalition/opt-in | Opt In To Coalition
[**opt_out_of_coalition_api_v1_coalition_opt_out_post**](CoalitionApi.md#opt_out_of_coalition_api_v1_coalition_opt_out_post) | **POST** /api/v1/coalition/opt-out | Opt Out Of Coalition
[**opt_out_of_coalition_api_v1_coalition_opt_out_post_0**](CoalitionApi.md#opt_out_of_coalition_api_v1_coalition_opt_out_post_0) | **POST** /api/v1/coalition/opt-out | Opt Out Of Coalition


# **get_coalition_dashboard_api_v1_coalition_dashboard_get**
> CoalitionDashboardResponse get_coalition_dashboard_api_v1_coalition_dashboard_get()

Get Coalition Dashboard

Get coalition dashboard data for the organization.

Returns content stats, earnings, and payout information.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.coalition_dashboard_response import CoalitionDashboardResponse
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
    api_instance = encypher.CoalitionApi(api_client)

    try:
        # Get Coalition Dashboard
        api_response = api_instance.get_coalition_dashboard_api_v1_coalition_dashboard_get()
        print("The response of CoalitionApi->get_coalition_dashboard_api_v1_coalition_dashboard_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CoalitionApi->get_coalition_dashboard_api_v1_coalition_dashboard_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**CoalitionDashboardResponse**](CoalitionDashboardResponse.md)

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

# **get_coalition_dashboard_api_v1_coalition_dashboard_get_0**
> CoalitionDashboardResponse get_coalition_dashboard_api_v1_coalition_dashboard_get_0()

Get Coalition Dashboard

Get coalition dashboard data for the organization.

Returns content stats, earnings, and payout information.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.coalition_dashboard_response import CoalitionDashboardResponse
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
    api_instance = encypher.CoalitionApi(api_client)

    try:
        # Get Coalition Dashboard
        api_response = api_instance.get_coalition_dashboard_api_v1_coalition_dashboard_get_0()
        print("The response of CoalitionApi->get_coalition_dashboard_api_v1_coalition_dashboard_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CoalitionApi->get_coalition_dashboard_api_v1_coalition_dashboard_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**CoalitionDashboardResponse**](CoalitionDashboardResponse.md)

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

# **get_content_stats_api_v1_coalition_content_stats_get**
> object get_content_stats_api_v1_coalition_content_stats_get(months=months)

Get Content Stats

Get historical content corpus statistics.

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
    api_instance = encypher.CoalitionApi(api_client)
    months = 12 # int |  (optional) (default to 12)

    try:
        # Get Content Stats
        api_response = api_instance.get_content_stats_api_v1_coalition_content_stats_get(months=months)
        print("The response of CoalitionApi->get_content_stats_api_v1_coalition_content_stats_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CoalitionApi->get_content_stats_api_v1_coalition_content_stats_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **months** | **int**|  | [optional] [default to 12]

### Return type

**object**

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

# **get_content_stats_api_v1_coalition_content_stats_get_0**
> object get_content_stats_api_v1_coalition_content_stats_get_0(months=months)

Get Content Stats

Get historical content corpus statistics.

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
    api_instance = encypher.CoalitionApi(api_client)
    months = 12 # int |  (optional) (default to 12)

    try:
        # Get Content Stats
        api_response = api_instance.get_content_stats_api_v1_coalition_content_stats_get_0(months=months)
        print("The response of CoalitionApi->get_content_stats_api_v1_coalition_content_stats_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CoalitionApi->get_content_stats_api_v1_coalition_content_stats_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **months** | **int**|  | [optional] [default to 12]

### Return type

**object**

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

# **get_earnings_history_api_v1_coalition_earnings_get**
> object get_earnings_history_api_v1_coalition_earnings_get(months=months)

Get Earnings History

Get detailed earnings history.

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
    api_instance = encypher.CoalitionApi(api_client)
    months = 12 # int |  (optional) (default to 12)

    try:
        # Get Earnings History
        api_response = api_instance.get_earnings_history_api_v1_coalition_earnings_get(months=months)
        print("The response of CoalitionApi->get_earnings_history_api_v1_coalition_earnings_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CoalitionApi->get_earnings_history_api_v1_coalition_earnings_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **months** | **int**|  | [optional] [default to 12]

### Return type

**object**

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

# **get_earnings_history_api_v1_coalition_earnings_get_0**
> object get_earnings_history_api_v1_coalition_earnings_get_0(months=months)

Get Earnings History

Get detailed earnings history.

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
    api_instance = encypher.CoalitionApi(api_client)
    months = 12 # int |  (optional) (default to 12)

    try:
        # Get Earnings History
        api_response = api_instance.get_earnings_history_api_v1_coalition_earnings_get_0(months=months)
        print("The response of CoalitionApi->get_earnings_history_api_v1_coalition_earnings_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CoalitionApi->get_earnings_history_api_v1_coalition_earnings_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **months** | **int**|  | [optional] [default to 12]

### Return type

**object**

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

# **get_public_coalition_stats_api_v1_coalition_public_stats_get**
> Dict[str, object] get_public_coalition_stats_api_v1_coalition_public_stats_get()

Public coalition aggregate statistics

Returns aggregate-only coalition statistics for public display. No authentication required. Individual member data is never exposed. Used by the marketing site to show coalition scale.

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
    api_instance = encypher.CoalitionApi(api_client)

    try:
        # Public coalition aggregate statistics
        api_response = api_instance.get_public_coalition_stats_api_v1_coalition_public_stats_get()
        print("The response of CoalitionApi->get_public_coalition_stats_api_v1_coalition_public_stats_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CoalitionApi->get_public_coalition_stats_api_v1_coalition_public_stats_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_public_coalition_stats_api_v1_coalition_public_stats_get_0**
> Dict[str, object] get_public_coalition_stats_api_v1_coalition_public_stats_get_0()

Public coalition aggregate statistics

Returns aggregate-only coalition statistics for public display. No authentication required. Individual member data is never exposed. Used by the marketing site to show coalition scale.

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
    api_instance = encypher.CoalitionApi(api_client)

    try:
        # Public coalition aggregate statistics
        api_response = api_instance.get_public_coalition_stats_api_v1_coalition_public_stats_get_0()
        print("The response of CoalitionApi->get_public_coalition_stats_api_v1_coalition_public_stats_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CoalitionApi->get_public_coalition_stats_api_v1_coalition_public_stats_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **opt_in_to_coalition_api_v1_coalition_opt_in_post**
> object opt_in_to_coalition_api_v1_coalition_opt_in_post()

Opt In To Coalition

Opt back into the coalition revenue sharing program.

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
    api_instance = encypher.CoalitionApi(api_client)

    try:
        # Opt In To Coalition
        api_response = api_instance.opt_in_to_coalition_api_v1_coalition_opt_in_post()
        print("The response of CoalitionApi->opt_in_to_coalition_api_v1_coalition_opt_in_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CoalitionApi->opt_in_to_coalition_api_v1_coalition_opt_in_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

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

# **opt_in_to_coalition_api_v1_coalition_opt_in_post_0**
> object opt_in_to_coalition_api_v1_coalition_opt_in_post_0()

Opt In To Coalition

Opt back into the coalition revenue sharing program.

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
    api_instance = encypher.CoalitionApi(api_client)

    try:
        # Opt In To Coalition
        api_response = api_instance.opt_in_to_coalition_api_v1_coalition_opt_in_post_0()
        print("The response of CoalitionApi->opt_in_to_coalition_api_v1_coalition_opt_in_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CoalitionApi->opt_in_to_coalition_api_v1_coalition_opt_in_post_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

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

# **opt_out_of_coalition_api_v1_coalition_opt_out_post**
> object opt_out_of_coalition_api_v1_coalition_opt_out_post()

Opt Out Of Coalition

Opt out of the coalition revenue sharing program.

Note: This will stop future earnings but won't affect pending payouts.

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
    api_instance = encypher.CoalitionApi(api_client)

    try:
        # Opt Out Of Coalition
        api_response = api_instance.opt_out_of_coalition_api_v1_coalition_opt_out_post()
        print("The response of CoalitionApi->opt_out_of_coalition_api_v1_coalition_opt_out_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CoalitionApi->opt_out_of_coalition_api_v1_coalition_opt_out_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

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

# **opt_out_of_coalition_api_v1_coalition_opt_out_post_0**
> object opt_out_of_coalition_api_v1_coalition_opt_out_post_0()

Opt Out Of Coalition

Opt out of the coalition revenue sharing program.

Note: This will stop future earnings but won't affect pending payouts.

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
    api_instance = encypher.CoalitionApi(api_client)

    try:
        # Opt Out Of Coalition
        api_response = api_instance.opt_out_of_coalition_api_v1_coalition_opt_out_post_0()
        print("The response of CoalitionApi->opt_out_of_coalition_api_v1_coalition_opt_out_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CoalitionApi->opt_out_of_coalition_api_v1_coalition_opt_out_post_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

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
