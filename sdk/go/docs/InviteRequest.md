# InviteRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Email** | **string** |  | 
**Role** | Pointer to [**TeamRole**](TeamRole.md) |  | [optional] 
**Name** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewInviteRequest

`func NewInviteRequest(email string, ) *InviteRequest`

NewInviteRequest instantiates a new InviteRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewInviteRequestWithDefaults

`func NewInviteRequestWithDefaults() *InviteRequest`

NewInviteRequestWithDefaults instantiates a new InviteRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetEmail

`func (o *InviteRequest) GetEmail() string`

GetEmail returns the Email field if non-nil, zero value otherwise.

### GetEmailOk

`func (o *InviteRequest) GetEmailOk() (*string, bool)`

GetEmailOk returns a tuple with the Email field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmail

`func (o *InviteRequest) SetEmail(v string)`

SetEmail sets Email field to given value.


### GetRole

`func (o *InviteRequest) GetRole() TeamRole`

GetRole returns the Role field if non-nil, zero value otherwise.

### GetRoleOk

`func (o *InviteRequest) GetRoleOk() (*TeamRole, bool)`

GetRoleOk returns a tuple with the Role field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRole

`func (o *InviteRequest) SetRole(v TeamRole)`

SetRole sets Role field to given value.

### HasRole

`func (o *InviteRequest) HasRole() bool`

HasRole returns a boolean if a field has been set.

### GetName

`func (o *InviteRequest) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *InviteRequest) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *InviteRequest) SetName(v string)`

SetName sets Name field to given value.

### HasName

`func (o *InviteRequest) HasName() bool`

HasName returns a boolean if a field has been set.

### SetNameNil

`func (o *InviteRequest) SetNameNil(b bool)`

 SetNameNil sets the value for Name to be an explicit nil

### UnsetName
`func (o *InviteRequest) UnsetName()`

UnsetName ensures that no value is present for Name, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


