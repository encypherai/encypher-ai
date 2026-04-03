# \EvidenceGenerationApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**generate_evidence_api_v1_enterprise_evidence_generate_post**](EvidenceGenerationApi.md#generate_evidence_api_v1_enterprise_evidence_generate_post) | **POST** /api/v1/enterprise/evidence/generate | Generate Evidence



## generate_evidence_api_v1_enterprise_evidence_generate_post

> models::EvidenceGenerateResponse generate_evidence_api_v1_enterprise_evidence_generate_post(evidence_generate_request)
Generate Evidence

Generate an evidence package for content attribution.  This endpoint creates a comprehensive evidence package containing: - Content hash verification - Merkle proof (if available) - Signature verification chain - Timestamp verification - Source attribution details  **Tier Requirement:** Enterprise  Patent Reference: FIG. 11 - Evidence Generation & Attribution Flow

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**evidence_generate_request** | [**EvidenceGenerateRequest**](EvidenceGenerateRequest.md) |  | [required] |

### Return type

[**models::EvidenceGenerateResponse**](EvidenceGenerateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
