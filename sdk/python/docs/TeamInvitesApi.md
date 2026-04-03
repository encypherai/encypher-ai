# encypher.TeamInvitesApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**accept_invite_new_user_api_v1_org_invites_public_token_accept_new_post**](TeamInvitesApi.md#accept_invite_new_user_api_v1_org_invites_public_token_accept_new_post) | **POST** /api/v1/org/invites/public/{token}/accept-new | Accept Invite New User
[**accept_invite_new_user_api_v1_org_invites_public_token_accept_new_post_0**](TeamInvitesApi.md#accept_invite_new_user_api_v1_org_invites_public_token_accept_new_post_0) | **POST** /api/v1/org/invites/public/{token}/accept-new | Accept Invite New User
[**get_public_invite_api_v1_org_invites_public_token_get**](TeamInvitesApi.md#get_public_invite_api_v1_org_invites_public_token_get) | **GET** /api/v1/org/invites/public/{token} | Get Public Invite
[**get_public_invite_api_v1_org_invites_public_token_get_0**](TeamInvitesApi.md#get_public_invite_api_v1_org_invites_public_token_get_0) | **GET** /api/v1/org/invites/public/{token} | Get Public Invite


# **accept_invite_new_user_api_v1_org_invites_public_token_accept_new_post**
> object accept_invite_new_user_api_v1_org_invites_public_token_accept_new_post(token, accept_invite_new_user_request)

Accept Invite New User

Accept a team invitation and create a new user account in one step.

- Validates the invite token
- Creates a new user account via auth-service internal endpoint (email auto-verified)
- Creates the org member record
- Marks the invite as accepted
- Returns access + refresh tokens so the dashboard can auto-login

Returns 409 if the email is already registered (frontend shows 'sign in instead').
Returns 404/410 if the invite is missing or expired.

### Example


```python
import encypher
from encypher.models.accept_invite_new_user_request import AcceptInviteNewUserRequest
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.TeamInvitesApi(api_client)
    token = 'token_example' # str |
    accept_invite_new_user_request = encypher.AcceptInviteNewUserRequest() # AcceptInviteNewUserRequest |

    try:
        # Accept Invite New User
        api_response = api_instance.accept_invite_new_user_api_v1_org_invites_public_token_accept_new_post(token, accept_invite_new_user_request)
        print("The response of TeamInvitesApi->accept_invite_new_user_api_v1_org_invites_public_token_accept_new_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamInvitesApi->accept_invite_new_user_api_v1_org_invites_public_token_accept_new_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**|  |
 **accept_invite_new_user_request** | [**AcceptInviteNewUserRequest**](AcceptInviteNewUserRequest.md)|  |

### Return type

**object**

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

# **accept_invite_new_user_api_v1_org_invites_public_token_accept_new_post_0**
> object accept_invite_new_user_api_v1_org_invites_public_token_accept_new_post_0(token, accept_invite_new_user_request)

Accept Invite New User

Accept a team invitation and create a new user account in one step.

- Validates the invite token
- Creates a new user account via auth-service internal endpoint (email auto-verified)
- Creates the org member record
- Marks the invite as accepted
- Returns access + refresh tokens so the dashboard can auto-login

Returns 409 if the email is already registered (frontend shows 'sign in instead').
Returns 404/410 if the invite is missing or expired.

### Example


```python
import encypher
from encypher.models.accept_invite_new_user_request import AcceptInviteNewUserRequest
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.TeamInvitesApi(api_client)
    token = 'token_example' # str |
    accept_invite_new_user_request = encypher.AcceptInviteNewUserRequest() # AcceptInviteNewUserRequest |

    try:
        # Accept Invite New User
        api_response = api_instance.accept_invite_new_user_api_v1_org_invites_public_token_accept_new_post_0(token, accept_invite_new_user_request)
        print("The response of TeamInvitesApi->accept_invite_new_user_api_v1_org_invites_public_token_accept_new_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamInvitesApi->accept_invite_new_user_api_v1_org_invites_public_token_accept_new_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**|  |
 **accept_invite_new_user_request** | [**AcceptInviteNewUserRequest**](AcceptInviteNewUserRequest.md)|  |

### Return type

**object**

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

# **get_public_invite_api_v1_org_invites_public_token_get**
> object get_public_invite_api_v1_org_invites_public_token_get(token)

Get Public Invite

Return invite metadata for a pending team invitation (no auth required).

Used by the /invite/team/[token] dashboard page to render invite details
before the user is logged in.

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.TeamInvitesApi(api_client)
    token = 'token_example' # str |

    try:
        # Get Public Invite
        api_response = api_instance.get_public_invite_api_v1_org_invites_public_token_get(token)
        print("The response of TeamInvitesApi->get_public_invite_api_v1_org_invites_public_token_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamInvitesApi->get_public_invite_api_v1_org_invites_public_token_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**|  |

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

# **get_public_invite_api_v1_org_invites_public_token_get_0**
> object get_public_invite_api_v1_org_invites_public_token_get_0(token)

Get Public Invite

Return invite metadata for a pending team invitation (no auth required).

Used by the /invite/team/[token] dashboard page to render invite details
before the user is logged in.

### Example


```python
import encypher
from encypher.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.encypher.com
# See configuration.py for a list of all supported configuration parameters.
configuration = encypher.Configuration(
    host = "https://api.encypher.com"
)


# Enter a context with an instance of the API client
with encypher.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = encypher.TeamInvitesApi(api_client)
    token = 'token_example' # str |

    try:
        # Get Public Invite
        api_response = api_instance.get_public_invite_api_v1_org_invites_public_token_get_0(token)
        print("The response of TeamInvitesApi->get_public_invite_api_v1_org_invites_public_token_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamInvitesApi->get_public_invite_api_v1_org_invites_public_token_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**|  |

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
