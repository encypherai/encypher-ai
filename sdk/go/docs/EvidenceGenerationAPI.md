# \EvidenceGenerationAPI

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GenerateEvidenceApiV1EnterpriseEvidenceGeneratePost**](EvidenceGenerationAPI.md#GenerateEvidenceApiV1EnterpriseEvidenceGeneratePost) | **Post** /api/v1/enterprise/evidence/generate | Generate Evidence



## GenerateEvidenceApiV1EnterpriseEvidenceGeneratePost

> EvidenceGenerateResponse GenerateEvidenceApiV1EnterpriseEvidenceGeneratePost(ctx).EvidenceGenerateRequest(evidenceGenerateRequest).Execute()

Generate Evidence



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/encypherai/encypherai-commercial/sdk/go"
)

func main() {
	evidenceGenerateRequest := *openapiclient.NewEvidenceGenerateRequest("TargetText_example") // EvidenceGenerateRequest |

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.EvidenceGenerationAPI.GenerateEvidenceApiV1EnterpriseEvidenceGeneratePost(context.Background()).EvidenceGenerateRequest(evidenceGenerateRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `EvidenceGenerationAPI.GenerateEvidenceApiV1EnterpriseEvidenceGeneratePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GenerateEvidenceApiV1EnterpriseEvidenceGeneratePost`: EvidenceGenerateResponse
	fmt.Fprintf(os.Stdout, "Response from `EvidenceGenerationAPI.GenerateEvidenceApiV1EnterpriseEvidenceGeneratePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGenerateEvidenceApiV1EnterpriseEvidenceGeneratePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **evidenceGenerateRequest** | [**EvidenceGenerateRequest**](EvidenceGenerateRequest.md) |  |

### Return type

[**EvidenceGenerateResponse**](EvidenceGenerateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
