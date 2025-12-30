# encypher.EnterpriseMerkleTreesApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**detect_plagiarism_api_v1_enterprise_merkle_detect_plagiarism_post**](EnterpriseMerkleTreesApi.md#detect_plagiarism_api_v1_enterprise_merkle_detect_plagiarism_post) | **POST** /api/v1/enterprise/merkle/detect-plagiarism | Detect Plagiarism
[**encode_document_api_v1_enterprise_merkle_encode_post**](EnterpriseMerkleTreesApi.md#encode_document_api_v1_enterprise_merkle_encode_post) | **POST** /api/v1/enterprise/merkle/encode | Encode Document into Merkle Trees
[**find_sources_api_v1_enterprise_merkle_attribute_post**](EnterpriseMerkleTreesApi.md#find_sources_api_v1_enterprise_merkle_attribute_post) | **POST** /api/v1/enterprise/merkle/attribute | Find Source Documents


# **detect_plagiarism_api_v1_enterprise_merkle_detect_plagiarism_post**
> PlagiarismDetectionResponse detect_plagiarism_api_v1_enterprise_merkle_detect_plagiarism_post(plagiarism_detection_request)

Detect Plagiarism

Analyze text for potential plagiarism by comparing against indexed documents.
    
    This endpoint:
    1. Segments the target text
    2. Checks each segment against the Merkle tree index
    3. Identifies matching source documents
    4. Calculates match percentages and confidence scores
    5. Generates a heat map showing which parts match
    
    **Use Cases:**
    - Academic plagiarism detection
    - Content originality verification
    - Copyright infringement detection
    - Duplicate content identification
    
    **Enterprise Tier Only**

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.plagiarism_detection_request import PlagiarismDetectionRequest
from encypher.models.plagiarism_detection_response import PlagiarismDetectionResponse
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
    plagiarism_detection_request = encypher.PlagiarismDetectionRequest() # PlagiarismDetectionRequest | 

    try:
        # Detect Plagiarism
        api_response = api_instance.detect_plagiarism_api_v1_enterprise_merkle_detect_plagiarism_post(plagiarism_detection_request)
        print("The response of EnterpriseMerkleTreesApi->detect_plagiarism_api_v1_enterprise_merkle_detect_plagiarism_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EnterpriseMerkleTreesApi->detect_plagiarism_api_v1_enterprise_merkle_detect_plagiarism_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plagiarism_detection_request** | [**PlagiarismDetectionRequest**](PlagiarismDetectionRequest.md)|  | 

### Return type

[**PlagiarismDetectionResponse**](PlagiarismDetectionResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Analysis completed successfully |  -  |
**400** | Invalid request |  -  |
**401** | Unauthorized |  -  |
**500** | Server error |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

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

# **find_sources_api_v1_enterprise_merkle_attribute_post**
> SourceAttributionResponse find_sources_api_v1_enterprise_merkle_attribute_post(source_attribution_request)

Find Source Documents

Find source documents that contain a specific text segment.
    
    This endpoint searches the Merkle tree index to find which documents
    contain the provided text segment.
    
    **Use Cases:**
    - Verify if a text segment appears in your document repository
    - Find the original source of a quote or passage
    - Check if content has been previously published
    
    **Enterprise Tier Only**

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.source_attribution_request import SourceAttributionRequest
from encypher.models.source_attribution_response import SourceAttributionResponse
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
    source_attribution_request = encypher.SourceAttributionRequest() # SourceAttributionRequest | 

    try:
        # Find Source Documents
        api_response = api_instance.find_sources_api_v1_enterprise_merkle_attribute_post(source_attribution_request)
        print("The response of EnterpriseMerkleTreesApi->find_sources_api_v1_enterprise_merkle_attribute_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EnterpriseMerkleTreesApi->find_sources_api_v1_enterprise_merkle_attribute_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_attribution_request** | [**SourceAttributionRequest**](SourceAttributionRequest.md)|  | 

### Return type

[**SourceAttributionResponse**](SourceAttributionResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Search completed successfully |  -  |
**400** | Invalid request |  -  |
**401** | Unauthorized |  -  |
**500** | Server error |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

