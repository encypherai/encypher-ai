# \SigningApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**sign_content_api_v1_sign_post**](SigningApi.md#sign_content_api_v1_sign_post) | **POST** /api/v1/sign | Sign Content



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

