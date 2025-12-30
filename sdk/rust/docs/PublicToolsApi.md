# \PublicToolsApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**decode_text_api_v1_tools_decode_post**](PublicToolsApi.md#decode_text_api_v1_tools_decode_post) | **POST** /api/v1/tools/decode | Decode Text
[**decode_text_api_v1_tools_decode_post_0**](PublicToolsApi.md#decode_text_api_v1_tools_decode_post_0) | **POST** /api/v1/tools/decode | Decode Text
[**encode_text_api_v1_tools_encode_post**](PublicToolsApi.md#encode_text_api_v1_tools_encode_post) | **POST** /api/v1/tools/encode | Encode Text
[**encode_text_api_v1_tools_encode_post_0**](PublicToolsApi.md#encode_text_api_v1_tools_encode_post_0) | **POST** /api/v1/tools/encode | Encode Text



## decode_text_api_v1_tools_decode_post

> models::DecodeToolResponse decode_text_api_v1_tools_decode_post(decode_tool_request)
Decode Text

Decode and verify text containing embedded metadata.  This is a public endpoint for the website demo tool. Supports multiple embeddings in a single text (Encypher proprietary feature). Verification uses Trust Anchor lookup - checks database for org public keys. Falls back to demo key for demo-signed content.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**decode_tool_request** | [**DecodeToolRequest**](DecodeToolRequest.md) |  | [required] |

### Return type

[**models::DecodeToolResponse**](DecodeToolResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## decode_text_api_v1_tools_decode_post_0

> models::DecodeToolResponse decode_text_api_v1_tools_decode_post_0(decode_tool_request)
Decode Text

Decode and verify text containing embedded metadata.  This is a public endpoint for the website demo tool. Supports multiple embeddings in a single text (Encypher proprietary feature). Verification uses Trust Anchor lookup - checks database for org public keys. Falls back to demo key for demo-signed content.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**decode_tool_request** | [**DecodeToolRequest**](DecodeToolRequest.md) |  | [required] |

### Return type

[**models::DecodeToolResponse**](DecodeToolResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## encode_text_api_v1_tools_encode_post

> models::EncodeToolResponse encode_text_api_v1_tools_encode_post(encode_tool_request)
Encode Text

Encode text with embedded metadata using the demo key.  This is a public endpoint for the website demo tool. All encoding uses a server-side demo key.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**encode_tool_request** | [**EncodeToolRequest**](EncodeToolRequest.md) |  | [required] |

### Return type

[**models::EncodeToolResponse**](EncodeToolResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## encode_text_api_v1_tools_encode_post_0

> models::EncodeToolResponse encode_text_api_v1_tools_encode_post_0(encode_tool_request)
Encode Text

Encode text with embedded metadata using the demo key.  This is a public endpoint for the website demo tool. All encoding uses a server-side demo key.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**encode_tool_request** | [**EncodeToolRequest**](EncodeToolRequest.md) |  | [required] |

### Return type

[**models::EncodeToolResponse**](EncodeToolResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

