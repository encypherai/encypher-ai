# \TeamManagementApi

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



## accept_invite_api_v1_org_members_accept_invite_post

> serde_json::Value accept_invite_api_v1_org_members_accept_invite_post(token, user_id)
Accept Invite

Accept a team invitation.  This endpoint is called after the user authenticates.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**token** | **String** | Invitation token | [required] |
**user_id** | **String** | User ID of the accepting user | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## accept_invite_api_v1_org_members_accept_invite_post_0

> serde_json::Value accept_invite_api_v1_org_members_accept_invite_post_0(token, user_id)
Accept Invite

Accept a team invitation.  This endpoint is called after the user authenticates.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**token** | **String** | Invitation token | [required] |
**user_id** | **String** | User ID of the accepting user | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## invite_member_api_v1_org_members_invite_post

> models::InviteResponse invite_member_api_v1_org_members_invite_post(invite_request)
Invite Member

Invite a new member to the organization.  Sends an email invitation that expires in 7 days.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**invite_request** | [**InviteRequest**](InviteRequest.md) |  | [required] |

### Return type

[**models::InviteResponse**](InviteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## invite_member_api_v1_org_members_invite_post_0

> models::InviteResponse invite_member_api_v1_org_members_invite_post_0(invite_request)
Invite Member

Invite a new member to the organization.  Sends an email invitation that expires in 7 days.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**invite_request** | [**InviteRequest**](InviteRequest.md) |  | [required] |

### Return type

[**models::InviteResponse**](InviteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_pending_invites_api_v1_org_members_invites_get

> Vec<models::PendingInvite> list_pending_invites_api_v1_org_members_invites_get()
List Pending Invites

List all pending invitations.

### Parameters

This endpoint does not need any parameter.

### Return type

[**Vec<models::PendingInvite>**](PendingInvite.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_pending_invites_api_v1_org_members_invites_get_0

> Vec<models::PendingInvite> list_pending_invites_api_v1_org_members_invites_get_0()
List Pending Invites

List all pending invitations.

### Parameters

This endpoint does not need any parameter.

### Return type

[**Vec<models::PendingInvite>**](PendingInvite.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_team_members_api_v1_org_members_get

> models::TeamMemberListResponse list_team_members_api_v1_org_members_get()
List Team Members

List all team members in the organization.

### Parameters

This endpoint does not need any parameter.

### Return type

[**models::TeamMemberListResponse**](TeamMemberListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_team_members_api_v1_org_members_get_0

> models::TeamMemberListResponse list_team_members_api_v1_org_members_get_0()
List Team Members

List all team members in the organization.

### Parameters

This endpoint does not need any parameter.

### Return type

[**models::TeamMemberListResponse**](TeamMemberListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## remove_member_api_v1_org_members_member_id_delete

> serde_json::Value remove_member_api_v1_org_members_member_id_delete(member_id)
Remove Member

Remove a team member from the organization.  Cannot remove the owner.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**member_id** | **String** |  | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## remove_member_api_v1_org_members_member_id_delete_0

> serde_json::Value remove_member_api_v1_org_members_member_id_delete_0(member_id)
Remove Member

Remove a team member from the organization.  Cannot remove the owner.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**member_id** | **String** |  | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## revoke_invite_api_v1_org_members_invites_invite_id_delete

> serde_json::Value revoke_invite_api_v1_org_members_invites_invite_id_delete(invite_id)
Revoke Invite

Revoke a pending invitation.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**invite_id** | **String** |  | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## revoke_invite_api_v1_org_members_invites_invite_id_delete_0

> serde_json::Value revoke_invite_api_v1_org_members_invites_invite_id_delete_0(invite_id)
Revoke Invite

Revoke a pending invitation.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**invite_id** | **String** |  | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## update_member_role_api_v1_org_members_member_id_role_patch

> serde_json::Value update_member_role_api_v1_org_members_member_id_role_patch(member_id, update_role_request)
Update Member Role

Update a team member's role.  Admins can change roles of members and viewers. Only owners can change admin roles.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**member_id** | **String** |  | [required] |
**update_role_request** | [**UpdateRoleRequest**](UpdateRoleRequest.md) |  | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## update_member_role_api_v1_org_members_member_id_role_patch_0

> serde_json::Value update_member_role_api_v1_org_members_member_id_role_patch_0(member_id, update_role_request)
Update Member Role

Update a team member's role.  Admins can change roles of members and viewers. Only owners can change admin roles.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**member_id** | **String** |  | [required] |
**update_role_request** | [**UpdateRoleRequest**](UpdateRoleRequest.md) |  | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

