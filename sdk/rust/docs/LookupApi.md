# \LookupApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**lookup_sentence_api_v1_lookup_post**](LookupApi.md#lookup_sentence_api_v1_lookup_post) | **POST** /api/v1/lookup | Lookup Sentence



## lookup_sentence_api_v1_lookup_post

> models::LookupResponse lookup_sentence_api_v1_lookup_post(lookup_request)
Lookup Sentence

Look up sentence provenance by hash.  This endpoint allows anyone to paste a sentence and find which document it originally came from, along with metadata about the publisher.  Use case: User pastes a sentence, we find which document it came from.  Note: This endpoint does NOT require authentication (public lookup).  Args:     request: LookupRequest containing sentence text     db: Database session  Returns:     LookupResponse with document and organization details if found

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

