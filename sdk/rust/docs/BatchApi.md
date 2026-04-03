# \BatchApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**batch_sign_api_v1_batch_sign_post**](BatchApi.md#batch_sign_api_v1_batch_sign_post) | **POST** /api/v1/batch/sign | Batch Sign
[**batch_verify_api_v1_batch_verify_post**](BatchApi.md#batch_verify_api_v1_batch_verify_post) | **POST** /api/v1/batch/verify | Batch Verify



## batch_sign_api_v1_batch_sign_post

> models::BatchResponseEnvelope batch_sign_api_v1_batch_sign_post(batch_sign_request)
Batch Sign

Sign multiple documents in a single request.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**batch_sign_request** | [**BatchSignRequest**](BatchSignRequest.md) |  | [required] |

### Return type

[**models::BatchResponseEnvelope**](BatchResponseEnvelope.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## batch_verify_api_v1_batch_verify_post

> models::BatchResponseEnvelope batch_verify_api_v1_batch_verify_post(app_schemas_batch_batch_verify_request)
Batch Verify

Verify multiple documents in a single request.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**app_schemas_batch_batch_verify_request** | [**AppSchemasBatchBatchVerifyRequest**](AppSchemasBatchBatchVerifyRequest.md) |  | [required] |

### Return type

[**models::BatchResponseEnvelope**](BatchResponseEnvelope.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
