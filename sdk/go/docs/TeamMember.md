# TeamMember

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**UserId** | **string** |  | 
**Email** | **string** |  | 
**Name** | Pointer to **NullableString** |  | [optional] 
**Role** | [**TeamRole**](TeamRole.md) |  | 
**Status** | **string** |  | 
**InvitedAt** | Pointer to **NullableString** |  | [optional] 
**AcceptedAt** | Pointer to **NullableString** |  | [optional] 
**LastActiveAt** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewTeamMember

`func NewTeamMember(id string, userId string, email string, role TeamRole, status string, ) *TeamMember`

NewTeamMember instantiates a new TeamMember object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewTeamMemberWithDefaults

`func NewTeamMemberWithDefaults() *TeamMember`

NewTeamMemberWithDefaults instantiates a new TeamMember object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *TeamMember) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *TeamMember) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *TeamMember) SetId(v string)`

SetId sets Id field to given value.


### GetUserId

`func (o *TeamMember) GetUserId() string`

GetUserId returns the UserId field if non-nil, zero value otherwise.

### GetUserIdOk

`func (o *TeamMember) GetUserIdOk() (*string, bool)`

GetUserIdOk returns a tuple with the UserId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUserId

`func (o *TeamMember) SetUserId(v string)`

SetUserId sets UserId field to given value.


### GetEmail

`func (o *TeamMember) GetEmail() string`

GetEmail returns the Email field if non-nil, zero value otherwise.

### GetEmailOk

`func (o *TeamMember) GetEmailOk() (*string, bool)`

GetEmailOk returns a tuple with the Email field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmail

`func (o *TeamMember) SetEmail(v string)`

SetEmail sets Email field to given value.


### GetName

`func (o *TeamMember) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *TeamMember) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *TeamMember) SetName(v string)`

SetName sets Name field to given value.

### HasName

`func (o *TeamMember) HasName() bool`

HasName returns a boolean if a field has been set.

### SetNameNil

`func (o *TeamMember) SetNameNil(b bool)`

 SetNameNil sets the value for Name to be an explicit nil

### UnsetName
`func (o *TeamMember) UnsetName()`

UnsetName ensures that no value is present for Name, not even an explicit nil
### GetRole

`func (o *TeamMember) GetRole() TeamRole`

GetRole returns the Role field if non-nil, zero value otherwise.

### GetRoleOk

`func (o *TeamMember) GetRoleOk() (*TeamRole, bool)`

GetRoleOk returns a tuple with the Role field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRole

`func (o *TeamMember) SetRole(v TeamRole)`

SetRole sets Role field to given value.


### GetStatus

`func (o *TeamMember) GetStatus() string`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *TeamMember) GetStatusOk() (*string, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *TeamMember) SetStatus(v string)`

SetStatus sets Status field to given value.


### GetInvitedAt

`func (o *TeamMember) GetInvitedAt() string`

GetInvitedAt returns the InvitedAt field if non-nil, zero value otherwise.

### GetInvitedAtOk

`func (o *TeamMember) GetInvitedAtOk() (*string, bool)`

GetInvitedAtOk returns a tuple with the InvitedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetInvitedAt

`func (o *TeamMember) SetInvitedAt(v string)`

SetInvitedAt sets InvitedAt field to given value.

### HasInvitedAt

`func (o *TeamMember) HasInvitedAt() bool`

HasInvitedAt returns a boolean if a field has been set.

### SetInvitedAtNil

`func (o *TeamMember) SetInvitedAtNil(b bool)`

 SetInvitedAtNil sets the value for InvitedAt to be an explicit nil

### UnsetInvitedAt
`func (o *TeamMember) UnsetInvitedAt()`

UnsetInvitedAt ensures that no value is present for InvitedAt, not even an explicit nil
### GetAcceptedAt

`func (o *TeamMember) GetAcceptedAt() string`

GetAcceptedAt returns the AcceptedAt field if non-nil, zero value otherwise.

### GetAcceptedAtOk

`func (o *TeamMember) GetAcceptedAtOk() (*string, bool)`

GetAcceptedAtOk returns a tuple with the AcceptedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAcceptedAt

`func (o *TeamMember) SetAcceptedAt(v string)`

SetAcceptedAt sets AcceptedAt field to given value.

### HasAcceptedAt

`func (o *TeamMember) HasAcceptedAt() bool`

HasAcceptedAt returns a boolean if a field has been set.

### SetAcceptedAtNil

`func (o *TeamMember) SetAcceptedAtNil(b bool)`

 SetAcceptedAtNil sets the value for AcceptedAt to be an explicit nil

### UnsetAcceptedAt
`func (o *TeamMember) UnsetAcceptedAt()`

UnsetAcceptedAt ensures that no value is present for AcceptedAt, not even an explicit nil
### GetLastActiveAt

`func (o *TeamMember) GetLastActiveAt() string`

GetLastActiveAt returns the LastActiveAt field if non-nil, zero value otherwise.

### GetLastActiveAtOk

`func (o *TeamMember) GetLastActiveAtOk() (*string, bool)`

GetLastActiveAtOk returns a tuple with the LastActiveAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLastActiveAt

`func (o *TeamMember) SetLastActiveAt(v string)`

SetLastActiveAt sets LastActiveAt field to given value.

### HasLastActiveAt

`func (o *TeamMember) HasLastActiveAt() bool`

HasLastActiveAt returns a boolean if a field has been set.

### SetLastActiveAtNil

`func (o *TeamMember) SetLastActiveAtNil(b bool)`

 SetLastActiveAtNil sets the value for LastActiveAt to be an explicit nil

### UnsetLastActiveAt
`func (o *TeamMember) UnsetLastActiveAt()`

UnsetLastActiveAt ensures that no value is present for LastActiveAt, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


