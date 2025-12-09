# APIKeyCreateRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | Pointer to **NullableString** |  | [optional] 
**ExpiresInDays** | Pointer to **NullableInt32** |  | [optional] 
**Scopes** | Pointer to **[]string** |  | [optional] 

## Methods

### NewAPIKeyCreateRequest

`func NewAPIKeyCreateRequest() *APIKeyCreateRequest`

NewAPIKeyCreateRequest instantiates a new APIKeyCreateRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAPIKeyCreateRequestWithDefaults

`func NewAPIKeyCreateRequestWithDefaults() *APIKeyCreateRequest`

NewAPIKeyCreateRequestWithDefaults instantiates a new APIKeyCreateRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *APIKeyCreateRequest) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *APIKeyCreateRequest) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *APIKeyCreateRequest) SetName(v string)`

SetName sets Name field to given value.

### HasName

`func (o *APIKeyCreateRequest) HasName() bool`

HasName returns a boolean if a field has been set.

### SetNameNil

`func (o *APIKeyCreateRequest) SetNameNil(b bool)`

 SetNameNil sets the value for Name to be an explicit nil

### UnsetName
`func (o *APIKeyCreateRequest) UnsetName()`

UnsetName ensures that no value is present for Name, not even an explicit nil
### GetExpiresInDays

`func (o *APIKeyCreateRequest) GetExpiresInDays() int32`

GetExpiresInDays returns the ExpiresInDays field if non-nil, zero value otherwise.

### GetExpiresInDaysOk

`func (o *APIKeyCreateRequest) GetExpiresInDaysOk() (*int32, bool)`

GetExpiresInDaysOk returns a tuple with the ExpiresInDays field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetExpiresInDays

`func (o *APIKeyCreateRequest) SetExpiresInDays(v int32)`

SetExpiresInDays sets ExpiresInDays field to given value.

### HasExpiresInDays

`func (o *APIKeyCreateRequest) HasExpiresInDays() bool`

HasExpiresInDays returns a boolean if a field has been set.

### SetExpiresInDaysNil

`func (o *APIKeyCreateRequest) SetExpiresInDaysNil(b bool)`

 SetExpiresInDaysNil sets the value for ExpiresInDays to be an explicit nil

### UnsetExpiresInDays
`func (o *APIKeyCreateRequest) UnsetExpiresInDays()`

UnsetExpiresInDays ensures that no value is present for ExpiresInDays, not even an explicit nil
### GetScopes

`func (o *APIKeyCreateRequest) GetScopes() []string`

GetScopes returns the Scopes field if non-nil, zero value otherwise.

### GetScopesOk

`func (o *APIKeyCreateRequest) GetScopesOk() (*[]string, bool)`

GetScopesOk returns a tuple with the Scopes field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetScopes

`func (o *APIKeyCreateRequest) SetScopes(v []string)`

SetScopes sets Scopes field to given value.

### HasScopes

`func (o *APIKeyCreateRequest) HasScopes() bool`

HasScopes returns a boolean if a field has been set.

### SetScopesNil

`func (o *APIKeyCreateRequest) SetScopesNil(b bool)`

 SetScopesNil sets the value for Scopes to be an explicit nil

### UnsetScopes
`func (o *APIKeyCreateRequest) UnsetScopes()`

UnsetScopes ensures that no value is present for Scopes, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


