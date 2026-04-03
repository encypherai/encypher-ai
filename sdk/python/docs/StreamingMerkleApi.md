# encypher.StreamingMerkleApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_segment_to_session_api_v1_enterprise_stream_merkle_segment_post**](StreamingMerkleApi.md#add_segment_to_session_api_v1_enterprise_stream_merkle_segment_post) | **POST** /api/v1/enterprise/stream/merkle/segment | Add Segment To Session
[**finalize_streaming_session_api_v1_enterprise_stream_merkle_finalize_post**](StreamingMerkleApi.md#finalize_streaming_session_api_v1_enterprise_stream_merkle_finalize_post) | **POST** /api/v1/enterprise/stream/merkle/finalize | Finalize Streaming Session
[**get_session_status_api_v1_enterprise_stream_merkle_status_post**](StreamingMerkleApi.md#get_session_status_api_v1_enterprise_stream_merkle_status_post) | **POST** /api/v1/enterprise/stream/merkle/status | Get Session Status
[**start_streaming_merkle_session_api_v1_enterprise_stream_merkle_start_post**](StreamingMerkleApi.md#start_streaming_merkle_session_api_v1_enterprise_stream_merkle_start_post) | **POST** /api/v1/enterprise/stream/merkle/start | Start Streaming Merkle Session


# **add_segment_to_session_api_v1_enterprise_stream_merkle_segment_post**
> StreamMerkleSegmentResponse add_segment_to_session_api_v1_enterprise_stream_merkle_segment_post(stream_merkle_segment_request)

Add Segment To Session

Add a segment to an active streaming Merkle session.

Segments are buffered and combined into the Merkle tree incrementally.
The tree is constructed using a bounded buffer approach for memory efficiency.

Set `is_final=true` to finalize the session after adding this segment.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.stream_merkle_segment_request import StreamMerkleSegmentRequest
from encypher.models.stream_merkle_segment_response import StreamMerkleSegmentResponse
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
    api_instance = encypher.StreamingMerkleApi(api_client)
    stream_merkle_segment_request = encypher.StreamMerkleSegmentRequest() # StreamMerkleSegmentRequest |

    try:
        # Add Segment To Session
        api_response = api_instance.add_segment_to_session_api_v1_enterprise_stream_merkle_segment_post(stream_merkle_segment_request)
        print("The response of StreamingMerkleApi->add_segment_to_session_api_v1_enterprise_stream_merkle_segment_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StreamingMerkleApi->add_segment_to_session_api_v1_enterprise_stream_merkle_segment_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stream_merkle_segment_request** | [**StreamMerkleSegmentRequest**](StreamMerkleSegmentRequest.md)|  |

### Return type

[**StreamMerkleSegmentResponse**](StreamMerkleSegmentResponse.md)

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

# **finalize_streaming_session_api_v1_enterprise_stream_merkle_finalize_post**
> StreamMerkleFinalizeResponse finalize_streaming_session_api_v1_enterprise_stream_merkle_finalize_post(stream_merkle_finalize_request)

Finalize Streaming Session

Finalize a streaming Merkle session and compute the final root.

This completes the tree construction, computes the final root hash,
and optionally embeds a C2PA manifest into the full document.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.stream_merkle_finalize_request import StreamMerkleFinalizeRequest
from encypher.models.stream_merkle_finalize_response import StreamMerkleFinalizeResponse
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
    api_instance = encypher.StreamingMerkleApi(api_client)
    stream_merkle_finalize_request = encypher.StreamMerkleFinalizeRequest() # StreamMerkleFinalizeRequest |

    try:
        # Finalize Streaming Session
        api_response = api_instance.finalize_streaming_session_api_v1_enterprise_stream_merkle_finalize_post(stream_merkle_finalize_request)
        print("The response of StreamingMerkleApi->finalize_streaming_session_api_v1_enterprise_stream_merkle_finalize_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StreamingMerkleApi->finalize_streaming_session_api_v1_enterprise_stream_merkle_finalize_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stream_merkle_finalize_request** | [**StreamMerkleFinalizeRequest**](StreamMerkleFinalizeRequest.md)|  |

### Return type

[**StreamMerkleFinalizeResponse**](StreamMerkleFinalizeResponse.md)

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

# **get_session_status_api_v1_enterprise_stream_merkle_status_post**
> StreamMerkleStatusResponse get_session_status_api_v1_enterprise_stream_merkle_status_post(stream_merkle_status_request)

Get Session Status

Check the status of a streaming Merkle session.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.stream_merkle_status_request import StreamMerkleStatusRequest
from encypher.models.stream_merkle_status_response import StreamMerkleStatusResponse
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
    api_instance = encypher.StreamingMerkleApi(api_client)
    stream_merkle_status_request = encypher.StreamMerkleStatusRequest() # StreamMerkleStatusRequest |

    try:
        # Get Session Status
        api_response = api_instance.get_session_status_api_v1_enterprise_stream_merkle_status_post(stream_merkle_status_request)
        print("The response of StreamingMerkleApi->get_session_status_api_v1_enterprise_stream_merkle_status_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StreamingMerkleApi->get_session_status_api_v1_enterprise_stream_merkle_status_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stream_merkle_status_request** | [**StreamMerkleStatusRequest**](StreamMerkleStatusRequest.md)|  |

### Return type

[**StreamMerkleStatusResponse**](StreamMerkleStatusResponse.md)

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

# **start_streaming_merkle_session_api_v1_enterprise_stream_merkle_start_post**
> StreamMerkleStartResponse start_streaming_merkle_session_api_v1_enterprise_stream_merkle_start_post(stream_merkle_start_request)

Start Streaming Merkle Session

Start a new streaming Merkle tree construction session.

This initiates a session that allows segments to be added incrementally,
ideal for real-time LLM output signing where content is generated token-by-token.

**Tier Requirement:** Professional+

Patent Reference: FIG. 5 - Streaming Merkle Tree Construction

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.stream_merkle_start_request import StreamMerkleStartRequest
from encypher.models.stream_merkle_start_response import StreamMerkleStartResponse
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
    api_instance = encypher.StreamingMerkleApi(api_client)
    stream_merkle_start_request = encypher.StreamMerkleStartRequest() # StreamMerkleStartRequest |

    try:
        # Start Streaming Merkle Session
        api_response = api_instance.start_streaming_merkle_session_api_v1_enterprise_stream_merkle_start_post(stream_merkle_start_request)
        print("The response of StreamingMerkleApi->start_streaming_merkle_session_api_v1_enterprise_stream_merkle_start_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StreamingMerkleApi->start_streaming_merkle_session_api_v1_enterprise_stream_merkle_start_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stream_merkle_start_request** | [**StreamMerkleStartRequest**](StreamMerkleStartRequest.md)|  |

### Return type

[**StreamMerkleStartResponse**](StreamMerkleStartResponse.md)

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
