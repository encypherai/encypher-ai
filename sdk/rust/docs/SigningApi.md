# \SigningApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**sign_advanced_api_v1_sign_advanced_post**](SigningApi.md#sign_advanced_api_v1_sign_advanced_post) | **POST** /api/v1/sign/advanced | REMOVED - Use POST /sign with options instead
[**sign_content_api_v1_sign_post**](SigningApi.md#sign_content_api_v1_sign_post) | **POST** /api/v1/sign | Sign content with C2PA manifest



## sign_advanced_api_v1_sign_advanced_post

> serde_json::Value sign_advanced_api_v1_sign_advanced_post()
REMOVED - Use POST /sign with options instead

**⚠️ REMOVED: This endpoint has been removed.**  Please use `POST /sign` with options instead.  Migration example: ```json // Old /sign/advanced request {     \"document_id\": \"doc1\",     \"text\": \"...\",     \"segmentation_level\": \"sentence\" }  // New /sign request {     \"text\": \"...\",     \"document_id\": \"doc1\",     \"options\": {         \"segmentation_level\": \"sentence\"     } } ```

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


## sign_content_api_v1_sign_post

> serde_json::Value sign_content_api_v1_sign_post(unified_sign_request)
Sign content with C2PA manifest

Sign content with C2PA manifest. Features are gated by tier.  **Tier Feature Matrix:**  | Feature | Free/Starter | Professional | Business | Enterprise | |---------|--------------|--------------|----------|------------| | Basic C2PA signing | ✅ | ✅ | ✅ | ✅ | | Sentence segmentation | ❌ | ✅ | ✅ | ✅ | | Advanced manifest modes | ❌ | ✅ | ✅ | ✅ | | Attribution indexing | ❌ | ✅ | ✅ | ✅ | | Custom assertions | ❌ | ❌ | ✅ | ✅ | | Rights metadata | ❌ | ❌ | ✅ | ✅ | | Dual binding | ❌ | ❌ | ❌ | ✅ | | Fingerprinting | ❌ | ❌ | ❌ | ✅ | | Batch size | 1 | 10 | 50 | 100 |  **Single Document:** ```json {     \"text\": \"Content to sign...\",     \"document_title\": \"My Article\",     \"options\": {         \"segmentation_level\": \"sentence\"     } } ```  **Batch (Professional+):** ```json {     \"documents\": [         {\"text\": \"First doc...\", \"document_title\": \"Doc 1\"},         {\"text\": \"Second doc...\", \"document_title\": \"Doc 2\"}     ],     \"options\": {         \"segmentation_level\": \"sentence\"     } } ```  The response includes `meta.features_gated` showing features available at higher tiers.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**unified_sign_request** | [**UnifiedSignRequest**](UnifiedSignRequest.md) |  | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

