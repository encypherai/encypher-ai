# encypher.EvidenceGenerationApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**generate_evidence_api_v1_enterprise_evidence_generate_post**](EvidenceGenerationApi.md#generate_evidence_api_v1_enterprise_evidence_generate_post) | **POST** /api/v1/enterprise/evidence/generate | Generate Evidence


# **generate_evidence_api_v1_enterprise_evidence_generate_post**
> EvidenceGenerateResponse generate_evidence_api_v1_enterprise_evidence_generate_post(evidence_generate_request)

Generate Evidence

Generate an evidence package for content attribution.

This endpoint creates a comprehensive evidence package containing:
- Content hash verification
- Merkle proof (if available)
- Signature verification chain
- Timestamp verification
- Source attribution details

**Tier Requirement:** Enterprise

Patent Reference: FIG. 11 - Evidence Generation & Attribution Flow

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.evidence_generate_request import EvidenceGenerateRequest
from encypher.models.evidence_generate_response import EvidenceGenerateResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypherai.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypherai.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = encypher.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.EvidenceGenerationApi(api_client)
    evidence_generate_request = encypher.EvidenceGenerateRequest() # EvidenceGenerateRequest | 

    try:
        # Generate Evidence
        api_response = api_instance.generate_evidence_api_v1_enterprise_evidence_generate_post(evidence_generate_request)
        print("The response of EvidenceGenerationApi->generate_evidence_api_v1_enterprise_evidence_generate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EvidenceGenerationApi->generate_evidence_api_v1_enterprise_evidence_generate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **evidence_generate_request** | [**EvidenceGenerateRequest**](EvidenceGenerateRequest.md)|  | 

### Return type

[**EvidenceGenerateResponse**](EvidenceGenerateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

