# \FingerprintApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**detect_fingerprint_api_v1_enterprise_fingerprint_detect_post**](FingerprintApi.md#detect_fingerprint_api_v1_enterprise_fingerprint_detect_post) | **POST** /api/v1/enterprise/fingerprint/detect | Detect Fingerprint
[**encode_fingerprint_api_v1_enterprise_fingerprint_encode_post**](FingerprintApi.md#encode_fingerprint_api_v1_enterprise_fingerprint_encode_post) | **POST** /api/v1/enterprise/fingerprint/encode | Encode Fingerprint



## detect_fingerprint_api_v1_enterprise_fingerprint_detect_post

> models::FingerprintDetectResponse detect_fingerprint_api_v1_enterprise_fingerprint_detect_post(fingerprint_detect_request)
Detect Fingerprint

Detect a fingerprint in text.  Detection uses score-based matching with confidence threshold to identify fingerprinted content even after modifications.  **Tier Requirement:** Enterprise

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**fingerprint_detect_request** | [**FingerprintDetectRequest**](FingerprintDetectRequest.md) |  | [required] |

### Return type

[**models::FingerprintDetectResponse**](FingerprintDetectResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## encode_fingerprint_api_v1_enterprise_fingerprint_encode_post

> models::FingerprintEncodeResponse encode_fingerprint_api_v1_enterprise_fingerprint_encode_post(fingerprint_encode_request)
Encode Fingerprint

Encode a robust fingerprint into text.  Fingerprints use secret-seeded placement of invisible markers that survive text modifications like paraphrasing or truncation.  **Tier Requirement:** Enterprise

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**fingerprint_encode_request** | [**FingerprintEncodeRequest**](FingerprintEncodeRequest.md) |  | [required] |

### Return type

[**models::FingerprintEncodeResponse**](FingerprintEncodeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
