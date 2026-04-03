# \EnterpriseMerkleTreesApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**encode_document_api_v1_enterprise_merkle_encode_post**](EnterpriseMerkleTreesApi.md#encode_document_api_v1_enterprise_merkle_encode_post) | **POST** /api/v1/enterprise/merkle/encode | Encode Document into Merkle Trees



## encode_document_api_v1_enterprise_merkle_encode_post

> models::DocumentEncodeResponse encode_document_api_v1_enterprise_merkle_encode_post(document_encode_request)
Encode Document into Merkle Trees

Encode a document into Merkle trees at specified segmentation levels.          This endpoint:     1. Segments the document text at multiple levels (word/sentence/paragraph/section)     2. Builds Merkle trees for each segmentation level     3. Stores all tree data in the database for future attribution queries     4. Returns root hashes and tree metadata          **Enterprise Tier Only** - Requires valid organization with Merkle features enabled.          **Rate Limits:**     - Free tier: Not available     - Enterprise tier: 1000 documents/month          **Processing Time:**     - Small documents (<1000 words): ~100-200ms     - Medium documents (1000-10000 words): ~500ms-2s     - Large documents (>10000 words): ~2-10s

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_encode_request** | [**DocumentEncodeRequest**](DocumentEncodeRequest.md) |  | [required] |

### Return type

[**models::DocumentEncodeResponse**](DocumentEncodeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
