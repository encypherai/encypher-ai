# \EnterpriseEmbeddingsApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post**](EnterpriseEmbeddingsApi.md#encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post) | **POST** /api/v1/enterprise/embeddings/encode-with-embeddings | Encode With Embeddings
[**sign_advanced_api_v1_enterprise_embeddings_sign_advanced_post**](EnterpriseEmbeddingsApi.md#sign_advanced_api_v1_enterprise_embeddings_sign_advanced_post) | **POST** /api/v1/enterprise/embeddings/sign/advanced | Sign Advanced



## encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post

> models::EncodeWithEmbeddingsResponse encode_with_embeddings_api_v1_enterprise_embeddings_encode_with_embeddings_post(encode_with_embeddings_request, authorization)
Encode With Embeddings

Encode a document with invisible embeddings.  **Alias:** POST /enterprise/sign/advanced

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


## sign_advanced_api_v1_enterprise_embeddings_sign_advanced_post

> models::EncodeWithEmbeddingsResponse sign_advanced_api_v1_enterprise_embeddings_sign_advanced_post(encode_with_embeddings_request, authorization)
Sign Advanced

Sign a document with advanced invisible embeddings.  This is an alias for POST /enterprise/embeddings/encode-with-embeddings with a clearer name. Creates C2PA-compliant invisible signatures.  Requires Professional or Enterprise tier.

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

