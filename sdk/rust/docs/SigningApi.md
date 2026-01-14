# \SigningApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**sign_advanced_api_v1_sign_advanced_post**](SigningApi.md#sign_advanced_api_v1_sign_advanced_post) | **POST** /api/v1/sign/advanced | Sign with advanced embedding controls
[**sign_content_api_v1_sign_post**](SigningApi.md#sign_content_api_v1_sign_post) | **POST** /api/v1/sign | Sign Content



## sign_advanced_api_v1_sign_advanced_post

> models::EncodeWithEmbeddingsResponse sign_advanced_api_v1_sign_advanced_post(encode_with_embeddings_request)
Sign with advanced embedding controls

Sign a document while enabling advanced embedding controls (e.g., manifest options and distribution strategies).  Tier requirements are enforced server-side (typically Professional+ depending on selected options).

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**encode_with_embeddings_request** | [**EncodeWithEmbeddingsRequest**](EncodeWithEmbeddingsRequest.md) |  | [required] |

### Return type

[**models::EncodeWithEmbeddingsResponse**](EncodeWithEmbeddingsResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## sign_content_api_v1_sign_post

> models::SignResponse sign_content_api_v1_sign_post(sign_request)
Sign Content

Sign content with a C2PA manifest.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**sign_request** | [**SignRequest**](SignRequest.md) |  | [required] |

### Return type

[**models::SignResponse**](SignResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

