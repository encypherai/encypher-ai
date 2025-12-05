# \TeamManagementAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**AcceptInviteApiV1OrgMembersAcceptInvitePost**](TeamManagementAPI.md#AcceptInviteApiV1OrgMembersAcceptInvitePost) | **Post** /api/v1/org/members/accept-invite | Accept Invite
[**AcceptInviteApiV1OrgMembersAcceptInvitePost_0**](TeamManagementAPI.md#AcceptInviteApiV1OrgMembersAcceptInvitePost_0) | **Post** /api/v1/org/members/accept-invite | Accept Invite
[**InviteMemberApiV1OrgMembersInvitePost**](TeamManagementAPI.md#InviteMemberApiV1OrgMembersInvitePost) | **Post** /api/v1/org/members/invite | Invite Member
[**InviteMemberApiV1OrgMembersInvitePost_0**](TeamManagementAPI.md#InviteMemberApiV1OrgMembersInvitePost_0) | **Post** /api/v1/org/members/invite | Invite Member
[**ListPendingInvitesApiV1OrgMembersInvitesGet**](TeamManagementAPI.md#ListPendingInvitesApiV1OrgMembersInvitesGet) | **Get** /api/v1/org/members/invites | List Pending Invites
[**ListPendingInvitesApiV1OrgMembersInvitesGet_0**](TeamManagementAPI.md#ListPendingInvitesApiV1OrgMembersInvitesGet_0) | **Get** /api/v1/org/members/invites | List Pending Invites
[**ListTeamMembersApiV1OrgMembersGet**](TeamManagementAPI.md#ListTeamMembersApiV1OrgMembersGet) | **Get** /api/v1/org/members | List Team Members
[**ListTeamMembersApiV1OrgMembersGet_0**](TeamManagementAPI.md#ListTeamMembersApiV1OrgMembersGet_0) | **Get** /api/v1/org/members | List Team Members
[**RemoveMemberApiV1OrgMembersMemberIdDelete**](TeamManagementAPI.md#RemoveMemberApiV1OrgMembersMemberIdDelete) | **Delete** /api/v1/org/members/{member_id} | Remove Member
[**RemoveMemberApiV1OrgMembersMemberIdDelete_0**](TeamManagementAPI.md#RemoveMemberApiV1OrgMembersMemberIdDelete_0) | **Delete** /api/v1/org/members/{member_id} | Remove Member
[**RevokeInviteApiV1OrgMembersInvitesInviteIdDelete**](TeamManagementAPI.md#RevokeInviteApiV1OrgMembersInvitesInviteIdDelete) | **Delete** /api/v1/org/members/invites/{invite_id} | Revoke Invite
[**RevokeInviteApiV1OrgMembersInvitesInviteIdDelete_0**](TeamManagementAPI.md#RevokeInviteApiV1OrgMembersInvitesInviteIdDelete_0) | **Delete** /api/v1/org/members/invites/{invite_id} | Revoke Invite
[**UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch**](TeamManagementAPI.md#UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch) | **Patch** /api/v1/org/members/{member_id}/role | Update Member Role
[**UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch_0**](TeamManagementAPI.md#UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch_0) | **Patch** /api/v1/org/members/{member_id}/role | Update Member Role



## AcceptInviteApiV1OrgMembersAcceptInvitePost

> interface{} AcceptInviteApiV1OrgMembersAcceptInvitePost(ctx).Token(token).UserId(userId).Execute()

Accept Invite



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	token := "token_example" // string | Invitation token
	userId := "userId_example" // string | User ID of the accepting user

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TeamManagementAPI.AcceptInviteApiV1OrgMembersAcceptInvitePost(context.Background()).Token(token).UserId(userId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TeamManagementAPI.AcceptInviteApiV1OrgMembersAcceptInvitePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `AcceptInviteApiV1OrgMembersAcceptInvitePost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `TeamManagementAPI.AcceptInviteApiV1OrgMembersAcceptInvitePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiAcceptInviteApiV1OrgMembersAcceptInvitePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **string** | Invitation token | 
 **userId** | **string** | User ID of the accepting user | 

### Return type

**interface{}**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AcceptInviteApiV1OrgMembersAcceptInvitePost_0

> interface{} AcceptInviteApiV1OrgMembersAcceptInvitePost_0(ctx).Token(token).UserId(userId).Execute()

Accept Invite



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	token := "token_example" // string | Invitation token
	userId := "userId_example" // string | User ID of the accepting user

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TeamManagementAPI.AcceptInviteApiV1OrgMembersAcceptInvitePost_0(context.Background()).Token(token).UserId(userId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TeamManagementAPI.AcceptInviteApiV1OrgMembersAcceptInvitePost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `AcceptInviteApiV1OrgMembersAcceptInvitePost_0`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `TeamManagementAPI.AcceptInviteApiV1OrgMembersAcceptInvitePost_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiAcceptInviteApiV1OrgMembersAcceptInvitePost_1Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **string** | Invitation token | 
 **userId** | **string** | User ID of the accepting user | 

### Return type

**interface{}**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## InviteMemberApiV1OrgMembersInvitePost

> InviteResponse InviteMemberApiV1OrgMembersInvitePost(ctx).InviteRequest(inviteRequest).Execute()

Invite Member



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	inviteRequest := *openapiclient.NewInviteRequest("Email_example") // InviteRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TeamManagementAPI.InviteMemberApiV1OrgMembersInvitePost(context.Background()).InviteRequest(inviteRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TeamManagementAPI.InviteMemberApiV1OrgMembersInvitePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `InviteMemberApiV1OrgMembersInvitePost`: InviteResponse
	fmt.Fprintf(os.Stdout, "Response from `TeamManagementAPI.InviteMemberApiV1OrgMembersInvitePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiInviteMemberApiV1OrgMembersInvitePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **inviteRequest** | [**InviteRequest**](InviteRequest.md) |  | 

### Return type

[**InviteResponse**](InviteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## InviteMemberApiV1OrgMembersInvitePost_0

> InviteResponse InviteMemberApiV1OrgMembersInvitePost_0(ctx).InviteRequest(inviteRequest).Execute()

Invite Member



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	inviteRequest := *openapiclient.NewInviteRequest("Email_example") // InviteRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TeamManagementAPI.InviteMemberApiV1OrgMembersInvitePost_0(context.Background()).InviteRequest(inviteRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TeamManagementAPI.InviteMemberApiV1OrgMembersInvitePost_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `InviteMemberApiV1OrgMembersInvitePost_0`: InviteResponse
	fmt.Fprintf(os.Stdout, "Response from `TeamManagementAPI.InviteMemberApiV1OrgMembersInvitePost_0`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiInviteMemberApiV1OrgMembersInvitePost_2Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **inviteRequest** | [**InviteRequest**](InviteRequest.md) |  | 

### Return type

[**InviteResponse**](InviteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListPendingInvitesApiV1OrgMembersInvitesGet

> []PendingInvite ListPendingInvitesApiV1OrgMembersInvitesGet(ctx).Execute()

List Pending Invites



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TeamManagementAPI.ListPendingInvitesApiV1OrgMembersInvitesGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TeamManagementAPI.ListPendingInvitesApiV1OrgMembersInvitesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListPendingInvitesApiV1OrgMembersInvitesGet`: []PendingInvite
	fmt.Fprintf(os.Stdout, "Response from `TeamManagementAPI.ListPendingInvitesApiV1OrgMembersInvitesGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiListPendingInvitesApiV1OrgMembersInvitesGetRequest struct via the builder pattern


### Return type

[**[]PendingInvite**](PendingInvite.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListPendingInvitesApiV1OrgMembersInvitesGet_0

> []PendingInvite ListPendingInvitesApiV1OrgMembersInvitesGet_0(ctx).Execute()

List Pending Invites



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TeamManagementAPI.ListPendingInvitesApiV1OrgMembersInvitesGet_0(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TeamManagementAPI.ListPendingInvitesApiV1OrgMembersInvitesGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListPendingInvitesApiV1OrgMembersInvitesGet_0`: []PendingInvite
	fmt.Fprintf(os.Stdout, "Response from `TeamManagementAPI.ListPendingInvitesApiV1OrgMembersInvitesGet_0`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiListPendingInvitesApiV1OrgMembersInvitesGet_3Request struct via the builder pattern


### Return type

[**[]PendingInvite**](PendingInvite.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListTeamMembersApiV1OrgMembersGet

> TeamMemberListResponse ListTeamMembersApiV1OrgMembersGet(ctx).Execute()

List Team Members



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TeamManagementAPI.ListTeamMembersApiV1OrgMembersGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TeamManagementAPI.ListTeamMembersApiV1OrgMembersGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListTeamMembersApiV1OrgMembersGet`: TeamMemberListResponse
	fmt.Fprintf(os.Stdout, "Response from `TeamManagementAPI.ListTeamMembersApiV1OrgMembersGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiListTeamMembersApiV1OrgMembersGetRequest struct via the builder pattern


### Return type

[**TeamMemberListResponse**](TeamMemberListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListTeamMembersApiV1OrgMembersGet_0

> TeamMemberListResponse ListTeamMembersApiV1OrgMembersGet_0(ctx).Execute()

List Team Members



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TeamManagementAPI.ListTeamMembersApiV1OrgMembersGet_0(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TeamManagementAPI.ListTeamMembersApiV1OrgMembersGet_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListTeamMembersApiV1OrgMembersGet_0`: TeamMemberListResponse
	fmt.Fprintf(os.Stdout, "Response from `TeamManagementAPI.ListTeamMembersApiV1OrgMembersGet_0`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiListTeamMembersApiV1OrgMembersGet_4Request struct via the builder pattern


### Return type

[**TeamMemberListResponse**](TeamMemberListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RemoveMemberApiV1OrgMembersMemberIdDelete

> interface{} RemoveMemberApiV1OrgMembersMemberIdDelete(ctx, memberId).Execute()

Remove Member



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	memberId := "memberId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TeamManagementAPI.RemoveMemberApiV1OrgMembersMemberIdDelete(context.Background(), memberId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TeamManagementAPI.RemoveMemberApiV1OrgMembersMemberIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RemoveMemberApiV1OrgMembersMemberIdDelete`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `TeamManagementAPI.RemoveMemberApiV1OrgMembersMemberIdDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**memberId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiRemoveMemberApiV1OrgMembersMemberIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

**interface{}**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RemoveMemberApiV1OrgMembersMemberIdDelete_0

> interface{} RemoveMemberApiV1OrgMembersMemberIdDelete_0(ctx, memberId).Execute()

Remove Member



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	memberId := "memberId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TeamManagementAPI.RemoveMemberApiV1OrgMembersMemberIdDelete_0(context.Background(), memberId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TeamManagementAPI.RemoveMemberApiV1OrgMembersMemberIdDelete_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RemoveMemberApiV1OrgMembersMemberIdDelete_0`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `TeamManagementAPI.RemoveMemberApiV1OrgMembersMemberIdDelete_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**memberId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiRemoveMemberApiV1OrgMembersMemberIdDelete_5Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

**interface{}**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RevokeInviteApiV1OrgMembersInvitesInviteIdDelete

> interface{} RevokeInviteApiV1OrgMembersInvitesInviteIdDelete(ctx, inviteId).Execute()

Revoke Invite



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	inviteId := "inviteId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TeamManagementAPI.RevokeInviteApiV1OrgMembersInvitesInviteIdDelete(context.Background(), inviteId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TeamManagementAPI.RevokeInviteApiV1OrgMembersInvitesInviteIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RevokeInviteApiV1OrgMembersInvitesInviteIdDelete`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `TeamManagementAPI.RevokeInviteApiV1OrgMembersInvitesInviteIdDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**inviteId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiRevokeInviteApiV1OrgMembersInvitesInviteIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

**interface{}**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RevokeInviteApiV1OrgMembersInvitesInviteIdDelete_0

> interface{} RevokeInviteApiV1OrgMembersInvitesInviteIdDelete_0(ctx, inviteId).Execute()

Revoke Invite



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	inviteId := "inviteId_example" // string | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TeamManagementAPI.RevokeInviteApiV1OrgMembersInvitesInviteIdDelete_0(context.Background(), inviteId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TeamManagementAPI.RevokeInviteApiV1OrgMembersInvitesInviteIdDelete_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RevokeInviteApiV1OrgMembersInvitesInviteIdDelete_0`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `TeamManagementAPI.RevokeInviteApiV1OrgMembersInvitesInviteIdDelete_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**inviteId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiRevokeInviteApiV1OrgMembersInvitesInviteIdDelete_6Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

**interface{}**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch

> interface{} UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch(ctx, memberId).UpdateRoleRequest(updateRoleRequest).Execute()

Update Member Role



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	memberId := "memberId_example" // string | 
	updateRoleRequest := *openapiclient.NewUpdateRoleRequest(openapiclient.TeamRole("owner")) // UpdateRoleRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TeamManagementAPI.UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch(context.Background(), memberId).UpdateRoleRequest(updateRoleRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TeamManagementAPI.UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `TeamManagementAPI.UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**memberId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateMemberRoleApiV1OrgMembersMemberIdRolePatchRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **updateRoleRequest** | [**UpdateRoleRequest**](UpdateRoleRequest.md) |  | 

### Return type

**interface{}**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch_0

> interface{} UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch_0(ctx, memberId).UpdateRoleRequest(updateRoleRequest).Execute()

Update Member Role



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	memberId := "memberId_example" // string | 
	updateRoleRequest := *openapiclient.NewUpdateRoleRequest(openapiclient.TeamRole("owner")) // UpdateRoleRequest | 

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TeamManagementAPI.UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch_0(context.Background(), memberId).UpdateRoleRequest(updateRoleRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TeamManagementAPI.UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch_0``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch_0`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `TeamManagementAPI.UpdateMemberRoleApiV1OrgMembersMemberIdRolePatch_0`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**memberId** | **string** |  | 

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateMemberRoleApiV1OrgMembersMemberIdRolePatch_7Request struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **updateRoleRequest** | [**UpdateRoleRequest**](UpdateRoleRequest.md) |  | 

### Return type

**interface{}**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

