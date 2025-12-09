# UserAccountCreateRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Email** | **string** | User email address | 
**FullName** | Pointer to **NullableString** |  | [optional] 
**OrganizationId** | Pointer to **NullableString** |  | [optional] 
**Role** | Pointer to **NullableString** |  | [optional] 
**SendWelcomeEmail** | Pointer to **bool** | Whether to send welcome email | [optional] [default to true]

## Methods

### NewUserAccountCreateRequest

`func NewUserAccountCreateRequest(email string, ) *UserAccountCreateRequest`

NewUserAccountCreateRequest instantiates a new UserAccountCreateRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewUserAccountCreateRequestWithDefaults

`func NewUserAccountCreateRequestWithDefaults() *UserAccountCreateRequest`

NewUserAccountCreateRequestWithDefaults instantiates a new UserAccountCreateRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetEmail

`func (o *UserAccountCreateRequest) GetEmail() string`

GetEmail returns the Email field if non-nil, zero value otherwise.

### GetEmailOk

`func (o *UserAccountCreateRequest) GetEmailOk() (*string, bool)`

GetEmailOk returns a tuple with the Email field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmail

`func (o *UserAccountCreateRequest) SetEmail(v string)`

SetEmail sets Email field to given value.


### GetFullName

`func (o *UserAccountCreateRequest) GetFullName() string`

GetFullName returns the FullName field if non-nil, zero value otherwise.

### GetFullNameOk

`func (o *UserAccountCreateRequest) GetFullNameOk() (*string, bool)`

GetFullNameOk returns a tuple with the FullName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFullName

`func (o *UserAccountCreateRequest) SetFullName(v string)`

SetFullName sets FullName field to given value.

### HasFullName

`func (o *UserAccountCreateRequest) HasFullName() bool`

HasFullName returns a boolean if a field has been set.

### SetFullNameNil

`func (o *UserAccountCreateRequest) SetFullNameNil(b bool)`

 SetFullNameNil sets the value for FullName to be an explicit nil

### UnsetFullName
`func (o *UserAccountCreateRequest) UnsetFullName()`

UnsetFullName ensures that no value is present for FullName, not even an explicit nil
### GetOrganizationId

`func (o *UserAccountCreateRequest) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *UserAccountCreateRequest) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *UserAccountCreateRequest) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.

### HasOrganizationId

`func (o *UserAccountCreateRequest) HasOrganizationId() bool`

HasOrganizationId returns a boolean if a field has been set.

### SetOrganizationIdNil

`func (o *UserAccountCreateRequest) SetOrganizationIdNil(b bool)`

 SetOrganizationIdNil sets the value for OrganizationId to be an explicit nil

### UnsetOrganizationId
`func (o *UserAccountCreateRequest) UnsetOrganizationId()`

UnsetOrganizationId ensures that no value is present for OrganizationId, not even an explicit nil
### GetRole

`func (o *UserAccountCreateRequest) GetRole() string`

GetRole returns the Role field if non-nil, zero value otherwise.

### GetRoleOk

`func (o *UserAccountCreateRequest) GetRoleOk() (*string, bool)`

GetRoleOk returns a tuple with the Role field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRole

`func (o *UserAccountCreateRequest) SetRole(v string)`

SetRole sets Role field to given value.

### HasRole

`func (o *UserAccountCreateRequest) HasRole() bool`

HasRole returns a boolean if a field has been set.

### SetRoleNil

`func (o *UserAccountCreateRequest) SetRoleNil(b bool)`

 SetRoleNil sets the value for Role to be an explicit nil

### UnsetRole
`func (o *UserAccountCreateRequest) UnsetRole()`

UnsetRole ensures that no value is present for Role, not even an explicit nil
### GetSendWelcomeEmail

`func (o *UserAccountCreateRequest) GetSendWelcomeEmail() bool`

GetSendWelcomeEmail returns the SendWelcomeEmail field if non-nil, zero value otherwise.

### GetSendWelcomeEmailOk

`func (o *UserAccountCreateRequest) GetSendWelcomeEmailOk() (*bool, bool)`

GetSendWelcomeEmailOk returns a tuple with the SendWelcomeEmail field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSendWelcomeEmail

`func (o *UserAccountCreateRequest) SetSendWelcomeEmail(v bool)`

SetSendWelcomeEmail sets SendWelcomeEmail field to given value.

### HasSendWelcomeEmail

`func (o *UserAccountCreateRequest) HasSendWelcomeEmail() bool`

HasSendWelcomeEmail returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


