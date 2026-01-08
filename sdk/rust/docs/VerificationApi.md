# \VerificationApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**verify_by_document_id_api_v1_verify_document_id_get**](VerificationApi.md#verify_by_document_id_api_v1_verify_document_id_get) | **GET** /api/v1/verify/{document_id} | Verify By Document Id
[**verify_content_api_v1_verify_post**](VerificationApi.md#verify_content_api_v1_verify_post) | **POST** /api/v1/verify | Verify Content



## verify_by_document_id_api_v1_verify_document_id_get

> serde_json::Value verify_by_document_id_api_v1_verify_document_id_get(document_id)
Verify By Document Id

Verify a document by its ID (for clickable verification links).  Returns an HTML page so users can preview verification state in a browser.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_id** | **String** |  | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## verify_content_api_v1_verify_post

> models::VerifyResponse verify_content_api_v1_verify_post(verify_request)
Verify Content

Verify C2PA manifest in signed content using the encypher-ai library.  This endpoint is public, rate limited, and returns structured machine-friendly verdicts that SDKs consume.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**verify_request** | [**VerifyRequest**](VerifyRequest.md) |  | [required] |

### Return type

[**models::VerifyResponse**](VerifyResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

