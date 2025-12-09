# encypher.VerificationApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**verify_by_document_id_api_v1_verify_document_id_get**](VerificationApi.md#verify_by_document_id_api_v1_verify_document_id_get) | **GET** /api/v1/verify/{document_id} | Verify By Document Id
[**verify_content_api_v1_verify_post**](VerificationApi.md#verify_content_api_v1_verify_post) | **POST** /api/v1/verify | Verify Content


# **verify_by_document_id_api_v1_verify_document_id_get**
> object verify_by_document_id_api_v1_verify_document_id_get(document_id)

Verify By Document Id

Verify a document by its ID (for clickable verification links).

Returns an HTML page so users can preview verification state in a browser.

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
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

# **verify_content_api_v1_verify_post**
> VerifyResponse verify_content_api_v1_verify_post(verify_request)

Verify Content

Verify C2PA manifest in signed content using the encypher-ai library.

This endpoint is public, rate limited, and returns structured machine-friendly
verdicts that SDKs consume.

### Example


```python
import encypher
from encypher.models.verify_request import VerifyRequest
from encypher.models.verify_response import VerifyResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.VerificationApi(api_client)
    verify_request = encypher.VerifyRequest() # VerifyRequest | 

    try:
        # Verify Content
        api_response = api_instance.verify_content_api_v1_verify_post(verify_request)
        print("The response of VerificationApi->verify_content_api_v1_verify_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VerificationApi->verify_content_api_v1_verify_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verify_request** | [**VerifyRequest**](VerifyRequest.md)|  | 

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

