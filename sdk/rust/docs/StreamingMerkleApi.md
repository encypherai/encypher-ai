# \StreamingMerkleApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_segment_to_session_api_v1_enterprise_stream_merkle_segment_post**](StreamingMerkleApi.md#add_segment_to_session_api_v1_enterprise_stream_merkle_segment_post) | **POST** /api/v1/enterprise/stream/merkle/segment | Add Segment To Session
[**finalize_streaming_session_api_v1_enterprise_stream_merkle_finalize_post**](StreamingMerkleApi.md#finalize_streaming_session_api_v1_enterprise_stream_merkle_finalize_post) | **POST** /api/v1/enterprise/stream/merkle/finalize | Finalize Streaming Session
[**get_session_status_api_v1_enterprise_stream_merkle_status_post**](StreamingMerkleApi.md#get_session_status_api_v1_enterprise_stream_merkle_status_post) | **POST** /api/v1/enterprise/stream/merkle/status | Get Session Status
[**start_streaming_merkle_session_api_v1_enterprise_stream_merkle_start_post**](StreamingMerkleApi.md#start_streaming_merkle_session_api_v1_enterprise_stream_merkle_start_post) | **POST** /api/v1/enterprise/stream/merkle/start | Start Streaming Merkle Session



## add_segment_to_session_api_v1_enterprise_stream_merkle_segment_post

> models::StreamMerkleSegmentResponse add_segment_to_session_api_v1_enterprise_stream_merkle_segment_post(stream_merkle_segment_request)
Add Segment To Session

Add a segment to an active streaming Merkle session.  Segments are buffered and combined into the Merkle tree incrementally. The tree is constructed using a bounded buffer approach for memory efficiency.  Set `is_final=true` to finalize the session after adding this segment.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**stream_merkle_segment_request** | [**StreamMerkleSegmentRequest**](StreamMerkleSegmentRequest.md) |  | [required] |

### Return type

[**models::StreamMerkleSegmentResponse**](StreamMerkleSegmentResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## finalize_streaming_session_api_v1_enterprise_stream_merkle_finalize_post

> models::StreamMerkleFinalizeResponse finalize_streaming_session_api_v1_enterprise_stream_merkle_finalize_post(stream_merkle_finalize_request)
Finalize Streaming Session

Finalize a streaming Merkle session and compute the final root.  This completes the tree construction, computes the final root hash, and optionally embeds a C2PA manifest into the full document.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**stream_merkle_finalize_request** | [**StreamMerkleFinalizeRequest**](StreamMerkleFinalizeRequest.md) |  | [required] |

### Return type

[**models::StreamMerkleFinalizeResponse**](StreamMerkleFinalizeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_session_status_api_v1_enterprise_stream_merkle_status_post

> models::StreamMerkleStatusResponse get_session_status_api_v1_enterprise_stream_merkle_status_post(stream_merkle_status_request)
Get Session Status

Check the status of a streaming Merkle session.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**stream_merkle_status_request** | [**StreamMerkleStatusRequest**](StreamMerkleStatusRequest.md) |  | [required] |

### Return type

[**models::StreamMerkleStatusResponse**](StreamMerkleStatusResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## start_streaming_merkle_session_api_v1_enterprise_stream_merkle_start_post

> models::StreamMerkleStartResponse start_streaming_merkle_session_api_v1_enterprise_stream_merkle_start_post(stream_merkle_start_request)
Start Streaming Merkle Session

Start a new streaming Merkle tree construction session.  This initiates a session that allows segments to be added incrementally, ideal for real-time LLM output signing where content is generated token-by-token.  **Tier Requirement:** Professional+  Patent Reference: FIG. 5 - Streaming Merkle Tree Construction

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**stream_merkle_start_request** | [**StreamMerkleStartRequest**](StreamMerkleStartRequest.md) |  | [required] |

### Return type

[**models::StreamMerkleStartResponse**](StreamMerkleStartResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
