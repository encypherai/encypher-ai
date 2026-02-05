# \PublicVerificationApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**batch_verify_embeddings_api_v1_public_verify_batch_post**](PublicVerificationApi.md#batch_verify_embeddings_api_v1_public_verify_batch_post) | **POST** /api/v1/public/verify/batch | Batch Verify Embeddings (Public - No Auth Required)
[**extract_and_verify_embedding_api_v1_public_extract_and_verify_post**](PublicVerificationApi.md#extract_and_verify_embedding_api_v1_public_extract_and_verify_post) | **POST** /api/v1/public/extract-and-verify | DEPRECATED - Use POST /api/v1/verify instead
[**verify_embedding_api_v1_public_verify_ref_id_get**](PublicVerificationApi.md#verify_embedding_api_v1_public_verify_ref_id_get) | **GET** /api/v1/public/verify/{ref_id} | Verify Embedding (Public - No Auth Required)



## batch_verify_embeddings_api_v1_public_verify_batch_post

> models::BatchVerifyResponse batch_verify_embeddings_api_v1_public_verify_batch_post(batch_verify_request, authorization)
Batch Verify Embeddings (Public - No Auth Required)

Verify multiple embeddings in a single request.          **This endpoint is PUBLIC and does NOT require authentication.**          Useful for:     - Verifying all embeddings on a page at once     - Bulk verification by web scrapers     - Browser extensions checking multiple paragraphs          **Rate Limiting:**     - 100 requests/hour per IP address     - Maximum 50 embeddings per request

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**batch_verify_request** | [**BatchVerifyRequest**](BatchVerifyRequest.md) |  | [required] |
**authorization** | Option<**String**> |  |  |

### Return type

[**models::BatchVerifyResponse**](BatchVerifyResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## extract_and_verify_embedding_api_v1_public_extract_and_verify_post

> serde_json::Value extract_and_verify_embedding_api_v1_public_extract_and_verify_post(extract_and_verify_request)
DEPRECATED - Use POST /api/v1/verify instead

**⚠️ DEPRECATED: This endpoint is deprecated and will be removed.**          Please use `POST /api/v1/verify` instead, which provides:     - Full C2PA trust chain validation     - Document info, licensing, and C2PA details (all free)     - Merkle proof (with API key)     - Better performance via verification-service

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**extract_and_verify_request** | [**ExtractAndVerifyRequest**](ExtractAndVerifyRequest.md) |  | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## verify_embedding_api_v1_public_verify_ref_id_get

> models::VerifyEmbeddingResponse verify_embedding_api_v1_public_verify_ref_id_get(ref_id, signature, authorization)
Verify Embedding (Public - No Auth Required)

Verify a minimal signed embedding and retrieve associated metadata.          **This endpoint is PUBLIC and does NOT require authentication.**          Third parties can use this endpoint to:     - Verify authenticity of content with embedded markers     - Retrieve document metadata (title, author, organization)     - Access C2PA manifest information     - View licensing terms     - Get Merkle proof for cryptographic verification          **Rate Limiting:**     - 1000 requests/hour per IP address     - CAPTCHA required after repeated failures          **Privacy:**     - Does not return DB-stored text     - Full text content is NOT exposed     - Internal document IDs are mapped to public IDs          **Example Usage:**     ```     GET /api/v1/public/verify/a3f9c2e1?signature=8k3mP9xQ     ```

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**ref_id** | **String** |  | [required] |
**signature** | **String** | HMAC signature (8+ hex characters) | [required] |
**authorization** | Option<**String**> |  |  |

### Return type

[**models::VerifyEmbeddingResponse**](VerifyEmbeddingResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

