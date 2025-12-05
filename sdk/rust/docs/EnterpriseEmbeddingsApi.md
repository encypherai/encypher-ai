# \EnterpriseEmbeddingsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post**](EnterpriseEmbeddingsApi.md#encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post) | **POST** /api/v1/enterprise/embeddings/encode-with-embeddings | Encode With Embeddings



## encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post

> models::EncodeWithEmbeddingsResponse encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post(encode_with_embeddings_request, authorization)
Encode With Embeddings

Encode a document with invisible embeddings.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**encode_with_embeddings_request** | [**EncodeWithEmbeddingsRequest**](EncodeWithEmbeddingsRequest.md) |  | [required] |
**authorization** | Option<**String**> |  |  |

### Return type

[**models::EncodeWithEmbeddingsResponse**](EncodeWithEmbeddingsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

