# encypher.PartnerPortalApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_partner_aggregate_api_v1_partner_portal_aggregate_get**](PartnerPortalApi.md#get_partner_aggregate_api_v1_partner_portal_aggregate_get) | **GET** /api/v1/partner/portal/aggregate | Get Partner Aggregate
[**get_partner_aggregate_api_v1_partner_portal_aggregate_get_0**](PartnerPortalApi.md#get_partner_aggregate_api_v1_partner_portal_aggregate_get_0) | **GET** /api/v1/partner/portal/aggregate | Get Partner Aggregate
[**get_partner_publisher_detail_api_v1_partner_portal_publishers_pub_org_id_get**](PartnerPortalApi.md#get_partner_publisher_detail_api_v1_partner_portal_publishers_pub_org_id_get) | **GET** /api/v1/partner/portal/publishers/{pub_org_id} | Get Partner Publisher Detail
[**get_partner_publisher_detail_api_v1_partner_portal_publishers_pub_org_id_get_0**](PartnerPortalApi.md#get_partner_publisher_detail_api_v1_partner_portal_publishers_pub_org_id_get_0) | **GET** /api/v1/partner/portal/publishers/{pub_org_id} | Get Partner Publisher Detail
[**list_partner_publishers_api_v1_partner_portal_publishers_get**](PartnerPortalApi.md#list_partner_publishers_api_v1_partner_portal_publishers_get) | **GET** /api/v1/partner/portal/publishers | List Partner Publishers
[**list_partner_publishers_api_v1_partner_portal_publishers_get_0**](PartnerPortalApi.md#list_partner_publishers_api_v1_partner_portal_publishers_get_0) | **GET** /api/v1/partner/portal/publishers | List Partner Publishers


# **get_partner_aggregate_api_v1_partner_portal_aggregate_get**
> Dict[str, object] get_partner_aggregate_api_v1_partner_portal_aggregate_get()

Get Partner Aggregate

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
    api_instance = encypher.PartnerPortalApi(api_client)

    try:
        # Get Partner Aggregate
        api_response = api_instance.get_partner_aggregate_api_v1_partner_portal_aggregate_get()
        print("The response of PartnerPortalApi->get_partner_aggregate_api_v1_partner_portal_aggregate_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartnerPortalApi->get_partner_aggregate_api_v1_partner_portal_aggregate_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_partner_aggregate_api_v1_partner_portal_aggregate_get_0**
> Dict[str, object] get_partner_aggregate_api_v1_partner_portal_aggregate_get_0()

Get Partner Aggregate

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
    api_instance = encypher.PartnerPortalApi(api_client)

    try:
        # Get Partner Aggregate
        api_response = api_instance.get_partner_aggregate_api_v1_partner_portal_aggregate_get_0()
        print("The response of PartnerPortalApi->get_partner_aggregate_api_v1_partner_portal_aggregate_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartnerPortalApi->get_partner_aggregate_api_v1_partner_portal_aggregate_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_partner_publisher_detail_api_v1_partner_portal_publishers_pub_org_id_get**
> Dict[str, object] get_partner_publisher_detail_api_v1_partner_portal_publishers_pub_org_id_get(pub_org_id)

Get Partner Publisher Detail

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
    api_instance = encypher.PartnerPortalApi(api_client)
    pub_org_id = 'pub_org_id_example' # str |

    try:
        # Get Partner Publisher Detail
        api_response = api_instance.get_partner_publisher_detail_api_v1_partner_portal_publishers_pub_org_id_get(pub_org_id)
        print("The response of PartnerPortalApi->get_partner_publisher_detail_api_v1_partner_portal_publishers_pub_org_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartnerPortalApi->get_partner_publisher_detail_api_v1_partner_portal_publishers_pub_org_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **pub_org_id** | **str**|  |

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

# **get_partner_publisher_detail_api_v1_partner_portal_publishers_pub_org_id_get_0**
> Dict[str, object] get_partner_publisher_detail_api_v1_partner_portal_publishers_pub_org_id_get_0(pub_org_id)

Get Partner Publisher Detail

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
    api_instance = encypher.PartnerPortalApi(api_client)
    pub_org_id = 'pub_org_id_example' # str |

    try:
        # Get Partner Publisher Detail
        api_response = api_instance.get_partner_publisher_detail_api_v1_partner_portal_publishers_pub_org_id_get_0(pub_org_id)
        print("The response of PartnerPortalApi->get_partner_publisher_detail_api_v1_partner_portal_publishers_pub_org_id_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartnerPortalApi->get_partner_publisher_detail_api_v1_partner_portal_publishers_pub_org_id_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **pub_org_id** | **str**|  |

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

# **list_partner_publishers_api_v1_partner_portal_publishers_get**
> Dict[str, object] list_partner_publishers_api_v1_partner_portal_publishers_get()

List Partner Publishers

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
    api_instance = encypher.PartnerPortalApi(api_client)

    try:
        # List Partner Publishers
        api_response = api_instance.list_partner_publishers_api_v1_partner_portal_publishers_get()
        print("The response of PartnerPortalApi->list_partner_publishers_api_v1_partner_portal_publishers_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartnerPortalApi->list_partner_publishers_api_v1_partner_portal_publishers_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_partner_publishers_api_v1_partner_portal_publishers_get_0**
> Dict[str, object] list_partner_publishers_api_v1_partner_portal_publishers_get_0()

List Partner Publishers

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
    api_instance = encypher.PartnerPortalApi(api_client)

    try:
        # List Partner Publishers
        api_response = api_instance.list_partner_publishers_api_v1_partner_portal_publishers_get_0()
        print("The response of PartnerPortalApi->list_partner_publishers_api_v1_partner_portal_publishers_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartnerPortalApi->list_partner_publishers_api_v1_partner_portal_publishers_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
