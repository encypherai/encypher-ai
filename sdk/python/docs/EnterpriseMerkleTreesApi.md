# encypher.EnterpriseMerkleTreesApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**encode_document_api_v1_enterprise_merkle_encode_post**](EnterpriseMerkleTreesApi.md#encode_document_api_v1_enterprise_merkle_encode_post) | **POST** /api/v1/enterprise/merkle/encode | Encode Document into Merkle Trees


# **encode_document_api_v1_enterprise_merkle_encode_post**
> DocumentEncodeResponse encode_document_api_v1_enterprise_merkle_encode_post(document_encode_request)

Encode Document into Merkle Trees

Encode a document into Merkle trees at specified segmentation levels.
    
    This endpoint:
    1. Segments the document text at multiple levels (word/sentence/paragraph/section)
    2. Builds Merkle trees for each segmentation level
    3. Stores all tree data in the database for future attribution queries
    4. Returns root hashes and tree metadata
    
    **Enterprise Tier Only** - Requires valid organization with Merkle features enabled.
    
    **Rate Limits:**
    - Free tier: Not available
    - Enterprise tier: 1000 documents/month
    
    **Processing Time:**
    - Small documents (<1000 words): ~100-200ms
    - Medium documents (1000-10000 words): ~500ms-2s
    - Large documents (>10000 words): ~2-10s

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.document_encode_request import DocumentEncodeRequest
from encypher.models.document_encode_response import DocumentEncodeResponse
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
    api_instance = encypher.EnterpriseMerkleTreesApi(api_client)
    document_encode_request = encypher.DocumentEncodeRequest() # DocumentEncodeRequest | 

    try:
        # Encode Document into Merkle Trees
        api_response = api_instance.encode_document_api_v1_enterprise_merkle_encode_post(document_encode_request)
        print("The response of EnterpriseMerkleTreesApi->encode_document_api_v1_enterprise_merkle_encode_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EnterpriseMerkleTreesApi->encode_document_api_v1_enterprise_merkle_encode_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_encode_request** | [**DocumentEncodeRequest**](DocumentEncodeRequest.md)|  | 

### Return type

[**DocumentEncodeResponse**](DocumentEncodeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Document encoded successfully |  -  |
**400** | Invalid request |  -  |
**401** | Unauthorized |  -  |
**403** | Quota exceeded or feature not enabled |  -  |
**500** | Server error |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

