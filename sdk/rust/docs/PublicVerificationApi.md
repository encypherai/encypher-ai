# \PublicVerificationApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**batch_verify_embeddings_api_v1_public_verify_batch_post**](PublicVerificationApi.md#batch_verify_embeddings_api_v1_public_verify_batch_post) | **POST** /api/v1/public/verify/batch | Batch Verify Embeddings (Public - No Auth Required)
[**extract_and_verify_embedding_api_v1_public_extract_and_verify_post**](PublicVerificationApi.md#extract_and_verify_embedding_api_v1_public_extract_and_verify_post) | **POST** /api/v1/public/extract-and-verify | Extract and Verify Invisible Embedding (Public - No Auth Required)
[**verify_embedding_api_v1_public_verify_ref_id_get**](PublicVerificationApi.md#verify_embedding_api_v1_public_verify_ref_id_get) | **GET** /api/v1/public/verify/{ref_id} | Verify Embedding (Public - No Auth Required)



## batch_verify_embeddings_api_v1_public_verify_batch_post

> models::BatchVerifyResponse batch_verify_embeddings_api_v1_public_verify_batch_post(app_schemas_embeddings_batch_verify_request, authorization)
Batch Verify Embeddings (Public - No Auth Required)

Verify multiple embeddings in a single request.          **This endpoint is PUBLIC and does NOT require authentication.**          Useful for:     - Verifying all embeddings on a page at once     - Bulk verification by web scrapers     - Browser extensions checking multiple paragraphs          **Rate Limiting:**     - 100 requests/hour per IP address     - Maximum 50 embeddings per request

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**app_schemas_embeddings_batch_verify_request** | [**AppSchemasEmbeddingsBatchVerifyRequest**](AppSchemasEmbeddingsBatchVerifyRequest.md) |  | [required] |
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

> models::ExtractAndVerifyResponse extract_and_verify_embedding_api_v1_public_extract_and_verify_post(extract_and_verify_request, authorization)
Extract and Verify Invisible Embedding (Public - No Auth Required)

Extract and verify invisible Unicode embedding from text using encypher-ai.          **This endpoint is PUBLIC and does NOT require authentication.**          This is the NEW verification method for invisible embeddings:     - Extracts invisible Unicode variation selector embeddings     - Verifies cryptographic signature using encypher-ai     - Returns enterprise metadata (Merkle tree, document info, etc.)          **How it works:**     1. Text contains invisible Unicode variation selectors     2. encypher-ai extracts and verifies the embedded metadata     3. Enterprise API looks up Merkle tree and document info     4. Returns full verification result with all metadata          **Rate Limiting:**     - 1000 requests/hour per IP address          **Example Usage:**     ```json     POST /api/v1/public/extract-and-verify     {       \"text\": \"Content with invisible embedding...\"     }     ```

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**extract_and_verify_request** | [**ExtractAndVerifyRequest**](ExtractAndVerifyRequest.md) |  | [required] |
**authorization** | Option<**String**> |  |  |

### Return type

[**models::ExtractAndVerifyResponse**](ExtractAndVerifyResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## verify_embedding_api_v1_public_verify_ref_id_get

> models::VerifyEmbeddingResponse verify_embedding_api_v1_public_verify_ref_id_get(ref_id, signature, authorization)
Verify Embedding (Public - No Auth Required)

Verify a minimal signed embedding and retrieve associated metadata.          **This endpoint is PUBLIC and does NOT require authentication.**          Third parties can use this endpoint to:     - Verify authenticity of content with embedded markers     - Retrieve document metadata (title, author, organization)     - Access C2PA manifest information     - View licensing terms     - Get Merkle proof for cryptographic verification          **Rate Limiting:**     - 1000 requests/hour per IP address     - CAPTCHA required after repeated failures          **Privacy:**     - Only returns text preview (first 200 characters)     - Full text content is NOT exposed     - Internal document IDs are mapped to public IDs          **Example Usage:**     ```     GET /api/v1/public/verify/a3f9c2e1?signature=8k3mP9xQ     ```

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

