# encypher.PartnerApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulk_provision_publishers_api_v1_partner_publishers_provision_post**](PartnerApi.md#bulk_provision_publishers_api_v1_partner_publishers_provision_post) | **POST** /api/v1/partner/publishers/provision | Bulk-provision publisher organizations
[**bulk_provision_publishers_api_v1_partner_publishers_provision_post_0**](PartnerApi.md#bulk_provision_publishers_api_v1_partner_publishers_provision_post_0) | **POST** /api/v1/partner/publishers/provision | Bulk-provision publisher organizations


# **bulk_provision_publishers_api_v1_partner_publishers_provision_post**
> object bulk_provision_publishers_api_v1_partner_publishers_provision_post(partner_bulk_provision_request)

Bulk-provision publisher organizations

Platform partners (strategic_partner tier) can provision up to 1000 publisher organizations in a single call. Each publisher gets a free-tier org, a rights profile using the specified template, and a partner-branded claim email.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.partner_bulk_provision_request import PartnerBulkProvisionRequest
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
    api_instance = encypher.PartnerApi(api_client)
    partner_bulk_provision_request = encypher.PartnerBulkProvisionRequest() # PartnerBulkProvisionRequest |

    try:
        # Bulk-provision publisher organizations
        api_response = api_instance.bulk_provision_publishers_api_v1_partner_publishers_provision_post(partner_bulk_provision_request)
        print("The response of PartnerApi->bulk_provision_publishers_api_v1_partner_publishers_provision_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartnerApi->bulk_provision_publishers_api_v1_partner_publishers_provision_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **partner_bulk_provision_request** | [**PartnerBulkProvisionRequest**](PartnerBulkProvisionRequest.md)|  |

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **bulk_provision_publishers_api_v1_partner_publishers_provision_post_0**
> object bulk_provision_publishers_api_v1_partner_publishers_provision_post_0(partner_bulk_provision_request)

Bulk-provision publisher organizations

Platform partners (strategic_partner tier) can provision up to 1000 publisher organizations in a single call. Each publisher gets a free-tier org, a rights profile using the specified template, and a partner-branded claim email.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.partner_bulk_provision_request import PartnerBulkProvisionRequest
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
    api_instance = encypher.PartnerApi(api_client)
    partner_bulk_provision_request = encypher.PartnerBulkProvisionRequest() # PartnerBulkProvisionRequest |

    try:
        # Bulk-provision publisher organizations
        api_response = api_instance.bulk_provision_publishers_api_v1_partner_publishers_provision_post_0(partner_bulk_provision_request)
        print("The response of PartnerApi->bulk_provision_publishers_api_v1_partner_publishers_provision_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PartnerApi->bulk_provision_publishers_api_v1_partner_publishers_provision_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **partner_bulk_provision_request** | [**PartnerBulkProvisionRequest**](PartnerBulkProvisionRequest.md)|  |

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
