# TeamManagementApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**acceptInviteApiV1OrgMembersAcceptInvitePost**](TeamManagementApi.md#acceptinviteapiv1orgmembersacceptinvitepost) | **POST** /api/v1/org/members/accept-invite | Accept Invite |
| [**acceptInviteApiV1OrgMembersAcceptInvitePost_0**](TeamManagementApi.md#acceptinviteapiv1orgmembersacceptinvitepost_0) | **POST** /api/v1/org/members/accept-invite | Accept Invite |
| [**inviteMemberApiV1OrgMembersInvitePost**](TeamManagementApi.md#invitememberapiv1orgmembersinvitepost) | **POST** /api/v1/org/members/invite | Invite Member |
| [**inviteMemberApiV1OrgMembersInvitePost_0**](TeamManagementApi.md#invitememberapiv1orgmembersinvitepost_0) | **POST** /api/v1/org/members/invite | Invite Member |
| [**listPendingInvitesApiV1OrgMembersInvitesGet**](TeamManagementApi.md#listpendinginvitesapiv1orgmembersinvitesget) | **GET** /api/v1/org/members/invites | List Pending Invites |
| [**listPendingInvitesApiV1OrgMembersInvitesGet_0**](TeamManagementApi.md#listpendinginvitesapiv1orgmembersinvitesget_0) | **GET** /api/v1/org/members/invites | List Pending Invites |
| [**listTeamMembersApiV1OrgMembersGet**](TeamManagementApi.md#listteammembersapiv1orgmembersget) | **GET** /api/v1/org/members | List Team Members |
| [**listTeamMembersApiV1OrgMembersGet_0**](TeamManagementApi.md#listteammembersapiv1orgmembersget_0) | **GET** /api/v1/org/members | List Team Members |
| [**removeMemberApiV1OrgMembersMemberIdDelete**](TeamManagementApi.md#removememberapiv1orgmembersmemberiddelete) | **DELETE** /api/v1/org/members/{member_id} | Remove Member |
| [**removeMemberApiV1OrgMembersMemberIdDelete_0**](TeamManagementApi.md#removememberapiv1orgmembersmemberiddelete_0) | **DELETE** /api/v1/org/members/{member_id} | Remove Member |
| [**revokeInviteApiV1OrgMembersInvitesInviteIdDelete**](TeamManagementApi.md#revokeinviteapiv1orgmembersinvitesinviteiddelete) | **DELETE** /api/v1/org/members/invites/{invite_id} | Revoke Invite |
| [**revokeInviteApiV1OrgMembersInvitesInviteIdDelete_0**](TeamManagementApi.md#revokeinviteapiv1orgmembersinvitesinviteiddelete_0) | **DELETE** /api/v1/org/members/invites/{invite_id} | Revoke Invite |
| [**updateMemberRoleApiV1OrgMembersMemberIdRolePatch**](TeamManagementApi.md#updatememberroleapiv1orgmembersmemberidrolepatch) | **PATCH** /api/v1/org/members/{member_id}/role | Update Member Role |
| [**updateMemberRoleApiV1OrgMembersMemberIdRolePatch_0**](TeamManagementApi.md#updatememberroleapiv1orgmembersmemberidrolepatch_0) | **PATCH** /api/v1/org/members/{member_id}/role | Update Member Role |



## acceptInviteApiV1OrgMembersAcceptInvitePost

> any acceptInviteApiV1OrgMembersAcceptInvitePost(token, userId)

Accept Invite

Accept a team invitation.  This endpoint is called after the user authenticates.

### Example

```ts
import {
  Configuration,
  TeamManagementApi,
} from '@encypher/sdk';
import type { AcceptInviteApiV1OrgMembersAcceptInvitePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new TeamManagementApi();

  const body = {
    // string | Invitation token
    token: token_example,
    // string | User ID of the accepting user
    userId: userId_example,
  } satisfies AcceptInviteApiV1OrgMembersAcceptInvitePostRequest;

  try {
    const data = await api.acceptInviteApiV1OrgMembersAcceptInvitePost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **token** | `string` | Invitation token | [Defaults to `undefined`] |
| **userId** | `string` | User ID of the accepting user | [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## acceptInviteApiV1OrgMembersAcceptInvitePost_0

> any acceptInviteApiV1OrgMembersAcceptInvitePost_0(token, userId)

Accept Invite

Accept a team invitation.  This endpoint is called after the user authenticates.

### Example

```ts
import {
  Configuration,
  TeamManagementApi,
} from '@encypher/sdk';
import type { AcceptInviteApiV1OrgMembersAcceptInvitePost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new TeamManagementApi();

  const body = {
    // string | Invitation token
    token: token_example,
    // string | User ID of the accepting user
    userId: userId_example,
  } satisfies AcceptInviteApiV1OrgMembersAcceptInvitePost0Request;

  try {
    const data = await api.acceptInviteApiV1OrgMembersAcceptInvitePost_0(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **token** | `string` | Invitation token | [Defaults to `undefined`] |
| **userId** | `string` | User ID of the accepting user | [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## inviteMemberApiV1OrgMembersInvitePost

> InviteResponse inviteMemberApiV1OrgMembersInvitePost(inviteRequest)

Invite Member

Invite a new member to the organization.  Sends an email invitation that expires in 7 days.

### Example

```ts
import {
  Configuration,
  TeamManagementApi,
} from '@encypher/sdk';
import type { InviteMemberApiV1OrgMembersInvitePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TeamManagementApi(config);

  const body = {
    // InviteRequest
    inviteRequest: ...,
  } satisfies InviteMemberApiV1OrgMembersInvitePostRequest;

  try {
    const data = await api.inviteMemberApiV1OrgMembersInvitePost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **inviteRequest** | [InviteRequest](InviteRequest.md) |  | |

### Return type

[**InviteResponse**](InviteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## inviteMemberApiV1OrgMembersInvitePost_0

> InviteResponse inviteMemberApiV1OrgMembersInvitePost_0(inviteRequest)

Invite Member

Invite a new member to the organization.  Sends an email invitation that expires in 7 days.

### Example

```ts
import {
  Configuration,
  TeamManagementApi,
} from '@encypher/sdk';
import type { InviteMemberApiV1OrgMembersInvitePost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TeamManagementApi(config);

  const body = {
    // InviteRequest
    inviteRequest: ...,
  } satisfies InviteMemberApiV1OrgMembersInvitePost0Request;

  try {
    const data = await api.inviteMemberApiV1OrgMembersInvitePost_0(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **inviteRequest** | [InviteRequest](InviteRequest.md) |  | |

### Return type

[**InviteResponse**](InviteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listPendingInvitesApiV1OrgMembersInvitesGet

> Array&lt;PendingInvite&gt; listPendingInvitesApiV1OrgMembersInvitesGet()

List Pending Invites

List all pending invitations.

### Example

```ts
import {
  Configuration,
  TeamManagementApi,
} from '@encypher/sdk';
import type { ListPendingInvitesApiV1OrgMembersInvitesGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TeamManagementApi(config);

  try {
    const data = await api.listPendingInvitesApiV1OrgMembersInvitesGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;PendingInvite&gt;**](PendingInvite.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listPendingInvitesApiV1OrgMembersInvitesGet_0

> Array&lt;PendingInvite&gt; listPendingInvitesApiV1OrgMembersInvitesGet_0()

List Pending Invites

List all pending invitations.

### Example

```ts
import {
  Configuration,
  TeamManagementApi,
} from '@encypher/sdk';
import type { ListPendingInvitesApiV1OrgMembersInvitesGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TeamManagementApi(config);

  try {
    const data = await api.listPendingInvitesApiV1OrgMembersInvitesGet_0();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;PendingInvite&gt;**](PendingInvite.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listTeamMembersApiV1OrgMembersGet

> TeamMemberListResponse listTeamMembersApiV1OrgMembersGet()

List Team Members

List all team members in the organization.

### Example

```ts
import {
  Configuration,
  TeamManagementApi,
} from '@encypher/sdk';
import type { ListTeamMembersApiV1OrgMembersGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TeamManagementApi(config);

  try {
    const data = await api.listTeamMembersApiV1OrgMembersGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**TeamMemberListResponse**](TeamMemberListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listTeamMembersApiV1OrgMembersGet_0

> TeamMemberListResponse listTeamMembersApiV1OrgMembersGet_0()

List Team Members

List all team members in the organization.

### Example

```ts
import {
  Configuration,
  TeamManagementApi,
} from '@encypher/sdk';
import type { ListTeamMembersApiV1OrgMembersGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TeamManagementApi(config);

  try {
    const data = await api.listTeamMembersApiV1OrgMembersGet_0();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**TeamMemberListResponse**](TeamMemberListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## removeMemberApiV1OrgMembersMemberIdDelete

> any removeMemberApiV1OrgMembersMemberIdDelete(memberId)

Remove Member

Remove a team member from the organization.  Cannot remove the owner.

### Example

```ts
import {
  Configuration,
  TeamManagementApi,
} from '@encypher/sdk';
import type { RemoveMemberApiV1OrgMembersMemberIdDeleteRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TeamManagementApi(config);

  const body = {
    // string
    memberId: memberId_example,
  } satisfies RemoveMemberApiV1OrgMembersMemberIdDeleteRequest;

  try {
    const data = await api.removeMemberApiV1OrgMembersMemberIdDelete(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **memberId** | `string` |  | [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## removeMemberApiV1OrgMembersMemberIdDelete_0

> any removeMemberApiV1OrgMembersMemberIdDelete_0(memberId)

Remove Member

Remove a team member from the organization.  Cannot remove the owner.

### Example

```ts
import {
  Configuration,
  TeamManagementApi,
} from '@encypher/sdk';
import type { RemoveMemberApiV1OrgMembersMemberIdDelete0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TeamManagementApi(config);

  const body = {
    // string
    memberId: memberId_example,
  } satisfies RemoveMemberApiV1OrgMembersMemberIdDelete0Request;

  try {
    const data = await api.removeMemberApiV1OrgMembersMemberIdDelete_0(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **memberId** | `string` |  | [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## revokeInviteApiV1OrgMembersInvitesInviteIdDelete

> any revokeInviteApiV1OrgMembersInvitesInviteIdDelete(inviteId)

Revoke Invite

Revoke a pending invitation.

### Example

```ts
import {
  Configuration,
  TeamManagementApi,
} from '@encypher/sdk';
import type { RevokeInviteApiV1OrgMembersInvitesInviteIdDeleteRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TeamManagementApi(config);

  const body = {
    // string
    inviteId: inviteId_example,
  } satisfies RevokeInviteApiV1OrgMembersInvitesInviteIdDeleteRequest;

  try {
    const data = await api.revokeInviteApiV1OrgMembersInvitesInviteIdDelete(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **inviteId** | `string` |  | [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## revokeInviteApiV1OrgMembersInvitesInviteIdDelete_0

> any revokeInviteApiV1OrgMembersInvitesInviteIdDelete_0(inviteId)

Revoke Invite

Revoke a pending invitation.

### Example

```ts
import {
  Configuration,
  TeamManagementApi,
} from '@encypher/sdk';
import type { RevokeInviteApiV1OrgMembersInvitesInviteIdDelete0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TeamManagementApi(config);

  const body = {
    // string
    inviteId: inviteId_example,
  } satisfies RevokeInviteApiV1OrgMembersInvitesInviteIdDelete0Request;

  try {
    const data = await api.revokeInviteApiV1OrgMembersInvitesInviteIdDelete_0(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **inviteId** | `string` |  | [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## updateMemberRoleApiV1OrgMembersMemberIdRolePatch

> any updateMemberRoleApiV1OrgMembersMemberIdRolePatch(memberId, updateRoleRequest)

Update Member Role

Update a team member\&#39;s role.  Admins can change roles of members and viewers. Only owners can change admin roles.

### Example

```ts
import {
  Configuration,
  TeamManagementApi,
} from '@encypher/sdk';
import type { UpdateMemberRoleApiV1OrgMembersMemberIdRolePatchRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TeamManagementApi(config);

  const body = {
    // string
    memberId: memberId_example,
    // UpdateRoleRequest
    updateRoleRequest: ...,
  } satisfies UpdateMemberRoleApiV1OrgMembersMemberIdRolePatchRequest;

  try {
    const data = await api.updateMemberRoleApiV1OrgMembersMemberIdRolePatch(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **memberId** | `string` |  | [Defaults to `undefined`] |
| **updateRoleRequest** | [UpdateRoleRequest](UpdateRoleRequest.md) |  | |

### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## updateMemberRoleApiV1OrgMembersMemberIdRolePatch_0

> any updateMemberRoleApiV1OrgMembersMemberIdRolePatch_0(memberId, updateRoleRequest)

Update Member Role

Update a team member\&#39;s role.  Admins can change roles of members and viewers. Only owners can change admin roles.

### Example

```ts
import {
  Configuration,
  TeamManagementApi,
} from '@encypher/sdk';
import type { UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TeamManagementApi(config);

  const body = {
    // string
    memberId: memberId_example,
    // UpdateRoleRequest
    updateRoleRequest: ...,
  } satisfies UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch0Request;

  try {
    const data = await api.updateMemberRoleApiV1OrgMembersMemberIdRolePatch_0(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **memberId** | `string` |  | [Defaults to `undefined`] |
| **updateRoleRequest** | [UpdateRoleRequest](UpdateRoleRequest.md) |  | |

### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

