# encypher.FormalNoticesApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_formal_notice_api_v1_notices_create_post**](FormalNoticesApi.md#create_formal_notice_api_v1_notices_create_post) | **POST** /api/v1/notices/create | Create a formal notice
[**create_formal_notice_api_v1_notices_create_post_0**](FormalNoticesApi.md#create_formal_notice_api_v1_notices_create_post_0) | **POST** /api/v1/notices/create | Create a formal notice
[**deliver_notice_api_v1_notices_notice_id_deliver_post**](FormalNoticesApi.md#deliver_notice_api_v1_notices_notice_id_deliver_post) | **POST** /api/v1/notices/{notice_id}/deliver | Deliver a formal notice
[**deliver_notice_api_v1_notices_notice_id_deliver_post_0**](FormalNoticesApi.md#deliver_notice_api_v1_notices_notice_id_deliver_post_0) | **POST** /api/v1/notices/{notice_id}/deliver | Deliver a formal notice
[**get_evidence_package_api_v1_notices_notice_id_evidence_get**](FormalNoticesApi.md#get_evidence_package_api_v1_notices_notice_id_evidence_get) | **GET** /api/v1/notices/{notice_id}/evidence | Generate court-ready evidence package
[**get_evidence_package_api_v1_notices_notice_id_evidence_get_0**](FormalNoticesApi.md#get_evidence_package_api_v1_notices_notice_id_evidence_get_0) | **GET** /api/v1/notices/{notice_id}/evidence | Generate court-ready evidence package
[**get_evidence_package_pdf_api_v1_notices_notice_id_evidence_pdf_get**](FormalNoticesApi.md#get_evidence_package_pdf_api_v1_notices_notice_id_evidence_pdf_get) | **GET** /api/v1/notices/{notice_id}/evidence/pdf | Download court-ready evidence package as PDF
[**get_evidence_package_pdf_api_v1_notices_notice_id_evidence_pdf_get_0**](FormalNoticesApi.md#get_evidence_package_pdf_api_v1_notices_notice_id_evidence_pdf_get_0) | **GET** /api/v1/notices/{notice_id}/evidence/pdf | Download court-ready evidence package as PDF
[**get_formal_notice_api_v1_notices_notice_id_get**](FormalNoticesApi.md#get_formal_notice_api_v1_notices_notice_id_get) | **GET** /api/v1/notices/{notice_id} | Get notice details and delivery status
[**get_formal_notice_api_v1_notices_notice_id_get_0**](FormalNoticesApi.md#get_formal_notice_api_v1_notices_notice_id_get_0) | **GET** /api/v1/notices/{notice_id} | Get notice details and delivery status
[**list_notices_api_v1_notices_get**](FormalNoticesApi.md#list_notices_api_v1_notices_get) | **GET** /api/v1/notices/ | List formal notices for the organization
[**list_notices_api_v1_notices_get_0**](FormalNoticesApi.md#list_notices_api_v1_notices_get_0) | **GET** /api/v1/notices/ | List formal notices for the organization


# **create_formal_notice_api_v1_notices_create_post**
> Dict[str, object] create_formal_notice_api_v1_notices_create_post(request_body)

Create a formal notice

Create a formal notice for an AI company or other entity.

The notice text is SHA-256 hashed on creation. Once delivered, the content is
cryptographically locked and cannot be changed. Every event in the notice
lifecycle is recorded in an append-only evidence chain.

**Notice types:**
- `licensing_notice` — Informational notice that content is registered
- `cease_and_desist` — Legal demand to stop using content without license
- `dmca_takedown` — DMCA formal takedown notice
- `formal_awareness` — Formal record that the entity is aware of rights

Requires: Organization admin.

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
    api_instance = encypher.FormalNoticesApi(api_client)
    request_body = None # Dict[str, object] |

    try:
        # Create a formal notice
        api_response = api_instance.create_formal_notice_api_v1_notices_create_post(request_body)
        print("The response of FormalNoticesApi->create_formal_notice_api_v1_notices_create_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormalNoticesApi->create_formal_notice_api_v1_notices_create_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**Dict[str, object]**](object.md)|  |

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

# **create_formal_notice_api_v1_notices_create_post_0**
> Dict[str, object] create_formal_notice_api_v1_notices_create_post_0(request_body)

Create a formal notice

Create a formal notice for an AI company or other entity.

The notice text is SHA-256 hashed on creation. Once delivered, the content is
cryptographically locked and cannot be changed. Every event in the notice
lifecycle is recorded in an append-only evidence chain.

**Notice types:**
- `licensing_notice` — Informational notice that content is registered
- `cease_and_desist` — Legal demand to stop using content without license
- `dmca_takedown` — DMCA formal takedown notice
- `formal_awareness` — Formal record that the entity is aware of rights

Requires: Organization admin.

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
    api_instance = encypher.FormalNoticesApi(api_client)
    request_body = None # Dict[str, object] |

    try:
        # Create a formal notice
        api_response = api_instance.create_formal_notice_api_v1_notices_create_post_0(request_body)
        print("The response of FormalNoticesApi->create_formal_notice_api_v1_notices_create_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormalNoticesApi->create_formal_notice_api_v1_notices_create_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**Dict[str, object]**](object.md)|  |

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

# **deliver_notice_api_v1_notices_notice_id_deliver_post**
> Dict[str, object] deliver_notice_api_v1_notices_notice_id_deliver_post(notice_id, request_body=request_body)

Deliver a formal notice

Deliver the formal notice via available channels (email, API, registered mail).

**Once a notice is delivered:**
1. Its content is cryptographically locked (notice_text and notice_hash cannot change)
2. A delivery receipt is generated with timestamp and cryptographic proof
3. The delivery event is appended to the evidence chain

Delivery methods:
- `email` — Send via Encypher notification service
- `api` — Record as API-delivered (recipient must acknowledge via API)
- `registered_mail` — Record manual registered mail delivery

Returns delivery receipt with timestamp and cryptographic proof.

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
    api_instance = encypher.FormalNoticesApi(api_client)
    notice_id = 'notice_id_example' # str | Notice UUID
    request_body = None # Dict[str, object] |  (optional)

    try:
        # Deliver a formal notice
        api_response = api_instance.deliver_notice_api_v1_notices_notice_id_deliver_post(notice_id, request_body=request_body)
        print("The response of FormalNoticesApi->deliver_notice_api_v1_notices_notice_id_deliver_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormalNoticesApi->deliver_notice_api_v1_notices_notice_id_deliver_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notice_id** | **str**| Notice UUID |
 **request_body** | [**Dict[str, object]**](object.md)|  | [optional]

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

# **deliver_notice_api_v1_notices_notice_id_deliver_post_0**
> Dict[str, object] deliver_notice_api_v1_notices_notice_id_deliver_post_0(notice_id, request_body=request_body)

Deliver a formal notice

Deliver the formal notice via available channels (email, API, registered mail).

**Once a notice is delivered:**
1. Its content is cryptographically locked (notice_text and notice_hash cannot change)
2. A delivery receipt is generated with timestamp and cryptographic proof
3. The delivery event is appended to the evidence chain

Delivery methods:
- `email` — Send via Encypher notification service
- `api` — Record as API-delivered (recipient must acknowledge via API)
- `registered_mail` — Record manual registered mail delivery

Returns delivery receipt with timestamp and cryptographic proof.

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
    api_instance = encypher.FormalNoticesApi(api_client)
    notice_id = 'notice_id_example' # str | Notice UUID
    request_body = None # Dict[str, object] |  (optional)

    try:
        # Deliver a formal notice
        api_response = api_instance.deliver_notice_api_v1_notices_notice_id_deliver_post_0(notice_id, request_body=request_body)
        print("The response of FormalNoticesApi->deliver_notice_api_v1_notices_notice_id_deliver_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormalNoticesApi->deliver_notice_api_v1_notices_notice_id_deliver_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notice_id** | **str**| Notice UUID |
 **request_body** | [**Dict[str, object]**](object.md)|  | [optional]

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

# **get_evidence_package_api_v1_notices_notice_id_evidence_get**
> Dict[str, object] get_evidence_package_api_v1_notices_notice_id_evidence_get(notice_id)

Generate court-ready evidence package

Generate a court-ready evidence package proving:
1. Content was cryptographically signed (original signed content with Merkle proofs)
2. Formal notice was created with specific content (notice hash)
3. Notice was delivered with confirmed receipt (delivery chain)
4. Rights terms were in effect at time of signing (rights snapshot)
5. Complete chain-of-custody documentation

The evidence package includes:
- Original signed content with C2PA manifest references
- Formal notice with SHA-256 hash
- Full evidence chain with each event's hash (tamper-evident linked list)
- Delivery confirmation with timestamp
- Rights terms at time of signing

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
    api_instance = encypher.FormalNoticesApi(api_client)
    notice_id = 'notice_id_example' # str | Notice UUID

    try:
        # Generate court-ready evidence package
        api_response = api_instance.get_evidence_package_api_v1_notices_notice_id_evidence_get(notice_id)
        print("The response of FormalNoticesApi->get_evidence_package_api_v1_notices_notice_id_evidence_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormalNoticesApi->get_evidence_package_api_v1_notices_notice_id_evidence_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notice_id** | **str**| Notice UUID |

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

# **get_evidence_package_api_v1_notices_notice_id_evidence_get_0**
> Dict[str, object] get_evidence_package_api_v1_notices_notice_id_evidence_get_0(notice_id)

Generate court-ready evidence package

Generate a court-ready evidence package proving:
1. Content was cryptographically signed (original signed content with Merkle proofs)
2. Formal notice was created with specific content (notice hash)
3. Notice was delivered with confirmed receipt (delivery chain)
4. Rights terms were in effect at time of signing (rights snapshot)
5. Complete chain-of-custody documentation

The evidence package includes:
- Original signed content with C2PA manifest references
- Formal notice with SHA-256 hash
- Full evidence chain with each event's hash (tamper-evident linked list)
- Delivery confirmation with timestamp
- Rights terms at time of signing

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
    api_instance = encypher.FormalNoticesApi(api_client)
    notice_id = 'notice_id_example' # str | Notice UUID

    try:
        # Generate court-ready evidence package
        api_response = api_instance.get_evidence_package_api_v1_notices_notice_id_evidence_get_0(notice_id)
        print("The response of FormalNoticesApi->get_evidence_package_api_v1_notices_notice_id_evidence_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormalNoticesApi->get_evidence_package_api_v1_notices_notice_id_evidence_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notice_id** | **str**| Notice UUID |

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

# **get_evidence_package_pdf_api_v1_notices_notice_id_evidence_pdf_get**
> get_evidence_package_pdf_api_v1_notices_notice_id_evidence_pdf_get(notice_id)

Download court-ready evidence package as PDF

Generate and download an Encypher-branded PDF evidence package for the notice.

The PDF contains:
- Cover page with issuing org, recipient, scope, and notice details
- Notice text with SHA-256 hash and verification status
- Full evidence chain table (tamper-evident linked list)

Suitable for attachment to legal correspondence or submission to media law clinics.

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
    api_instance = encypher.FormalNoticesApi(api_client)
    notice_id = 'notice_id_example' # str | Notice UUID

    try:
        # Download court-ready evidence package as PDF
        api_instance.get_evidence_package_pdf_api_v1_notices_notice_id_evidence_pdf_get(notice_id)
    except Exception as e:
        print("Exception when calling FormalNoticesApi->get_evidence_package_pdf_api_v1_notices_notice_id_evidence_pdf_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notice_id** | **str**| Notice UUID |

### Return type

void (empty response body)

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

# **get_evidence_package_pdf_api_v1_notices_notice_id_evidence_pdf_get_0**
> get_evidence_package_pdf_api_v1_notices_notice_id_evidence_pdf_get_0(notice_id)

Download court-ready evidence package as PDF

Generate and download an Encypher-branded PDF evidence package for the notice.

The PDF contains:
- Cover page with issuing org, recipient, scope, and notice details
- Notice text with SHA-256 hash and verification status
- Full evidence chain table (tamper-evident linked list)

Suitable for attachment to legal correspondence or submission to media law clinics.

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
    api_instance = encypher.FormalNoticesApi(api_client)
    notice_id = 'notice_id_example' # str | Notice UUID

    try:
        # Download court-ready evidence package as PDF
        api_instance.get_evidence_package_pdf_api_v1_notices_notice_id_evidence_pdf_get_0(notice_id)
    except Exception as e:
        print("Exception when calling FormalNoticesApi->get_evidence_package_pdf_api_v1_notices_notice_id_evidence_pdf_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notice_id** | **str**| Notice UUID |

### Return type

void (empty response body)

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

# **get_formal_notice_api_v1_notices_notice_id_get**
> Dict[str, object] get_formal_notice_api_v1_notices_notice_id_get(notice_id)

Get notice details and delivery status

Retrieve a formal notice with its full cryptographic proof, delivery confirmations,
and response history.

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
    api_instance = encypher.FormalNoticesApi(api_client)
    notice_id = 'notice_id_example' # str | Notice UUID

    try:
        # Get notice details and delivery status
        api_response = api_instance.get_formal_notice_api_v1_notices_notice_id_get(notice_id)
        print("The response of FormalNoticesApi->get_formal_notice_api_v1_notices_notice_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormalNoticesApi->get_formal_notice_api_v1_notices_notice_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notice_id** | **str**| Notice UUID |

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

# **get_formal_notice_api_v1_notices_notice_id_get_0**
> Dict[str, object] get_formal_notice_api_v1_notices_notice_id_get_0(notice_id)

Get notice details and delivery status

Retrieve a formal notice with its full cryptographic proof, delivery confirmations,
and response history.

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
    api_instance = encypher.FormalNoticesApi(api_client)
    notice_id = 'notice_id_example' # str | Notice UUID

    try:
        # Get notice details and delivery status
        api_response = api_instance.get_formal_notice_api_v1_notices_notice_id_get_0(notice_id)
        print("The response of FormalNoticesApi->get_formal_notice_api_v1_notices_notice_id_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormalNoticesApi->get_formal_notice_api_v1_notices_notice_id_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notice_id** | **str**| Notice UUID |

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

# **list_notices_api_v1_notices_get**
> List[Optional[Dict[str, object]]] list_notices_api_v1_notices_get()

List formal notices for the organization

Retrieve all formal notices issued by the authenticated organization, ordered by creation date (most recent first). Use the notice ID to fetch full evidence chain details.

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
    api_instance = encypher.FormalNoticesApi(api_client)

    try:
        # List formal notices for the organization
        api_response = api_instance.list_notices_api_v1_notices_get()
        print("The response of FormalNoticesApi->list_notices_api_v1_notices_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormalNoticesApi->list_notices_api_v1_notices_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**List[Optional[Dict[str, object]]]**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_notices_api_v1_notices_get_0**
> List[Optional[Dict[str, object]]] list_notices_api_v1_notices_get_0()

List formal notices for the organization

Retrieve all formal notices issued by the authenticated organization, ordered by creation date (most recent first). Use the notice ID to fetch full evidence chain details.

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
    api_instance = encypher.FormalNoticesApi(api_client)

    try:
        # List formal notices for the organization
        api_response = api_instance.list_notices_api_v1_notices_get_0()
        print("The response of FormalNoticesApi->list_notices_api_v1_notices_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormalNoticesApi->list_notices_api_v1_notices_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**List[Optional[Dict[str, object]]]**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
