# encypher.PublicToolsApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**decode_text_api_v1_tools_decode_post**](PublicToolsApi.md#decode_text_api_v1_tools_decode_post) | **POST** /api/v1/tools/decode | Decode Text
[**decode_text_api_v1_tools_decode_post_0**](PublicToolsApi.md#decode_text_api_v1_tools_decode_post_0) | **POST** /api/v1/tools/decode | Decode Text
[**encode_text_api_v1_tools_encode_post**](PublicToolsApi.md#encode_text_api_v1_tools_encode_post) | **POST** /api/v1/tools/encode | Encode Text
[**encode_text_api_v1_tools_encode_post_0**](PublicToolsApi.md#encode_text_api_v1_tools_encode_post_0) | **POST** /api/v1/tools/encode | Encode Text


# **decode_text_api_v1_tools_decode_post**
> DecodeToolResponse decode_text_api_v1_tools_decode_post(decode_tool_request)

Decode Text

Decode and verify text containing embedded metadata.

This is a public endpoint for the website demo tool.
Supports multiple embeddings in a single text (Encypher proprietary feature).
Verification uses Trust Anchor lookup - checks database for org public keys.
Falls back to demo key for demo-signed content.

### Example


```python
import encypher
from encypher.models.decode_tool_request import DecodeToolRequest
from encypher.models.decode_tool_response import DecodeToolResponse
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
    api_instance = encypher.PublicToolsApi(api_client)
    decode_tool_request = encypher.DecodeToolRequest() # DecodeToolRequest | 

    try:
        # Decode Text
        api_response = api_instance.decode_text_api_v1_tools_decode_post(decode_tool_request)
        print("The response of PublicToolsApi->decode_text_api_v1_tools_decode_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicToolsApi->decode_text_api_v1_tools_decode_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **decode_tool_request** | [**DecodeToolRequest**](DecodeToolRequest.md)|  | 

### Return type

[**DecodeToolResponse**](DecodeToolResponse.md)

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

# **decode_text_api_v1_tools_decode_post_0**
> DecodeToolResponse decode_text_api_v1_tools_decode_post_0(decode_tool_request)

Decode Text

Decode and verify text containing embedded metadata.

This is a public endpoint for the website demo tool.
Supports multiple embeddings in a single text (Encypher proprietary feature).
Verification uses Trust Anchor lookup - checks database for org public keys.
Falls back to demo key for demo-signed content.

### Example


```python
import encypher
from encypher.models.decode_tool_request import DecodeToolRequest
from encypher.models.decode_tool_response import DecodeToolResponse
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
    api_instance = encypher.PublicToolsApi(api_client)
    decode_tool_request = encypher.DecodeToolRequest() # DecodeToolRequest | 

    try:
        # Decode Text
        api_response = api_instance.decode_text_api_v1_tools_decode_post_0(decode_tool_request)
        print("The response of PublicToolsApi->decode_text_api_v1_tools_decode_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicToolsApi->decode_text_api_v1_tools_decode_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **decode_tool_request** | [**DecodeToolRequest**](DecodeToolRequest.md)|  | 

### Return type

[**DecodeToolResponse**](DecodeToolResponse.md)

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

# **encode_text_api_v1_tools_encode_post**
> EncodeToolResponse encode_text_api_v1_tools_encode_post(encode_tool_request)

Encode Text

Encode text with embedded metadata using the demo key.

This is a public endpoint for the website demo tool.
All encoding uses a server-side demo key.

### Example


```python
import encypher
from encypher.models.encode_tool_request import EncodeToolRequest
from encypher.models.encode_tool_response import EncodeToolResponse
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
    api_instance = encypher.PublicToolsApi(api_client)
    encode_tool_request = encypher.EncodeToolRequest() # EncodeToolRequest | 

    try:
        # Encode Text
        api_response = api_instance.encode_text_api_v1_tools_encode_post(encode_tool_request)
        print("The response of PublicToolsApi->encode_text_api_v1_tools_encode_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicToolsApi->encode_text_api_v1_tools_encode_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **encode_tool_request** | [**EncodeToolRequest**](EncodeToolRequest.md)|  | 

### Return type

[**EncodeToolResponse**](EncodeToolResponse.md)

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

# **encode_text_api_v1_tools_encode_post_0**
> EncodeToolResponse encode_text_api_v1_tools_encode_post_0(encode_tool_request)

Encode Text

Encode text with embedded metadata using the demo key.

This is a public endpoint for the website demo tool.
All encoding uses a server-side demo key.

### Example


```python
import encypher
from encypher.models.encode_tool_request import EncodeToolRequest
from encypher.models.encode_tool_response import EncodeToolResponse
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
    api_instance = encypher.PublicToolsApi(api_client)
    encode_tool_request = encypher.EncodeToolRequest() # EncodeToolRequest | 

    try:
        # Encode Text
        api_response = api_instance.encode_text_api_v1_tools_encode_post_0(encode_tool_request)
        print("The response of PublicToolsApi->encode_text_api_v1_tools_encode_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicToolsApi->encode_text_api_v1_tools_encode_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **encode_tool_request** | [**EncodeToolRequest**](EncodeToolRequest.md)|  | 

### Return type

[**EncodeToolResponse**](EncodeToolResponse.md)

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

