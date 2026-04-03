# encypher.CDNAnalyticsApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_analytics_summary_api_v1_cdn_analytics_summary_get**](CDNAnalyticsApi.md#get_analytics_summary_api_v1_cdn_analytics_summary_get) | **GET** /api/v1/cdn/analytics/summary | CDN provenance analytics summary
[**get_analytics_summary_api_v1_cdn_analytics_summary_get_0**](CDNAnalyticsApi.md#get_analytics_summary_api_v1_cdn_analytics_summary_get_0) | **GET** /api/v1/cdn/analytics/summary | CDN provenance analytics summary
[**get_analytics_timeline_api_v1_cdn_analytics_timeline_get**](CDNAnalyticsApi.md#get_analytics_timeline_api_v1_cdn_analytics_timeline_get) | **GET** /api/v1/cdn/analytics/timeline | CDN provenance analytics day-by-day timeline
[**get_analytics_timeline_api_v1_cdn_analytics_timeline_get_0**](CDNAnalyticsApi.md#get_analytics_timeline_api_v1_cdn_analytics_timeline_get_0) | **GET** /api/v1/cdn/analytics/timeline | CDN provenance analytics day-by-day timeline


# **get_analytics_summary_api_v1_cdn_analytics_summary_get**
> CdnAnalyticsSummary get_analytics_summary_api_v1_cdn_analytics_summary_get()

CDN provenance analytics summary

Return per-org dashboard metrics for image provenance protection.

Returns counts of protected assets, registered variants, and tracked image
requests, plus a recoverable percentage.

**Requires authentication.**

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_analytics_summary import CdnAnalyticsSummary
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
    api_instance = encypher.CDNAnalyticsApi(api_client)

    try:
        # CDN provenance analytics summary
        api_response = api_instance.get_analytics_summary_api_v1_cdn_analytics_summary_get()
        print("The response of CDNAnalyticsApi->get_analytics_summary_api_v1_cdn_analytics_summary_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNAnalyticsApi->get_analytics_summary_api_v1_cdn_analytics_summary_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**CdnAnalyticsSummary**](CdnAnalyticsSummary.md)

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

# **get_analytics_summary_api_v1_cdn_analytics_summary_get_0**
> CdnAnalyticsSummary get_analytics_summary_api_v1_cdn_analytics_summary_get_0()

CDN provenance analytics summary

Return per-org dashboard metrics for image provenance protection.

Returns counts of protected assets, registered variants, and tracked image
requests, plus a recoverable percentage.

**Requires authentication.**

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_analytics_summary import CdnAnalyticsSummary
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
    api_instance = encypher.CDNAnalyticsApi(api_client)

    try:
        # CDN provenance analytics summary
        api_response = api_instance.get_analytics_summary_api_v1_cdn_analytics_summary_get_0()
        print("The response of CDNAnalyticsApi->get_analytics_summary_api_v1_cdn_analytics_summary_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNAnalyticsApi->get_analytics_summary_api_v1_cdn_analytics_summary_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**CdnAnalyticsSummary**](CdnAnalyticsSummary.md)

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

# **get_analytics_timeline_api_v1_cdn_analytics_timeline_get**
> CdnAnalyticsTimeline get_analytics_timeline_api_v1_cdn_analytics_timeline_get(days=days)

CDN provenance analytics day-by-day timeline

Return day-by-day counts of images signed and attribution events tracked
over the past N days (default 30).

**Requires authentication.**

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_analytics_timeline import CdnAnalyticsTimeline
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
    api_instance = encypher.CDNAnalyticsApi(api_client)
    days = 30 # int | Number of days to include (optional) (default to 30)

    try:
        # CDN provenance analytics day-by-day timeline
        api_response = api_instance.get_analytics_timeline_api_v1_cdn_analytics_timeline_get(days=days)
        print("The response of CDNAnalyticsApi->get_analytics_timeline_api_v1_cdn_analytics_timeline_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNAnalyticsApi->get_analytics_timeline_api_v1_cdn_analytics_timeline_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **days** | **int**| Number of days to include | [optional] [default to 30]

### Return type

[**CdnAnalyticsTimeline**](CdnAnalyticsTimeline.md)

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

# **get_analytics_timeline_api_v1_cdn_analytics_timeline_get_0**
> CdnAnalyticsTimeline get_analytics_timeline_api_v1_cdn_analytics_timeline_get_0(days=days)

CDN provenance analytics day-by-day timeline

Return day-by-day counts of images signed and attribution events tracked
over the past N days (default 30).

**Requires authentication.**

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.cdn_analytics_timeline import CdnAnalyticsTimeline
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
    api_instance = encypher.CDNAnalyticsApi(api_client)
    days = 30 # int | Number of days to include (optional) (default to 30)

    try:
        # CDN provenance analytics day-by-day timeline
        api_response = api_instance.get_analytics_timeline_api_v1_cdn_analytics_timeline_get_0(days=days)
        print("The response of CDNAnalyticsApi->get_analytics_timeline_api_v1_cdn_analytics_timeline_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CDNAnalyticsApi->get_analytics_timeline_api_v1_cdn_analytics_timeline_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **days** | **int**| Number of days to include | [optional] [default to 30]

### Return type

[**CdnAnalyticsTimeline**](CdnAnalyticsTimeline.md)

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
