# EvidenceGenerationApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**generateEvidenceApiV1EnterpriseEvidenceGeneratePost**](EvidenceGenerationApi.md#generateevidenceapiv1enterpriseevidencegeneratepost) | **POST** /api/v1/enterprise/evidence/generate | Generate Evidence |



## generateEvidenceApiV1EnterpriseEvidenceGeneratePost

> EvidenceGenerateResponse generateEvidenceApiV1EnterpriseEvidenceGeneratePost(evidenceGenerateRequest)

Generate Evidence

Generate an evidence package for content attribution.  This endpoint creates a comprehensive evidence package containing: - Content hash verification - Merkle proof (if available) - Signature verification chain - Timestamp verification - Source attribution details  **Tier Requirement:** Enterprise  Patent Reference: FIG. 11 - Evidence Generation &amp; Attribution Flow

### Example

```ts
import {
  Configuration,
  EvidenceGenerationApi,
} from '@encypher/sdk';
import type { GenerateEvidenceApiV1EnterpriseEvidenceGeneratePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new EvidenceGenerationApi(config);

  const body = {
    // EvidenceGenerateRequest
    evidenceGenerateRequest: ...,
  } satisfies GenerateEvidenceApiV1EnterpriseEvidenceGeneratePostRequest;

  try {
    const data = await api.generateEvidenceApiV1EnterpriseEvidenceGeneratePost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **evidenceGenerateRequest** | [EvidenceGenerateRequest](EvidenceGenerateRequest.md) |  | |

### Return type

[**EvidenceGenerateResponse**](EvidenceGenerateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

