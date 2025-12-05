# encypher.AuditApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**export_audit_logs_api_v1_audit_logs_export_get**](AuditApi.md#export_audit_logs_api_v1_audit_logs_export_get) | **GET** /api/v1/audit-logs/export | Export Audit Logs
[**get_audit_logs_api_v1_audit_logs_get**](AuditApi.md#get_audit_logs_api_v1_audit_logs_get) | **GET** /api/v1/audit-logs | Get Audit Logs


# **export_audit_logs_api_v1_audit_logs_export_get**
> object export_audit_logs_api_v1_audit_logs_export_get(format=format, start_date=start_date, end_date=end_date)

Export Audit Logs

Export audit logs in JSON or CSV format.

Returns all logs within the specified date range.
Default is last 30 days if no dates specified.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
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
    api_instance = encypher.AuditApi(api_client)
    format = 'json' # str |  (optional) (default to 'json')
    start_date = 'start_date_example' # str |  (optional)
    end_date = 'end_date_example' # str |  (optional)

    try:
        # Export Audit Logs
        api_response = api_instance.export_audit_logs_api_v1_audit_logs_export_get(format=format, start_date=start_date, end_date=end_date)
        print("The response of AuditApi->export_audit_logs_api_v1_audit_logs_export_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->export_audit_logs_api_v1_audit_logs_export_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **format** | **str**|  | [optional] [default to &#39;json&#39;]
 **start_date** | **str**|  | [optional] 
 **end_date** | **str**|  | [optional] 

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

# **get_audit_logs_api_v1_audit_logs_get**
> AuditLogResponse get_audit_logs_api_v1_audit_logs_get(page=page, page_size=page_size, action=action, actor_id=actor_id, resource_type=resource_type, start_date=start_date, end_date=end_date)

Get Audit Logs

Get audit logs for the organization.

Supports filtering by:
- action: Type of action (e.g., "document.signed")
- actor_id: ID of the user or API key that performed the action
- resource_type: Type of resource affected
- start_date/end_date: Date range

Results are paginated and sorted by timestamp (newest first).

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.audit_log_response import AuditLogResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
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
    api_instance = encypher.AuditApi(api_client)
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    action = 'action_example' # str | Filter by action type (optional)
    actor_id = 'actor_id_example' # str | Filter by actor ID (optional)
    resource_type = 'resource_type_example' # str | Filter by resource type (optional)
    start_date = 'start_date_example' # str | Start date (ISO format) (optional)
    end_date = 'end_date_example' # str | End date (ISO format) (optional)

    try:
        # Get Audit Logs
        api_response = api_instance.get_audit_logs_api_v1_audit_logs_get(page=page, page_size=page_size, action=action, actor_id=actor_id, resource_type=resource_type, start_date=start_date, end_date=end_date)
        print("The response of AuditApi->get_audit_logs_api_v1_audit_logs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->get_audit_logs_api_v1_audit_logs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]
 **action** | **str**| Filter by action type | [optional] 
 **actor_id** | **str**| Filter by actor ID | [optional] 
 **resource_type** | **str**| Filter by resource type | [optional] 
 **start_date** | **str**| Start date (ISO format) | [optional] 
 **end_date** | **str**| End date (ISO format) | [optional] 

### Return type

[**AuditLogResponse**](AuditLogResponse.md)

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

