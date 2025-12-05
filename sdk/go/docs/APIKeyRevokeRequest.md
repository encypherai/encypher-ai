# APIKeyRevokeRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**KeyId** | **string** | API key identifier to revoke | 
**Reason** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewAPIKeyRevokeRequest

`func NewAPIKeyRevokeRequest(keyId string, ) *APIKeyRevokeRequest`

NewAPIKeyRevokeRequest instantiates a new APIKeyRevokeRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAPIKeyRevokeRequestWithDefaults

`func NewAPIKeyRevokeRequestWithDefaults() *APIKeyRevokeRequest`

NewAPIKeyRevokeRequestWithDefaults instantiates a new APIKeyRevokeRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetKeyId

`func (o *APIKeyRevokeRequest) GetKeyId() string`

GetKeyId returns the KeyId field if non-nil, zero value otherwise.

### GetKeyIdOk

`func (o *APIKeyRevokeRequest) GetKeyIdOk() (*string, bool)`

GetKeyIdOk returns a tuple with the KeyId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKeyId

`func (o *APIKeyRevokeRequest) SetKeyId(v string)`

SetKeyId sets KeyId field to given value.


### GetReason

`func (o *APIKeyRevokeRequest) GetReason() string`

GetReason returns the Reason field if non-nil, zero value otherwise.

### GetReasonOk

`func (o *APIKeyRevokeRequest) GetReasonOk() (*string, bool)`

GetReasonOk returns a tuple with the Reason field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetReason

`func (o *APIKeyRevokeRequest) SetReason(v string)`

SetReason sets Reason field to given value.

### HasReason

`func (o *APIKeyRevokeRequest) HasReason() bool`

HasReason returns a boolean if a field has been set.

### SetReasonNil

`func (o *APIKeyRevokeRequest) SetReasonNil(b bool)`

 SetReasonNil sets the value for Reason to be an explicit nil

### UnsetReason
`func (o *APIKeyRevokeRequest) UnsetReason()`

UnsetReason ensures that no value is present for Reason, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


