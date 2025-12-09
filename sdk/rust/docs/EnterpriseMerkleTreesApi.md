# \EnterpriseMerkleTreesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**detect_plagiarism_api_v1_enterprise_merkle_detect_plagiarism_post**](EnterpriseMerkleTreesApi.md#detect_plagiarism_api_v1_enterprise_merkle_detect_plagiarism_post) | **POST** /api/v1/enterprise/merkle/detect-plagiarism | Detect Plagiarism
[**encode_document_api_v1_enterprise_merkle_encode_post**](EnterpriseMerkleTreesApi.md#encode_document_api_v1_enterprise_merkle_encode_post) | **POST** /api/v1/enterprise/merkle/encode | Encode Document into Merkle Trees
[**find_sources_api_v1_enterprise_merkle_attribute_post**](EnterpriseMerkleTreesApi.md#find_sources_api_v1_enterprise_merkle_attribute_post) | **POST** /api/v1/enterprise/merkle/attribute | Find Source Documents



## detect_plagiarism_api_v1_enterprise_merkle_detect_plagiarism_post

> models::PlagiarismDetectionResponse detect_plagiarism_api_v1_enterprise_merkle_detect_plagiarism_post(plagiarism_detection_request)
Detect Plagiarism

Analyze text for potential plagiarism by comparing against indexed documents.          This endpoint:     1. Segments the target text     2. Checks each segment against the Merkle tree index     3. Identifies matching source documents     4. Calculates match percentages and confidence scores     5. Generates a heat map showing which parts match          **Use Cases:**     - Academic plagiarism detection     - Content originality verification     - Copyright infringement detection     - Duplicate content identification          **Enterprise Tier Only**

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**plagiarism_detection_request** | [**PlagiarismDetectionRequest**](PlagiarismDetectionRequest.md) |  | [required] |

### Return type

[**models::PlagiarismDetectionResponse**](PlagiarismDetectionResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


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


## find_sources_api_v1_enterprise_merkle_attribute_post

> models::SourceAttributionResponse find_sources_api_v1_enterprise_merkle_attribute_post(source_attribution_request)
Find Source Documents

Find source documents that contain a specific text segment.          This endpoint searches the Merkle tree index to find which documents     contain the provided text segment.          **Use Cases:**     - Verify if a text segment appears in your document repository     - Find the original source of a quote or passage     - Check if content has been previously published          **Enterprise Tier Only**

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**source_attribution_request** | [**SourceAttributionRequest**](SourceAttributionRequest.md) |  | [required] |

### Return type

[**models::SourceAttributionResponse**](SourceAttributionResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

