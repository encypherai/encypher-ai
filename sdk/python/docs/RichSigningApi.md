# encypher.RichSigningApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**sign_rich_content_api_v1_sign_rich_post**](RichSigningApi.md#sign_rich_content_api_v1_sign_rich_post) | **POST** /api/v1/sign/rich | Sign rich article (text + images) with C2PA


# **sign_rich_content_api_v1_sign_rich_post**
> object sign_rich_content_api_v1_sign_rich_post(rich_article_sign_request)

Sign rich article (text + images) with C2PA

Sign a rich article containing both text and embedded images as a single
atomic provenance unit.

Each image receives a standalone C2PA JUMBF-embedded manifest. The article-level
composite manifest binds text (via Merkle root) and all images (via ingredient
references) into a single provenance record.

**Tier feature matrix:**

| Feature | Free | Enterprise |
|---------|------|------------|
| Basic image C2PA signing | Yes | Yes |
| pHash attribution indexing | Yes | Yes |
| TrustMark neural watermark | No | Yes |

**Quota:** Each call consumes (N_images + 1 text + 1 composite) signatures.

**Images:** Up to 20 images per request. Each image is base64-encoded in the
request body and returned base64-encoded in the response. Publishers are
responsible for hosting signed images on their own CDN.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.rich_article_sign_request import RichArticleSignRequest
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
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
    api_instance = encypher.RichSigningApi(api_client)
    rich_article_sign_request = encypher.RichArticleSignRequest() # RichArticleSignRequest |

    try:
        # Sign rich article (text + images) with C2PA
        api_response = api_instance.sign_rich_content_api_v1_sign_rich_post(rich_article_sign_request)
        print("The response of RichSigningApi->sign_rich_content_api_v1_sign_rich_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RichSigningApi->sign_rich_content_api_v1_sign_rich_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rich_article_sign_request** | [**RichArticleSignRequest**](RichArticleSignRequest.md)|  |

### Return type

**object**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Article signed successfully |  -  |
**400** | Invalid request (bad image data, unsupported MIME type) |  -  |
**403** | Feature requires higher tier or insufficient quota |  -  |
**422** | Image signing or text signing failed |  -  |
**429** | Rate limit exceeded |  -  |
**503** | Signing credentials not configured |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
