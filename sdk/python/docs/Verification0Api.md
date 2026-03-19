# encypher.VerificationApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_stats_api_v1_verify_stats_get**](VerificationApi.md#get_stats_api_v1_verify_stats_get) | **GET** /api/v1/verify/stats | Get Stats
[**get_verification_history_api_v1_verify_history_document_id_get**](VerificationApi.md#get_verification_history_api_v1_verify_history_document_id_get) | **GET** /api/v1/verify/history/{document_id} | Get Verification History
[**health_check_api_v1_verify_health_get**](VerificationApi.md#health_check_api_v1_verify_health_get) | **GET** /api/v1/verify/health | Health Check
[**verify_by_document_id_api_v1_verify_document_id_get**](VerificationApi.md#verify_by_document_id_api_v1_verify_document_id_get) | **GET** /api/v1/verify/{document_id} | Verify By Document Id
[**verify_document_api_v1_verify_document_post**](VerificationApi.md#verify_document_api_v1_verify_document_post) | **POST** /api/v1/verify/document | [DEPRECATED] Verify a document
[**verify_signature_api_v1_verify_signature_post**](VerificationApi.md#verify_signature_api_v1_verify_signature_post) | **POST** /api/v1/verify/signature | [DEPRECATED] Verify a signature
[**verify_text_api_v1_verify_post**](VerificationApi.md#verify_text_api_v1_verify_post) | **POST** /api/v1/verify | Verify Text


# **get_stats_api_v1_verify_stats_get**
> VerificationStats get_stats_api_v1_verify_stats_get(authorization=authorization)

Get Stats

Get verification statistics

### Example


```python
import encypher
from encypher.models.verification_stats import VerificationStats
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
    api_instance = encypher.VerificationApi(api_client)
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Get Stats
        api_response = api_instance.get_stats_api_v1_verify_stats_get(authorization=authorization)
        print("The response of VerificationApi->get_stats_api_v1_verify_stats_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VerificationApi->get_stats_api_v1_verify_stats_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]

### Return type

[**VerificationStats**](VerificationStats.md)

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

# **get_verification_history_api_v1_verify_history_document_id_get**
> List[VerificationHistory] get_verification_history_api_v1_verify_history_document_id_get(document_id, limit=limit)

Get Verification History

Get verification history for a document (public endpoint)

- **document_id**: Document ID
- **limit**: Maximum number of results

### Example


```python
import encypher
from encypher.models.verification_history import VerificationHistory
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
    api_instance = encypher.VerificationApi(api_client)
    document_id = 'document_id_example' # str |
    limit = 100 # int |  (optional) (default to 100)

    try:
        # Get Verification History
        api_response = api_instance.get_verification_history_api_v1_verify_history_document_id_get(document_id, limit=limit)
        print("The response of VerificationApi->get_verification_history_api_v1_verify_history_document_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VerificationApi->get_verification_history_api_v1_verify_history_document_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  |
 **limit** | **int**|  | [optional] [default to 100]

### Return type

[**List[VerificationHistory]**](VerificationHistory.md)

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

# **health_check_api_v1_verify_health_get**
> object health_check_api_v1_verify_health_get()

Health Check

Health check endpoint

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
    api_instance = encypher.VerificationApi(api_client)

    try:
        # Health Check
        api_response = api_instance.health_check_api_v1_verify_health_get()
        print("The response of VerificationApi->health_check_api_v1_verify_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VerificationApi->health_check_api_v1_verify_health_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **verify_by_document_id_api_v1_verify_document_id_get**
> object verify_by_document_id_api_v1_verify_document_id_get(document_id)

Verify By Document Id

Verify a document by its ID (for clickable verification links).

Returns HTML or JSON depending on the Accept header.

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
    api_instance = encypher.VerificationApi(api_client)
    document_id = 'document_id_example' # str |

    try:
        # Verify By Document Id
        api_response = api_instance.verify_by_document_id_api_v1_verify_document_id_get(document_id)
        print("The response of VerificationApi->verify_by_document_id_api_v1_verify_document_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VerificationApi->verify_by_document_id_api_v1_verify_document_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  |

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

# **verify_document_api_v1_verify_document_post**
> VerificationResponse verify_document_api_v1_verify_document_post(document_verify, x_forwarded_for=x_forwarded_for, user_agent=user_agent, authorization=authorization)

[DEPRECATED] Verify a document

**Deprecated.** Use `POST /api/v1/verify` instead. This endpoint will be removed in a future release.

### Example


```python
import encypher
from encypher.models.document_verify import DocumentVerify
from encypher.models.verification_response import VerificationResponse
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
    api_instance = encypher.VerificationApi(api_client)
    document_verify = encypher.DocumentVerify() # DocumentVerify |
    x_forwarded_for = 'x_forwarded_for_example' # str |  (optional)
    user_agent = 'user_agent_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)

    try:
        # [DEPRECATED] Verify a document
        api_response = api_instance.verify_document_api_v1_verify_document_post(document_verify, x_forwarded_for=x_forwarded_for, user_agent=user_agent, authorization=authorization)
        print("The response of VerificationApi->verify_document_api_v1_verify_document_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VerificationApi->verify_document_api_v1_verify_document_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_verify** | [**DocumentVerify**](DocumentVerify.md)|  |
 **x_forwarded_for** | **str**|  | [optional]
 **user_agent** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]

### Return type

[**VerificationResponse**](VerificationResponse.md)

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

# **verify_signature_api_v1_verify_signature_post**
> VerificationResponse verify_signature_api_v1_verify_signature_post(signature_verify, x_forwarded_for=x_forwarded_for, user_agent=user_agent, authorization=authorization)

[DEPRECATED] Verify a signature

**Deprecated.** Use `POST /api/v1/verify` instead. This endpoint will be removed in a future release.

### Example


```python
import encypher
from encypher.models.signature_verify import SignatureVerify
from encypher.models.verification_response import VerificationResponse
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
    api_instance = encypher.VerificationApi(api_client)
    signature_verify = encypher.SignatureVerify() # SignatureVerify |
    x_forwarded_for = 'x_forwarded_for_example' # str |  (optional)
    user_agent = 'user_agent_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)

    try:
        # [DEPRECATED] Verify a signature
        api_response = api_instance.verify_signature_api_v1_verify_signature_post(signature_verify, x_forwarded_for=x_forwarded_for, user_agent=user_agent, authorization=authorization)
        print("The response of VerificationApi->verify_signature_api_v1_verify_signature_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VerificationApi->verify_signature_api_v1_verify_signature_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **signature_verify** | [**SignatureVerify**](SignatureVerify.md)|  |
 **x_forwarded_for** | **str**|  | [optional]
 **user_agent** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]

### Return type

[**VerificationResponse**](VerificationResponse.md)

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

# **verify_text_api_v1_verify_post**
> VerifyResponse verify_text_api_v1_verify_post(verify_request, authorization=authorization)

Verify Text

Verify signed content and return a structured verdict.

### Example


```python
import encypher
from encypher.models.verify_request import VerifyRequest
from encypher.models.verify_response import VerifyResponse
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
    api_instance = encypher.VerificationApi(api_client)
    verify_request = encypher.VerifyRequest() # VerifyRequest |
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Verify Text
        api_response = api_instance.verify_text_api_v1_verify_post(verify_request, authorization=authorization)
        print("The response of VerificationApi->verify_text_api_v1_verify_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VerificationApi->verify_text_api_v1_verify_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verify_request** | [**VerifyRequest**](VerifyRequest.md)|  |
 **authorization** | **str**|  | [optional]

### Return type

[**VerifyResponse**](VerifyResponse.md)

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
