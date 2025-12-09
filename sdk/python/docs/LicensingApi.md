# encypher.LicensingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_agreement_api_v1_licensing_agreements_post**](LicensingApi.md#create_agreement_api_v1_licensing_agreements_post) | **POST** /api/v1/licensing/agreements | Create Agreement
[**create_agreement_api_v1_licensing_agreements_post_0**](LicensingApi.md#create_agreement_api_v1_licensing_agreements_post_0) | **POST** /api/v1/licensing/agreements | Create Agreement
[**create_revenue_distribution_api_v1_licensing_distributions_post**](LicensingApi.md#create_revenue_distribution_api_v1_licensing_distributions_post) | **POST** /api/v1/licensing/distributions | Create Revenue Distribution
[**create_revenue_distribution_api_v1_licensing_distributions_post_0**](LicensingApi.md#create_revenue_distribution_api_v1_licensing_distributions_post_0) | **POST** /api/v1/licensing/distributions | Create Revenue Distribution
[**get_agreement_api_v1_licensing_agreements_agreement_id_get**](LicensingApi.md#get_agreement_api_v1_licensing_agreements_agreement_id_get) | **GET** /api/v1/licensing/agreements/{agreement_id} | Get Agreement
[**get_agreement_api_v1_licensing_agreements_agreement_id_get_0**](LicensingApi.md#get_agreement_api_v1_licensing_agreements_agreement_id_get_0) | **GET** /api/v1/licensing/agreements/{agreement_id} | Get Agreement
[**get_distribution_api_v1_licensing_distributions_distribution_id_get**](LicensingApi.md#get_distribution_api_v1_licensing_distributions_distribution_id_get) | **GET** /api/v1/licensing/distributions/{distribution_id} | Get Distribution
[**get_distribution_api_v1_licensing_distributions_distribution_id_get_0**](LicensingApi.md#get_distribution_api_v1_licensing_distributions_distribution_id_get_0) | **GET** /api/v1/licensing/distributions/{distribution_id} | Get Distribution
[**list_agreements_api_v1_licensing_agreements_get**](LicensingApi.md#list_agreements_api_v1_licensing_agreements_get) | **GET** /api/v1/licensing/agreements | List Agreements
[**list_agreements_api_v1_licensing_agreements_get_0**](LicensingApi.md#list_agreements_api_v1_licensing_agreements_get_0) | **GET** /api/v1/licensing/agreements | List Agreements
[**list_available_content_api_v1_licensing_content_get**](LicensingApi.md#list_available_content_api_v1_licensing_content_get) | **GET** /api/v1/licensing/content | List Available Content
[**list_available_content_api_v1_licensing_content_get_0**](LicensingApi.md#list_available_content_api_v1_licensing_content_get_0) | **GET** /api/v1/licensing/content | List Available Content
[**list_distributions_api_v1_licensing_distributions_get**](LicensingApi.md#list_distributions_api_v1_licensing_distributions_get) | **GET** /api/v1/licensing/distributions | List Distributions
[**list_distributions_api_v1_licensing_distributions_get_0**](LicensingApi.md#list_distributions_api_v1_licensing_distributions_get_0) | **GET** /api/v1/licensing/distributions | List Distributions
[**process_payouts_api_v1_licensing_payouts_post**](LicensingApi.md#process_payouts_api_v1_licensing_payouts_post) | **POST** /api/v1/licensing/payouts | Process Payouts
[**process_payouts_api_v1_licensing_payouts_post_0**](LicensingApi.md#process_payouts_api_v1_licensing_payouts_post_0) | **POST** /api/v1/licensing/payouts | Process Payouts
[**terminate_agreement_api_v1_licensing_agreements_agreement_id_delete**](LicensingApi.md#terminate_agreement_api_v1_licensing_agreements_agreement_id_delete) | **DELETE** /api/v1/licensing/agreements/{agreement_id} | Terminate Agreement
[**terminate_agreement_api_v1_licensing_agreements_agreement_id_delete_0**](LicensingApi.md#terminate_agreement_api_v1_licensing_agreements_agreement_id_delete_0) | **DELETE** /api/v1/licensing/agreements/{agreement_id} | Terminate Agreement
[**track_content_access_api_v1_licensing_track_access_post**](LicensingApi.md#track_content_access_api_v1_licensing_track_access_post) | **POST** /api/v1/licensing/track-access | Track Content Access
[**track_content_access_api_v1_licensing_track_access_post_0**](LicensingApi.md#track_content_access_api_v1_licensing_track_access_post_0) | **POST** /api/v1/licensing/track-access | Track Content Access
[**update_agreement_api_v1_licensing_agreements_agreement_id_patch**](LicensingApi.md#update_agreement_api_v1_licensing_agreements_agreement_id_patch) | **PATCH** /api/v1/licensing/agreements/{agreement_id} | Update Agreement
[**update_agreement_api_v1_licensing_agreements_agreement_id_patch_0**](LicensingApi.md#update_agreement_api_v1_licensing_agreements_agreement_id_patch_0) | **PATCH** /api/v1/licensing/agreements/{agreement_id} | Update Agreement


# **create_agreement_api_v1_licensing_agreements_post**
> LicensingAgreementCreateResponse create_agreement_api_v1_licensing_agreements_post(licensing_agreement_create)

Create Agreement

Create a new licensing agreement with an AI company.

**Admin only** - Creates agreement and generates API key for AI company.

Returns:
    Agreement details including the API key (only shown once)

### Example


```python
import encypher
from encypher.models.licensing_agreement_create import LicensingAgreementCreate
from encypher.models.licensing_agreement_create_response import LicensingAgreementCreateResponse
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
    api_instance = encypher.LicensingApi(api_client)
    licensing_agreement_create = encypher.LicensingAgreementCreate() # LicensingAgreementCreate | 

    try:
        # Create Agreement
        api_response = api_instance.create_agreement_api_v1_licensing_agreements_post(licensing_agreement_create)
        print("The response of LicensingApi->create_agreement_api_v1_licensing_agreements_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->create_agreement_api_v1_licensing_agreements_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **licensing_agreement_create** | [**LicensingAgreementCreate**](LicensingAgreementCreate.md)|  | 

### Return type

[**LicensingAgreementCreateResponse**](LicensingAgreementCreateResponse.md)

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

# **create_agreement_api_v1_licensing_agreements_post_0**
> LicensingAgreementCreateResponse create_agreement_api_v1_licensing_agreements_post_0(licensing_agreement_create)

Create Agreement

Create a new licensing agreement with an AI company.

**Admin only** - Creates agreement and generates API key for AI company.

Returns:
    Agreement details including the API key (only shown once)

### Example


```python
import encypher
from encypher.models.licensing_agreement_create import LicensingAgreementCreate
from encypher.models.licensing_agreement_create_response import LicensingAgreementCreateResponse
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
    api_instance = encypher.LicensingApi(api_client)
    licensing_agreement_create = encypher.LicensingAgreementCreate() # LicensingAgreementCreate | 

    try:
        # Create Agreement
        api_response = api_instance.create_agreement_api_v1_licensing_agreements_post_0(licensing_agreement_create)
        print("The response of LicensingApi->create_agreement_api_v1_licensing_agreements_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->create_agreement_api_v1_licensing_agreements_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **licensing_agreement_create** | [**LicensingAgreementCreate**](LicensingAgreementCreate.md)|  | 

### Return type

[**LicensingAgreementCreateResponse**](LicensingAgreementCreateResponse.md)

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

# **create_revenue_distribution_api_v1_licensing_distributions_post**
> RevenueDistributionResponse create_revenue_distribution_api_v1_licensing_distributions_post(revenue_distribution_create)

Create Revenue Distribution

Create revenue distribution for a period.

**Admin only** - Calculates and creates revenue distribution based on
content access during the specified period. Implements 70/30 split.

### Example


```python
import encypher
from encypher.models.revenue_distribution_create import RevenueDistributionCreate
from encypher.models.revenue_distribution_response import RevenueDistributionResponse
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
    api_instance = encypher.LicensingApi(api_client)
    revenue_distribution_create = encypher.RevenueDistributionCreate() # RevenueDistributionCreate | 

    try:
        # Create Revenue Distribution
        api_response = api_instance.create_revenue_distribution_api_v1_licensing_distributions_post(revenue_distribution_create)
        print("The response of LicensingApi->create_revenue_distribution_api_v1_licensing_distributions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->create_revenue_distribution_api_v1_licensing_distributions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **revenue_distribution_create** | [**RevenueDistributionCreate**](RevenueDistributionCreate.md)|  | 

### Return type

[**RevenueDistributionResponse**](RevenueDistributionResponse.md)

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

# **create_revenue_distribution_api_v1_licensing_distributions_post_0**
> RevenueDistributionResponse create_revenue_distribution_api_v1_licensing_distributions_post_0(revenue_distribution_create)

Create Revenue Distribution

Create revenue distribution for a period.

**Admin only** - Calculates and creates revenue distribution based on
content access during the specified period. Implements 70/30 split.

### Example


```python
import encypher
from encypher.models.revenue_distribution_create import RevenueDistributionCreate
from encypher.models.revenue_distribution_response import RevenueDistributionResponse
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
    api_instance = encypher.LicensingApi(api_client)
    revenue_distribution_create = encypher.RevenueDistributionCreate() # RevenueDistributionCreate | 

    try:
        # Create Revenue Distribution
        api_response = api_instance.create_revenue_distribution_api_v1_licensing_distributions_post_0(revenue_distribution_create)
        print("The response of LicensingApi->create_revenue_distribution_api_v1_licensing_distributions_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->create_revenue_distribution_api_v1_licensing_distributions_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **revenue_distribution_create** | [**RevenueDistributionCreate**](RevenueDistributionCreate.md)|  | 

### Return type

[**RevenueDistributionResponse**](RevenueDistributionResponse.md)

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

# **get_agreement_api_v1_licensing_agreements_agreement_id_get**
> LicensingAgreementResponse get_agreement_api_v1_licensing_agreements_agreement_id_get(agreement_id)

Get Agreement

Get details of a specific licensing agreement.

**Admin only**

### Example


```python
import encypher
from encypher.models.licensing_agreement_response import LicensingAgreementResponse
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
    api_instance = encypher.LicensingApi(api_client)
    agreement_id = 'agreement_id_example' # str | 

    try:
        # Get Agreement
        api_response = api_instance.get_agreement_api_v1_licensing_agreements_agreement_id_get(agreement_id)
        print("The response of LicensingApi->get_agreement_api_v1_licensing_agreements_agreement_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->get_agreement_api_v1_licensing_agreements_agreement_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agreement_id** | **str**|  | 

### Return type

[**LicensingAgreementResponse**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_agreement_api_v1_licensing_agreements_agreement_id_get_0**
> LicensingAgreementResponse get_agreement_api_v1_licensing_agreements_agreement_id_get_0(agreement_id)

Get Agreement

Get details of a specific licensing agreement.

**Admin only**

### Example


```python
import encypher
from encypher.models.licensing_agreement_response import LicensingAgreementResponse
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
    api_instance = encypher.LicensingApi(api_client)
    agreement_id = 'agreement_id_example' # str | 

    try:
        # Get Agreement
        api_response = api_instance.get_agreement_api_v1_licensing_agreements_agreement_id_get_0(agreement_id)
        print("The response of LicensingApi->get_agreement_api_v1_licensing_agreements_agreement_id_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->get_agreement_api_v1_licensing_agreements_agreement_id_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agreement_id** | **str**|  | 

### Return type

[**LicensingAgreementResponse**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_distribution_api_v1_licensing_distributions_distribution_id_get**
> RevenueDistributionResponse get_distribution_api_v1_licensing_distributions_distribution_id_get(distribution_id)

Get Distribution

Get details of a revenue distribution.

**Admin only** - Includes breakdown of member revenues.

### Example


```python
import encypher
from encypher.models.revenue_distribution_response import RevenueDistributionResponse
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
    api_instance = encypher.LicensingApi(api_client)
    distribution_id = 'distribution_id_example' # str | 

    try:
        # Get Distribution
        api_response = api_instance.get_distribution_api_v1_licensing_distributions_distribution_id_get(distribution_id)
        print("The response of LicensingApi->get_distribution_api_v1_licensing_distributions_distribution_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->get_distribution_api_v1_licensing_distributions_distribution_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **distribution_id** | **str**|  | 

### Return type

[**RevenueDistributionResponse**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_distribution_api_v1_licensing_distributions_distribution_id_get_0**
> RevenueDistributionResponse get_distribution_api_v1_licensing_distributions_distribution_id_get_0(distribution_id)

Get Distribution

Get details of a revenue distribution.

**Admin only** - Includes breakdown of member revenues.

### Example


```python
import encypher
from encypher.models.revenue_distribution_response import RevenueDistributionResponse
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
    api_instance = encypher.LicensingApi(api_client)
    distribution_id = 'distribution_id_example' # str | 

    try:
        # Get Distribution
        api_response = api_instance.get_distribution_api_v1_licensing_distributions_distribution_id_get_0(distribution_id)
        print("The response of LicensingApi->get_distribution_api_v1_licensing_distributions_distribution_id_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->get_distribution_api_v1_licensing_distributions_distribution_id_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **distribution_id** | **str**|  | 

### Return type

[**RevenueDistributionResponse**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_agreements_api_v1_licensing_agreements_get**
> List[LicensingAgreementResponse] list_agreements_api_v1_licensing_agreements_get(status=status, limit=limit, offset=offset)

List Agreements

List all licensing agreements.

**Admin only** - Returns all agreements with optional filtering.

### Example


```python
import encypher
from encypher.models.agreement_status import AgreementStatus
from encypher.models.licensing_agreement_response import LicensingAgreementResponse
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
    api_instance = encypher.LicensingApi(api_client)
    status = encypher.AgreementStatus() # AgreementStatus | Filter by status (optional)
    limit = 100 # int | Results per page (optional) (default to 100)
    offset = 0 # int | Pagination offset (optional) (default to 0)

    try:
        # List Agreements
        api_response = api_instance.list_agreements_api_v1_licensing_agreements_get(status=status, limit=limit, offset=offset)
        print("The response of LicensingApi->list_agreements_api_v1_licensing_agreements_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->list_agreements_api_v1_licensing_agreements_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | [**AgreementStatus**](.md)| Filter by status | [optional] 
 **limit** | **int**| Results per page | [optional] [default to 100]
 **offset** | **int**| Pagination offset | [optional] [default to 0]

### Return type

[**List[LicensingAgreementResponse]**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_agreements_api_v1_licensing_agreements_get_0**
> List[LicensingAgreementResponse] list_agreements_api_v1_licensing_agreements_get_0(status=status, limit=limit, offset=offset)

List Agreements

List all licensing agreements.

**Admin only** - Returns all agreements with optional filtering.

### Example


```python
import encypher
from encypher.models.agreement_status import AgreementStatus
from encypher.models.licensing_agreement_response import LicensingAgreementResponse
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
    api_instance = encypher.LicensingApi(api_client)
    status = encypher.AgreementStatus() # AgreementStatus | Filter by status (optional)
    limit = 100 # int | Results per page (optional) (default to 100)
    offset = 0 # int | Pagination offset (optional) (default to 0)

    try:
        # List Agreements
        api_response = api_instance.list_agreements_api_v1_licensing_agreements_get_0(status=status, limit=limit, offset=offset)
        print("The response of LicensingApi->list_agreements_api_v1_licensing_agreements_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->list_agreements_api_v1_licensing_agreements_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | [**AgreementStatus**](.md)| Filter by status | [optional] 
 **limit** | **int**| Results per page | [optional] [default to 100]
 **offset** | **int**| Pagination offset | [optional] [default to 0]

### Return type

[**List[LicensingAgreementResponse]**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_available_content_api_v1_licensing_content_get**
> ContentListResponse list_available_content_api_v1_licensing_content_get(content_type=content_type, min_word_count=min_word_count, limit=limit, offset=offset)

List Available Content

List available content for licensed AI company.

**Requires AI company API key** - Returns content metadata that matches
the terms of active licensing agreements.

Headers:
    Authorization: Bearer lic_abc123...

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.content_list_response import ContentListResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
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
    api_instance = encypher.LicensingApi(api_client)
    content_type = 'content_type_example' # str | Filter by content type (optional)
    min_word_count = 56 # int | Minimum word count (optional)
    limit = 100 # int | Results per page (optional) (default to 100)
    offset = 0 # int | Pagination offset (optional) (default to 0)

    try:
        # List Available Content
        api_response = api_instance.list_available_content_api_v1_licensing_content_get(content_type=content_type, min_word_count=min_word_count, limit=limit, offset=offset)
        print("The response of LicensingApi->list_available_content_api_v1_licensing_content_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->list_available_content_api_v1_licensing_content_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **content_type** | **str**| Filter by content type | [optional] 
 **min_word_count** | **int**| Minimum word count | [optional] 
 **limit** | **int**| Results per page | [optional] [default to 100]
 **offset** | **int**| Pagination offset | [optional] [default to 0]

### Return type

[**ContentListResponse**](ContentListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_available_content_api_v1_licensing_content_get_0**
> ContentListResponse list_available_content_api_v1_licensing_content_get_0(content_type=content_type, min_word_count=min_word_count, limit=limit, offset=offset)

List Available Content

List available content for licensed AI company.

**Requires AI company API key** - Returns content metadata that matches
the terms of active licensing agreements.

Headers:
    Authorization: Bearer lic_abc123...

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.content_list_response import ContentListResponse
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
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
    api_instance = encypher.LicensingApi(api_client)
    content_type = 'content_type_example' # str | Filter by content type (optional)
    min_word_count = 56 # int | Minimum word count (optional)
    limit = 100 # int | Results per page (optional) (default to 100)
    offset = 0 # int | Pagination offset (optional) (default to 0)

    try:
        # List Available Content
        api_response = api_instance.list_available_content_api_v1_licensing_content_get_0(content_type=content_type, min_word_count=min_word_count, limit=limit, offset=offset)
        print("The response of LicensingApi->list_available_content_api_v1_licensing_content_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->list_available_content_api_v1_licensing_content_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **content_type** | **str**| Filter by content type | [optional] 
 **min_word_count** | **int**| Minimum word count | [optional] 
 **limit** | **int**| Results per page | [optional] [default to 100]
 **offset** | **int**| Pagination offset | [optional] [default to 0]

### Return type

[**ContentListResponse**](ContentListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_distributions_api_v1_licensing_distributions_get**
> List[RevenueDistributionResponse] list_distributions_api_v1_licensing_distributions_get(agreement_id=agreement_id, status=status, limit=limit, offset=offset)

List Distributions

List revenue distributions.

**Admin only** - Returns all distributions with optional filtering.

### Example


```python
import encypher
from encypher.models.distribution_status import DistributionStatus
from encypher.models.revenue_distribution_response import RevenueDistributionResponse
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
    api_instance = encypher.LicensingApi(api_client)
    agreement_id = 'agreement_id_example' # str | Filter by agreement (optional)
    status = encypher.DistributionStatus() # DistributionStatus | Filter by status (optional)
    limit = 100 # int | Results per page (optional) (default to 100)
    offset = 0 # int | Pagination offset (optional) (default to 0)

    try:
        # List Distributions
        api_response = api_instance.list_distributions_api_v1_licensing_distributions_get(agreement_id=agreement_id, status=status, limit=limit, offset=offset)
        print("The response of LicensingApi->list_distributions_api_v1_licensing_distributions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->list_distributions_api_v1_licensing_distributions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agreement_id** | **str**| Filter by agreement | [optional] 
 **status** | [**DistributionStatus**](.md)| Filter by status | [optional] 
 **limit** | **int**| Results per page | [optional] [default to 100]
 **offset** | **int**| Pagination offset | [optional] [default to 0]

### Return type

[**List[RevenueDistributionResponse]**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_distributions_api_v1_licensing_distributions_get_0**
> List[RevenueDistributionResponse] list_distributions_api_v1_licensing_distributions_get_0(agreement_id=agreement_id, status=status, limit=limit, offset=offset)

List Distributions

List revenue distributions.

**Admin only** - Returns all distributions with optional filtering.

### Example


```python
import encypher
from encypher.models.distribution_status import DistributionStatus
from encypher.models.revenue_distribution_response import RevenueDistributionResponse
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
    api_instance = encypher.LicensingApi(api_client)
    agreement_id = 'agreement_id_example' # str | Filter by agreement (optional)
    status = encypher.DistributionStatus() # DistributionStatus | Filter by status (optional)
    limit = 100 # int | Results per page (optional) (default to 100)
    offset = 0 # int | Pagination offset (optional) (default to 0)

    try:
        # List Distributions
        api_response = api_instance.list_distributions_api_v1_licensing_distributions_get_0(agreement_id=agreement_id, status=status, limit=limit, offset=offset)
        print("The response of LicensingApi->list_distributions_api_v1_licensing_distributions_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->list_distributions_api_v1_licensing_distributions_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agreement_id** | **str**| Filter by agreement | [optional] 
 **status** | [**DistributionStatus**](.md)| Filter by status | [optional] 
 **limit** | **int**| Results per page | [optional] [default to 100]
 **offset** | **int**| Pagination offset | [optional] [default to 0]

### Return type

[**List[RevenueDistributionResponse]**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **process_payouts_api_v1_licensing_payouts_post**
> PayoutResponse process_payouts_api_v1_licensing_payouts_post(payout_create)

Process Payouts

Process payouts for a revenue distribution.

**Admin only** - Initiates payment processing for all members in a distribution.

Note: This is currently a simulation. In production, this would integrate
with Stripe or other payment processors.

### Example


```python
import encypher
from encypher.models.payout_create import PayoutCreate
from encypher.models.payout_response import PayoutResponse
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
    api_instance = encypher.LicensingApi(api_client)
    payout_create = encypher.PayoutCreate() # PayoutCreate | 

    try:
        # Process Payouts
        api_response = api_instance.process_payouts_api_v1_licensing_payouts_post(payout_create)
        print("The response of LicensingApi->process_payouts_api_v1_licensing_payouts_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->process_payouts_api_v1_licensing_payouts_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **payout_create** | [**PayoutCreate**](PayoutCreate.md)|  | 

### Return type

[**PayoutResponse**](PayoutResponse.md)

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

# **process_payouts_api_v1_licensing_payouts_post_0**
> PayoutResponse process_payouts_api_v1_licensing_payouts_post_0(payout_create)

Process Payouts

Process payouts for a revenue distribution.

**Admin only** - Initiates payment processing for all members in a distribution.

Note: This is currently a simulation. In production, this would integrate
with Stripe or other payment processors.

### Example


```python
import encypher
from encypher.models.payout_create import PayoutCreate
from encypher.models.payout_response import PayoutResponse
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
    api_instance = encypher.LicensingApi(api_client)
    payout_create = encypher.PayoutCreate() # PayoutCreate | 

    try:
        # Process Payouts
        api_response = api_instance.process_payouts_api_v1_licensing_payouts_post_0(payout_create)
        print("The response of LicensingApi->process_payouts_api_v1_licensing_payouts_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->process_payouts_api_v1_licensing_payouts_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **payout_create** | [**PayoutCreate**](PayoutCreate.md)|  | 

### Return type

[**PayoutResponse**](PayoutResponse.md)

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

# **terminate_agreement_api_v1_licensing_agreements_agreement_id_delete**
> SuccessResponse terminate_agreement_api_v1_licensing_agreements_agreement_id_delete(agreement_id)

Terminate Agreement

Terminate a licensing agreement.

**Admin only** - Sets agreement status to terminated.

### Example


```python
import encypher
from encypher.models.success_response import SuccessResponse
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
    api_instance = encypher.LicensingApi(api_client)
    agreement_id = 'agreement_id_example' # str | 

    try:
        # Terminate Agreement
        api_response = api_instance.terminate_agreement_api_v1_licensing_agreements_agreement_id_delete(agreement_id)
        print("The response of LicensingApi->terminate_agreement_api_v1_licensing_agreements_agreement_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->terminate_agreement_api_v1_licensing_agreements_agreement_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agreement_id** | **str**|  | 

### Return type

[**SuccessResponse**](SuccessResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **terminate_agreement_api_v1_licensing_agreements_agreement_id_delete_0**
> SuccessResponse terminate_agreement_api_v1_licensing_agreements_agreement_id_delete_0(agreement_id)

Terminate Agreement

Terminate a licensing agreement.

**Admin only** - Sets agreement status to terminated.

### Example


```python
import encypher
from encypher.models.success_response import SuccessResponse
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
    api_instance = encypher.LicensingApi(api_client)
    agreement_id = 'agreement_id_example' # str | 

    try:
        # Terminate Agreement
        api_response = api_instance.terminate_agreement_api_v1_licensing_agreements_agreement_id_delete_0(agreement_id)
        print("The response of LicensingApi->terminate_agreement_api_v1_licensing_agreements_agreement_id_delete_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->terminate_agreement_api_v1_licensing_agreements_agreement_id_delete_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agreement_id** | **str**|  | 

### Return type

[**SuccessResponse**](SuccessResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **track_content_access_api_v1_licensing_track_access_post**
> ContentAccessLogResponse track_content_access_api_v1_licensing_track_access_post(content_access_track)

Track Content Access

Track content access by AI company.

**Requires AI company API key** - Logs when content is accessed for
revenue attribution.

Headers:
    Authorization: Bearer lic_abc123...

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.content_access_log_response import ContentAccessLogResponse
from encypher.models.content_access_track import ContentAccessTrack
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
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
    api_instance = encypher.LicensingApi(api_client)
    content_access_track = encypher.ContentAccessTrack() # ContentAccessTrack | 

    try:
        # Track Content Access
        api_response = api_instance.track_content_access_api_v1_licensing_track_access_post(content_access_track)
        print("The response of LicensingApi->track_content_access_api_v1_licensing_track_access_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->track_content_access_api_v1_licensing_track_access_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **content_access_track** | [**ContentAccessTrack**](ContentAccessTrack.md)|  | 

### Return type

[**ContentAccessLogResponse**](ContentAccessLogResponse.md)

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

# **track_content_access_api_v1_licensing_track_access_post_0**
> ContentAccessLogResponse track_content_access_api_v1_licensing_track_access_post_0(content_access_track)

Track Content Access

Track content access by AI company.

**Requires AI company API key** - Logs when content is accessed for
revenue attribution.

Headers:
    Authorization: Bearer lic_abc123...

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.content_access_log_response import ContentAccessLogResponse
from encypher.models.content_access_track import ContentAccessTrack
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "http://localhost"
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
    api_instance = encypher.LicensingApi(api_client)
    content_access_track = encypher.ContentAccessTrack() # ContentAccessTrack | 

    try:
        # Track Content Access
        api_response = api_instance.track_content_access_api_v1_licensing_track_access_post_0(content_access_track)
        print("The response of LicensingApi->track_content_access_api_v1_licensing_track_access_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->track_content_access_api_v1_licensing_track_access_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **content_access_track** | [**ContentAccessTrack**](ContentAccessTrack.md)|  | 

### Return type

[**ContentAccessLogResponse**](ContentAccessLogResponse.md)

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

# **update_agreement_api_v1_licensing_agreements_agreement_id_patch**
> LicensingAgreementResponse update_agreement_api_v1_licensing_agreements_agreement_id_patch(agreement_id, licensing_agreement_update)

Update Agreement

Update a licensing agreement.

**Admin only** - Allows updating agreement terms and status.

### Example


```python
import encypher
from encypher.models.licensing_agreement_response import LicensingAgreementResponse
from encypher.models.licensing_agreement_update import LicensingAgreementUpdate
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
    api_instance = encypher.LicensingApi(api_client)
    agreement_id = 'agreement_id_example' # str | 
    licensing_agreement_update = encypher.LicensingAgreementUpdate() # LicensingAgreementUpdate | 

    try:
        # Update Agreement
        api_response = api_instance.update_agreement_api_v1_licensing_agreements_agreement_id_patch(agreement_id, licensing_agreement_update)
        print("The response of LicensingApi->update_agreement_api_v1_licensing_agreements_agreement_id_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->update_agreement_api_v1_licensing_agreements_agreement_id_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agreement_id** | **str**|  | 
 **licensing_agreement_update** | [**LicensingAgreementUpdate**](LicensingAgreementUpdate.md)|  | 

### Return type

[**LicensingAgreementResponse**](LicensingAgreementResponse.md)

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

# **update_agreement_api_v1_licensing_agreements_agreement_id_patch_0**
> LicensingAgreementResponse update_agreement_api_v1_licensing_agreements_agreement_id_patch_0(agreement_id, licensing_agreement_update)

Update Agreement

Update a licensing agreement.

**Admin only** - Allows updating agreement terms and status.

### Example


```python
import encypher
from encypher.models.licensing_agreement_response import LicensingAgreementResponse
from encypher.models.licensing_agreement_update import LicensingAgreementUpdate
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
    api_instance = encypher.LicensingApi(api_client)
    agreement_id = 'agreement_id_example' # str | 
    licensing_agreement_update = encypher.LicensingAgreementUpdate() # LicensingAgreementUpdate | 

    try:
        # Update Agreement
        api_response = api_instance.update_agreement_api_v1_licensing_agreements_agreement_id_patch_0(agreement_id, licensing_agreement_update)
        print("The response of LicensingApi->update_agreement_api_v1_licensing_agreements_agreement_id_patch_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LicensingApi->update_agreement_api_v1_licensing_agreements_agreement_id_patch_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agreement_id** | **str**|  | 
 **licensing_agreement_update** | [**LicensingAgreementUpdate**](LicensingAgreementUpdate.md)|  | 

### Return type

[**LicensingAgreementResponse**](LicensingAgreementResponse.md)

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

