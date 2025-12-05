# encypher.LookupApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**lookup_sentence_api_v1_lookup_post**](LookupApi.md#lookup_sentence_api_v1_lookup_post) | **POST** /api/v1/lookup | Lookup Sentence


# **lookup_sentence_api_v1_lookup_post**
> LookupResponse lookup_sentence_api_v1_lookup_post(lookup_request)

Lookup Sentence

Look up sentence provenance by hash.

This endpoint allows anyone to paste a sentence and find which document
it originally came from, along with metadata about the publisher.

Use case: User pastes a sentence, we find which document it came from.

Note: This endpoint does NOT require authentication (public lookup).

Args:
    request: LookupRequest containing sentence text
    db: Database session

Returns:
    LookupResponse with document and organization details if found

### Example


```python
import encypher
from encypher.models.lookup_request import LookupRequest
from encypher.models.lookup_response import LookupResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.LookupApi(api_client)
    lookup_request = encypher.LookupRequest() # LookupRequest | 

    try:
        # Lookup Sentence
        api_response = api_instance.lookup_sentence_api_v1_lookup_post(lookup_request)
        print("The response of LookupApi->lookup_sentence_api_v1_lookup_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LookupApi->lookup_sentence_api_v1_lookup_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lookup_request** | [**LookupRequest**](LookupRequest.md)|  | 

### Return type

[**LookupResponse**](LookupResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

