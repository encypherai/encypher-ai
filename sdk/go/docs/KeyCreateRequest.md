# KeyCreateRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | Pointer to **NullableString** |  | [optional] 
**Permissions** | Pointer to **[]string** | Permissions: sign, verify, read, admin | [optional] [default to [sign, verify]]
**ExpiresInDays** | Pointer to **NullableInt32** |  | [optional] 

## Methods

### NewKeyCreateRequest

`func NewKeyCreateRequest() *KeyCreateRequest`

NewKeyCreateRequest instantiates a new KeyCreateRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewKeyCreateRequestWithDefaults

`func NewKeyCreateRequestWithDefaults() *KeyCreateRequest`

NewKeyCreateRequestWithDefaults instantiates a new KeyCreateRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *KeyCreateRequest) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *KeyCreateRequest) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *KeyCreateRequest) SetName(v string)`

SetName sets Name field to given value.

### HasName

`func (o *KeyCreateRequest) HasName() bool`

HasName returns a boolean if a field has been set.

### SetNameNil

`func (o *KeyCreateRequest) SetNameNil(b bool)`

 SetNameNil sets the value for Name to be an explicit nil

### UnsetName
`func (o *KeyCreateRequest) UnsetName()`

UnsetName ensures that no value is present for Name, not even an explicit nil
### GetPermissions

`func (o *KeyCreateRequest) GetPermissions() []string`

GetPermissions returns the Permissions field if non-nil, zero value otherwise.

### GetPermissionsOk

`func (o *KeyCreateRequest) GetPermissionsOk() (*[]string, bool)`

GetPermissionsOk returns a tuple with the Permissions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPermissions

`func (o *KeyCreateRequest) SetPermissions(v []string)`

SetPermissions sets Permissions field to given value.

### HasPermissions

`func (o *KeyCreateRequest) HasPermissions() bool`

HasPermissions returns a boolean if a field has been set.

### GetExpiresInDays

`func (o *KeyCreateRequest) GetExpiresInDays() int32`

GetExpiresInDays returns the ExpiresInDays field if non-nil, zero value otherwise.

### GetExpiresInDaysOk

`func (o *KeyCreateRequest) GetExpiresInDaysOk() (*int32, bool)`

GetExpiresInDaysOk returns a tuple with the ExpiresInDays field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetExpiresInDays

`func (o *KeyCreateRequest) SetExpiresInDays(v int32)`

SetExpiresInDays sets ExpiresInDays field to given value.

### HasExpiresInDays

`func (o *KeyCreateRequest) HasExpiresInDays() bool`

HasExpiresInDays returns a boolean if a field has been set.

### SetExpiresInDaysNil

`func (o *KeyCreateRequest) SetExpiresInDaysNil(b bool)`

 SetExpiresInDaysNil sets the value for ExpiresInDays to be an explicit nil

### UnsetExpiresInDays
`func (o *KeyCreateRequest) UnsetExpiresInDays()`

UnsetExpiresInDays ensures that no value is present for ExpiresInDays, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


