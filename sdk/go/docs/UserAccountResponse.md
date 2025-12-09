# UserAccountResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**UserId** | **string** | User identifier | 
**Email** | **string** | User email | 
**FullName** | Pointer to **NullableString** |  | [optional] 
**OrganizationId** | **string** | Associated organization | 
**Role** | **string** | User role | 
**CreatedAt** | **time.Time** | Creation timestamp | 
**IsActive** | **bool** | Whether account is active | 

## Methods

### NewUserAccountResponse

`func NewUserAccountResponse(userId string, email string, organizationId string, role string, createdAt time.Time, isActive bool, ) *UserAccountResponse`

NewUserAccountResponse instantiates a new UserAccountResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewUserAccountResponseWithDefaults

`func NewUserAccountResponseWithDefaults() *UserAccountResponse`

NewUserAccountResponseWithDefaults instantiates a new UserAccountResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetUserId

`func (o *UserAccountResponse) GetUserId() string`

GetUserId returns the UserId field if non-nil, zero value otherwise.

### GetUserIdOk

`func (o *UserAccountResponse) GetUserIdOk() (*string, bool)`

GetUserIdOk returns a tuple with the UserId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUserId

`func (o *UserAccountResponse) SetUserId(v string)`

SetUserId sets UserId field to given value.


### GetEmail

`func (o *UserAccountResponse) GetEmail() string`

GetEmail returns the Email field if non-nil, zero value otherwise.

### GetEmailOk

`func (o *UserAccountResponse) GetEmailOk() (*string, bool)`

GetEmailOk returns a tuple with the Email field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmail

`func (o *UserAccountResponse) SetEmail(v string)`

SetEmail sets Email field to given value.


### GetFullName

`func (o *UserAccountResponse) GetFullName() string`

GetFullName returns the FullName field if non-nil, zero value otherwise.

### GetFullNameOk

`func (o *UserAccountResponse) GetFullNameOk() (*string, bool)`

GetFullNameOk returns a tuple with the FullName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFullName

`func (o *UserAccountResponse) SetFullName(v string)`

SetFullName sets FullName field to given value.

### HasFullName

`func (o *UserAccountResponse) HasFullName() bool`

HasFullName returns a boolean if a field has been set.

### SetFullNameNil

`func (o *UserAccountResponse) SetFullNameNil(b bool)`

 SetFullNameNil sets the value for FullName to be an explicit nil

### UnsetFullName
`func (o *UserAccountResponse) UnsetFullName()`

UnsetFullName ensures that no value is present for FullName, not even an explicit nil
### GetOrganizationId

`func (o *UserAccountResponse) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *UserAccountResponse) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *UserAccountResponse) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetRole

`func (o *UserAccountResponse) GetRole() string`

GetRole returns the Role field if non-nil, zero value otherwise.

### GetRoleOk

`func (o *UserAccountResponse) GetRoleOk() (*string, bool)`

GetRoleOk returns a tuple with the Role field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRole

`func (o *UserAccountResponse) SetRole(v string)`

SetRole sets Role field to given value.


### GetCreatedAt

`func (o *UserAccountResponse) GetCreatedAt() time.Time`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *UserAccountResponse) GetCreatedAtOk() (*time.Time, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *UserAccountResponse) SetCreatedAt(v time.Time)`

SetCreatedAt sets CreatedAt field to given value.


### GetIsActive

`func (o *UserAccountResponse) GetIsActive() bool`

GetIsActive returns the IsActive field if non-nil, zero value otherwise.

### GetIsActiveOk

`func (o *UserAccountResponse) GetIsActiveOk() (*bool, bool)`

GetIsActiveOk returns a tuple with the IsActive field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsActive

`func (o *UserAccountResponse) SetIsActive(v bool)`

SetIsActive sets IsActive field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


