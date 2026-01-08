# \LookupApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**lookup_sentence_api_v1_lookup_post**](LookupApi.md#lookup_sentence_api_v1_lookup_post) | **POST** /api/v1/lookup | Lookup Sentence
[**provenance_lookup_api_v1_provenance_lookup_post**](LookupApi.md#provenance_lookup_api_v1_provenance_lookup_post) | **POST** /api/v1/provenance/lookup | Provenance Lookup



## lookup_sentence_api_v1_lookup_post

> models::LookupResponse lookup_sentence_api_v1_lookup_post(lookup_request)
Lookup Sentence

Look up sentence provenance by hash.  This endpoint allows anyone to paste a sentence and find which document it originally came from, along with metadata about the publisher.  Use case: User pastes a sentence, we find which document it came from.  Note: This endpoint does NOT require authentication (public lookup).  **Alias:** POST /provenance/lookup

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**lookup_request** | [**LookupRequest**](LookupRequest.md) |  | [required] |

### Return type

[**models::LookupResponse**](LookupResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## provenance_lookup_api_v1_provenance_lookup_post

> models::LookupResponse provenance_lookup_api_v1_provenance_lookup_post(lookup_request)
Provenance Lookup

Look up sentence provenance by hash.  This is an alias for POST /lookup with a clearer name. Find which document a sentence originally came from.  Note: This endpoint does NOT require authentication (public lookup).

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**lookup_request** | [**LookupRequest**](LookupRequest.md) |  | [required] |

### Return type

[**models::LookupResponse**](LookupResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

