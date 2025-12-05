# encypher.TeamManagementApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**accept_invite_api_v1_org_members_accept_invite_post**](TeamManagementApi.md#accept_invite_api_v1_org_members_accept_invite_post) | **POST** /api/v1/org/members/accept-invite | Accept Invite
[**accept_invite_api_v1_org_members_accept_invite_post_0**](TeamManagementApi.md#accept_invite_api_v1_org_members_accept_invite_post_0) | **POST** /api/v1/org/members/accept-invite | Accept Invite
[**invite_member_api_v1_org_members_invite_post**](TeamManagementApi.md#invite_member_api_v1_org_members_invite_post) | **POST** /api/v1/org/members/invite | Invite Member
[**invite_member_api_v1_org_members_invite_post_0**](TeamManagementApi.md#invite_member_api_v1_org_members_invite_post_0) | **POST** /api/v1/org/members/invite | Invite Member
[**list_pending_invites_api_v1_org_members_invites_get**](TeamManagementApi.md#list_pending_invites_api_v1_org_members_invites_get) | **GET** /api/v1/org/members/invites | List Pending Invites
[**list_pending_invites_api_v1_org_members_invites_get_0**](TeamManagementApi.md#list_pending_invites_api_v1_org_members_invites_get_0) | **GET** /api/v1/org/members/invites | List Pending Invites
[**list_team_members_api_v1_org_members_get**](TeamManagementApi.md#list_team_members_api_v1_org_members_get) | **GET** /api/v1/org/members | List Team Members
[**list_team_members_api_v1_org_members_get_0**](TeamManagementApi.md#list_team_members_api_v1_org_members_get_0) | **GET** /api/v1/org/members | List Team Members
[**remove_member_api_v1_org_members_member_id_delete**](TeamManagementApi.md#remove_member_api_v1_org_members_member_id_delete) | **DELETE** /api/v1/org/members/{member_id} | Remove Member
[**remove_member_api_v1_org_members_member_id_delete_0**](TeamManagementApi.md#remove_member_api_v1_org_members_member_id_delete_0) | **DELETE** /api/v1/org/members/{member_id} | Remove Member
[**revoke_invite_api_v1_org_members_invites_invite_id_delete**](TeamManagementApi.md#revoke_invite_api_v1_org_members_invites_invite_id_delete) | **DELETE** /api/v1/org/members/invites/{invite_id} | Revoke Invite
[**revoke_invite_api_v1_org_members_invites_invite_id_delete_0**](TeamManagementApi.md#revoke_invite_api_v1_org_members_invites_invite_id_delete_0) | **DELETE** /api/v1/org/members/invites/{invite_id} | Revoke Invite
[**update_member_role_api_v1_org_members_member_id_role_patch**](TeamManagementApi.md#update_member_role_api_v1_org_members_member_id_role_patch) | **PATCH** /api/v1/org/members/{member_id}/role | Update Member Role
[**update_member_role_api_v1_org_members_member_id_role_patch_0**](TeamManagementApi.md#update_member_role_api_v1_org_members_member_id_role_patch_0) | **PATCH** /api/v1/org/members/{member_id}/role | Update Member Role


# **accept_invite_api_v1_org_members_accept_invite_post**
> object accept_invite_api_v1_org_members_accept_invite_post(token, user_id)

Accept Invite

Accept a team invitation.

This endpoint is called after the user authenticates.

### Example


```python
import encypher
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
    api_instance = encypher.TeamManagementApi(api_client)
    token = 'token_example' # str | Invitation token
    user_id = 'user_id_example' # str | User ID of the accepting user

    try:
        # Accept Invite
        api_response = api_instance.accept_invite_api_v1_org_members_accept_invite_post(token, user_id)
        print("The response of TeamManagementApi->accept_invite_api_v1_org_members_accept_invite_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamManagementApi->accept_invite_api_v1_org_members_accept_invite_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| Invitation token | 
 **user_id** | **str**| User ID of the accepting user | 

### Return type

**object**

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

# **accept_invite_api_v1_org_members_accept_invite_post_0**
> object accept_invite_api_v1_org_members_accept_invite_post_0(token, user_id)

Accept Invite

Accept a team invitation.

This endpoint is called after the user authenticates.

### Example


```python
import encypher
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
    api_instance = encypher.TeamManagementApi(api_client)
    token = 'token_example' # str | Invitation token
    user_id = 'user_id_example' # str | User ID of the accepting user

    try:
        # Accept Invite
        api_response = api_instance.accept_invite_api_v1_org_members_accept_invite_post_0(token, user_id)
        print("The response of TeamManagementApi->accept_invite_api_v1_org_members_accept_invite_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamManagementApi->accept_invite_api_v1_org_members_accept_invite_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| Invitation token | 
 **user_id** | **str**| User ID of the accepting user | 

### Return type

**object**

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

# **invite_member_api_v1_org_members_invite_post**
> InviteResponse invite_member_api_v1_org_members_invite_post(invite_request)

Invite Member

Invite a new member to the organization.

Sends an email invitation that expires in 7 days.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.invite_request import InviteRequest
from encypher.models.invite_response import InviteResponse
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
    api_instance = encypher.TeamManagementApi(api_client)
    invite_request = encypher.InviteRequest() # InviteRequest | 

    try:
        # Invite Member
        api_response = api_instance.invite_member_api_v1_org_members_invite_post(invite_request)
        print("The response of TeamManagementApi->invite_member_api_v1_org_members_invite_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamManagementApi->invite_member_api_v1_org_members_invite_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invite_request** | [**InviteRequest**](InviteRequest.md)|  | 

### Return type

[**InviteResponse**](InviteResponse.md)

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

# **invite_member_api_v1_org_members_invite_post_0**
> InviteResponse invite_member_api_v1_org_members_invite_post_0(invite_request)

Invite Member

Invite a new member to the organization.

Sends an email invitation that expires in 7 days.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.invite_request import InviteRequest
from encypher.models.invite_response import InviteResponse
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
    api_instance = encypher.TeamManagementApi(api_client)
    invite_request = encypher.InviteRequest() # InviteRequest | 

    try:
        # Invite Member
        api_response = api_instance.invite_member_api_v1_org_members_invite_post_0(invite_request)
        print("The response of TeamManagementApi->invite_member_api_v1_org_members_invite_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamManagementApi->invite_member_api_v1_org_members_invite_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invite_request** | [**InviteRequest**](InviteRequest.md)|  | 

### Return type

[**InviteResponse**](InviteResponse.md)

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

# **list_pending_invites_api_v1_org_members_invites_get**
> List[PendingInvite] list_pending_invites_api_v1_org_members_invites_get()

List Pending Invites

List all pending invitations.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.pending_invite import PendingInvite
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
    api_instance = encypher.TeamManagementApi(api_client)

    try:
        # List Pending Invites
        api_response = api_instance.list_pending_invites_api_v1_org_members_invites_get()
        print("The response of TeamManagementApi->list_pending_invites_api_v1_org_members_invites_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamManagementApi->list_pending_invites_api_v1_org_members_invites_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[PendingInvite]**](PendingInvite.md)

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

# **list_pending_invites_api_v1_org_members_invites_get_0**
> List[PendingInvite] list_pending_invites_api_v1_org_members_invites_get_0()

List Pending Invites

List all pending invitations.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.pending_invite import PendingInvite
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
    api_instance = encypher.TeamManagementApi(api_client)

    try:
        # List Pending Invites
        api_response = api_instance.list_pending_invites_api_v1_org_members_invites_get_0()
        print("The response of TeamManagementApi->list_pending_invites_api_v1_org_members_invites_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamManagementApi->list_pending_invites_api_v1_org_members_invites_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[PendingInvite]**](PendingInvite.md)

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

# **list_team_members_api_v1_org_members_get**
> TeamMemberListResponse list_team_members_api_v1_org_members_get()

List Team Members

List all team members in the organization.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.team_member_list_response import TeamMemberListResponse
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
    api_instance = encypher.TeamManagementApi(api_client)

    try:
        # List Team Members
        api_response = api_instance.list_team_members_api_v1_org_members_get()
        print("The response of TeamManagementApi->list_team_members_api_v1_org_members_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamManagementApi->list_team_members_api_v1_org_members_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**TeamMemberListResponse**](TeamMemberListResponse.md)

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

# **list_team_members_api_v1_org_members_get_0**
> TeamMemberListResponse list_team_members_api_v1_org_members_get_0()

List Team Members

List all team members in the organization.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.team_member_list_response import TeamMemberListResponse
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
    api_instance = encypher.TeamManagementApi(api_client)

    try:
        # List Team Members
        api_response = api_instance.list_team_members_api_v1_org_members_get_0()
        print("The response of TeamManagementApi->list_team_members_api_v1_org_members_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamManagementApi->list_team_members_api_v1_org_members_get_0: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**TeamMemberListResponse**](TeamMemberListResponse.md)

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

# **remove_member_api_v1_org_members_member_id_delete**
> object remove_member_api_v1_org_members_member_id_delete(member_id)

Remove Member

Remove a team member from the organization.

Cannot remove the owner.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.TeamManagementApi(api_client)
    member_id = 'member_id_example' # str | 

    try:
        # Remove Member
        api_response = api_instance.remove_member_api_v1_org_members_member_id_delete(member_id)
        print("The response of TeamManagementApi->remove_member_api_v1_org_members_member_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamManagementApi->remove_member_api_v1_org_members_member_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **member_id** | **str**|  | 

### Return type

**object**

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

# **remove_member_api_v1_org_members_member_id_delete_0**
> object remove_member_api_v1_org_members_member_id_delete_0(member_id)

Remove Member

Remove a team member from the organization.

Cannot remove the owner.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.TeamManagementApi(api_client)
    member_id = 'member_id_example' # str | 

    try:
        # Remove Member
        api_response = api_instance.remove_member_api_v1_org_members_member_id_delete_0(member_id)
        print("The response of TeamManagementApi->remove_member_api_v1_org_members_member_id_delete_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamManagementApi->remove_member_api_v1_org_members_member_id_delete_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **member_id** | **str**|  | 

### Return type

**object**

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

# **revoke_invite_api_v1_org_members_invites_invite_id_delete**
> object revoke_invite_api_v1_org_members_invites_invite_id_delete(invite_id)

Revoke Invite

Revoke a pending invitation.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.TeamManagementApi(api_client)
    invite_id = 'invite_id_example' # str | 

    try:
        # Revoke Invite
        api_response = api_instance.revoke_invite_api_v1_org_members_invites_invite_id_delete(invite_id)
        print("The response of TeamManagementApi->revoke_invite_api_v1_org_members_invites_invite_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamManagementApi->revoke_invite_api_v1_org_members_invites_invite_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invite_id** | **str**|  | 

### Return type

**object**

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

# **revoke_invite_api_v1_org_members_invites_invite_id_delete_0**
> object revoke_invite_api_v1_org_members_invites_invite_id_delete_0(invite_id)

Revoke Invite

Revoke a pending invitation.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
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
    api_instance = encypher.TeamManagementApi(api_client)
    invite_id = 'invite_id_example' # str | 

    try:
        # Revoke Invite
        api_response = api_instance.revoke_invite_api_v1_org_members_invites_invite_id_delete_0(invite_id)
        print("The response of TeamManagementApi->revoke_invite_api_v1_org_members_invites_invite_id_delete_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamManagementApi->revoke_invite_api_v1_org_members_invites_invite_id_delete_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invite_id** | **str**|  | 

### Return type

**object**

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

# **update_member_role_api_v1_org_members_member_id_role_patch**
> object update_member_role_api_v1_org_members_member_id_role_patch(member_id, update_role_request)

Update Member Role

Update a team member's role.

Admins can change roles of members and viewers.
Only owners can change admin roles.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.update_role_request import UpdateRoleRequest
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
    api_instance = encypher.TeamManagementApi(api_client)
    member_id = 'member_id_example' # str | 
    update_role_request = encypher.UpdateRoleRequest() # UpdateRoleRequest | 

    try:
        # Update Member Role
        api_response = api_instance.update_member_role_api_v1_org_members_member_id_role_patch(member_id, update_role_request)
        print("The response of TeamManagementApi->update_member_role_api_v1_org_members_member_id_role_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamManagementApi->update_member_role_api_v1_org_members_member_id_role_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **member_id** | **str**|  | 
 **update_role_request** | [**UpdateRoleRequest**](UpdateRoleRequest.md)|  | 

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

# **update_member_role_api_v1_org_members_member_id_role_patch_0**
> object update_member_role_api_v1_org_members_member_id_role_patch_0(member_id, update_role_request)

Update Member Role

Update a team member's role.

Admins can change roles of members and viewers.
Only owners can change admin roles.

### Example

* Bearer Authentication (HTTPBearer):

```python
import encypher
from encypher.models.update_role_request import UpdateRoleRequest
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
    api_instance = encypher.TeamManagementApi(api_client)
    member_id = 'member_id_example' # str | 
    update_role_request = encypher.UpdateRoleRequest() # UpdateRoleRequest | 

    try:
        # Update Member Role
        api_response = api_instance.update_member_role_api_v1_org_members_member_id_role_patch_0(member_id, update_role_request)
        print("The response of TeamManagementApi->update_member_role_api_v1_org_members_member_id_role_patch_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamManagementApi->update_member_role_api_v1_org_members_member_id_role_patch_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **member_id** | **str**|  | 
 **update_role_request** | [**UpdateRoleRequest**](UpdateRoleRequest.md)|  | 

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

