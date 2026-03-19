# encypher.AttestationPoliciesApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_policy_api_v1_attestation_policies_post**](AttestationPoliciesApi.md#create_policy_api_v1_attestation_policies_post) | **POST** /api/v1/attestation-policies/ | Create Policy
[**create_policy_api_v1_attestation_policies_post_0**](AttestationPoliciesApi.md#create_policy_api_v1_attestation_policies_post_0) | **POST** /api/v1/attestation-policies/ | Create Policy
[**delete_policy_api_v1_attestation_policies_policy_id_delete**](AttestationPoliciesApi.md#delete_policy_api_v1_attestation_policies_policy_id_delete) | **DELETE** /api/v1/attestation-policies/{policy_id} | Delete Policy
[**delete_policy_api_v1_attestation_policies_policy_id_delete_0**](AttestationPoliciesApi.md#delete_policy_api_v1_attestation_policies_policy_id_delete_0) | **DELETE** /api/v1/attestation-policies/{policy_id} | Delete Policy
[**get_policy_api_v1_attestation_policies_policy_id_get**](AttestationPoliciesApi.md#get_policy_api_v1_attestation_policies_policy_id_get) | **GET** /api/v1/attestation-policies/{policy_id} | Get Policy
[**get_policy_api_v1_attestation_policies_policy_id_get_0**](AttestationPoliciesApi.md#get_policy_api_v1_attestation_policies_policy_id_get_0) | **GET** /api/v1/attestation-policies/{policy_id} | Get Policy
[**list_attestations_api_v1_attestations_get**](AttestationPoliciesApi.md#list_attestations_api_v1_attestations_get) | **GET** /api/v1/attestations/ | List Attestations
[**list_attestations_api_v1_attestations_get_0**](AttestationPoliciesApi.md#list_attestations_api_v1_attestations_get_0) | **GET** /api/v1/attestations/ | List Attestations
[**list_policies_api_v1_attestation_policies_get**](AttestationPoliciesApi.md#list_policies_api_v1_attestation_policies_get) | **GET** /api/v1/attestation-policies/ | List Policies
[**list_policies_api_v1_attestation_policies_get_0**](AttestationPoliciesApi.md#list_policies_api_v1_attestation_policies_get_0) | **GET** /api/v1/attestation-policies/ | List Policies
[**update_policy_api_v1_attestation_policies_policy_id_put**](AttestationPoliciesApi.md#update_policy_api_v1_attestation_policies_policy_id_put) | **PUT** /api/v1/attestation-policies/{policy_id} | Update Policy
[**update_policy_api_v1_attestation_policies_policy_id_put_0**](AttestationPoliciesApi.md#update_policy_api_v1_attestation_policies_policy_id_put_0) | **PUT** /api/v1/attestation-policies/{policy_id} | Update Policy


# **create_policy_api_v1_attestation_policies_post**
> Dict[str, object] create_policy_api_v1_attestation_policies_post(create_policy_request)

Create Policy

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.create_policy_request import CreatePolicyRequest
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
    api_instance = encypher.AttestationPoliciesApi(api_client)
    create_policy_request = encypher.CreatePolicyRequest() # CreatePolicyRequest |

    try:
        # Create Policy
        api_response = api_instance.create_policy_api_v1_attestation_policies_post(create_policy_request)
        print("The response of AttestationPoliciesApi->create_policy_api_v1_attestation_policies_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttestationPoliciesApi->create_policy_api_v1_attestation_policies_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_policy_request** | [**CreatePolicyRequest**](CreatePolicyRequest.md)|  |

### Return type

**Dict[str, object]**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_policy_api_v1_attestation_policies_post_0**
> Dict[str, object] create_policy_api_v1_attestation_policies_post_0(create_policy_request)

Create Policy

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.create_policy_request import CreatePolicyRequest
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
    api_instance = encypher.AttestationPoliciesApi(api_client)
    create_policy_request = encypher.CreatePolicyRequest() # CreatePolicyRequest |

    try:
        # Create Policy
        api_response = api_instance.create_policy_api_v1_attestation_policies_post_0(create_policy_request)
        print("The response of AttestationPoliciesApi->create_policy_api_v1_attestation_policies_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttestationPoliciesApi->create_policy_api_v1_attestation_policies_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_policy_request** | [**CreatePolicyRequest**](CreatePolicyRequest.md)|  |

### Return type

**Dict[str, object]**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_policy_api_v1_attestation_policies_policy_id_delete**
> Dict[str, object] delete_policy_api_v1_attestation_policies_policy_id_delete(policy_id)

Delete Policy

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.AttestationPoliciesApi(api_client)
    policy_id = 'policy_id_example' # str |

    try:
        # Delete Policy
        api_response = api_instance.delete_policy_api_v1_attestation_policies_policy_id_delete(policy_id)
        print("The response of AttestationPoliciesApi->delete_policy_api_v1_attestation_policies_policy_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttestationPoliciesApi->delete_policy_api_v1_attestation_policies_policy_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **str**|  |

### Return type

**Dict[str, object]**

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

# **delete_policy_api_v1_attestation_policies_policy_id_delete_0**
> Dict[str, object] delete_policy_api_v1_attestation_policies_policy_id_delete_0(policy_id)

Delete Policy

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.AttestationPoliciesApi(api_client)
    policy_id = 'policy_id_example' # str |

    try:
        # Delete Policy
        api_response = api_instance.delete_policy_api_v1_attestation_policies_policy_id_delete_0(policy_id)
        print("The response of AttestationPoliciesApi->delete_policy_api_v1_attestation_policies_policy_id_delete_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttestationPoliciesApi->delete_policy_api_v1_attestation_policies_policy_id_delete_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **str**|  |

### Return type

**Dict[str, object]**

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

# **get_policy_api_v1_attestation_policies_policy_id_get**
> Dict[str, object] get_policy_api_v1_attestation_policies_policy_id_get(policy_id)

Get Policy

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.AttestationPoliciesApi(api_client)
    policy_id = 'policy_id_example' # str |

    try:
        # Get Policy
        api_response = api_instance.get_policy_api_v1_attestation_policies_policy_id_get(policy_id)
        print("The response of AttestationPoliciesApi->get_policy_api_v1_attestation_policies_policy_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttestationPoliciesApi->get_policy_api_v1_attestation_policies_policy_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **str**|  |

### Return type

**Dict[str, object]**

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

# **get_policy_api_v1_attestation_policies_policy_id_get_0**
> Dict[str, object] get_policy_api_v1_attestation_policies_policy_id_get_0(policy_id)

Get Policy

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.AttestationPoliciesApi(api_client)
    policy_id = 'policy_id_example' # str |

    try:
        # Get Policy
        api_response = api_instance.get_policy_api_v1_attestation_policies_policy_id_get_0(policy_id)
        print("The response of AttestationPoliciesApi->get_policy_api_v1_attestation_policies_policy_id_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttestationPoliciesApi->get_policy_api_v1_attestation_policies_policy_id_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **str**|  |

### Return type

**Dict[str, object]**

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

# **list_attestations_api_v1_attestations_get**
> Dict[str, object] list_attestations_api_v1_attestations_get(document_id=document_id, verdict=verdict, limit=limit, offset=offset)

List Attestations

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.AttestationPoliciesApi(api_client)
    document_id = 'document_id_example' # str |  (optional)
    verdict = 'verdict_example' # str |  (optional)
    limit = 50 # int |  (optional) (default to 50)
    offset = 0 # int |  (optional) (default to 0)

    try:
        # List Attestations
        api_response = api_instance.list_attestations_api_v1_attestations_get(document_id=document_id, verdict=verdict, limit=limit, offset=offset)
        print("The response of AttestationPoliciesApi->list_attestations_api_v1_attestations_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttestationPoliciesApi->list_attestations_api_v1_attestations_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | [optional]
 **verdict** | **str**|  | [optional]
 **limit** | **int**|  | [optional] [default to 50]
 **offset** | **int**|  | [optional] [default to 0]

### Return type

**Dict[str, object]**

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

# **list_attestations_api_v1_attestations_get_0**
> Dict[str, object] list_attestations_api_v1_attestations_get_0(document_id=document_id, verdict=verdict, limit=limit, offset=offset)

List Attestations

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.AttestationPoliciesApi(api_client)
    document_id = 'document_id_example' # str |  (optional)
    verdict = 'verdict_example' # str |  (optional)
    limit = 50 # int |  (optional) (default to 50)
    offset = 0 # int |  (optional) (default to 0)

    try:
        # List Attestations
        api_response = api_instance.list_attestations_api_v1_attestations_get_0(document_id=document_id, verdict=verdict, limit=limit, offset=offset)
        print("The response of AttestationPoliciesApi->list_attestations_api_v1_attestations_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttestationPoliciesApi->list_attestations_api_v1_attestations_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | [optional]
 **verdict** | **str**|  | [optional]
 **limit** | **int**|  | [optional] [default to 50]
 **offset** | **int**|  | [optional] [default to 0]

### Return type

**Dict[str, object]**

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

# **list_policies_api_v1_attestation_policies_get**
> Dict[str, object] list_policies_api_v1_attestation_policies_get(active=active)

List Policies

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.AttestationPoliciesApi(api_client)
    active = True # bool |  (optional)

    try:
        # List Policies
        api_response = api_instance.list_policies_api_v1_attestation_policies_get(active=active)
        print("The response of AttestationPoliciesApi->list_policies_api_v1_attestation_policies_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttestationPoliciesApi->list_policies_api_v1_attestation_policies_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **active** | **bool**|  | [optional]

### Return type

**Dict[str, object]**

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

# **list_policies_api_v1_attestation_policies_get_0**
> Dict[str, object] list_policies_api_v1_attestation_policies_get_0(active=active)

List Policies

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.AttestationPoliciesApi(api_client)
    active = True # bool |  (optional)

    try:
        # List Policies
        api_response = api_instance.list_policies_api_v1_attestation_policies_get_0(active=active)
        print("The response of AttestationPoliciesApi->list_policies_api_v1_attestation_policies_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttestationPoliciesApi->list_policies_api_v1_attestation_policies_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **active** | **bool**|  | [optional]

### Return type

**Dict[str, object]**

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

# **update_policy_api_v1_attestation_policies_policy_id_put**
> Dict[str, object] update_policy_api_v1_attestation_policies_policy_id_put(policy_id, update_policy_request)

Update Policy

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.update_policy_request import UpdatePolicyRequest
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
    api_instance = encypher.AttestationPoliciesApi(api_client)
    policy_id = 'policy_id_example' # str |
    update_policy_request = encypher.UpdatePolicyRequest() # UpdatePolicyRequest |

    try:
        # Update Policy
        api_response = api_instance.update_policy_api_v1_attestation_policies_policy_id_put(policy_id, update_policy_request)
        print("The response of AttestationPoliciesApi->update_policy_api_v1_attestation_policies_policy_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttestationPoliciesApi->update_policy_api_v1_attestation_policies_policy_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **str**|  |
 **update_policy_request** | [**UpdatePolicyRequest**](UpdatePolicyRequest.md)|  |

### Return type

**Dict[str, object]**

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

# **update_policy_api_v1_attestation_policies_policy_id_put_0**
> Dict[str, object] update_policy_api_v1_attestation_policies_policy_id_put_0(policy_id, update_policy_request)

Update Policy

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.update_policy_request import UpdatePolicyRequest
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
    api_instance = encypher.AttestationPoliciesApi(api_client)
    policy_id = 'policy_id_example' # str |
    update_policy_request = encypher.UpdatePolicyRequest() # UpdatePolicyRequest |

    try:
        # Update Policy
        api_response = api_instance.update_policy_api_v1_attestation_policies_policy_id_put_0(policy_id, update_policy_request)
        print("The response of AttestationPoliciesApi->update_policy_api_v1_attestation_policies_policy_id_put_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttestationPoliciesApi->update_policy_api_v1_attestation_policies_policy_id_put_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **str**|  |
 **update_policy_request** | [**UpdatePolicyRequest**](UpdatePolicyRequest.md)|  |

### Return type

**Dict[str, object]**

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
