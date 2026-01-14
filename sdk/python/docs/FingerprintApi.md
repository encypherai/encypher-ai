# encypher.FingerprintApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**detect_fingerprint_api_v1_enterprise_fingerprint_detect_post**](FingerprintApi.md#detect_fingerprint_api_v1_enterprise_fingerprint_detect_post) | **POST** /api/v1/enterprise/fingerprint/detect | Detect Fingerprint
[**encode_fingerprint_api_v1_enterprise_fingerprint_encode_post**](FingerprintApi.md#encode_fingerprint_api_v1_enterprise_fingerprint_encode_post) | **POST** /api/v1/enterprise/fingerprint/encode | Encode Fingerprint


# **detect_fingerprint_api_v1_enterprise_fingerprint_detect_post**
> FingerprintDetectResponse detect_fingerprint_api_v1_enterprise_fingerprint_detect_post(fingerprint_detect_request)

Detect Fingerprint

Detect a fingerprint in text.

Detection uses score-based matching with confidence threshold
to identify fingerprinted content even after modifications.

**Tier Requirement:** Enterprise

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.fingerprint_detect_request import FingerprintDetectRequest
from encypher.models.fingerprint_detect_response import FingerprintDetectResponse
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
    api_instance = encypher.FingerprintApi(api_client)
    fingerprint_detect_request = encypher.FingerprintDetectRequest() # FingerprintDetectRequest | 

    try:
        # Detect Fingerprint
        api_response = api_instance.detect_fingerprint_api_v1_enterprise_fingerprint_detect_post(fingerprint_detect_request)
        print("The response of FingerprintApi->detect_fingerprint_api_v1_enterprise_fingerprint_detect_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FingerprintApi->detect_fingerprint_api_v1_enterprise_fingerprint_detect_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **fingerprint_detect_request** | [**FingerprintDetectRequest**](FingerprintDetectRequest.md)|  | 

### Return type

[**FingerprintDetectResponse**](FingerprintDetectResponse.md)

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

# **encode_fingerprint_api_v1_enterprise_fingerprint_encode_post**
> FingerprintEncodeResponse encode_fingerprint_api_v1_enterprise_fingerprint_encode_post(fingerprint_encode_request)

Encode Fingerprint

Encode a robust fingerprint into text.

Fingerprints use secret-seeded placement of invisible markers
that survive text modifications like paraphrasing or truncation.

**Tier Requirement:** Enterprise

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.fingerprint_encode_request import FingerprintEncodeRequest
from encypher.models.fingerprint_encode_response import FingerprintEncodeResponse
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
    api_instance = encypher.FingerprintApi(api_client)
    fingerprint_encode_request = encypher.FingerprintEncodeRequest() # FingerprintEncodeRequest | 

    try:
        # Encode Fingerprint
        api_response = api_instance.encode_fingerprint_api_v1_enterprise_fingerprint_encode_post(fingerprint_encode_request)
        print("The response of FingerprintApi->encode_fingerprint_api_v1_enterprise_fingerprint_encode_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FingerprintApi->encode_fingerprint_api_v1_enterprise_fingerprint_encode_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **fingerprint_encode_request** | [**FingerprintEncodeRequest**](FingerprintEncodeRequest.md)|  | 

### Return type

[**FingerprintEncodeResponse**](FingerprintEncodeResponse.md)

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

