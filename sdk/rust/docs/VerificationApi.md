# \VerificationApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_stats_api_v1_verify_stats_get**](VerificationApi.md#get_stats_api_v1_verify_stats_get) | **GET** /api/v1/verify/stats | Get Stats
[**get_verification_history_api_v1_verify_history_document_id_get**](VerificationApi.md#get_verification_history_api_v1_verify_history_document_id_get) | **GET** /api/v1/verify/history/{document_id} | Get Verification History
[**health_check_api_v1_verify_health_get**](VerificationApi.md#health_check_api_v1_verify_health_get) | **GET** /api/v1/verify/health | Health Check
[**verify_advanced_api_v1_verify_advanced_post**](VerificationApi.md#verify_advanced_api_v1_verify_advanced_post) | **POST** /api/v1/verify/advanced | Advanced verification
[**verify_by_document_id_api_v1_verify_document_id_get**](VerificationApi.md#verify_by_document_id_api_v1_verify_document_id_get) | **GET** /api/v1/verify/{document_id} | Verify By Document Id
[**verify_document_api_v1_verify_document_post**](VerificationApi.md#verify_document_api_v1_verify_document_post) | **POST** /api/v1/verify/document | Verify Document
[**verify_signature_api_v1_verify_signature_post**](VerificationApi.md#verify_signature_api_v1_verify_signature_post) | **POST** /api/v1/verify/signature | Verify Signature
[**verify_text_api_v1_verify_post**](VerificationApi.md#verify_text_api_v1_verify_post) | **POST** /api/v1/verify | Verify Text



## get_stats_api_v1_verify_stats_get

> models::VerificationStats get_stats_api_v1_verify_stats_get(authorization)
Get Stats

Get verification statistics

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**authorization** | Option<**String**> |  |  |

### Return type

[**models::VerificationStats**](VerificationStats.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_verification_history_api_v1_verify_history_document_id_get

> Vec<models::VerificationHistory> get_verification_history_api_v1_verify_history_document_id_get(document_id, limit)
Get Verification History

Get verification history for a document (public endpoint)  - **document_id**: Document ID - **limit**: Maximum number of results

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_id** | **String** |  | [required] |
**limit** | Option<**i32**> |  |  |[default to 100]

### Return type

[**Vec<models::VerificationHistory>**](VerificationHistory.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## health_check_api_v1_verify_health_get

> serde_json::Value health_check_api_v1_verify_health_get()
Health Check

Health check endpoint

### Parameters

This endpoint does not need any parameter.

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## verify_advanced_api_v1_verify_advanced_post

> serde_json::Value verify_advanced_api_v1_verify_advanced_post(verify_advanced_request)
Advanced verification

Verify signed content and optionally run attribution/plagiarism analysis.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**verify_advanced_request** | [**VerifyAdvancedRequest**](VerifyAdvancedRequest.md) |  | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## verify_by_document_id_api_v1_verify_document_id_get

> serde_json::Value verify_by_document_id_api_v1_verify_document_id_get(document_id)
Verify By Document Id

Verify a document by its ID (for clickable verification links).  Returns an HTML page so users can preview verification state in a browser. This endpoint queries the content database for the signed document.

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


## verify_document_api_v1_verify_document_post

> models::VerificationResponse verify_document_api_v1_verify_document_post(document_verify, x_forwarded_for, user_agent, authorization)
Verify Document

Complete document verification (public endpoint)  - **document_id**: Document ID from encoding service - **content**: Current content to verify

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_verify** | [**DocumentVerify**](DocumentVerify.md) |  | [required] |
**x_forwarded_for** | Option<**String**> |  |  |
**user_agent** | Option<**String**> |  |  |
**authorization** | Option<**String**> |  |  |

### Return type

[**models::VerificationResponse**](VerificationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## verify_signature_api_v1_verify_signature_post

> models::VerificationResponse verify_signature_api_v1_verify_signature_post(signature_verify, x_forwarded_for, user_agent, authorization)
Verify Signature

Verify a signature (public endpoint)  - **content**: Original content - **signature**: Hex-encoded signature - **public_key_pem**: PEM-encoded public key

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**signature_verify** | [**SignatureVerify**](SignatureVerify.md) |  | [required] |
**x_forwarded_for** | Option<**String**> |  |  |
**user_agent** | Option<**String**> |  |  |
**authorization** | Option<**String**> |  |  |

### Return type

[**models::VerificationResponse**](VerificationResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## verify_text_api_v1_verify_post

> models::VerifyResponse verify_text_api_v1_verify_post(verify_request, authorization)
Verify Text

Verify signed content and return a structured verdict.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**verify_request** | [**VerifyRequest**](VerifyRequest.md) |  | [required] |
**authorization** | Option<**String**> |  |  |

### Return type

[**models::VerifyResponse**](VerifyResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
